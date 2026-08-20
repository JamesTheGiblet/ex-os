#!/usr/bin/env python3
"""
SCP — Schema Validation

Validates SCP capsule schema v1.2.

Schema fields:
- scp_version: Protocol version
- scp_id: Unique identifier (namespace/capsule-name)
- created: ISO 8601 UTC timestamp
- inherits: Historical governance pointer
- declaration: Semantic declaration
- licence: MSL-1.0
- signature: {key_id, algorithm: Ed25519, value}

Usage:
    from core.scp.schema import validate_schema

    try:
        validate_schema(capsule)
        print("Valid")
    except ValueError as e:
        print(f"Invalid: {e}")
"""

import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

SCHEMA_VERSION = "1.2"
SUPPORTED_VERSIONS = ["0.1", "1.0", "1.1", "1.2"]

# SCP ID pattern: namespace/capsule-name
SCP_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+/[a-zA-Z0-9_\-\.]+$')

# Object classes
OBJECT_CLASSES = ["Safe", "Euclid", "Keter", "Thaumiel"]

# Licence
LICENCE = "MSL-1.0"


def validate_schema(capsule: Dict[str, Any]) -> bool:
    """
    Validate an SCP capsule against the schema.

    Args:
        capsule: Capsule dict

    Returns:
        True if valid

    Raises:
        ValueError: If capsule is invalid
    """
    errors = []

    # Check required fields
    required = ["scp_version", "scp_id", "declaration"]
    for field in required:
        if field not in capsule:
            errors.append(f"Missing required field: {field}")

    # Check scp_version
    scp_version = capsule.get("scp_version", "")
    if scp_version not in SUPPORTED_VERSIONS:
        errors.append(f"Unsupported scp_version: {scp_version} (supported: {SUPPORTED_VERSIONS})")

    # Check scp_id
    scp_id = capsule.get("scp_id", "")
    if not scp_id:
        errors.append("scp_id is empty")
    elif not SCP_ID_PATTERN.match(scp_id):
        errors.append(f"Invalid scp_id format: {scp_id} (expected: namespace/capsule-name)")

    # Check created (if present)
    created = capsule.get("created")
    if created:
        try:
            datetime.fromisoformat(created.replace('Z', '+00:00'))
        except ValueError:
            errors.append(f"Invalid created timestamp: {created}")

    # Check inherits (if present)
    inherits = capsule.get("inherits")
    if inherits and not isinstance(inherits, str):
        errors.append("inherits must be a string")

    # Check declaration
    declaration = capsule.get("declaration")
    if declaration:
        if not isinstance(declaration, dict):
            errors.append("declaration must be an object")
        else:
            # Check required declaration fields for capsule types
            capsule_type = declaration.get("type")
            if capsule_type:
                if capsule_type == "capsule":
                    # Capsule declaration requires object_class and intent
                    if "object_class" not in declaration:
                        errors.append("capsule declaration missing object_class")
                    elif declaration.get("object_class") not in OBJECT_CLASSES:
                        errors.append(f"Invalid object_class: {declaration.get('object_class')}")

                    if "intent" not in declaration:
                        errors.append("capsule declaration missing intent")
                elif capsule_type == "rule":
                    # Rule declaration requires conditions and conclusion
                    if "conditions" not in declaration:
                        errors.append("rule declaration missing conditions")
                    if "conclusion" not in declaration:
                        errors.append("rule declaration missing conclusion")
                elif capsule_type == "attestation":
                    # Attestation declaration requires target and outcome
                    if "target" not in declaration:
                        errors.append("attestation declaration missing target")
                    if "outcome" not in declaration:
                        errors.append("attestation declaration missing outcome")
            else:
                errors.append("declaration missing type field")
    else:
        errors.append("declaration is empty or missing")

    # Check licence (if present)
    licence = capsule.get("licence")
    if licence and licence != LICENCE:
        errors.append(f"Invalid licence: {licence} (must be {LICENCE})")

    # Check signature (if present)
    signature = capsule.get("signature")
    if signature:
        if not isinstance(signature, dict):
            errors.append("signature must be an object")
        else:
            if "key_id" not in signature:
                errors.append("signature missing key_id")
            if "algorithm" not in signature:
                errors.append("signature missing algorithm")
            elif signature.get("algorithm") != "Ed25519":
                errors.append(f"Unsupported signature algorithm: {signature.get('algorithm')}")
            if "value" not in signature:
                errors.append("signature missing value")

    if errors:
        raise ValueError("Invalid SCP capsule:\n  - " + "\n  - ".join(errors))

    return True


def get_schema_version() -> str:
    """Get the current schema version."""
    return SCHEMA_VERSION


def is_supported_version(version: str) -> bool:
    """Check if a version is supported."""
    return version in SUPPORTED_VERSIONS


# ============================================================
# CLI
# ============================================================

def main():
    """Test schema validation."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="SCP — Schema Validation")
    parser.add_argument("file", type=str, nargs="?", help="Capsule file to validate")

    args = parser.parse_args()

    if args.file:
        with open(args.file, "r") as f:
            capsule = json.load(f)

        try:
            validate_schema(capsule)
            print(f"✅ Valid SCP capsule: {capsule.get('scp_id', 'unknown')}")
        except ValueError as e:
            print(f"❌ Invalid: {e}")
            sys.exit(1)
    else:
        print(f"SCP Schema v{SCHEMA_VERSION}")
        print(f"Supported versions: {SUPPORTED_VERSIONS}")
        print(f"Licence: {LICENCE}")


if __name__ == "__main__":
    main()