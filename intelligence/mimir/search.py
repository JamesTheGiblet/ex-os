#!/usr/bin/env python3
"""
Mimir — Semantic Search

Search over SCP capsules using keyword matching and λ scoring.

Usage:
    from intelligence.mimir.search import MimirSearch

    searcher = MimirSearch("capsules/")
    results = searcher.search("authentication")
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import re


class MimirSearch:
    """
    Mimir search engine — searches capsules by keyword, relevance, and λ.
    """

    def __init__(self, capsule_dir: str = "capsules"):
        """
        Initialise search engine.

        Args:
            capsule_dir: Directory containing capsules
        """
        self.capsule_dir = Path(capsule_dir)
        self.capsules = []
        self._load_capsules()

    def _load_capsules(self):
        """Load all capsules from directory."""
        if not self.capsule_dir.exists():
            return

        for file_path in self.capsule_dir.rglob("*.scp.json"):
            try:
                with open(file_path, "r") as f:
                    capsule = json.load(f)
                    capsule["_file"] = str(file_path)
                    self.capsules.append(capsule)
            except (json.JSONDecodeError, OSError):
                continue

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search capsules by query.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching capsules with scores
        """
        query_words = set(query.lower().split())
        results = []

        for capsule in self.capsules:
            score = self._score_capsule(capsule, query_words)

            if score > 0:
                capsule["_score"] = score
                results.append(capsule)

        # Sort by score descending
        results.sort(key=lambda x: x.get("_score", 0), reverse=True)

        # Limit and clean
        results = results[:limit]
        for r in results:
            r["_score"] = round(r["_score"], 3)

        return results

    def _score_capsule(self, capsule: Dict, query_words: set) -> float:
        """Score a capsule against query words."""
        score = 0.0

        # Score intent
        intent = capsule.get("intent", "").lower()
        intent_words = set(intent.split())
        match = len(query_words & intent_words)
        if match > 0:
            score += min(match * 0.3, 1.0)

        # Score content
        content = capsule.get("content", {})
        if isinstance(content, dict):
            text = " ".join(str(v) for v in content.values())
        elif isinstance(content, str):
            text = content
        else:
            text = ""

        text_words = set(text.lower().split())
        match = len(query_words & text_words)
        if match > 0:
            score += min(match * 0.2, 0.8)

        # Score scp_id
        scp_id = capsule.get("scp_id", "").lower()
        id_words = set(scp_id.replace("/", ".").replace("_", ".").split("."))
        match = len(query_words & id_words)
        if match > 0:
            score += min(match * 0.5, 1.0)

        # Boost by λ
        λ = capsule.get("_trust", 1.0)
        if λ >= 1.5:
            score *= 1.5
        elif λ >= 1.0:
            score *= 1.2
        elif λ < 0.6:
            score *= 0.5

        return score

    def search_by_tag(self, tag: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search capsules by tag."""
        results = []

        for capsule in self.capsules:
            content = capsule.get("content", {})
            if isinstance(content, dict):
                tags = content.get("tags", [])
                if isinstance(tags, list):
                    if tag in tags:
                        capsule["_score"] = 1.0
                        results.append(capsule)

        results.sort(key=lambda x: x.get("_trust", 1.0), reverse=True)
        return results[:limit]

    def get_stats(self) -> Dict[str, Any]:
        """Get search statistics."""
        return {
            "total_capsules": len(self.capsules),
            "avg_λ": sum(c.get("_trust", 1.0) for c in self.capsules) / len(self.capsules) if self.capsules else 0,
        }


def semantic_search(query: str, capsule_dir: str = "capsules", limit: int = 10) -> List[Dict[str, Any]]:
    """Convenience function for semantic search."""
    searcher = MimirSearch(capsule_dir)
    return searcher.search(query, limit)


# ============================================================
# CLI
# ============================================================

def main():
    """Test search."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Mimir — Semantic Search")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--capsules", "-c", type=str, default="capsules", help="Capsule directory")
    parser.add_argument("--limit", "-l", type=int, default=10, help="Max results")

    args = parser.parse_args()

    print(f"🔍 Mimir — Semantic Search")
    print(f"   Query: {args.query}")
    print("=" * 60)

    results = semantic_search(args.query, args.capsules, args.limit)

    if not results:
        print("No results found.")
        return

    print(f"\n📊 Found {len(results)} results:")
    for i, r in enumerate(results, 1):
        print(f"\n{i}. {r.get('scp_id', 'unknown')} (score: {r.get('_score', 0):.2f})")
        print(f"   Intent: {r.get('intent', 'No description')}")
        print(f"   λ: {r.get('_trust', 1.0):.2f}")


if __name__ == "__main__":
    main()