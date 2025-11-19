"""
Extended API implementations for YahooQuery provider
"""
from typing import Dict
import pandas as pd
from yahooquery import Ticker as YQTicker


def get_calendar_yahooquery(symbol: str) -> Dict:
    """Get calendar data from YahooQuery"""
    try:
        ticker = YQTicker(symbol)
        calendar = ticker.calendar_events
        
        if isinstance(calendar, dict) and symbol in calendar:
            data = calendar[symbol]
            
            result = {}
            
            # Earnings date
            if 'earnings' in data and 'earningsDate' in data['earnings']:
                result['Earnings Date'] = data['earnings']['earningsDate']
            
            # Dividend dates
            if 'dividendDate' in data:
                result['Dividend Date'] = data['dividendDate']
            if 'exDividendDate' in data:
                result['Ex-Dividend Date'] = data['exDividendDate']
            
            return result
        
        return {}
    except Exception as e:
        print(f"[yahooquery] Calendar error: {e}")
        return {}


def get_recommendations_yahooquery(symbol: str) -> pd.DataFrame:
    """Get analyst recommendations from YahooQuery"""
    try:
        ticker = YQTicker(symbol)
        recs = ticker.recommendation_trend
        
        if isinstance(recs, pd.DataFrame) and not recs.empty:
            # YahooQuery returns DataFrame with columns like:
            # period, strongBuy, buy, hold, sell, strongSell
            return recs
        
        return pd.DataFrame()
    except Exception as e:
        print(f"[yahooquery] Recommendations error: {e}")
        return pd.DataFrame()


def get_financials_yahooquery(symbol: str, statement: str, frequency: str) -> pd.DataFrame:
    """Get financial statements from YahooQuery"""
    try:
        ticker = YQTicker(symbol)
        
        # Map statement type
        if statement == 'income':
            if frequency == 'annual':
                data = ticker.income_statement(frequency='a')
            else:
                data = ticker.income_statement(frequency='q')
        elif statement == 'balance':
            if frequency == 'annual':
                data = ticker.balance_sheet(frequency='a')
            else:
                data = ticker.balance_sheet(frequency='q')
        elif statement == 'cashflow':
            if frequency == 'annual':
                data = ticker.cash_flow(frequency='a')
            else:
                data = ticker.cash_flow(frequency='q')
        else:
            return pd.DataFrame()
        
        if isinstance(data, pd.DataFrame) and not data.empty:
            # YahooQuery returns DataFrame with symbol in multi-index
            # We need to extract just this symbol's data
            if symbol in data.index.get_level_values(0):
                df = data.loc[symbol]
                # Transpose so dates are columns (yfinance format)
                df = df.T
                return df
        
        return pd.DataFrame()
    except Exception as e:
        print(f"[yahooquery] Financials error: {e}")
        return pd.DataFrame()
