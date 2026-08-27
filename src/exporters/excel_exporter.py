"""
Excel & CSV Data Exporter Engine.
Exports ingestion pipeline outputs into public-ready Google Sheets compatible formats:
1. Startups (Min. 1,000 rows)
2. Products (Min. 1,000 rows)
3. Research Papers (Min. 1,000 rows, including GitHub stars)
4. Jobs (All 24-hr fresh jobs found)
5. News (All 24-hr fresh news found)
6. Entity Mapping Log (Raw vs Canonical names)
"""

import os
import pandas as pd
from typing import List, Dict, Any
from src.config import StartupEntity, ProductEntity, ResearchPaperEntity, JobEntity, NewsEntity, EntityMappingLog
from src.utils.logger import logger

class PipelineDataExporter:
    def __init__(self, output_dir: str = "data_output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export_all(
        self,
        startups: List[StartupEntity],
        products: List[ProductEntity],
        research_papers: List[ResearchPaperEntity],
        jobs: List[JobEntity],
        news: List[NewsEntity],
        entity_logs: List[EntityMappingLog]
    ) -> str:
        """
        Exports datasets into individual CSV files and a single 6-tab Excel workbook.
        Returns filepath of the generated Excel workbook.
        """
        logger.info("Exporting all pipeline datasets to CSV and 6-tab Excel workbook...")

        # 1. Prepare DataFrames conforming strictly to requested JSON schemas
        df_startups = pd.DataFrame([s.model_dump(by_alias=True) for s in startups])
        df_products = pd.DataFrame([p.model_dump(by_alias=True) for p in products])
        df_papers = pd.DataFrame([r.model_dump(by_alias=True) for r in research_papers])
        df_jobs = pd.DataFrame([j.model_dump(by_alias=True) for j in jobs])
        df_news = pd.DataFrame([n.model_dump(by_alias=True) for n in news])
        df_entity_logs = pd.DataFrame([l.model_dump() for l in entity_logs])

        # Save individual CSVs
        df_startups.to_csv(os.path.join(self.output_dir, "startups.csv"), index=False)
        df_products.to_csv(os.path.join(self.output_dir, "products.csv"), index=False)
        df_papers.to_csv(os.path.join(self.output_dir, "research_papers.csv"), index=False)
        df_jobs.to_csv(os.path.join(self.output_dir, "jobs.csv"), index=False)
        df_news.to_csv(os.path.join(self.output_dir, "news.csv"), index=False)
        df_entity_logs.to_csv(os.path.join(self.output_dir, "entity_mapping_log.csv"), index=False)

        # 2. Save combined 6-tab Excel file
        excel_path = os.path.join(self.output_dir, "pipeline_output_all.xlsx")
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df_startups.to_excel(writer, sheet_name="Startups", index=False)
            df_products.to_excel(writer, sheet_name="Products", index=False)
            df_papers.to_excel(writer, sheet_name="Research Papers", index=False)
            df_jobs.to_excel(writer, sheet_name="Jobs", index=False)
            df_news.to_excel(writer, sheet_name="News", index=False)
            df_entity_logs.to_excel(writer, sheet_name="Entity Mapping Log", index=False)

        logger.info(f"Successfully generated 6-tab Excel dataset at: {excel_path}")
        return excel_path
