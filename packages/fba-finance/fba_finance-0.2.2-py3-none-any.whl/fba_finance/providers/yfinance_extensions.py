"""
Extended API implementations for YFinance provider
"""
from typing import Dict
import pandas as pd
import yfinance as yf


def get_calendar_yfinance(symbol: str) -> Dict:
    """Get calendar data from yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        calendar = ticker.calendar
        
        if calendar and isinstance(calendar, dict):
            return calendar
        
        return {}
    except Exception as e:
        print(f"[yfinance] Calendar error: {e}")
        return {}


def get_recommendations_yfinance(symbol: str) -> pd.DataFrame:
    """Get analyst recommendations from yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        recs = ticker.recommendations
        
        if recs is not None and isinstance(recs, pd.DataFrame) and not recs.empty:
            return recs
        
        return pd.DataFrame()
    except Exception as e:
        print(f"[yfinance] Recommendations error: {e}")
        return pd.DataFrame()


def get_financials_yfinance(symbol: str, statement: str, frequency: str) -> pd.DataFrame:
    """Get financial statements from yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        
        # Map statement type
        if statement == 'income':
            if frequency == 'annual':
                data = ticker.financials  # Annual income statement
            else:
                data = ticker.quarterly_financials
        elif statement == 'balance':
            if frequency == 'annual':
                data = ticker.balance_sheet
            else:
                data = ticker.quarterly_balance_sheet
        elif statement == 'cashflow':
            if frequency == 'annual':
                data = ticker.cashflow
            else:
                data = ticker.quarterly_cashflow
        else:
            return pd.DataFrame()
        
        if data is not None and isinstance(data, pd.DataFrame) and not data.empty:
            return data
        
        return pd.DataFrame()
    except Exception as e:
        print(f"[yfinance] Financials error: {e}")
        return pd.DataFrame()
