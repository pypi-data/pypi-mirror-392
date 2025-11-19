"""
Multi-provider aggregator with automatic fallback and load balancing
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd
import warnings
import random

from .providers import (
    BaseProvider,
    YFinanceProvider,
    YahooQueryProvider,
    YahooScraperProvider,
    TwelveDataProvider,
    AlphaVantageProvider,
)
from .core import CacheManager, ProviderRateLimiter
from .models import Quote, HistoricalData, ProviderStatus
from .config import Config


class ProviderAggregator:
    """
    Aggregates multiple data providers with automatic fallback and load balancing.
    
    Supports three load balancing modes:
    - fallback: Try providers in order until one succeeds (default)
    - round-robin: Distribute requests evenly across providers
    - random: Randomly select provider for each request
    """
    
    def __init__(self,
                 use_cache: bool = True,
                 use_rate_limiting: bool = True,
                 provider_priority: Optional[List[str]] = None,
                 load_balancing_mode: Optional[str] = None):
        
        self.use_cache = use_cache
        self.use_rate_limiting = use_rate_limiting
        self.provider_priority = provider_priority or Config.PROVIDER_PRIORITY
        self.load_balancing_mode = load_balancing_mode or Config.LOAD_BALANCING_MODE
        
        # Round-robin counter
        self._round_robin_index = 0
        
        # Initialize cache
        if self.use_cache:
            self.cache = CacheManager(
                backend=Config.CACHE_BACKEND,
                cache_dir=Config.CACHE_DIR
            )
        else:
            self.cache = None
        
        # Initialize rate limiter
        if self.use_rate_limiting:
            self.rate_limiter = ProviderRateLimiter()
        else:
            self.rate_limiter = None
        
        # Initialize providers
        self.providers: Dict[str, BaseProvider] = {}
        self._init_providers()
    
    def _init_providers(self):
        """Initialize all available providers"""
        provider_classes = {
            "yfinance": YFinanceProvider,
            "yahooquery": YahooQueryProvider,
            "yahoo_scraper": YahooScraperProvider,
            "twelvedata": TwelveDataProvider,
            "alphavantage": AlphaVantageProvider,
        }
        
        for name, provider_class in provider_classes.items():
            try:
                # Pass API key if needed
                if name in ["twelvedata", "alphavantage"]:
                    provider = provider_class(rate_limiter=self.rate_limiter)
                else:
                    provider = provider_class(rate_limiter=self.rate_limiter)
                
                self.providers[name] = provider
                
                if provider.available:
                    print(f"✓ {name} provider initialized")
                else:
                    print(f"✗ {name} provider not available: {provider.last_error}")
                    
            except Exception as e:
                print(f"✗ Failed to initialize {name}: {e}")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return [name for name, provider in self.providers.items() if provider.available]
    
    def get_provider_status(self) -> List[ProviderStatus]:
        """Get status of all providers"""
        statuses = []
        
        for name, provider in self.providers.items():
            has_key = Config.has_api_key(name) if name in ["alphavantage", "twelvedata", "polygon", "fmp"] else True
            
            status = ProviderStatus(
                name=name,
                available=provider.available,
                has_api_key=has_key,
                rate_limited=False,  # TODO: track this
                last_error=provider.last_error,
            )
            statuses.append(status)
        
        return statuses
    
    def _get_providers_in_order(self, force_provider: Optional[str] = None) -> List[BaseProvider]:
        """
        Get providers in priority order.
        
        Args:
            force_provider: Force specific provider (optional)
        
        Returns:
            List of provider instances in order to try
        """
        if force_provider:
            # Use only specified provider
            if force_provider in self.providers:
                return [self.providers[force_provider]]
            else:
                print(f"⚠️ Provider '{force_provider}' not available")
                return []
        
        # Return providers in priority order (only available ones)
        ordered_providers = []
        for name in self.provider_priority:
            if name in self.providers and self.providers[name].available:
                ordered_providers.append(self.providers[name])
        
        return ordered_providers
    
    def _get_ordered_providers(self) -> List[BaseProvider]:
        """
        Get providers in order based on load balancing mode.
        
        Returns:
            List of provider instances in order to try
        """
        # Get all available providers
        available = []
        for name in self.provider_priority:
            if name in self.providers and self.providers[name].available:
                available.append(self.providers[name])
        
        if not available:
            return []
        
        # Apply load balancing strategy
        if self.load_balancing_mode == "round-robin":
            # Rotate providers in round-robin fashion
            ordered = []
            start_idx = self._round_robin_index % len(available)
            
            # Start from current index, then wrap around
            for i in range(len(available)):
                idx = (start_idx + i) % len(available)
                ordered.append(available[idx])
            
            # Increment for next call
            self._round_robin_index = (self._round_robin_index + 1) % len(available)
            return ordered
        
        elif self.load_balancing_mode == "random":
            # Randomize provider order
            return random.sample(available, len(available))
        
        else:  # fallback (default)
            # Use priority order
            return available
    
    def get_quote(self, symbol: str, force_provider: Optional[str] = None) -> Optional[Quote]:
        """
        Get quote with automatic fallback between providers
        
        Args:
            symbol: Ticker symbol
            force_provider: Force use of specific provider (optional)
        
        Returns:
            Quote object or None
        """
        # Check market status and warn if closed
        try:
            from .market_hours import get_market_state
            market_state = get_market_state(symbol)
            if market_state == "CLOSED":
                warnings.warn(
                    f"Market is currently CLOSED for {symbol}. "
                    f"Real-time data may be stale.",
                    UserWarning
                )
        except Exception:
            pass  # Silently ignore if market_hours not available
        
        # Get dynamic cache TTL based on market hours
        cache_ttl = Config.get_cache_ttl_realtime(symbol)
        
        # Check cache first
        if self.cache:
            cached = self.cache.get_cached_quote(symbol)
            if cached:
                print(f"📦 Cache hit for {symbol}")
                return cached
        
        # If specific provider requested
        if force_provider:
            if force_provider in self.providers:
                provider = self.providers[force_provider]
                if provider.available:
                    quote = provider.get_quote(symbol)
                    if quote and self.cache:
                        self.cache.cache_quote(symbol, quote, cache_ttl)
                    return quote
            return None
        
        # Try providers in order
        providers = self._get_ordered_providers()
        
        for provider in providers:
            try:
                print(f"🔍 Trying {provider.name} for {symbol}...")
                quote = provider.get_quote(symbol)
                
                if quote:
                    print(f"✓ Got quote from {provider.name}")
                    
                    # Cache the result with dynamic TTL
                    if self.cache:
                        self.cache.cache_quote(symbol, quote, cache_ttl)
                    
                    return quote
                else:
                    print(f"✗ {provider.name} returned no data")
                    
            except Exception as e:
                print(f"✗ {provider.name} failed: {e}")
                continue
        
        print(f"❌ All providers failed for {symbol}")
        return None
    
    def get_historical(self,
                      symbol: str,
                      start: datetime,
                      end: datetime,
                      interval: str = "1d",
                      force_provider: Optional[str] = None) -> Optional[HistoricalData]:
        """
        Get historical data with automatic fallback
        
        Args:
            symbol: Ticker symbol
            start: Start date
            end: End date
            interval: Data interval (1m, 5m, 15m, 1h, 1d, 1wk, 1mo)
            force_provider: Force use of specific provider (optional)
        
        Returns:
            HistoricalData object or None
        """
        # Get dynamic cache TTL based on market hours
        cache_ttl = Config.get_cache_ttl_historical(symbol)
        
        # Check cache first
        if self.cache:
            cached = self.cache.get_cached_historical(
                symbol, interval, start.isoformat(), end.isoformat()
            )
            if cached:
                print(f"📦 Cache hit for {symbol} historical")
                return cached
        
        # If specific provider requested
        if force_provider:
            if force_provider in self.providers:
                provider = self.providers[force_provider]
                if provider.available:
                    data = provider.get_historical(symbol, start, end, interval)
                    if data and self.cache:
                        self.cache.cache_historical(
                            symbol, interval, start.isoformat(), end.isoformat(),
                            data, cache_ttl
                        )
                    return data
            return None
        
        # Try providers in order
        providers = self._get_ordered_providers()
        
        for provider in providers:
            try:
                print(f"🔍 Trying {provider.name} for {symbol} historical...")
                data = provider.get_historical(symbol, start, end, interval)
                
                if data and data.data is not None and not data.data.empty:
                    print(f"✓ Got historical data from {provider.name}")
                    
                    # Cache the result with dynamic TTL
                    if self.cache:
                        self.cache.cache_historical(
                            symbol, interval, start.isoformat(), end.isoformat(),
                            data, cache_ttl
                        )
                    
                    return data
                else:
                    print(f"✗ {provider.name} returned no data")
                    
            except Exception as e:
                print(f"✗ {provider.name} failed: {e}")
                continue
        
        print(f"❌ All providers failed for {symbol} historical data")
        return None
    
    def get_multiple_quotes(self, 
                           symbols: List[str],
                           force_provider: Optional[str] = None) -> Dict[str, Quote]:
        """
        Get quotes for multiple symbols
        
        Args:
            symbols: List of ticker symbols
            force_provider: Force use of specific provider (optional)
        
        Returns:
            Dictionary mapping symbols to Quote objects
        """
        results = {}
        
        # Check cache for each symbol
        uncached_symbols = []
        if self.cache:
            for symbol in symbols:
                cached = self.cache.get_cached_quote(symbol)
                if cached:
                    results[symbol] = cached
                else:
                    uncached_symbols.append(symbol)
        else:
            uncached_symbols = symbols
        
        if not uncached_symbols:
            return results
        
        # Try batch request with preferred provider
        if force_provider:
            providers = [self.providers[force_provider]] if force_provider in self.providers else []
        else:
            providers = self._get_ordered_providers()
        
        for provider in providers:
            try:
                print(f"🔍 Trying batch request with {provider.name} for {len(uncached_symbols)} symbols...")
                quotes = provider.get_multiple_quotes(uncached_symbols)
                
                for quote in quotes:
                    results[quote.symbol] = quote
                    if self.cache:
                        self.cache.cache_quote(quote.symbol, quote, Config.CACHE_TTL_REALTIME)
                
                # Check if we got all symbols
                if len(results) == len(symbols):
                    print(f"✓ Got all quotes from {provider.name}")
                    return results
                
                # Update uncached list
                uncached_symbols = [s for s in symbols if s not in results]
                
            except Exception as e:
                print(f"✗ {provider.name} batch failed: {e}")
                continue
        
        # Fallback: get remaining symbols individually
        for symbol in uncached_symbols:
            quote = self.get_quote(symbol)
            if quote:
                results[symbol] = quote
        
        return results
    
    def clear_cache(self):
        """Clear all cached data"""
        if self.cache:
            self.cache.clear()
            print("Cache cleared")
    
    # ========================================================================
    # Extended APIs - Calendar, Recommendations, Financials
    # ========================================================================
    
    def get_calendar(self, symbol: str, force_provider: Optional[str] = None) -> Dict:
        """
        Get upcoming events calendar with provider fallback.
        
        Args:
            symbol: Ticker symbol
            force_provider: Force specific provider
        
        Returns:
            Dictionary with calendar events
        """
        # Check cache (TTL: 1 hour for calendar data)
        if self.cache and not force_provider:
            cached = self.cache.get(f"calendar_{symbol}")
            if cached:
                print(f"📦 Cache hit for {symbol} calendar")
                return cached
        
        # Try providers
        for provider in self._get_providers_in_order(force_provider):
            if not hasattr(provider, 'get_calendar'):
                continue
            
            try:
                if self.rate_limiter:
                    self.rate_limiter.wait_if_needed(provider.name)
                
                print(f"🔍 Trying {provider.name} for {symbol} calendar...")
                calendar = provider.get_calendar(symbol)
                
                if calendar:
                    print(f"✓ Got calendar from {provider.name}")
                    if self.cache:
                        self.cache.set(f"calendar_{symbol}", calendar, ttl=3600)  # 1 hour
                    return calendar
                else:
                    print(f"✗ {provider.name} returned no calendar data")
            except Exception as e:
                print(f"✗ {provider.name} calendar error: {e}")
                continue
        
        print(f"❌ All providers failed for {symbol} calendar")
        return {}
    
    def get_recommendations(self, symbol: str, force_provider: Optional[str] = None):
        """
        Get analyst recommendations with provider fallback.
        
        Args:
            symbol: Ticker symbol
            force_provider: Force specific provider
        
        Returns:
            pd.DataFrame: Recommendations data
        """
        # Check cache (TTL: 1 hour for recommendations)
        if self.cache and not force_provider:
            cached = self.cache.get(f"recommendations_{symbol}")
            if cached is not None:
                print(f"📦 Cache hit for {symbol} recommendations")
                return cached
        
        # Try providers
        for provider in self._get_providers_in_order(force_provider):
            if not hasattr(provider, 'get_recommendations'):
                continue
            
            try:
                if self.rate_limiter:
                    self.rate_limiter.wait_if_needed(provider.name)
                
                print(f"🔍 Trying {provider.name} for {symbol} recommendations...")
                recs = provider.get_recommendations(symbol)
                
                if recs is not None and not recs.empty:
                    print(f"✓ Got recommendations from {provider.name}")
                    if self.cache:
                        self.cache.set(f"recommendations_{symbol}", recs, ttl=3600)  # 1 hour
                    return recs
                else:
                    print(f"✗ {provider.name} returned no recommendations")
            except Exception as e:
                print(f"✗ {provider.name} recommendations error: {e}")
                continue
        
        print(f"❌ All providers failed for {symbol} recommendations")
        return pd.DataFrame()
    
    def get_financials(self,
                      symbol: str,
                      statement: str = 'income',
                      frequency: str = 'annual',
                      force_provider: Optional[str] = None):
        """
        Get financial statements with provider fallback.
        
        Args:
            symbol: Ticker symbol
            statement: 'income', 'balance', or 'cashflow'
            frequency: 'annual' or 'quarterly'
            force_provider: Force specific provider
        
        Returns:
            pd.DataFrame: Financial statement data
        """
        # Check cache (TTL: 24 hours for financials - they don't change often)
        cache_key = f"financials_{symbol}_{statement}_{frequency}"
        if self.cache and not force_provider:
            cached = self.cache.get(cache_key)
            if cached is not None:
                print(f"📦 Cache hit for {symbol} {frequency} {statement}")
                return cached
        
        # Try providers
        for provider in self._get_providers_in_order(force_provider):
            if not hasattr(provider, 'get_financials'):
                continue
            
            try:
                if self.rate_limiter:
                    self.rate_limiter.wait_if_needed(provider.name)
                
                print(f"🔍 Trying {provider.name} for {symbol} {frequency} {statement}...")
                financials = provider.get_financials(symbol, statement, frequency)
                
                if financials is not None and not financials.empty:
                    print(f"✓ Got financials from {provider.name}")
                    if self.cache:
                        self.cache.set(cache_key, financials, ttl=86400)  # 24 hours
                    return financials
                else:
                    print(f"✗ {provider.name} returned no financials")
            except Exception as e:
                print(f"✗ {provider.name} financials error: {e}")
                continue
        
        print(f"❌ All providers failed for {symbol} {frequency} {statement}")
        return pd.DataFrame()
