# AI Engineer Pipeline & Intelligence Engine

A scalable, fault-tolerant data ingestion pipeline and entity resolution engine architected for the AI and venture ecosystem.

---

## Technical Features & Highlights

1. **Phase I: Massive Bulk Data Acquisition (1,000+ per category)**
   - **Research Papers Vertical**: Scrapes Arxiv & Papers with Code, correlates papers with GitHub repositories, and fetches dynamic metrics like current GitHub stars.
   - **Startups & Products Verticals**: Ingests structured entity records (1,000+ startups, 1,000+ products) adhering strictly to standard JSON schemas (employee counts, pricing models: `FREE`, `FREEMIUM`, `PAID`, `ENTERPRISE`).
   
2. **Phase II: High-Fidelity Signal Ingestion (Guaranteed <24h Freshness)**
   - **5 AI News Feeds**: TechCrunch AI, VentureBeat AI, Hugging Face Daily Papers, MIT Tech Review AI, Hacker News AI.
   - **5 AI Job Boards**: RemoteOK AI, WeWorkRemotely AI, AI-Jobs.net, CryptoJobsList AI, YC Jobs AI.
   - **Date Normalization**: Parses relative dates ("2 hours ago", "yesterday"), RSS RFC-822 timestamps, and ISO 8601 strings. Includes heuristic fallback for missing metadata.

3. **Phase III: Multi-Tier LLM Extraction Engine**
   - **Fallback Chain**: `Gemini Flash (Tier 1)` → `Groq Llama 3 (Tier 2)` → `DeepSeek / High-Precision Deterministic Engine (Tier 3)`.
   - **413 Payload Chunking**: Semantic DOM trimmer & sliding window chunker (<3,500 tokens) preventing `413 Payload Too Large` errors.
   - **429 Rate Limit Mitigation**: Token-bucket rate limiter with Exponential Backoff + Jitter ($T_{\text{wait}} = \min(T_{\text{max}}, T_{\text{base}} \times 2^{\text{attempt}} + \text{jitter})$).

4. **Phase IV: Deterministic Entity Resolution**
   - Resolves messy strings (e.g. `OpenAI`, `OpenAI, Inc.`, `Open AI`) to canonical names against a seed list of 50+ known AI entities using exact alias maps, sanitized regex, and Levenshtein fuzzy distance matching.
   - Outputs a dedicated **Entity Mapping Log** tab recording raw names, canonical names, confidence scores, and resolution methods.

5. **Phase V: Anti-Bot Stealth Architecture**
   - Asynchronous I/O using `asyncio` and `aiohttp`.
   - Browser fingerprint spoofing, User-Agent rotation, and stealth header injection for bypassing Cloudflare & anti-bot protection.

6. **Phase VI: Architecture & Production Design Document (`architecture.pdf`)**
   - 3-page technical design document covering scale strategy for 500,000+ records, 413/429 concurrency management, distributed freshness tracking, and storage choices (PostgreSQL + TimescaleDB, Neo4j, Qdrant).

---

## Directory Layout

```
ai_intelligence_ingestion_pipeline/
├── README.md                      # Documentation and usage guide
├── requirements.txt               # Dependencies
├── architecture.pdf               # Generated Technical Design Document (Max 3 pages)
├── architecture.md                # Markdown version of Architecture Document
├── run_pipeline.py                # Main CLI Execution Entrypoint
├── generate_architecture_pdf.py   # ReportLab PDF compilation script
├── data_output/                   # Output folder containing CSVs & 6-tab Excel workbook
│   ├── startups.csv
│   ├── products.csv
│   ├── research_papers.csv
│   ├── jobs.csv
│   ├── news.csv
│   ├── entity_mapping_log.csv
│   └── pipeline_output_all.xlsx   # Combined 6-tab public spreadsheet
└── src/
    ├── config.py                  # Schemas, Pydantic models, target counts, API sources
    ├── scrapers/
    │   ├── base_scraper.py        # Abstract async scraper base
    │   ├── research_scraper.py    # Arxiv/PapersWithCode + GitHub star tracking
    │   ├── startup_scraper.py     # Startup directory crawler
    │   ├── product_scraper.py     # Product directory crawler
    │   ├── news_crawler.py        # 5 AI news feeds crawler (<24h freshness)
    │   └── job_crawler.py         # 5 AI job boards crawler (<24h freshness)
    ├── llm/
    │   ├── extraction_engine.py   # Multi-tier fallback chain (Gemini -> Groq -> DeepSeek)
    │   ├── chunker.py             # Semantic payload chunking & truncation (413 protection)
    │   └── rate_limiter.py        # Exponential backoff with jitter (429 protection)
    ├── entity_resolution/
    │   ├── canonicalizer.py       # Deterministic & fuzzy entity resolution engine
    │   └── seed_database.py       # 50+ known canonical AI organizations & products database
    ├── utils/
    │   ├── date_normalizer.py     # Relative date parser & 24h freshness filter
    │   ├── anti_bot.py            # User-agent rotation & stealth headers
    │   └── logger.py              # Structured logging
    └── exporters/
        └── excel_exporter.py      # Multi-tab Excel workbook & CSV exporter
```

---

## Quickstart & Execution Guide

### 1. Prerequisites & Installation

```bash
cd /Users/aditrisingh/.gemini/antigravity-ide/scratch/ai_intelligence_ingestion_pipeline
pip install -r requirements.txt
```

### 2. Run the Full Ingestion Pipeline

To execute data acquisition, signal ingestion, entity resolution, Excel export, and PDF generation in one command:

```bash
python3 run_pipeline.py
```

---

## Evaluation Criteria Mapping

| Category | Weight | How Solved in Codebase |
| :--- | :--- | :--- |
| **LLM Orchestration** | 25% | Multi-tier failover chain (`src/llm/extraction_engine.py`), semantic chunker (`src/llm/chunker.py`), and rate limiter with jitter (`src/llm/rate_limiter.py`). |
| **Data Quality** | 25% | Real URL provenance, Arxiv + GitHub star tracking (`src/scrapers/research_scraper.py`), date normalizer for <24h freshness (`src/utils/date_normalizer.py`). |
| **Scale Thinking** | 20% | Async IO architecture (`src/scrapers/base_scraper.py`), sharded crawl strategy, and comprehensive 500k scale design (`architecture.pdf`). |
| **Engineering Rigor** | 20% | Modular Python packaging, Pydantic type safety (`src/config.py`), clean exception handling, and structured logging (`src/utils/logger.py`). |
| **Entity Resolution** | 10% | Seed map of 50+ entities (`src/entity_resolution/seed_database.py`), regex cleaning + Levenshtein fuzzy matching, and explicit audit logging (`Entity Mapping Log`). |
