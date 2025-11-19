"""
Rate limiter to prevent hitting API limits
"""
import time
from collections import deque
from threading import Lock
from typing import Dict, Optional


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
        with self._provider_locks.get(provider, self._global_lock):
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
    
    # Provider-specific limits (free tier)
    PROVIDER_LIMITS = {
        "yfinance": {"per_second": 2, "per_minute": 60, "per_day": None},
        "yahooquery": {"per_second": 2, "per_minute": 60, "per_day": None},
        "alphavantage": {"per_second": 1, "per_minute": 5, "per_day": 500},
        "twelvedata": {"per_second": 1, "per_minute": 8, "per_day": 800},
        "polygon": {"per_second": 1, "per_minute": 5, "per_day": None},
        "fmp": {"per_second": 1, "per_minute": 10, "per_day": 250},
        "yahoo_scraper": {"per_second": 1, "per_minute": 30, "per_day": None},
    }
    
    def __init__(self):
        self._limiters: Dict[str, RateLimiter] = {}
    
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

    def can_use_provider(self, provider: str) -> bool:
        """
        Check if provider can be used now (not rate limited).
        
        Args:
            provider: Provider name
            
        Returns:
            True if provider available, False if rate limited
        """
        limiter = self._get_limiter(provider)
        request_queue = limiter._get_provider_queue(provider)
        current_time = time.time()
        
        # Clean old requests
        limiter._clean_old_requests(request_queue, 1)
        
        # Check if would exceed limits
        second_requests = sum(1 for t in request_queue if current_time - t < 1)
        if second_requests >= limiter.requests_per_second:
            return False
        
        limiter._clean_old_requests(request_queue, 60)
        minute_requests = sum(1 for t in request_queue if current_time - t < 60)
        if minute_requests >= limiter.requests_per_minute:
            return False
        
        return True
    
    def record_success(self, provider: str):
        """
        Record successful request (already done by wait_if_needed,
but exposed for manual tracking).
        
        Args:
            provider: Provider name
        """
        # wait_if_needed already records, this is a no-op
        # but kept for API compatibility
        pass
    
    def record_rate_limit(self, provider: str, cooldown_seconds: int = 300):
        """
        Record rate limit error for provider and enforce cooldown.
        
        Args:
            provider: Provider name
            cooldown_seconds: Cooldown duration (default: 5 minutes)
        """
        if not hasattr(self, '_blocked_until'):
            self._blocked_until = {}
        
        self._blocked_until[provider] = time.time() + cooldown_seconds
        print(f"⚠️ Provider {provider} rate limited, cooldown for {cooldown_seconds}s")
    
    def is_provider_blocked(self, provider: str) -> bool:
        """Check if provider is in cooldown period"""
        if not hasattr(self, '_blocked_until'):
            return False
        
        if provider in self._blocked_until:
            if time.time() < self._blocked_until[provider]:
                return True
            else:
                # Cooldown expired
                del self._blocked_until[provider]
        
        return False
