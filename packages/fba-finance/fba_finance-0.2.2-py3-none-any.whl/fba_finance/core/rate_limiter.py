"""
Rate limiter to prevent hitting API limits with daily usage tracking
"""
import time
from collections import deque
from threading import Lock
from typing import Dict, Optional
import warnings


class RateLimiter:
    """Token bucket rate limiter with per-provider limits"""
    
    def __init__(self, 
                 requests_per_second: int = 2,
                 requests_per_minute: int = 50,
                 requests_per_day: Optional[int] = None):
        self.requests_per_second = requests_per_second
        self.requests_per_minute = requests_per_minute
        self.requests_per_day = requests_per_day
        
        # Track requests per provider
        self._provider_requests: Dict[str, deque] = {}
        self._provider_locks: Dict[str, Lock] = {}
        
        # Global limits
        self._global_requests = deque()
        self._global_lock = Lock()
    
    def _get_provider_queue(self, provider: str) -> deque:
        """Get or create request queue for provider"""
        if provider not in self._provider_requests:
            self._provider_requests[provider] = deque()
            self._provider_locks[provider] = Lock()
        return self._provider_requests[provider]
    
    def _clean_old_requests(self, request_queue: deque, time_window: float):
        """Remove requests older than time_window seconds"""
        current_time = time.time()
        while request_queue and current_time - request_queue[0] > time_window:
            request_queue.popleft()
    
    def wait_if_needed(self, provider: str = "global"):
        """Wait if rate limit would be exceeded"""
        # Import here to avoid circular dependency
        from ..config import Config
        from ..usage_tracker import get_usage_tracker
        
        with self._provider_locks.get(provider, self._global_lock):
            # Check daily limit first (if enabled)
            if Config.ENABLE_DAILY_LIMIT_CHECK and provider in Config.DAILY_LIMITS:
                tracker = get_usage_tracker()
                daily_limit = Config.DAILY_LIMITS[provider]
                
                if not tracker.check_limit(provider, daily_limit):
                    usage = tracker.get_daily_usage(provider)
                    msg = (
                        f"Daily limit reached for {provider}: "
                        f"{usage}/{daily_limit} requests today. "
                        f"Consider using another provider or wait until tomorrow."
                    )
                    warnings.warn(msg, UserWarning)
                    raise Exception(f"Daily limit exceeded for {provider}")
            
            request_queue = self._get_provider_queue(provider)
            current_time = time.time()
            
            # Clean old requests
            self._clean_old_requests(request_queue, 86400)  # 24 hours for daily limit
            
            # Check daily limit
            if self.requests_per_day:
                daily_requests = sum(1 for t in request_queue if current_time - t < 86400)
                if daily_requests >= self.requests_per_day:
                    wait_time = 86400 - (current_time - request_queue[0])
                    if wait_time > 0:
                        print(f"Daily limit reached for {provider}, waiting {wait_time:.0f}s")
                        time.sleep(wait_time)
            
            # Check minute limit
            self._clean_old_requests(request_queue, 60)
            minute_requests = sum(1 for t in request_queue if current_time - t < 60)
            if minute_requests >= self.requests_per_minute:
                wait_time = 60 - (current_time - request_queue[0])
                if wait_time > 0:
                    time.sleep(wait_time)
            
            # Check second limit
            self._clean_old_requests(request_queue, 1)
            second_requests = sum(1 for t in request_queue if current_time - t < 1)
            if second_requests >= self.requests_per_second:
                wait_time = 1 - (current_time - request_queue[0])
                if wait_time > 0:
                    time.sleep(wait_time)
            
            # Record this request
            request_queue.append(time.time())
            
            # Track in usage tracker
            if Config.ENABLE_DAILY_LIMIT_CHECK:
                from ..usage_tracker import get_usage_tracker
                tracker = get_usage_tracker()
                tracker.record_request(provider)
    
    def get_provider_stats(self, provider: str) -> Dict[str, int]:
        """Get request statistics for a provider"""
        request_queue = self._get_provider_queue(provider)
        current_time = time.time()
        
        return {
            "last_second": sum(1 for t in request_queue if current_time - t < 1),
            "last_minute": sum(1 for t in request_queue if current_time - t < 60),
            "last_hour": sum(1 for t in request_queue if current_time - t < 3600),
            "last_day": sum(1 for t in request_queue if current_time - t < 86400),
            "total": len(request_queue),
        }


class ProviderRateLimiter:
    """Specialized rate limiter for different providers"""
    
    # Provider-specific limits (free tier, calibrated to 75% saturation)
    # per_minute based on 12-hour daily usage (720 minutes)
    # per_second removed - not meaningful for trading platform context
    # Daily limits enforced through Config.DAILY_LIMITS
    PROVIDER_LIMITS = {
        "yfinance": {"per_second": 1, "per_minute": 2, "per_day": None},       # Batch-capable
        "yahooquery": {"per_second": 1, "per_minute": 2, "per_day": None},    # Batch-capable
        "alphavantage": {"per_second": 1, "per_minute": 1, "per_day": 375},  # Single requests
        "twelvedata": {"per_second": 1, "per_minute": 1, "per_day": 600},    # Batch-capable, respect 8/min official
        "polygon": {"per_second": 1, "per_minute": 1, "per_day": 5},         # Not recommended
        "fmp": {"per_second": 1, "per_minute": 1, "per_day": 187},           # Single requests
        "yahoo_scraper": {"per_second": 1, "per_minute": 1, "per_day": None}, # Anti-detection
    }
    
    def __init__(self):
        self._limiters: Dict[str, RateLimiter] = {}
        self._blocked_providers: Dict[str, float] = {}  # provider -> unblock_timestamp
        self._locks: Dict[str, Lock] = {}
    
    def _get_limiter(self, provider: str) -> RateLimiter:
        """Get or create rate limiter for provider"""
        if provider not in self._limiters:
            limits = self.PROVIDER_LIMITS.get(provider, {"per_second": 1, "per_minute": 10, "per_day": None})
            self._limiters[provider] = RateLimiter(
                requests_per_second=limits["per_second"],
                requests_per_minute=limits["per_minute"],
                requests_per_day=limits["per_day"]
            )
        return self._limiters[provider]
    
    def wait_if_needed(self, provider: str):
        """Wait if needed for specific provider"""
        limiter = self._get_limiter(provider)
        limiter.wait_if_needed(provider)
    
    def get_stats(self, provider: str) -> Dict[str, int]:
        """Get stats for provider"""
        limiter = self._get_limiter(provider)
        return limiter.get_provider_stats(provider)
    
    def is_provider_blocked(self, provider: str) -> bool:
        """Check if provider is temporarily blocked (cooldown)"""
        if provider in self._blocked_providers:
            unblock_time = self._blocked_providers[provider]
            if time.time() < unblock_time:
                return True  # Still blocked
            else:
                # Cooldown expired, unblock
                del self._blocked_providers[provider]
        return False
    
    def block_provider(self, provider: str, duration: float = 300):
        """Block provider temporarily (default 5 minutes)"""
        self._blocked_providers[provider] = time.time() + duration
        print(f"⚠️ Provider '{provider}' blocked for {duration}s")
    
    def can_use_provider(self, provider: str) -> bool:
        """
        Check if provider can be used now (not rate limited).
        Returns True if we can make a request without waiting.
        """
        if self.is_provider_blocked(provider):
            return False
        
        limiter = self._get_limiter(provider)
        request_queue = limiter._get_provider_queue(provider)
        current_time = time.time()
        
        # Clean old requests
        limiter._clean_old_requests(request_queue, 60)
        
        # Check if we're at the limit
        minute_requests = sum(1 for t in request_queue if current_time - t < 60)
        if minute_requests >= limiter.requests_per_minute:
            return False  # Would need to wait
        
        second_requests = sum(1 for t in request_queue if current_time - t < 1)
        if second_requests >= limiter.requests_per_second:
            return False  # Would need to wait
        
        return True  # Can make request now
