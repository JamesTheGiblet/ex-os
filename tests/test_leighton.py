#!/usr/bin/env python3
"""
Ex-OS — Leighton Weight Tests

Unit tests for Leighton Weight Engine.
"""

import sys
import tempfile
from pathlib import Path


def test_lambda_computation():
    """Test λ computation."""
    try:
        from core.leighton.engine import LeightonEngine

        with tempfile.TemporaryDirectory() as tmpdir:
            engine = LeightonEngine(tmpdir)

            # Record observations
            engine.record_observation("test-entity", "success", "system", 1.0)
            engine.record_observation("test-entity", "success", "system", 1.0)

            λ = engine.compute("test-entity")

            assert λ >= 1.0
            assert λ <= 2.0

            print("  ✅ λ computation working")
            return True

    except AssertionError as e:
        print(f"  ❌ Assertion failed: {e}")
        return False
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False


def test_decay():
    """Test decay function."""
    try:
        from core.leighton.decay import neutral_attractor

        λ = 1.5
        k = 0.01
        days = 30

        decayed = neutral_attractor(λ, k, days)

        # Should decay toward 1.00
        assert decayed < 1.5
        assert decayed > 1.0

        print("  ✅ Decay working")
        return True

    except AssertionError as e:
        print(f"  ❌ Assertion failed: {e}")
        return False
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False


def run_tests():
    """Run all Leighton Weight tests."""
    print("\n⚡ Leighton Weight Tests")
    print("-" * 40)

    tests = [
        ("λ Computation", test_lambda_computation),
        ("Decay", test_decay),
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
    print(f"\n📊 Leighton Weight Tests: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)