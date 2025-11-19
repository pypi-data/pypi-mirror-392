"""
Data models for financial data
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class QuoteType(Enum):
    """Type of financial instrument"""
    STOCK = "stock"
    ETF = "etf"
    INDEX = "index"
    FOREX = "forex"
    CRYPTO = "crypto"
    FUTURE = "future"
    OPTION = "option"
    MUTUAL_FUND = "mutual_fund"


@dataclass
class Quote:
    """Real-time or near-real-time quote data"""
    symbol: str
    timestamp: datetime
    price: float
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[int] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    bid_size: Optional[int] = None
    ask_size: Optional[int] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    previous_close: Optional[float] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    quote_type: Optional[QuoteType] = None
    exchange: Optional[str] = None
    currency: Optional[str] = None
    source: Optional[str] = None  # Which provider gave us this data
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "price": self.price,
        }
        
        # Add optional fields if present
        for field in ["open", "high", "low", "close", "volume", "bid", "ask",
                      "bid_size", "ask_size", "change", "change_percent",
                      "previous_close", "market_cap", "pe_ratio",
                      "fifty_two_week_high", "fifty_two_week_low",
                      "exchange", "currency", "source"]:
            value = getattr(self, field)
            if value is not None:
                result[field] = value
        
        if self.quote_type:
            result["quote_type"] = self.quote_type.value
            
        if self.metadata:
            result["metadata"] = self.metadata
            
        return result


@dataclass
class HistoricalData:
    """Historical OHLCV data"""
    symbol: str
    data: Any  # Pandas DataFrame with columns: date, open, high, low, close, volume
    start_date: datetime
    end_date: datetime
    interval: str  # 1m, 5m, 15m, 1h, 1d, 1wk, 1mo
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "symbol": self.symbol,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "interval": self.interval,
            "source": self.source,
            "data": self.data.to_dict("records") if hasattr(self.data, "to_dict") else self.data,
            "metadata": self.metadata,
        }


@dataclass
class ProviderStatus:
    """Status of a data provider"""
    name: str
    available: bool
    has_api_key: bool
    rate_limited: bool
    last_error: Optional[str] = None
    requests_count: int = 0
    last_request_time: Optional[datetime] = None
