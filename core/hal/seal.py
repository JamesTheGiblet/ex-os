#!/usr/bin/env python3
"""
HAL — Seal

The seal is HAL's artefact. It authorises actions based on trust.

Features:
- Requires verified authoriser-score-file
- No manual λ entry
- Refuses to seal if λ insufficient for tier
- Records seal in ChronoSCRIBE

Usage:
    from core.hal.seal import seal

    result = seal(
        action="DEPLOY",
        authoriser="did:key:z6MktudRY5LBZJeE13BiF4BeisAwWs7gvg6srh2GwLAMKDwJ",
        tier=3,
        score_file="scores/trusted.json"
    )
"""

import json
import os
import hashlib
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

from .tiers import TIERS, get_lambda_for_tier, get_tier_for_lambda, is_quarantined
from .verify import verify_score_file, load_score_file


class Seal:
    """
    HAL seal — an authorised action.
    """

    def __init__(
        self,
        action: str,
        authoriser: str,
        tier: int,
        λ: float,
        separation: str = "none",
        description: str = "",
    ):
        """
        Initialise a seal.

        Args:
            action: The action being sealed
            authoriser: did:key of the authoriser
            tier: Tier (1-5)
            λ: Trust score of the authoriser
            separation: "none" or "verified"
            description: Optional description
        """
        self.action = action
        self.authoriser = authoriser
        self.tier = tier
        self.λ = λ
        self.separation = separation
        self.description = description
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.seal_id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate a unique seal ID."""
        data = f"{self.action}:{self.authoriser}:{self.tier}:{self.λ}:{self.timestamp}"
        return f"seal-{hashlib.sha256(data.encode()).hexdigest()[:12]}"

    def to_dict(self) -> Dict[str, Any]:
        """Export seal as dict."""
        return {
            "seal_id": self.seal_id,
            "action": self.action,
            "authoriser": self.authoriser,
            "tier": self.tier,
            "λ": self.λ,
            "separation": self.separation,
            "description": self.description,
            "timestamp": self.timestamp,
            "status": "active",
        }

    def to_json(self, indent: int = 2) -> str:
        """Export seal as JSON."""
        return json.dumps(self.to_dict(), indent=indent)

    def save(self, output_dir: str = "seals"):
        """Save seal to file."""
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{self.seal_id}.json")
        with open(file_path, "w") as f:
            f.write(self.to_json())
        return file_path


def seal(
    action: str,
    authoriser: str,
    tier: int,
    score_file: str,
    description: str = "",
    separation: str = "none",
) -> Dict[str, Any]:
    """
    Seal an action.

    Args:
        action: Action to seal
        authoriser: did:key of the authoriser
        tier: Tier (1-5)
        score_file: Path to verified score file
        description: Optional description
        separation: "none" or "verified"

    Returns:
        Result dict with status and seal data
    """
    # Validate tier
    if tier not in TIERS:
        return {
            "status": "error",
            "message": f"Invalid tier: {tier}. Must be 1-5",
            "seal": None,
        }

    # Load and verify score file
    try:
        score_data = load_score_file(score_file)
        valid, message = verify_score_file(score_data)
        if not valid:
            return {
                "status": "error",
                "message": f"Invalid score file: {message}",
                "seal": None,
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to load score file: {e}",
            "seal": None,
        }

    # Get λ from score file
    λ = score_data.get("λ", 0.0)

    # Check quarantine
    if is_quarantined(λ):
        return {
            "status": "refused",
            "message": f"Quarantine: λ={λ:.2f} < 0.60",
            "seal": None,
            "λ": λ,
        }

    # Check tier requirement
    tier_lambda = get_lambda_for_tier(tier)
    if λ < tier_lambda:
        return {
            "status": "refused",
            "message": f"Insufficient trust: λ={λ:.2f} < {tier_lambda:.2f} (required for tier {tier})",
            "seal": None,
            "λ": λ,
            "required": tier_lambda,
        }

    # Create seal
    seal_obj = Seal(
        action=action,
        authoriser=authoriser,
        tier=tier,
        λ=λ,
        separation=separation,
        description=description,
    )

    # Save seal
    seal_path = seal_obj.save()

    # Record in ChronoSCRIBE (if available)
    try:
        from core.chronoscribe.ledger import append_entry
        append_entry(
            consumer="hal",
            event="event.hal.seal",
            source="hal",
            payload=seal_obj.to_dict(),
        )
    except (ImportError, AttributeError):
        # ChronoSCRIBE not available — log to file
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "seals.log")
        with open(log_path, "a") as f:
            f.write(json.dumps({"event": "event.hal.seal", "payload": seal_obj.to_dict()}) + "\n")

    return {
        "status": "sealed",
        "message": f"Action '{action}' sealed with tier {tier}",
        "seal": seal_obj.to_dict(),
        "λ": λ,
        "seal_path": seal_path,
    }


def seal_from_file(
    seal_file: str,
    action: Optional[str] = None,
    tier: Optional[int] = None,
    description: str = "",
) -> Dict[str, Any]:
    """
    Create a seal from a score file.

    Args:
        seal_file: Path to score file
        action: Action to seal (overrides score file)
        tier: Tier (overrides score file)
        description: Optional description

    Returns:
        Result dict
    """
    try:
        with open(seal_file, "r") as f:
            data = json.load(f)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to load seal file: {e}",
            "seal": None,
        }

    action_value = action if action is not None else data.get("action", "UNKNOWN")
    tier_value = tier if tier is not None else data.get("tier", 3)
    authoriser = data.get("authoriser", "unknown")

    if not isinstance(action_value, str):
        return {"status": "error", "message": "Invalid action in seal file", "seal": None}
    if not isinstance(tier_value, int):
        return {"status": "error", "message": "Invalid tier in seal file", "seal": None}
    if not isinstance(authoriser, str):
        return {"status": "error", "message": "Invalid authoriser in seal file", "seal": None}

    return seal(
        action=action_value,
        authoriser=authoriser,
        tier=tier_value,
        score_file=seal_file,
        description=description,
    )


def get_seal(seal_id: str, seal_dir: str = "seals") -> Optional[Dict[str, Any]]:
    """
    Get a seal by ID.

    Args:
        seal_id: Seal ID
        seal_dir: Directory containing seals

    Returns:
        Seal dict or None
    """
    file_path = os.path.join(seal_dir, f"{seal_id}.json")
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r") as f:
        return json.load(f)


def list_seals(seal_dir: str = "seals", limit: int = 20) -> list:
    """
    List all seals.

    Args:
        seal_dir: Directory containing seals
        limit: Maximum number of seals

    Returns:
        List of seal dicts
    """
    if not os.path.exists(seal_dir):
        return []

    seals = []
    for file_path in sorted(Path(seal_dir).glob("*.json"), reverse=True):
        try:
            with open(file_path, "r") as f:
                seals.append(json.load(f))
        except (json.JSONDecodeError, OSError):
            continue

    return seals[:limit]


# ============================================================
# CLI
# ============================================================

def main():
    """Test sealing."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="HAL — Seal")
    parser.add_argument("--action", "-a", type=str, required=True, help="Action to seal")
    parser.add_argument("--authoriser", "-i", type=str, required=True, help="Authoriser did:key")
    parser.add_argument("--tier", "-t", type=int, default=3, help="Tier (1-5)")
    parser.add_argument("--score", "-s", type=str, required=True, help="Score file path")
    parser.add_argument("--description", "-d", type=str, help="Description")
    parser.add_argument("--list", "-l", action="store_true", help="List seals")
    parser.add_argument("--get", "-g", type=str, help="Get seal by ID")

    args = parser.parse_args()

    if args.list:
        print("📋 HAL Seals")
        print("=" * 60)
        seals = list_seals()
        for s in seals:
            print(f"  {s.get('seal_id', 'unknown')} — {s.get('action', 'unknown')} (tier {s.get('tier', '?')})")
        print(f"\nTotal: {len(seals)}")
        return

    if args.get:
        seal_data = get_seal(args.get)
        if seal_data:
            print(f"🔏 Seal: {args.get}")
            print("=" * 60)
            print(json.dumps(seal_data, indent=2))
        else:
            print(f"❌ Seal not found: {args.get}")
            sys.exit(1)
        return

    # Create seal
    print(f"🔏 HAL — Sealing Action")
    print("=" * 60)
    print(f"   Action: {args.action}")
    print(f"   Tier: {args.tier}")
    print(f"   Authoriser: {args.authoriser}")
    print(f"   Score file: {args.score}")

    result = seal(
        action=args.action,
        authoriser=args.authoriser,
        tier=args.tier,
        score_file=args.score,
        description=args.description or "",
    )

    print("\n📊 Result:")
    print(f"   Status: {result['status']}")
    print(f"   Message: {result.get('message', '')}")
    if result.get('seal'):
        print(f"   Seal ID: {result['seal']['seal_id']}")
        print(f"   λ: {result['seal']['λ']:.2f}")
        print(f"   Timestamp: {result['seal']['timestamp']}")


if __name__ == "__main__":
    main()
