"""
Deterministic Entity Resolution & Canonicalization Engine.
Deduplicates messy input names (e.g. "OpenAI", "OpenAI, Inc.", "Open AI" -> "OpenAI")
by applying:
  1. Exact seed alias lookup
  2. Corporate suffix stripping + re-lookup
  3. True Levenshtein edit-distance fuzzy matching
  4. Title-case fallback

FIX: Replaced broken character-diff approximation with true Wagner-Fischer
Levenshtein distance matrix algorithm. Also fixed sanitize_string to NOT strip
meaningful AI company suffixes like "AI" and "io" from the brand name.
"""

import re
from typing import Tuple, List, Optional
from src.entity_resolution.seed_database import CANONICAL_SEED_ENTITIES
from src.config import EntityMappingLog
from src.utils.logger import logger

# FIX: Only strip legal/corporate entity suffixes, NOT brand identity words like "AI" or "io"
CORPORATE_SUFFIXES = [
    r'\b(incorporated|corporation|limited|pbc|llc|gmbh)\b',
    r'\b(inc|corp|ltd|co)\b(?=\.|,|\s|$)',  # Only strip abbreviated forms at word boundaries
]

class EntityResolver:
    def __init__(self):
        self.seed_map = {}
        for canonical, info in CANONICAL_SEED_ENTITIES.items():
            self.seed_map[canonical.lower()] = canonical
            for alias in info["aliases"]:
                self.seed_map[alias.lower()] = canonical

        self.mapping_logs: List[EntityMappingLog] = []

    def sanitize_string(self, raw_name: str) -> str:
        """
        Cleans raw organization names.
        FIX: Only strips true legal entity suffixes (Inc., LLC, Corp).
        Does NOT strip brand identity words like 'AI', 'io', 'tech'
        which are integral parts of many AI company names.
        """
        if not raw_name:
            return ""
        s = raw_name.strip()
        for pat in CORPORATE_SUFFIXES:
            s = re.sub(pat, '', s, flags=re.IGNORECASE)
        s = re.sub(r'[^\w\s]', ' ', s)
        s = re.sub(r'\s+', ' ', s).strip()
        return s

    def resolve_entity(self, raw_name: str, entity_type: str = "STARTUP") -> Tuple[str, float, str]:
        """
        Resolves a raw input string to its canonical name.
        Returns tuple: (canonical_name, confidence_score, resolution_method)
        """
        if not raw_name or not raw_name.strip():
            return "Unknown Entity", 0.0, "EMPTY_INPUT"

        raw_clean = raw_name.strip()
        raw_lower = raw_clean.lower()

        # 1. Direct exact match
        if raw_lower in self.seed_map:
            canonical = self.seed_map[raw_lower]
            self._log(raw_name, canonical, entity_type, 1.0, "EXACT_SEED_ALIAS_MATCH")
            return canonical, 1.0, "EXACT_SEED_ALIAS_MATCH"

        # 2. Sanitized match (legal suffix removal)
        sanitized = self.sanitize_string(raw_clean)
        sanitized_lower = sanitized.lower()
        if sanitized_lower and sanitized_lower in self.seed_map:
            canonical = self.seed_map[sanitized_lower]
            self._log(raw_name, canonical, entity_type, 0.95, "SANITIZED_SUFFIX_MATCH")
            return canonical, 0.95, "SANITIZED_SUFFIX_MATCH"

        # 3. True Levenshtein fuzzy match
        best_canonical = None
        best_score = 0.0
        compare_str = sanitized_lower if sanitized_lower else raw_lower

        for canonical_name in CANONICAL_SEED_ENTITIES.keys():
            score = self._levenshtein_similarity(compare_str, canonical_name.lower())
            if score > best_score:
                best_score = score
                best_canonical = canonical_name

        if best_score >= 0.80 and best_canonical:
            self._log(raw_name, best_canonical, entity_type, round(best_score, 3), "LEVENSHTEIN_FUZZY_MATCH")
            return best_canonical, round(best_score, 3), "LEVENSHTEIN_FUZZY_MATCH"

        # 4. Title-case fallback — preserve original brand name casing
        title_canonical = sanitized.title() if sanitized else raw_clean.title()
        self._log(raw_name, title_canonical, entity_type, 0.60, "TITLECASE_FALLBACK")
        return title_canonical, 0.60, "TITLECASE_FALLBACK"

    def _levenshtein_similarity(self, s1: str, s2: str) -> float:
        """
        True Wagner-Fischer Levenshtein edit distance algorithm.
        Returns normalized similarity score in [0, 1].
        FIX: Replaces previous broken character-zip approximation which
             gave inflated scores for short strings and wrong results overall.
        """
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        if s1 == s2:
            return 1.0

        len1, len2 = len(s1), len(s2)
        # Build full DP matrix
        dp = list(range(len2 + 1))
        for i in range(1, len1 + 1):
            prev_row = dp[:]
            dp[0] = i
            for j in range(1, len2 + 1):
                cost = 0 if s1[i - 1] == s2[j - 1] else 1
                dp[j] = min(
                    dp[j] + 1,          # deletion
                    dp[j - 1] + 1,      # insertion
                    prev_row[j - 1] + cost  # substitution
                )

        edit_dist = dp[len2]
        max_len = max(len1, len2)
        return 1.0 - (edit_dist / max_len)

    def _log(self, raw: str, canonical: str, entity_type: str, score: float, method: str):
        self.mapping_logs.append(EntityMappingLog(
            rawName=raw,
            canonicalName=canonical,
            entityType=entity_type,
            confidenceScore=score,
            resolutionMethod=method
        ))

    def get_logs(self) -> List[EntityMappingLog]:
        return self.mapping_logs
