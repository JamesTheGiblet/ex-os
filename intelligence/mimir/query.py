#!/usr/bin/env python3
"""
Mimir — Query Engine

Mimir answers questions about your codebase using SCP capsules.
Queries are scored against all capsules to find the most relevant context.
Responses are generated with full provenance.

Pipeline:
    Query → Score Capsules → Build Context → Generate Response → Watermark

Usage:
    from intelligence.mimir.query import MimirQuery

    engine = MimirQuery(repo_path="/path/to/repo")
    result = engine.query("how does authentication work")
    print(result["answer"])
    print(result["provenance"])
"""

import json
import os
import re
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from datetime import datetime


class MimirQuery:
    """
    Mimir query engine.

    Searches SCP capsules, scores them by relevance and trust (λ),
    and generates answers with full provenance.
    """

    def __init__(
        self,
        repo_path: str,
        binding_capsule: Optional[Dict] = None,
        max_results: int = 5,
    ):
        """
        Initialise query engine.

        Args:
            repo_path: Path to repository with capsules
            binding_capsule: Mimir binding capsule (loads default if None)
            max_results: Maximum sources to include
        """
        self.repo_path = Path(repo_path)
        self.max_results = max_results
        self.capsules = []
        self._load_capsules()

        # Load binding
        if binding_capsule:
            from intelligence.mimir.binding import MimirBinding
            if isinstance(binding_capsule, dict):
                self.binding = MimirBinding(binding_capsule)
            else:
                self.binding = binding_capsule
        else:
            from intelligence.mimir.binding import MimirBinding
            self.binding = MimirBinding.load_default()

    def _load_capsules(self):
        """Load all SCP capsules from the repository."""
        self.capsules = []

        if not self.repo_path.exists():
            return

        # Find all .scp.json files
        scp_files = list(self.repo_path.rglob("*.scp.json"))

        for file_path in scp_files:
            try:
                with open(file_path, "r") as f:
                    capsule = json.load(f)
                    capsule["_file"] = str(file_path)
                    self.capsules.append(capsule)
            except (json.JSONDecodeError, OSError):
                continue

    def query(self, query: str) -> Dict[str, Any]:
        """
        Answer a question about the codebase.

        Args:
            query: User question

        Returns:
            Dict with answer, sources, and provenance
        """
        # Score capsules by relevance
        scored = self._score_capsules(query)

        # Filter by trust threshold
        min_trust = self.binding.get_min_trust()
        filtered = [
            c for c in scored
            if c.get("_trust", 1.0) >= min_trust
        ]

        # Get top results
        top_results = filtered[:self.max_results]

        # Build context
        context = self._build_context(top_results, query)

        # Generate response
        response = self._generate_response(query, context, top_results)

        return response

    def _score_capsules(self, query: str) -> List[Dict]:
        """
        Score capsules by relevance to query.

        Scoring considers:
        - Keyword matches in content
        - Keyword matches in intent
        - λ (Leighton Weight) trust score
        """
        scored = []
        query_words = set(query.lower().split())

        for capsule in self.capsules:
            score = 0.0

            # Score intent
            intent = capsule.get("intent", "").lower()
            intent_words = set(intent.split())
            match = len(query_words & intent_words)
            if match > 0:
                score += min(match * 0.2, 1.0)

            # Score content (if available)
            content = capsule.get("content", {})
            if isinstance(content, dict):
                text = " ".join(str(v) for v in content.values())
            elif isinstance(content, str):
                text = content
            else:
                text = ""

            # Simple keyword scoring
            text_words = set(text.lower().split())
            match = len(query_words & text_words)
            if match > 0:
                score += min(match * 0.1, 0.5)

            # Score by λ (trust)
            λ = capsule.get("_trust", 1.0)
            if λ >= 1.5:
                score += 0.5
            elif λ >= 1.0:
                score += 0.3
            elif λ >= 0.6:
                score += 0.1

            # Penalise quarantined
            if λ < 0.6:
                score = -1.0

            capsule["_score"] = score
            capsule["_trust"] = λ
            scored.append(capsule)

        # Sort by score descending
        scored.sort(key=lambda x: x.get("_score", 0.0), reverse=True)
        return scored

    def _build_context(self, capsules: List[Dict], query: str) -> str:
        """
        Build context string from top capsules.
        """
        if not capsules:
            return "No relevant capsules found."

        context_lines = []
        for i, capsule in enumerate(capsules, 1):
            scp_id = capsule.get("scp_id", "unknown")
            intent = capsule.get("intent", "No description")
            λ = capsule.get("_trust", 1.0)
            file_path = capsule.get("_file", "unknown")

            context_lines.append(f"[{i}] {scp_id} (λ: {λ:.2f})")
            context_lines.append(f"    Intent: {intent}")
            context_lines.append(f"    Source: {file_path}")

            # Add content if available
            content = capsule.get("content")
            if isinstance(content, dict):
                summary = " ".join(str(v) for v in content.values())[:200]
                context_lines.append(f"    Content: {summary}...")
            elif isinstance(content, str):
                context_lines.append(f"    Content: {content[:200]}...")

        return "\n".join(context_lines)

    def _generate_response(
        self,
        query: str,
        context: str,
        sources: List[Dict]
    ) -> Dict[str, Any]:
        """
        Generate response using LLM with context.
        """
        from intelligence.mimir.watermark_llm import MimirLLM

        # Try to use LLM
        try:
            llm = MimirLLM(binding_capsule=self.binding.to_dict())
            result = llm.generate(
                prompt=query,
                context=sources,
                max_tokens=500,
            )
            answer = result["text"]
            provenance = result["provenance"]

        except ImportError:
            # Fallback: no LLM available
            answer = self._fallback_response(query, context, sources)
            provenance = {
                "scp_id": self.binding.get_scp_id(),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "sources": sources,
                "model": "fallback",
                "watermarked": False,
                "watermark_version": "1.0",
            }

        # Add sources to response
        return {
            "answer": answer,
            "query": query,
            "sources": [
                {
                    "file": s.get("_file", "unknown"),
                    "scp_id": s.get("scp_id", "unknown"),
                    "trust": s.get("_trust", 1.0),
                    "score": s.get("_score", 0.0),
                }
                for s in sources
            ],
            "provenance": provenance,
            "binding": self.binding.get_scp_id(),
            "min_trust": self.binding.get_min_trust(),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    def _fallback_response(self, query: str, context: str, sources: List[Dict]) -> str:
        """
        Generate a fallback response without LLM.

        Uses the first source's content to answer.
        """
        if not sources:
            return "I couldn't find any relevant capsules for your query."

        # Use the top source
        top = sources[0]
        scp_id = top.get("scp_id", "unknown")
        intent = top.get("intent", "No description")

        return (
            f"Based on capsule '{scp_id}':\n"
            f"{intent}\n\n"
            f"This answer is sourced from {scp_id} (λ: {top.get('_trust', 1.0):.2f})."
        )


def search_capsules(repo_path: str, query: str, max_results: int = 5) -> List[Dict]:
    """
    Quick search function for capsules.

    Args:
        repo_path: Path to repository
        query: Search query
        max_results: Maximum results

    Returns:
        List of relevant capsules with scores
    """
    engine = MimirQuery(repo_path, max_results=max_results)
    result = engine.query(query)
    return result.get("sources", [])


# ============================================================
# CLI
# ============================================================

def main():
    """Test query engine."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Mimir — Query Engine")
    parser.add_argument("query", type=str, nargs="?", help="Question to ask")
    parser.add_argument("--repo", "-r", type=str, default=".", help="Repository path")
    parser.add_argument("--max", "-m", type=int, default=5, help="Max sources")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show full output")

    args = parser.parse_args()

    if not args.query:
        args.query = input("Enter your question: ")

    print(f"🔍 Searching in: {args.repo}")
    print(f"❓ Query: {args.query}")
    print("")

    engine = MimirQuery(args.repo, max_results=args.max)
    result = engine.query(args.query)

    print("=" * 60)
    print("ANSWER:")
    print("=" * 60)
    print(result["answer"])

    print("\n" + "=" * 60)
    print("SOURCES:")
    print("=" * 60)
    for source in result["sources"]:
        trust_emoji = "⭐" if source["trust"] >= 1.5 else "✅" if source["trust"] >= 1.0 else "⚠️"
        print(f"  {trust_emoji} {source['scp_id']} (λ: {source['trust']:.2f})")
        print(f"     {source['file']}")

    if args.verbose:
        print("\n" + "=" * 60)
        print("PROVENANCE:")
        print("=" * 60)
        print(json.dumps(result["provenance"], indent=2))


if __name__ == "__main__":
    main()