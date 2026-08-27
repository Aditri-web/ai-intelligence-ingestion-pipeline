"""
Date Normalization module for parsing, standardizing, and checking 24-hour freshness.
Handles relative date strings ("2 hours ago", "yesterday", "3 mins ago"), RFC-822/2822 RSS formats,
ISO 8601 strings, and fallback heuristics for missing publication metadata.
"""

import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from email.utils import parsedate_to_datetime

class DateNormalizer:
    @staticmethod
    def parse_date(date_str: Optional[str]) -> Optional[datetime]:
        """
        Parses raw date strings into standard UTC datetime objects.
        Handles relative phrases, RSS date formats, ISO strings, etc.
        """
        if not date_str:
            return None

        date_str = str(date_str).strip()
        now = datetime.now(timezone.utc)

        # 1. Relative time parsing (e.g. "2 hours ago", "15 mins ago", "1 day ago")
        rel_match = re.search(r'(\d+)\s+(second|sec|minute|min|hour|hr|day|d)\w*\s+ago', date_str, re.IGNORECASE)
        if rel_match:
            val = int(rel_match.group(1))
            unit = rel_match.group(2).lower()
            if unit.startswith('s'):
                return now - timedelta(seconds=val)
            elif unit.startswith('m'):
                return now - timedelta(minutes=val)
            elif unit.startswith('h'):
                return now - timedelta(hours=val)
            elif unit.startswith('d'):
                return now - timedelta(days=val)

        # "just now" / "today" / "yesterday"
        if re.search(r'just now|moments ago', date_str, re.IGNORECASE):
            return now
        if re.search(r'yesterday', date_str, re.IGNORECASE):
            return now - timedelta(days=1)

        # 2. RFC-822 / RSS format (e.g., "Wed, 26 Aug 2026 14:20:00 GMT")
        try:
            dt = parsedate_to_datetime(date_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass

        # 3. ISO 8601 parsing (e.g. "2026-08-27T14:30:00Z", "2026-08-27")
        try:
            cleaned_str = date_str.replace('Z', '+00:00')
            dt = datetime.fromisoformat(cleaned_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass

        # 4. Common standard date string formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d %b %Y",
            "%b %d, %Y",
            "%B %d, %Y",
            "%Y/%m/%d"
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue

        return None

    @classmethod
    def normalize_to_iso(cls, date_str: Optional[str], default_now: bool = True) -> str:
        """
        Converts any date string into canonical ISO-8601 UTC string.
        If unparseable and default_now=True, uses current timestamp.
        """
        dt = cls.parse_date(date_str)
        if dt:
            return dt.isoformat()
        if default_now:
            return datetime.now(timezone.utc).isoformat()
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    def is_within_24_hours(cls, date_str: Optional[str], fallback_allow: bool = True) -> Tuple[bool, str]:
        """
        Checks if publication date is within the last 24 hours.
        Returns tuple of (is_fresh, iso_date_string).
        If date string is missing/unparseable and fallback_allow is True, uses heuristic evaluation.
        """
        dt = cls.parse_date(date_str)
        now = datetime.now(timezone.utc)
        if dt:
            diff = now - dt
            is_fresh = timedelta(0) <= diff <= timedelta(hours=24)
            return is_fresh, dt.isoformat()
        
        # Intelligent Heuristic fallback:
        # If strict date metadata is absent, content discovered on active stream feed is assumed recent (<24h)
        return fallback_allow, now.isoformat()
