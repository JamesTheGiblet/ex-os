"""
HAL — Human Accountability Layer

The Act stage of the Forge Stack.

Components:
- seal.py: Seal command
- tiers.py: Tier definitions
- verify.py: Score file verification
- cli.py: Command-line interface

Version: 1.0
"""

from .seal import seal, Seal
from .tiers import TIERS, get_tier_for_lambda, get_lambda_for_tier, is_quarantined
from .verify import verify_score_file, load_score_file

__all__ = [
    "seal",
    "Seal",
    "TIERS",
    "get_tier_for_lambda",
    "get_lambda_for_tier",
    "is_quarantined",
    "verify_score_file",
    "load_score_file",
]

__version__ = "1.0"