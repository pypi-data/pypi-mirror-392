"""
Alpha Vantage API provider (free tier: 25 requests/day)
"""
from typing import Optional, List, Dict
from datetime import datetime
import pandas as pd

try:
    from alpha_vantage.timeseries import TimeSeries
    from alpha_vantage.cryptocurrencies import CryptoCurrencies
except ImportError:
    TimeSeries = None
    CryptoCurrencies = None

from .base import BaseProvider
from ..models import Quote, HistoricalData
from ..core import ProviderRateLimiter
from ..config import Config
from .alphavantage_extensions import (
    get_calendar_alphavantage,
    get_recommendations_alphavantage,
    get_financials_alphavantage
)


class AlphaVantageProvider(BaseProvider):
    """Alpha Vantage API provider"""
    
    def __init__(self, api_key: Optional[str] = None, rate_limiter: Optional[ProviderRateLimiter] = None):
        super().__init__("alphavantage")
        self.rate_limiter = rate_limiter
        self.api_key = api_key or Config.ALPHA_VANTAGE_API_KEY
        
        if TimeSeries is None:
            self._available = False
            self._last_error = "alpha_vantage not installed"
        elif not self.api_key:
            self._available = False
            self._last_error = "Alpha Vantage API key not configured"
        else:
            try:
                self.ts = TimeSeries(key=self.api_key, output_format='pandas')
                self.cc = CryptoCurrencies(key=self.api_key, output_format='pandas')
            except Exception as e:
                self._available = False
                self._last_error = f"Failed to initialize client: {e}"
    
    def get_quote(self, symbol: str) -> Optional[Quote]:
        """Get real-time quote"""
        if not self._available:
            return None
        
        try:
            if self.rate_limiter:
                self.rate_limiter.wait_if_needed("alphavantage")
            
            # Get intraday data (last minute)
            data, meta_data = self.ts.get_intraday(
                symbol=symbol,
                interval='1min',
                outputsize='compact'
            )
            
            if data is None or data.empty:
                return None
            
            # Get the latest row
            latest = data.iloc[0]
            timestamp = data.index[0]
            
            quote = Quote(
                symbol=symbol,
                timestamp=timestamp,
                price=float(latest['4. close']),
                open=float(latest['1. open']),
                high=float(latest['2. high']),
                low=float(latest['3. low']),
                close=float(latest['4. close']),
                volume=int(latest['5. volume']),
                source="alphavantage",
                metadata=meta_data
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
                self.rate_limiter.wait_if_needed("alphavantage")
            
            # Alpha Vantage has different functions for different intervals
            if interval in ["1m", "5m", "15m", "30m", "1h"]:
                # Intraday data
                av_interval = {
                    "1m": "1min", "5m": "5min", "15m": "15min",
                    "30m": "30min", "1h": "60min"
                }[interval]
                
                data, meta_data = self.ts.get_intraday(
                    symbol=symbol,
                    interval=av_interval,
                    outputsize='full'
                )
            else:
                # Daily data
                data, meta_data = self.ts.get_daily(
                    symbol=symbol,
                    outputsize='full'
                )
            
            if data is None or data.empty:
                return None
            
            # Filter by date range
            data = data.loc[start:end]
            
            # Standardize column names
            data = data.reset_index()
            data.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
            
            return HistoricalData(
                symbol=symbol,
                data=data,
                start_date=start,
                end_date=end,
                interval=interval,
                source="alphavantage",
                metadata=meta_data
            )
            
        except Exception as e:
            self._handle_error(e, f"get_historical({symbol})")
            return None
    
    def get_multiple_quotes(self, symbols: List[str]) -> List[Quote]:
        """Get quotes for multiple symbols (sequential due to rate limits)"""
        quotes = []
        
        for symbol in symbols:
            quote = self.get_quote(symbol)
            if quote:
                quotes.append(quote)
        
        return quotes
    
    # ========================================================================
    # Extended APIs
    # ========================================================================
    
    def get_calendar(self, symbol: str) -> Dict:
        """Get upcoming events calendar"""
        if not self._available or not self.api_key:
            return {}
        return get_calendar_alphavantage(symbol, self.api_key)
    
    def get_recommendations(self, symbol: str) -> pd.DataFrame:
        """Get analyst recommendations (not supported by Alpha Vantage)"""
        return pd.DataFrame()
    
    def get_financials(self, symbol: str, statement: str, frequency: str) -> pd.DataFrame:
        """Get financial statements"""
        if not self._available or not self.api_key:
            return pd.DataFrame()
        return get_financials_alphavantage(symbol, statement, frequency, self.api_key)
