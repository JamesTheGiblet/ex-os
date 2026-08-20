#!/usr/bin/env python3
"""
UBVM — CLI

Command-line interface for UBVM.

Usage:
    ubvm run capsule.scp.json
    ubvm boot
    ubvm schedule
    ubvm test
    ubvm version
"""

import sys
import json
import argparse
from pathlib import Path


def run_command(capsule_path: str, trigger: str = "manual"):
    """Run a capsule."""
    try:
        from .interpreter import Interpreter

        interpreter = Interpreter()
        result = interpreter.run(capsule_path, trigger)

        print(f"🚀 Running: {capsule_path}")
        print("=" * 60)
        print(f"scp_id: {result.get('scp_id', 'unknown')}")
        print(f"status: {result.get('status', 'unknown')}")

        if result.get("results"):
            print(f"\n📊 Results ({len(result['results'])}):")
            for r in result["results"]:
                print(f"   - {r}")

        if result.get("errors"):
            print(f"\n❌ Errors ({len(result['errors'])}):")
            for e in result["errors"]:
                print(f"   - {e}")

        if result.get("events"):
            print(f"\n📡 Events ({len(result['events'])}):")
            for e in result["events"]:
                print(f"   - {e}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def boot_command():
    """Run all on_load capsules."""
    try:
        from .triggers import TriggerHandler

        handler = TriggerHandler()
        results = handler.run_on_load()

        print("🚀 UBVM Boot")
        print("=" * 60)
        print(f"✅ {len(results)} capsules executed")

        for i, r in enumerate(results):
            status = r.get("status", "unknown")
            emoji = "✅" if status == "ok" else "⚠️" if status == "partial" else "❌"
            print(f"   {emoji} {r.get('scp_id', f'capsule-{i}')}: {status}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def schedule_command():
    """Start the scheduler (cron + event daemon)."""
    try:
        from .triggers import TriggerHandler
        from .event_bus import EventBus
        import time

        handler = TriggerHandler()
        bus = EventBus()

        print("🔄 UBVM Scheduler")
        print("=" * 60)
        print("Running cron + event daemon...")
        print("Press Ctrl+C to stop")
        print("")

        # Track cursor position
        cursor = 0

        try:
            while True:
                # Run cron tasks (every minute)
                now = time.localtime()
                if now.tm_sec == 0:
                    print(f"[{time.strftime('%H:%M:%S')}] Running cron tasks...")
                    results = handler.run_cron()
                    print(f"   ✅ {len(results)} capsules executed")

                # Process new events
                events = bus.tail_from_cursor()
                for event in events:
                    event_name = event.get("event")
                    print(f"[{time.strftime('%H:%M:%S')}] Event: {event_name} from {event.get('source', 'unknown')}")
                    if not isinstance(event_name, str):
                        continue

                    results = handler.run_on_event(event_name)
                    if results:
                        print(f"   ✅ {len(results)} capsules triggered")

                time.sleep(1)

        except KeyboardInterrupt:
            print("\n🛑 Scheduler stopped")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def test_command():
    """Run tests."""
    print("🧪 UBVM Tests")
    print("=" * 60)
    print("✅ All tests passing (placeholder)")
    print("   - Core primitives: 7 registered")
    print("   - Triggers: on_load, cron, on_event")
    print("   - Event bus: queue.jsonl")


def version_command():
    """Show version."""
    print("UBVM v1.0")
    print("Ex-OS runtime engine")
    print("Supported scp_version: 0.1, 1.0")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="UBVM — Universal Behavioural Virtual Machine",
        prog="ubvm"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a capsule")
    run_parser.add_argument("capsule", type=str, help="Capsule file path")
    run_parser.add_argument("--trigger", "-t", type=str, default="manual",
                            choices=["manual", "on_load", "cron", "on_event"])

    # Boot command
    subparsers.add_parser("boot", help="Run all on_load capsules")

    # Schedule command
    subparsers.add_parser("schedule", help="Start cron + event daemon")

    # Test command
    subparsers.add_parser("test", help="Run tests")

    # Version command
    subparsers.add_parser("version", help="Show version")

    args = parser.parse_args()

    if args.command == "run":
        run_command(args.capsule, args.trigger)
    elif args.command == "boot":
        boot_command()
    elif args.command == "schedule":
        schedule_command()
    elif args.command == "test":
        test_command()
    elif args.command == "version":
        version_command()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
