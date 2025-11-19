"""
Extended API implementations for Alpha Vantage provider
"""
from typing import Dict
import pandas as pd
from datetime import datetime


def get_calendar_alphavantage(symbol: str, api_key: str) -> Dict:
    """
    Get calendar data from Alpha Vantage.
    Alpha Vantage has earnings calendar API.
    """
    try:
        import requests
        
        # Earnings calendar endpoint
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'EARNINGS_CALENDAR',
            'symbol': symbol,
            'apikey': api_key
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            # Alpha Vantage returns CSV for earnings calendar
            lines = response.text.strip().split('\n')
            if len(lines) > 1:
                # Parse first data row (next earnings)
                headers = lines[0].split(',')
                data = lines[1].split(',')
                
                result = {}
                
                # Extract earnings date
                if 'reportDate' in headers:
                    idx = headers.index('reportDate')
                    if idx < len(data):
                        result['Earnings Date'] = data[idx]
                
                return result
        
        return {}
    except Exception as e:
        print(f"[alphavantage] Calendar error: {e}")
        return {}


def get_recommendations_alphavantage(symbol: str, api_key: str) -> pd.DataFrame:
    """
    Alpha Vantage does not have analyst recommendations API.
    Return empty DataFrame.
    """
    return pd.DataFrame()


def get_financials_alphavantage(symbol: str, statement: str, frequency: str, api_key: str) -> pd.DataFrame:
    """Get financial statements from Alpha Vantage"""
    try:
        import requests
        
        # Map statement type to Alpha Vantage function
        function_map = {
            'income': 'INCOME_STATEMENT',
            'balance': 'BALANCE_SHEET',
            'cashflow': 'CASH_FLOW'
        }
        
        if statement not in function_map:
            return pd.DataFrame()
        
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': function_map[statement],
            'symbol': symbol,
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for error
            if 'Error Message' in data or 'Note' in data:
                error_msg = data.get('Error Message') or data.get('Note', '')
                print(f"[alphavantage] Financials API error: {error_msg}")
                return pd.DataFrame()
            
            # Get the right report type
            report_key = 'annualReports' if frequency == 'annual' else 'quarterlyReports'
            
            if report_key not in data:
                return pd.DataFrame()
            
            reports = data[report_key]
            
            if not reports:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(reports)
            
            # Set fiscal date as column name and transpose
            if 'fiscalDateEnding' in df.columns:
                df = df.set_index('fiscalDateEnding')
                df = df.T
                
                # Convert to numeric where possible
                for col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                
                return df
        
        return pd.DataFrame()
    except Exception as e:
        print(f"[alphavantage] Financials error: {e}")
        return pd.DataFrame()
