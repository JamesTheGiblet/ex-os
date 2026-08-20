#!/usr/bin/env python3
"""
HAL — Tiers

Tier definitions for HAL.

Tiers 1-5 mapped to λ thresholds:
- Tier 1: λ ≥ 1.00
- Tier 2: λ ≥ 1.20
- Tier 3: λ ≥ 1.40
- Tier 4: λ ≥ 1.60
- Tier 5: λ ≥ 1.80

Quarantine: λ < 0.60

Usage:
    from core.hal.tiers import TIERS, get_tier_for_lambda
"""

from typing import Dict, Any, Optional

# Tier definitions
TIERS = {
    1: {
        "name": "Observable",
        "min_λ": 1.00,
        "description": "Read-only operations, observation, reporting",
        "consequence": "No state change",
    },
    2: {
        "name": "Informational",
        "min_λ": 1.20,
        "description": "Warnings, notifications, non-critical alerts",
        "consequence": "State change visible to user",
    },
    3: {
        "name": "Advisory",
        "min_λ": 1.40,
        "description": "Recommendations, suggestions, config changes",
        "consequence": "Recommended action logged",
    },
    4: {
        "name": "Authoritative",
        "min_λ": 1.60,
        "description": "System changes, deployments, updates",
        "consequence": "System state modified",
    },
    5: {
        "name": "Consequential",
        "min_λ": 1.80,
        "description": "Physical actions, irreversible changes, deployments to hardware",
        "consequence": "Irreversible physical action",
    },
}

# Quarantine threshold
QUARANTINE_THRESHOLD = 0.60

# Reflex threshold
REFLEX_THRESHOLD = 1.80


def get_tier_for_lambda(λ: float) -> Optional[int]:
    """
    Get the highest tier a λ qualifies for.

    Args:
        λ: Leighton Weight score

    Returns:
        Tier number (1-5) or None if quarantined
    """
    if λ < QUARANTINE_THRESHOLD:
        return None

    if λ >= 1.80:
        return 5
    elif λ >= 1.60:
        return 4
    elif λ >= 1.40:
        return 3
    elif λ >= 1.20:
        return 2
    elif λ >= 1.00:
        return 1
    else:
        return None


def get_lambda_for_tier(tier: int) -> float:
    """
    Get the minimum λ required for a tier.

    Args:
        tier: Tier number (1-5)

    Returns:
        Minimum λ for the tier
    """
    if tier in TIERS:
        return TIERS[tier]["min_λ"]
    return 0.0


def is_quarantined(λ: float) -> bool:
    """
    Check if a λ is quarantined.

    Args:
        λ: Leighton Weight score

    Returns:
        True if quarantined
    """
    return λ < QUARANTINE_THRESHOLD


def is_reflex(λ: float) -> bool:
    """
    Check if a λ is a reflex (highly trusted).

    Args:
        λ: Leighton Weight score

    Returns:
        True if reflex
    """
    return λ >= REFLEX_THRESHOLD


def get_tier_name(tier: int) -> str:
    """Get the name of a tier."""
    if tier in TIERS:
        return TIERS[tier]["name"]
    return "Unknown"


def get_tier_description(tier: int) -> str:
    """Get the description of a tier."""
    if tier in TIERS:
        return TIERS[tier]["description"]
    return ""


def get_tier_consequence(tier: int) -> str:
    """Get the consequence of a tier."""
    if tier in TIERS:
        return TIERS[tier]["consequence"]
    return ""


# ============================================================
# CLI
# ============================================================

def main():
    """Display tier information."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="HAL — Tiers")
    parser.add_argument("--λ", "-l", type=float, help="Check tier for λ value")
    parser.add_argument("--list", action="store_true", help="List all tiers")

    args = parser.parse_args()

    if args.list:
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

    elif args.λ is not None:
        tier = get_tier_for_lambda(args.λ)
        if tier is None:
            print(f"λ = {args.λ:.2f} → QUARANTINED (λ < {QUARANTINE_THRESHOLD})")
        else:
            print(f"λ = {args.λ:.2f} → Tier {tier}: {get_tier_name(tier)}")
            print(f"  {get_tier_description(tier)}")
            if is_reflex(args.λ):
                print("  ⚡ REFLEX")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()