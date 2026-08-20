#!/usr/bin/env python3
"""
ChronoSCRIBE — Verification

Verifies ledger integrity, chain consistency, and entries.

Usage:
    from core.chronoscribe.verify import verify_chain, verify_entry
"""

import json
import hashlib
from typing import Tuple, List, Dict, Any, Optional
from pathlib import Path

from .ledger import Ledger


def verify_entry(entry: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Verify a single ledger entry.

    Args:
        entry: Entry dict

    Returns:
        (valid, message)
    """
    # Check required fields
    required = ["entry_id", "previous", "event", "source", "ts"]
    for field in required:
        if field not in entry:
            return False, f"Missing required field: {field}"

    # Check entry_id format
    entry_id = entry.get("entry_id", "")
    if not entry_id.startswith("sha256:"):
        return False, f"Invalid entry_id format: {entry_id}"

    # Check timestamp format
    ts = entry.get("ts", "")
    if not ts.endswith("Z"):
        return False, f"Invalid timestamp format: {ts}"

    # Check payload
    if "payload" not in entry:
        return False, "Missing payload"

    return True, "Entry valid"


def verify_chain(consumer: str, base_dir: str = "ledger") -> Tuple[bool, List[str]]:
    """
    Verify the entire chain for a consumer.

    Args:
        consumer: Consumer name
        base_dir: Base directory for ledgers

    Returns:
        (valid, errors)
    """
    ledger = Ledger(consumer, base_dir)
    return ledger.verify()


def verify_ledger(consumer: str, base_dir: str = "ledger") -> Tuple[bool, List[str]]:
    """
    Verify ledger integrity.

    Args:
        consumer: Consumer name
        base_dir: Base directory for ledgers

    Returns:
        (valid, errors)
    """
    return verify_chain(consumer, base_dir)


def verify_integrity(consumer: str, base_dir: str = "ledger") -> Dict[str, Any]:
    """
    Comprehensive integrity check.

    Args:
        consumer: Consumer name
        base_dir: Base directory for ledgers

    Returns:
        Integrity report
    """
    ledger = Ledger(consumer, base_dir)
    chain_valid, chain_errors = ledger.verify()

    root_anchor = ledger.get_root_anchor()
    entries = ledger.get_entries(limit=1)

    return {
        "consumer": consumer,
        "chain_valid": chain_valid,
        "chain_errors": chain_errors,
        "root_anchor": root_anchor,
        "entries": ledger.get_stats().get("entries", 0),
        "integrity": "verified" if chain_valid else "corrupted",
    }


def get_entry_hash(entry: Dict[str, Any]) -> str:
    """Calculate the expected hash of an entry."""
    # Remove entry_id and calculate hash
    test_entry = entry.copy()
    test_entry.pop("entry_id", None)

    # Deterministic JSON
    data = json.dumps(test_entry, sort_keys=True)
    return f"sha256:{hashlib.sha256(data.encode()).hexdigest()}"


# ============================================================
# CLI
# ============================================================

def main():
    """Test verification."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="ChronoSCRIBE — Verify")
    parser.add_argument("--consumer", "-c", type=str, required=True, help="Consumer name")
    parser.add_argument("--entry", "-e", type=str, help="Entry ID to verify")
    parser.add_argument("--full", "-f", action="store_true", help="Full chain verification")

    args = parser.parse_args()

    if args.entry:
        ledger = Ledger(args.consumer)
        entry = ledger.get_entry(args.entry)

        if not entry:
            print(f"❌ Entry not found: {args.entry}")
            sys.exit(1)

        valid, message = verify_entry(entry)
        if valid:
            print(f"✅ Entry verified: {args.entry}")
            print(f"   Event: {entry.get('event', 'unknown')}")
            print(f"   Source: {entry.get('source', 'unknown')}")
        else:
            print(f"❌ Invalid entry: {message}")
            sys.exit(1)

    elif args.full:
        valid, errors = verify_chain(args.consumer)

        print(f"🔍 Verifying: {args.consumer}")
        print("=" * 60)

        if valid:
            print("✅ Chain verified")
        else:
            print("❌ Chain errors:")
            for error in errors:
                print(f"   - {error}")
            sys.exit(1)

    else:
        # Quick check
        ledger = Ledger(args.consumer)
        stats = ledger.get_stats()
        valid, errors = verify_chain(args.consumer)

        print(f"🔍 Quick check: {args.consumer}")
        print("=" * 60)
        print(f"   Entries: {stats.get('entries', 0)}")
        print(f"   Root anchor: {stats.get('root_anchor', 'None')}")
        print(f"   Integrity: {'✅ verified' if valid else '❌ corrupted'}")


if __name__ == "__main__":
    main()