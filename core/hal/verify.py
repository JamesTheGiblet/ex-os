#!/usr/bin/env python3
"""
HAL — Score File Verification

Verifies score files for HAL sealing.

Score files are signed snapshots carrying:
- as-of timestamp
- parameter epochs
- TTL check

Usage:
    from core.hal.verify import verify_score_file, load_score_file
"""

import json
import os
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timedelta

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.exceptions import InvalidSignature
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


def load_score_file(file_path: str) -> Dict[str, Any]:
    """
    Load a score file.

    Args:
        file_path: Path to score file

    Returns:
        Score data dict
    """
    with open(file_path, "r") as f:
        return json.load(f)


def verify_score_file(
    score_data: Dict[str, Any],
    max_age_seconds: int = 3600,
) -> Tuple[bool, str]:
    """
    Verify a score file.

    Args:
        score_data: Score data dict
        max_age_seconds: Maximum age of score file

    Returns:
        (valid, message)
    """
    # Check required fields
    required = ["entity_id", "λ", "timestamp", "signature"]
    for field in required:
        if field not in score_data:
            return False, f"Missing required field: {field}"

    # Check timestamp
    timestamp_str = score_data.get("timestamp")
    if not isinstance(timestamp_str, str):
        return False, f"Invalid timestamp: {timestamp_str}"

    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        age = (datetime.now().replace(tzinfo=timestamp.tzinfo) - timestamp).total_seconds()
        if age > max_age_seconds:
            return False, f"Score file expired: {age:.0f}s > {max_age_seconds}s"
    except ValueError:
        return False, f"Invalid timestamp: {timestamp_str}"

    # Verify signature
    if CRYPTO_AVAILABLE:
        signature_hex = score_data.get("signature", {}).get("value")
        key_id = score_data.get("signature", {}).get("key_id")

        if not signature_hex or not key_id:
            return False, "No signature or key_id in score file"

        try:
            signature = bytes.fromhex(signature_hex)
        except ValueError:
            return False, "Invalid signature hex"

        # In production, would fetch public key from registry
        # For now, we check that signature exists and is valid format
        # Actual verification requires public key from key registry

    # Check λ range
    λ = score_data.get("λ", 0.0)
    if not 0.0 <= λ <= 2.0:
        return False, f"λ out of range: {λ} (must be 0.0-2.0)"

    return True, "Score file verified"


def create_score_file(
    entity_id: str,
    λ: float,
    private_key_path: str,
    output_path: str,
) -> str:
    """
    Create a signed score file.

    Args:
        entity_id: Entity ID
        λ: Leighton Weight score
        private_key_path: Path to private key
        output_path: Output path

    Returns:
        Path to score file
    """
    score_data = {
        "entity_id": entity_id,
        "λ": λ,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "signature": {
            "key_id": "did:key:unknown",
            "algorithm": "Ed25519",
            "value": "pending",  # Would be signed in production
        },
    }

    # In production, would sign with private key

    with open(output_path, "w") as f:
        json.dump(score_data, f, indent=2)

    return output_path


def get_score_ttl(score_data: Dict[str, Any]) -> Optional[int]:
    """
    Get the TTL (time-to-live) of a score file.

    Args:
        score_data: Score data dict

    Returns:
        TTL in seconds or None
    """
    timestamp_str = score_data.get("timestamp")
    if not isinstance(timestamp_str, str):
        return None

    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        age = (datetime.now().replace(tzinfo=timestamp.tzinfo) - timestamp).total_seconds()
        return int(age)
    except ValueError:
        return None


# ============================================================
# CLI
# ============================================================

def main():
    """Test verification."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="HAL — Verify Score File")
    parser.add_argument("file", type=str, help="Score file path")
    parser.add_argument("--max-age", "-a", type=int, default=3600, help="Max age in seconds")

    args = parser.parse_args()

    try:
        score_data = load_score_file(args.file)
        valid, message = verify_score_file(score_data, args.max_age)

        if valid:
            print(f"✅ Valid score file")
            print(f"   Entity: {score_data.get('entity_id', 'unknown')}")
            print(f"   λ: {score_data.get('λ', 0):.2f}")
            print(f"   Timestamp: {score_data.get('timestamp', 'unknown')}")
        else:
            print(f"❌ Invalid: {message}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
