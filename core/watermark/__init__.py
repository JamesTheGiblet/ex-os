"""
Watermark — Provenance and Traceability

The provenance and traceability layer of Ex-OS.

Components:
- engine.py: Watermark engine
- verify.py: Watermark verification
- provenance.py: Provenance tracking
- cli.py: Command-line interface

Version: 1.0
"""

from .engine import WatermarkEngine, create_watermark, watermark_content
from .verify import verify_watermark, verify_content
from .provenance import ProvenanceTracker, track_provenance

__all__ = [
    "WatermarkEngine",
    "create_watermark",
    "watermark_content",
    "verify_watermark",
    "verify_content",
    "ProvenanceTracker",
    "track_provenance",
]

__version__ = "1.0"