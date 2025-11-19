"""
Base provider interface
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from datetime import datetime
import pandas as pd

from ..models import Quote, HistoricalData


class BaseProvider(ABC):
    """Base class for all data providers"""
    
    def __init__(self, name: str):
        self.name = name
        self._available = True
        self._last_error = None
    
    @abstractmethod
    def get_quote(self, symbol: str) -> Optional[Quote]:
        """Get real-time quote for a symbol"""
        pass
    
    @abstractmethod
    def get_historical(self, 
                      symbol: str,
                      start: datetime,
                      end: datetime,
                      interval: str = "1d") -> Optional[HistoricalData]:
        """Get historical data for a symbol"""
        pass
    
    @abstractmethod
    def get_multiple_quotes(self, symbols: List[str]) -> List[Quote]:
        """Get quotes for multiple symbols (batch operation)"""
        pass
    
    @property
    def available(self) -> bool:
        """Check if provider is available"""
        return self._available
    
    @property
    def last_error(self) -> Optional[str]:
        """Get last error message"""
        return self._last_error
    
    def _handle_error(self, error: Exception, context: str = ""):
        """Handle and log errors"""
        self._last_error = f"{context}: {str(error)}" if context else str(error)
        print(f"[{self.name}] Error: {self._last_error}")
    
    # ========================================================================
    # Extended APIs - Optional implementations (not all providers support)
    # ========================================================================
    
    def get_calendar(self, symbol: str) -> Dict:
        """
        Get upcoming events calendar (earnings, dividends).
        Override in subclass if provider supports this.
        
        Returns:
            Dict with keys: 'Earnings Date', 'Ex-Dividend Date', 'Dividend Date'
        """
        raise NotImplementedError(f"{self.name} does not support calendar data")
    
    def get_recommendations(self, symbol: str) -> pd.DataFrame:
        """
        Get analyst recommendations history.
        Override in subclass if provider supports this.
        
        Returns:
            pd.DataFrame with columns: Date, Firm, To Rating, From Rating, Action
        """
        raise NotImplementedError(f"{self.name} does not support recommendations")
    
    def get_financials(self, 
                      symbol: str,
                      statement: str = 'income',
                      frequency: str = 'annual') -> pd.DataFrame:
        """
        Get financial statements.
        Override in subclass if provider supports this.
        
        Args:
            symbol: Ticker symbol
            statement: 'income', 'balance', or 'cashflow'
            frequency: 'annual' or 'quarterly'
        
        Returns:
            pd.DataFrame with financial line items as index, dates as columns
        """
        raise NotImplementedError(f"{self.name} does not support financials")
