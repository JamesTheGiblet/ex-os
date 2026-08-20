#!/usr/bin/env python3
"""
DataCube — CLI

Command-line interface for DataCube.

Usage:
    datacube create "claim" --namespace domain.general --lens UNKNOWN
    datacube list --lens FACT --limit 10
    datacube stats
    datacube ingest data.json --namespace domain.electronics
    datacube validate cube-123 --validator James
"""

import sys
import json
import argparse
from pathlib import Path


def create_command(claim: str, namespace: str, lens: str):
    """Create a cube."""
    try:
        from .cube import create_cube
        from .store import save_cube

        cube = create_cube(claim, namespace, lens)
        cube.fill_all_lenses()

        cube_id = save_cube(cube)

        print(f"✅ Cube created: {cube_id}")
        print(f"   Claim: {cube.claim}")
        print(f"   Lens: {cube.lens}")
        print(f"   Completeness: {cube.get_completeness():.2%}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def list_command(lens: str, namespace: str, limit: int, min_completeness: float):
    """List cubes."""
    try:
        from .store import search_cubes

        cubes = search_cubes(lens, namespace, min_completeness, limit)

        if not cubes:
            print("No cubes found")
            return

        print(f"📋 Cubes ({len(cubes)}):")
        print("=" * 60)

        for c in cubes:
            completeness = c.get_completeness()
            emoji = "🔒" if c.is_trust_eligible() else "📝" if c.is_fully_validated() else "⏳"
            print(f"  {emoji} {c.cube_id} — {c.lens} ({completeness:.0%})")
            print(f"     {c.claim[:60]}...")
            print(f"     Namespace: {c.namespace}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def stats_command(store_dir: str = "cubes"):
    """Show store statistics."""
    try:
        from .store import CubeStore

        store = CubeStore(store_dir)
        stats = store.get_stats()

        print(f"📊 DataCube Store")
        print("=" * 60)
        print(f"  Total cubes: {stats['total']}")
        print(f"  Validated: {stats['validated']}")
        print(f"\n  By lens:")
        for lens, count in stats['by_lens'].items():
            bar = "█" * int(count / max(1, stats['total']) * 30)
            print(f"    {lens}: {count:4d} {bar}")
        print(f"\n  By namespace:")
        for ns, count in stats['by_namespace'].items():
            print(f"    {ns}: {count}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def ingest_command(file_path: str, namespace: str, store_dir: str = "cubes"):
    """Bulk ingest a file."""
    try:
        from .bulk import bulk_ingest_auto
        from .store import CubeStore

        store = CubeStore(store_dir)
        cubes = bulk_ingest_auto(file_path, namespace, store)

        print(f"✅ Ingested {len(cubes)} cubes from {file_path}")
        print(f"   Namespace: {namespace}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def validate_command(cube_id: str, validator: str, store_dir: str = "cubes"):
    """Apply human validation to a cube."""
    try:
        from .store import CubeStore

        store = CubeStore(store_dir)
        cube = store.get(cube_id)

        if not cube:
            print(f"❌ Cube not found: {cube_id}")
            sys.exit(1)

        cube.validate_human(validator)
        store.save(cube)

        print(f"✅ Validated: {cube_id}")
        print(f"   Validator: {validator}")
        print(f"   Completeness: {cube.get_completeness():.2%}")
        print(f"   Trust eligible: {cube.is_trust_eligible()}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="DataCube — The Classify Stage",
        prog="datacube"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a cube")
    create_parser.add_argument("claim", type=str, help="The claim")
    create_parser.add_argument("--namespace", "-n", type=str, default="domain.general", help="Namespace")
    create_parser.add_argument("--lens", "-l", type=str, default="UNKNOWN", help="Lens")

    # List command
    list_parser = subparsers.add_parser("list", help="List cubes")
    list_parser.add_argument("--lens", "-l", type=str, help="Filter by lens")
    list_parser.add_argument("--namespace", "-n", type=str, help="Filter by namespace")
    list_parser.add_argument("--limit", "-L", type=int, default=20, help="Max results")
    list_parser.add_argument("--min-completeness", "-m", type=float, default=0.0, help="Min completeness")

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show store statistics")
    stats_parser.add_argument("--store", "-s", type=str, default="cubes", help="Store directory")

    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Bulk ingest a file")
    ingest_parser.add_argument("file", type=str, help="File to ingest (.json or .csv)")
    ingest_parser.add_argument("--namespace", "-n", type=str, default="domain.unknown", help="Namespace")
    ingest_parser.add_argument("--store", "-s", type=str, default="cubes", help="Store directory")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Apply human validation")
    validate_parser.add_argument("cube_id", type=str, help="Cube ID")
    validate_parser.add_argument("--validator", "-v", type=str, default="cli", help="Validator name")
    validate_parser.add_argument("--store", "-s", type=str, default="cubes", help="Store directory")

    args = parser.parse_args()

    if args.command == "create":
        create_command(args.claim, args.namespace, args.lens)
    elif args.command == "list":
        list_command(args.lens, args.namespace, args.limit, args.min_completeness)
    elif args.command == "stats":
        stats_command(args.store)
    elif args.command == "ingest":
        ingest_command(args.file, args.namespace, args.store)
    elif args.command == "validate":
        validate_command(args.cube_id, args.validator, args.store)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()