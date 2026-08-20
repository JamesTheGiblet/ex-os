#!/usr/bin/env python3
"""
Ex-OS — SCP Tests

Unit tests for SCP component.
"""

import sys
import json
import tempfile
from pathlib import Path


def test_schema_validation():
    """Test SCP schema validation."""
    try:
        from core.scp.schema import validate_schema

        # Valid capsule
        capsule = {
            "scp_version": "0.1",
            "scp_id": "test/example",
            "declaration": {
                "type": "capsule",
                "object_class": "Safe",
                "intent": "Test capsule"
            }
        }
        try:
            validate_schema(capsule)
            print("  ✅ Valid capsule passed")
        except ValueError:
            print("  ❌ Valid capsule failed")
            return False

        # Invalid capsule (missing field)
        capsule = {
            "scp_version": "0.1"
        }
        try:
            validate_schema(capsule)
            print("  ❌ Invalid capsule passed")
            return False
        except ValueError:
            print("  ✅ Invalid capsule caught")

        return True

    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False


def test_canonicalisation():
    """Test JSON canonicalisation."""
    try:
        from core.scp.canonicalise import canonicalise_json

        obj = {"b": 2, "a": 1}
        canonical = canonicalise_json(obj)

        # Should be sorted keys
        assert canonical == '{"a":1,"b":2}'

        print("  ✅ Canonicalisation working")
        return True

    except AssertionError:
        print("  ❌ Canonicalisation failed")
        return False
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False


def run_tests():
    """Run all SCP tests."""
    print("\n🔏 SCP Tests")
    print("-" * 40)

    tests = [
        ("Schema Validation", test_schema_validation),
        ("Canonicalisation", test_canonicalisation),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        success = test_func()
        if success:
            passed += 1
        else:
            failed += 1

    return passed, failed


if __name__ == "__main__":
    passed, failed = run_tests()
    print(f"\n📊 SCP Tests: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)