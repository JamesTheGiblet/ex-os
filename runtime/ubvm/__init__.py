"""
UBVM — Universal Behavioural Virtual Machine

The runtime engine for SCP capsules.

Components:
- interpreter.py: Core dispatch loop
- primitives.py: Core primitives (log, emit_event, etc.)
- triggers.py: Trigger handlers (on_load, cron, on_event)
- event_bus.py: Event bus (queue.jsonl)
- cli.py: Command-line interface

Version: 1.0
"""

from .interpreter import Interpreter, run_capsule
from .primitives import DISPATCH, register_primitive, get_primitive
from .triggers import TriggerHandler
from .event_bus import EventBus

__all__ = [
    "Interpreter",
    "run_capsule",
    "DISPATCH",
    "register_primitive",
    "get_primitive",
    "TriggerHandler",
    "EventBus",
]

__version__ = "1.0"