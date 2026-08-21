#!/usr/bin/env python3
"""
SCP — CLI

Command-line interface for SCP.

Usage:
    scp validate capsule.scp.json
    scp sign capsule.scp.json --key private.pem
    scp verify capsule.scp.json --key public.pem
    scp generate-key
    scp canonicalise capsule.scp.json
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional

# Allow `python core/scp/cli.py ...` as well as `python -m core.scp.cli ...`.
# Direct script execution has no parent package, so the relative imports
# below (`from .sign import ...`) fail with ImportError; fall back to the
# absolute package path once the repo root is on sys.path.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def validate_command(file_path: str):
    """Validate a capsule."""
    try:
        try:
            from .schema import validate_schema
        except ImportError:
            from core.scp.schema import validate_schema
        with open(file_path, "r") as f:
            capsule = json.load(f)

        validate_schema(capsule)
        print(f"✅ Valid SCP capsule: {capsule.get('scp_id', 'unknown')}")

    except Exception as e:
        print(f"❌ Invalid: {e}")
        sys.exit(1)


def sign_command(file_path: str, key_path: str, output: Optional[str] = None) -> None:
    """Sign a capsule."""
    try:
        try:
            from .sign import sign_capsule_file
        except ImportError:
            from core.scp.sign import sign_capsule_file
        output = sign_capsule_file(file_path, key_path, output)
        print(f"✅ Signed: {output}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def verify_command(file_path: str, key_path: Optional[str] = None) -> None:
    """Verify a capsule."""
    try:
        try:
            from .verify import verify_capsule
        except ImportError:
            from core.scp.verify import verify_capsule
        valid, message, capsule = verify_capsule(file_path, key_path)

        if valid and capsule is not None:
            print(f"✅ Verified: {capsule.get('scp_id', 'unknown')}")
            print(f"   {message}")
        else:
            print(f"❌ Failed: {message}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def generate_key_command(output: str = "forge-signing.pem"):
    """Generate a key pair."""
    try:
        try:
            from .sign import generate_key_pair
        except ImportError:
            from core.scp.sign import generate_key_pair
        generate_key_pair(output)
        print(f"✅ Key pair generated: {output}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def canonicalise_command(file_path: str):
    """Canonicalise a capsule."""
    try:
        try:
            from .canonicalise import canonicalise_json
        except ImportError:
            from core.scp.canonicalise import canonicalise_json
        with open(file_path, "r") as f:
            capsule = json.load(f)

        canonical = canonicalise_json(capsule)
        print(canonical)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SCP — Semantic Capsule Protocol",
        prog="scp"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a capsule")
    validate_parser.add_argument("file", type=str, help="Capsule file path")

    # Sign command
    sign_parser = subparsers.add_parser("sign", help="Sign a capsule")
    sign_parser.add_argument("file", type=str, help="Capsule file path")
    sign_parser.add_argument("--key", "-k", type=str, default="forge-signing.pem", help="Private key path")
    sign_parser.add_argument("--output", "-o", type=str, help="Output path")

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify a capsule")
    verify_parser.add_argument("file", type=str, help="Capsule file path")
    verify_parser.add_argument("--key", "-k", type=str, help="Public key path")

    # Generate key command
    genkey_parser = subparsers.add_parser("generate-key", help="Generate key pair")
    genkey_parser.add_argument("--output", "-o", type=str, default="forge-signing.pem", help="Output path")

    # Canonicalise command
    can_parser = subparsers.add_parser("canonicalise", help="Canonicalise a capsule")
    can_parser.add_argument("file", type=str, help="Capsule file path")

    args = parser.parse_args()

    if args.command == "validate":
        validate_command(args.file)
    elif args.command == "sign":
        sign_command(args.file, args.key, args.output)
    elif args.command == "verify":
        verify_command(args.file, args.key)
    elif args.command == "generate-key":
        generate_key_command(args.output)
    elif args.command == "canonicalise":
        canonicalise_command(args.file)
    else:
        parser.print_help()


if __name__ == "__main__":
    # Windows consoles default to a legacy codepage (e.g. cp1252) that can't
    # encode the emoji used in status messages above; force UTF-8 so a
    # successful operation doesn't crash on the confirmation print.
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    main()
