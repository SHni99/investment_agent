"""
Simple rate limiter to avoid API quota issues
"""
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class RateLimiter:
    """
    Simple rate limiter to manage API call frequency
    """
    def __init__(self, calls_per_minute: int = 2, calls_per_day: int = 60):
        self.calls_per_minute = calls_per_minute
        self.calls_per_day = calls_per_day
        self.minute_calls = 0
        self.daily_calls = 0
        self.last_reset_minute = datetime.now()
        self.last_reset_day = datetime.now().date()
    
    def check_and_wait(self) -> bool:
        """
        Check if we can make another call and wait if needed
        Returns True if call is allowed, False if quota would be exceeded
        """
        now = datetime.now()
        
        # Reset minute counter if a minute has passed
        if (now - self.last_reset_minute).total_seconds() >= 60:
            self.minute_calls = 0
            self.last_reset_minute = now
        
        # Reset daily counter if day changed
        if now.date() != self.last_reset_day:
            self.daily_calls = 0
            self.last_reset_day = now.date()
        
        # Check if we've hit limits
        if self.minute_calls >= self.calls_per_minute:
            seconds_to_wait = 60 - (now - self.last_reset_minute).total_seconds()
            if seconds_to_wait > 0:
                print(f"Rate limit reached. Waiting {seconds_to_wait:.1f} seconds...")
                time.sleep(seconds_to_wait)
                # Reset after waiting
                self.minute_calls = 0
                self.last_reset_minute = datetime.now()
        
        if self.daily_calls >= self.calls_per_day:
            return False
        
        # Increment counters
        self.minute_calls += 1
        self.daily_calls += 1
        return True

# Create a singleton instance
gemini_rate_limiter = RateLimiter(calls_per_minute=1, calls_per_day=60)
