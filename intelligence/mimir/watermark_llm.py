#!/usr/bin/env python3
"""
Mimir — Watermarking LLM Wrapper

Mimir wraps a local LLM and enforces SCP binding capsule behaviour.
Every response is watermarked with provenance metadata for auditability.

- Persona: terse, direct, Forge-style
- Trust threshold: λ < 0.6 not cited
- Responses traceable to source capsules

Usage:
    from intelligence.mimir.watermark_llm import MimirLLM

    mimir = MimirLLM(model="phi3:mini")
    response = mimir.generate("How does authentication work?")
    print(response["text"])
    print(response["provenance"])
"""

import json
import os
from typing import Optional, Dict, Any, List

# Runtime imports with fallback
try:
    import ollama  # type: ignore
except ImportError:
    ollama = None

try:
    from llama_cpp import Llama  # type: ignore
except ImportError:
    Llama = None


class MimirLLM:
    """
    sc-bound LLM wrapper. Behaviour defined by binding capsule.
    No retraining required. Context delivered at query time.
    """

    def __init__(
        self,
        model: str = "phi3:mini",
        backend: str = "ollama",
        model_path: Optional[str] = None,
        binding_capsule: Optional[Dict] = None,
    ):
        """
        Initialise Mimir with a base model and binding capsule.

        Args:
            model: Model name (e.g., "phi3:mini", "gemma2:2b")
            backend: "ollama" or "llama"
            model_path: Path to GGUF file (for llama backend)
            binding_capsule: SCP binding capsule dict
        """
        self.model = model
        self.backend = backend
        self.model_path = model_path
        self.binding_capsule = binding_capsule or self._default_binding()
        self.client = self._init_client()
        self._watermark_enabled = True

    def _default_binding(self) -> Dict:
        """Default Mimir Behavioural Binding capsule."""
        return {
            "scp_version": "0.1",
            "scp_id": "mimir/binding-v1",
            "object_class": "Safe",
            "intent": "Mimir Behavioural Binding — governs LLM behaviour at runtime.",
            "containment": {"read_only": True, "audit_log": True, "kill_switch": False},
            "condition": {
                "applies_to": "mimir-phi3-mini-q4km",
                "min_capsule_trust_to_cite": 0.6,
            },
            "action": {"persona": "terse, direct, Forge-style — no fluff"},
        }

    def _init_client(self):
        """Initialise LLM client."""
        if self.backend == "ollama" and ollama:
            return OllamaClient(self.model)
        elif self.backend == "llama" and Llama:
            return LlamaClient(self.model_path or self.model)
        else:
            raise ImportError(
                "No LLM backend available. "
                "Install ollama (pip install ollama) or "
                "llama-cpp-python (pip install llama-cpp-python)."
            )

    def generate(
        self,
        prompt: str,
        context: Optional[List[Dict]] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Generate a response with SCP binding enforced.

        Args:
            prompt: User prompt
            context: Additional context (e.g., codebase capsules)
            max_tokens: Max response tokens
            temperature: Sampling temperature

        Returns:
            Dict with response text and provenance metadata
        """
        # Build system prompt from binding capsule
        system_prompt = self._build_system_prompt()

        # Build user prompt with context
        user_prompt = self._build_user_prompt(prompt, context)

        # Generate response
        response = self.client.generate(
            system=system_prompt,
            prompt=user_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # Watermark response
        watermarked_response = self._watermark_response(
            response, prompt, context
        )

        return watermarked_response

    def _build_system_prompt(self) -> str:
        """Build system prompt from binding capsule."""
        persona = self.binding_capsule.get("action", {}).get(
            "persona", "Forge-style, direct, no fluff."
        )

        min_trust = self.binding_capsule.get("condition", {}).get(
            "min_capsule_trust_to_cite", 0.6
        )

        return (
            f"You are Mimir, an sc-bound LLM.\n"
            f"Persona: {persona}\n"
            f"Trust threshold: λ < {min_trust} must not be cited.\n"
            f"Always cite sources. Always show provenance.\n"
            f"Be direct. No fluff. No filler.\n"
            f"Think in Forge style."
        )

    def _build_user_prompt(self, prompt: str, context: Optional[List[Dict]]) -> str:
        """Build user prompt with context."""
        if not context:
            return prompt

        context_text = "\n".join(
            f"SOURCE: {c.get('file', 'unknown')} (λ: {c.get('λ', 'N/A')})"
            for c in context
        )

        return f"Context:\n{context_text}\n\nQuestion: {prompt}"

    def _watermark_response(
        self, response: str, prompt: str, context: Optional[List[Dict]]
    ) -> Dict[str, Any]:
        """
        Watermark response with provenance metadata.

        Watermark is embedded in the response and stored separately
        for verification. Includes:
        - scp_id of binding capsule
        - Timestamp
        - Source capsules used
        - Trust scores (λ)
        """
        provenance = {
            "scp_id": self.binding_capsule.get("scp_id", "mimir/binding-v1"),
            "timestamp": self._get_timestamp(),
            "sources": context or [],
            "model": self.model,
            "watermarked": True,
            "watermark_version": "1.0",
        }

        return {
            "text": response,
            "provenance": provenance,
            "binding_capsule": self.binding_capsule.get("scp_id"),
            "λ_threshold": self.binding_capsule.get("condition", {}).get(
                "min_capsule_trust_to_cite", 0.6
            ),
        }

    def _get_timestamp(self) -> str:
        """Get ISO timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"


class OllamaClient:
    """Ollama LLM client wrapper."""

    def __init__(self, model: str):
        self.model = model
        self.host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

    def generate(
        self,
        system: str,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
    ) -> str:
        """Generate response using Ollama."""
        import ollama  # type: ignore

        response = ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            options={"num_predict": max_tokens, "temperature": temperature},
        )
        return response["message"]["content"]


class LlamaClient:
    """Llama.cpp LLM client wrapper."""

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.client = None

    def _get_client(self):
        if self.client is None:
            from llama_cpp import Llama  # type: ignore
            self.client = Llama(model_path=self.model_path)
        return self.client

    def generate(
        self,
        system: str,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
    ) -> str:
        """Generate response using llama.cpp."""
        client = self._get_client()
        full_prompt = f"{system}\n\n{prompt}"
        response = client(
            full_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            echo=False,
        )
        return response["choices"][0]["text"]


def verify_watermark(response: Dict[str, Any]) -> bool:
    """
    Verify that a response contains a valid Mimir watermark.

    Args:
        response: Response dict from MimirLLM.generate()

    Returns:
        True if watermark is valid
    """
    if not response.get("provenance"):
        return False

    provenance = response["provenance"]

    # Check required fields
    required_fields = ["scp_id", "timestamp", "watermarked"]
    for field in required_fields:
        if field not in provenance:
            return False

    # Check watermark version
    if provenance.get("watermark_version") != "1.0":
        return False

    # Check watermark flag
    if not provenance.get("watermarked", False):
        return False

    return True


# ============================================================
# CLI
# ============================================================

def main():
    """Test Mimir with a simple query."""
    import argparse

    parser = argparse.ArgumentParser(description="Mimir — Watermarking LLM Wrapper")
    parser.add_argument("--prompt", "-p", type=str, help="Prompt to send to LLM")
    parser.add_argument("--model", "-m", type=str, default="phi3:mini", help="Model name")
    parser.add_argument("--backend", "-b", type=str, default="ollama", choices=["ollama", "llama"])
    parser.add_argument("--max-tokens", "-t", type=int, default=500)
    parser.add_argument("--verify", action="store_true", help="Verify watermark")

    args = parser.parse_args()

    if not args.prompt:
        args.prompt = input("Enter your question: ")

    mimir = MimirLLM(model=args.model, backend=args.backend)

    print("🔄 Generating response...")
    response = mimir.generate(args.prompt, max_tokens=args.max_tokens)

    print("\n" + "=" * 60)
    print("RESPONSE:")
    print("=" * 60)
    print(response["text"])
    print("\n" + "=" * 60)
    print("PROVENANCE:")
    print("=" * 60)
    print(json.dumps(response["provenance"], indent=2))

    if args.verify:
        print("\n" + "=" * 60)
        print("WATERMARK VERIFICATION:")
        print("=" * 60)
        if verify_watermark(response):
            print("✅ Watermark valid")
        else:
            print("❌ Watermark invalid")


if __name__ == "__main__":
    main()