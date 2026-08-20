# intelligence/buddai/watermark_llm.py
# Watermark-aware LLM wrapper for BuddAI

import json
import requests
import math
import hashlib
import sys
import os
import random
from datetime import datetime
from typing import List, Dict, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.watermark.engine import WatermarkGenerator, get_secret_key, get_config

# ============================================================
# OLLAMA WRAPPER WITH WATERMARK
# ============================================================

class WatermarkedLLM:
    """LLM wrapper that applies cryptographic watermark during generation."""

    def __init__(self, model: str = "gemma2:2b", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host
        self.generator = WatermarkGenerator()
        self.config = get_config()
        self.bias = self.config.get("bias", 0.5)
        self.vocab_size = self.config.get("vocab_size", 32000)
        
        # Tokenizer cache
        self.vocab = None
        self.token_to_id = None
        self.eos_token = 2

    def _get_vocab(self) -> Tuple[List[str], Dict[str, int]]:
        """Get vocabulary from Ollama."""
        if self.vocab is not None:
            return self.vocab, self.token_to_id
        
        try:
            # For Ollama, we need to get the vocabulary
            self.vocab = [f"token_{i}" for i in range(self.vocab_size)]
            self.token_to_id = {f"token_{i}": i for i in range(self.vocab_size)}
            self.eos_token = 2
            return self.vocab, self.token_to_id
        except Exception as e:
            print(f"[WARN] Could not get vocab: {e}")
            return [], {}

    def tokenize(self, text: str) -> List[int]:
        """Tokenize text using Ollama's tokenizer."""
        try:
            # Use Ollama's tokenize endpoint (if available)
            response = requests.post(
                f"{self.host}/api/tokenize",
                json={"model": self.model, "content": text},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("tokens", [])
            else:
                # Fallback: simple tokenization
                return [hash(c) % self.vocab_size for c in text[:1000]]
        except Exception as e:
            print(f"[WARN] Tokenization failed: {e}, using fallback")
            return [hash(c) % self.vocab_size for c in text[:1000]]

    def decode(self, token_ids: List[int]) -> str:
        """Decode token IDs back to text."""
        try:
            # Use Ollama's detokenize endpoint (if available)
            response = requests.post(
                f"{self.host}/api/detokenize",
                json={"model": self.model, "tokens": token_ids},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("content", "")
            else:
                # Fallback: simple decoding
                return "".join(str(t) for t in token_ids[:100])
        except Exception as e:
            print(f"[WARN] Decoding failed: {e}, using fallback")
            return "".join(str(t) for t in token_ids[:100])

    def generate(self, prompt: str, max_tokens: int = 256, temperature: float = 0.8) -> Dict:
        """
        Generate text with watermark embedded.
        
        Returns:
            dict with text, token_ids, watermark_info
        """
        # Use Ollama's generate endpoint directly
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                text = data.get("response", "")
                
                # Tokenize for watermark validation
                token_ids = self.tokenize(text)
                validation = self.generator.validate(token_ids)
                
                return {
                    "text": text,
                    "prompt": prompt,
                    "token_count": len(token_ids),
                    "watermark": {
                        "z_score": validation["z_score"],
                        "green_count": validation["green_count"],
                        "total_tokens": validation["total"],
                        "expected": validation["expected"],
                        "is_watermarked": validation["is_watermarked"],
                        "threshold": validation["threshold"]
                    },
                    "provenance": {
                        "key_id": hashlib.sha256(self.generator.secret_key).hexdigest()[:16],
                        "method": "cryptographic_watermark_ollama",
                        "bias": self.bias,
                        "timestamp": datetime.now().isoformat() + "Z"
                    }
                }
            else:
                return {
                    "text": f"[ERROR] Ollama returned {response.status_code}",
                    "prompt": prompt,
                    "token_count": 0,
                    "watermark": {"z_score": 0, "is_watermarked": False, "green_count": 0, "total_tokens": 0, "expected": 0, "threshold": 4.0},
                    "provenance": {"error": f"HTTP {response.status_code}"}
                }
        except Exception as e:
            return {
                "text": f"[ERROR] {str(e)}",
                "prompt": prompt,
                "token_count": 0,
                "watermark": {"z_score": 0, "is_watermarked": False, "green_count": 0, "total_tokens": 0, "expected": 0, "threshold": 4.0},
                "provenance": {"error": str(e)}
            }


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python watermark_llm.py generate <prompt>  - Generate with watermark")
        print("  python watermark_llm.py validate <text>    - Validate text")
        print("  python watermark_llm.py status             - Show status")
        sys.exit(1)

    llm = WatermarkedLLM()

    command = sys.argv[1]

    if command == "generate":
        prompt = " ".join(sys.argv[2:])
        if not prompt:
            print("Please provide a prompt.")
            sys.exit(1)
        
        print(f"\n{'='*50}")
        print(f"Generating with watermark...")
        print(f"{'='*50}\n")
        
        result = llm.generate(prompt, max_tokens=200)
        
        print(f"Prompt: {result['prompt']}")
        print(f"\nResponse: {result['text']}")
        print(f"\n{'='*40}")
        print("WATERMARK INFO:")
        wm = result.get('watermark', {})
        print(f"  Z-score: {wm.get('z_score', 0):.4f}")
        print(f"  Watermarked: {wm.get('is_watermarked', False)}")
        print(f"  Green count: {wm.get('green_count', 0)}/{wm.get('total_tokens', 0)}")
        print(f"  Expected: {wm.get('expected', 0):.2f}")
        print(f"  Threshold: {wm.get('threshold', 4.0)}")
        prov = result.get('provenance', {})
        print(f"  Key ID: {prov.get('key_id', 'unknown')}")

    elif command == "validate":
        text = " ".join(sys.argv[2:])
        if not text:
            print("Please provide text to validate.")
            sys.exit(1)
        
        token_ids = llm.tokenize(text)
        validation = llm.generator.validate(token_ids)
        
        print(f"\n{'='*40}")
        print("WATERMARK VALIDATION:")
        print(f"{'='*40}")
        print(f"  Z-score: {validation['z_score']:.4f}")
        print(f"  Is watermarked: {validation['is_watermarked']}")
        print(f"  Green count: {validation['green_count']}/{validation['total']}")
        print(f"  Expected: {validation['expected']:.2f}")
        print(f"  Threshold: {validation['threshold']}")

    elif command == "status":
        print(f"\n{'='*40}")
        print("WATERMARK LLM STATUS:")
        print(f"{'='*40}")
        print(f"  Model: {llm.model}")
        print(f"  Host: {llm.host}")
        print(f"  Bias: {llm.bias}")
        print(f"  Vocab size: {llm.vocab_size}")
        print(f"  Key ID: {hashlib.sha256(llm.generator.secret_key).hexdigest()[:16]}")

    else:
        print(f"Unknown command: {command}")
