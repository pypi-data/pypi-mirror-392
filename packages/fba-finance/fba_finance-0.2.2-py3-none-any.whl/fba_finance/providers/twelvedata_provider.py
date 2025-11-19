"""
Twelve Data API provider (free tier: 800 requests/day)
"""
from typing import Optional, List, Dict
from datetime import datetime
import pandas as pd

try:
    from twelvedata import TDClient
except ImportError:
    TDClient = None

from .base import BaseProvider
from ..models import Quote, HistoricalData
from ..core import ProviderRateLimiter
from ..config import Config
from .twelvedata_extensions import (
    get_calendar_twelvedata,
    get_recommendations_twelvedata,
    get_financials_twelvedata
)


class TwelveDataProvider(BaseProvider):
    """Twelve Data API provider"""
    
    def __init__(self, api_key: Optional[str] = None, rate_limiter: Optional[ProviderRateLimiter] = None):
        super().__init__("twelvedata")
        self.rate_limiter = rate_limiter
        self.api_key = api_key or Config.TWELVE_DATA_API_KEY
        
        if TDClient is None:
            self._available = False
            self._last_error = "twelvedata not installed"
        elif not self.api_key:
            self._available = False
            self._last_error = "Twelve Data API key not configured"
        else:
            try:
                self.client = TDClient(apikey=self.api_key)
            except Exception as e:
                self._available = False
                self._last_error = f"Failed to initialize client: {e}"
    
    def get_quote(self, symbol: str) -> Optional[Quote]:
        """Get real-time quote"""
        if not self._available:
            return None
        
        try:
            if self.rate_limiter:
                self.rate_limiter.wait_if_needed("twelvedata")
            
            # Get quote
            ts = self.client.time_series(
                symbol=symbol,
                interval="1min",
                outputsize=1
            )
            
            data = ts.as_json()
            
            if not data or 'values' not in data or not data['values']:
                return None
            
            latest = data['values'][0]
            
            quote = Quote(
                symbol=symbol,
                timestamp=datetime.strptime(latest['datetime'], "%Y-%m-%d %H:%M:%S"),
                price=float(latest['close']),
                open=float(latest['open']),
                high=float(latest['high']),
                low=float(latest['low']),
                close=float(latest['close']),
                volume=int(latest.get('volume', 0)) if latest.get('volume') else None,
                source="twelvedata",
                metadata=data.get('meta', {})
            )
            
            return quote
            
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
                self.rate_limiter.wait_if_needed("twelvedata")
            
            # Map interval format
            interval_map = {
                "1m": "1min", "5m": "5min", "15m": "15min", "30m": "30min",
                "1h": "1h", "1d": "1day", "1wk": "1week", "1mo": "1month"
            }
            td_interval = interval_map.get(interval, "1day")
            
            # Get historical data
            ts = self.client.time_series(
                symbol=symbol,
                interval=td_interval,
                start_date=start.strftime("%Y-%m-%d"),
                end_date=end.strftime("%Y-%m-%d"),
                outputsize=5000
            )
            
            df = ts.as_pandas()
            
            if df is None or df.empty:
                return None
            
            # Reset index and standardize columns to match yfinance format
            df = df.reset_index()
            col_map = {
                'open': 'Open', 'high': 'High', 'low': 'Low',
                'close': 'Close', 'volume': 'Volume',
                'datetime': 'Date', 'date': 'Date'
            }
            df.columns = [col_map.get(col.lower(), col) for col in df.columns]
            
            # Set date as index for compatibility with yfinance format
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"], utc=True).dt.tz_localize(None)
                df = df.set_index("Date")
            
            return HistoricalData(
                symbol=symbol,
                data=df,
                start_date=start,
                end_date=end,
                interval=interval,
                source="twelvedata"
            )
            
        except Exception as e:
            self._handle_error(e, f"get_historical({symbol})")
            return None
    
    def get_multiple_quotes(self, symbols: List[str]) -> List[Quote]:
        """Get quotes for multiple symbols"""
        quotes = []
        
        # Twelve Data supports batch requests
        try:
            if self.rate_limiter:
                self.rate_limiter.wait_if_needed("twelvedata")
            
            # Batch request (limit to 120 symbols per request in free tier)
            batch_size = 100
            for i in range(0, len(symbols), batch_size):
                batch = symbols[i:i+batch_size]
                
                for symbol in batch:
                    quote = self.get_quote(symbol)
                    if quote:
                        quotes.append(quote)
                        
        except Exception as e:
            self._handle_error(e, "get_multiple_quotes")
        
        return quotes
    
    # ========================================================================
    # Extended APIs
    # ========================================================================
    
    def get_calendar(self, symbol: str) -> Dict:
        """Get upcoming events calendar"""
        if not self._available or not self.api_key:
            return {}
        return get_calendar_twelvedata(symbol, self.api_key)
    
    def get_recommendations(self, symbol: str) -> pd.DataFrame:
        """Get analyst recommendations (not in free tier)"""
        return pd.DataFrame()
    
    def get_financials(self, symbol: str, statement: str, frequency: str) -> pd.DataFrame:
        """Get financial statements"""
        if not self._available or not self.api_key:
            return pd.DataFrame()
        return get_financials_twelvedata(symbol, statement, frequency, self.api_key)
