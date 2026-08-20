#!/usr/bin/env python3
"""
SCP — Ed25519 Signing

Deterministic Ed25519 signing for SCP capsules.

Features:
- Ed25519 deterministic signing
- Canonicalised JSON signing
- Detached .sig sidecars for non-JSON artefacts
- Key management

Usage:
    from core.scp.sign import sign_capsule, sign_capsule_file

    # Sign a capsule dict
    signed = sign_capsule(capsule, private_key)

    # Sign a capsule file
    sign_capsule_file("capsule.scp.json", private_key_path)
"""

import json
import os
import hashlib
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
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


# Default key ID (James's identity)
DEFAULT_KEY_ID = "did:key:z6MktudRY5LBZJeE13BiF4BeisAwWs7gvg6srh2GwLAMKDwJ"


class Signer:
    """
    SCP signer — handles Ed25519 signing of capsules.
    """

    def __init__(self, private_key_path: Optional[str] = None):
        """
        Initialise signer.

        Args:
            private_key_path: Path to private key PEM file
        """
        self.private_key = None
        self.public_key = None
        self.key_id = DEFAULT_KEY_ID

        if private_key_path and os.path.exists(private_key_path):
            self.load_private_key(private_key_path)

    def load_private_key(self, key_path: str):
        """
        Load private key from PEM file.

        Args:
            key_path: Path to private key PEM file
        """
        if not CRYPTO_AVAILABLE:
            raise ImportError("cryptography module not installed")

        with open(key_path, "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
            )

        if not isinstance(private_key, ed25519.Ed25519PrivateKey):
            raise ValueError("Private key is not Ed25519")

        self.private_key = private_key
        self.public_key = private_key.public_key()

        # Generate key_id from public key
        pub_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        self.key_id = f"did:key:{self._base58_encode(pub_bytes)}"

    def sign(self, capsule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sign a capsule.

        Args:
            capsule: Capsule dict (must be valid SCP schema)

        Returns:
            Signed capsule dict with signature field
        """
        if not self.private_key:
            raise ValueError("Private key not loaded")

        # Validate schema first
        from .schema import validate_schema
        validate_schema(capsule)

        # Create a copy without signature
        capsule_copy = capsule.copy()
        if "signature" in capsule_copy:
            del capsule_copy["signature"]

        # Canonicalise
        canonical = canonicalise_json(capsule_copy)

        # Sign
        signature = self.private_key.sign(canonical.encode('utf-8'))

        # Add signature to capsule
        capsule_copy["signature"] = {
            "key_id": self.key_id,
            "algorithm": "Ed25519",
            "value": signature.hex(),
        }

        return capsule_copy

    def sign_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Sign a capsule file.

        Args:
            file_path: Path to capsule file
            output_path: Output path (default: file_path with .scp.json)

        Returns:
            Path to signed file
        """
        with open(file_path, "r") as f:
            capsule = json.load(f)

        signed = self.sign(capsule)

        output_path = output_path or file_path
        with open(output_path, "w") as f:
            json.dump(signed, f, indent=2)

        return output_path

    def sign_sidecar(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Create a detached .sig sidecar for a non-JSON artefact.

        Args:
            file_path: Path to the artefact
            output_path: Output path for .sig file

        Returns:
            Path to .sig file
        """
        if not self.private_key:
            raise ValueError("Private key not loaded")

        # Read raw bytes
        with open(file_path, "rb") as f:
            data = f.read()

        # Sign raw bytes
        signature = self.private_key.sign(data)

        # Create .sig file
        output_path = output_path or f"{file_path}.sig"
        with open(output_path, "w") as f:
            json.dump({
                "key_id": self.key_id,
                "algorithm": "Ed25519",
                "value": signature.hex(),
                "target": os.path.basename(file_path),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }, f, indent=2)

        return output_path

    def _base58_encode(self, data: bytes) -> str:
        """Simple base58 encoding (for did:key)."""
        # This is a simplified version
        # Full implementation would use proper base58
        import base64
        return base64.b64encode(data).decode('utf-8').replace('+', '-').replace('/', '_')


def sign_capsule(capsule: Dict[str, Any], private_key_path: str) -> Dict[str, Any]:
    """
    Convenience function to sign a capsule.

    Args:
        capsule: Capsule dict
        private_key_path: Path to private key

    Returns:
        Signed capsule dict
    """
    signer = Signer(private_key_path)
    return signer.sign(capsule)


def sign_capsule_file(file_path: str, private_key_path: str, output_path: Optional[str] = None) -> str:
    """
    Convenience function to sign a capsule file.

    Args:
        file_path: Path to capsule file
        private_key_path: Path to private key
        output_path: Output path

    Returns:
        Path to signed file
    """
    signer = Signer(private_key_path)
    return signer.sign_file(file_path, output_path)


def generate_key_pair(output_path: str = "forge-signing.pem") -> str:
    """
    Generate a new Ed25519 key pair.

    Args:
        output_path: Output path for private key

    Returns:
        Path to private key file
    """
    if not CRYPTO_AVAILABLE:
        raise ImportError("cryptography module not installed")

    private_key = ed25519.Ed25519PrivateKey.generate()

    with open(output_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    return output_path


def get_public_key(private_key_path: str) -> str:
    """
    Get public key from private key file.

    Args:
        private_key_path: Path to private key

    Returns:
        Public key as hex
    """
    if not CRYPTO_AVAILABLE:
        raise ImportError("cryptography module not installed")

    with open(private_key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
        )

    if not isinstance(private_key, ed25519.Ed25519PrivateKey):
        raise ValueError("Private key is not Ed25519")

    public_key = private_key.public_key()
    pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    return pub_bytes.hex()


# ============================================================
# CLI
# ============================================================

def main():
    """Test signing."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="SCP — Signing")
    parser.add_argument("--generate", "-g", action="store_true", help="Generate key pair")
    parser.add_argument("--sign", "-s", type=str, help="Sign capsule file")
    parser.add_argument("--key", "-k", type=str, default="forge-signing.pem", help="Private key path")
    parser.add_argument("--sidecar", "-c", type=str, help="Create sidecar for file")

    args = parser.parse_args()

    if args.generate:
        print("🔑 Generating key pair...")
        path = generate_key_pair(args.key)
        print(f"✅ Key pair generated: {path}")
        pub = get_public_key(path)
        print(f"   Public key: {pub[:16]}...")

    elif args.sign:
        print(f"🔏 Signing: {args.sign}")
        sign_capsule_file(args.sign, args.key)
        print(f"✅ Signed: {args.sign}")

    elif args.sidecar:
        print(f"📎 Creating sidecar: {args.sidecar}")
        signer = Signer(args.key)
        signer.sign_sidecar(args.sidecar)
        print(f"✅ Sidecar created: {args.sidecar}.sig")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
