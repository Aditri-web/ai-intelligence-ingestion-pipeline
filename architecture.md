# GraphOne / FrontierAtlas - System Architecture & Production Design Document

## Executive Summary
This document outlines the production architecture for **GraphOne / FrontierAtlas's Global AI Intelligence Graph Ingestion Engine**. Designed to operate continuously at scale, the infrastructure ingests, normalizes, and enriches multi-dimensional datasets covering **500,000+ Startups, Products, Research Papers, News Signals, and Job Openings** across thousands of global sources.

---

## 1. Scale Strategy (Ingesting 500,000+ Entities Hand-Free)

To scale from tens of thousands of records to **500,000+ entities without manual intervention**, our architecture decouples discovery, extraction, enrichment, and storage into an event-driven, distributed actor network powered by **Celery / Temporal.io** over **Kubernetes (GKE)**.

```
                  +-----------------------------------+
                  |   Distributed Crawler Nodes       |
                  |  (Playwright / Async aiohttp Pool)|
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------+-----------------+
                  |   Kafka Event Stream / Redis Bus  |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------+-----------------+
                  | Multi-Tier LLM Extraction Engine |
                  | (Gemini / Groq / DeepSeek Pool)  |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------+-----------------+
                  | Deterministic Entity Resolver    |
                  +-----------------+-----------------+
                                    |
       +----------------------------+----------------------------+
       |                            |                            |
       v                            v                            v
+--------------+           +------------------+         +------------------+
| PostgreSQL   |           |  Neo4j Knowledge |         | Qdrant Vector DB |
| TimescaleDB  |           |     Graph DB     |         | (Semantic Index) |
+--------------+           +------------------+         +------------------+
```

### Core Scale Principles:
1. **Asynchronous Distributed Worker Clusters**:
   - Web crawlers are containerized microservices operating on **Playwright Async** and **aiohttp**.
   - Sharded crawl targets are dynamically assigned via consistent hashing algorithms (`hash(domain) % worker_nodes`).
2. **Anti-Bot Proxy & TLS Fingerprint Swarm**:
   - Bypasses Cloudflare / Datadome protections using proxy pools (BrightData/Smartproxy) combined with browser fingerprint spoofing (Chromium TLS stack imitation, HTTP/2 frame ordering, headers rotation).
3. **Automated Seed Discovery Pipeline**:
   - Recursive URL crawler recursively discovers new startups, products, and papers from arXiv RSS, GitHub Trending, ProductHunt feeds, and YC directory updates.

---

## 2. Handling 413s & 429s (Context Windows & Concurrency)

LLM pipeline bottlenecks are dominated by **413 Payload Too Large** (context overflows) and **429 Too Many Requests** (rate limits). Our multi-tier LLM engine solves both deterministically:

### Handling 413s (Payload Too Large & Context Window Management):
- **Semantic DOM Truncation**: Raw HTML pages are stripped of non-content nodes (`<script>`, `<style>`, `<nav>`, `<footer>`, SVG paths).
- **Sliding-Window Semantic Chunker**: High-density content is tokenized into chunks (< 3,500 tokens). Headers, meta tags, and structured schema anchors are attached to every chunk so context is retained.
- **Payload Compression**: Text payload is compressed using Gzip before hitting API endpoints.

### Handling 429s (Rate Limits & API Quota Overflows):
- **Multi-Tier LLM Fallback Chain**:
  - **Tier 1**: Gemini 1.5/2.0 Flash (Primary high-throughput tier)
  - **Tier 2**: Groq Llama 3 70B (Secondary sub-second fallback)
  - **Tier 3**: DeepSeek Chat / Local vLLM Cluster (Tertiary failover)
- **Token Bucket Rate Limiting with Full Jitter**:
  - Retries follow exponential backoff with full randomized jitter:
    $$\text{WaitTime} = \min\left(T_{\text{max}}, T_{\text{base}} \times 2^{\text{attempt}} + \text{random\_jitter}\right)$$
- **Distributed Token Bucket Queue**: Distributed Redis rate-limiter coordinates API requests across all worker pods to stay strictly under provider RPM/TPM thresholds.

---

## 3. Freshness Tracking (< 24 Hours & Deduplication Across Nodes)

To ensure zero duplicate crawling and guarantee sub-24-hour freshness for high-velocity signals (News & Jobs):

1. **Distributed Bloom Filters & Redis Timestamp Caching**:
   - Before crawling a URL, nodes perform an $O(1)$ query against a **Redis Scalable Bloom Filter**.
   - If a URL was processed within 24 hours, the crawl is skipped immediately.
2. **Content Hash (SHA-256) Deduplication**:
   - Extracted full-text articles are hashed ($\text{SHA-256}(\text{normalized\_content})$).
   - Identical press releases syndicated across multiple news outlets are merged automatically into a single canonical event.
3. **Publication Date Normalization Heuristics**:
   - Parses ISO dates, RSS RFC-822 timestamps, and relative date phrases ("3 hours ago").
   - If metadata is missing, content freshness is calculated using DOM modification headers and RSS feed sequence position heuristics.

---

## 4. Storage Strategy (Primary DB, Graph, Vector)

To support GraphOne's intelligence graph querying requirements, we deploy a **Tri-Storage Hybrid Architecture**:

| Database | Technology | Primary Role & Justification |
| :--- | :--- | :--- |
| **Primary Relational DB** | **PostgreSQL 16 + TimescaleDB** | Stores canonical tables (Startups, Products, Research Papers, Jobs, News) with ACID compliance, schema validation, and time-series analytical capabilities. |
| **Knowledge Graph DB** | **Neo4j Enterprise** | Maps multi-dimensional relationships: `(Founder)-[:FOUNDED]->(Startup)-[:PRODUCES]->(Product)` and `(Paper)-[:USES_REPO]->(GitHubRepo)`. Enables sub-millisecond multi-hop graph traversals. |
| **Vector DB** | **Qdrant / Milvus** | Stores dense embeddings (text-embedding-3-large) for semantic similarity search, cross-entity matching, and RAG discovery across unstructured job listings and research abstracts. |

---

## 5. Summary Evaluation Matrix

- **LLM Orchestration**: Multi-tier failover chain + semantic payload chunker + exponential backoff jitter.
- **Data Quality**: 100% real URL provenance, strict date parsing, live GitHub star tracking.
- **Scale Thinking**: Distributed worker nodes, Kafka event streams, Redis bloom filter deduplication.
- **Entity Resolution**: Deterministic alias lookup, regex cleaning, and Levenshtein fuzzy matching logged explicitly in the audit table.
