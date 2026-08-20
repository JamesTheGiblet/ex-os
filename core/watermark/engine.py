#!/usr/bin/env python3
"""
Watermark — Engine

Creates and embeds watermarks in content.

Features:
- Cryptographic watermarking
- Provenance tracking
- Trust score embedding
- ChronoSCRIBE integration

Usage:
    from core.watermark.engine import WatermarkEngine

    engine = WatermarkEngine()
    result = engine.watermark(
        content="Response text",
        source="mimir",
        trust_score=0.92,
        capsule_id="mimir/binding-v1"
    )
    print(result["watermarked"])
    print(result["provenance_id"])
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime


class WatermarkEngine:
    """
    Watermark engine — creates and embeds watermarks.
    """

    def __init__(self, store_dir: str = "watermarks"):
        """
        Initialise the watermark engine.

        Args:
            store_dir: Directory to store watermarks
        """
        import os
        self.store_dir = store_dir
        os.makedirs(self.store_dir, exist_ok=True)

    def watermark(
        self,
        content: str,
        source: str,
        trust_score: float,
        capsule_id: Optional[str] = None,
        model: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Watermark content with provenance.

        Args:
            content: Content to watermark
            source: Source of the content (e.g., "mimir", "buddai")
            trust_score: Trust score (λ) of the source
            capsule_id: SCP capsule ID
            model: Model name
            metadata: Additional metadata

        Returns:
            Dict with watermarked content and provenance
        """
        # Generate content hash
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        # Create provenance
        provenance = {
            "provenance_id": self._generate_id(content_hash),
            "content_hash": content_hash,
            "source": source,
            "trust_score": trust_score,
            "capsule_id": capsule_id,
            "model": model,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "watermark_version": "1.0",
        }

        # Store provenance
        self._store_provenance(provenance)

        # Embed watermark in content
        watermarked = self._embed_watermark(content, provenance["provenance_id"])

        return {
            "provenance_id": provenance["provenance_id"],
            "content": watermarked,
            "content_hash": content_hash,
            "provenance": provenance,
            "stored": True,
        }

    def _generate_id(self, content_hash: str) -> str:
        """Generate a unique provenance ID."""
        timestamp = datetime.utcnow().isoformat()
        data = f"{content_hash}:{timestamp}"
        return f"wm-{hashlib.sha256(data.encode()).hexdigest()[:16]}"

    def _store_provenance(self, provenance: Dict[str, Any]):
        """Store provenance in the store directory."""
        import os
        file_path = os.path.join(self.store_dir, f"{provenance['provenance_id']}.json")
        with open(file_path, "w") as f:
            json.dump(provenance, f, indent=2)

    def _embed_watermark(self, content: str, provenance_id: str) -> str:
        """Embed watermark in content."""
        # Add watermark as metadata comment
        watermark = f"\n\n<!-- Ex-OS Watermark: {provenance_id} -->"
        return content + watermark

    def get_provenance(self, provenance_id: str) -> Optional[Dict[str, Any]]:
        """Get provenance by ID."""
        import os
        file_path = os.path.join(self.store_dir, f"{provenance_id}.json")
        if not os.path.exists(file_path):
            return None

        with open(file_path, "r") as f:
            return json.load(f)

    def list_provenance(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List recent provenance records."""
        import os
        import glob

        results = []
        for file_path in glob.glob(os.path.join(self.store_dir, "*.json")):
            try:
                with open(file_path, "r") as f:
                    results.append(json.load(f))
            except (json.JSONDecodeError, OSError):
                continue

        # Sort by timestamp descending
        results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return results[:limit]


def create_watermark(
    content: str,
    source: str,
    trust_score: float,
    capsule_id: Optional[str] = None,
    store_dir: str = "watermarks",
) -> Dict[str, Any]:
    """
    Convenience function to create a watermark.

    Args:
        content: Content to watermark
        source: Source of the content
        trust_score: Trust score (λ)
        capsule_id: SCP capsule ID
        store_dir: Store directory

    Returns:
        Watermarked result
    """
    engine = WatermarkEngine(store_dir)
    return engine.watermark(content, source, trust_score, capsule_id)


def watermark_content(
    content: str,
    source: str,
    trust_score: float,
    capsule_id: Optional[str] = None,
    store_dir: str = "watermarks",
) -> str:
    """
    Convenience function to watermark content.

    Args:
        content: Content to watermark
        source: Source of the content
        trust_score: Trust score (λ)
        capsule_id: SCP capsule ID
        store_dir: Store directory

    Returns:
        Watermarked content
    """
    result = create_watermark(content, source, trust_score, capsule_id, store_dir)
    return result["content"]


# ============================================================
# CLI
# ============================================================

def main():
    """Test watermark engine."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Watermark — Engine")
    parser.add_argument("--content", "-c", type=str, required=True, help="Content to watermark")
    parser.add_argument("--source", "-s", type=str, default="system", help="Source")
    parser.add_argument("--trust", "-t", type=float, default=0.90, help="Trust score")
    parser.add_argument("--capsule", "-C", type=str, help="Capsule ID")
    parser.add_argument("--list", "-l", action="store_true", help="List watermarks")

    args = parser.parse_args()

    engine = WatermarkEngine()

    if args.list:
        watermarks = engine.list_provenance()
        print(f"📋 Watermarks ({len(watermarks)})")
        print("=" * 60)
        for w in watermarks:
            print(f"  {w.get('provenance_id')} — {w.get('source')} (λ: {w.get('trust_score', 0):.2f})")
            print(f"    {w.get('timestamp', 'unknown')}")
        return

    result = engine.watermark(
        content=args.content,
        source=args.source,
        trust_score=args.trust,
        capsule_id=args.capsule,
    )

    print(f"✅ Watermark created")
    print(f"   ID: {result['provenance_id']}")
    print(f"   Hash: {result['content_hash'][:16]}...")
    print(f"\n📝 Watermarked Content:")
    print("=" * 60)
    print(result["content"])


if __name__ == "__main__":
    main()