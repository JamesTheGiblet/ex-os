#!/usr/bin/env python3
"""
DataCube — Cube

A cube is DataCube's artefact. It represents a classified claim.

Features:
- Five lenses (16% each)
- Human validation (20%)
- Self-filling via neighbourhood-router
- Completeness gates trust

Usage:
    from core.datacube.cube import Cube, create_cube

    cube = create_cube(
        claim="Ohm's Law: V = IR",
        namespace="domain.electronics",
        lens="FACT"
    )
"""

import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime

from .lenses import LENSES, LENS_NAMES, is_valid_lens


LENS_COMPLETENESS = 0.16  # 16% per lens
HUMAN_VALIDATION_WEIGHT = 0.20  # 20% final validation
MAX_COMPLETENESS = 1.0


class Cube:
    """
    A cube — classified claim with lenses and self-filling.
    """

    def __init__(
        self,
        claim: str,
        namespace: str,
        lens: str = "UNKNOWN",
        metadata: Optional[Dict] = None,
        contradictory_cubes: Optional[List[str]] = None,
    ):
        """
        Initialise a cube.

        Args:
            claim: The claim being classified
            namespace: event.*, state.*, domain.*, behaviour.*
            lens: FACT, OPINION, FICTION, CONTEXT, UNKNOWN
            metadata: Additional metadata
            contradictory_cubes: List of cube IDs that contradict this cube
        """
        if not is_valid_lens(lens):
            raise ValueError(f"Invalid lens: {lens}")

        self.claim = claim
        self.namespace = namespace
        self.lens = lens
        self.metadata = metadata or {}
        self.contradictory_cubes = contradictory_cubes or []
        self.cube_id = self._generate_id()

        # Lens completeness (each starts at 0)
        self.lens_completeness = {l: 0.0 for l in LENS_NAMES}
        self.lens_completeness[lens] = LENS_COMPLETENESS

        # Human validation
        self.human_validated = False
        self.human_validator = None
        self.human_validation_timestamp = None

        self.created = datetime.utcnow().isoformat() + "Z"
        self.updated = self.created
        self._trust_eligible = False

    def _generate_id(self) -> str:
        """Generate a unique cube ID."""
        data = f"{self.claim}:{self.namespace}:{self.lens}:{datetime.utcnow().isoformat()}"
        return f"cube-{hashlib.sha256(data.encode()).hexdigest()[:16]}"

    def fill_lens(self, lens: str, weight: float = LENS_COMPLETENESS):
        """
        Fill a lens (self-filling).

        Args:
            lens: Lens name
            weight: Completeness weight (0.0-1.0)
        """
        if not is_valid_lens(lens):
            raise ValueError(f"Invalid lens: {lens}")

        if lens == self.lens:
            # Primary lens can be filled more
            self.lens_completeness[lens] = min(1.0, self.lens_completeness[lens] + weight * 0.5)
        else:
            self.lens_completeness[lens] = min(1.0, self.lens_completeness[lens] + weight)

        self.updated = datetime.utcnow().isoformat() + "Z"

    def fill_all_lenses(self):
        """Fill all lenses to 16% completeness."""
        for lens in LENS_NAMES:
            self.lens_completeness[lens] = LENS_COMPLETENESS
        self.updated = datetime.utcnow().isoformat() + "Z"

    def validate_human(self, validator: str):
        """Apply human validation (20% completeness)."""
        self.human_validated = True
        self.human_validator = validator
        self.human_validation_timestamp = datetime.utcnow().isoformat() + "Z"
        self.updated = self.human_validation_timestamp

    def get_completeness(self) -> float:
        """
        Get total completeness.

        Sum of lens completeness (5 × 16% = 80%) + human validation (20%)
        """
        lens_total = sum(self.lens_completeness.values())
        human_total = HUMAN_VALIDATION_WEIGHT if self.human_validated else 0.0
        return min(MAX_COMPLETENESS, lens_total + human_total)

    def is_fully_validated(self) -> bool:
        """Check if cube is fully validated (100% completeness)."""
        return self.get_completeness() >= MAX_COMPLETENESS

    def is_trust_eligible(self) -> bool:
        """Check if cube is eligible for Leighton Weight attestation."""
        return self.is_fully_validated() and self.human_validated

    def add_contradiction(self, cube_id: str):
        """Add a contradictory cube."""
        if cube_id not in self.contradictory_cubes and cube_id != self.cube_id:
            self.contradictory_cubes.append(cube_id)
            self.updated = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict[str, Any]:
        """Export cube as dict."""
        return {
            "cube_id": self.cube_id,
            "claim": self.claim,
            "namespace": self.namespace,
            "lens": self.lens,
            "lens_completeness": self.lens_completeness,
            "human_validated": self.human_validated,
            "human_validator": self.human_validator,
            "human_validation_timestamp": self.human_validation_timestamp,
            "contradictory_cubes": self.contradictory_cubes,
            "completeness": self.get_completeness(),
            "fully_validated": self.is_fully_validated(),
            "trust_eligible": self.is_trust_eligible(),
            "metadata": self.metadata,
            "created": self.created,
            "updated": self.updated,
        }

    def to_json(self, indent: int = 2) -> str:
        """Export cube as JSON."""
        return json.dumps(self.to_dict(), indent=indent)


def create_cube(
    claim: str,
    namespace: str,
    lens: str = "UNKNOWN",
    metadata: Optional[Dict] = None,
    contradictory_cubes: Optional[List[str]] = None,
) -> Cube:
    """
    Convenience function to create a cube.

    Args:
        claim: The claim being classified
        namespace: event.*, state.*, domain.*, behaviour.*
        lens: FACT, OPINION, FICTION, CONTEXT, UNKNOWN
        metadata: Additional metadata
        contradictory_cubes: List of contradictory cube IDs

    Returns:
        Cube instance
    """
    return Cube(claim, namespace, lens, metadata, contradictory_cubes)


def get_completeness(cube: Cube) -> float:
    """Get completeness of a cube."""
    return cube.get_completeness()


# ============================================================
# CLI
# ============================================================

def main():
    """Test cube creation."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="DataCube — Cube")
    parser.add_argument("--claim", "-c", type=str, required=True, help="Claim")
    parser.add_argument("--namespace", "-n", type=str, default="domain.general", help="Namespace")
    parser.add_argument("--lens", "-l", type=str, default="UNKNOWN", help="Lens")
    parser.add_argument("--validate", "-v", action="store_true", help="Apply human validation")

    args = parser.parse_args()

    cube = create_cube(args.claim, args.namespace, args.lens)

    print(f"📊 Cube created:")
    print(f"   ID: {cube.cube_id}")
    print(f"   Claim: {cube.claim}")
    print(f"   Lens: {cube.lens}")
    print(f"   Completeness: {cube.get_completeness():.2%}")

    if args.validate:
        cube.validate_human("cli")
        print(f"   ✅ Human validated")
        print(f"   Completeness: {cube.get_completeness():.2%}")
        print(f"   Trust eligible: {cube.is_trust_eligible()}")


if __name__ == "__main__":
    main()