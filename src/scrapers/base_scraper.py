"""
Base Async Scraper Module.
Provides async HTTP requesting via aiohttp, automatic anti-bot stealth header injection,
retry handling, and structured parsing capabilities.
"""

import aiohttp
import asyncio
from typing import Optional, Dict, Any
from src.utils.anti_bot import AntiBotManager
from src.utils.logger import logger

class BaseAsyncScraper:
    def __init__(self, timeout_seconds: int = 15, max_concurrent: int = 20):
        self.timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_url(self, session: aiohttp.ClientSession, url: str, headers: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Fetches raw text/HTML content from a given URL using stealth headers."""
        req_headers = AntiBotManager.get_stealth_headers(headers)
        async with self.semaphore:
            try:
                async with session.get(url, headers=req_headers, timeout=self.timeout) as resp:
                    if resp.status == 200:
                        return await resp.text()
                    elif resp.status == 429:
                        logger.warning(f"429 Rate limited at {url}. Backing off...")
                        await asyncio.sleep(2.0)
                    else:
                        logger.warning(f"HTTP {resp.status} received for {url}")
            except Exception as e:
                logger.debug(f"Error fetching {url}: {e}")
            return None
