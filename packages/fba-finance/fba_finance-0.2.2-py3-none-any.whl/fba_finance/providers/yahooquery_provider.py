"""
Yahoo Finance provider using yahooquery library (alternative to yfinance)
"""
from typing import Optional, List, Dict
from datetime import datetime
import pandas as pd

try:
    from yahooquery import Ticker
except ImportError:
    Ticker = None

from .base import BaseProvider
from ..models import Quote, HistoricalData
from ..core import ProviderRateLimiter
from .yahooquery_extensions import (
    get_calendar_yahooquery,
    get_recommendations_yahooquery,
    get_financials_yahooquery
)


class YahooQueryProvider(BaseProvider):
    """Yahoo Finance data provider using yahooquery"""
    
    def __init__(self, rate_limiter: Optional[ProviderRateLimiter] = None):
        super().__init__("yahooquery")
        self.rate_limiter = rate_limiter
        
        if Ticker is None:
            self._available = False
            self._last_error = "yahooquery not installed"
    
    def get_quote(self, symbol: str) -> Optional[Quote]:
        """Get real-time quote"""
        if not self._available:
            return None
        
        try:
            if self.rate_limiter:
                self.rate_limiter.wait_if_needed("yahooquery")
            
            ticker = Ticker(symbol)
            quote_data = ticker.price
            
            if isinstance(quote_data, dict) and symbol in quote_data:
                data = quote_data[symbol]
                
                # Check for error
                if isinstance(data, str) or "error" in str(data).lower():
                    return None
                
                price = data.get("regularMarketPrice")
                if not price:
                    return None
                
                quote = Quote(
                    symbol=symbol,
                    timestamp=datetime.now(),
                    price=price,
                    open=data.get("regularMarketOpen"),
                    high=data.get("regularMarketDayHigh"),
                    low=data.get("regularMarketDayLow"),
                    close=data.get("regularMarketPrice"),
                    volume=data.get("regularMarketVolume"),
                    change=data.get("regularMarketChange"),
                    change_percent=data.get("regularMarketChangePercent"),
                    previous_close=data.get("regularMarketPreviousClose"),
                    market_cap=data.get("marketCap"),
                    exchange=data.get("exchange"),
                    currency=data.get("currency"),
                    source="yahooquery"
                )
                
                return quote
            
            return None
            
        except Exception as e:
            self._handle_error(e, f"get_quote({symbol})")
            return None
    
    def get_historical(self,
                      symbol: str,
                      start: datetime,
                      end: datetime,
                      interval: str = "1d") -> Optional[HistoricalData]:
        """Get historical data"""
        if not self._available:
            return None
        
        try:
            if self.rate_limiter:
                self.rate_limiter.wait_if_needed("yahooquery")
            
            ticker = Ticker(symbol)
            
            # yahooquery uses different interval notation
            df = ticker.history(
                start=start.strftime("%Y-%m-%d"),
                end=end.strftime("%Y-%m-%d"),
                interval=interval
            )
            
            if df is None or df.empty:
                return None
            
            # Reset index to get symbol and date as columns
            df = df.reset_index()
            
            # Standardize column names to match yfinance format
            col_map = {
                'open': 'Open', 'high': 'High', 'low': 'Low', 
                'close': 'Close', 'volume': 'Volume', 
                'adjclose': 'Adj Close', 'dividends': 'Dividends',
                'symbol': 'Symbol', 'date': 'Date'
            }
            df.columns = [col_map.get(col.lower(), col) for col in df.columns]
            
            # Set date as index for compatibility with yfinance format
            if "Date" in df.columns:
                # Convert to datetime UTC then remove timezone (yfinance compatibility)
                df["Date"] = pd.to_datetime(df["Date"], utc=True).dt.tz_localize(None)
                df = df.set_index("Date")
            
            return HistoricalData(
                symbol=symbol,
                data=df,
                start_date=start,
                end_date=end,
                interval=interval,
                source="yahooquery"
            )
            
        except Exception as e:
            self._handle_error(e, f"get_historical({symbol})")
            return None
    
    def get_multiple_quotes(self, symbols: List[str]) -> List[Quote]:
        """Get quotes for multiple symbols - yahooquery is efficient with batch requests"""
        if not self._available:
            return []
        
        quotes = []
        
        try:
            if self.rate_limiter:
                self.rate_limiter.wait_if_needed("yahooquery")
            
            # yahooquery can handle multiple symbols efficiently
            ticker = Ticker(symbols)
            quote_data = ticker.price
            
            for symbol in symbols:
                if symbol in quote_data:
                    data = quote_data[symbol]
                    
                    if isinstance(data, dict) and "regularMarketPrice" in data:
                        price = data.get("regularMarketPrice")
                        
                        quote = Quote(
                            symbol=symbol,
                            timestamp=datetime.now(),
                            price=price,
                            open=data.get("regularMarketOpen"),
                            high=data.get("regularMarketDayHigh"),
                            low=data.get("regularMarketDayLow"),
                            close=data.get("regularMarketPrice"),
                            volume=data.get("regularMarketVolume"),
                            change=data.get("regularMarketChange"),
                            change_percent=data.get("regularMarketChangePercent"),
                            previous_close=data.get("regularMarketPreviousClose"),
                            market_cap=data.get("marketCap"),
                            exchange=data.get("exchange"),
                            currency=data.get("currency"),
                            source="yahooquery"
                        )
                        quotes.append(quote)
                        
        except Exception as e:
            self._handle_error(e, "get_multiple_quotes")
        
        return quotes
    
    # ========================================================================
    # Extended APIs
    # ========================================================================
    
    def get_calendar(self, symbol: str) -> Dict:
        """Get upcoming events calendar"""
        if not self._available:
            return {}
        return get_calendar_yahooquery(symbol)
    
    def get_recommendations(self, symbol: str) -> pd.DataFrame:
        """Get analyst recommendations"""
        if not self._available:
            return pd.DataFrame()
        return get_recommendations_yahooquery(symbol)
    
    def get_financials(self, symbol: str, statement: str, frequency: str) -> pd.DataFrame:
        """Get financial statements"""
        if not self._available:
            return pd.DataFrame()
        return get_financials_yahooquery(symbol, statement, frequency)
