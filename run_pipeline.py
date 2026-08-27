"""
Main Entrypoint CLI for the GraphOne / FrontierAtlas Ingestion Pipeline.
Executes end-to-end data acquisition, signal ingestion, LLM structuring, entity resolution,
and export to 6-tab Excel workbook and CSV datasets. Also generates architecture.pdf document.
"""

import asyncio
import os
import sys
from src.pipeline.orchestrator import IngestionPipelineOrchestrator
from generate_architecture_pdf import build_pdf

async def main():
    print("=================================================================")
    print("  GraphOne / FrontierAtlas - AI Engineer Pipeline Execution  ")
    print("=================================================================")
    
    # Step 1: Generate PDF Architecture Document
    print("\n[Step 1/2] Generating Technical Architecture Document (architecture.pdf)...")
    build_pdf("architecture.pdf")

    # Step 2: Run Async Data Ingestion Pipeline
    print("\n[Step 2/2] Running Ingestion & Entity Resolution Pipeline...")
    orchestrator = IngestionPipelineOrchestrator()
    stats = await orchestrator.run_pipeline()

    print("\n=================================================================")
    print("  PIPELINE EXECUTION & DELIVERABLE SUMMARY  ")
    print("=================================================================")
    print(f" Startups Extracted       : {stats['startups_count']} records (Min. 1,000)")
    print(f" Products Extracted       : {stats['products_count']} records (Min. 1,000)")
    print(f" Research Papers Extracted: {stats['research_papers_count']} records (Min. 1,000)")
    print(f" Fresh AI Jobs (<24h)     : {stats['jobs_count']} records")
    print(f" Fresh AI News (<24h)     : {stats['news_count']} records")
    print(f" Entity Resolution Logs   : {stats['entity_logs_count']} audit entries")
    print(f"\n Deliverables Generated:")
    print(f"  - 6-Tab Workbook : {os.path.abspath(stats['excel_output_path'])}")
    print(f"  - CSV Files Dir  : {os.path.abspath('data_output/')}")
    print(f"  - Architecture PDF: {os.path.abspath('architecture.pdf')}")
    print("=================================================================\n")

if __name__ == "__main__":
    asyncio.run(main())
