#!/usr/bin/env python3
"""
Ex-OS — Fresh Clone Test

The real test. Verifies that Ex-OS works from a clean checkout.

This test should be run after every fresh clone.

Usage:
    python tests/test_fresh_clone.py
"""

import sys
import os
import json
import importlib
from pathlib import Path

def test_imports():
    """Test all imports work."""
    print("📦 Testing imports...")

    failures = []

    try:
        import core.scp.sign
        print("  ✅ core.scp.sign")
    except ImportError as e:
        failures.append(f"core.scp.sign: {e}")
        print("  ❌ core.scp.sign")

    try:
        import core.datacube.cube
        print("  ✅ core.datacube.cube")
    except ImportError as e:
        failures.append(f"core.datacube.cube: {e}")
        print("  ❌ core.datacube.cube")

    try:
        import core.leighton.engine
        print("  ✅ core.leighton.engine")
    except ImportError as e:
        failures.append(f"core.leighton.engine: {e}")
        print("  ❌ core.leighton.engine")

    try:
        import core.chronoscribe.ledger
        print("  ✅ core.chronoscribe.ledger")
    except ImportError as e:
        failures.append(f"core.chronoscribe.ledger: {e}")
        print("  ❌ core.chronoscribe.ledger")

    try:
        import core.hal.seal
        print("  ✅ core.hal.seal")
    except ImportError as e:
        failures.append(f"core.hal.seal: {e}")
        print("  ❌ core.hal.seal")

    try:
        import runtime.ubvm.interpreter
        print("  ✅ runtime.ubvm.interpreter")
    except ImportError as e:
        failures.append(f"runtime.ubvm.interpreter: {e}")
        print("  ❌ runtime.ubvm.interpreter")

    try:
        import runtime.ubvm.primitives
        print("  ✅ runtime.ubvm.primitives")
    except ImportError as e:
        failures.append(f"runtime.ubvm.primitives: {e}")
        print("  ❌ runtime.ubvm.primitives")

    try:
        import intelligence.mimir.binding
        print("  ✅ intelligence.mimir.binding")
    except ImportError as e:
        failures.append(f"intelligence.mimir.binding: {e}")
        print("  ❌ intelligence.mimir.binding")

    try:
        import intelligence.buddai.personality
        print("  ✅ intelligence.buddai.personality")
    except ImportError as e:
        failures.append(f"intelligence.buddai.personality: {e}")
        print("  ❌ intelligence.buddai.personality")

    try:
        import core.watermark.engine
        print("  ✅ core.watermark.engine")
    except ImportError as e:
        failures.append(f"core.watermark.engine: {e}")
        print("  ❌ core.watermark.engine")

    return len(failures) == 0, failures


def test_core_primitives():
    """Test core primitives."""
    print("\n🔧 Testing core primitives...")

    try:
        from runtime.ubvm.primitives import DISPATCH

        # Check core primitives exist
        required = ["log", "emit_event", "http_request", "read_file", "write_file", "validate_self"]
        missing = [p for p in required if p not in DISPATCH]

        if missing:
            print(f"  ❌ Missing primitives: {missing}")
            return False, missing

        print(f"  ✅ All core primitives present ({len(DISPATCH)} total)")
        return True, []

    except ImportError as e:
        print(f"  ❌ Failed to import DISPATCH: {e}")
        return False, [str(e)]


def test_scp_sign():
    """Test SCP signing."""
    print("\n🔏 Testing SCP signing...")

    try:
        from core.scp.sign import sign_capsule

        # Create a test capsule
        test_capsule = {
            "scp_version": "0.1",
            "scp_id": "test/example",
            "declaration": {
                "type": "capsule",
                "object_class": "Safe",
                "intent": "Test capsule"
            }
        }

        # Check function exists
        assert callable(sign_capsule)
        print("  ✅ sign_capsule is callable")
        return True, []

    except AssertionError:
        print("  ❌ sign_capsule is not callable")
        return False, ["sign_capsule not callable"]
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False, [str(e)]


def test_chronoscribe():
    """Test ChronoSCRIBE."""
    print("\n📜 Testing ChronoSCRIBE...")

    try:
        from core.chronoscribe.ledger import Ledger

        # Create test ledger
        ledger = Ledger("test")
        stats = ledger.get_stats()

        print(f"  ✅ Ledger created (entries: {stats.get('entries', 0)})")
        return True, []

    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False, [str(e)]


def test_leighton():
    """Test Leighton Weight Engine."""
    print("\n⚡ Testing Leighton Weight Engine...")

    try:
        from core.leighton.engine import compute_lambda

        # Test compute function exists
        assert callable(compute_lambda)
        print("  ✅ compute_lambda is callable")
        return True, []

    except AssertionError:
        print("  ❌ compute_lambda is not callable")
        return False, ["compute_lambda not callable"]
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False, [str(e)]


def test_hal():
    """Test HAL."""
    print("\n🔏 Testing HAL...")

    try:
        from core.hal.tiers import get_tier_for_lambda

        # Test tier mapping
        tier = get_tier_for_lambda(1.5)
        assert tier == 3  # 1.5 is tier 3

        tier = get_tier_for_lambda(0.5)
        assert tier is None

        print("  ✅ HAL tiers working")
        return True, []

    except AssertionError:
        print("  ❌ HAL tier mapping failed")
        return False, ["HAL tier mapping failed"]
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False, [str(e)]


def test_datacube():
    """Test DataCube."""
    print("\n📊 Testing DataCube...")

    try:
        from core.datacube.cube import create_cube
        from core.datacube.lenses import LENSES

        # Create a test cube
        cube = create_cube("Test claim", "test.namespace")

        assert cube.cube_id is not None
        assert cube.claim == "Test claim"
        assert cube.lens == "UNKNOWN"
        assert cube.get_completeness() > 0

        print(f"  ✅ Cube created (completeness: {cube.get_completeness():.2%})")
        return True, []

    except AssertionError as e:
        print(f"  ❌ Assertion failed: {e}")
        return False, [str(e)]
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False, [str(e)]


def test_mimir():
    """Test Mimir."""
    print("\n🧠 Testing Mimir...")

    try:
        from intelligence.mimir.binding import MimirBinding

        # Create default binding
        binding = MimirBinding.load_default()
        assert binding.get_persona() is not None

        print("  ✅ Mimir binding loaded")
        return True, []

    except AssertionError as e:
        print(f"  ❌ Assertion failed: {e}")
        return False, [str(e)]
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False, [str(e)]


def test_watermark():
    """Test Watermark."""
    print("\n💧 Testing Watermark...")

    try:
        from core.watermark.engine import WatermarkEngine

        # Create watermark
        engine = WatermarkEngine()
        result = engine.watermark("Test content", "test", 0.9)

        assert result["provenance_id"] is not None
        assert "Ex-OS Watermark" in result["content"]

        print(f"  ✅ Watermark created: {result['provenance_id']}")
        return True, []

    except AssertionError as e:
        print(f"  ❌ Assertion failed: {e}")
        return False, [str(e)]
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False, [str(e)]


def test_keystone():
    """Test Keystone Gate."""
    print("\n🚪 Testing Keystone Gate...")
    try:
        from core.keystone.gate import KeystoneGate

        gate = KeystoneGate()
        status = gate.get_status()

        assert status is not None

        print(f"  ✅ Keystone Gate initialised")
        return True, []

    except AssertionError as e:
        print(f"  ❌ Assertion failed: {e}")
        return False, [str(e)]
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False, [str(e)]
        return False, [str(e)]


def test_buddai():
    """Test BuddAI."""
    print("\n🧠 Testing BuddAI...")

    try:
        from intelligence.buddai.personality import PersonalityEngine

        engine = PersonalityEngine()

        # Test intent detection
        intent = engine.detect_intent("thinking about a spinner robot")
        assert intent["type"] == "project"

        print(f"  ✅ BuddAI intent detected: {intent['type']}")
        return True, []

    except AssertionError as e:
        print(f"  ❌ Assertion failed: {e}")
        return False, [str(e)]
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False, [str(e)]


def test_integration():
    """Test integration layer."""
    print("\n🔗 Testing Integration...")

    try:
        from integration.api import APIHandler

        handler = APIHandler()
        result = handler.handle_status({})

        assert result["status"] == "ok"

        print("  ✅ Integration API working")
        return True, []

    except AssertionError as e:
        print(f"  ❌ Assertion failed: {e}")
        return False, [str(e)]
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False, [str(e)]


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("🧪 EX-OS — FRESH CLONE TEST")
    print("=" * 60)
    print("\nThis is the real test. Verifies everything works from a fresh clone.\n")

    tests = [
        ("Imports", test_imports),
        ("Core Primitives", test_core_primitives),
        ("SCP Signing", test_scp_sign),
        ("ChronoSCRIBE", test_chronoscribe),
        ("Leighton Weight", test_leighton),
        ("HAL", test_hal),
        ("DataCube", test_datacube),
        ("Mimir", test_mimir),
        ("Watermark", test_watermark),
        ("Keystone Gate", test_keystone),
        ("BuddAI", test_buddai),
        ("Integration", test_integration),
    ]

    passed = 0
    failed = 0
    failures = []

    for name, test_func in tests:
        print(f"\n--- {name} ---")
        success, errors = test_func()

        if success:
            passed += 1
        else:
            failed += 1
            failures.append((name, errors))

    print("\n" + "=" * 60)
    print("📊 RESULTS")
    print("=" * 60)

    if failed == 0:
        print(f"✅ All {passed} tests passed!")
        print("\n✨ Fresh clone verified. Ex-OS is building.")
        return 0
    else:
        print(f"❌ {failed} tests failed, {passed} passed")
        print("\nFailures:")
        for name, errors in failures:
            print(f"  - {name}: {', '.join(errors)}")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())