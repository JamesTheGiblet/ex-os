"""
Mimir — Codebase Intelligence Engine

An sc-bound LLM that ingests codebases, answers questions,
and generates code with full provenance.

Components:
- binding.py: SCP binding capsule loader
- query.py: Query engine with scoring
- watermark_llm.py: LLM wrapper + watermarking
- ingest.py: Codebase ingestion pipeline
- search.py: Semantic search over capsules
- generate.py: Code generation with context
- cli.py: Command-line interface

Version: 1.0
"""

from .binding import MimirBinding, verify_binding
from .query import MimirQuery, search_capsules
from .watermark_llm import MimirLLM, verify_watermark
from .ingest import MimirIngest, ingest_repo
from .search import MimirSearch, semantic_search
from .generate import MimirGenerate, generate_code

__all__ = [
    "MimirBinding",
    "verify_binding",
    "MimirQuery",
    "search_capsules",
    "MimirLLM",
    "verify_watermark",
    "MimirIngest",
    "ingest_repo",
    "MimirSearch",
    "semantic_search",
    "MimirGenerate",
    "generate_code",
]

__version__ = "1.0"