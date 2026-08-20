#!/usr/bin/env python3
"""
Leighton Weight — Decay

Neutral-attractor decay for trust scores.

Formula:
    λ(t) = 1.00 + (λ₀ − 1.00) × e^(−kt)

Features:
- Decays toward 1.00 (neutral), not 0
- Asymmetric: recovery-from-below is harder than decay-from-above
- Per-domain decay constants

Usage:
    from core.leighton.decay import neutral_attractor, asymmetric_decay
"""

import math
from typing import Optional


def neutral_attractor(λ: float, k: float, time_diff: float) -> float:
    """
    Apply neutral-attractor decay.

    λ decays toward 1.00 (neutral) over time.

    Args:
        λ: Current trust score
        k: Decay constant (per-domain)
        time_diff: Time elapsed (in days)

    Returns:
        Decayed λ
    """
    if time_diff <= 0:
        return λ

    return 1.00 + (λ - 1.00) * math.exp(-k * time_diff)


def asymmetric_decay(λ: float, k: float, time_diff: float, asymmetry_factor: float = 1.5) -> float:
    """
    Apply asymmetric decay.

    Sub-neutral λ climbs back toward 1.00 more slowly than
    supra-neutral λ falls toward it.

    Args:
        λ: Current trust score
        k: Decay constant (per-domain)
        time_diff: Time elapsed (in days)
        asymmetry_factor: Recovery penalty (higher = slower recovery)

    Returns:
        Decayed λ
    """
    if time_diff <= 0:
        return λ

    # Calculate neutral-attractor decay
    decayed = neutral_attractor(λ, k, time_diff)

    # Apply asymmetry
    if λ < 1.00 and decayed > λ:
        # Recovering from below — slower
        recovery_factor = 1.0 / asymmetry_factor
        return λ + (decayed - λ) * recovery_factor

    if λ > 1.00 and decayed < λ:
        # Decaying from above — faster
        decay_factor = asymmetry_factor
        return λ - (λ - decayed) * decay_factor

    return decayed


def decay_lambda(
    λ: float,
    k: float,
    time_diff: float,
    asymmetric: bool = True,
    asymmetry_factor: float = 1.5,
) -> float:
    """
    Decay a trust score over time.

    Args:
        λ: Current trust score
        k: Decay constant (per-domain)
        time_diff: Time elapsed (in days)
        asymmetric: Apply asymmetric decay
        asymmetry_factor: Recovery penalty

    Returns:
        Decayed λ
    """
    if asymmetric:
        return asymmetric_decay(λ, k, time_diff, asymmetry_factor)
    else:
        return neutral_attractor(λ, k, time_diff)


def get_time_diff(start_time: str, end_time: Optional[str] = None) -> float:
    """
    Calculate time difference in days.

    Args:
        start_time: ISO timestamp
        end_time: ISO timestamp (default: now)

    Returns:
        Time difference in days
    """
    from datetime import datetime

    try:
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_time.replace('Z', '+00:00')) if end_time else datetime.utcnow()
        return (end - start).total_seconds() / 86400.0
    except (ValueError, TypeError):
        return 0.0


# ============================================================
# CLI
# ============================================================

def main():
    """Test decay."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Leighton Weight — Decay")
    parser.add_argument("λ", type=float, help="Initial λ")
    parser.add_argument("--days", "-d", type=float, default=30, help="Days elapsed")
    parser.add_argument("--k", "-k", type=float, default=0.01, help="Decay constant")
    parser.add_argument("--asymmetric", "-a", action="store_true", help="Use asymmetric decay")
    parser.add_argument("--factor", "-f", type=float, default=1.5, help="Asymmetry factor")

    args = parser.parse_args()

    initial = args.λ

    if args.asymmetric:
        decayed = asymmetric_decay(initial, args.k, args.days, args.factor)
        print(f"Asymmetric decay:")
    else:
        decayed = neutral_attractor(initial, args.k, args.days)
        print(f"Neutral-attractor decay:")

    print(f"  Initial λ: {initial:.3f}")
    print(f"  Days: {args.days}")
    print(f"  k: {args.k}")
    print(f"  Decayed λ: {decayed:.3f}")


if __name__ == "__main__":
    main()