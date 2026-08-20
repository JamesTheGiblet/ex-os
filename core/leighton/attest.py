#!/usr/bin/env python3
"""
Leighton Weight — Attestation

Attestations fill the "observe outcomes" arrow in the Leighton Loop.

Attestations are signed ledger events (event.attestation.issued)
recording a judgement on a past event, hash-linked to it.

Usage:
    from core.leighton.attest import process_attestation, Attestation
"""

import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime


class Attestation:
    """
    An attestation — a signed judgement on a past event.
    """

    def __init__(
        self,
        target_event_id: str,
        attester: str,
        outcome: str,
        confidence: float = 1.0,
        evidence_mass: float = 1.0,
        message: str = "",
    ):
        """
        Initialise an attestation.

        Args:
            target_event_id: ID of the event being judged
            attester: who made the attestation
            outcome: "success", "failure", "partial", "neutral"
            confidence: Confidence in the judgement (0.0-1.0)
            evidence_mass: Strength of evidence
            message: Optional message
        """
        self.target_event_id = target_event_id
        self.attester = attester
        self.outcome = outcome
        self.confidence = confidence
        self.evidence_mass = evidence_mass
        self.message = message
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.attestation_id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate a unique attestation ID."""
        data = f"{self.target_event_id}:{self.attester}:{self.outcome}:{self.timestamp}"
        return f"attest-{hashlib.sha256(data.encode()).hexdigest()[:12]}"

    def to_dict(self) -> Dict[str, Any]:
        """Export attestation as dict."""
        return {
            "attestation_id": self.attestation_id,
            "target_event_id": self.target_event_id,
            "attester": self.attester,
            "outcome": self.outcome,
            "confidence": self.confidence,
            "evidence_mass": self.evidence_mass,
            "message": self.message,
            "timestamp": self.timestamp,
        }

    def to_json(self, indent: int = 2) -> str:
        """Export attestation as JSON."""
        return json.dumps(self.to_dict(), indent=indent)


def process_attestation(
    attestation: Attestation,
    target_λ: float,
    attester_λ: float,
    decay_k: float = 0.01,
) -> float:
    """
    Process an attestation and update trust.

    This implements the "observe outcomes" arrow in the Leighton Loop.

    Args:
        attestation: The attestation
        target_λ: Current λ of the target entity
        attester_λ: Current λ of the attester
        decay_k: Decay constant

    Returns:
        Updated λ for the target entity
    """
    # Apply decay
    from .decay import neutral_attractor
    decayed_λ = neutral_attractor(target_λ, decay_k, 0.001)  # Small decay

    # Process outcome
    outcome = attestation.outcome
    confidence = attestation.confidence
    evidence_mass = attestation.evidence_mass

    # Weighted by attester's λ
    attester_weight = attester_λ / 2.0  # Normalise 0-1

    if outcome == "success":
        # Positive outcome — increase trust
        remaining = 2.00 - decayed_λ
        step = 0.10 * remaining * attester_weight * confidence * evidence_mass
        return min(2.00, decayed_λ + step)

    elif outcome == "failure":
        # Negative outcome — decrease trust
        remaining = decayed_λ - 0.00
        step = 0.10 * remaining * attester_weight * confidence * evidence_mass
        return max(0.00, decayed_λ - step)

    elif outcome == "partial":
        # Mixed outcome — small adjustment
        if decayed_λ < 1.00:
            return min(1.00, decayed_λ + 0.02 * attester_weight)
        else:
            return max(1.00, decayed_λ - 0.02 * attester_weight)

    else:  # neutral
        return decayed_λ


def record_attestation(
    target_event_id: str,
    attester: str,
    outcome: str,
    confidence: float = 1.0,
    evidence_mass: float = 1.0,
    message: str = "",
) -> Attestation:
    """
    Create and record an attestation.

    Args:
        target_event_id: ID of the event being judged
        attester: who made the attestation
        outcome: "success", "failure", "partial", "neutral"
        confidence: Confidence in the judgement
        evidence_mass: Strength of evidence
        message: Optional message

    Returns:
        The attestation
    """
    attestation = Attestation(
        target_event_id=target_event_id,
        attester=attester,
        outcome=outcome,
        confidence=confidence,
        evidence_mass=evidence_mass,
        message=message,
    )

    # In production, would store in ChronoSCRIBE
    # For now, just return

    return attestation


# ============================================================
# CLI
# ============================================================

def main():
    """Test attestation."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Leighton Weight — Attestation")
    parser.add_argument("--target-event", "-t", type=str, required=True, help="Target event ID")
    parser.add_argument("--attester", "-a", type=str, default="system", help="Attester")
    parser.add_argument("--outcome", "-o", type=str, choices=["success", "failure", "partial", "neutral"],
                        default="success", help="Outcome")
    parser.add_argument("--confidence", "-c", type=float, default=1.0, help="Confidence")
    parser.add_argument("--evidence", "-e", type=float, default=1.0, help="Evidence mass")
    parser.add_argument("--target-λ", type=float, default=1.00, help="Target's current λ")
    parser.add_argument("--attester-λ", type=float, default=1.00, help="Attester's λ")

    args = parser.parse_args()

    # Create attestation
    attestation = record_attestation(
        target_event_id=args.target_event,
        attester=args.attester,
        outcome=args.outcome,
        confidence=args.confidence,
        evidence_mass=args.evidence,
    )

    print("📝 Attestation created:")
    print(f"   ID: {attestation.attestation_id}")
    print(f"   Target: {attestation.target_event_id}")
    print(f"   Outcome: {attestation.outcome}")

    # Process attestation
    updated_λ = process_attestation(
        attestation=attestation,
        target_λ=args.target_λ,
        attester_λ=args.attester_λ,
    )

    print(f"\n📊 Trust updated:")
    print(f"   Previous λ: {args.target_λ:.3f}")
    print(f"   Updated λ: {updated_λ:.3f}")
    print(f"   Change: {updated_λ - args.target_λ:+.3f}")


if __name__ == "__main__":
    main()