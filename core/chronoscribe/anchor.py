#!/usr/bin/env python3
"""
ChronoSCRIBE — Anchor

Root anchoring for ChronoSCRIBE.

Every consumer ledger starts with event.ledger.anchor.root —
cryptographically anchoring it to the root chain's head.

Usage:
    from core.chronoscribe.anchor import anchor_root, get_root_anchor
"""

import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from .ledger import Ledger


ROOT_CONSUMER = "root"


def anchor_root(
    consumer: str,
    root_ledger: Optional[Ledger] = None,
    base_dir: str = "ledger",
) -> Dict[str, Any]:
    """
    Anchor a consumer ledger to the root chain.

    Args:
        consumer: Consumer name
        root_ledger: Root ledger instance (creates if None)
        base_dir: Base directory for ledgers

    Returns:
        The anchor entry
    """
    # Get or create root ledger
    if root_ledger is None:
        root_ledger = Ledger(ROOT_CONSUMER, base_dir)

    # Get consumer ledger
    consumer_ledger = Ledger(consumer, base_dir)

    # Get consumer head
    consumer_head = consumer_ledger._get_last_entry_id()

    # Create anchor event
    anchor_entry = root_ledger.append({
        "event": "event.ledger.anchor.root",
        "source": "chronoscribe",
        "payload": {
            "consumer": consumer,
            "consumer_head": consumer_head,
            "consumer_entries": consumer_ledger.get_stats().get("entries", 0),
        }
    })

    # Store anchor in consumer meta
    consumer_ledger._set_root_anchor(anchor_entry["entry_id"])

    return anchor_entry


def get_root_anchor(consumer: str, base_dir: str = "ledger") -> Optional[str]:
    """
    Get the root anchor for a consumer.

    Args:
        consumer: Consumer name
        base_dir: Base directory for ledgers

    Returns:
        Root anchor entry ID or None
    """
    ledger = Ledger(consumer, base_dir)
    return ledger.get_root_anchor()


def verify_anchor(consumer: str, base_dir: str = "ledger") -> bool:
    """
    Verify that a consumer is properly anchored.

    Args:
        consumer: Consumer name
        base_dir: Base directory for ledgers

    Returns:
        True if anchored and verified
    """
    ledger = Ledger(consumer, base_dir)
    root_anchor = ledger.get_root_anchor()

    if not root_anchor:
        return False

    # Check that the anchor entry exists in root ledger
    root_ledger = Ledger(ROOT_CONSUMER, base_dir)
    entry = root_ledger.get_entry(root_anchor)

    if not entry:
        return False

    # Verify the payload matches
    payload = entry.get("payload", {})
    if payload.get("consumer") != consumer:
        return False

    return True


def list_anchored_consumers(base_dir: str = "ledger") -> list:
    """
    List all anchored consumers.

    Args:
        base_dir: Base directory for ledgers

    Returns:
        List of consumer names
    """
    root_ledger = Ledger(ROOT_CONSUMER, base_dir)
    entries = root_ledger.get_entries(limit=1000)

    consumers = []
    for entry in entries:
        if entry.get("event") == "event.ledger.anchor.root":
            payload = entry.get("payload", {})
            consumer = payload.get("consumer")
            if consumer:
                consumers.append(consumer)

    return consumers


# ============================================================
# CLI
# ============================================================

def main():
    """Test anchoring."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="ChronoSCRIBE — Anchor")
    parser.add_argument("--consumer", "-c", type=str, required=True, help="Consumer name")
    parser.add_argument("--anchor", "-a", action="store_true", help="Anchor consumer")
    parser.add_argument("--verify", "-v", action="store_true", help="Verify anchor")
    parser.add_argument("--list", "-l", action="store_true", help="List anchored consumers")

    args = parser.parse_args()

    if args.anchor:
        print(f"🔗 Anchoring: {args.consumer}")
        entry = anchor_root(args.consumer)
        print(f"✅ Anchored: {entry['entry_id']}")
        print(f"   Consumer: {args.consumer}")
        print(f"   Root entry: {entry['entry_id']}")

    elif args.verify:
        print(f"🔍 Verifying: {args.consumer}")
        if verify_anchor(args.consumer):
            print(f"✅ Verified: {args.consumer} is anchored")
            print(f"   Root anchor: {get_root_anchor(args.consumer)}")
        else:
            print(f"❌ Not anchored or invalid: {args.consumer}")
            sys.exit(1)

    elif args.list:
        consumers = list_anchored_consumers()
        print(f"📋 Anchored consumers ({len(consumers)}):")
        for c in consumers:
            print(f"  - {c}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()