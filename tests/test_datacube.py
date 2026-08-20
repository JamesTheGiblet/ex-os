#!/usr/bin/env python3
"""
Ex-OS — DataCube Tests

Unit tests for DataCube component.
"""

import sys
import tempfile
from pathlib import Path


def test_cube_creation():
    """Test cube creation."""
    try:
        from core.datacube.cube import create_cube

        cube = create_cube("Test claim", "test.namespace")

        assert cube.cube_id is not None
        assert cube.claim == "Test claim"
        assert cube.lens == "UNKNOWN"
        assert cube.namespace == "test.namespace"

        print("  ✅ Cube creation working")
        return True

    except AssertionError as e:
        print(f"  ❌ Assertion failed: {e}")
        return False
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False


def test_lens_completeness():
    """Test lens completeness."""
    try:
        from core.datacube.cube import create_cube

        cube = create_cube("Test", "test.namespace")
        cube.fill_all_lenses()

        completeness = cube.get_completeness()

        # 5 lenses at 16% each = 80%
        assert completeness >= 0.8

        # Validate human
        cube.validate_human("tester")
        assert cube.is_fully_validated()
        assert cube.is_trust_eligible()

        print("  ✅ Lens completeness working")
        return True

    except AssertionError as e:
        print(f"  ❌ Assertion failed: {e}")
        return False
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False


def test_store():
    """Test cube store."""
    try:
        from core.datacube.store import CubeStore
        from core.datacube.cube import create_cube

        with tempfile.TemporaryDirectory() as tmpdir:
            store = CubeStore(tmpdir)

            cube = create_cube("Store test", "test.namespace")
            cube_id = store.save(cube)

            retrieved = store.get(cube_id)
            assert retrieved is not None
            assert retrieved.claim == "Store test"

            print("  ✅ Cube store working")
            return True

    except AssertionError as e:
        print(f"  ❌ Assertion failed: {e}")
        return False
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False


def run_tests():
    """Run all DataCube tests."""
    print("\n📊 DataCube Tests")
    print("-" * 40)

    tests = [
        ("Cube Creation", test_cube_creation),
        ("Lens Completeness", test_lens_completeness),
        ("Store", test_store),
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
    print(f"\n📊 DataCube Tests: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)