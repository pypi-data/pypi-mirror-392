"""
Market Hours Management for Global Exchanges

This module provides comprehensive market hours tracking for 15 major global exchanges,
including timezone handling, holiday calendars, and real-time market state detection.

Features:
- Real-time market open/closed status
- Pre-market and after-hours detection
- Holiday calendar for 2025
- Timezone-aware datetime handling
- Next open/close time calculation
- Support for 15 global exchanges

Supported Exchanges:
- NYSE, NASDAQ (US)
- LSE (London)
- XETRA (Germany)
- Euronext Paris
- SIX Swiss Exchange
- TSE (Tokyo)
- HKEX (Hong Kong)
- SSE, SZSE (China)
- NSE (India)
- ASX (Australia)
- TSX (Canada)
- BMV (Mexico)
- B3 (Brazil)
"""

from datetime import datetime, time, timedelta
from typing import Optional, Dict, Tuple, List
from zoneinfo import ZoneInfo
import warnings


# Exchange configurations: (timezone, open_time, close_time)
EXCHANGE_HOURS = {
    # US Markets
    "NYSE": ("America/New_York", time(9, 30), time(16, 0)),
    "NASDAQ": ("America/New_York", time(9, 30), time(16, 0)),
    "AMEX": ("America/New_York", time(9, 30), time(16, 0)),
    
    # European Markets
    "LSE": ("Europe/London", time(8, 0), time(16, 30)),
    "XETRA": ("Europe/Berlin", time(9, 0), time(17, 30)),
    "EPA": ("Europe/Paris", time(9, 0), time(17, 30)),  # Euronext Paris
    "SIX": ("Europe/Zurich", time(9, 0), time(17, 30)),  # Swiss
    
    # Asian Markets
    "TSE": ("Asia/Tokyo", time(9, 0), time(15, 0)),
    "HKEX": ("Asia/Hong_Kong", time(9, 30), time(16, 0)),
    "SSE": ("Asia/Shanghai", time(9, 30), time(15, 0)),  # Shanghai
    "SZSE": ("Asia/Shanghai", time(9, 30), time(15, 0)),  # Shenzhen
    "NSE": ("Asia/Kolkata", time(9, 15), time(15, 30)),  # India
    
    # Other Markets
    "ASX": ("Australia/Sydney", time(10, 0), time(16, 0)),
    "TSX": ("America/Toronto", time(9, 30), time(16, 0)),  # Canada
    "BMV": ("America/Mexico_City", time(8, 30), time(15, 0)),  # Mexico
    "B3": ("America/Sao_Paulo", time(10, 0), time(17, 0)),  # Brazil
}

# Pre-market and after-hours
PRE_MARKET_HOURS = {
    "NYSE": time(4, 0),
    "NASDAQ": time(4, 0),
    "AMEX": time(4, 0),
}

AFTER_HOURS = {
    "NYSE": time(20, 0),
    "NASDAQ": time(20, 0),
    "AMEX": time(20, 0),
}

# Multi-year Holiday Calendars (2025-2030)
# Updated annually with official exchange calendars
# Last update: November 2025

HOLIDAYS_BY_YEAR = {
    2025: {
        "NYSE": [
            "2025-01-01",  # New Year's Day
            "2025-01-20",  # Martin Luther King Jr. Day
            "2025-02-17",  # Presidents Day
            "2025-04-18",  # Good Friday
            "2025-05-26",  # Memorial Day
            "2025-06-19",  # Juneteenth
            "2025-07-04",  # Independence Day
            "2025-09-01",  # Labor Day
            "2025-11-27",  # Thanksgiving
            "2025-12-25",  # Christmas
        ],
        "NASDAQ": [
            "2025-01-01", "2025-01-20", "2025-02-17", "2025-04-18",
            "2025-05-26", "2025-06-19", "2025-07-04", "2025-09-01",
            "2025-11-27", "2025-12-25",
        ],
            "LSE": [
            "2025-01-01",  # New Year's Day
            "2025-04-18",  # Good Friday
            "2025-04-21",  # Easter Monday
            "2025-05-05",  # Early May Bank Holiday
            "2025-05-26",  # Spring Bank Holiday
            "2025-08-25",  # Summer Bank Holiday
            "2025-12-25",  # Christmas Day
            "2025-12-26",  # Boxing Day
        ],
            "XETRA": [
            "2025-01-01",  # New Year's Day
            "2025-04-18",  # Good Friday
            "2025-04-21",  # Easter Monday
            "2025-05-01",  # Labour Day
            "2025-12-24",  # Christmas Eve
            "2025-12-25",  # Christmas Day
            "2025-12-26",  # Boxing Day
            "2025-12-31",  # New Year's Eve
        ],
            "TSE": [
            "2025-01-01", "2025-01-02", "2025-01-03",  # New Year
            "2025-01-13",  # Coming of Age Day
            "2025-02-11",  # National Foundation Day
            "2025-02-23",  # Emperor's Birthday
            "2025-03-20",  # Spring Equinox
            "2025-04-29",  # Showa Day
            "2025-05-03",  # Constitution Day
            "2025-05-04",  # Greenery Day
            "2025-05-05",  # Children's Day
            "2025-07-21",  # Marine Day
            "2025-08-11",  # Mountain Day
            "2025-09-15",  # Respect for the Aged Day
            "2025-09-23",  # Autumn Equinox
            "2025-10-13",  # Sports Day
            "2025-11-03",  # Culture Day
            "2025-11-23",  # Labour Thanksgiving Day
            "2025-12-31",  # New Year's Eve
        ],
            "HKEX": [
            "2025-01-01",  # New Year's Day
            "2025-01-29", "2025-01-30", "2025-01-31",  # Chinese New Year
            "2025-04-04",  # Ching Ming
            "2025-04-18",  # Good Friday
            "2025-04-21",  # Easter Monday
            "2025-05-01",  # Labour Day
            "2025-05-05",  # Buddha's Birthday
            "2025-06-02",  # Dragon Boat Festival
            "2025-07-01",  # HK SAR Establishment Day
            "2025-10-01",  # National Day
            "2025-10-07",  # Day after Mid-Autumn Festival
            "2025-10-11",  # Chung Yeung Festival
            "2025-12-25",  # Christmas
            "2025-12-26",  # Boxing Day
        ],
            "SSE": [
            "2025-01-01",  # New Year's Day
            "2025-01-28", "2025-01-29", "2025-01-30", "2025-01-31", "2025-02-03", "2025-02-04",  # CNY
            "2025-04-04", "2025-04-05", "2025-04-06",  # Qingming
            "2025-05-01", "2025-05-02", "2025-05-03",  # Labour Day
            "2025-05-31", "2025-06-02",  # Dragon Boat
            "2025-10-01", "2025-10-02", "2025-10-03", "2025-10-04", "2025-10-05", "2025-10-06", "2025-10-07",  # National Day
        ],
            "NSE": [
            "2025-01-26",  # Republic Day
            "2025-03-14",  # Holi
            "2025-03-31",  # Id-Ul-Fitr
            "2025-04-10",  # Mahavir Jayanti
            "2025-04-18",  # Good Friday
            "2025-05-01",  # Maharashtra Day
            "2025-08-15",  # Independence Day
            "2025-10-02",  # Gandhi Jayanti
            "2025-10-22",  # Dussehra
            "2025-11-12",  # Diwali
            "2025-11-13",  # Diwali (Balipratipada)
            "2025-12-25",  # Christmas
        ],
            "ASX": [
            "2025-01-01",  # New Year's Day
            "2025-01-27",  # Australia Day
            "2025-04-18",  # Good Friday
            "2025-04-21",  # Easter Monday
            "2025-04-25",  # ANZAC Day
            "2025-06-09",  # Queen's Birthday
            "2025-12-25",  # Christmas Day
            "2025-12-26",  # Boxing Day
        ],
            "TSX": [
            "2025-01-01",  # New Year's Day
            "2025-02-17",  # Family Day
            "2025-04-18",  # Good Friday
            "2025-05-19",  # Victoria Day
            "2025-07-01",  # Canada Day
            "2025-08-04",  # Civic Holiday
            "2025-09-01",  # Labour Day
            "2025-10-13",  # Thanksgiving
            "2025-12-25",  # Christmas Day
            "2025-12-26",  # Boxing Day
        ],
        "B3": ["2025-01-01", "2025-04-18", "2025-05-01", "2025-12-25"],
        "BMV": ["2025-01-01", "2025-05-01", "2025-09-16", "2025-12-25"],
    },
    2026: {
        "NYSE": [
            "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03",
            "2026-05-25", "2026-06-19", "2026-07-03", "2026-09-07",
            "2026-11-26", "2026-12-25",
        ],
        "NASDAQ": [
            "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03",
            "2026-05-25", "2026-06-19", "2026-07-03", "2026-09-07",
            "2026-11-26", "2026-12-25",
        ],
        "LSE": [
            "2026-01-01", "2026-04-03", "2026-04-06", "2026-05-04",
            "2026-05-25", "2026-08-31", "2026-12-25", "2026-12-28",
        ],
        "XETRA": [
            "2026-01-01", "2026-04-03", "2026-04-06", "2026-05-01",
            "2026-12-24", "2026-12-25", "2026-12-31",
        ],
        "TSE": [
            "2026-01-01", "2026-01-02", "2026-01-03", "2026-01-12",
            "2026-02-11", "2026-02-23", "2026-03-20", "2026-04-29",
            "2026-05-03", "2026-05-04", "2026-05-05", "2026-07-20",
            "2026-08-11", "2026-09-21", "2026-09-22", "2026-10-12",
            "2026-11-03", "2026-11-23", "2026-12-31",
        ],
        "HKEX": [
            "2026-01-01", "2026-02-17", "2026-02-18", "2026-02-19",
            "2026-04-03", "2026-04-06", "2026-04-25", "2026-05-01",
            "2026-05-19", "2026-07-01", "2026-10-01", "2026-10-26",
            "2026-12-25", "2026-12-26",
        ],
        "SSE": [
            "2026-01-01", "2026-02-16", "2026-02-17", "2026-02-18", "2026-02-19", "2026-02-20",
            "2026-04-04", "2026-04-05", "2026-04-06",
            "2026-05-01", "2026-05-02", "2026-05-03",
            "2026-06-09", "2026-06-10", "2026-06-11",
            "2026-10-01", "2026-10-02", "2026-10-03", "2026-10-04", "2026-10-05", "2026-10-06", "2026-10-07",
        ],
        "NSE": [
            "2026-01-26", "2026-03-05", "2026-03-21", "2026-03-30",
            "2026-04-03", "2026-04-06", "2026-05-01", "2026-08-15",
            "2026-10-02", "2026-10-12", "2026-11-01", "2026-11-02", "2026-12-25",
        ],
        "ASX": [
            "2026-01-01", "2026-01-26", "2026-04-03", "2026-04-06",
            "2026-04-27", "2026-06-08", "2026-12-25", "2026-12-28",
        ],
        "TSX": [
            "2026-01-01", "2026-02-16", "2026-04-03", "2026-05-18",
            "2026-07-01", "2026-08-03", "2026-09-07", "2026-10-12",
            "2026-12-25", "2026-12-28",
        ],
        "B3": ["2026-01-01", "2026-04-03", "2026-05-01", "2026-12-25"],
        "BMV": ["2026-01-01", "2026-05-01", "2026-09-16", "2026-12-25"],
    },
    # 2027-2030: Add more years as needed
    # Library will show warning if year not available
}

# Copy holidays to similar exchanges for all years
for year_data in HOLIDAYS_BY_YEAR.values():
    if "NYSE" in year_data:
        year_data["AMEX"] = year_data["NYSE"]
    if "SSE" in year_data:
        year_data["SZSE"] = year_data["SSE"]
    if "XETRA" in year_data:
        year_data["EPA"] = year_data["XETRA"]
        year_data["SIX"] = year_data["XETRA"]

# Early closes (markets close early, typically 13:00 instead of regular time)
# Format: "YYYY-MM-DD" for dates with early close
EARLY_CLOSES = {
    2025: {
        "NYSE": ["2025-07-03", "2025-11-28", "2025-12-24"],  # Day before Independence Day, Black Friday, Christmas Eve
        "NASDAQ": ["2025-07-03", "2025-11-28", "2025-12-24"],
    },
    2026: {
        "NYSE": ["2026-07-02", "2026-11-27", "2026-12-24"],
        "NASDAQ": ["2026-07-02", "2026-11-27", "2026-12-24"],
    },
}


class MarketHours:
    """
    Market hours manager for global exchanges.
    
    Provides real-time market status, holiday detection, and timezone handling.
    
    Example:
        >>> mh = MarketHours()
        >>> mh.is_market_open("NYSE")
        True
        >>> mh.get_market_state("NASDAQ")
        'REGULAR'
        >>> mh.next_market_open("LSE")
        datetime.datetime(2025, 11, 18, 8, 0, tzinfo=ZoneInfo('Europe/London'))
    """
    
    def __init__(self):
        """Initialize market hours manager"""
        self.exchange_hours = EXCHANGE_HOURS
        self.pre_market = PRE_MARKET_HOURS
        self.after_hours = AFTER_HOURS
        self.holidays_by_year = HOLIDAYS_BY_YEAR
        self.early_closes = EARLY_CLOSES
        self._warned_years = set()  # Track which years we've warned about
    
    def _get_holidays_for_year(self, year: int, exchange: str) -> List[str]:
        """
        Get holiday list for specific year with intelligent fallback.
        
        Args:
            year: Year to get holidays for
            exchange: Exchange code
            
        Returns:
            List of holiday date strings (YYYY-MM-DD format)
        """
        # Try exact year
        if year in self.holidays_by_year:
            return self.holidays_by_year[year].get(exchange, [])
        
        # Fallback: use most recent year available
        available_years = sorted(self.holidays_by_year.keys())
        if not available_years:
            return []
        
        fallback_year = max(available_years)
        
        # Warn once per year (not per call)
        if year not in self._warned_years:
            warnings.warn(
                f"Holiday calendar for year {year} not available. "
                f"Using {fallback_year} calendar as fallback. "
                f"Please update fba_finance library for accurate {year} holidays.",
                UserWarning
            )
            self._warned_years.add(year)
        
        # Get holidays from fallback year and adjust dates to requested year
        fallback_holidays = self.holidays_by_year[fallback_year].get(exchange, [])
        
        # Convert dates from fallback year to requested year
        adjusted_holidays = []
        for holiday_str in fallback_holidays:
            # Parse date from fallback year
            holiday_date = datetime.strptime(holiday_str, "%Y-%m-%d")
            # Create same date in requested year
            adjusted_date = holiday_date.replace(year=year)
            adjusted_holidays.append(adjusted_date.strftime("%Y-%m-%d"))
        
        return adjusted_holidays
    
    def _get_exchange_for_symbol(self, symbol: str) -> str:
        """
        Infer exchange from symbol suffix.
        
        Args:
            symbol: Ticker symbol (e.g., "AAPL", "0700.HK", "BMW.DE")
            
        Returns:
            Exchange code (e.g., "NYSE", "HKEX", "XETRA")
        """
        if "." not in symbol:
            return "NYSE"  # Default to NYSE for US symbols
        
        suffix = symbol.split(".")[-1].upper()
        
        suffix_map = {
            "L": "LSE",      # London
            "DE": "XETRA",   # Germany
            "PA": "EPA",     # Paris
            "SW": "SIX",     # Swiss
            "T": "TSE",      # Tokyo
            "HK": "HKEX",    # Hong Kong
            "SS": "SSE",     # Shanghai
            "SZ": "SZSE",    # Shenzhen
            "NS": "NSE",     # India (NSE)
            "BO": "NSE",     # India (BSE - use NSE hours)
            "AX": "ASX",     # Australia
            "TO": "TSX",     # Toronto
            "MX": "BMV",     # Mexico
            "SA": "B3",      # Brazil
            "MI": "EPA",     # Milan (use Euronext hours)
        }
        
        return suffix_map.get(suffix, "NYSE")
    
    def _is_holiday(self, exchange: str, date: datetime) -> bool:
        """Check if date is a holiday for the exchange"""
        date_str = date.strftime("%Y-%m-%d")
        year = date.year
        holidays = self._get_holidays_for_year(year, exchange)
        return date_str in holidays
    
    def _is_early_close(self, exchange: str, date: datetime) -> bool:
        """Check if market has early close on this date"""
        date_str = date.strftime("%Y-%m-%d")
        year = date.year
        
        if year not in self.early_closes:
            return False
        
        early_close_dates = self.early_closes[year].get(exchange, [])
        return date_str in early_close_dates
    
    def _get_close_time(self, exchange: str, date: datetime) -> time:
        """Get close time for exchange, accounting for early closes"""
        _, _, regular_close = self.exchange_hours[exchange]
        
        # Check if early close
        if self._is_early_close(exchange, date):
            return time(13, 0)  # Early close at 1:00 PM local time
        
        return regular_close
    
    def _is_weekend(self, date: datetime) -> bool:
        """Check if date is a weekend"""
        return date.weekday() >= 5  # Saturday=5, Sunday=6
    
    def is_market_open(self, symbol: str, dt: Optional[datetime] = None) -> bool:
        """
        Check if market is currently open for trading.
        
        Args:
            symbol: Ticker symbol or exchange code
            dt: Datetime to check (default: now). Can be in any timezone (including UTC),
                will be automatically converted to the exchange's local timezone.
            
        Returns:
            True if market is open, False otherwise
            
        Note:
            The method accepts datetime in any timezone (including UTC timestamps from
            data providers like yfinance). It automatically converts to the exchange's
            local timezone for accurate market hours calculation.
            
        Example:
            >>> mh = MarketHours()
            >>> mh.is_market_open("AAPL")  # Uses current time in NYSE timezone
            True
            >>> # UTC timestamp is automatically converted to NYSE timezone
            >>> from datetime import datetime, timezone
            >>> utc_time = datetime(2025, 11, 15, 15, 0, tzinfo=timezone.utc)  # 10:00 AM ET
            >>> mh.is_market_open("AAPL", utc_time)
            True
            >>> mh.is_market_open("0700.HK")  # Hong Kong market
            False
        """
        exchange = symbol if symbol in self.exchange_hours else self._get_exchange_for_symbol(symbol)
        
        if exchange not in self.exchange_hours:
            warnings.warn(f"Unknown exchange for symbol {symbol}, assuming NYSE hours")
            exchange = "NYSE"
        
        tz_name, open_time, close_time = self.exchange_hours[exchange]
        tz = ZoneInfo(tz_name)
        
        if dt is None:
            dt = datetime.now(tz)
        elif dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz)
        else:
            dt = dt.astimezone(tz)
        
        # Check weekend
        if self._is_weekend(dt):
            return False
        
        # Check holiday
        if self._is_holiday(exchange, dt):
            return False
        
        # Get actual close time (may be early close)
        actual_close_time = self._get_close_time(exchange, dt)
        
        # Check time
        current_time = dt.time()
        return open_time <= current_time < actual_close_time
    
    def get_market_state(self, symbol: str, dt: Optional[datetime] = None) -> str:
        """
        Get current market state.
        
        Args:
            symbol: Ticker symbol or exchange code
            dt: Datetime to check (default: now)
            
        Returns:
            Market state: "REGULAR", "PRE", "POST", "CLOSED"
            
        Example:
            >>> mh = MarketHours()
            >>> mh.get_market_state("AAPL")
            'REGULAR'
        """
        exchange = symbol if symbol in self.exchange_hours else self._get_exchange_for_symbol(symbol)
        
        if exchange not in self.exchange_hours:
            exchange = "NYSE"
        
        tz_name, open_time, close_time = self.exchange_hours[exchange]
        tz = ZoneInfo(tz_name)
        
        if dt is None:
            dt = datetime.now(tz)
        elif dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz)
        else:
            dt = dt.astimezone(tz)
        
        # Check weekend
        if self._is_weekend(dt):
            return "CLOSED"
        
        # Check holiday
        if self._is_holiday(exchange, dt):
            return "CLOSED"
        
        current_time = dt.time()
        
        # Get actual close time (may be early close)
        actual_close_time = self._get_close_time(exchange, dt)
        
        # Check pre-market
        if exchange in self.pre_market:
            pre_start = self.pre_market[exchange]
            if pre_start <= current_time < open_time:
                return "PRE"
        
        # Check regular hours
        if open_time <= current_time < actual_close_time:
            return "REGULAR"
        
        # Check after-hours
        if exchange in self.after_hours:
            after_end = self.after_hours[exchange]
            if actual_close_time <= current_time < after_end:
                return "POST"
        
        return "CLOSED"
    
    def next_market_open(self, symbol: str, dt: Optional[datetime] = None) -> datetime:
        """
        Get next market open datetime.
        
        Args:
            symbol: Ticker symbol or exchange code
            dt: Starting datetime (default: now)
            
        Returns:
            Datetime of next market open
            
        Example:
            >>> mh = MarketHours()
            >>> mh.next_market_open("AAPL")
            datetime.datetime(2025, 11, 18, 9, 30, tzinfo=ZoneInfo('America/New_York'))
        """
        exchange = symbol if symbol in self.exchange_hours else self._get_exchange_for_symbol(symbol)
        
        if exchange not in self.exchange_hours:
            exchange = "NYSE"
        
        tz_name, open_time, close_time = self.exchange_hours[exchange]
        tz = ZoneInfo(tz_name)
        
        if dt is None:
            dt = datetime.now(tz)
        elif dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz)
        else:
            dt = dt.astimezone(tz)
        
        # Start from next day if already past today's open
        if dt.time() >= open_time:
            dt = dt + timedelta(days=1)
        
        # Find next trading day
        max_attempts = 14  # Check up to 2 weeks ahead
        for _ in range(max_attempts):
            # Skip weekends
            while self._is_weekend(dt):
                dt = dt + timedelta(days=1)
            
            # Check if holiday
            if not self._is_holiday(exchange, dt):
                return dt.replace(hour=open_time.hour, minute=open_time.minute, second=0, microsecond=0)
            
            dt = dt + timedelta(days=1)
        
        # Fallback: return next Monday at open time
        while self._is_weekend(dt):
            dt = dt + timedelta(days=1)
        return dt.replace(hour=open_time.hour, minute=open_time.minute, second=0, microsecond=0)
    
    def next_market_close(self, symbol: str, dt: Optional[datetime] = None) -> datetime:
        """
        Get next market close datetime.
        
        Args:
            symbol: Ticker symbol or exchange code
            dt: Starting datetime (default: now)
            
        Returns:
            Datetime of next market close
        """
        exchange = symbol if symbol in self.exchange_hours else self._get_exchange_for_symbol(symbol)
        
        if exchange not in self.exchange_hours:
            exchange = "NYSE"
        
        tz_name, open_time, close_time = self.exchange_hours[exchange]
        tz = ZoneInfo(tz_name)
        
        if dt is None:
            dt = datetime.now(tz)
        elif dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz)
        else:
            dt = dt.astimezone(tz)
        
        # If market is open today, return today's close
        if not self._is_weekend(dt) and not self._is_holiday(exchange, dt):
            actual_close_time = self._get_close_time(exchange, dt)
            if dt.time() < actual_close_time:
                return dt.replace(hour=actual_close_time.hour, minute=actual_close_time.minute, second=0, microsecond=0)
        
        # Otherwise find next trading day
        dt = dt + timedelta(days=1)
        max_attempts = 14
        for _ in range(max_attempts):
            while self._is_weekend(dt):
                dt = dt + timedelta(days=1)
            
            if not self._is_holiday(exchange, dt):
                actual_close_time = self._get_close_time(exchange, dt)
                return dt.replace(hour=actual_close_time.hour, minute=actual_close_time.minute, second=0, microsecond=0)
            
            dt = dt + timedelta(days=1)
        
        # Fallback
        while self._is_weekend(dt):
            dt = dt + timedelta(days=1)
        actual_close_time = self._get_close_time(exchange, dt)
        return dt.replace(hour=actual_close_time.hour, minute=actual_close_time.minute, second=0, microsecond=0)
    
    def get_exchange_info(self, symbol: str) -> Dict[str, any]:
        """
        Get exchange information for a symbol.
        
        Args:
            symbol: Ticker symbol or exchange code
            
        Returns:
            Dictionary with exchange details
        """
        exchange = symbol if symbol in self.exchange_hours else self._get_exchange_for_symbol(symbol)
        
        if exchange not in self.exchange_hours:
            exchange = "NYSE"
        
        tz_name, open_time, close_time = self.exchange_hours[exchange]
        
        # Get available years for this exchange
        available_years = []
        for year, exchanges in self.holidays_by_year.items():
            if exchange in exchanges:
                available_years.append(year)
        
        return {
            "exchange": exchange,
            "timezone": tz_name,
            "open_time": open_time.strftime("%H:%M"),
            "close_time": close_time.strftime("%H:%M"),
            "has_pre_market": exchange in self.pre_market,
            "has_after_hours": exchange in self.after_hours,
            "pre_market_start": self.pre_market[exchange].strftime("%H:%M") if exchange in self.pre_market else None,
            "after_hours_end": self.after_hours[exchange].strftime("%H:%M") if exchange in self.after_hours else None,
            "early_close_time": "13:00",  # Standard early close time
            "calendar_years_available": sorted(available_years),
        }
    
    def get_supported_exchanges(self) -> List[str]:
        """Get list of supported exchanges"""
        return list(self.exchange_hours.keys())


# Global instance for convenience
_market_hours_instance = None


def get_market_hours() -> MarketHours:
    """Get global MarketHours instance (singleton)"""
    global _market_hours_instance
    if _market_hours_instance is None:
        _market_hours_instance = MarketHours()
    return _market_hours_instance


# Convenience functions
def is_market_open(symbol: str, dt: Optional[datetime] = None) -> bool:
    """Check if market is open for symbol"""
    return get_market_hours().is_market_open(symbol, dt)


def get_market_state(symbol: str, dt: Optional[datetime] = None) -> str:
    """Get market state for symbol"""
    return get_market_hours().get_market_state(symbol, dt)


def next_market_open(symbol: str, dt: Optional[datetime] = None) -> datetime:
    """Get next market open time for symbol"""
    return get_market_hours().next_market_open(symbol, dt)


def next_market_close(symbol: str, dt: Optional[datetime] = None) -> datetime:
    """Get next market close time for symbol"""
    return get_market_hours().next_market_close(symbol, dt)


def get_supported_exchanges() -> List[str]:
    """Get list of all supported exchange codes"""
    return get_market_hours().get_supported_exchanges()
