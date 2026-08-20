"""
SCP — Semantic Capsule Protocol

The Declare stage of the Forge Stack.

Components:
- schema.py: Schema validation
- sign.py: Ed25519 signing
- canonicalise.py: JSON canonicalisation
- verify.py: Signature verification
- cli.py: Command-line interface

Version: 1.2
"""

from .schema import validate_schema, SCHEMA_VERSION
from .sign import sign_capsule, sign_capsule_file
from .canonicalise import canonicalise_json
from .verify import verify_signature, verify_capsule

__all__ = [
    "validate_schema",
    "SCHEMA_VERSION",
    "sign_capsule",
    "sign_capsule_file",
    "canonicalise_json",
    "verify_signature",
    "verify_capsule",
]

__version__ = "1.2"