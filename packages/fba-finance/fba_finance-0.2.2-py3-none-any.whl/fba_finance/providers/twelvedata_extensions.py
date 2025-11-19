"""
Extended API implementations for Twelve Data provider
"""
from typing import Dict
import pandas as pd


def get_calendar_twelvedata(symbol: str, api_key: str) -> Dict:
    """
    Twelve Data has earnings calendar API.
    """
    try:
        import requests
        
        url = f"https://api.twelvedata.com/earnings_calendar"
        params = {
            'symbol': symbol,
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'earnings' in data and data['earnings']:
                result = {}
                
                # Get next earnings
                next_earnings = data['earnings'][0]
                
                if 'date' in next_earnings:
                    result['Earnings Date'] = next_earnings['date']
                
                return result
        
        return {}
    except Exception as e:
        print(f"[twelvedata] Calendar error: {e}")
        return {}


def get_recommendations_twelvedata(symbol: str, api_key: str) -> pd.DataFrame:
    """
    Twelve Data does not have analyst recommendations in free tier.
    Return empty DataFrame.
    """
    return pd.DataFrame()


def get_financials_twelvedata(symbol: str, statement: str, frequency: str, api_key: str) -> pd.DataFrame:
    """Get financial statements from Twelve Data"""
    try:
        import requests
        
        # Map statement type to Twelve Data endpoint
        endpoint_map = {
            'income': 'income_statement',
            'balance': 'balance_sheet',
            'cashflow': 'cash_flow'
        }
        
        if statement not in endpoint_map:
            return pd.DataFrame()
        
        url = f"https://api.twelvedata.com/{endpoint_map[statement]}"
        params = {
            'symbol': symbol,
            'period': 'annual' if frequency == 'annual' else 'quarterly',
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for error
            if 'status' in data and data['status'] == 'error':
                print(f"[twelvedata] Financials API error: {data.get('message', 'Unknown error')}")
                return pd.DataFrame()
            
            # Twelve Data returns data in different formats based on statement
            if statement == 'income' and 'income_statement' in data:
                statements = data['income_statement']
            elif statement == 'balance' and 'balance_sheet' in data:
                statements = data['balance_sheet']
            elif statement == 'cashflow' and 'cash_flow' in data:
                statements = data['cash_flow']
            else:
                return pd.DataFrame()
            
            if not statements:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(statements)
            
            # Set fiscal date as index and transpose (yfinance format)
            if 'fiscal_date' in df.columns:
                df = df.set_index('fiscal_date')
                df = df.T
                
                # Convert to numeric where possible
                for col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                
                return df
        
        return pd.DataFrame()
    except Exception as e:
        print(f"[twelvedata] Financials error: {e}")
        return pd.DataFrame()
