"""
Ex-OS — Integration Layer

The nervous system of Ex-OS. Connects all components.

Components:
- network_daemon.py: Unified API server (port 8080)
- api.py: Route handlers
- dashboard.html: Web UI
- cli.py: Ex-OS CLI wrapper

Version: 1.0
"""

from .network_daemon import ExOSHandler
from .api import APIHandler

__all__ = [
    "ExOSHandler",
    "APIHandler",
]

__version__ = "1.0"
