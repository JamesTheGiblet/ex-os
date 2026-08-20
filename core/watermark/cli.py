#!/usr/bin/env python3
"""
Watermark — CLI

Command-line interface for Watermark.

Usage:
    watermark embed "content" --source mimir --trust 0.92
    watermark verify "content"
    watermark provenance --source mimir --trust 0.92
    watermark list
    watermark get <id>
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional


def embed_command(
    content: Optional[str],
    source: str,
    trust: float,
    capsule: Optional[str] = None,
    file: Optional[str] = None,
) -> None:
    """Embed a watermark."""
    try:
        from .engine import watermark_content

        if file:
            with open(file, "r") as f:
                content = f.read()

        if content is None:
            print("âŒ Provide --content or --file")
            sys.exit(1)

        watermarked = watermark_content(content, source, trust, capsule)

        print(f"✅ Watermarked")
        print("=" * 60)
        print(watermarked)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def verify_command(content: Optional[str] = None, file: Optional[str] = None) -> None:
    """Verify a watermark."""
    try:
        from .verify import verify_watermark

        if file:
            with open(file, "r") as f:
                content = f.read()

        if not content:
            print("❌ Provide --content or --file")
            sys.exit(1)

        result = verify_watermark(content)

        if result["valid"]:
            print(f"✅ Watermark Verified")
            print(f"   ID: {result['provenance_id']}")
            print(f"   Source: {result['provenance'].get('source', 'unknown')}")
            print(f"   Trust: {result['provenance'].get('trust_score', 0):.2f}")
            print(f"   Timestamp: {result['provenance'].get('timestamp', 'unknown')}")
        else:
            print(f"❌ Verification Failed")
            print(f"   Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def provenance_command(
    source: Optional[str] = None,
    trust: float = 0.90,
    capsule: Optional[str] = None,
) -> None:
    """Track provenance."""
    try:
        from .provenance import track_provenance

        provenance_id = track_provenance(
            source=source or "cli",
            trust_score=trust,
            capsule_id=capsule,
        )

        print(f"✅ Provenance tracked: {provenance_id}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def list_command(limit: int = 20):
    """List watermarks."""
    try:
        from .engine import WatermarkEngine

        engine = WatermarkEngine()
        watermarks = engine.list_provenance(limit)

        print(f"📋 Watermarks ({len(watermarks)})")
        print("=" * 60)
        for w in watermarks:
            print(f"  {w.get('provenance_id')} — {w.get('source')} (λ: {w.get('trust_score', 0):.2f})")
            print(f"    {w.get('timestamp', 'unknown')}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def get_command(provenance_id: str):
    """Get provenance by ID."""
    try:
        from .engine import WatermarkEngine

        engine = WatermarkEngine()
        provenance = engine.get_provenance(provenance_id)

        if not provenance:
            print(f"❌ Provenance not found: {provenance_id}")
            sys.exit(1)

        print(f"📋 Provenance: {provenance_id}")
        print("=" * 60)
        print(json.dumps(provenance, indent=2))

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Watermark — Provenance and Traceability",
        prog="watermark"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Embed command
    embed_parser = subparsers.add_parser("embed", help="Embed a watermark")
    embed_parser.add_argument("--content", "-c", type=str, help="Content to watermark")
    embed_parser.add_argument("--file", "-f", type=str, help="File to watermark")
    embed_parser.add_argument("--source", "-s", type=str, required=True, help="Source")
    embed_parser.add_argument("--trust", "-t", type=float, default=0.90, help="Trust score")
    embed_parser.add_argument("--capsule", "-C", type=str, help="Capsule ID")

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify a watermark")
    verify_parser.add_argument("--content", "-c", type=str, help="Content to verify")
    verify_parser.add_argument("--file", "-f", type=str, help="File to verify")

    # Provenance command
    prov_parser = subparsers.add_parser("provenance", help="Track provenance")
    prov_parser.add_argument("--source", "-s", type=str, help="Source")
    prov_parser.add_argument("--trust", "-t", type=float, default=0.90, help="Trust score")
    prov_parser.add_argument("--capsule", "-C", type=str, help="Capsule ID")

    # List command
    list_parser = subparsers.add_parser("list", help="List watermarks")
    list_parser.add_argument("--limit", "-l", type=int, default=20, help="Max results")

    # Get command
    get_parser = subparsers.add_parser("get", help="Get provenance by ID")
    get_parser.add_argument("provenance_id", type=str, help="Provenance ID")

    args = parser.parse_args()

    if args.command == "embed":
        embed_command(args.content, args.source, args.trust, args.capsule, args.file)
    elif args.command == "verify":
        verify_command(args.content, args.file)
    elif args.command == "provenance":
        provenance_command(args.source, args.trust, args.capsule)
    elif args.command == "list":
        list_command(args.limit)
    elif args.command == "get":
        get_command(args.provenance_id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
