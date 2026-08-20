#!/usr/bin/env python3
"""
Keystone Gate — Enforcement Layer

Binds an LLM to an SCP capsule and forces compliance.

The LLM only handles interface and language.
The Gate handles truth arbitration.

Usage:
    from enforcement.keystone.gate import KeystoneGate

    gate = KeystoneGate()
    gate.bind("mimir/binding-v1")

    response = gate.generate("What is Ohm's law?")
    if response["valid"]:
        print(response["text"])
"""

import json
import hashlib
import importlib
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from pathlib import Path

from .binding import bind_capsule, Binding
from .validate import validate_against_capsule
from .adversarial import run_adversarial_tests


class KeystoneGate:
    """
    Keystone Gate — enforcement layer.

    Binds LLM to SCP capsule and validates all responses.
    """

    def __init__(
        self,
        llm_client: Optional[Any] = None,
        trust_threshold: float = 0.85,
        adversarial_enabled: bool = True,
    ):
        """
        Initialise the Gate.

        Args:
            llm_client: LLM client (Ollama, llama.cpp, etc.)
            trust_threshold: λ threshold for validation (default: 0.85)
            adversarial_enabled: Enable Replicant adversarial testing
        """
        self.llm_client = llm_client
        self.trust_threshold = trust_threshold
        self.adversarial_enabled = adversarial_enabled
        self.binding: Optional[Binding] = None
        self.conversation_history = []
        self.validation_log = []

    def bind(self, capsule_path: str, model_name: Optional[str] = None) -> bool:
        """
        Bind the LLM to a capsule.

        Args:
            capsule_path: Path to SCP capsule
            model_name: Name of the model (for condition check)

        Returns:
            True if binding successful
        """
        try:
            self.binding = bind_capsule(capsule_path, model_name)
            self.conversation_history = []
            print(f"✅ Bound to: {self.binding.scp_id}")
            return True
        except Exception as e:
            print(f"❌ Binding failed: {e}")
            return False

    def generate(self, prompt: str, context: Optional[List] = None) -> Dict[str, Any]:
        """
        Generate a response with enforcement.

        Args:
            prompt: User prompt
            context: Optional context

        Returns:
            Response dict with validation status
        """
        if not self.binding:
            return {
                "status": "error",
                "message": "No capsule bound. Call bind() first.",
                "valid": False,
            }

        # Build system prompt from binding
        system_prompt = self.binding.build_system_prompt()

        # Generate response
        if self.llm_client is None:
            # Simulate LLM response (for testing)
            response_text = self._simulate_response(prompt)
        else:
            response_text = self._call_llm(system_prompt, prompt, context)

        # Validate response
        validation_result = validate_against_capsule(
            response_text,
            self.binding.capsule,
            trust_threshold=self.trust_threshold,
        )

        # Run adversarial tests if enabled
        adversarial_result = None
        if self.adversarial_enabled and validation_result["valid"]:
            adversarial_result = run_adversarial_tests(
                response_text,
                self.binding.capsule,
                iterations=3,
            )
            # If adversarial tests fail, override validation
            if adversarial_result and not adversarial_result.get("passed", True):
                validation_result["valid"] = False
                validation_result["reasoning"] += " (failed adversarial tests)"

        # Record validation
        self._log_validation(prompt, response_text, validation_result)

        # Store conversation history
        if validation_result["valid"]:
            self.conversation_history.append({
                "role": "user",
                "content": prompt,
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text,
            })

        return {
            "status": "ok" if validation_result["valid"] else "blocked",
            "text": response_text if validation_result["valid"] else None,
            "valid": validation_result["valid"],
            "reasoning": validation_result.get("reasoning", ""),
            "λ": validation_result.get("λ", 0.0),
            "audit_trail": validation_result.get("audit_trail"),
            "adversarial": adversarial_result,
            "binding_id": self.binding.scp_id,
        }

    def _simulate_response(self, prompt: str) -> str:
        """Simulate an LLM response for testing."""
        return f"Simulated response to: {prompt}"

    def _call_llm(self, system: str, prompt: str, context: Optional[List]) -> str:
        """Call the LLM client."""
        if self.llm_client is None:
            return self._simulate_response(prompt)

        try:
            # Ollama is optional; import it only when an LLM client is configured.
            ollama = importlib.import_module("ollama")
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ]
            response = ollama.chat(
                model=self.llm_client,
                messages=messages,
            )
            return response["message"]["content"]
        except ImportError:
            # Fallback
            return self._simulate_response(prompt)
        except Exception:
            return self._simulate_response(prompt)

    def _log_validation(self, prompt: str, response: str, result: Dict[str, Any]):
        """Log validation for audit."""
        entry = {
            "prompt": prompt[:200],
            "response": response[:200],
            "valid": result.get("valid", False),
            "reasoning": result.get("reasoning", ""),
            "λ": result.get("λ", 0.0),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "binding_id": self.binding.scp_id if self.binding else None,
        }
        self.validation_log.append(entry)

    def get_audit_trail(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get the audit trail of validations."""
        return self.validation_log[-limit:]

    def get_status(self) -> Dict[str, Any]:
        """Get Gate status."""
        return {
            "bound": self.binding is not None,
            "binding_id": self.binding.scp_id if self.binding else None,
            "persona": self.binding.get_persona() if self.binding else None,
            "trust_threshold": self.trust_threshold,
            "adversarial_enabled": self.adversarial_enabled,
            "history_length": len(self.conversation_history),
            "validations": len(self.validation_log),
        }


def bind_llm(llm_client: Any, capsule_path: str, model_name: Optional[str] = None) -> KeystoneGate:
    """
    Convenience function to bind an LLM to a capsule.

    Args:
        llm_client: LLM client
        capsule_path: Path to SCP capsule
        model_name: Name of the model

    Returns:
        KeystoneGate instance
    """
    gate = KeystoneGate(llm_client)
    gate.bind(capsule_path, model_name)
    return gate


def validate_response(
    response: str,
    capsule_path: str,
    trust_threshold: float = 0.85,
) -> Dict[str, Any]:
    """
    Convenience function to validate a response.

    Args:
        response: Response text
        capsule_path: Path to SCP capsule
        trust_threshold: λ threshold

    Returns:
        Validation result
    """
    from .binding import bind_capsule
    binding = bind_capsule(capsule_path)
    return validate_against_capsule(response, binding.capsule, trust_threshold)


# ============================================================
# CLI
# ============================================================

def main():
    """Test Keystone Gate."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Keystone Gate")
    parser.add_argument("--bind", "-b", type=str, help="Capsule to bind")
    parser.add_argument("--prompt", "-p", type=str, help="Prompt to generate")
    parser.add_argument("--validate", "-v", type=str, help="Validate a response against capsule")
    parser.add_argument("--capsule", "-c", type=str, help="Capsule for validation")
    parser.add_argument("--threshold", "-t", type=float, default=0.85, help="Trust threshold")
    parser.add_argument("--status", "-s", action="store_true", help="Show Gate status")

    args = parser.parse_args()

    gate = KeystoneGate(trust_threshold=args.threshold)

    if args.status:
        status = gate.get_status()
        print(f"📊 Keystone Gate Status")
        print("=" * 60)
        for key, value in status.items():
            print(f"  {key}: {value}")
        return

    if args.bind:
        gate.bind(args.bind)
        print(f"✅ Bound to: {args.bind}")
        return

    if args.prompt and gate.binding:
        result = gate.generate(args.prompt)
        print(f"📝 Prompt: {args.prompt}")
        print("=" * 60)
        if result["valid"]:
            print(result["text"])
        else:
            print(f"❌ Blocked: {result.get('reasoning', 'No reason given')}")

    elif args.validate and args.capsule:
        result = validate_response(args.validate, args.capsule, args.threshold)
        print(f"📝 Response: {args.validate[:60]}...")
        print("=" * 60)
        print(f"  Valid: {result.get('valid', False)}")
        print(f"  Reasoning: {result.get('reasoning', '')}")
        print(f"  λ: {result.get('λ', 0.0):.3f}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
