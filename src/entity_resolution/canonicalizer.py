"""
Deterministic Entity Resolution & Canonicalization Engine.
Deduplicates messy input names (e.g. "OpenAI", "OpenAI, Inc.", "Open AI" -> "OpenAI")
by applying rule-based regex cleaning, exact seed database lookup, and Levenshtein fuzzy distance matching.
Generates an explicit audit log (Entity Mapping Log).
"""

import re
from typing import Tuple, List
from src.entity_resolution.seed_database import CANONICAL_SEED_ENTITIES
from src.config import EntityMappingLog
from src.utils.logger import logger

class EntityResolver:
    def __init__(self):
        self.seed_map = {}
        # Populate lowercase alias lookup table from seed entities
        for canonical, info in CANONICAL_SEED_ENTITIES.items():
            self.seed_map[canonical.lower()] = canonical
            for alias in info["aliases"]:
                self.seed_map[alias.lower()] = canonical

        self.mapping_logs: List[EntityMappingLog] = []

    def sanitize_string(self, raw_name: str) -> str:
        """
        Cleans and normalizes raw organization/product strings.
        Strips common corporate legal suffixes, extra punctuation, and whitespace.
        """
        if not raw_name:
            return ""

        s = raw_name.strip()
        # Remove common corporate suffixes
        patterns = [
            r'\b(inc|incorporated|corp|corporation|ltd|limited|pbc|llc|gmbh|co|co\.|ai|io|tech|technology|technologies)\b'
        ]
        s_clean = s
        for pat in patterns:
            s_clean = re.sub(pat, '', s_clean, flags=re.IGNORECASE)

        # Remove special characters
        s_clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', s_clean)
        s_clean = re.sub(r'\s+', ' ', s_clean).strip()
        return s_clean

    def resolve_entity(self, raw_name: str, entity_type: str = "STARTUP") -> Tuple[str, float, str]:
        """
        Resolves a raw input string to its canonical name.
        Returns tuple: (canonical_name, confidence_score, resolution_method)
        """
        if not raw_name or not raw_name.strip():
            return "Unknown Entity", 0.0, "EMPTY_INPUT"

        raw_clean = raw_name.strip()
        raw_lower = raw_clean.lower()

        # 1. Direct Match against seed map or exact alias
        if raw_lower in self.seed_map:
            canonical = self.seed_map[raw_lower]
            log_entry = EntityMappingLog(
                rawName=raw_name,
                canonicalName=canonical,
                entityType=entity_type,
                confidenceScore=1.0,
                resolutionMethod="EXACT_SEED_ALIAS_MATCH"
            )
            self.mapping_logs.append(log_entry)
            return canonical, 1.0, "EXACT_SEED_ALIAS_MATCH"

        # 2. Normalized Regex Suffix Removal Match
        sanitized = self.sanitize_string(raw_clean)
        sanitized_lower = sanitized.lower()

        if sanitized_lower in self.seed_map:
            canonical = self.seed_map[sanitized_lower]
            log_entry = EntityMappingLog(
                rawName=raw_name,
                canonicalName=canonical,
                entityType=entity_type,
                confidenceScore=0.95,
                resolutionMethod="SANITIZED_REGEX_MATCH"
            )
            self.mapping_logs.append(log_entry)
            return canonical, 0.95, "SANITIZED_REGEX_MATCH"

        # 3. Fuzzy Levenshtein Distance Match against Canonical List
        best_canonical = None
        best_ratio = 0.0

        for canonical_name in CANONICAL_SEED_ENTITIES.keys():
            ratio = self._similarity_ratio(sanitized_lower, canonical_name.lower())
            if ratio > best_ratio:
                best_ratio = ratio
                best_canonical = canonical_name

        if best_ratio >= 0.82 and best_canonical:
            log_entry = EntityMappingLog(
                rawName=raw_name,
                canonicalName=best_canonical,
                entityType=entity_type,
                confidenceScore=round(best_ratio, 2),
                resolutionMethod="FUZZY_LEVENSHTEIN_MATCH"
            )
            self.mapping_logs.append(log_entry)
            return best_canonical, round(best_ratio, 2), "FUZZY_LEVENSHTEIN_MATCH"

        # 4. Fallback: Title Case Format of Cleaned String
        title_canonical = sanitized.title() if sanitized else raw_clean.title()
        log_entry = EntityMappingLog(
            rawName=raw_name,
            canonicalName=title_canonical,
            entityType=entity_type,
            confidenceScore=0.70,
            resolutionMethod="DETERMINISTIC_TITLECASE_CANONICAL"
        )
        self.mapping_logs.append(log_entry)
        return title_canonical, 0.70, "DETERMINISTIC_TITLECASE_CANONICAL"

    def _similarity_ratio(self, s1: str, s2: str) -> float:
        """Computes simple normalized edit similarity between two strings."""
        if not s1 or not s2:
            return 0.0
        if s1 == s2:
            return 1.0

        # Simple character overlap & sequence match ratio
        set1, set2 = set(s1.split()), set(s2.split())
        overlap = len(set1.intersection(set2)) / max(len(set1), len(set2))
        
        # Levenshtein distance approximation
        len_max = max(len(s1), len(s2))
        dist = sum(1 for a, b in zip(s1, s2) if a != b) + abs(len(s1) - len(s2))
        lev_ratio = 1.0 - (dist / len_max)
        
        return max(overlap, lev_ratio)

    def get_logs(self) -> List[EntityMappingLog]:
        return self.mapping_logs
