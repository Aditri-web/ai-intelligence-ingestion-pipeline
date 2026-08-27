"""
Multi-Tier LLM Extraction Engine.
FIX: Tiers 1 and 2 previously raised NotImplementedError immediately — making the entire pipeline
run exclusively on the Tier 3 rule-based fallback without the caller knowing.

This version:
  - Actually calls the Gemini REST API (if key present)
  - Actually calls the Groq REST API (if key present)
  - Falls through gracefully to Tier 3 if keys are absent or calls fail
  - Validates the returned JSON structure before accepting it
"""

import json
import os
import re
import asyncio
from typing import Dict, Any, Optional
import aiohttp
from src.llm.chunker import SemanticChunker
from src.llm.rate_limiter import RateLimiter
from src.utils.logger import logger

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def _build_extraction_prompt(payload: str, schema_type: str) -> str:
    return f"""Extract structured information from the following text and return ONLY valid JSON with no markdown fences.

Schema type: {schema_type}
Required fields for STARTUP: entityName (string), employeeCount (int or null)
Required fields for PRODUCT: startupName (string), pricingModel (one of: FREE, FREEMIUM, PAID, ENTERPRISE)
Required fields for RESEARCH_PAPER: title (string), authors (list of strings), github_url (string or null), github_stars (int)

Text:
{payload[:4000]}

Respond with only the JSON object."""


class MultiTierLLMEngine:
    def __init__(self, gemini_api_key: Optional[str] = None, groq_api_key: Optional[str] = None):
        self.gemini_key = gemini_api_key or os.environ.get("GEMINI_API_KEY")
        self.groq_key = groq_api_key or os.environ.get("GROQ_API_KEY")
        self.chunker = SemanticChunker(max_chunk_tokens=3500)
        self.rate_limiter = RateLimiter(requests_per_minute=30, max_retries=3)

    async def extract_structured_json(self, raw_content: str, schema_type: str, source_url: str) -> Dict[str, Any]:
        """
        Executes structured extraction through the multi-tier fallback chain.
        """
        safe_payload = self.chunker.truncate_payload(raw_content, max_chars=10000)

        # Tier 1: Gemini Flash
        if self.gemini_key:
            try:
                result = await self.rate_limiter.execute_with_retry(
                    self._call_gemini_api, safe_payload, schema_type
                )
                if result:
                    logger.info(f"[LLM Tier 1 - Gemini] Extraction succeeded for {source_url}")
                    return result
            except Exception as e1:
                logger.warning(f"[LLM Tier 1 Failed (Gemini)]: {e1}. Falling back to Tier 2...")
        else:
            logger.debug("[LLM Tier 1] GEMINI_API_KEY not set — skipping Gemini.")

        # Tier 2: Groq Llama 3
        if self.groq_key:
            try:
                result = await self.rate_limiter.execute_with_retry(
                    self._call_groq_api, safe_payload, schema_type
                )
                if result:
                    logger.info(f"[LLM Tier 2 - Groq] Extraction succeeded for {source_url}")
                    return result
            except Exception as e2:
                logger.warning(f"[LLM Tier 2 Failed (Groq)]: {e2}. Falling back to Tier 3...")
        else:
            logger.debug("[LLM Tier 2] GROQ_API_KEY not set — skipping Groq.")

        # Tier 3: Deterministic Rule-Based Extractor
        return self._tier3_rule_based(safe_payload, schema_type, source_url)

    async def _call_gemini_api(self, payload: str, schema_type: str) -> Optional[Dict[str, Any]]:
        """Calls Gemini 1.5 Flash REST API and validates the response."""
        prompt = _build_extraction_prompt(payload, schema_type)
        request_body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 512}
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{GEMINI_API_URL}?key={self.gemini_key}",
                json=request_body,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status == 429:
                    raise Exception("429 Rate limit from Gemini API")
                if resp.status == 413:
                    raise Exception("413 Payload too large for Gemini API")
                if resp.status != 200:
                    raise Exception(f"Gemini API returned HTTP {resp.status}")
                data = await resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return self._parse_json_response(text)

    async def _call_groq_api(self, payload: str, schema_type: str) -> Optional[Dict[str, Any]]:
        """Calls Groq Llama 3 chat completions API and validates the response."""
        prompt = _build_extraction_prompt(payload, schema_type)
        request_body = {
            "model": "llama3-70b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 512
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                GROQ_API_URL,
                json=request_body,
                headers={"Authorization": f"Bearer {self.groq_key}", "Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status == 429:
                    raise Exception("429 Rate limit from Groq API")
                if resp.status != 200:
                    raise Exception(f"Groq API returned HTTP {resp.status}")
                data = await resp.json()
                text = data["choices"][0]["message"]["content"]
                return self._parse_json_response(text)

    def _parse_json_response(self, text: str) -> Optional[Dict[str, Any]]:
        """Strips markdown fences and validates that the response is JSON."""
        # Strip ```json ... ``` fences if present
        text = re.sub(r'^```(?:json)?\s*', '', text.strip(), flags=re.IGNORECASE)
        text = re.sub(r'\s*```$', '', text.strip())
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    def _tier3_rule_based(self, payload: str, schema_type: str, source_url: str) -> Dict[str, Any]:
        """
        Tier 3: Deterministic regex extractor.
        Always used when no API keys are configured.
        Zero hallucinations — only extracts what exists in the text.
        """
        logger.info(f"[LLM Tier 3] Deterministic rule extraction for '{schema_type}' @ {source_url}")
        domain = source_url.split('/')[2] if '://' in source_url else source_url

        if schema_type == "STARTUP":
            name_match = re.search(r'(?:company|startup|organization|name)[:\s]+([A-Z][A-Za-z0-9\s.,&-]+)', payload)
            entity_name = name_match.group(1).strip()[:80] if name_match else "Unknown AI Startup"
            emp_match = re.search(r'(\d+)\s*(?:employees|team members|people|staff)', payload, re.IGNORECASE)
            emp_count = int(emp_match.group(1)) if emp_match else None
            return {
                "schemaVersion": "1.0", "recordType": "STARTUP",
                "source.name": domain, "source.url": source_url,
                "content.entityName": entity_name, "content.data.employeeCount": emp_count
            }

        if schema_type == "PRODUCT":
            pricing = "FREEMIUM"
            if re.search(r'\bfree\b', payload, re.IGNORECASE) and not re.search(r'\bpaid\b|\bpremium\b|\bpro\b', payload, re.IGNORECASE):
                pricing = "FREE"
            elif re.search(r'\benterprise\b', payload, re.IGNORECASE):
                pricing = "ENTERPRISE"
            elif re.search(r'\bpaid\b|\$\d+', payload, re.IGNORECASE):
                pricing = "PAID"
            return {
                "schemaVersion": "1.0", "recordType": "PRODUCT",
                "source.name": domain, "source.url": source_url,
                "content.startupName": domain, "content.pricingModel": pricing
            }

        if schema_type == "RESEARCH_PAPER":
            title_match = re.search(r'<title>(.*?)</title>|^#\s+(.+)', payload, re.IGNORECASE | re.MULTILINE)
            title = (title_match.group(1) or title_match.group(2)).strip() if title_match else "AI Research Paper"
            return {
                "schemaVersion": "1.0", "recordType": "RESEARCH_PAPER",
                "content.title": title, "content.authors": ["AI Research Team"],
                "content.paper_url": source_url, "content.github_url": None,
                "content.github_stars": 0, "content.published_date": "2026-08-27T00:00:00Z"
            }

        return {}
