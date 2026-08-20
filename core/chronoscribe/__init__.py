"""
ChronoSCRIBE — The Audit Stage

The immutable, append-only, cryptographically-anchored ledger.

Components:
- ledger.py: Append-only ledger
- anchor.py: Root anchoring
- verify.py: Ledger verification
- cli.py: Command-line interface

Version: 1.0
"""

from .ledger import Ledger, append_entry, get_ledger, get_entries
from .anchor import anchor_root, get_root_anchor, verify_anchor
from .verify import verify_chain, verify_entry, verify_ledger

__all__ = [
    "Ledger",
    "append_entry",
    "get_ledger",
    "get_entries",
    "anchor_root",
    "get_root_anchor",
    "verify_anchor",
    "verify_chain",
    "verify_entry",
    "verify_ledger",
]

__version__ = "1.0"