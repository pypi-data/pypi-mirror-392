"""
Main client interface for FBA Finance
"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from .aggregator import ProviderAggregator
from .models import Quote, HistoricalData, ProviderStatus
from .config import Config


class FinanceClient:
    """
    Main client for accessing financial data from multiple sources.
    
    Features:
    - Automatic fallback between providers
    - Built-in caching with market-aware TTL
    - Rate limiting with market-aware optimization
    - Support for all major markets
    - Market hours tracking (15 global exchanges)
    
    Example:
        >>> client = FinanceClient()
        >>> quote = client.get_quote("AAPL")
        >>> print(quote.price)
        >>> 
        >>> # Check if market is open
        >>> if client.is_market_open("AAPL"):
        ...     print("Market is open!")
    """
    
    def __init__(self,
                 use_cache: bool = True,
                 use_rate_limiting: bool = True,
                 provider_priority: Optional[List[str]] = None):
        """
        Initialize the finance client
        
        Args:
            use_cache: Enable caching (default: True)
            use_rate_limiting: Enable rate limiting (default: True)
            provider_priority: Custom provider priority order (optional)
        """
        self.aggregator = ProviderAggregator(
            use_cache=use_cache,
            use_rate_limiting=use_rate_limiting,
            provider_priority=provider_priority
        )
    
    def get_quote(self, symbol: str, provider: Optional[str] = None) -> Optional[Quote]:
        """
        Get real-time (or near-real-time) quote for a symbol
        
        Args:
            symbol: Ticker symbol (e.g., "AAPL", "MSFT", "BTC-USD")
            provider: Force specific provider (optional)
        
        Returns:
            Quote object with current price and metadata
        
        Example:
            >>> quote = client.get_quote("AAPL")
            >>> print(f"{quote.symbol}: ${quote.price}")
        """
        return self.aggregator.get_quote(symbol, force_provider=provider)
    
    def get_quotes(self, symbols: List[str], provider: Optional[str] = None) -> Dict[str, Quote]:
        """
        Get quotes for multiple symbols (batch operation)
        
        Args:
            symbols: List of ticker symbols
            provider: Force specific provider (optional)
        
        Returns:
            Dictionary mapping symbols to Quote objects
        
        Example:
            >>> quotes = client.get_quotes(["AAPL", "MSFT", "GOOGL"])
            >>> for symbol, quote in quotes.items():
            ...     print(f"{symbol}: ${quote.price}")
        """
        return self.aggregator.get_multiple_quotes(symbols, force_provider=provider)
    
    def get_historical(self,
                      symbol: str,
                      start: Optional[datetime] = None,
                      end: Optional[datetime] = None,
                      period: Optional[str] = None,
                      interval: str = "1d",
                      provider: Optional[str] = None) -> Optional[HistoricalData]:
        """
        Get historical OHLCV data
        
        Args:
            symbol: Ticker symbol
            start: Start date (optional if period is specified)
            end: End date (optional, defaults to now)
            period: Period string like "1mo", "3mo", "1y", "5y" (alternative to start/end)
            interval: Data interval - "1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"
            provider: Force specific provider (optional)
        
        Returns:
            HistoricalData object with pandas DataFrame
        
        Example:
            >>> # Get 1 year of daily data
            >>> data = client.get_historical("AAPL", period="1y", interval="1d")
            >>> print(data.data.head())
            
            >>> # Get specific date range
            >>> from datetime import datetime, timedelta
            >>> end = datetime.now()
            >>> start = end - timedelta(days=30)
            >>> data = client.get_historical("AAPL", start=start, end=end)
        """
        # Handle period shorthand
        if period and not start:
            end = end or datetime.now()
            period_map = {
                "1d": 1, "5d": 5,
                "1mo": 30, "3mo": 90, "6mo": 180,
                "1y": 365, "2y": 730, "5y": 1825, "10y": 3650
            }
            days = period_map.get(period, 365)
            start = end - timedelta(days=days)
        
        if not start:
            start = datetime.now() - timedelta(days=365)
        
        if not end:
            end = datetime.now()
        
        return self.aggregator.get_historical(
            symbol, start, end, interval, force_provider=provider
        )
    
    def get_provider_status(self) -> List[ProviderStatus]:
        """
        Get status of all data providers
        
        Returns:
            List of ProviderStatus objects
        
        Example:
            >>> statuses = client.get_provider_status()
            >>> for status in statuses:
            ...     print(f"{status.name}: {'✓' if status.available else '✗'}")
        """
        return self.aggregator.get_provider_status()
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available provider names
        
        Returns:
            List of provider names that are currently available
        """
        return self.aggregator.get_available_providers()
    
    def clear_cache(self):
        """Clear all cached data"""
        self.aggregator.clear_cache()
    
    # Convenience methods
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get just the current price (convenience method)
        
        Args:
            symbol: Ticker symbol
        
        Returns:
            Current price as float, or None if unavailable
        """
        quote = self.get_quote(symbol)
        return quote.price if quote else None
    
    def get_day_change(self, symbol: str) -> Optional[tuple]:
        """
        Get day change and change percent
        
        Args:
            symbol: Ticker symbol
        
        Returns:
            Tuple of (change, change_percent) or None
        """
        quote = self.get_quote(symbol)
        if quote:
            return (quote.change, quote.change_percent)
        return None
    
    # ========================================================================
    # Extended APIs - Calendar, Recommendations, Financials
    # ========================================================================
    
    def get_calendar(self, symbol: str, provider: Optional[str] = None) -> Dict:
        """
        Get upcoming events calendar (earnings, dividends).
        
        Args:
            symbol: Ticker symbol
            provider: Force specific provider (optional)
        
        Returns:
            Dictionary with upcoming events
        
        Example:
            >>> calendar = client.get_calendar("AAPL")
            >>> print(calendar.get('Earnings Date'))
        """
        return self.aggregator.get_calendar(symbol, force_provider=provider)
    
    def get_recommendations(self, symbol: str, provider: Optional[str] = None):
        """
        Get analyst recommendations history.
        
        Args:
            symbol: Ticker symbol
            provider: Force specific provider (optional)
        
        Returns:
            pd.DataFrame: Analyst recommendations
        
        Example:
            >>> recs = client.get_recommendations("AAPL")
            >>> print(recs.head())
        """
        return self.aggregator.get_recommendations(symbol, force_provider=provider)
    
    def get_financials(self,
                      symbol: str,
                      statement: str = 'income',
                      frequency: str = 'annual',
                      provider: Optional[str] = None):
        """
        Get financial statements.
        
        Args:
            symbol: Ticker symbol
            statement: Statement type - 'income', 'balance', 'cashflow'
            frequency: 'annual' or 'quarterly'
            provider: Force specific provider (optional)
        
        Returns:
            pd.DataFrame: Financial statement data
        
        Example:
            >>> financials = client.get_financials("AAPL", "income", "annual")
            >>> print(financials.loc['Total Revenue'])
        """
        return self.aggregator.get_financials(
            symbol,
            statement=statement,
            frequency=frequency,
            force_provider=provider
        )
    
    # ========================================================================
    # Market Hours Helper Methods (NEW in v0.1.4)
    # ========================================================================
    
    def is_market_open(self, symbol: str, dt: Optional[datetime] = None) -> bool:
        """
        Check if market is currently open for trading.
        
        Automatically detects exchange from symbol and checks:
        - Regular trading hours
        - Weekends
        - Holidays (2025 calendar)
        - Timezone-aware
        
        Args:
            symbol: Ticker symbol (e.g., "AAPL", "0700.HK", "BMW.DE")
            dt: Datetime to check (default: now)
        
        Returns:
            True if market is open, False otherwise
        
        Example:
            >>> client.is_market_open("AAPL")  # US market
            True
            >>> client.is_market_open("0700.HK")  # Hong Kong
            False
            >>> client.is_market_open("BMW.DE")  # Germany
            True
        """
        try:
            from .market_hours import is_market_open
            return is_market_open(symbol, dt)
        except ImportError:
            return True  # Fallback: assume open if module not available
    
    def get_market_state(self, symbol: str, dt: Optional[datetime] = None) -> str:
        """
        Get current market state.
        
        Args:
            symbol: Ticker symbol
            dt: Datetime to check (default: now)
        
        Returns:
            Market state: "REGULAR", "PRE", "POST", "CLOSED"
        
        Example:
            >>> client.get_market_state("AAPL")
            'REGULAR'
            >>> client.get_market_state("AAPL", datetime(2025, 11, 16, 7, 0))
            'PRE'
        """
        try:
            from .market_hours import get_market_state
            return get_market_state(symbol, dt)
        except ImportError:
            return "REGULAR"
    
    def next_market_open(self, symbol: str, dt: Optional[datetime] = None) -> datetime:
        """
        Get next market open datetime.
        
        Args:
            symbol: Ticker symbol
            dt: Starting datetime (default: now)
        
        Returns:
            Datetime of next market open (timezone-aware)
        
        Example:
            >>> next_open = client.next_market_open("AAPL")
            >>> print(f"Market opens at: {next_open}")
        """
        try:
            from .market_hours import next_market_open
            return next_market_open(symbol, dt)
        except ImportError:
            # Fallback: return tomorrow 9:30 AM
            base = dt or datetime.now()
            return base.replace(hour=9, minute=30, second=0, microsecond=0) + timedelta(days=1)
    
    def next_market_close(self, symbol: str, dt: Optional[datetime] = None) -> datetime:
        """
        Get next market close datetime.
        
        Args:
            symbol: Ticker symbol
            dt: Starting datetime (default: now)
        
        Returns:
            Datetime of next market close (timezone-aware)
        
        Example:
            >>> next_close = client.next_market_close("AAPL")
            >>> print(f"Market closes at: {next_close}")
        """
        try:
            from .market_hours import next_market_close
            return next_market_close(symbol, dt)
        except ImportError:
            # Fallback: return today 4:00 PM
            base = dt or datetime.now()
            return base.replace(hour=16, minute=0, second=0, microsecond=0)
    
    def get_exchange_info(self, symbol: str) -> Dict:
        """
        Get exchange information for a symbol.
        
        Args:
            symbol: Ticker symbol
        
        Returns:
            Dictionary with exchange details (timezone, hours, etc.)
        
        Example:
            >>> info = client.get_exchange_info("AAPL")
            >>> print(info['exchange'])  # NYSE
            >>> print(info['timezone'])  # America/New_York
            >>> print(info['open_time'])  # 09:30
        """
        try:
            from .market_hours import get_market_hours
            mh = get_market_hours()
            return mh.get_exchange_info(symbol)
        except ImportError:
            return {
                "exchange": "NYSE",
                "timezone": "America/New_York",
                "open_time": "09:30",
                "close_time": "16:00",
            }
    
    def get_supported_exchanges(self) -> List[str]:
        """
        Get list of supported exchanges.
        
        Returns:
            List of exchange codes (NYSE, NASDAQ, LSE, TSE, HKEX, etc.)
        
        Example:
            >>> exchanges = client.get_supported_exchanges()
            >>> print(exchanges)
            ['NYSE', 'NASDAQ', 'LSE', 'XETRA', 'TSE', 'HKEX', ...]
        """
        try:
            from .market_hours import get_market_hours
            mh = get_market_hours()
            return mh.get_supported_exchanges()
        except ImportError:
            return ["NYSE", "NASDAQ"]

