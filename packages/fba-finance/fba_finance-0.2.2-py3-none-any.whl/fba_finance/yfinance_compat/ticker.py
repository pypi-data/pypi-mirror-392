"""
yfinance-compatible Ticker wrapper for fba_finance
Drop-in replacement for yfinance.Ticker
"""
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import pandas as pd

from ..client import FinanceClient
from ..models import Quote, HistoricalData


class Ticker:
    """
    Drop-in replacement for yfinance.Ticker
    
    Provides complete API compatibility with yfinance while using
    fba_finance multi-provider backend.
    
    Usage:
        >>> import fba_finance as yf  # Drop-in replacement
        >>> ticker = yf.Ticker("AAPL")
        >>> info = ticker.info
        >>> hist = ticker.history(period="1mo")
    """
    
    def __init__(
        self,
        ticker: str,
        session: Optional[Any] = None,
        cache: bool = True,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 3600
    ):
        """
        Initialize Ticker object.
        
        Args:
            ticker: Ticker symbol (e.g., "AAPL", "MSFT")
            session: HTTP session (ignored, for yfinance compatibility)
            cache: Enable caching (default: True)
            cache_dir: Cache directory (ignored, uses fba_finance config)
            cache_ttl: Cache TTL in seconds (default: 3600)
        """
        self.ticker = ticker.upper()
        self._client = FinanceClient(use_cache=cache)
        self._info_cache = None
        self._info_cache_time = None
        self._info_ttl = 300  # 5 minutes for info
        
        # Extended API caches (lazy loading)
        self._dividends = None
        self._splits = None
        self._actions = None
        self._calendar = None
        self._recommendations = None
        self._financials = None
        self._quarterly_financials = None
        self._balance_sheet = None
        self._quarterly_balance_sheet = None
        self._cashflow = None
        self._quarterly_cashflow = None
        
    @property
    def info(self) -> Dict[str, Any]:
        """
        Get all metadata for the symbol.
        
        Returns a dictionary with 78+ guaranteed fields compatible with yfinance.
        
        Returns:
            Dict[str, Any]: Dictionary with all metadata fields
            
        Example:
            >>> ticker = Ticker("AAPL")
            >>> info = ticker.info
            >>> print(info['longName'])  # "Apple Inc."
            >>> print(info['currentPrice'])  # 175.43
        """
        # Check cache
        if self._info_cache is not None and self._info_cache_time is not None:
            if (datetime.now() - self._info_cache_time).total_seconds() < self._info_ttl:
                return self._info_cache
        
        # Fetch fresh data
        quote = self._client.get_quote(self.ticker)
        
        if not quote:
            # Return minimal info if quote fetch fails
            return self._get_minimal_info()
        
        # Build comprehensive info dict
        info = self._build_info_dict(quote)
        
        # Cache it
        self._info_cache = info
        self._info_cache_time = datetime.now()
        
        return info
    
    def _get_minimal_info(self) -> Dict[str, Any]:
        """Return minimal info dict when data unavailable"""
        return {
            # Identification
            'symbol': self.ticker,
            'longName': None,
            'shortName': None,
            'exchange': '',
            'quoteType': 'EQUITY',
            'currency': 'USD',
            'country': None,
            
            # Sector
            'sector': None,
            'industry': None,
            
            # Prices (all zeros)
            'currentPrice': 0.0,
            'regularMarketPrice': 0.0,
            'previousClose': 0.0,
            'open': 0.0,
            'dayHigh': 0.0,
            'dayLow': 0.0,
            'fiftyTwoWeekHigh': 0.0,
            'fiftyTwoWeekLow': 0.0,
            
            # Volumes
            'volume': 0,
            'averageVolume': 0,
            'averageVolume10days': 0,
            
            # Market cap & valuation
            'marketCap': 0,
            'enterpriseValue': 0,
            'trailingPE': None,
            'forwardPE': None,
            'pegRatio': None,
            'priceToBook': None,
            'priceToSalesTrailing12Months': None,
            
            # Dividends
            'dividendRate': None,
            'dividendYield': None,
            'payoutRatio': None,
            'exDividendDate': None,
            
            # Financials
            'totalRevenue': None,
            'profitMargins': None,
            'operatingMargins': None,
            'returnOnEquity': None,
            'returnOnAssets': None,
            
            # Technical
            'beta': None,
            'fiftyDayAverage': None,
            'twoHundredDayAverage': None,
            
            # Trading
            'bid': 0.0,
            'ask': 0.0,
            'bidSize': 0,
            'askSize': 0,
            'tradeable': True,
            'marketState': 'REGULAR',
            
            # Other
            'longBusinessSummary': None,
            'website': None,
            'fullTimeEmployees': None,
        }
    
    def _build_info_dict(self, quote: Quote) -> Dict[str, Any]:
        """Build comprehensive info dictionary from Quote object"""
        
        # Get metadata from quote
        metadata = quote.metadata or {}
        
        info = {
            # === 1. Identification (7 fields) ===
            'symbol': self.ticker,
            'longName': metadata.get('longName'),
            'shortName': metadata.get('shortName'),
            'exchange': quote.exchange or '',
            'quoteType': metadata.get('quoteType', 'EQUITY'),
            'currency': quote.currency or 'USD',
            'country': metadata.get('country'),
            
            # === 2. Sector/Industry (2 fields) ===
            'sector': metadata.get('sector'),
            'industry': metadata.get('industry'),
            
            # === 3. Current Prices (8 fields) ===
            'currentPrice': quote.price,
            'regularMarketPrice': quote.price,
            'previousClose': quote.previous_close or 0.0,
            'open': quote.open or 0.0,
            'dayHigh': quote.high or 0.0,
            'dayLow': quote.low or 0.0,
            'fiftyTwoWeekHigh': quote.fifty_two_week_high or 0.0,
            'fiftyTwoWeekLow': quote.fifty_two_week_low or 0.0,
            
            # === 4. Volumes (3 fields) ===
            'volume': quote.volume or 0,
            'averageVolume': metadata.get('averageVolume', 0),
            'averageVolume10days': metadata.get('averageVolume10days', 0),
            
            # === 5. Market Cap & Valuation (7 fields) ===
            'marketCap': quote.market_cap or 0,
            'enterpriseValue': metadata.get('enterpriseValue', 0),
            'trailingPE': quote.pe_ratio,
            'forwardPE': metadata.get('forwardPE'),
            'pegRatio': metadata.get('pegRatio'),
            'priceToBook': metadata.get('priceToBook'),
            'priceToSalesTrailing12Months': metadata.get('priceToSalesTrailing12Months'),
            
            # === 6. Dividends (4 fields) ===
            'dividendRate': metadata.get('dividendRate'),
            'dividendYield': metadata.get('dividendYield'),
            'payoutRatio': metadata.get('payoutRatio'),
            'exDividendDate': metadata.get('exDividendDate'),
            
            # === 7. Financials (5 fields) ===
            'totalRevenue': metadata.get('totalRevenue'),
            'profitMargins': metadata.get('profitMargins'),
            'operatingMargins': metadata.get('operatingMargins'),
            'returnOnEquity': metadata.get('returnOnEquity'),
            'returnOnAssets': metadata.get('returnOnAssets'),
            
            # === 8. Technical Indicators (3 fields) ===
            'beta': metadata.get('beta'),
            'fiftyDayAverage': metadata.get('fiftyDayAverage'),
            'twoHundredDayAverage': metadata.get('twoHundredDayAverage'),
            
            # === 9. Trading Info (6 fields) ===
            'bid': quote.bid or 0.0,
            'ask': quote.ask or 0.0,
            'bidSize': quote.bid_size or 0,
            'askSize': quote.ask_size or 0,
            'tradeable': metadata.get('tradeable', True),
            'marketState': metadata.get('marketState', 'REGULAR'),
            
            # === 10. Company Info (3 fields) ===
            'longBusinessSummary': metadata.get('longBusinessSummary'),
            'website': metadata.get('website'),
            'fullTimeEmployees': metadata.get('fullTimeEmployees'),
            
            # === 11. Price Changes (3 fields) ===
            'regularMarketChange': quote.change or 0.0,
            'regularMarketChangePercent': quote.change_percent or 0.0,
            'regularMarketDayRange': f"{quote.low or 0.0} - {quote.high or 0.0}" if quote.low and quote.high else None,
            
            # === 12. Additional yfinance compatibility ===
            'regularMarketVolume': quote.volume or 0,
            'regularMarketOpen': quote.open or 0.0,
            'regularMarketDayHigh': quote.high or 0.0,
            'regularMarketDayLow': quote.low or 0.0,
            'regularMarketPreviousClose': quote.previous_close or 0.0,
        }
        
        # Add all metadata fields that aren't already in info
        for key, value in metadata.items():
            if key not in info:
                info[key] = value
        
        return info
    
    def history(
        self,
        period: str = "1mo",
        interval: str = "1d",
        start: Optional[str] = None,
        end: Optional[str] = None,
        prepost: bool = False,
        auto_adjust: bool = True,
        back_adjust: bool = False,
        actions: bool = True,
        **kwargs
    ) -> pd.DataFrame:
        """
        Get historical OHLCV data.
        
        Args:
            period: Period to download ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval: Data interval ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
            start: Start date (YYYY-MM-DD or datetime)
            end: End date (YYYY-MM-DD or datetime)
            prepost: Include pre and post market data (ignored)
            auto_adjust: Adjust all OHLC automatically (ignored)
            back_adjust: Back-adjust data (ignored)
            actions: Include dividends and stock splits
            
        Returns:
            pd.DataFrame: Historical data with columns [Open, High, Low, Close, Volume, Dividends, Stock Splits]
                         Index: DatetimeIndex
                         
        Example:
            >>> ticker = Ticker("AAPL")
            >>> hist = ticker.history(period="1mo", interval="1d")
            >>> print(hist.head())
            >>> current_price = hist['Close'].iloc[-1]
        """
        # Parse dates
        if start and end:
            start_dt = pd.to_datetime(start) if isinstance(start, str) else start
            end_dt = pd.to_datetime(end) if isinstance(end, str) else end
        else:
            end_dt = datetime.now()
            # Map period to days
            period_map = {
                '1d': 1, '5d': 5,
                '1mo': 30, '3mo': 90, '6mo': 180,
                '1y': 365, '2y': 730, '5y': 1825, '10y': 3650,
                'ytd': (datetime.now() - datetime(datetime.now().year, 1, 1)).days,
                'max': 36500  # ~100 years
            }
            days = period_map.get(period, 30)
            start_dt = end_dt - timedelta(days=days)
        
        # Get data from client
        data = self._client.get_historical(
            self.ticker,
            start=start_dt,
            end=end_dt,
            interval=interval
        )
        
        if not data or data.data is None or data.data.empty:
            # Return empty DataFrame with correct structure
            return self._get_empty_dataframe()
        
        df = data.data.copy()
        
        # Standardize column names (yfinance uses capitalized names)
        column_mapping = {
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume',
            'date': 'Date'
        }
        
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        # Ensure required columns exist
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_cols:
            if col not in df.columns:
                df[col] = 0.0
        
        # Add Dividends and Stock Splits columns (yfinance compatibility)
        if 'Dividends' not in df.columns:
            df['Dividends'] = 0.0
        if 'Stock Splits' not in df.columns:
            df['Stock Splits'] = 0.0
        
        # Set DatetimeIndex with timezone normalization
        if 'Date' in df.columns:
            # Convert to datetime UTC then remove timezone (yfinance compatibility)
            df['Date'] = pd.to_datetime(df['Date'], utc=True).dt.tz_localize(None)
            df = df.set_index('Date')
        elif 'date' in df.columns:
            # Convert to datetime UTC then remove timezone (yfinance compatibility)
            df['date'] = pd.to_datetime(df['date'], utc=True).dt.tz_localize(None)
            df = df.set_index('date')
            df.index.name = 'Date'
        
        # Ensure index is DatetimeIndex
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
        
        # Sort by date
        df = df.sort_index()
        
        # Select and order columns like yfinance
        column_order = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
        df = df[[col for col in column_order if col in df.columns]]
        
        return df
    
    def _get_empty_dataframe(self) -> pd.DataFrame:
        """Return empty DataFrame with correct yfinance structure"""
        df = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits'])
        df.index = pd.DatetimeIndex([])
        df.index.name = 'Date'
        return df
    
    # ========================================================================
    # Extended APIs - Phase 1: Corporate Actions
    # ========================================================================
    
    @property
    def dividends(self):
        """
        Get historical dividends as pandas Series.
        
        Returns:
            pd.Series: Dividends with DatetimeIndex (only dates with dividends > 0)
            
        Example:
            >>> ticker = Ticker("AAPL")
            >>> divs = ticker.dividends
            >>> print(divs.tail())  # Last 5 dividends
        """
        if self._dividends is None:
            # Get maximum history available
            hist = self.history(period='max', interval='1d')
            
            if not hist.empty and 'Dividends' in hist.columns:
                # Filter only dates with actual dividends
                self._dividends = hist['Dividends'][hist['Dividends'] > 0]
            else:
                # Return empty series if no data
                self._dividends = pd.Series([], dtype=float, name='Dividends')
                self._dividends.index = pd.DatetimeIndex([])
        
        return self._dividends
    
    @property
    def splits(self):
        """
        Get historical stock splits as pandas Series.
        
        Returns:
            pd.Series: Stock splits with DatetimeIndex (only dates with splits)
            
        Example:
            >>> ticker = Ticker("AAPL")
            >>> splits = ticker.splits
            >>> print(splits)  # All stock splits
        """
        if self._splits is None:
            # Get maximum history available
            hist = self.history(period='max', interval='1d')
            
            if not hist.empty and 'Stock Splits' in hist.columns:
                # Filter only dates with actual splits (non-zero)
                self._splits = hist['Stock Splits'][hist['Stock Splits'] != 0]
            else:
                # Return empty series if no data
                self._splits = pd.Series([], dtype=float, name='Stock Splits')
                self._splits.index = pd.DatetimeIndex([])
        
        return self._splits
    
    @property
    def actions(self):
        """
        Get combined dividends and stock splits as pandas DataFrame.
        
        Returns:
            pd.DataFrame: DataFrame with 'Dividends' and 'Stock Splits' columns
            
        Example:
            >>> ticker = Ticker("AAPL")
            >>> actions = ticker.actions
            >>> print(actions.tail())  # Last 5 corporate actions
        """
        if self._actions is None:
            # Combine dividends and splits
            dividends = self.dividends
            splits = self.splits
            
            # Create DataFrame with both series
            self._actions = pd.DataFrame({
                'Dividends': dividends,
                'Stock Splits': splits
            })
            
            # Fill NaN with 0.0 for missing values
            self._actions = self._actions.fillna(0.0)
            
            # Sort by date descending (most recent first)
            self._actions = self._actions.sort_index(ascending=False)
        
        return self._actions
    
    # ========================================================================
    # Extended APIs - Phase 1: Calendar & Recommendations
    # ========================================================================
    
    @property
    def calendar(self):
        """
        Get upcoming events calendar (earnings, dividends).
        
        Returns:
            dict: Calendar with upcoming events
            
        Example:
            >>> ticker = Ticker("AAPL")
            >>> cal = ticker.calendar
            >>> print(cal.get('Earnings Date'))
        """
        if self._calendar is None:
            self._calendar = self._client.get_calendar(self.ticker)
        return self._calendar
    
    @property
    def recommendations(self):
        """
        Get analyst recommendations history.
        
        Returns:
            pd.DataFrame: Analyst recommendations with dates, firms, ratings
            
        Example:
            >>> ticker = Ticker("AAPL")
            >>> recs = ticker.recommendations
            >>> print(recs.head())
        """
        if self._recommendations is None:
            self._recommendations = self._client.get_recommendations(self.ticker)
        return self._recommendations
    
    # ========================================================================
    # Extended APIs - Phase 2: Financial Statements
    # ========================================================================
    
    @property
    def financials(self):
        """
        Get annual income statement.
        
        Returns:
            pd.DataFrame: Annual income statement (latest → oldest columns)
            
        Example:
            >>> ticker = Ticker("AAPL")
            >>> financials = ticker.financials
            >>> print(financials.loc['Total Revenue'])
        """
        if self._financials is None:
            self._financials = self._client.get_financials(
                self.ticker,
                statement='income',
                frequency='annual'
            )
        return self._financials
    
    @property
    def quarterly_financials(self):
        """
        Get quarterly income statement.
        
        Returns:
            pd.DataFrame: Quarterly income statement (latest → oldest columns)
            
        Example:
            >>> ticker = Ticker("AAPL")
            >>> qtr_financials = ticker.quarterly_financials
            >>> print(qtr_financials.loc['Total Revenue'])
        """
        if self._quarterly_financials is None:
            self._quarterly_financials = self._client.get_financials(
                self.ticker,
                statement='income',
                frequency='quarterly'
            )
        return self._quarterly_financials
    
    @property
    def balance_sheet(self):
        """
        Get annual balance sheet.
        
        Returns:
            pd.DataFrame: Annual balance sheet (latest → oldest columns)
            
        Example:
            >>> ticker = Ticker("AAPL")
            >>> balance = ticker.balance_sheet
            >>> print(balance.loc['Total Assets'])
        """
        if self._balance_sheet is None:
            self._balance_sheet = self._client.get_financials(
                self.ticker,
                statement='balance',
                frequency='annual'
            )
        return self._balance_sheet
    
    @property
    def quarterly_balance_sheet(self):
        """
        Get quarterly balance sheet.
        
        Returns:
            pd.DataFrame: Quarterly balance sheet (latest → oldest columns)
            
        Example:
            >>> ticker = Ticker("AAPL")
            >>> qtr_balance = ticker.quarterly_balance_sheet
            >>> print(qtr_balance.loc['Total Assets'])
        """
        if self._quarterly_balance_sheet is None:
            self._quarterly_balance_sheet = self._client.get_financials(
                self.ticker,
                statement='balance',
                frequency='quarterly'
            )
        return self._quarterly_balance_sheet
    
    @property
    def cashflow(self):
        """
        Get annual cash flow statement.
        
        Returns:
            pd.DataFrame: Annual cash flow (latest → oldest columns)
            
        Example:
            >>> ticker = Ticker("AAPL")
            >>> cf = ticker.cashflow
            >>> print(cf.loc['Operating Cash Flow'])
        """
        if self._cashflow is None:
            self._cashflow = self._client.get_financials(
                self.ticker,
                statement='cashflow',
                frequency='annual'
            )
        return self._cashflow
    
    @property
    def quarterly_cashflow(self):
        """
        Get quarterly cash flow statement.
        
        Returns:
            pd.DataFrame: Quarterly cash flow (latest → oldest columns)
            
        Example:
            >>> ticker = Ticker("AAPL")
            >>> qtr_cf = ticker.quarterly_cashflow
            >>> print(qtr_cf.loc['Operating Cash Flow'])
        """
        if self._quarterly_cashflow is None:
            self._quarterly_cashflow = self._client.get_financials(
                self.ticker,
                statement='cashflow',
                frequency='quarterly'
            )
        return self._quarterly_cashflow
    
    def __repr__(self) -> str:
        return f"fba_finance.Ticker('{self.ticker}')"
