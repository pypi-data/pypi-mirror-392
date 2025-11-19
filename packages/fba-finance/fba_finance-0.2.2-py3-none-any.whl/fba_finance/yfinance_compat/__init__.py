"""
yfinance compatibility layer
Provides drop-in replacement for yfinance API
"""

from .ticker import Ticker
from .download import download

__all__ = ['Ticker', 'download']
