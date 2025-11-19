"""
Smart Portfolio API - RealtimePortfolio with built-in intelligence

Philosophy: "Ask always, library decides when to fetch"

Features:
- Automatic cache management with market-aware TTL
- Provider failover and rate limiting
- Multiple operation modes (realtime, aggressive, historical, manual)
- Thread-safe operations
- Zero configuration required

Usage:
    >>> import fba_finance as yf
    >>> portfolio = yf.RealtimePortfolio(
    ...     symbols=["AAPL", "MSFT", "GOOGL"],
    ...     mode="realtime"
    ... )
    >>> 
    >>> # Simple loop - library handles everything
    >>> while True:
    ...     quotes = portfolio.get_quotes()  # Smart: cache or fetch
    ...     process(quotes)
    ...     time.sleep(1)  # Fast loop OK, library throttles
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import time
import threading

from .core.cache import CacheManager
from .core.rate_limiter import ProviderRateLimiter
from .market_hours import is_market_open
from .config import Config
from .client import FinanceClient


class OperationMode:
    """Portfolio operation mode configuration"""
    
    def __init__(self, name: str, ttl_open: int, ttl_closed: int, description: str):
        self.name = name
        self.ttl_open = ttl_open          # TTL when market open (seconds)
        self.ttl_closed = ttl_closed      # TTL when market closed
        self.description = description
    
    def __repr__(self):
        return f"OperationMode({self.name}, open={self.ttl_open}s, closed={self.ttl_closed}s)"


# Pre-defined operation modes
MODES = {
    "realtime": OperationMode(
        name="realtime",
        ttl_open=60,        # 1 minute when market open
        ttl_closed=3600,    # 1 hour when market closed
        description="Market-aware with dynamic TTL (default)"
    ),
    "aggressive": OperationMode(
        name="aggressive",
        ttl_open=30,        # 30 seconds
        ttl_closed=30,      # Always aggressive, even when closed
        description="Low TTL for high-frequency trading"
    ),
    "historical": OperationMode(
        name="historical",
        ttl_open=3600,      # 1 hour
        ttl_closed=86400,   # 24 hours when closed
        description="Long TTL for backtesting and analysis"
    ),
    "manual": OperationMode(
        name="manual",
        ttl_open=float('inf'),
        ttl_closed=float('inf'),
        description="No auto-fetch, full manual control"
    )
}


class RealtimePortfolio:
    """
    Smart portfolio with built-in data fetching intelligence.
    
    The portfolio handles all complexity internally:
    - Decides when to fetch vs return cache
    - Manages provider failover automatically
    - Respects rate limits across all providers
    - Adjusts behavior based on market hours
    
    Args:
        symbols: List of ticker symbols
        mode: Operation mode ("realtime", "aggressive", "historical", "manual")
        respect_market_hours: Auto-adjust TTL based on market state
        providers: Custom provider priority list (optional)
        cache_backend: Cache backend ("memory", "disk", "redis")
    
    Example:
        >>> # Create portfolio
        >>> portfolio = RealtimePortfolio(
        ...     symbols=["AAPL", "MSFT"],
        ...     mode="realtime"
        ... )
        >>> 
        >>> # Get quotes (smart fetch)
        >>> quotes = portfolio.get_quotes()
        >>> print(quotes["AAPL"]["price"])
        >>> 
        >>> # Force fresh fetch
        >>> quotes = portfolio.get_quotes(force=True)
        >>> 
        >>> # Get status
        >>> status = portfolio.get_status()
        >>> print(status["cache_hit_rate"])
    """
    
    def __init__(
        self,
        symbols: List[str],
        mode: str = "realtime",
        respect_market_hours: bool = True,
        providers: Optional[List[str]] = None,
        cache_backend: str = "memory"
    ):
        if mode not in MODES:
            raise ValueError(f"Invalid mode: {mode}. Available: {list(MODES.keys())}")
        
        self.symbols = symbols
        self.mode_config = MODES[mode]
        self.respect_market_hours = respect_market_hours
        self.providers = providers or Config.PROVIDER_PRIORITY
        
        # Initialize components
        self.cache = CacheManager(backend=cache_backend)
        self.rate_limiter = ProviderRateLimiter()
        self.client = FinanceClient(use_cache=False, use_rate_limiting=False)
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Statistics
        self._stats = {
            "requests_total": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "api_calls": 0,
            "rate_limit_blocks": 0
        }
        
        print(f"✅ RealtimePortfolio initialized: {len(symbols)} symbols, mode={mode}")
    
    def get_quotes(self, force: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        Get quotes for all symbols in portfolio.
        
        Smart behavior:
        1. Check cache freshness (market-aware TTL)
        2. Check rate limits
        3. Fetch only if needed
        4. Return cached data when appropriate
        
        Args:
            force: Force fresh fetch, bypass all checks
        
        Returns:
            Dictionary mapping symbols to quote data
        
        Example:
            >>> quotes = portfolio.get_quotes()
            >>> for symbol, data in quotes.items():
            ...     print(f"{symbol}: ${data['price']}")
        """
        with self._lock:
            self._stats["requests_total"] += 1
            
            results = {}
            symbols_to_fetch = []
            
            for symbol in self.symbols:
                if force:
                    symbols_to_fetch.append(symbol)
                elif self._should_fetch(symbol):
                    symbols_to_fetch.append(symbol)
                    self._stats["cache_misses"] += 1
                else:
                    # Return cached data
                    cached = self._get_from_cache(symbol)
                    if cached:
                        results[symbol] = cached
                        self._stats["cache_hits"] += 1
            
            # Fetch if needed
            if symbols_to_fetch:
                fresh_data = self._fetch_batch(symbols_to_fetch)
                results.update(fresh_data)
            
            return results
    
    def _should_fetch(self, symbol: str) -> bool:
        """
        Decide if we should fetch fresh data.
        
        Intelligence:
        1. Check cache freshness (market-aware TTL)
        2. Manual mode: never auto-fetch
        """
        # Manual mode: never auto-fetch
        if self.mode_config.name == "manual":
            return False
        
        # Get appropriate TTL
        ttl = self._get_ttl_for_symbol(symbol)
        
        # Check cache staleness
        cache_key = f"quote:{symbol}"
        return self.cache.is_stale(cache_key, ttl)
    
    def _get_ttl_for_symbol(self, symbol: str) -> int:
        """Get TTL for symbol based on market hours"""
        if not self.respect_market_hours:
            return self.mode_config.ttl_open
        
        # Check if market is open
        try:
            market_open = is_market_open(symbol)
            return self.mode_config.ttl_open if market_open else self.mode_config.ttl_closed
        except Exception:
            # Fallback: use "open" TTL
            return self.mode_config.ttl_open
    
    def _get_from_cache(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached quote for symbol"""
        cache_key = f"quote:{symbol}"
        return self.cache.get(cache_key)
    
    def _fetch_batch(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Fetch fresh data with provider failover.
        
        Tries providers in priority order until success.
        Handles rate limiting and failures gracefully.
        """
        self._stats["api_calls"] += 1
        
        for provider in self.providers:
            # Check if provider is blocked (cooldown)
            if self.rate_limiter.is_provider_blocked(provider):
                continue
            
            # Check rate limits
            if not self.rate_limiter.can_use_provider(provider):
                self._stats["rate_limit_blocks"] += 1
                continue
            
            try:
                # Wait for rate limiter (automatically enforces limits)
                self.rate_limiter.wait_if_needed(provider)
                
                # Fetch from provider
                data = self.client.get_quotes(symbols, provider=provider)
                
                # Convert to dict and cache
                results = {}
                for symbol in symbols:
                    if symbol in data and data[symbol]:
                        quote_dict = self._quote_to_dict(data[symbol])
                        results[symbol] = quote_dict
                        
                        # Cache the result
                        cache_key = f"quote:{symbol}"
                        ttl = self._get_ttl_for_symbol(symbol)
                        self.cache.set(cache_key, quote_dict, ttl)
                
                # Success!
                self.rate_limiter.record_success(provider)
                return results
            
            except Exception as e:
                # Check if rate limit error
                error_str = str(e).lower()
                if "429" in error_str or "rate limit" in error_str:
                    self.rate_limiter.record_rate_limit(provider, cooldown_seconds=300)
                
                # Try next provider
                print(f"⚠️ Provider {provider} failed: {e}")
                continue
        
        # All providers failed - return cached data (even if stale)
        print(f"❌ All providers failed for {symbols}, returning cached data")
        results = {}
        for symbol in symbols:
            cached = self._get_from_cache(symbol)
            if cached:
                results[symbol] = cached
        
        return results
    
    def _quote_to_dict(self, quote) -> Dict[str, Any]:
        """Convert Quote object to dictionary"""
        if isinstance(quote, dict):
            return quote
        
        # Convert Quote object to dict (use to_dict if available)
        if hasattr(quote, 'to_dict'):
            return quote.to_dict()
        
        # Fallback: manual conversion
        return {
            "symbol": quote.symbol,
            "price": quote.price,
            "change": getattr(quote, "change", None),
            "change_percent": getattr(quote, "change_percent", None),
            "volume": getattr(quote, "volume", None),
            "market_cap": getattr(quote, "market_cap", None),
            "timestamp": getattr(quote, "timestamp", datetime.now()).isoformat(),
            "source": getattr(quote, "source", None)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get portfolio status for monitoring.
        
        Returns:
            Dictionary with statistics and status
        
        Example:
            >>> status = portfolio.get_status()
            >>> print(f"Cache hit rate: {status['cache_hit_rate']}")
            >>> print(f"API calls: {status['api_calls']}")
        """
        total_requests = self._stats["cache_hits"] + self._stats["cache_misses"]
        cache_hit_rate = (
            self._stats["cache_hits"] / total_requests * 100 
            if total_requests > 0 else 0
        )
        
        return {
            "symbols_count": len(self.symbols),
            "mode": self.mode_config.name,
            "respect_market_hours": self.respect_market_hours,
            "cache_hit_rate": f"{cache_hit_rate:.1f}%",
            "statistics": self._stats.copy(),
            "cache_backend": self.cache.backend,
            "cache_stats": self.cache.get_stats() if hasattr(self.cache, 'get_stats') else {}
        }
    
    def clear_cache(self):
        """Clear all cached data for this portfolio"""
        for symbol in self.symbols:
            cache_key = f"quote:{symbol}"
            self.cache.delete(cache_key)
        print(f"✅ Cache cleared for {len(self.symbols)} symbols")
    
    def update_symbols(self, symbols: List[str]):
        """Update portfolio symbols"""
        self.symbols = symbols
        print(f"✅ Portfolio updated: {len(symbols)} symbols")
    
    def __repr__(self):
        return f"RealtimePortfolio(symbols={len(self.symbols)}, mode={self.mode_config.name})"
