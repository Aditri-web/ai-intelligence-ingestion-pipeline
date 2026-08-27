"""
Pipeline Orchestrator Engine.
Main control system orchestrating Phase I through Phase V tasks asynchronously:
- Phase I: Bulk extraction (1000 Startups, 1000 Products, 1000 Research Papers with GitHub metrics)
- Phase II: High-Fidelity Signal Ingestion (5 News Feeds, 5 Job Boards with <24h freshness)
- Phase III: Multi-Tier LLM Structuring & 413/429 Handling
- Phase IV: Deterministic Entity Resolution against seed database
- Phase V: Async execution with anti-bot protection
"""

import aiohttp
import asyncio
from typing import Dict, Any, Tuple, List
from src.scrapers.research_scraper import ResearchPaperScraper
from src.scrapers.startup_scraper import StartupScraper
from src.scrapers.product_scraper import ProductScraper
from src.scrapers.news_crawler import NewsCrawler
from src.scrapers.job_crawler import JobCrawler
from src.entity_resolution.canonicalizer import EntityResolver
from src.exporters.excel_exporter import PipelineDataExporter
from src.utils.logger import logger
from src.config import TARGET_COUNTS

class IngestionPipelineOrchestrator:
    def __init__(self):
        self.entity_resolver = EntityResolver()
        self.exporter = PipelineDataExporter()

    async def run_pipeline(self) -> Dict[str, Any]:
        logger.info("=========================================================")
        logger.info("STARTING GRAPHONE / FRONTIERATLAS INGESTION PIPELINE")
        logger.info("=========================================================")

        async with aiohttp.ClientSession() as session:
            # Phase I & II: Run all scrapers concurrently
            logger.info("Launching Phase I (Bulk Extraction) & Phase II (Fresh Signals)...")
            
            research_scraper = ResearchPaperScraper(target_count=TARGET_COUNTS["research_papers"])
            startup_scraper = StartupScraper(target_count=TARGET_COUNTS["startups"])
            product_scraper = ProductScraper(target_count=TARGET_COUNTS["products"])
            news_crawler = NewsCrawler()
            job_crawler = JobCrawler()

            # Execute all scrapers concurrently.
            # FIX: return_exceptions=True ensures one failing scraper doesn't crash the full pipeline.
            results = await asyncio.gather(
                research_scraper.scrape_all(session),
                startup_scraper.scrape_all(session),
                product_scraper.scrape_all(session),
                news_crawler.crawl_all(session),
                job_crawler.crawl_all(session),
                return_exceptions=True
            )

            scraper_names = ["research_papers", "startups", "products", "news", "jobs"]
            papers, startups, products, news, jobs = [], [], [], [], []
            safe_results = [papers, startups, products, news, jobs]

            for i, (name, result) in enumerate(zip(scraper_names, results)):
                if isinstance(result, Exception):
                    logger.error(f"[Scraper Failed] '{name}' raised an exception: {result}. Continuing with empty dataset.")
                else:
                    safe_results[i].extend(result)

            papers, startups, products, news, jobs = safe_results

            # Phase IV: Entity Resolution & Canonicalization
            logger.info("Executing Phase IV: Deterministic Entity Resolution...")
            for s in startups:
                raw_name = s.contentEntityName
                canonical, score, method = self.entity_resolver.resolve_entity(raw_name, entity_type="STARTUP")
                s.contentEntityName = canonical

            for p in products:
                raw_name = p.contentStartupName
                canonical, score, method = self.entity_resolver.resolve_entity(raw_name, entity_type="STARTUP")
                p.contentStartupName = canonical

            for j in jobs:
                raw_company = j.company
                canonical, score, method = self.entity_resolver.resolve_entity(raw_company, entity_type="COMPANY")
                j.company = canonical

            entity_logs = self.entity_resolver.get_logs()

            # Phase VI / Deliverables: Export to CSV and 6-tab Excel
            excel_file = self.exporter.export_all(
                startups=startups,
                products=products,
                research_papers=papers,
                jobs=jobs,
                news=news,
                entity_logs=entity_logs
            )

            stats = {
                "startups_count": len(startups),
                "products_count": len(products),
                "research_papers_count": len(papers),
                "jobs_count": len(jobs),
                "news_count": len(news),
                "entity_logs_count": len(entity_logs),
                "excel_output_path": excel_file
            }

            logger.info("=========================================================")
            logger.info("PIPELINE COMPLETED SUCCESSFULLY!")
            logger.info(f"Summary Metrics: {stats}")
            logger.info("=========================================================")

            return stats
