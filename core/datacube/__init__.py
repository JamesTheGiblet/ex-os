"""
DataCube — The Classify Stage

The Classify stage of the Forge Stack.

Components:
- lenses.py: Five lenses (FACT, OPINION, FICTION, CONTEXT, UNKNOWN)
- cube.py: Cube object + self-filling
- store.py: Storage (SQLite/JSON)
- bulk.py: Bulk ingestion
- cli.py: Command-line interface

Version: 1.0
"""

from .lenses import LENSES, LENS_NAMES, is_valid_lens, get_lens_description
from .cube import Cube, create_cube, get_completeness
from .store import CubeStore, save_cube, get_cube, search_cubes
from .bulk import bulk_ingest_json, bulk_ingest_csv

__all__ = [
    "LENSES",
    "LENS_NAMES",
    "is_valid_lens",
    "get_lens_description",
    "Cube",
    "create_cube",
    "get_completeness",
    "CubeStore",
    "save_cube",
    "get_cube",
    "search_cubes",
    "bulk_ingest_json",
    "bulk_ingest_csv",
]

__version__ = "1.0"