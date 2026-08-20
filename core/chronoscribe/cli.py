#!/usr/bin/env python3
"""
ChronoSCRIBE — CLI

Command-line interface for ChronoSCRIBE.

Usage:
    chronoscribe append --consumer LifeForge --event event.capsule.signed --source sign
    chronoscribe list --consumer LifeForge --limit 10
    chronoscribe stats --consumer LifeForge
    chronoscribe anchor --consumer LifeForge
    chronoscribe verify --consumer LifeForge
"""

import sys
import json
import argparse
from pathlib import Path


def append_command(consumer: str, event: str, source: str, payload: str):
    """Append an entry."""
    try:
        from .ledger import append_entry

        try:
            payload_data = json.loads(payload) if payload else {}
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON payload")
            sys.exit(1)

        entry = append_entry(consumer, event, source, payload_data)

        print(f"✅ Appended: {entry['entry_id']}")
        print(f"   Event: {entry['event']}")
        print(f"   Source: {entry['source']}")
        print(f"   Timestamp: {entry['ts']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def list_command(consumer: str, limit: int, offset: int, verbose: bool):
    """List entries."""
    try:
        from .ledger import get_entries

        entries = get_entries(consumer, limit, offset)

        print(f"📋 Ledger: {consumer} (showing {len(entries)} entries)")
        print("=" * 60)

        for entry in entries:
            print(f"\n🔗 {entry.get('entry_id', 'unknown')}")
            print(f"   Event: {entry.get('event', 'unknown')}")
            print(f"   Source: {entry.get('source', 'unknown')}")
            print(f"   Time: {entry.get('ts', 'unknown')}")

            if verbose and entry.get('payload'):
                print(f"   Payload: {json.dumps(entry['payload'], indent=2)}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def stats_command(consumer: str):
    """Show ledger statistics."""
    try:
        from .ledger import Ledger

        ledger = Ledger(consumer)
        stats = ledger.get_stats()

        print(f"📊 ChronoSCRIBE — {consumer}")
        print("=" * 60)
        for key, value in stats.items():
            print(f"  {key}: {value}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def anchor_command(consumer: str):
    """Anchor a consumer to the root chain."""
    try:
        from .anchor import anchor_root, get_root_anchor, verify_anchor

        # Check if already anchored
        if verify_anchor(consumer):
            print(f"ℹ️  {consumer} already anchored")
            print(f"   Root anchor: {get_root_anchor(consumer)}")
            return

        print(f"🔗 Anchoring: {consumer}")
        entry = anchor_root(consumer)

        print(f"✅ Anchored!")
        print(f"   Anchor ID: {entry['entry_id']}")
        print(f"   Consumer: {consumer}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def verify_command(consumer: str):
    """Verify a ledger."""
    try:
        from .verify import verify_chain
        from .anchor import verify_anchor

        # Check anchor
        anchored = verify_anchor(consumer)
        print(f"🔍 Verifying: {consumer}")
        print("=" * 60)
        print(f"   Anchored: {'✅' if anchored else '❌'}")

        # Check chain
        valid, errors = verify_chain(consumer)

        if valid:
            print("   Chain: ✅ valid")
        else:
            print("   Chain: ❌ errors")
            for error in errors[:5]:
                print(f"      - {error}")

        if not anchored or not valid:
            print("\n⚠️  Integrity check failed")
            sys.exit(1)

        print("\n✅ Ledger integrity verified")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ChronoSCRIBE — Immutable Ledger",
        prog="chronoscribe"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Append command
    append_parser = subparsers.add_parser("append", help="Append an entry")
    append_parser.add_argument("--consumer", "-c", type=str, required=True, help="Consumer name")
    append_parser.add_argument("--event", "-e", type=str, required=True, help="Event name")
    append_parser.add_argument("--source", "-s", type=str, required=True, help="Event source")
    append_parser.add_argument("--payload", "-p", type=str, default="{}", help="Event payload (JSON)")

    # List command
    list_parser = subparsers.add_parser("list", help="List entries")
    list_parser.add_argument("--consumer", "-c", type=str, required=True, help="Consumer name")
    list_parser.add_argument("--limit", "-l", type=int, default=10, help="Max entries")
    list_parser.add_argument("--offset", "-o", type=int, default=0, help="Offset from end")
    list_parser.add_argument("--verbose", "-v", action="store_true", help="Show payloads")

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show ledger statistics")
    stats_parser.add_argument("--consumer", "-c", type=str, required=True, help="Consumer name")

    # Anchor command
    anchor_parser = subparsers.add_parser("anchor", help="Anchor consumer to root chain")
    anchor_parser.add_argument("--consumer", "-c", type=str, required=True, help="Consumer name")

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify ledger integrity")
    verify_parser.add_argument("--consumer", "-c", type=str, required=True, help="Consumer name")

    args = parser.parse_args()

    if args.command == "append":
        append_command(args.consumer, args.event, args.source, args.payload)
    elif args.command == "list":
        list_command(args.consumer, args.limit, args.offset, args.verbose)
    elif args.command == "stats":
        stats_command(args.consumer)
    elif args.command == "anchor":
        anchor_command(args.consumer)
    elif args.command == "verify":
        verify_command(args.consumer)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()