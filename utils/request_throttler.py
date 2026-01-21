"""
Request Throttler - Rate limiting to be respectful to the server.
Prevents hammering and reduces chances of being blocked.

Best Practices:
- 1-2 second delay between requests
- Random jitter to avoid patterns
- Per-domain rate limiting
- Backoff on 429/503 responses
"""

import asyncio
import time
from collections import defaultdict
from datetime import datetime, timedelta
from utils.logger import get_logger

logger = get_logger("THROTTLER")


class RequestThrottler:
    """
    Rate limiter for HTTP requests.
    Tracks requests per domain and enforces delays.
    """
    
    def __init__(self, min_delay: float = 1.5, max_delay: float = 3.0):
        """
        Args:
            min_delay: Minimum delay between requests in seconds
            max_delay: Maximum delay (with random jitter)
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time: dict[str, float] = defaultdict(float)
        self.lock = asyncio.Lock()
    
    async def wait(self, domain: str = "default"):
        """
        Wait if necessary before making next request to domain.
        
        Args:
            domain: Domain identifier (e.g., "tradestat.commerce.gov.in")
        """
        async with self.lock:
            now = time.time()
            last_time = self.last_request_time.get(domain, 0)
            time_since_last = now - last_time
            
            # Calculate required delay with jitter
            import random
            required_delay = random.uniform(self.min_delay, self.max_delay)
            
            if time_since_last < required_delay:
                wait_time = required_delay - time_since_last
                logger.debug(f"Throttling {domain}: waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
            
            self.last_request_time[domain] = time.time()
    
    async def wait_on_rate_limit(self, retry_after: int = 60):
        """
        Wait when rate limited (HTTP 429 or 503).
        
        Args:
            retry_after: Seconds to wait (from Retry-After header)
        """
        logger.warning(f"Rate limited! Waiting {retry_after} seconds...")
        await asyncio.sleep(retry_after)


# Global throttler instance
_global_throttler: RequestThrottler = None


def get_throttler(min_delay: float = 1.5, max_delay: float = 3.0) -> RequestThrottler:
    """Get or create global throttler instance"""
    global _global_throttler
    
    if _global_throttler is None:
        _global_throttler = RequestThrottler(min_delay=min_delay, max_delay=max_delay)
    
    return _global_throttler


# Example usage in scraper
"""
# In your scraper code:

throttler = get_throttler()

async def scrape_page():
    # Wait before making request
    await throttler.wait(domain="tradestat.commerce.gov.in")
    
    # Make request
    response = await page.goto(url)
    
    # Check for rate limiting
    if response.status == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        await throttler.wait_on_rate_limit(retry_after)
        # Retry request
"""
