#!/usr/bin/env python3
"""
DataCube — Five Lenses

Five lenses plus a contradicts relational field.

Lenses:
- FACT: Verified, concrete claims
- OPINION: Subjective, based on judgement
- FICTION: Speculative, not real
- CONTEXT: Situational, background
- UNKNOWN: Not enough information yet

contradicts: Relational field between cubes (replaces COUNTER)

Usage:
    from core.datacube.lenses import LENSES, is_valid_lens
"""

# Lens definitions
LENSES = {
    "FACT": {
        "name": "FACT",
        "description": "Verified, concrete claims. Highest epistemic status.",
        "epistemic_weight": 1.0,
        "requires_verification": True,
        "color": "#00ff88",
    },
    "OPINION": {
        "name": "OPINION",
        "description": "Subjective, interpretive, based on judgement.",
        "epistemic_weight": 0.7,
        "requires_verification": False,
        "color": "#ffaa00",
    },
    "FICTION": {
        "name": "FICTION",
        "description": "Speculative, imagined, not real.",
        "epistemic_weight": 0.2,
        "requires_verification": False,
        "color": "#ff4444",
    },
    "CONTEXT": {
        "name": "CONTEXT",
        "description": "Situational, background information.",
        "epistemic_weight": 0.5,
        "requires_verification": False,
        "color": "#4488ff",
    },
    "UNKNOWN": {
        "name": "UNKNOWN",
        "description": "Not enough information yet. Default landing lens.",
        "epistemic_weight": 0.0,
        "requires_verification": False,
        "color": "#888888",
    },
}

LENS_NAMES = list(LENSES.keys())


def is_valid_lens(lens: str) -> bool:
    """Check if a lens is valid."""
    return lens in LENSES


def get_lens_description(lens: str) -> str:
    """Get the description of a lens."""
    if lens in LENSES:
        return LENSES[lens]["description"]
    return "Unknown lens"


def get_lens_weight(lens: str) -> float:
    """Get the epistemic weight of a lens."""
    if lens in LENSES:
        return LENSES[lens]["epistemic_weight"]
    return 0.0


def get_lens_color(lens: str) -> str:
    """Get the color of a lens."""
    if lens in LENSES:
        return LENSES[lens]["color"]
    return "#ffffff"


# ============================================================
# CLI
# ============================================================

def main():
    """Display lens information."""
    print("📊 DataCube — Five Lenses")
    print("=" * 60)
    for lens, data in LENSES.items():
        print(f"\n{lens}:")
        print(f"  {data['description']}")
        print(f"  Weight: {data['epistemic_weight']}")
        print(f"  Verified required: {data['requires_verification']}")


if __name__ == "__main__":
    main()