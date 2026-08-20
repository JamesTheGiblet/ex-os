"""
BuddAI — Personal AI Exocortex

A local AI partner that remembers projects, learns your style,
and gets better every time you use it.

Components:
- personality.py: Intent detection, context awareness
- memory.py: Short/long-term memory with Forge Theory decay
- validators.py: 8 hardware-specific code validators
- learning.py: Permanent correction storage
- server.py: API server

Version: 5.0
"""

from .personality import PersonalityEngine
from .memory import MemorySystem
from .validators import ValidatorEngine
from .learning import LearningEngine

__all__ = [
    "PersonalityEngine",
    "MemorySystem",
    "ValidatorEngine",
    "LearningEngine",
]

__version__ = "5.0"