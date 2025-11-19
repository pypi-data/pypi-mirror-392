"""
Configuration module for FBA Finance
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Central configuration class"""
    
    # API Keys
    ALPHA_VANTAGE_API_KEY: Optional[str] = os.getenv("ALPHA_VANTAGE_API_KEY")
    TWELVE_DATA_API_KEY: Optional[str] = os.getenv("TWELVE_DATA_API_KEY")
    POLYGON_API_KEY: Optional[str] = os.getenv("POLYGON_API_KEY")
    FMP_API_KEY: Optional[str] = os.getenv("FMP_API_KEY")
    
    # Cache settings (default enabled for better performance and reduced API usage)
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_BACKEND: str = os.getenv("CACHE_BACKEND", "disk")  # disk, redis, memory
    CACHE_DIR: str = os.getenv("CACHE_DIR", ".cache")
    CACHE_TTL_REALTIME: int = int(os.getenv("CACHE_TTL_REALTIME", "60"))  # seconds
    CACHE_TTL_HISTORICAL: int = int(os.getenv("CACHE_TTL_HISTORICAL", "3600"))  # seconds
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    MAX_REQUESTS_PER_SECOND: int = int(os.getenv("MAX_REQUESTS_PER_SECOND", "2"))
    MAX_REQUESTS_PER_MINUTE: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "50"))
    
    # Retry settings
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY: float = float(os.getenv("RETRY_DELAY", "1.0"))
    BACKOFF_FACTOR: float = float(os.getenv("BACKOFF_FACTOR", "2.0"))
    
    # Proxy settings
    USE_PROXY: bool = os.getenv("USE_PROXY", "false").lower() == "true"
    PROXY_LIST: list = os.getenv("PROXY_LIST", "").split(",") if os.getenv("PROXY_LIST") else []
    
    # Provider priorities (order matters for fallback)
    PROVIDER_PRIORITY = [
        "yfinance",
        "yahooquery", 
        "yahoo_scraper",
        "twelvedata",
        "alphavantage",
        "polygon",
        "fmp",
    ]
    
    # Load balancing mode
    LOAD_BALANCING_MODE: str = os.getenv("LOAD_BALANCING_MODE", "fallback")  # fallback, round-robin, random
    
    # Daily request limits per provider (free tier, calibrated to 75% saturation)
    # Based on 12-hour daily usage (720 minutes) for trading platform
    # Assumes batch operations for quotes to minimize request count
    ENABLE_DAILY_LIMIT_CHECK: bool = os.getenv("ENABLE_DAILY_LIMIT_CHECK", "true").lower() == "true"
    DAILY_LIMITS = {
        "yfinance": 1500,        # 75% of 2000 estimated limit, batch-capable
        "yahooquery": 1500,      # 75% of 2000 estimated limit, batch-capable
        "yahoo_scraper": 750,    # 75% of 1000 conservative limit
        "twelvedata": 600,       # 75% of 800 free tier (batch-capable)
        "alphavantage": 375,     # 75% of 500 free tier (single requests only)
        "polygon": 5,            # Free tier: very limited, not recommended
        "fmp": 187,              # 75% of 250 free tier
    }
    
    # User agents for web scraping
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    ]
    
    @classmethod
    def has_api_key(cls, provider: str) -> bool:
        """Check if API key is configured for a provider"""
        key_map = {
            "alphavantage": cls.ALPHA_VANTAGE_API_KEY,
            "twelvedata": cls.TWELVE_DATA_API_KEY,
            "polygon": cls.POLYGON_API_KEY,
            "fmp": cls.FMP_API_KEY,
        }
        return key_map.get(provider) is not None
    
    @classmethod
    def get_cache_ttl_realtime(cls, symbol: str = "AAPL") -> int:
        """
        Get dynamic cache TTL for real-time data based on market hours.
        
        When market is open: short TTL (60s) for fresh data
        When market is closed: long TTL (3600s) to reduce unnecessary requests
        
        Args:
            symbol: Ticker symbol to check market hours (default: AAPL)
            
        Returns:
            TTL in seconds
        """
        try:
            from .market_hours import is_market_open
            if is_market_open(symbol):
                return cls.CACHE_TTL_REALTIME  # 60s when market open
            else:
                return 3600  # 1 hour when market closed
        except Exception:
            # Fallback to default if market_hours not available
            return cls.CACHE_TTL_REALTIME
    
    @classmethod
    def get_cache_ttl_historical(cls, symbol: str = "AAPL") -> int:
        """
        Get dynamic cache TTL for historical data based on market hours.
        
        Historical data changes less frequently, so use longer TTL.
        Can be further optimized based on market state.
        
        Args:
            symbol: Ticker symbol to check market hours (default: AAPL)
            
        Returns:
            TTL in seconds
        """
        try:
            from .market_hours import is_market_open
            if is_market_open(symbol):
                return cls.CACHE_TTL_HISTORICAL  # 3600s when market open
            else:
                return 86400  # 24 hours when market closed
        except Exception:
            return cls.CACHE_TTL_HISTORICAL
    
    @classmethod
    def get_rate_limit_per_second(cls, symbol: str = "AAPL") -> int:
        """
        Get dynamic rate limit based on market hours.
        
        Can relax rate limits when markets are closed since data changes less.
        
        Args:
            symbol: Ticker symbol to check market hours (default: AAPL)
            
        Returns:
            Max requests per second
        """
        try:
            from .market_hours import is_market_open
            if is_market_open(symbol):
                return cls.MAX_REQUESTS_PER_SECOND
            else:
                # Relax rate limits when market closed
                return cls.MAX_REQUESTS_PER_SECOND * 2
        except Exception:
            return cls.MAX_REQUESTS_PER_SECOND
