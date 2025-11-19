"""
FBA Finance Library - Core Module
Multi-source financial data aggregator with anti-rate-limiting

Version 0.2.0 - Smart Portfolio API (Option A)
"""

__version__ = "0.2.2"
__author__ = "Fausto Bandini"

from .client import FinanceClient
from .models import Quote, HistoricalData, QuoteType
from .config import Config

# NEW: Smart Portfolio API (Option A)
from .portfolio import RealtimePortfolio, OperationMode, MODES

# yfinance compatibility layer
from .yfinance_compat import Ticker, download

# Screener module
from .screener import (
    get_top_tickers,
    get_sector_tickers,
    get_market_tickers,
    get_available_sectors,
    get_ticker_count_by_market,
    get_ticker_count_by_sector,
)

# Market hours module
from .market_hours import (
    MarketHours,
    is_market_open,
    get_market_state,
    next_market_open,
    next_market_close,
    get_market_hours,
    get_supported_exchanges,
)

# Usage tracking module (NEW in v0.2.0)
from .usage_tracker import get_usage_tracker, UsageTracker

__all__ = [
    # Core API
    "FinanceClient", 
    "Quote", 
    "HistoricalData", 
    "QuoteType", 
    "Config",
    # Smart Portfolio API (NEW in v0.2.0)
    "RealtimePortfolio",
    "OperationMode",
    "MODES",
    # yfinance compatibility
    "Ticker",
    "download",
    # Screener
    "get_top_tickers",
    "get_sector_tickers",
    "get_market_tickers",
    "get_available_sectors",
    "get_ticker_count_by_market",
    "get_ticker_count_by_sector",
    # Market Hours
    "MarketHours",
    "is_market_open",
    "get_market_state",
    "next_market_open",
    "next_market_close",
    "get_market_hours",
    "get_supported_exchanges",
    # Usage Tracking (NEW in v0.2.0)
    "get_usage_tracker",
    "UsageTracker",
]
