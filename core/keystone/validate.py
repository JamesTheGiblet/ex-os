#!/usr/bin/env python3
"""
Keystone Gate — Validation

Validates LLM responses against SCP capsules.

Features:
- Check compliance with persona
- Check trust threshold (λ > 0.85)
- Check constraints (no speculation, no hallucination)
- Audit trail generation

Usage:
    from enforcement.keystone.validate import validate_against_capsule

    result = validate_against_capsule(response, capsule)
"""

import json
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime


def validate_against_capsule(
    response: str,
    capsule: Dict[str, Any],
    trust_threshold: float = 0.85,
) -> Dict[str, Any]:
    """
    Validate a response against a capsule.

    Args:
        response: Response text
        capsule: SCP capsule dict
        trust_threshold: λ threshold

    Returns:
        Validation result dict
    """
    errors = []
    warnings = []
    passed = True

    # Check persona compliance
    persona = capsule.get("action", {}).get("persona", "")
    if persona:
        if not _check_persona(response, persona):
            errors.append("Response does not match required persona")
            passed = False
        else:
            warnings.append("Persona compliance check passed")

    # Check no speculation constraint
    constraints = capsule.get("constraints", {})
    if constraints.get("no_speculation", False):
        if _has_speculation(response):
            errors.append("Response contains speculation")
            passed = False

    # Check no hallucination constraint
    if constraints.get("no_hallucination", False):
        if _has_hallucination(response):
            errors.append("Response contains unsubstantiated claims")
            passed = False

    # Check citation requirement
    if constraints.get("cite_sources", False):
        if not _has_citations(response):
            warnings.append("Response lacks citations")

    # Check trust threshold
    λ = capsule.get("_trust", 1.0)
    if λ < trust_threshold:
        errors.append(f"Trust score {λ:.2f} below threshold {trust_threshold}")
        passed = False

    # Check containment
    containment = capsule.get("containment", {})
    if containment.get("read_only", False):
        if _contains_write_operations(response):
            errors.append("Response contains write operations in read-only mode")
            passed = False

    # Generate audit trail
    audit_trail = {
        "validation_id": f"val-{datetime.utcnow().timestamp()}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "passed": passed,
        "errors": errors,
        "warnings": warnings,
        "λ": λ,
        "threshold": trust_threshold,
        "capsule_id": capsule.get("scp_id", "unknown"),
    }

    return {
        "valid": passed,
        "reasoning": "; ".join(errors) if errors else "All checks passed",
        "errors": errors,
        "warnings": warnings,
        "λ": λ,
        "audit_trail": audit_trail,
    }


def _check_persona(response: str, persona: str) -> bool:
    """Check if response matches the persona."""
    # Simple persona check
    persona_lower = persona.lower()
    response_lower = response.lower()

    # Check for persona keywords
    persona_keywords = ["terse", "direct", "no fluff", "concise", "brief"]
    if "terse" in persona_lower or "direct" in persona_lower:
        # Check if response is too verbose
        if len(response.split()) > 100:
            return False

    if "no fluff" in persona_lower:
        # Check for filler words
        filler_words = ["actually", "basically", "honestly", "literally", "really", "very"]
        filler_count = sum(1 for w in filler_words if w in response_lower)
        if filler_count > 3:
            return False

    return True


def _has_speculation(response: str) -> bool:
    """Check if response contains speculation."""
    speculation_patterns = [
        r"\b(maybe|perhaps|possibly|could be|might be|may be)\b",
        r"\b(i think|i believe|i guess|i suppose|in my opinion)\b",
        r"\b(probably|likely|unlikely|suggests|suggesting)\b",
    ]
    for pattern in speculation_patterns:
        if re.search(pattern, response, re.IGNORECASE):
            return True
    return False


def _has_hallucination(response: str) -> bool:
    """Check if response contains unsubstantiated claims."""
    # Heuristic: check for specific claims without sources
    # In production, would check against knowledge base
    hallucination_patterns = [
        r"\b(according to|per|based on) (common knowledge|popular belief|conventional wisdom)\b",
        r"\b(it is well known|everyone knows)\b",
    ]
    for pattern in hallucination_patterns:
        if re.search(pattern, response, re.IGNORECASE):
            return True
    return False


def _has_citations(response: str) -> bool:
    """Check if response contains citations."""
    citation_patterns = [
        r"\[[0-9]+\]",
        r"\(\w+,\s*\d{4}\)",
        r"(source|reference|cited from|based on)",
        r"according to [A-Z][a-z]+",
    ]
    for pattern in citation_patterns:
        if re.search(pattern, response, re.IGNORECASE):
            return True
    return False


def _contains_write_operations(response: str) -> bool:
    """Check if response contains write operations."""
    write_patterns = [
        r"\b(write|delete|update|insert|modify|create)\b",
        r"\b(save|store|persist|change|alter)\b",
    ]
    for pattern in write_patterns:
        if re.search(pattern, response, re.IGNORECASE):
            return True
    return False


# ============================================================
# CLI
# ============================================================

def main():
    """Test validation."""
    import argparse
    import sys
    import json

    parser = argparse.ArgumentParser(description="Keystone Gate — Validation")
    parser.add_argument("--response", "-r", type=str, help="Response to validate")
    parser.add_argument("--capsule", "-c", type=str, help="Capsule file")
    parser.add_argument("--threshold", "-t", type=float, default=0.85, help="Trust threshold")

    args = parser.parse_args()

    if args.capsule and args.response:
        with open(args.capsule, "r") as f:
            capsule = json.load(f)

        result = validate_against_capsule(args.response, capsule, args.threshold)

        print(f"📊 Validation Result")
        print("=" * 60)
        print(f"  Valid: {result['valid']}")
        print(f"  λ: {result.get('λ', 0.0):.3f}")
        print(f"\n  Reasoning: {result.get('reasoning', '')}")
        if result.get('errors'):
            print(f"\n  Errors:")
            for e in result['errors']:
                print(f"    ❌ {e}")
        if result.get('warnings'):
            print(f"\n  Warnings:")
            for w in result['warnings']:
                print(f"    ⚠️ {w}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()