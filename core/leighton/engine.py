#!/usr/bin/env python3
"""
Leighton Weight Engine — λ Computation

Computes λ (Leighton Weight) — a trust score between 0.00 and 2.00.

λ is never stored. It's computed on-the-fly from an observation stream.

Formula:
    λ(t) = 1.00 + (λ₀ − 1.00) × e^(−kt)

Where:
    k = decay constant (per-domain)
    λ₀ = initial trust score (1.00 for new entities)
    t = time since last observation

Usage:
    from core.leighton.engine import compute_lambda

    λ = compute_lambda("entity-001", domain="system")
    print(f"Trust score: {λ:.2f}")
"""

import json
import os
import math
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path

# Default parameters
DEFAULT_K = 0.01
DEFAULT_BETA_PLUS = 0.10
DEFAULT_RHO = 2.0
DEFAULT_SIGMA = 3.0

# Trust status thresholds
TRUST_STATUS = {
    "REFLEX": (1.80, 2.00, "Highly trusted — automatic"),
    "VALIDATED": (1.00, 1.79, "Trusted — verified"),
    "QUESTIONABLE": (0.60, 0.99, "Skepticism required"),
    "QUARANTINED": (0.00, 0.59, "Do not use"),
}


class LeightonEngine:
    """
    Leighton Weight Engine — computes λ from observation streams.
    """

    def __init__(
        self,
        observations_dir: str = "observations",
        k: float = DEFAULT_K,
        beta_plus: float = DEFAULT_BETA_PLUS,
        rho: float = DEFAULT_RHO,
        sigma: float = DEFAULT_SIGMA,
    ):
        """
        Initialise the Leighton Weight Engine.

        Args:
            observations_dir: Directory containing observation streams
            k: Decay constant (per-domain)
            beta_plus: Upward step size
            rho: Asymmetry ratio (β₋ = ρ × β₊)
            sigma: Evidence mass threshold
        """
        self.observations_dir = Path(observations_dir)
        self.k = k
        self.beta_plus = beta_plus
        self.rho = rho
        self.sigma = sigma
        self.observations_dir.mkdir(parents=True, exist_ok=True)

    def compute(self, entity_id: str, domain: str = "default") -> float:
        """
        Compute λ for an entity.

        Args:
            entity_id: Entity ID
            domain: Domain for decay context

        Returns:
            λ (0.00-2.00)
        """
        # Load observations
        observations = self._load_observations(entity_id, domain)

        if not observations:
            return 1.00  # Neutral initial

        # Sort by timestamp
        observations.sort(key=lambda x: x.get("ts", ""))

        # Start with neutral
        λ = 1.00
        last_time = None

        for obs in observations:
            # Apply decay from last event
            if last_time is not None:
                time_diff = self._time_diff(last_time, obs.get("ts", ""))
                λ = self._decay(λ, time_diff)

            # Apply update
            outcome = obs.get("outcome", "neutral")
            attester = obs.get("attester", "unknown")
            attester_λ = obs.get("attester_λ", 1.00)
            evidence_mass = obs.get("evidence_mass", 1)

            λ = self._update(λ, outcome, attester_λ, evidence_mass)

            # Clamp
            λ = max(0.00, min(2.00, λ))

            last_time = obs.get("ts", "")

        # Apply final decay to current time
        if last_time is not None:
            time_diff = self._time_diff(last_time, datetime.utcnow().isoformat() + "Z")
            λ = self._decay(λ, time_diff)
            λ = max(0.00, min(2.00, λ))

        return λ

    def _decay(self, λ: float, time_diff: float) -> float:
        """
        Apply neutral-attractor decay.

        λ(t) = 1.00 + (λ₀ − 1.00) × e^(−kt)
        """
        if time_diff <= 0:
            return λ

        return 1.00 + (λ - 1.00) * math.exp(-self.k * time_diff)

    def _update(
        self,
        λ: float,
        outcome: str,
        attester_λ: float,
        evidence_mass: float,
    ) -> float:
        """
        Apply update based on outcome.

        Update rule:
        - λ-weighted increment
        - Asymmetric step size (β₋ = ρ × β₊)
        - Fraction-of-remaining-distance to relevant bound
        """
        # Determine step size
        if outcome in ["success", "positive"]:
            # Upward movement
            remaining = 2.00 - λ
            step = self.beta_plus * remaining * attester_λ * evidence_mass / self.sigma
            return λ + step

        elif outcome in ["failure", "negative"]:
            # Downward movement (asymmetric: β₋ = ρ × β₊)
            remaining = λ - 0.00
            step = (self.rho * self.beta_plus) * remaining * attester_λ * evidence_mass / self.sigma
            return λ - step

        elif outcome in ["partial", "neutral"]:
            # Small adjustment
            step = (self.beta_plus * 0.5) * attester_λ * evidence_mass / self.sigma
            return λ + (step if λ < 1.00 else -step)

        else:
            return λ

    def _time_diff(self, start: str, end: str) -> float:
        """Calculate time difference in days."""
        try:
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
            diff = (end_dt - start_dt).total_seconds()
            return diff / 86400.0  # Convert to days
        except (ValueError, TypeError):
            return 0.0

    def _load_observations(self, entity_id: str, domain: str) -> List[Dict[str, Any]]:
        """Load observations for an entity."""
        obs_file = self.observations_dir / domain / f"{entity_id}.jsonl"

        if not obs_file.exists():
            return []

        observations = []
        with open(obs_file, "r") as f:
            for line in f:
                try:
                    observations.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        return observations

    def record_observation(
        self,
        entity_id: str,
        outcome: str,
        attester: str = "system",
        attester_λ: float = 1.00,
        evidence_mass: float = 1.0,
        domain: str = "default",
        metadata: Optional[Dict] = None,
    ):
        """
        Record an observation for an entity.

        Args:
            entity_id: Entity ID
            outcome: "success", "failure", "partial", "neutral"
            attester: Who made the attestation
            attester_λ: Trust score of the attester
            evidence_mass: Strength of evidence (n)
            domain: Domain for decay context
            metadata: Additional data
        """
        observation = {
            "entity_id": entity_id,
            "outcome": outcome,
            "attester": attester,
            "attester_λ": attester_λ,
            "evidence_mass": evidence_mass,
            "metadata": metadata or {},
            "ts": datetime.utcnow().isoformat() + "Z",
        }

        # Ensure directory exists
        obs_dir = self.observations_dir / domain
        obs_dir.mkdir(parents=True, exist_ok=True)

        # Append to observation stream
        obs_file = obs_dir / f"{entity_id}.jsonl"
        with open(obs_file, "a") as f:
            f.write(json.dumps(observation) + "\n")

    def get_status(self, entity_id: str, domain: str = "default") -> Dict[str, Any]:
        """
        Get full trust status for an entity.

        Args:
            entity_id: Entity ID
            domain: Domain for decay context

        Returns:
            Status dict with λ, tier, status, and evidence_mass
        """
        λ = self.compute(entity_id, domain)

        # Get status label
        status = "UNKNOWN"
        for label, (low, high, description) in TRUST_STATUS.items():
            if low <= λ <= high:
                status = label
                break

        # Count observations
        observations = self._load_observations(entity_id, domain)
        evidence_mass = sum(obs.get("evidence_mass", 1) for obs in observations)

        return {
            "entity_id": entity_id,
            "λ": round(λ, 3),
            "status": status,
            "evidence_mass": evidence_mass,
            "domain": domain,
            "observations": len(observations),
        }


def compute_lambda(entity_id: str, domain: str = "default", observations_dir: str = "observations") -> float:
    """
    Convenience function to compute λ.

    Args:
        entity_id: Entity ID
        domain: Domain for decay context
        observations_dir: Directory containing observations

    Returns:
        λ (0.00-2.00)
    """
    engine = LeightonEngine(observations_dir)
    return engine.compute(entity_id, domain)


def get_trust_status(entity_id: str, domain: str = "default", observations_dir: str = "observations") -> Dict[str, Any]:
    """
    Convenience function to get trust status.

    Args:
        entity_id: Entity ID
        domain: Domain for decay context
        observations_dir: Directory containing observations

    Returns:
        Status dict
    """
    engine = LeightonEngine(observations_dir)
    return engine.get_status(entity_id, domain)


# ============================================================
# CLI
# ============================================================

def main():
    """Test Leighton Weight Engine."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Leighton Weight Engine")
    parser.add_argument("entity", type=str, help="Entity ID")
    parser.add_argument("--domain", "-d", type=str, default="default", help="Domain")
    parser.add_argument("--record", "-r", type=str, choices=["success", "failure", "partial", "neutral"],
                        help="Record an observation")
    parser.add_argument("--attester", "-a", type=str, default="system", help="Attester")
    parser.add_argument("--attester-λ", type=float, default=1.00, help="Attester's λ")
    parser.add_argument("--evidence", "-e", type=float, default=1.0, help="Evidence mass")
    parser.add_argument("--status", "-s", action="store_true", help="Show status")

    args = parser.parse_args()

    engine = LeightonEngine()

    if args.record:
        print(f"📝 Recording observation: {args.entity} → {args.record}")
        engine.record_observation(
            entity_id=args.entity,
            outcome=args.record,
            attester=args.attester,
            attester_λ=args.attester_λ,
            evidence_mass=args.evidence,
            domain=args.domain,
        )
        print(f"✅ Recorded")

    if args.status:
        status = engine.get_status(args.entity, args.domain)

        print(f"📊 Leighton Weight Status: {args.entity}")
        print("=" * 60)
        print(f"   λ: {status['λ']:.3f}")
        print(f"   Status: {status['status']}")
        print(f"   Evidence mass: {status['evidence_mass']}")
        print(f"   Observations: {status['observations']}")
        print(f"   Domain: {status['domain']}")


if __name__ == "__main__":
    main()