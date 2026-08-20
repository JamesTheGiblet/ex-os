#!/usr/bin/env python3
"""
UBVM — Interpreter

The core dispatch loop of UBVM.

Features:
- Loads and validates SCP capsules
- Evaluates triggers (on_load, cron, on_event)
- Dispatches primitives in order
- Returns structured result objects

Usage:
    from runtime.ubvm.interpreter import Interpreter

    interpreter = Interpreter()
    result = interpreter.run("capsules/example.scp.json")
    print(result["status"])
"""

import json
import os
import sys
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from datetime import datetime

# Import primitives
from .primitives import DISPATCH


class Interpreter:
    """
    UBVM interpreter — executes SCP capsules.
    """

    # Supported versions
    SUPPORTED_VERSIONS = ["0.1", "1.0"]

    def __init__(self, ubvm_home: Optional[str] = None):
        """
        Initialise interpreter.

        Args:
            ubvm_home: UBVM home directory
        """
        self.ubvm_home = ubvm_home or os.environ.get("UBVM_HOME", os.getcwd())
        self.results = []

    def run(self, capsule_path: str, trigger: str = "manual") -> Dict[str, Any]:
        """
        Run a capsule.

        Args:
            capsule_path: Path to capsule file
            trigger: Trigger type ("manual", "on_load", "cron", "on_event")

        Returns:
            Result dict with status, results, errors, events
        """
        # Load capsule
        try:
            with open(capsule_path, "r") as f:
                capsule = json.load(f)
        except Exception as e:
            return {
                "scp_id": "unknown",
                "status": "error",
                "results": [],
                "errors": [f"Failed to load capsule: {e}"],
                "events": [],
            }

        # Validate capsule
        validation = self._validate(capsule)
        if not validation["valid"]:
            return {
                "scp_id": capsule.get("scp_id", "unknown"),
                "status": "error",
                "results": [],
                "errors": validation["errors"],
                "events": [],
            }

        scp_id = capsule.get("scp_id", "unknown")

        # Get behaviours
        behaviours = capsule.get("behaviours", [])

        # Filter by trigger
        matching_behaviours = [
            b for b in behaviours
            if b.get("trigger") == trigger or trigger == "manual"
        ]

        if not matching_behaviours:
            # No matching behaviours, but that's not an error
            return {
                "scp_id": scp_id,
                "status": "ok",
                "results": [],
                "errors": [],
                "events": [],
            }

        # Execute behaviours
        all_results = []
        all_errors = []
        all_events = []

        for behaviour in matching_behaviours:
            actions = behaviour.get("actions", [])

            for action in actions:
                primitive_name = action.get("primitive")
                params = action.get("params", {})

                if not primitive_name:
                    all_errors.append("Action missing 'primitive' field")
                    continue

                # Get primitive
                primitive = DISPATCH.get(primitive_name)
                if primitive is None:
                    all_errors.append(f"Unknown primitive: {primitive_name}")
                    continue

                # Build context
                context = self._build_context(capsule)

                # Execute primitive
                try:
                    result = primitive(params, context)
                    all_results.append(result)

                    # Collect events from result
                    if isinstance(result, dict) and "events" in result:
                        all_events.extend(result["events"])

                except Exception as e:
                    all_errors.append(f"Primitive '{primitive_name}' failed: {e}")

        # Determine status
        if all_errors:
            if all_results:
                status = "partial"
            else:
                status = "error"
        else:
            status = "ok"

        return {
            "scp_id": scp_id,
            "status": status,
            "results": all_results,
            "errors": all_errors,
            "events": all_events,
        }

    def _validate(self, capsule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a capsule against the schema.

        Returns:
            Dict with 'valid' bool and 'errors' list
        """
        errors = []

        # Check required fields
        required = ["scp_version", "scp_id", "object_class", "intent", "behaviours"]
        for field in required:
            if field not in capsule:
                errors.append(f"Missing required field: {field}")

        # Check scp_version
        scp_version = capsule.get("scp_version", "")
        if scp_version not in self.SUPPORTED_VERSIONS:
            errors.append(f"Unsupported scp_version: {scp_version}")

        # Check object_class
        object_class = capsule.get("object_class", "")
        if object_class not in ["Safe", "Euclid", "Keter", "Thaumiel"]:
            errors.append(f"Invalid object_class: {object_class}")

        # Check behaviours
        behaviours = capsule.get("behaviours", [])
        if not behaviours:
            errors.append("No behaviours defined")

        for i, behaviour in enumerate(behaviours):
            trigger = behaviour.get("trigger")
            if trigger not in ["on_load", "cron", "on_event"]:
                errors.append(f"Behaviour {i}: invalid trigger: {trigger}")

            if trigger == "cron" and "schedule" not in behaviour:
                errors.append(f"Behaviour {i}: cron trigger missing schedule")

            if trigger == "on_event" and "event" not in behaviour:
                errors.append(f"Behaviour {i}: on_event trigger missing event")

            actions = behaviour.get("actions", [])
            if not actions:
                errors.append(f"Behaviour {i}: no actions defined")

            for j, action in enumerate(actions):
                if "primitive" not in action:
                    errors.append(f"Behaviour {i}, action {j}: missing primitive")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }

    def _build_context(self, capsule: Dict[str, Any]) -> Dict[str, Any]:
        """Build runtime context for primitives."""
        return {
            "scp_id": capsule.get("scp_id", "unknown"),
            "ubvm_home": self.ubvm_home,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "env": {
                k: v for k, v in os.environ.items()
                if k.startswith(("UBVM_", "UBC_", "EXOS_"))
            },
        }


def run_capsule(capsule_path: str, trigger: str = "manual") -> Dict[str, Any]:
    """
    Convenience function to run a capsule.

    Args:
        capsule_path: Path to capsule file
        trigger: Trigger type

    Returns:
        Result dict
    """
    interpreter = Interpreter()
    return interpreter.run(capsule_path, trigger)


# ============================================================
# CLI
# ============================================================

def main():
    """Test interpreter."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="UBVM — Interpreter")
    parser.add_argument("capsule", type=str, help="Capsule file path")
    parser.add_argument("--trigger", "-t", type=str, default="manual",
                        choices=["manual", "on_load", "cron", "on_event"])

    args = parser.parse_args()

    print(f"🚀 UBVM Interpreter")
    print(f"   Capsule: {args.capsule}")
    print(f"   Trigger: {args.trigger}")
    print("=" * 60)

    result = run_capsule(args.capsule, args.trigger)

    print(f"\n📊 Result:")
    print(f"   scp_id: {result.get('scp_id', 'unknown')}")
    print(f"   status: {result.get('status', 'unknown')}")

    if result.get("results"):
        print(f"   Results: {len(result['results'])}")
        for r in result["results"]:
            print(f"     - {r}")

    if result.get("errors"):
        print(f"   Errors: {len(result['errors'])}")
        for e in result["errors"]:
            print(f"     ❌ {e}")

    if result.get("events"):
        print(f"   Events: {len(result['events'])}")
        for e in result["events"]:
            print(f"     📡 {e}")


if __name__ == "__main__":
    main()