"""
PDF Architecture Document Generator using ReportLab.
Compiles the technical design document into a professional 3-page PDF file: architecture.pdf
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def build_pdf(filename: str = "architecture.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#2563EB'),
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=10,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=12,
        spaceAfter=3
    )

    story = []

    # Title
    story.append(Paragraph("GraphOne / FrontierAtlas - Technical Architecture", title_style))
    story.append(Paragraph("Global AI Intelligence Graph Ingestion Engine | Production Design Document", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=8))

    # Section 1: Executive Summary & Scale Strategy
    story.append(Paragraph("1. Scale Strategy (Ingesting 500,000+ Entities Hand-Free)", h1_style))
    story.append(Paragraph(
        "To acquire 500,000+ Startups, Products, Research Papers, Jobs, and News items without manual intervention, "
        "our ingestion architecture decouples discovery, extraction, enrichment, and storage into a distributed event-driven actor system. "
        "Built on Playwright Async, aiohttp, Celery, and Kafka over Kubernetes, the system handles hundreds of thousands of requests concurrently.",
        body_style
    ))

    story.append(Paragraph("<b>Core Scale Mechanisms:</b>", body_style))
    story.append(Paragraph("&bull; <b>Sharded Distributed Workers:</b> Web crawlers run as async microservices. Crawl targets are sharded dynamically via consistent hashing across cluster pods.", bullet_style))
    story.append(Paragraph("&bull; <b>Anti-Bot Proxy &amp; Stealth Swarm:</b> Rotates proxy IPs (Smartproxy/BrightData) and spoofing browser TLS stack fingerprints to bypass Cloudflare and Datadome protections.", bullet_style))
    story.append(Paragraph("&bull; <b>Recursive Seed Discovery:</b> Automated crawlers continually discover new entities from arXiv feeds, YC directories, and ProductHunt releases.", bullet_style))

    # Section 2: 413s & 429s
    story.append(Spacer(1, 6))
    story.append(Paragraph("2. Managing LLM 413 Context Windows &amp; 429 Rate Limits", h1_style))
    story.append(Paragraph(
        "LLM payload processing faces two main bottlenecks: <b>413 Payload Too Large</b> (context overflows) and <b>429 Rate Limits</b>. "
        "Our multi-tier engine guarantees resilient structuring through payload chunking and failover chains.",
        body_style
    ))
    story.append(Paragraph("&bull; <b>413 Payload Chunking:</b> Raw HTML is stripped of non-content tags (&lt;script&gt;, &lt;style&gt;). Large payloads are chunked into semantically dense sections (&lt;3,500 tokens) retaining structural header anchors.", bullet_style))
    story.append(Paragraph("&bull; <b>Multi-Tier LLM Fallback Chain:</b> Primary: Gemini 1.5/2.0 Flash &rarr; Secondary: Groq Llama 3 70B &rarr; Tertiary: DeepSeek Chat / Rule-based Extractor.", bullet_style))
    story.append(Paragraph("&bull; <b>429 Exponential Backoff with Jitter:</b> Token bucket rate-limiter delays requests using <i>Wait = min(T_max, T_base * 2^attempt + jitter)</i>, coordinated across pods via Redis.", bullet_style))

    # Section 3: Freshness Tracking
    story.append(Spacer(1, 6))
    story.append(Paragraph("3. Distributed Freshness Tracking (&lt; 24 Hours)", h1_style))
    story.append(Paragraph(
        "High-velocity signals (News &amp; Jobs) must be guaranteed to have been published within the last 24 hours without duplicate processing across crawler nodes:",
        body_style
    ))
    story.append(Paragraph("&bull; <b>Redis Bloom Filters:</b> O(1) timestamp check skips URLs processed within the last 24 hours.", bullet_style))
    story.append(Paragraph("&bull; <b>Content SHA-256 Hash Deduplication:</b> SHA-256 hashes of normalized article texts merge syndicated press releases into a single event.", bullet_style))
    story.append(Paragraph("&bull; <b>Date Normalization Engine:</b> Parses relative dates ('2 hours ago'), RSS RFC-822, and ISO strings, falling back to DOM modification heuristics if metadata is missing.", bullet_style))

    # Section 4: Storage Strategy Table
    story.append(Spacer(1, 6))
    story.append(Paragraph("4. Storage Strategy (Primary DB, Graph, Vector Storage)", h1_style))
    story.append(Paragraph("We deploy a Tri-Storage Hybrid Architecture to power complex intelligence graph queries:", body_style))

    table_data = [
        [Paragraph("<b>Database</b>", body_style), Paragraph("<b>Technology</b>", body_style), Paragraph("<b>Role &amp; Justification</b>", body_style)],
        [
            Paragraph("Primary DB", body_style),
            Paragraph("PostgreSQL 16 + TimescaleDB", body_style),
            Paragraph("ACID compliant relational storage for canonical records, time-series telemetry, and schema validation.", body_style)
        ],
        [
            Paragraph("Knowledge Graph", body_style),
            Paragraph("Neo4j Enterprise", body_style),
            Paragraph("Maps relationships: (Founder)-[:FOUNDED]-&gt;(Startup)-[:PRODUCES]-&gt;(Product) for sub-ms multi-hop traversals.", body_style)
        ],
        [
            Paragraph("Vector DB", body_style),
            Paragraph("Qdrant / Milvus", body_style),
            Paragraph("Stores text-embedding-3-large vectors for semantic search, cross-entity matching, and RAG discovery.", body_style)
        ]
    ]

    table = Table(table_data, colWidths=[1.1*inch, 1.8*inch, 4.3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))

    story.append(Spacer(1, 6))
    story.append(table)
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=6))
    story.append(Paragraph("<b>GraphOne / FrontierAtlas AI Ingestion Pipeline Architecture</b> | Generated Automatically", ParagraphStyle('Foot', parent=body_style, fontSize=8, textColor=colors.HexColor('#64748B'))))

    doc.build(story)
    print(f"Architecture PDF generated successfully at: {filename}")

if __name__ == "__main__":
    build_pdf()
