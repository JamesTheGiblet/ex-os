# core/watermark/engine.py
# Cryptographic watermark for Ex-OS text generation

import hashlib
import secrets
import math
import json
import os
import random
from pathlib import Path
from typing import List, Set, Optional

# ============================================================
# CONFIGURATION
# ============================================================

WATERMARK_DIR = "watermark"
KEY_FILE = f"{WATERMARK_DIR}/secret.key"
CONFIG_FILE = f"{WATERMARK_DIR}/config.json"

DEFAULT_BIAS = 0.5
DEFAULT_Z_THRESHOLD = 4.0
VOCAB_SIZE = 32000  # Typical LLM vocab size

# ============================================================
# KEY MANAGEMENT
# ============================================================

def ensure_dir():
    Path(WATERMARK_DIR).mkdir(exist_ok=True)


def get_secret_key() -> bytes:
    """Get or generate the secret key."""
    ensure_dir()
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    else:
        key = secrets.token_bytes(32)
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        return key


def get_config() -> dict:
    """Get watermark config."""
    ensure_dir()
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        config = {
            "bias": DEFAULT_BIAS,
            "z_threshold": DEFAULT_Z_THRESHOLD,
            "vocab_size": VOCAB_SIZE,
            "version": "1.0"
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        return config


# ============================================================
# WATERMARK GENERATOR
# ============================================================

class WatermarkGenerator:
    """Cryptographic watermark for text generation."""

    def __init__(self, secret_key: Optional[bytes] = None, vocab_size: int = VOCAB_SIZE):
        self.secret_key = secret_key or get_secret_key()
        self.vocab_size = vocab_size
        self.config = get_config()
        self.bias = self.config.get("bias", DEFAULT_BIAS)
        self._cache = {}

    def _get_green_list(self, prev_token_id: int, step: int) -> Set[int]:
        """Deterministically generate the green list for a given context."""
        cache_key = (prev_token_id, step)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Create deterministic seed
        data = (
            self.secret_key +
            prev_token_id.to_bytes(4, 'big') +
            step.to_bytes(4, 'big')
        )
        seed = int(hashlib.sha256(data).hexdigest(), 16)

        # Shuffle vocabulary deterministically
        rng = random.Random(seed)
        indices = list(range(self.vocab_size))
        rng.shuffle(indices)

        # First half is green
        green = set(indices[:self.vocab_size // 2])

        # Cache with size limit
        self._cache[cache_key] = green
        if len(self._cache) > 1000:
            keys = list(self._cache.keys())[:len(self._cache) - 500]
            for k in keys:
                del self._cache[k]

        return green

    def apply_bias(self, logits: List[float], prev_token_id: int, step: int, bias: Optional[float] = None) -> List[float]:
        """Apply watermark bias to logits."""
        if bias is None:
            bias = self.bias

        green_list = self._get_green_list(prev_token_id, step)

        for token_id in range(self.vocab_size):
            if token_id in green_list:
                if token_id < len(logits):
                    logits[token_id] += bias

        return logits

    def validate(self, token_ids: List[int]) -> dict:
        """Validate a text's watermark."""
        if not token_ids:
            return {
                "z_score": 0.0,
                "green_count": 0,
                "total": 0,
                "expected": 0,
                "is_watermarked": False,
                "threshold": self.config.get("z_threshold", DEFAULT_Z_THRESHOLD)
            }

        green_count = 0
        prev_token = 0
        self._cache.clear()

        for i, token in enumerate(token_ids):
            green_list = self._get_green_list(prev_token, i)
            if token in green_list:
                green_count += 1
            prev_token = token

        n = len(token_ids)
        expected = n * 0.5
        variance = n * 0.25
        z_score = (green_count - expected) / math.sqrt(variance)

        threshold = self.config.get("z_threshold", DEFAULT_Z_THRESHOLD)

        return {
            "z_score": z_score,
            "green_count": green_count,
            "total": n,
            "expected": expected,
            "is_watermarked": z_score > threshold,
            "threshold": threshold
        }


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python engine.py genkey          - Generate a new secret key")
        print("  python engine.py config          - Show current config")
        sys.exit(1)

    command = sys.argv[1]

    if command == "genkey":
        key = get_secret_key()
        print(f"✅ Key generated: {hashlib.sha256(key).hexdigest()[:16]}")
        print(f"   Stored at: {KEY_FILE}")

    elif command == "config":
        config = get_config()
        print(json.dumps(config, indent=2))

    else:
        print(f"Unknown command: {command}")
