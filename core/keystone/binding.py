#!/usr/bin/env python3
"""
Keystone Gate — Binding

SCP binding at runtime.

Features:
- Load and bind to SCP capsule
- Build system prompt from binding
- Check condition.applies_to

Usage:
    from enforcement.keystone.binding import bind_capsule, Binding

    binding = bind_capsule("mimir/binding-v1.scp.json")
    print(binding.get_persona())
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path


class Binding:
    """
    SCP binding — binds an LLM to a capsule at runtime.
    """

    def __init__(self, capsule: Dict[str, Any]):
        """
        Initialise binding from capsule.

        Args:
            capsule: SCP capsule dict
        """
        self.capsule = capsule
        self.scp_id = capsule.get("scp_id", "unknown")
        self._validate()

    def _validate(self):
        """Validate the binding capsule."""
        if "action" not in self.capsule:
            raise ValueError("Binding capsule missing 'action' field")
        if "persona" not in self.capsule.get("action", {}):
            raise ValueError("Binding capsule missing 'persona'")

    def get_persona(self) -> str:
        """Get the persona from the binding."""
        return self.capsule.get("action", {}).get("persona", "")

    def get_condition(self, key: str) -> Optional[Any]:
        """Get a condition value."""
        return self.capsule.get("condition", {}).get(key)

    def get_min_trust(self) -> float:
        """Get the minimum trust threshold."""
        return self.capsule.get("condition", {}).get("min_capsule_trust_to_cite", 0.6)

    def get_constraints(self) -> Dict[str, bool]:
        """Get the constraints from the binding."""
        return self.capsule.get("constraints", {})

    def check_applies_to(self, model_name: str) -> bool:
        """Check if this binding applies to a model."""
        applies_to = self.capsule.get("condition", {}).get("applies_to", "")
        if not applies_to:
            return True
        return model_name in applies_to

    def build_system_prompt(self) -> str:
        """Build the system prompt from the binding."""
        persona = self.get_persona()
        min_trust = self.get_min_trust()
        constraints = self.get_constraints()

        lines = [
            "You are bound to the following SCP capsule:",
            f"Persona: {persona}",
            f"Trust threshold: λ < {min_trust} must not be cited.",
        ]

        if constraints.get("no_speculation", False):
            lines.append("Do not speculate. Only answer from verified sources.")
        if constraints.get("no_hallucination", False):
            lines.append("Do not hallucinate. Only answer what you know.")
        if constraints.get("cite_sources", False):
            lines.append("Always cite sources. Show provenance for every answer.")

        lines.append("These constraints are mandatory. You must comply.")

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Export binding as dict."""
        return self.capsule.copy()


def bind_capsule(capsule_path: str, model_name: Optional[str] = None) -> Binding:
    """
    Load and bind an SCP capsule.

    Args:
        capsule_path: Path to SCP capsule
        model_name: Name of the model (for condition check)

    Returns:
        Binding instance

    Raises:
        FileNotFoundError: If capsule not found
        ValueError: If capsule is invalid
    """
    if not Path(capsule_path).exists():
        raise FileNotFoundError(f"Capsule not found: {capsule_path}")

    with open(capsule_path, "r") as f:
        capsule = json.load(f)

    binding = Binding(capsule)

    if model_name and not binding.check_applies_to(model_name):
        raise ValueError(f"Binding does not apply to model: {model_name}")

    return binding


# ============================================================
# CLI
# ============================================================

def main():
    """Test binding."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Keystone Gate — Binding")
    parser.add_argument("capsule", type=str, help="Capsule file")
    parser.add_argument("--model", "-m", type=str, help="Model name")

    args = parser.parse_args()

    try:
        binding = bind_capsule(args.capsule, args.model)

        print(f"📋 Binding: {binding.scp_id}")
        print("=" * 60)
        print(f"  Persona: {binding.get_persona()}")
        print(f"  Min trust: {binding.get_min_trust()}")
        print(f"  Applies to: {binding.get_condition('applies_to')}")

        if args.model:
            print(f"  Model: {args.model}")
            print(f"  Applies: {binding.check_applies_to(args.model)}")

        print("\n📝 System Prompt:")
        print("=" * 60)
        print(binding.build_system_prompt())

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()