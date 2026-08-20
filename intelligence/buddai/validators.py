#!/usr/bin/env python3
"""
BuddAI — Hardware Validators

8 hardware-specific validators that catch common mistakes
in generated code before it runs.

Validators:
1. ESP32 Hardware — Catches analogWrite(), wrong ADC resolution
2. Motor Control — Prevents PWM conflicts, ensures L298N pins defined
3. Timing Safety — Requires safety timeouts, prevents delay() in motor loops
4. Forge Theory — Suggests exponential smoothing for fluid movement
5. Servo/Combat — Enforces state machines for weapon systems
6. Arduino Compat — Removes unnecessary includes, checks initialization
7. Memory Safety — Removes unused variables
8. Style Guide — Prevents feature bloat, enforces naming conventions

Usage:
    from intelligence.buddai.validators import ValidatorEngine

    engine = ValidatorEngine()
    issues = engine.validate(code, target="esp32")
    if issues:
        for issue in issues:
            print(f"❌ {issue['message']}")
"""

import re
from typing import List, Dict, Any, Optional


class ValidatorEngine:
    """
    BuddAI validator engine — 8 hardware-specific validators.
    """

    def __init__(self):
        self.validators = {
            "esp32": self._validate_esp32,
            "motor": self._validate_motor,
            "timing": self._validate_timing,
            "forge": self._validate_forge,
            "servo": self._validate_servo,
            "arduino": self._validate_arduino,
            "memory": self._validate_memory,
            "style": self._validate_style,
        }
        self.validation_results = []

    def validate(self, code: str, target: str = "esp32") -> List[Dict[str, Any]]:
        """
        Validate code against all applicable validators.

        Args:
            code: Code string to validate
            target: Target hardware ("esp32", "arduino", "generic")

        Returns:
            List of validation issues
        """
        self.validation_results = []

        for validator_name, validator_fn in self.validators.items():
            issues = validator_fn(code, target)
            if issues:
                self.validation_results.extend(issues)

        return self.validation_results

    # ============================================================
    # Validator 1: ESP32 Hardware
    # ============================================================

    def _validate_esp32(self, code: str, target: str) -> List[Dict[str, Any]]:
        """ESP32 hardware-specific checks."""
        issues = []

        if target != "esp32":
            return issues

        # Check for analogWrite() on ESP32
        if "analogWrite(" in code:
            issues.append({
                "validator": "esp32",
                "type": "error",
                "message": "ESP32 does not support analogWrite(). Use ledcWrite() instead.",
                "fix": "Replace analogWrite(pin, value) with ledcWrite(channel, value)",
                "line": self._find_line(code, "analogWrite"),
            })

        # Check ADC resolution
        if "analogRead(" in code and "analogReadResolution" not in code:
            issues.append({
                "validator": "esp32",
                "type": "warning",
                "message": "ESP32 ADC resolution is 12-bit (0-4095), not 10-bit (0-1023).",
                "fix": "Add analogReadResolution(12) or map values accordingly.",
                "line": self._find_line(code, "analogRead"),
            })

        # Check for pinMode with INPUT_PULLUP on ESP32
        if "INPUT_PULLUP" in code:
            issues.append({
                "validator": "esp32",
                "type": "info",
                "message": "ESP32 supports INPUT_PULLUP, but consider using external pull-ups.",
                "fix": "Use INPUT_PULLUP with external resistor for reliability.",
                "line": self._find_line(code, "INPUT_PULLUP"),
            })

        return issues

    # ============================================================
    # Validator 2: Motor Control
    # ============================================================

    def _validate_motor(self, code: str, target: str) -> List[Dict[str, Any]]:
        """Motor control-specific checks."""
        issues = []

        # Check for L298N enable pins
        if "l298n" in code.lower() or "motor" in code.lower():
            if "enable" not in code.lower() and "pwm" not in code.lower():
                issues.append({
                    "validator": "motor",
                    "type": "warning",
                    "message": "Motor driver (L298N) requires enable/PWM pins for speed control.",
                    "fix": "Define enable pins and use analogWrite() or ledcWrite().",
                    "line": None,
                })

        # Check for conflicting PWM channels
        pwm_pins = re.findall(r"ledcWrite\((\d+),", code)
        if len(pwm_pins) != len(set(pwm_pins)):
            issues.append({
                "validator": "motor",
                "type": "error",
                "message": "Multiple motors using same PWM channel.",
                "fix": "Assign unique channels to each motor.",
                "line": None,
            })

        return issues

    # ============================================================
    # Validator 3: Timing Safety
    # ============================================================

    def _validate_timing(self, code: str, target: str) -> List[Dict[str, Any]]:
        """Timing and safety checks."""
        issues = []

        # Check for delay() in motor loops
        if "delay(" in code:
            delay_lines = re.findall(r"delay\((\d+)\)", code)
            if delay_lines:
                for delay_val in delay_lines:
                    if int(delay_val) > 100:
                        issues.append({
                            "validator": "timing",
                            "type": "warning",
                            "message": f"Long delay({delay_val}ms) detected in motor loop. This can cause missed events.",
                            "fix": "Use millis() for non-blocking timing instead.",
                            "line": self._find_line(code, f"delay({delay_val})"),
                        })

        # Check for safety timeouts
        if "motor" in code.lower() and "timeout" not in code.lower():
            issues.append({
                "validator": "timing",
                "type": "warning",
                "message": "Motor control should include safety timeouts.",
                "fix": "Add timeout detection to stop motors on failure.",
                "line": None,
            })

        return issues

    # ============================================================
    # Validator 4: Forge Theory
    # ============================================================

    def _validate_forge(self, code: str, target: str) -> List[Dict[str, Any]]:
        """Forge Theory-specific suggestions."""
        issues = []

        # Suggest exponential smoothing for fluid movement
        if "motor" in code.lower() or "servo" in code.lower():
            if "smooth" not in code.lower() and "lerp" not in code.lower():
                issues.append({
                    "validator": "forge",
                    "type": "info",
                    "message": "Consider using exponential smoothing for fluid movement.",
                    "fix": "Use: position = 0.9 * position + 0.1 * target_position",
                    "line": None,
                })

        return issues

    # ============================================================
    # Validator 5: Servo/Combat
    # ============================================================

    def _validate_servo(self, code: str, target: str) -> List[Dict[str, Any]]:
        """Servo and combat system checks."""
        issues = []

        if "servo" in code.lower():
            # Check for state machine
            if "switch" not in code and "if" not in code and "case" not in code:
                issues.append({
                    "validator": "servo",
                    "type": "warning",
                    "message": "Servo control should use a state machine for safety.",
                    "fix": "Implement states: IDLE, ARMING, FIRING, RETREAT.",
                    "line": None,
                })

            # Check for weapon safety
            if "weapon" in code.lower() and "safety" not in code.lower():
                issues.append({
                    "validator": "servo",
                    "type": "error",
                    "message": "Weapon systems require explicit safety checks.",
                    "fix": "Add safety interlock before enabling weapon.",
                    "line": None,
                })

        return issues

    # ============================================================
    # Validator 6: Arduino Compat
    # ============================================================

    def _validate_arduino(self, code: str, target: str) -> List[Dict[str, Any]]:
        """Arduino compatibility checks."""
        issues = []

        # Check for unused includes
        includes = re.findall(r'#include\s*<([^>]+)>', code)
        unused_includes = []
        for inc in includes:
            if inc not in code:
                unused_includes.append(inc)

        for inc in unused_includes:
            issues.append({
                "validator": "arduino",
                "type": "info",
                "message": f"Unused include: <{inc}>",
                "fix": f"Remove #include <{inc}>",
                "line": self._find_line(code, f"#include <{inc}>"),
            })

        # Check for missing setup/loop
        if "void setup()" not in code:
            issues.append({
                "validator": "arduino",
                "type": "error",
                "message": "Missing void setup() function.",
                "fix": "Add void setup() with pin initialization.",
                "line": None,
            })

        if "void loop()" not in code:
            issues.append({
                "validator": "arduino",
                "type": "error",
                "message": "Missing void loop() function.",
                "fix": "Add void loop() with main logic.",
                "line": None,
            })

        return issues

    # ============================================================
    # Validator 7: Memory Safety
    # ============================================================

    def _validate_memory(self, code: str, target: str) -> List[Dict[str, Any]]:
        """Memory safety checks."""
        issues = []

        # Check for unused variables
        var_pattern = re.compile(r'(int|float|double|char|bool|String|uint8_t|uint16_t|uint32_t)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[=;]')
        variables = var_pattern.findall(code)
        for var in variables:
            var_name = var[1]
            if code.count(var_name) < 2:
                issues.append({
                    "validator": "memory",
                    "type": "info",
                    "message": f"Unused variable: {var_name}",
                    "fix": f"Remove or use {var_name}.",
                    "line": self._find_line(code, var_name),
                })

        return issues

    # ============================================================
    # Validator 8: Style Guide
    # ============================================================

    def _validate_style(self, code: str, target: str) -> List[Dict[str, Any]]:
        """Style and naming convention checks."""
        issues = []

        # Check for feature bloat
        if code.count("void") > 20:
            issues.append({
                "validator": "style",
                "type": "warning",
                "message": "High number of functions detected. Consider modularising.",
                "fix": "Split code into separate modules or libraries.",
                "line": None,
            })

        # Check naming conventions
        camel_case = re.compile(r'[a-z]+[A-Z]')
        snake_case = re.compile(r'[a-z]+_[a-z]+')

        if camel_case.search(code) and not snake_case.search(code):
            issues.append({
                "validator": "style",
                "type": "info",
                "message": "Consider using snake_case for variable and function names.",
                "fix": "Rename CamelCase to snake_case.",
                "line": None,
            })

        return issues

    # ============================================================
    # Helpers
    # ============================================================

    def _find_line(self, code: str, pattern: str) -> Optional[int]:
        """Find line number of a pattern in code."""
        lines = code.split("\n")
        for i, line in enumerate(lines, 1):
            if pattern in line:
                return i
        return None


# ============================================================
# CLI
# ============================================================

def main():
    """Test validator engine."""
    import sys

    test_code = """
#include <WiFi.h>
#include <Servo.h>

int motor_enable = 25;
int motor_a = 26;
int motor_b = 27;

void setup() {
    pinMode(motor_enable, OUTPUT);
    pinMode(motor_a, OUTPUT);
    pinMode(motor_b, OUTPUT);
}

void loop() {
    digitalWrite(motor_a, HIGH);
    digitalWrite(motor_b, LOW);
    delay(1000);
    digitalWrite(motor_a, LOW);
    digitalWrite(motor_b, HIGH);
    delay(1000);
}
"""

    engine = ValidatorEngine()
    issues = engine.validate(test_code, target="esp32")

    print("BuddAI — Validator Engine Test")
    print("=" * 60)

    for issue in issues:
        emoji = "❌" if issue["type"] == "error" else "⚠️" if issue["type"] == "warning" else "ℹ️"
        print(f"{emoji} {issue['validator']}: {issue['message']}")
        if issue.get("fix"):
            print(f"   💡 {issue['fix']}")
        if issue.get("line"):
            print(f"   📍 Line: {issue['line']}")


if __name__ == "__main__":
    main()