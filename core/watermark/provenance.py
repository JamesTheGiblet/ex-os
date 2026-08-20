#!/usr/bin/env python3
"""
Watermark — Provenance

Tracks provenance for all outputs.

Features:
- Track source, trust, capsule
- Chain of custody
- Audit trail

Usage:
    from core.watermark.provenance import ProvenanceTracker

    tracker = ProvenanceTracker()
    tracker.track(source="mimir", trust=0.92, capsule_id="mimir/binding-v1")
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime


class ProvenanceTracker:
    """
    Provenance tracker — tracks provenance for all outputs.
    """

    def __init__(self, store_dir: str = "provenance"):
        """
        Initialise the provenance tracker.

        Args:
            store_dir: Directory to store provenance records
        """
        import os
        self.store_dir = store_dir
        os.makedirs(self.store_dir, exist_ok=True)

    def track(
        self,
        source: str,
        trust_score: float,
        capsule_id: Optional[str] = None,
        model: Optional[str] = None,
        input_hash: Optional[str] = None,
        output_hash: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> str:
        """
        Track provenance for an output.

        Args:
            source: Source of the output
            trust_score: Trust score (λ)
            capsule_id: SCP capsule ID
            model: Model name
            input_hash: Input hash (for traceability)
            output_hash: Output hash
            metadata: Additional metadata

        Returns:
            Provenance ID
        """
        # Generate IDs
        timestamp = datetime.utcnow().isoformat() + "Z"
        provenance_id = self._generate_id(source, timestamp)

        # Create provenance record
        record = {
            "provenance_id": provenance_id,
            "source": source,
            "trust_score": trust_score,
            "capsule_id": capsule_id,
            "model": model,
            "input_hash": input_hash,
            "output_hash": output_hash,
            "metadata": metadata or {},
            "timestamp": timestamp,
            "version": "1.0",
        }

        # Store record
        self._store_record(record)

        return provenance_id

    def _generate_id(self, source: str, timestamp: str) -> str:
        """Generate a unique provenance ID."""
        data = f"{source}:{timestamp}"
        return f"prov-{hashlib.sha256(data.encode()).hexdigest()[:16]}"

    def _store_record(self, record: Dict[str, Any]):
        """Store a provenance record."""
        import os
        file_path = os.path.join(self.store_dir, f"{record['provenance_id']}.json")
        with open(file_path, "w") as f:
            json.dump(record, f, indent=2)

    def get_record(self, provenance_id: str) -> Optional[Dict[str, Any]]:
        """Get a provenance record by ID."""
        import os
        file_path = os.path.join(self.store_dir, f"{provenance_id}.json")
        if not os.path.exists(file_path):
            return None

        with open(file_path, "r") as f:
            return json.load(f)

    def get_chain(self, provenance_id: str) -> List[Dict[str, Any]]:
        """
        Get the full chain of custody.

        Traces input_hash -> output_hash relationships.
        """
        chain = []
        current_id = provenance_id

        while current_id:
            record = self.get_record(current_id)
            if not record:
                break

            chain.append(record)

            # Move to previous in chain
            if record.get("metadata", {}).get("parent_provenance_id"):
                current_id = record["metadata"]["parent_provenance_id"]
            else:
                break

        return chain

    def list_records(self, limit: int = 20) -> List[Dict[str, Any]]:
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

        results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return results[:limit]


def track_provenance(
    source: str,
    trust_score: float,
    capsule_id: Optional[str] = None,
    store_dir: str = "provenance",
) -> str:
    """
    Convenience function to track provenance.

    Args:
        source: Source of the output
        trust_score: Trust score (λ)
        capsule_id: SCP capsule ID
        store_dir: Store directory

    Returns:
        Provenance ID
    """
    tracker = ProvenanceTracker(store_dir)
    return tracker.track(source, trust_score, capsule_id)


# ============================================================
# CLI
# ============================================================

def main():
    """Test provenance."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Watermark — Provenance")
    parser.add_argument("--source", "-s", type=str, required=True, help="Source")
    parser.add_argument("--trust", "-t", type=float, default=0.90, help="Trust score")
    parser.add_argument("--capsule", "-c", type=str, help="Capsule ID")
    parser.add_argument("--list", "-l", action="store_true", help="List records")
    parser.add_argument("--get", "-g", type=str, help="Get record by ID")
    parser.add_argument("--chain", "-C", type=str, help="Get chain by ID")

    args = parser.parse_args()

    tracker = ProvenanceTracker()

    if args.list:
        records = tracker.list_records()
        print(f"📋 Provenance Records ({len(records)})")
        print("=" * 60)
        for r in records:
            print(f"  {r.get('provenance_id')} — {r.get('source')} (λ: {r.get('trust_score', 0):.2f})")
            print(f"    {r.get('timestamp', 'unknown')}")
        return

    if args.get:
        record = tracker.get_record(args.get)
        if record:
            print(f"📋 Record: {args.get}")
            print("=" * 60)
            print(json.dumps(record, indent=2))
        else:
            print(f"❌ Record not found: {args.get}")
            sys.exit(1)
        return

    if args.chain:
        chain = tracker.get_chain(args.chain)
        print(f"📋 Chain: {args.chain}")
        print("=" * 60)
        for i, r in enumerate(chain):
            print(f"\n{i+1}. {r.get('provenance_id')}")
            print(f"   Source: {r.get('source')}")
            print(f"   Trust: {r.get('trust_score', 0):.2f}")
        return

    provenance_id = tracker.track(
        source=args.source,
        trust_score=args.trust,
        capsule_id=args.capsule,
    )

    print(f"✅ Provenance tracked: {provenance_id}")


if __name__ == "__main__":
    main()