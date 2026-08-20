"""
Keystone Gate — The Enforcement Layer

Binds LLM to SCP capsule and forces compliance.

Components:
- gate.py: Enforcement layer
- validate.py: Response validation
- binding.py: SCP binding
- adversarial.py: Replicant swarm integration
- cli.py: Command-line interface

Version: 1.0
"""

from .gate import KeystoneGate, bind_llm, validate_response
from .validate import validate_against_capsule
from .binding import Binding, bind_capsule
from .adversarial import AdversarialTest, run_adversarial_tests

__all__ = [
    "KeystoneGate",
    "bind_llm",
    "validate_response",
    "validate_against_capsule",
    "Binding",
    "bind_capsule",
    "AdversarialTest",
    "run_adversarial_tests",
]

__version__ = "1.0"