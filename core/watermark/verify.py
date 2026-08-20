#!/usr/bin/env python3
"""
Watermark — Verification

Verifies watermarks in content.

Features:
- Verify provenance
- Verify content integrity
- Trust score validation

Usage:
    from core.watermark.verify import verify_watermark

    result = verify_watermark(content)
    if result["valid"]:
        print(f"Provenance: {result['provenance']}")
"""

import json
import re
import hashlib
from typing import Dict, Any, Optional, Tuple


def verify_watermark(
    content: str,
    store_dir: str = "watermarks",
) -> Dict[str, Any]:
    """
    Verify a watermark in content.

    Args:
        content: Content with watermark
        store_dir: Store directory

    Returns:
        Verification result
    """
    # Extract provenance ID from watermark
    provenance_id = _extract_watermark(content)

    if not provenance_id:
        return {
            "valid": False,
            "error": "No watermark found",
            "content": content,
        }

    # Load provenance
    import os
    file_path = os.path.join(store_dir, f"{provenance_id}.json")
    if not os.path.exists(file_path):
        return {
            "valid": False,
            "error": f"Provenance not found: {provenance_id}",
            "provenance_id": provenance_id,
            "content": content,
        }

    with open(file_path, "r") as f:
        provenance = json.load(f)

    # Verify content hash
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    stored_hash = provenance.get("content_hash")

    if content_hash != stored_hash:
        return {
            "valid": False,
            "error": "Content hash mismatch — content has been modified",
            "provenance_id": provenance_id,
            "provenance": provenance,
            "content": content,
        }

    return {
        "valid": True,
        "provenance_id": provenance_id,
        "provenance": provenance,
        "content": content,
        "verified_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
    }


def verify_content(
    content: str,
    expected_provenance_id: Optional[str] = None,
    store_dir: str = "watermarks",
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Verify content integrity.

    Args:
        content: Content to verify
        expected_provenance_id: Expected provenance ID
        store_dir: Store directory

    Returns:
        (valid, message, provenance)
    """
    result = verify_watermark(content, store_dir)

    if not result.get("valid"):
        return False, result.get("error", "Verification failed"), None

    if expected_provenance_id and result["provenance_id"] != expected_provenance_id:
        return False, f"Provenance ID mismatch: {result['provenance_id']} != {expected_provenance_id}", None

    return True, "Content verified", result.get("provenance")


def _extract_watermark(content: str) -> Optional[str]:
    """Extract provenance ID from watermark."""
    # Look for watermark comment
    pattern = r'<!--\s*Ex-OS Watermark:\s*([a-zA-Z0-9\-_]+)\s*-->'
    match = re.search(pattern, content)

    if match:
        return match.group(1)

    return None


# ============================================================
# CLI
# ============================================================

def main():
    """Test verification."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Watermark — Verification")
    parser.add_argument("--content", "-c", type=str, help="Content to verify")
    parser.add_argument("--file", "-f", type=str, help="File to verify")
    parser.add_argument("--id", "-i", type=str, help="Expected provenance ID")

    args = parser.parse_args()

    if args.file:
        with open(args.file, "r") as f:
            content = f.read()
    elif args.content:
        content = args.content
    else:
        print("❌ Provide --content or --file")
        sys.exit(1)

    result = verify_watermark(content)

    if result["valid"]:
        print(f"✅ Watermark Verified")
        print(f"   ID: {result['provenance_id']}")
        print(f"   Source: {result['provenance'].get('source', 'unknown')}")
        print(f"   Trust: {result['provenance'].get('trust_score', 0):.2f}")
        print(f"   Timestamp: {result['provenance'].get('timestamp', 'unknown')}")
    else:
        print(f"❌ Verification Failed")
        print(f"   Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()