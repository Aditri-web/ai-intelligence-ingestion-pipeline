"""
Configuration module for the AI Intelligence Ingestion Pipeline.
Defines schemas, API settings, fallback tiers, and operational constants.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import datetime

class RecordType(str, Enum):
    STARTUP = "STARTUP"
    PRODUCT = "PRODUCT"
    RESEARCH_PAPER = "RESEARCH_PAPER"
    JOB = "JOB"
    NEWS = "NEWS"

class PricingModel(str, Enum):
    FREE = "FREE"
    FREEMIUM = "FREEMIUM"
    PAID = "PAID"
    ENTERPRISE = "ENTERPRISE"

# --- Schemas ---

class StartupContent(BaseModel):
    entityName: str = Field(..., description="Canonical startup name")
    employeeCount: Optional[int] = Field(None, description="Number of employees if available")
    description: Optional[str] = Field(None, description="Short summary/description")
    tags: List[str] = Field(default_factory=list, description="Industry tags or categories")

class StartupEntity(BaseModel):
    schemaVersion: str = "1.0"
    recordType: str = "STARTUP"
    sourceName: str = Field(..., alias="source.name")
    sourceUrl: str = Field(..., alias="source.url")
    contentEntityName: str = Field(..., alias="content.entityName")
    contentEmployeeCount: Optional[int] = Field(None, alias="content.data.employeeCount")
    collectedAt: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    class Config:
        populate_by_name = True

class ProductContent(BaseModel):
    startupName: str = Field(..., description="Canonical startup/company name")
    pricingModel: PricingModel = Field(PricingModel.FREEMIUM, description="Pricing model enum")
    productName: Optional[str] = Field(None, description="Name of the product")

class ProductEntity(BaseModel):
    schemaVersion: str = "1.0"
    recordType: str = "PRODUCT"
    sourceName: str = Field(..., alias="source.name")
    sourceUrl: str = Field(..., alias="source.url")
    contentStartupName: str = Field(..., alias="content.startupName")
    contentPricingModel: str = Field(..., alias="content.pricingModel")
    collectedAt: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    class Config:
        populate_by_name = True

class ResearchPaperEntity(BaseModel):
    schemaVersion: str = "1.0"
    recordType: str = "RESEARCH_PAPER"
    title: str = Field(..., alias="content.title")
    authors: List[str] = Field(default_factory=list, alias="content.authors")
    paperUrl: str = Field(..., alias="content.paper_url")
    githubUrl: Optional[str] = Field(None, alias="content.github_url")
    githubStars: Optional[int] = Field(0, alias="content.github_stars")
    publishedDate: str = Field(..., alias="content.published_date")
    collectedAt: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    class Config:
        populate_by_name = True

class JobEntity(BaseModel):
    schemaVersion: str = "1.0"
    recordType: str = "JOB"
    company: str = Field(..., alias="content.company")
    date: str = Field(..., alias="content.date")
    isRemote: bool = Field(True, alias="content.is_remote")
    roleFamily: str = Field("Engineering", alias="content.role_family")
    title: Optional[str] = Field(None, alias="content.title")
    sourceUrl: Optional[str] = Field(None, alias="source.url")
    collectedAt: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    class Config:
        populate_by_name = True

class NewsEntity(BaseModel):
    schemaVersion: str = "1.0"
    recordType: str = "NEWS"
    title: str = Field(..., alias="content.title")
    sourceName: str = Field(..., alias="content.source_name")
    url: str = Field(..., alias="content.url")
    publishedDate: str = Field(..., alias="content.published_date")
    summary: Optional[str] = Field(None, alias="content.summary")
    collectedAt: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    class Config:
        populate_by_name = True

class EntityMappingLog(BaseModel):
    rawName: str
    canonicalName: str
    entityType: str
    confidenceScore: float
    resolutionMethod: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

# --- Target Counts for Bulk & Fresh Pipeline ---
TARGET_COUNTS = {
    "startups": 1000,
    "products": 1000,
    "research_papers": 1000,
    "jobs": 100,  # fresh <24h jobs
    "news": 100,   # fresh <24h news
}

# AI News Sources (5 Distinct Feeds)
AI_NEWS_SOURCES = [
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/"},
    {"name": "Hugging Face Daily Papers", "url": "https://huggingface.co/api/daily_papers"},
    {"name": "MIT Tech Review AI", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed"},
    {"name": "Hacker News AI", "url": "https://hn.algolia.com/api/v1/search_by_date?tags=story&query=AI"}
]

# AI Job Boards (5 Distinct Feeds)
AI_JOB_BOARDS = [
    {"name": "RemoteOK AI", "url": "https://remoteok.com/api?tag=ai"},
    {"name": "WeWorkRemotely AI", "url": "https://weworkremotely.com/categories/remote-back-end-programming-jobs.rss"},
    {"name": "AI-Jobs.net", "url": "https://ai-jobs.net/feed/"},
    {"name": "CryptoJobsList AI", "url": "https://cryptojobslist.com/tags/ai.rss"},
    {"name": "YC Jobs AI", "url": "https://www.ycombinator.com/jobs/role/machine-learning-engineer"}
]
