"""
Leighton Weight Engine — The Trust-Score Stage

Computes λ (Leighton Weight) — a trust score between 0.00 and 2.00.

Components:
- engine.py: λ computation
- decay.py: Neutral-attractor decay
- attest.py: Attestation processing
- cli.py: Command-line interface

Version: 1.0
"""

from .engine import LeightonEngine, compute_lambda, get_trust_status
from .decay import decay_lambda, neutral_attractor, asymmetric_decay
from .attest import process_attestation, Attestation

__all__ = [
    "LeightonEngine",
    "compute_lambda",
    "get_trust_status",
    "decay_lambda",
    "neutral_attractor",
    "asymmetric_decay",
    "process_attestation",
    "Attestation",
]

__version__ = "1.0"