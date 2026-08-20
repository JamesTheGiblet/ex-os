#!/usr/bin/env python3
"""
BuddAI — Memory System

Short-term and long-term memory with Forge Theory decay.

Features:
- Short-term memory (session-based)
- Long-term memory (SQLite persistent)
- Forge Theory decay: weight(t) = initial × e^(-k × days)
- Promotion from short to long term
- Consolidation (nightly learning loop)

Usage:
    from intelligence.buddai.memory import MemorySystem

    memory = MemorySystem(db_path="buddai_memory.db")
    memory.remember("ESP32 uses ledcWrite", "correction", tags=["esp32", "pwm"])
    memories = memory.recall("esp32")
"""

import sqlite3
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path
import math


class MemorySystem:
    """
    BuddAI memory system — short-term and long-term with Forge Theory decay.
    """

    def __init__(self, db_path: str = "buddai_memory.db", decay_k: float = 0.01):
        """
        Initialise memory system.

        Args:
            db_path: Path to SQLite database
            decay_k: Forge Theory decay constant
        """
        self.db_path = db_path
        self.decay_k = decay_k
        self.short_term = []
        self._init_db()

    def _init_db(self):
        """Initialise SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Short-term memory table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS short_term (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                weight REAL DEFAULT 1.0,
                tags TEXT,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Long-term memory table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS long_term (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                weight REAL DEFAULT 1.0,
                tags TEXT,
                promoted_from INTEGER,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Corrections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS corrections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original TEXT,
                correction TEXT,
                pattern TEXT,
                tags TEXT,
                applied_count INTEGER DEFAULT 0,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def remember(
        self,
        content: str,
        memory_type: str = "short_term",
        tags: Optional[List[str]] = None,
        weight: float = 1.0
    ) -> int:
        """
        Store a memory.

        Args:
            content: Memory content
            memory_type: "short_term" or "long_term"
            tags: List of tags
            weight: Initial weight

        Returns:
            Memory ID
        """
        tags_json = json.dumps(tags or [])

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if memory_type == "short_term":
            cursor.execute("""
                INSERT INTO short_term (content, weight, tags)
                VALUES (?, ?, ?)
            """, (content, weight, tags_json))
        else:
            cursor.execute("""
                INSERT INTO long_term (content, weight, tags)
                VALUES (?, ?, ?)
            """, (content, weight, tags_json))

        memory_id = cursor.lastrowid
        conn.commit()
        conn.close()

        if memory_id is None:
            raise RuntimeError("Failed to retrieve the ID for the inserted memory")

        return memory_id

    def recall(
        self,
        query: str,
        memory_type: str = "all",
        min_weight: float = 0.1,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Recall memories matching a query.

        Args:
            query: Search query
            memory_type: "short_term", "long_term", or "all"
            min_weight: Minimum weight threshold
            limit: Maximum results

        Returns:
            List of memory dicts
        """
        self._decay_all()  # Apply decay before recall

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        results = []

        # Search short-term
        if memory_type in ["short_term", "all"]:
            cursor.execute("""
                SELECT 'short_term' as source, id, content, weight, tags, created
                FROM short_term
                WHERE content LIKE ? AND weight >= ?
                ORDER BY weight DESC, created DESC
                LIMIT ?
            """, (f"%{query}%", min_weight, limit))
            results.extend(cursor.fetchall())

        # Search long-term
        if memory_type in ["long_term", "all"]:
            cursor.execute("""
                SELECT 'long_term' as source, id, content, weight, tags, created
                FROM long_term
                WHERE content LIKE ? AND weight >= ?
                ORDER BY weight DESC, created DESC
                LIMIT ?
            """, (f"%{query}%", min_weight, limit))
            results.extend(cursor.fetchall())

        conn.close()

        # Convert to dict
        return [dict(row) for row in results]

    def recall_by_tags(
        self,
        tags: List[str],
        memory_type: str = "all",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Recall memories by tags.

        Args:
            tags: List of tags to match
            memory_type: "short_term", "long_term", or "all"

        Returns:
            List of memory dicts
        """
        self._decay_all()

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        results = []
        tag_patterns = [f"%{tag}%" for tag in tags]

        for tag in tag_patterns:
            if memory_type in ["short_term", "all"]:
                cursor.execute("""
                    SELECT 'short_term' as source, id, content, weight, tags, created
                    FROM short_term
                    WHERE tags LIKE ?
                    ORDER BY weight DESC
                    LIMIT ?
                """, (tag, limit))
                results.extend(cursor.fetchall())

            if memory_type in ["long_term", "all"]:
                cursor.execute("""
                    SELECT 'long_term' as source, id, content, weight, tags, created
                    FROM long_term
                    WHERE tags LIKE ?
                    ORDER BY weight DESC
                    LIMIT ?
                """, (tag, limit))
                results.extend(cursor.fetchall())

        conn.close()
        return [dict(row) for row in results]

    def promote_to_long_term(self, memory_id: int, min_weight: float = 0.8) -> bool:
        """
        Promote a short-term memory to long-term.

        Args:
            memory_id: Short-term memory ID
            min_weight: Minimum weight for promotion

        Returns:
            True if promoted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get short-term memory
        cursor.execute("""
            SELECT id, content, weight, tags, created
            FROM short_term
            WHERE id = ?
        """, (memory_id,))
        memory = cursor.fetchone()

        if not memory:
            conn.close()
            return False

        if memory[2] < min_weight:
            conn.close()
            return False

        # Move to long-term
        cursor.execute("""
            INSERT INTO long_term (content, weight, tags, promoted_from, created)
            VALUES (?, ?, ?, ?, ?)
        """, (memory[1], memory[2], memory[3], memory_id, memory[4]))

        # Delete from short-term
        cursor.execute("DELETE FROM short_term WHERE id = ?", (memory_id,))

        conn.commit()
        conn.close()
        return True

    def _decay_all(self):
        """Apply Forge Theory decay to all memories."""
        # Decay short-term
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE short_term
            SET weight = weight * exp(-? * (julianday('now') - julianday(created)))
            WHERE weight > 0.01
        """, (self.decay_k,))

        # Decay long-term
        cursor.execute("""
            UPDATE long_term
            SET weight = weight * exp(-? * (julianday('now') - julianday(created)))
            WHERE weight > 0.01
        """, (self.decay_k,))

        # Archive very low weight memories
        cursor.execute("""
            DELETE FROM short_term
            WHERE weight < 0.01
        """)

        cursor.execute("""
            DELETE FROM long_term
            WHERE weight < 0.01
        """)

        conn.commit()
        conn.close()

    def consolidate(self):
        """
        Nightly consolidation — clusters patterns and stores insights.

        Finds recurring patterns in short-term memories and promotes
        them to long-term as insights.
        """
        self._decay_all()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get all short-term memories
        cursor.execute("""
            SELECT id, content, weight, tags
            FROM short_term
            ORDER BY weight DESC
        """)
        memories = cursor.fetchall()

        # Simple pattern detection
        pattern_count = {}
        for memory in memories:
            words = memory[1].split()
            for i in range(len(words) - 1):
                pair = f"{words[i]} {words[i+1]}"
                pattern_count[pair] = pattern_count.get(pair, 0) + 1

        # Promote frequent patterns
        for pattern, count in pattern_count.items():
            if count >= 3:
                cursor.execute("""
                    INSERT INTO long_term (content, weight, tags, promoted_from)
                    VALUES (?, ?, ?, ?)
                """, (
                    f"Pattern: {pattern} (appeared {count} times)",
                    min(1.0, 0.5 + count * 0.1),
                    json.dumps(["pattern", "consolidated"]),
                    None
                ))

        conn.commit()
        conn.close()

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM short_term")
        short_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM long_term")
        long_count = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(weight) FROM short_term")
        short_avg = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT AVG(weight) FROM long_term")
        long_avg = cursor.fetchone()[0] or 0.0

        conn.close()

        return {
            "short_term": {"count": short_count, "avg_weight": short_avg},
            "long_term": {"count": long_count, "avg_weight": long_avg},
            "decay_k": self.decay_k,
        }


# ============================================================
# CLI
# ============================================================

def main():
    """Test memory system."""
    import sys

    print("BuddAI — Memory System Test")
    print("=" * 60)

    memory = MemorySystem("test_memory.db", decay_k=0.01)

    # Store memories
    memory.remember("ESP32 uses ledcWrite for PWM", "correction", tags=["esp32", "pwm"])
    memory.remember("Use exponential smoothing for fluid movement", "pattern", tags=["movement", "smoothing"])
    memory.remember("L298N motor driver needs enable pins", "fact", tags=["motor", "l298n"])

    print("✅ Stored 3 memories")

    # Recall
    results = memory.recall("esp32")
    print(f"\nRecall 'esp32': {len(results)} results")
    for r in results:
        print(f"  - {r['content']} (weight: {r['weight']:.2f})")

    # Stats
    stats = memory.get_stats()
    print(f"\nStats: {stats}")


if __name__ == "__main__":
    main()
