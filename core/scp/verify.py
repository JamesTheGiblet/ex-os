#!/usr/bin/env python3
"""
SCP — Signature Verification

Verifies Ed25519 signatures on SCP capsules.

Usage:
    from core.scp.verify import verify_signature, verify_capsule

    # Verify a signature
    valid = verify_signature(capsule, public_key)

    # Verify a capsule file
    valid = verify_capsule("capsule.scp.json")
"""

import json
import os
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.exceptions import InvalidSignature
    CRYPTO_AVAILABLE = True
except ImportError:
    # Keep optional dependency names defined for runtime and static analysis.
    serialization: Any = None
    ed25519: Any = None
    InvalidSignature: Any = None
    CRYPTO_AVAILABLE = False

from .canonicalise import canonicalise_json
from .schema import validate_schema


def verify_signature(
    capsule: Dict[str, Any],
    public_key_bytes: Optional[bytes] = None,
    public_key_path: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Verify an Ed25519 signature on a capsule.

    Args:
        capsule: Signed capsule dict
        public_key_bytes: Raw public key bytes
        public_key_path: Path to public key file

    Returns:
        (valid, message)
    """
    if not CRYPTO_AVAILABLE:
        return False, "cryptography module not installed"

    # Check signature exists
    signature_data = capsule.get("signature")
    if not isinstance(signature_data, dict):
        return False, "No signature found"

    # Check algorithm
    if signature_data.get("algorithm") != "Ed25519":
        return False, f"Unsupported algorithm: {signature_data.get('algorithm')}"

    # Get signature value
    signature_hex = signature_data.get("value")
    if not signature_hex:
        return False, "No signature value"

    try:
        signature = bytes.fromhex(signature_hex)
    except ValueError:
        return False, "Invalid signature hex"

    # Get public key
    if public_key_bytes is None and public_key_path is None:
        return False, "No public key provided"

    if public_key_path:
        with open(public_key_path, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())
            if not isinstance(public_key, ed25519.Ed25519PublicKey):
                return False, "Public key is not Ed25519"
            public_key_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )

    if public_key_bytes is None:
        return False, "No public key provided"

    # Create a copy without signature
    capsule_copy = capsule.copy()
    del capsule_copy["signature"]

    # Canonicalise
    canonical = canonicalise_json(capsule_copy)

    try:
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes[:32])
        public_key.verify(signature, canonical.encode('utf-8'))
        return True, "Signature verified"
    except InvalidSignature:
        return False, "Invalid signature"


def verify_capsule(
    file_path: str,
    public_key_path: Optional[str] = None,
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Verify a capsule file.

    Args:
        file_path: Path to capsule file
        public_key_path: Path to public key

    Returns:
        (valid, message, capsule)
    """
    try:
        with open(file_path, "r") as f:
            capsule = json.load(f)
    except Exception as e:
        return False, f"Failed to load capsule: {e}", None

    # Validate schema
    try:
        validate_schema(capsule)
    except ValueError as e:
        return False, f"Schema validation failed: {e}", capsule

    # Verify signature
    valid, message = verify_signature(capsule, public_key_path=public_key_path)

    return valid, message, capsule


def verify_sidecar(file_path: str, public_key_path: Optional[str] = None) -> Tuple[bool, str]:
    """
    Verify a .sig sidecar file.

    Args:
        file_path: Path to the original file
        public_key_path: Path to public key

    Returns:
        (valid, message)
    """
    if not CRYPTO_AVAILABLE:
        return False, "cryptography module not installed"

    sig_path = f"{file_path}.sig"
    if not os.path.exists(sig_path):
        return False, f"Sidecar not found: {sig_path}"

    try:
        with open(sig_path, "r") as f:
            sig_data = json.load(f)
    except Exception as e:
        return False, f"Failed to load sidecar: {e}"

    if not isinstance(sig_data, dict):
        return False, "Invalid sidecar format"

    # Get signature
    signature_hex = sig_data.get("value")
    if not signature_hex:
        return False, "No signature value in sidecar"

    try:
        signature = bytes.fromhex(signature_hex)
    except ValueError:
        return False, "Invalid signature hex"

    # Read original file
    try:
        with open(file_path, "rb") as f:
            data = f.read()
    except Exception as e:
        return False, f"Failed to read file: {e}"

    # Get public key
    if public_key_path:
        with open(public_key_path, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())
            if not isinstance(public_key, ed25519.Ed25519PublicKey):
                return False, "Public key is not Ed25519"
    else:
        # Try to get from sidecar key_id
        key_id = sig_data.get("key_id")
        if key_id:
            # In production, would fetch from key registry
            pass
        return False, "No public key provided"

    try:
        public_key.verify(signature, data)
        return True, "Sidecar verified"
    except InvalidSignature:
        return False, "Invalid sidecar signature"


# ============================================================
# CLI
# ============================================================

def main():
    """Test verification."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="SCP — Verification")
    parser.add_argument("file", type=str, help="Capsule file to verify")
    parser.add_argument("--key", "-k", type=str, help="Public key path")

    args = parser.parse_args()

    valid, message, capsule = verify_capsule(args.file, args.key)

    if valid and capsule is not None:
        print(f"✅ Verified: {capsule.get('scp_id', 'unknown')}")
        print(f"   {message}")
    else:
        print(f"❌ Failed: {message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
