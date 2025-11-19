"""
Daily usage tracker for monitoring API request limits per provider.
Helps prevent hitting daily limits by tracking and warning about usage.
"""
import json
from pathlib import Path
from datetime import date, timedelta
from typing import Dict, Optional
from threading import Lock


class UsageTracker:
    """
    Track daily API usage per provider.
    
    Persists usage data to disk to survive restarts.
    Thread-safe for concurrent access.
    """
    
    def __init__(self, stats_file: Optional[Path] = None):
        """
        Initialize usage tracker.
        
        Args:
            stats_file: Path to stats file (default: ~/.fba_finance/usage_stats.json)
        """
        if stats_file is None:
            stats_file = Path.home() / ".fba_finance" / "usage_stats.json"
        
        self.stats_file = Path(stats_file)
        self.stats: Dict[str, Dict[str, int]] = self._load_stats()
        self._lock = Lock()
        
        # Clean old stats on init
        self._clean_old_stats()
    
    def _load_stats(self) -> Dict[str, Dict[str, int]]:
        """Load usage stats from disk"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load usage stats: {e}")
                return {}
        return {}
    
    def _save_stats(self):
        """Save usage stats to disk"""
        try:
            self.stats_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save usage stats: {e}")
    
    def _clean_old_stats(self, days_to_keep: int = 7):
        """Remove stats older than specified days"""
        with self._lock:
            cutoff_date = (date.today() - timedelta(days=days_to_keep)).isoformat()
            
            # Remove old dates
            dates_to_remove = [d for d in self.stats.keys() if d < cutoff_date]
            for d in dates_to_remove:
                del self.stats[d]
            
            if dates_to_remove:
                self._save_stats()
    
    def record_request(self, provider: str):
        """
        Record a single API request for a provider.
        
        Args:
            provider: Provider name (e.g., 'yfinance', 'alphavantage')
        """
        with self._lock:
            today = date.today().isoformat()
            
            # Initialize today's stats if needed
            if today not in self.stats:
                self.stats[today] = {}
            
            # Initialize provider count if needed
            if provider not in self.stats[today]:
                self.stats[today][provider] = 0
            
            # Increment count
            self.stats[today][provider] += 1
            
            # Save to disk
            self._save_stats()
    
    def get_daily_usage(self, provider: str, day: Optional[date] = None) -> int:
        """
        Get request count for a provider on a specific day.
        
        Args:
            provider: Provider name
            day: Date to check (default: today)
        
        Returns:
            Number of requests made
        """
        day_str = (day or date.today()).isoformat()
        return self.stats.get(day_str, {}).get(provider, 0)
    
    def check_limit(self, provider: str, limit: int) -> bool:
        """
        Check if provider is under daily limit.
        
        Args:
            provider: Provider name
            limit: Daily limit to check against
        
        Returns:
            True if under limit, False if at or over limit
        """
        usage = self.get_daily_usage(provider)
        return usage < limit
    
    def get_remaining(self, provider: str, limit: int) -> int:
        """
        Get remaining requests for provider today.
        
        Args:
            provider: Provider name
            limit: Daily limit
        
        Returns:
            Number of requests remaining (0 if over limit)
        """
        usage = self.get_daily_usage(provider)
        remaining = limit - usage
        return max(0, remaining)
    
    def get_usage_percentage(self, provider: str, limit: int) -> float:
        """
        Get usage as percentage of daily limit.
        
        Args:
            provider: Provider name
            limit: Daily limit
        
        Returns:
            Usage percentage (0.0 to 100.0+)
        """
        usage = self.get_daily_usage(provider)
        if limit == 0:
            return 0.0
        return (usage / limit) * 100.0
    
    def get_stats_summary(self, days: int = 7) -> Dict[str, Dict[str, int]]:
        """
        Get usage summary for the last N days.
        
        Args:
            days: Number of days to include
        
        Returns:
            Dictionary mapping dates to provider usage counts
        """
        summary = {}
        
        for i in range(days):
            day = date.today() - timedelta(days=i)
            day_str = day.isoformat()
            summary[day_str] = self.stats.get(day_str, {})
        
        return summary
    
    def get_all_providers_today(self) -> Dict[str, int]:
        """
        Get usage for all providers today.
        
        Returns:
            Dictionary mapping provider names to request counts
        """
        today = date.today().isoformat()
        return self.stats.get(today, {}).copy()
    
    def reset_provider(self, provider: str, day: Optional[date] = None):
        """
        Reset usage count for a provider on a specific day.
        Useful for testing or manual corrections.
        
        Args:
            provider: Provider name
            day: Date to reset (default: today)
        """
        with self._lock:
            day_str = (day or date.today()).isoformat()
            
            if day_str in self.stats and provider in self.stats[day_str]:
                del self.stats[day_str][provider]
                self._save_stats()
    
    def reset_all(self):
        """
        Reset all usage statistics.
        Use with caution - this deletes all tracked data.
        """
        with self._lock:
            self.stats = {}
            self._save_stats()
    
    def print_summary(self):
        """Print a human-readable summary of today's usage"""
        from .config import Config
        
        today_usage = self.get_all_providers_today()
        
        if not today_usage:
            print("📊 No requests recorded today")
            return
        
        print("📊 Daily Usage Summary")
        print("=" * 60)
        
        for provider, count in sorted(today_usage.items()):
            limit = Config.DAILY_LIMITS.get(provider, 0)
            
            if limit > 0:
                percentage = self.get_usage_percentage(provider, limit)
                remaining = self.get_remaining(provider, limit)
                
                # Color coding based on usage
                if percentage >= 90:
                    status = "🔴"
                elif percentage >= 75:
                    status = "🟡"
                else:
                    status = "🟢"
                
                print(f"{status} {provider:15} {count:4} / {limit:4} ({percentage:5.1f}%) - {remaining:4} remaining")
            else:
                print(f"⚪ {provider:15} {count:4} / ∞")
        
        print("=" * 60)


# Singleton instance
_usage_tracker_instance: Optional[UsageTracker] = None


def get_usage_tracker() -> UsageTracker:
    """
    Get or create singleton UsageTracker instance.
    
    Returns:
        UsageTracker singleton
    """
    global _usage_tracker_instance
    
    if _usage_tracker_instance is None:
        _usage_tracker_instance = UsageTracker()
    
    return _usage_tracker_instance
