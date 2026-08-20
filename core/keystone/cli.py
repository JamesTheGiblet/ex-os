#!/usr/bin/env python3
"""
Keystone Gate — CLI

Command-line interface for Keystone Gate.

Usage:
    keystone bind capsule.scp.json
    keystone validate "response" --capsule capsule.scp.json
    keystone generate "prompt" --capsule capsule.scp.json
    keystone adversarial "response" --capsule capsule.scp.json
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional


def bind_command(capsule_path: str, model: Optional[str] = None) -> None:
    """Bind to a capsule."""
    try:
        from .binding import bind_capsule

        binding = bind_capsule(capsule_path, model)

        print(f"✅ Bound to: {binding.scp_id}")
        print(f"   Persona: {binding.get_persona()}")
        print(f"   Min trust: {binding.get_min_trust()}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def validate_command(response: str, capsule_path: str, threshold: float):
    """Validate a response."""
    try:
        from .validate import validate_against_capsule
        import json

        with open(capsule_path, "r") as f:
            capsule = json.load(f)

        result = validate_against_capsule(response, capsule, threshold)

        print(f"📊 Validation Result")
        print("=" * 60)
        print(f"  Valid: {result['valid']}")
        print(f"  λ: {result.get('λ', 0.0):.3f}")
        print(f"\n  Reasoning: {result.get('reasoning', '')}")

        if result.get('errors'):
            print(f"\n  Errors:")
            for e in result['errors']:
                print(f"    ❌ {e}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def generate_command(
    prompt: str,
    capsule_path: str,
    model: Optional[str] = None,
    threshold: float = 0.85,
) -> None:
    """Generate a response with enforcement."""
    try:
        from .gate import KeystoneGate

        gate = KeystoneGate(trust_threshold=threshold)
        gate.bind(capsule_path, model)

        result = gate.generate(prompt)

        print(f"📝 Prompt: {prompt}")
        print("=" * 60)

        if result["valid"]:
            print(result["text"])
            print(f"\n✅ Validated (λ: {result.get('λ', 0.0):.3f})")
        else:
            print(f"❌ Blocked: {result.get('reasoning', '')}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def adversarial_command(response: str, capsule_path: str, iterations: int):
    """Run adversarial tests."""
    try:
        from .adversarial import run_adversarial_tests
        import json

        with open(capsule_path, "r") as f:
            capsule = json.load(f)

        result = run_adversarial_tests(response, capsule, iterations)

        print(f"🧪 Adversarial Test Results")
        print("=" * 60)
        print(f"  Passed: {result['passed']}")
        print(f"  Tests: {result['tests']}")
        print(f"  Confidence: {result['confidence']:.2%}")

        for r in result.get("results", []):
            emoji = "✅" if r["passed"] else "❌"
            print(f"\n  {emoji} {r['claim']}...")
            print(f"     {r['reasoning']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def status_command():
    """Show Gate status."""
    try:
        from .gate import KeystoneGate

        gate = KeystoneGate()
        status = gate.get_status()

        print(f"📊 Keystone Gate Status")
        print("=" * 60)
        for key, value in status.items():
            print(f"  {key}: {value}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Keystone Gate — The Enforcement Layer",
        prog="keystone"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Bind command
    bind_parser = subparsers.add_parser("bind", help="Bind to a capsule")
    bind_parser.add_argument("capsule", type=str, help="Capsule file")
    bind_parser.add_argument("--model", "-m", type=str, help="Model name")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a response")
    validate_parser.add_argument("response", type=str, help="Response text")
    validate_parser.add_argument("--capsule", "-c", type=str, required=True, help="Capsule file")
    validate_parser.add_argument("--threshold", "-t", type=float, default=0.85, help="Trust threshold")

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate with enforcement")
    generate_parser.add_argument("prompt", type=str, help="Prompt")
    generate_parser.add_argument("--capsule", "-c", type=str, required=True, help="Capsule file")
    generate_parser.add_argument("--model", "-m", type=str, help="Model name")
    generate_parser.add_argument("--threshold", "-t", type=float, default=0.85, help="Trust threshold")

    # Adversarial command
    adv_parser = subparsers.add_parser("adversarial", help="Run adversarial tests")
    adv_parser.add_argument("response", type=str, help="Response text")
    adv_parser.add_argument("--capsule", "-c", type=str, required=True, help="Capsule file")
    adv_parser.add_argument("--iterations", "-i", type=int, default=3, help="Iterations")

    # Status command
    subparsers.add_parser("status", help="Show Gate status")

    args = parser.parse_args()

    if args.command == "bind":
        bind_command(args.capsule, args.model)
    elif args.command == "validate":
        validate_command(args.response, args.capsule, args.threshold)
    elif args.command == "generate":
        generate_command(args.prompt, args.capsule, args.model, args.threshold)
    elif args.command == "adversarial":
        adversarial_command(args.response, args.capsule, args.iterations)
    elif args.command == "status":
        status_command()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
