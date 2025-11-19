"""
yfinance-compatible download() function for batch operations
"""
from typing import Union, List, Optional
from datetime import datetime, timedelta
import pandas as pd

from ..client import FinanceClient


def download(
    tickers: Union[str, List[str]],
    period: str = "1mo",
    interval: str = "1d",
    start: Optional[str] = None,
    end: Optional[str] = None,
    group_by: str = 'column',
    auto_adjust: bool = True,
    prepost: bool = False,
    threads: bool = True,
    proxy: Optional[str] = None,
    **kwargs
) -> pd.DataFrame:
    """
    Download historical data for multiple tickers (yfinance compatible).
    
    This is a drop-in replacement for yfinance.download() with the same API.
    
    Args:
        tickers: Single ticker string or list of ticker strings
        period: Period to download ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        interval: Data interval ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
        start: Start date string (YYYY-MM-DD) or datetime
        end: End date string (YYYY-MM-DD) or datetime  
        group_by: 'column' or 'ticker' - how to group multi-ticker results
        auto_adjust: Adjust all OHLC automatically (ignored)
        prepost: Include pre and post market data (ignored)
        threads: Use multi-threading for faster downloads (ignored, always uses async)
        proxy: Proxy URL (ignored)
        
    Returns:
        pd.DataFrame: 
            - Single ticker: DataFrame with columns [Open, High, Low, Close, Volume, Dividends, Stock Splits]
            - Multiple tickers: MultiIndex DataFrame grouped by 'column' or 'ticker'
            
    Examples:
        # Single ticker
        >>> data = download("AAPL", period="1mo")
        >>> print(data['Close'].iloc[-1])
        
        # Multiple tickers
        >>> data = download(["AAPL", "MSFT", "GOOGL"], period="1y", interval="1d")
        >>> print(data['Close'])  # All tickers' close prices
        
        # With date range
        >>> data = download("AAPL", start="2024-01-01", end="2024-12-31")
        
        # Group by ticker
        >>> data = download(["AAPL", "MSFT"], period="1mo", group_by='ticker')
        >>> print(data['AAPL'])  # All columns for AAPL
    """
    # Normalize tickers input
    if isinstance(tickers, str):
        ticker_list = [t.strip() for t in tickers.split()]
    else:
        ticker_list = tickers
    
    # Parse dates
    if start and end:
        start_dt = pd.to_datetime(start) if isinstance(start, str) else start
        end_dt = pd.to_datetime(end) if isinstance(end, str) else end
    else:
        end_dt = datetime.now()
        # Map period to days
        period_map = {
            '1d': 1, '5d': 5,
            '1mo': 30, '3mo': 90, '6mo': 180,
            '1y': 365, '2y': 730, '5y': 1825, '10y': 3650,
            'ytd': (datetime.now() - datetime(datetime.now().year, 1, 1)).days,
            'max': 36500
        }
        days = period_map.get(period, 30)
        start_dt = end_dt - timedelta(days=days)
    
    # Initialize client
    client = FinanceClient(use_cache=True)
    
    # Single ticker - return simple DataFrame
    if len(ticker_list) == 1:
        return _download_single(client, ticker_list[0], start_dt, end_dt, interval)
    
    # Multiple tickers - return MultiIndex DataFrame
    return _download_multiple(client, ticker_list, start_dt, end_dt, interval, group_by)


def _download_single(
    client: FinanceClient,
    ticker: str,
    start: datetime,
    end: datetime,
    interval: str
) -> pd.DataFrame:
    """Download single ticker data"""
    data = client.get_historical(ticker, start=start, end=end, interval=interval)
    
    if not data or data.data is None or data.data.empty:
        return _get_empty_dataframe()
    
    df = data.data.copy()
    
    # Standardize columns
    column_mapping = {
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume',
        'date': 'Date'
    }
    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
    
    # Ensure required columns
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        if col not in df.columns:
            df[col] = 0.0
    
    # Add Dividends and Stock Splits
    if 'Dividends' not in df.columns:
        df['Dividends'] = 0.0
    if 'Stock Splits' not in df.columns:
        df['Stock Splits'] = 0.0
    
    # Set DatetimeIndex with timezone normalization
    if 'Date' in df.columns:
        # Convert to datetime UTC then remove timezone (yfinance compatibility)
        df['Date'] = pd.to_datetime(df['Date'], utc=True).dt.tz_localize(None)
        df = df.set_index('Date')
    elif 'date' in df.columns:
        # Convert to datetime UTC then remove timezone (yfinance compatibility)
        df['date'] = pd.to_datetime(df['date'], utc=True).dt.tz_localize(None)
        df = df.set_index('date')
        df.index.name = 'Date'
    
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
    
    df = df.sort_index()
    
    # Column order
    column_order = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
    df = df[[col for col in column_order if col in df.columns]]
    
    return df


def _download_multiple(
    client: FinanceClient,
    tickers: List[str],
    start: datetime,
    end: datetime,
    interval: str,
    group_by: str
) -> pd.DataFrame:
    """Download multiple tickers data and combine"""
    
    all_data = {}
    
    # Download data for each ticker
    for ticker in tickers:
        df = _download_single(client, ticker, start, end, interval)
        if not df.empty:
            all_data[ticker] = df
    
    if not all_data:
        return _get_empty_dataframe()
    
    # Combine based on group_by
    if group_by == 'ticker':
        # MultiIndex with ticker as first level
        combined = pd.concat(all_data, axis=0, keys=all_data.keys())
        combined.index.names = ['Ticker', 'Date']
        return combined
    
    else:  # group_by == 'column' (default)
        # MultiIndex with column as first level
        # Align all DataFrames to same index
        all_dates = pd.DatetimeIndex([])
        for df in all_data.values():
            all_dates = all_dates.union(df.index)
        all_dates = all_dates.sort_values()
        
        # Reindex all DataFrames
        aligned_data = {}
        for ticker, df in all_data.items():
            aligned_data[ticker] = df.reindex(all_dates)
        
        # Create MultiIndex DataFrame
        columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
        multi_columns = pd.MultiIndex.from_product([columns, sorted(all_data.keys())], names=['Price', 'Ticker'])
        
        combined = pd.DataFrame(index=all_dates, columns=multi_columns)
        combined.index.name = 'Date'
        
        for ticker, df in aligned_data.items():
            for col in columns:
                if col in df.columns:
                    combined[(col, ticker)] = df[col]
        
        return combined


def _get_empty_dataframe() -> pd.DataFrame:
    """Return empty DataFrame with correct structure"""
    df = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits'])
    df.index = pd.DatetimeIndex([])
    df.index.name = 'Date'
    return df
