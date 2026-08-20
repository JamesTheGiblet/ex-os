#!/usr/bin/env python3
"""
HAL — CLI

Command-line interface for HAL.

Usage:
    hal seal --action DEPLOY --authoriser did:key:... --tier 3 --score score.json
    hal list
    hal get <seal_id>
    hal tiers
    hal verify <score_file>
"""

import sys
import json
import argparse
from pathlib import Path


def seal_command(
    action: str,
    authoriser: str,
    tier: int,
    score_file: str,
    description: str = "",
):
    """Seal an action."""
    try:
        from .seal import seal

        result = seal(
            action=action,
            authoriser=authoriser,
            tier=tier,
            score_file=score_file,
            description=description,
        )

        print(f"🔏 HAL — Seal Result")
        print("=" * 60)
        print(f"Status: {result['status']}")
        print(f"Message: {result.get('message', '')}")

        if result.get('seal'):
            seal_data = result['seal']
            print(f"\n📋 Seal Details:")
            print(f"   ID: {seal_data['seal_id']}")
            print(f"   Action: {seal_data['action']}")
            print(f"   Tier: {seal_data['tier']}")
            print(f"   λ: {seal_data['λ']:.2f}")
            print(f"   Separation: {seal_data['separation']}")
            print(f"   Timestamp: {seal_data['timestamp']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def list_command(limit: int = 20):
    """List seals."""
    try:
        from .seal import list_seals

        seals = list_seals(limit=limit)

        print("📋 HAL Seals")
        print("=" * 60)

        if not seals:
            print("No seals found")
            return

        for s in seals:
            print(f"  {s.get('seal_id', 'unknown')} — {s.get('action', 'unknown')} (tier {s.get('tier', '?')})")
            print(f"    λ: {s.get('λ', 0):.2f} | {s.get('timestamp', 'unknown')}")

        print(f"\nTotal: {len(seals)}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def get_command(seal_id: str):
    """Get a seal by ID."""
    try:
        from .seal import get_seal

        seal_data = get_seal(seal_id)

        if not seal_data:
            print(f"❌ Seal not found: {seal_id}")
            sys.exit(1)

        print(f"🔏 Seal: {seal_id}")
        print("=" * 60)
        print(json.dumps(seal_data, indent=2))

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def tiers_command():
    """Display tier information."""
    try:
        from .tiers import TIERS, QUARANTINE_THRESHOLD, REFLEX_THRESHOLD

        print("📋 HAL Tiers")
        print("=" * 60)
        print(f"Quarantine: λ < {QUARANTINE_THRESHOLD}")
        print(f"Reflex: λ ≥ {REFLEX_THRESHOLD}")
        print("")

        for tier, data in TIERS.items():
            print(f"Tier {tier}: {data['name']}")
            print(f"  Min λ: {data['min_λ']}")
            print(f"  {data['description']}")
            print(f"  Consequence: {data['consequence']}")
            print("")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def verify_command(score_file: str, max_age: int = 3600):
    """Verify a score file."""
    try:
        from .verify import load_score_file, verify_score_file

        score_data = load_score_file(score_file)
        valid, message = verify_score_file(score_data, max_age)

        if valid:
            print(f"✅ Valid score file")
            print(f"   Entity: {score_data.get('entity_id', 'unknown')}")
            print(f"   λ: {score_data.get('λ', 0):.2f}")
            print(f"   Timestamp: {score_data.get('timestamp', 'unknown')}")
        else:
            print(f"❌ Invalid: {message}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="HAL — Human Accountability Layer",
        prog="hal"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Seal command
    seal_parser = subparsers.add_parser("seal", help="Seal an action")
    seal_parser.add_argument("--action", "-a", type=str, required=True, help="Action to seal")
    seal_parser.add_argument("--authoriser", "-i", type=str, required=True, help="Authoriser did:key")
    seal_parser.add_argument("--tier", "-t", type=int, default=3, help="Tier (1-5)")
    seal_parser.add_argument("--score", "-s", type=str, required=True, help="Score file path")
    seal_parser.add_argument("--description", "-d", type=str, help="Description")

    # List command
    list_parser = subparsers.add_parser("list", help="List seals")
    list_parser.add_argument("--limit", "-l", type=int, default=20, help="Max seals")

    # Get command
    get_parser = subparsers.add_parser("get", help="Get seal by ID")
    get_parser.add_argument("seal_id", type=str, help="Seal ID")

    # Tiers command
    subparsers.add_parser("tiers", help="Show tier information")

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify a score file")
    verify_parser.add_argument("file", type=str, help="Score file path")
    verify_parser.add_argument("--max-age", "-a", type=int, default=3600, help="Max age in seconds")

    args = parser.parse_args()

    if args.command == "seal":
        seal_command(args.action, args.authoriser, args.tier, args.score, args.description)
    elif args.command == "list":
        list_command(args.limit)
    elif args.command == "get":
        get_command(args.seal_id)
    elif args.command == "tiers":
        tiers_command()
    elif args.command == "verify":
        verify_command(args.file, args.max_age)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
