#!/usr/bin/env python3
"""
BuddAI — Learning Engine

Corrections become permanent patterns. You teach it once, it applies forever.

Features:
- Store corrections permanently
- Extract patterns from corrections
- Apply corrections automatically to future code
- Track correction effectiveness

Usage:
    from intelligence.buddai.learning import LearningEngine

    engine = LearningEngine()
    engine.learn("ESP32 uses ledcWrite, not analogWrite", tags=["esp32", "pwm"])
    patterns = engine.get_patterns("esp32")
"""

import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path


class LearningEngine:
    """
    BuddAI learning engine — corrections become permanent patterns.
    """

    def __init__(self, db_path: str = "buddai_learning.db"):
        """
        Initialise learning engine.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._init_db()
        self.patterns = []
        self._load_patterns()

    def _init_db(self):
        """Initialise SQLite database."""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original TEXT,
                correction TEXT,
                pattern TEXT,
                tags TEXT,
                applied_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_applied TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def _load_patterns(self):
        """Load all patterns from database."""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM patterns
            ORDER BY applied_count DESC
        """)
        self.patterns = [dict(row) for row in cursor.fetchall()]

        conn.close()

    def learn(self, correction: str, tags: Optional[List[str]] = None) -> int:
        """
        Learn a correction as a permanent pattern.

        Args:
            correction: The correction text
            tags: List of tags

        Returns:
            Pattern ID
        """
        import sqlite3

        tags_json = json.dumps(tags or [])

        # Extract pattern from correction
        pattern = self._extract_pattern(correction)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO patterns (original, correction, pattern, tags)
            VALUES (?, ?, ?, ?)
        """, (correction, correction, pattern, tags_json))

        pattern_id = cursor.lastrowid
        conn.commit()
        conn.close()

        if pattern_id is None:
            raise RuntimeError("Failed to retrieve the ID for the inserted pattern")

        self._load_patterns()
        return pattern_id

    def _extract_pattern(self, text: str) -> str:
        """
        Extract a reusable pattern from correction text.

        Args:
            text: Correction text

        Returns:
            Pattern string
        """
        # Simple pattern extraction
        patterns = []

        # Look for "use X instead of Y" patterns
        use_instead = re.search(r'use\s+([^,\.]+)\s+instead\s+of\s+([^,\.]+)', text, re.IGNORECASE)
        if use_instead:
            patterns.append(f"prefer {use_instead.group(1)} over {use_instead.group(2)}")

        # Look for "X uses Y" patterns
        uses_pattern = re.search(r'([A-Za-z0-9_]+)\s+uses\s+([^,\.]+)', text, re.IGNORECASE)
        if uses_pattern:
            patterns.append(f"{uses_pattern.group(1)} uses {uses_pattern.group(2)}")

        # Look for "replace X with Y" patterns
        replace = re.search(r'replace\s+([^,\.]+)\s+with\s+([^,\.]+)', text, re.IGNORECASE)
        if replace:
            patterns.append(f"use {replace.group(2)} instead of {replace.group(1)}")

        # Fallback
        if not patterns:
            patterns.append(text[:100])

        return "; ".join(patterns)

    def get_patterns(self, query: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get patterns matching a query.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of pattern dicts
        """
        results = []
        query_lower = query.lower()

        for pattern in self.patterns:
            if (query_lower in pattern.get("correction", "").lower() or
                query_lower in pattern.get("pattern", "").lower() or
                query_lower in pattern.get("tags", "").lower()):
                results.append(pattern)

        return results[:limit]

    def apply_patterns(self, code: str, tags: Optional[List[str]] = None) -> str:
        """
        Apply learned patterns to code.

        Args:
            code: Code string to apply patterns to
            tags: Tags to filter patterns

        Returns:
            Modified code string
        """
        patterns = self.patterns

        if tags:
            tag_str = json.dumps(tags)
            patterns = [p for p in patterns if tag_str in p.get("tags", "")]

        for pattern in patterns:
            # Simple pattern application
            correction = pattern.get("correction", "")
            original = pattern.get("original", "")

            # Try to replace
            if original and original in code:
                code = code.replace(original, correction)
                self._increment_apply(pattern["id"])

        return code

    def _increment_apply(self, pattern_id: int):
        """Increment applied count for a pattern."""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE patterns
            SET applied_count = applied_count + 1,
                last_applied = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (pattern_id,))

        conn.commit()
        conn.close()

    def record_success(self, pattern_id: int):
        """Record a successful pattern application."""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE patterns
            SET success_count = success_count + 1
            WHERE id = ?
        """, (pattern_id,))

        conn.commit()
        conn.close()

    def get_stats(self) -> Dict[str, Any]:
        """Get learning statistics."""
        if not self.patterns:
            return {"total": 0, "applied": 0, "success_rate": 0.0}

        total = len(self.patterns)
        applied = sum(p.get("applied_count", 0) for p in self.patterns)
        successes = sum(p.get("success_count", 0) for p in self.patterns)

        return {
            "total": total,
            "applied": applied,
            "success_rate": successes / applied if applied > 0 else 0.0,
        }


# ============================================================
# CLI
# ============================================================

def main():
    """Test learning engine."""
    import sys

    engine = LearningEngine("test_learning.db")

    print("BuddAI — Learning Engine Test")
    print("=" * 60)

    # Learn corrections
    corrections = [
        "ESP32 uses ledcWrite, not analogWrite",
        "Use millis() instead of delay() for timing",
        "ESP32 ADC resolution is 12-bit (0-4095)",
    ]

    for corr in corrections:
        engine.learn(corr)
        print(f"✅ Learned: {corr}")

    # Get patterns
    patterns = engine.get_patterns("esp32")
    print(f"\nPatterns for 'esp32': {len(patterns)}")
    for p in patterns:
        print(f"  - {p['pattern']}")

    # Stats
    stats = engine.get_stats()
    print(f"\nStats: {stats}")


if __name__ == "__main__":
    main()
