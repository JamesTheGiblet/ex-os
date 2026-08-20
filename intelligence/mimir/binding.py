#!/usr/bin/env python3
"""
Mimir — Binding Capsule Loader

Mimir's behaviour is defined by a rule-type capsule — Mimir Behavioural Binding v1.
This module loads the capsule, validates it, and enforces its constraints.

The binding capsule defines:
- Persona (terse, direct, Forge-style)
- Trust threshold (λ < 0.6 not cited)
- Model constraints (applies_to)

Usage:
    from intelligence.mimir.binding import MimirBinding

    binding = MimirBinding.load("capsules/mimir/binding-v1.scp.json")
    print(binding.get_persona())
    print(binding.get_min_trust())
"""

import json
import os
from typing import Optional, Dict, Any, List
from pathlib import Path


class MimirBinding:
    """
    Mimir Behavioural Binding capsule loader and enforcer.

    The binding capsule defines the model's persona, trust thresholds,
    and behaviour constraints at runtime — no retraining required.
    """

    def __init__(self, capsule: Dict[str, Any]):
        """
        Initialise binding from capsule dict.

        Args:
            capsule: Loaded SCP capsule dict
        """
        self.capsule = capsule
        self._validate()

    @classmethod
    def load(cls, path: str) -> "MimirBinding":
        """
        Load binding capsule from file.

        Args:
            path: Path to .scp.json capsule file

        Returns:
            MimirBinding instance

        Raises:
            FileNotFoundError: If capsule not found
            ValueError: If capsule is invalid
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Binding capsule not found: {path}")

        with open(path, "r") as f:
            capsule = json.load(f)

        return cls(capsule)

    @classmethod
    def load_default(cls) -> "MimirBinding":
        """
        Load the default Mimir Behavioural Binding v1 capsule.

        Returns:
            MimirBinding instance
        """
        default_capsule = {
            "scp_version": "0.1",
            "scp_id": "mimir/binding-v1",
            "object_class": "Safe",
            "intent": (
                "Mimir Behavioural Binding — governs LLM behaviour at runtime. "
                "Defines persona, trust thresholds, and behaviour constraints."
            ),
            "containment": {
                "read_only": True,
                "audit_log": True,
                "kill_switch": False
            },
            "condition": {
                "applies_to": "mimir-phi3-mini-q4km",
                "min_capsule_trust_to_cite": 0.6,
                "allowed_domains": ["code", "system", "general"],
            },
            "action": {
                "persona": "terse, direct, Forge-style — no fluff",
                "response_style": "structured",
                "citation_required": True,
            },
            "constraints": {
                "no_speculation": True,
                "no_hallucination": True,
                "cite_sources": True,
            }
        }
        return cls(default_capsule)

    def _validate(self):
        """Validate the binding capsule schema."""
        # Check required fields
        required_fields = ["scp_id", "scp_version", "object_class", "intent", "condition", "action"]
        for field in required_fields:
            if field not in self.capsule:
                raise ValueError(f"Binding capsule missing required field: {field}")

        # Check condition fields
        condition = self.capsule.get("condition", {})
        if "min_capsule_trust_to_cite" not in condition:
            raise ValueError("Binding capsule missing min_capsule_trust_to_cite")

        # Check action fields
        action = self.capsule.get("action", {})
        if "persona" not in action:
            raise ValueError("Binding capsule missing persona")

        # Check scp_id format
        scp_id = self.capsule.get("scp_id", "")
        if not scp_id.startswith("mimir/"):
            raise ValueError(f"Binding capsule scp_id must start with 'mimir/': {scp_id}")

        # Check trust threshold range
        min_trust = condition.get("min_capsule_trust_to_cite", 0.0)
        if not 0.0 <= min_trust <= 2.0:
            raise ValueError(f"min_capsule_trust_to_cite must be 0.0-2.0: {min_trust}")

    def get_scp_id(self) -> str:
        """Get capsule scp_id."""
        return self.capsule.get("scp_id", "mimir/binding-v1")

    def get_persona(self) -> str:
        """Get the persona description."""
        return self.capsule.get("action", {}).get("persona", "Forge-style, direct, no fluff.")

    def get_min_trust(self) -> float:
        """Get the minimum trust threshold for citing sources."""
        return self.capsule.get("condition", {}).get("min_capsule_trust_to_cite", 0.6)

    def get_applies_to(self) -> str:
        """Get the model this binding applies to."""
        return self.capsule.get("condition", {}).get("applies_to", "mimir-phi3-mini-q4km")

    def get_allowed_domains(self) -> List[str]:
        """Get allowed domains for queries."""
        return self.capsule.get("condition", {}).get("allowed_domains", ["code", "system", "general"])

    def get_response_style(self) -> str:
        """Get the response style."""
        return self.capsule.get("action", {}).get("response_style", "structured")

    def citation_required(self) -> bool:
        """Check if citations are required."""
        return self.capsule.get("action", {}).get("citation_required", True)

    def get_constraints(self) -> Dict[str, bool]:
        """Get behaviour constraints."""
        return self.capsule.get("constraints", {
            "no_speculation": True,
            "no_hallucination": True,
            "cite_sources": True,
        })

    def build_system_prompt(self) -> str:
        """
        Build a system prompt from the binding capsule.

        Returns:
            System prompt string for LLM
        """
        persona = self.get_persona()
        min_trust = self.get_min_trust()
        constraints = self.get_constraints()

        lines = [
            "You are Mimir, an sc-bound LLM.",
            f"Persona: {persona}",
            f"Trust threshold: λ < {min_trust} must not be cited.",
        ]

        if constraints.get("no_speculation", True):
            lines.append("Do not speculate. Only answer from verified sources.")
        if constraints.get("no_hallucination", True):
            lines.append("Do not hallucinate. Only answer what you know.")
        if constraints.get("cite_sources", True):
            lines.append("Always cite sources. Show provenance for every answer.")

        lines.append("Be direct. No fluff. No filler.")
        lines.append("Think in Forge style.")

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Export binding capsule as dict."""
        return self.capsule.copy()

    def to_json(self, indent: int = 2) -> str:
        """Export binding capsule as JSON."""
        return json.dumps(self.capsule, indent=indent)


def verify_binding(capsule: Dict[str, Any]) -> bool:
    """
    Verify that a capsule is a valid Mimir binding.

    Args:
        capsule: Capsule dict to verify

    Returns:
        True if valid
    """
    try:
        binding = MimirBinding(capsule)
        return True
    except ValueError:
        return False


# ============================================================
# CLI
# ============================================================

def main():
    """Test binding loader."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Mimir — Binding Capsule Loader")
    parser.add_argument("--file", "-f", type=str, help="Path to binding capsule")
    parser.add_argument("--verify", "-v", action="store_true", help="Verify binding")
    parser.add_argument("--show-prompt", "-p", action="store_true", help="Show system prompt")

    args = parser.parse_args()

    if args.file:
        try:
            binding = MimirBinding.load(args.file)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    else:
        binding = MimirBinding.load_default()

    print("✅ Mimir Binding loaded")
    print(f"   scp_id: {binding.get_scp_id()}")
    print(f"   Persona: {binding.get_persona()}")
    print(f"   Min trust: {binding.get_min_trust()}")
    print(f"   Applies to: {binding.get_applies_to()}")
    print(f"   Allowed domains: {binding.get_allowed_domains()}")
    print(f"   Citation required: {binding.citation_required()}")

    if args.show_prompt:
        print("\n" + "=" * 60)
        print("SYSTEM PROMPT:")
        print("=" * 60)
        print(binding.build_system_prompt())

    if args.verify:
        print("\n" + "=" * 60)
        print("VERIFICATION:")
        print("=" * 60)
        if verify_binding(binding.to_dict()):
            print("✅ Binding is valid")
        else:
            print("❌ Binding is invalid")


if __name__ == "__main__":
    main()