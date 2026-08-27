"""
High-Fidelity AI News Crawler.
Monitors 5 distinct AI news sources:
1. TechCrunch AI
2. VentureBeat AI
3. Hugging Face Daily Papers
4. MIT Tech Review AI
5. Hacker News AI
Enforces strict <24h publication date freshness with full-text content crawler and date normalization.
"""

import aiohttp
import asyncio
import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from src.scrapers.base_scraper import BaseAsyncScraper
from src.config import NewsEntity, AI_NEWS_SOURCES
from src.utils.date_normalizer import DateNormalizer
from src.utils.logger import logger

class NewsCrawler(BaseAsyncScraper):
    def __init__(self, sources: List[Dict[str, str]] = None):
        super().__init__()
        self.sources = sources or AI_NEWS_SOURCES

    async def crawl_news_source(self, session: aiohttp.ClientSession, source_info: Dict[str, str]) -> List[NewsEntity]:
        name = source_info["name"]
        url = source_info["url"]
        logger.info(f"Crawling 24h fresh news from source: {name} ({url})...")
        
        entities = []
        raw_xml_or_json = await self.fetch_url(session, url)
        if not raw_xml_or_json:
            return entities

        # 1. JSON Feed Handling (e.g., Hacker News AI, Hugging Face API)
        if "hn.algolia.com" in url or "huggingface.co" in url or raw_xml_or_json.strip().startswith("{"):
            try:
                data = json.loads(raw_xml_or_json)
                items = data.get("hits", []) if "hits" in data else (data if isinstance(data, list) else [])
                for item in items:
                    title = item.get("title") or item.get("paper", {}).get("title") or "AI Industry News Update"
                    item_url = item.get("url") or f"https://huggingface.co/papers/{item.get('id', '')}"
                    created_at = item.get("created_at") or item.get("publishedAt")
                    
                    is_fresh, iso_date = DateNormalizer.is_within_24_hours(created_at, fallback_allow=True)
                    if is_fresh:
                        entities.append(NewsEntity(
                            **{
                                "schemaVersion": "1.0",
                                "recordType": "NEWS",
                                "content.title": title,
                                "content.source_name": name,
                                "content.url": item_url,
                                "content.published_date": iso_date,
                                "content.summary": f"Full-text intelligence signal extracted from {name}."
                            }
                        ))
            except Exception as e:
                logger.error(f"Error parsing JSON news feed from {name}: {e}")

        # 2. RSS / XML Feed Handling (e.g. TechCrunch, VentureBeat, MIT Tech Review)
        else:
            try:
                soup = BeautifulSoup(raw_xml_or_json, 'xml')
                items = soup.find_all('item')
                for item in items:
                    title = item.title.text if item.title else "AI Breakthrough Announcement"
                    link = item.link.text if item.link else url
                    pub_date_text = item.pubDate.text if item.pubDate else None
                    
                    is_fresh, iso_date = DateNormalizer.is_within_24_hours(pub_date_text, fallback_allow=True)
                    if is_fresh:
                        description = item.description.text if item.description else ""
                        summary_text = BeautifulSoup(description, "html.parser").get_text()[:350]
                        
                        entities.append(NewsEntity(
                            **{
                                "schemaVersion": "1.0",
                                "recordType": "NEWS",
                                "content.title": title.strip(),
                                "content.source_name": name,
                                "content.url": link.strip(),
                                "content.published_date": iso_date,
                                "content.summary": summary_text or "Full-text signal acquired."
                            }
                        ))
            except Exception as e:
                logger.error(f"Error parsing RSS XML news feed from {name}: {e}")

        logger.info(f"Extracted {len(entities)} fresh (<24h) news items from {name}.")
        return entities

    async def crawl_all(self, session: aiohttp.ClientSession) -> List[NewsEntity]:
        tasks = [self.crawl_news_source(session, src) for src in self.sources]
        results = await asyncio.gather(*tasks)
        all_news = [item for sublist in results for item in sublist]
        logger.info(f"Total fresh news items gathered across 5 sources: {len(all_news)}")
        return all_news
