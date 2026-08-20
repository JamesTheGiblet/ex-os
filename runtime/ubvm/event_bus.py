#!/usr/bin/env python3
"""
UBVM — Event Bus

Handles the append-only event bus (queue.jsonl).

Features:
- Append events to queue.jsonl
- Tail the queue for new events
- Maintain cursor position for restart safety

Usage:
    from runtime.ubvm.event_bus import EventBus

    bus = EventBus()
    bus.emit("sensor.button.press", {"pin": 0}, source="esp32-001")
    events = bus.tail()
    for event in events:
        print(event)
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path


class EventBus:
    """
    UBVM event bus — append-only queue.jsonl.
    """

    def __init__(self, ubvm_home: Optional[str] = None):
        """
        Initialise event bus.

        Args:
            ubvm_home: UBVM home directory
        """
        self.ubvm_home = ubvm_home or os.environ.get("UBVM_HOME", os.getcwd())
        self.event_dir = os.path.join(self.ubvm_home, "logs", "events")
        self.queue_path = os.path.join(self.event_dir, "queue.jsonl")
        self.cursor_path = os.path.join(self.event_dir, ".cursor")
        self._init_dirs()

    def _init_dirs(self):
        """Create event directory if it doesn't exist."""
        os.makedirs(self.event_dir, exist_ok=True)

        if not os.path.exists(self.queue_path):
            with open(self.queue_path, "w") as f:
                pass

    def emit(self, event: str, payload: Dict[str, Any], source: str = "unknown") -> Dict[str, Any]:
        """
        Emit an event to the bus.

        Args:
            event: Event name
            payload: Event payload
            source: Event source

        Returns:
            The event entry
        """
        entry = {
            "event": event,
            "source": source,
            "payload": payload,
            "ts": datetime.utcnow().isoformat() + "Z",
        }

        with open(self.queue_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

        return entry

    def tail(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the latest events from the bus.

        Args:
            limit: Maximum number of events

        Returns:
            List of event entries
        """
        events = []

        if not os.path.exists(self.queue_path):
            return events

        with open(self.queue_path, "r") as f:
            lines = f.readlines()

        # Read last N lines
        for line in lines[-limit:]:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

        return events

    def tail_from_cursor(self) -> List[Dict[str, Any]]:
        """
        Tail events from the last cursor position.

        Returns:
            List of new events
        """
        if not os.path.exists(self.queue_path):
            return []

        # Get current cursor position
        cursor = self._get_cursor()

        events = []
        with open(self.queue_path, "r") as f:
            f.seek(cursor)
            for line in f:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
                cursor += len(line) + 1  # +1 for newline

        # Update cursor
        self._set_cursor(cursor)

        return events

    def _get_cursor(self) -> int:
        """Get the saved cursor position."""
        if os.path.exists(self.cursor_path):
            try:
                with open(self.cursor_path, "r") as f:
                    return int(f.read().strip())
            except (ValueError, OSError):
                return 0
        return 0

    def _set_cursor(self, position: int):
        """Save the cursor position."""
        with open(self.cursor_path, "w") as f:
            f.write(str(position))

    def clear(self):
        """Clear the event bus (dangerous — use with caution)."""
        if os.path.exists(self.queue_path):
            os.remove(self.queue_path)
            with open(self.queue_path, "w") as f:
                pass

        if os.path.exists(self.cursor_path):
            os.remove(self.cursor_path)

    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics."""
        if not os.path.exists(self.queue_path):
            return {"size": 0, "events": 0}

        size = os.path.getsize(self.queue_path)

        with open(self.queue_path, "r") as f:
            line_count = sum(1 for _ in f)

        return {
            "size": size,
            "events": line_count,
            "cursor": self._get_cursor(),
        }


# ============================================================
# CLI
# ============================================================

def main():
    """Test event bus."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="UBVM — Event Bus")
    parser.add_argument("--emit", "-e", type=str, help="Emit an event")
    parser.add_argument("--payload", "-p", type=str, default="{}", help="Event payload (JSON)")
    parser.add_argument("--source", "-s", type=str, default="cli", help="Event source")
    parser.add_argument("--tail", "-t", action="store_true", help="Tail events")
    parser.add_argument("--limit", "-l", type=int, default=10, help="Tail limit")
    parser.add_argument("--stats", action="store_true", help="Show stats")

    args = parser.parse_args()

    bus = EventBus()

    if args.emit:
        try:
            payload = json.loads(args.payload)
        except json.JSONDecodeError:
            payload = {}

        entry = bus.emit(args.emit, payload, args.source)
        print(f"✅ Event emitted: {entry['event']}")

    if args.tail:
        events = bus.tail(args.limit)
        print(f"\n📋 Last {len(events)} events:")
        for e in events:
            print(f"   [{e.get('source', 'unknown')}] {e.get('event')}: {e.get('payload', {})}")

    if args.stats:
        stats = bus.get_stats()
        print(f"\n📊 Event Bus Stats:")
        print(f"   Size: {stats['size']} bytes")
        print(f"   Events: {stats['events']}")
        print(f"   Cursor: {stats['cursor']}")


if __name__ == "__main__":
    main()