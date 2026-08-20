#!/usr/bin/env python3
"""
Leighton Weight — CLI

Command-line interface for Leighton Weight Engine.

Usage:
    leighton compute entity-001 --domain system
    leighton record entity-001 --outcome success --attester system
    leighton status entity-001
    leighton attest --target-event event-123 --outcome success
    leighton decay --λ 1.50 --days 30 --k 0.01
"""

import sys
import json
import argparse
from pathlib import Path


def compute_command(entity: str, domain: str, observations_dir: str = "observations"):
    """Compute λ for an entity."""
    try:
        from .engine import compute_lambda

        λ = compute_lambda(entity, domain, observations_dir)
        print(f"📊 λ for {entity} ({domain}): {λ:.3f}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def record_command(
    entity: str,
    outcome: str,
    attester: str,
    attester_λ: float,
    evidence: float,
    domain: str,
    observations_dir: str = "observations",
):
    """Record an observation."""
    try:
        from .engine import LeightonEngine

        engine = LeightonEngine(observations_dir)

        engine.record_observation(
            entity_id=entity,
            outcome=outcome,
            attester=attester,
            attester_λ=attester_λ,
            evidence_mass=evidence,
            domain=domain,
        )

        print(f"✅ Recorded: {entity} → {outcome}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def status_command(entity: str, domain: str, observations_dir: str = "observations"):
    """Get trust status for an entity."""
    try:
        from .engine import get_trust_status

        status = get_trust_status(entity, domain, observations_dir)

        print(f"📊 Trust Status: {entity}")
        print("=" * 60)
        print(f"   λ: {status['λ']:.3f}")
        print(f"   Status: {status['status']}")
        print(f"   Evidence mass: {status['evidence_mass']}")
        print(f"   Observations: {status['observations']}")
        print(f"   Domain: {status['domain']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def attest_command(
    target_event: str,
    attester: str,
    outcome: str,
    confidence: float,
    evidence: float,
    target_λ: float,
    attester_λ: float,
):
    """Create and process an attestation."""
    try:
        from .attest import record_attestation, process_attestation

        attestation = record_attestation(
            target_event_id=target_event,
            attester=attester,
            outcome=outcome,
            confidence=confidence,
            evidence_mass=evidence,
        )

        print(f"📝 Attestation: {attestation.attestation_id}")
        print(f"   Target: {attestation.target_event_id}")
        print(f"   Outcome: {attestation.outcome}")

        updated_λ = process_attestation(
            attestation=attestation,
            target_λ=target_λ,
            attester_λ=attester_λ,
        )

        print(f"\n📊 Trust updated:")
        print(f"   Previous λ: {target_λ:.3f}")
        print(f"   Updated λ: {updated_λ:.3f}")
        print(f"   Change: {updated_λ - target_λ:+.3f}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def decay_command(λ: float, days: float, k: float, asymmetric: bool):
    """Test decay function."""
    try:
        from .decay import neutral_attractor, asymmetric_decay

        if asymmetric:
            decayed = asymmetric_decay(λ, k, days, 1.5)
            print(f"Asymmetric decay:")
        else:
            decayed = neutral_attractor(λ, k, days)
            print(f"Neutral-attractor decay:")

        print(f"  Initial λ: {λ:.3f}")
        print(f"  Days: {days}")
        print(f"  k: {k}")
        print(f"  Decayed λ: {decayed:.3f}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Leighton Weight Engine — Trust Scoring",
        prog="leighton"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Compute command
    compute_parser = subparsers.add_parser("compute", help="Compute λ")
    compute_parser.add_argument("entity", type=str, help="Entity ID")
    compute_parser.add_argument("--domain", "-d", type=str, default="default", help="Domain")
    compute_parser.add_argument("--observations", "-o", type=str, default="observations", help="Observations dir")

    # Record command
    record_parser = subparsers.add_parser("record", help="Record an observation")
    record_parser.add_argument("entity", type=str, help="Entity ID")
    record_parser.add_argument("--outcome", "-r", type=str, choices=["success", "failure", "partial", "neutral"],
                               required=True, help="Outcome")
    record_parser.add_argument("--attester", "-a", type=str, default="system", help="Attester")
    record_parser.add_argument("--attester-λ", type=float, default=1.00, help="Attester's λ")
    record_parser.add_argument("--evidence", "-e", type=float, default=1.0, help="Evidence mass")
    record_parser.add_argument("--domain", "-d", type=str, default="default", help="Domain")
    record_parser.add_argument("--observations", "-o", type=str, default="observations", help="Observations dir")

    # Status command
    status_parser = subparsers.add_parser("status", help="Get trust status")
    status_parser.add_argument("entity", type=str, help="Entity ID")
    status_parser.add_argument("--domain", "-d", type=str, default="default", help="Domain")
    status_parser.add_argument("--observations", "-o", type=str, default="observations", help="Observations dir")

    # Attest command
    attest_parser = subparsers.add_parser("attest", help="Create and process attestation")
    attest_parser.add_argument("--target-event", "-t", type=str, required=True, help="Target event ID")
    attest_parser.add_argument("--attester", "-a", type=str, default="system", help="Attester")
    attest_parser.add_argument("--outcome", "-o", type=str, choices=["success", "failure", "partial", "neutral"],
                               default="success", help="Outcome")
    attest_parser.add_argument("--confidence", "-c", type=float, default=1.0, help="Confidence")
    attest_parser.add_argument("--evidence", "-e", type=float, default=1.0, help="Evidence mass")
    attest_parser.add_argument("--target-λ", type=float, default=1.00, help="Target's current λ")
    attest_parser.add_argument("--attester-λ", type=float, default=1.00, help="Attester's λ")

    # Decay command
    decay_parser = subparsers.add_parser("decay", help="Test decay function")
    decay_parser.add_argument("λ", type=float, help="Initial λ")
    decay_parser.add_argument("--days", "-d", type=float, default=30, help="Days elapsed")
    decay_parser.add_argument("--k", "-k", type=float, default=0.01, help="Decay constant")
    decay_parser.add_argument("--asymmetric", "-a", action="store_true", help="Use asymmetric decay")

    args = parser.parse_args()

    if args.command == "compute":
        compute_command(args.entity, args.domain, args.observations)
    elif args.command == "record":
        record_command(
            args.entity, args.outcome, args.attester, args.attester_λ,
            args.evidence, args.domain, args.observations
        )
    elif args.command == "status":
        status_command(args.entity, args.domain, args.observations)
    elif args.command == "attest":
        attest_command(
            args.target_event, args.attester, args.outcome,
            args.confidence, args.evidence,
            args.target_λ, args.attester_λ
        )
    elif args.command == "decay":
        decay_command(args.λ, args.days, args.k, args.asymmetric)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()