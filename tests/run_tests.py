#!/usr/bin/env python3
"""
Ex-OS — Test Runner

Runs all tests for Ex-OS.

Usage:
    python tests/run_tests.py [--component COMPONENT] [--verbose]
"""

import sys
import argparse
import subprocess
from pathlib import Path


def run_test_file(test_file: str, verbose: bool = False) -> bool:
    """Run a single test file."""
    cmd = [sys.executable, test_file]
    if verbose:
        cmd.append("--verbose")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ {test_file} failed")
            if verbose:
                print(result.stdout)
                print(result.stderr)
            return False
        else:
            print(f"✅ {test_file} passed")
            return True
    except Exception as e:
        print(f"❌ {test_file} error: {e}")
        return False


def main():
    """Run all tests."""
    parser = argparse.ArgumentParser(description="Ex-OS — Test Runner")
    parser.add_argument("--component", "-c", type=str, help="Run tests for a specific component")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fresh", "-f", action="store_true", help="Run fresh clone test only")

    args = parser.parse_args()

    print("🧪 Ex-OS — Test Runner")
    print("=" * 60)

    test_dir = Path(__file__).parent

    if args.fresh:
        print("Running fresh clone test...")
        fresh_test = test_dir / "test_fresh_clone.py"
        return 0 if run_test_file(str(fresh_test), args.verbose) else 1

    if args.component:
        test_file = test_dir / f"test_{args.component}.py"
        if not test_file.exists():
            print(f"❌ Test file not found: test_{args.component}.py")
            return 1
        return 0 if run_test_file(str(test_file), args.verbose) else 1

    # Run all tests
    test_files = list(test_dir.glob("test_*.py"))

    if not test_files:
        print("❌ No test files found")
        return 1

    print(f"Found {len(test_files)} test files")
    print("")

    passed = 0
    failed = 0

    for test_file in test_files:
        # Skip fresh clone test if other tests exist
        if "fresh" in test_file.name:
            continue

        if run_test_file(str(test_file), args.verbose):
            passed += 1
        else:
            failed += 1

    # Run fresh clone test last
    print("\n" + "-" * 40)
    fresh_test = test_dir / "test_fresh_clone.py"
    if fresh_test.exists():
        if run_test_file(str(fresh_test), args.verbose):
            passed += 1
        else:
            failed += 1

    print("")
    print("=" * 60)
    print("📊 Test Results")
    print("=" * 60)

    if failed == 0:
        print(f"✅ All {passed} tests passed!")
        return 0
    else:
        print(f"❌ {failed} tests failed, {passed} passed")
        return 1


if __name__ == "__main__":
    sys.exit(main())