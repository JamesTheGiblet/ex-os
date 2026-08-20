#!/usr/bin/env python3
"""
UBVM — Trigger Handler

Handles triggers for capsule execution:
- on_load: Run once on boot
- cron: Run on schedule
- on_event: Run when event matches

Usage:
    from runtime.ubvm.triggers import TriggerHandler

    handler = TriggerHandler()
    handler.run_on_load()
    handler.run_cron()
    handler.run_on_event("sensor.button.press")
"""

import os
import json
import glob
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from .interpreter import Interpreter


class TriggerHandler:
    """
    UBVM trigger handler — manages trigger execution.
    """

    def __init__(self, ubvm_home: Optional[str] = None):
        """
        Initialise trigger handler.

        Args:
            ubvm_home: UBVM home directory
        """
        self.ubvm_home = ubvm_home or os.environ.get("UBVM_HOME", os.getcwd())
        self.capsule_dir = os.path.join(self.ubvm_home, "capsules")
        self.interpreter = Interpreter(self.ubvm_home)

    def get_capsules(self) -> List[Dict[str, Any]]:
        """Load all capsules from capsule directory."""
        capsules = []

        if not os.path.exists(self.capsule_dir):
            return capsules

        for file_path in glob.glob(os.path.join(self.capsule_dir, "**", "*.scp.json"), recursive=True):
            try:
                with open(file_path, "r") as f:
                    capsule = json.load(f)
                    capsule["_file"] = file_path
                    capsules.append(capsule)
            except (json.JSONDecodeError, OSError):
                continue

        return capsules

    def run_on_load(self) -> List[Dict[str, Any]]:
        """Run all on_load capsules."""
        results = []
        capsules = self.get_capsules()

        for capsule in capsules:
            behaviours = capsule.get("behaviours", [])
            has_on_load = any(b.get("trigger") == "on_load" for b in behaviours)

            if has_on_load:
                result = self.interpreter.run(capsule["_file"], "on_load")
                results.append(result)

        return results

    def run_cron(self) -> List[Dict[str, Any]]:
        """Run all cron capsules."""
        results = []
        capsules = self.get_capsules()

        # Get current time for cron matching
        now = datetime.now()

        for capsule in capsules:
            behaviours = capsule.get("behaviours", [])
            for behaviour in behaviours:
                if behaviour.get("trigger") == "cron":
                    schedule = behaviour.get("schedule")
                    if schedule and self._matches_cron(schedule, now):
                        result = self.interpreter.run(capsule["_file"], "cron")
                        results.append(result)

        return results

    def run_on_event(self, event_name: str) -> List[Dict[str, Any]]:
        """Run all on_event capsules matching the event."""
        results = []
        capsules = self.get_capsules()

        for capsule in capsules:
            behaviours = capsule.get("behaviours", [])
            for behaviour in behaviours:
                if behaviour.get("trigger") == "on_event":
                    event = behaviour.get("event")
                    if event and event == event_name:
                        result = self.interpreter.run(capsule["_file"], "on_event")
                        results.append(result)

        return results

    def _matches_cron(self, schedule: str, now: datetime) -> bool:
        """
        Check if current time matches cron schedule.

        Simple cron matching:
        - minute hour day month day_of_week
        - * matches any
        - /step supported
        """
        parts = schedule.split()
        if len(parts) != 5:
            return False

        minute, hour, day, month, dow = parts

        # Simple matching (basic implementation)
        match = True

        # Minute
        if minute != "*":
            if "/" in minute:
                step = int(minute.split("/")[1])
                if now.minute % step != 0:
                    match = False
            elif int(minute) != now.minute:
                match = False

        # Hour
        if match and hour != "*":
            if "/" in hour:
                step = int(hour.split("/")[1])
                if now.hour % step != 0:
                    match = False
            elif int(hour) != now.hour:
                match = False

        # Day
        if match and day != "*":
            if "/" in day:
                step = int(day.split("/")[1])
                if now.day % step != 0:
                    match = False
            elif int(day) != now.day:
                match = False

        # Month
        if match and month != "*":
            if "/" in month:
                step = int(month.split("/")[1])
                if now.month % step != 0:
                    match = False
            elif int(month) != now.month:
                match = False

        # Day of week
        if match and dow != "*":
            if "/" in dow:
                step = int(dow.split("/")[1])
                if now.weekday() % step != 0:
                    match = False
            elif int(dow) != now.weekday():
                match = False

        return match


# ============================================================
# CLI
# ============================================================

def main():
    """Test trigger handler."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="UBVM — Trigger Handler")
    parser.add_argument("--on-load", "-l", action="store_true", help="Run on_load capsules")
    parser.add_argument("--cron", "-c", action="store_true", help="Run cron capsules")
    parser.add_argument("--event", "-e", type=str, help="Run on_event capsules matching event")

    args = parser.parse_args()

    handler = TriggerHandler()

    if args.on_load:
        print("🔄 Running on_load capsules...")
        results = handler.run_on_load()
        print(f"✅ {len(results)} capsules executed")

    if args.cron:
        print("🔄 Running cron capsules...")
        results = handler.run_cron()
        print(f"✅ {len(results)} capsules executed")

    if args.event:
        print(f"🔄 Running on_event capsules for: {args.event}")
        results = handler.run_on_event(args.event)
        print(f"✅ {len(results)} capsules executed")

    if not any([args.on_load, args.cron, args.event]):
        parser.print_help()


if __name__ == "__main__":
    main()