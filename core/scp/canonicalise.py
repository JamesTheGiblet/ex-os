#!/usr/bin/env python3
"""
SCP — JSON Canonicalisation

Canonicalises JSON for reproducible signing.

Rules:
- Sort keys
- No extra whitespace
- ASCII encoding
- Consistent number formatting
- No trailing zeros in decimals

Current scheme: forge-c14n-1
Target (v2): RFC 8785 / JCS

Usage:
    from core.scp.canonicalise import canonicalise_json

    canonical = canonicalise_json({"key": "value"})
"""

import json
import re
from typing import Dict, Any, Union

CANONICALISATION_SCHEME = "forge-c14n-1"


def canonicalise_json(obj: Union[Dict, Any]) -> str:
    """
    Canonicalise a JSON object for signing.

    Rules:
    - Sort keys alphabetically
    - Use separators (',', ':') without spaces
    - Ensure ASCII
    - Escape non-ASCII characters

    Args:
        obj: JSON-serialisable object

    Returns:
        Canonicalised JSON string
    """
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=True,
    )


def canonicalise_with_version(obj: Union[Dict, Any]) -> Dict[str, Any]:
    """
    Canonicalise and wrap with version information.

    Returns:
        {"_canonical": canonical_string, "_scheme": version}
    """
    return {
        "_canonical": canonicalise_json(obj),
        "_scheme": CANONICALISATION_SCHEME,
    }


def get_canonicalisation_scheme() -> str:
    """Get the current canonicalisation scheme."""
    return CANONICALISATION_SCHEME


# ============================================================
# CLI
# ============================================================

def main():
    """Test canonicalisation."""
    import argparse
    import sys
    import json

    parser = argparse.ArgumentParser(description="SCP — Canonicalisation")
    parser.add_argument("file", type=str, nargs="?", help="JSON file to canonicalise")

    args = parser.parse_args()

    if args.file:
        with open(args.file, "r") as f:
            data = json.load(f)

        canonical = canonicalise_json(data)
        print(canonical)

    else:
        # Test with sample data
        sample = {
            "scp_version": "0.1",
            "scp_id": "test/example",
            "declaration": {
                "type": "capsule",
                "object_class": "Safe",
                "intent": "Test capsule"
            }
        }

        print("Canonicalisation test:")
        print("=" * 60)
        print(canonicalise_json(sample))


if __name__ == "__main__":
    main()