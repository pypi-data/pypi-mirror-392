"""
Yahoo Finance provider using yfinance library
"""
from typing import Optional, List, Dict
from datetime import datetime
import pandas as pd

try:
    import yfinance as yf
except ImportError:
    yf = None

from .base import BaseProvider
from ..models import Quote, HistoricalData, QuoteType
from ..core import ProviderRateLimiter
from .yfinance_extensions import (
    get_calendar_yfinance,
    get_recommendations_yfinance,
    get_financials_yfinance
)


class YFinanceProvider(BaseProvider):
    """Yahoo Finance data provider using yfinance"""
    
    def __init__(self, rate_limiter: Optional[ProviderRateLimiter] = None):
        super().__init__("yfinance")
        self.rate_limiter = rate_limiter
        
        if yf is None:
            self._available = False
            self._last_error = "yfinance not installed"
    
    def get_quote(self, symbol: str) -> Optional[Quote]:
        """Get real-time quote"""
        if not self._available:
            return None
        
        try:
            if self.rate_limiter:
                self.rate_limiter.wait_if_needed("yfinance")
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price
            price = info.get("currentPrice") or info.get("regularMarketPrice")
            if not price:
                return None
            
            # Build quote object
            quote = Quote(
                symbol=symbol,
                timestamp=datetime.now(),
                price=price,
                open=info.get("regularMarketOpen"),
                high=info.get("regularMarketDayHigh"),
                low=info.get("regularMarketDayLow"),
                close=info.get("regularMarketPrice"),
                volume=info.get("regularMarketVolume"),
                bid=info.get("bid"),
                ask=info.get("ask"),
                bid_size=info.get("bidSize"),
                ask_size=info.get("askSize"),
                change=info.get("regularMarketChange"),
                change_percent=info.get("regularMarketChangePercent"),
                previous_close=info.get("previousClose"),
                market_cap=info.get("marketCap"),
                pe_ratio=info.get("trailingPE"),
                fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
                fifty_two_week_low=info.get("fiftyTwoWeekLow"),
                exchange=info.get("exchange"),
                currency=info.get("currency"),
                source="yfinance",
                metadata={"quote_type": info.get("quoteType")}
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
                self.rate_limiter.wait_if_needed("yfinance")
            
            ticker = yf.Ticker(symbol)
            
            # Map interval format
            interval_map = {
                "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
                "1h": "1h", "1d": "1d", "1wk": "1wk", "1mo": "1mo"
            }
            yf_interval = interval_map.get(interval, "1d")
            
            # Download data
            df = ticker.history(
                start=start,
                end=end,
                interval=yf_interval
            )
            
            if df.empty:
                return None
            
            # Standardize column names
            df.columns = [col.lower() for col in df.columns]
            df.reset_index(inplace=True)
            
            # Rename columns to standard format
            column_map = {
                "date": "date",
                "open": "open",
                "high": "high",
                "low": "low",
                "close": "close",
                "volume": "volume"
            }
            df = df.rename(columns=column_map)
            
            return HistoricalData(
                symbol=symbol,
                data=df,
                start_date=start,
                end_date=end,
                interval=interval,
                source="yfinance"
            )
            
        except Exception as e:
            self._handle_error(e, f"get_historical({symbol})")
            return None
    
    def get_multiple_quotes(self, symbols: List[str]) -> List[Quote]:
        """Get quotes for multiple symbols"""
        quotes = []
        
        try:
            if self.rate_limiter:
                self.rate_limiter.wait_if_needed("yfinance")
            
            # yfinance can download multiple tickers at once
            tickers = yf.Tickers(" ".join(symbols))
            
            for symbol in symbols:
                try:
                    ticker = tickers.tickers[symbol]
                    quote = self.get_quote(symbol)
                    if quote:
                        quotes.append(quote)
                except:
                    continue
                    
        except Exception as e:
            self._handle_error(e, "get_multiple_quotes")
            # Fallback to individual requests
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
        if not self._available:
            return {}
        return get_calendar_yfinance(symbol)
    
    def get_recommendations(self, symbol: str) -> pd.DataFrame:
        """Get analyst recommendations"""
        if not self._available:
            return pd.DataFrame()
        return get_recommendations_yfinance(symbol)
    
    def get_financials(self, symbol: str, statement: str, frequency: str) -> pd.DataFrame:
        """Get financial statements"""
        if not self._available:
            return pd.DataFrame()
        return get_financials_yfinance(symbol, statement, frequency)
