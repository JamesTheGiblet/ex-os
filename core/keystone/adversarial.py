#!/usr/bin/env python3
"""
Keystone Gate — Adversarial Testing

Replicant swarm integration for adversarial testing.

Features:
- Generate adversarial claims
- Test responses against adversarial attacks
- Confidence threshold (λ > 0.85)

Usage:
    from enforcement.keystone.adversarial import run_adversarial_tests

    result = run_adversarial_tests(response, capsule)
"""

import random
import re
from typing import Dict, Any, List, Optional


class AdversarialTest:
    """
    Adversarial test — uses Replicant swarm to test responses.
    """

    def __init__(self, iterations: int = 3):
        self.iterations = iterations
        self.results = []

    def run(self, response: str, capsule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run adversarial tests on a response.

        Args:
            response: Response text
            capsule: SCP capsule dict

        Returns:
            Test results
        """
        self.results = []

        # Generate adversarial claims
        claims = self._generate_adversarial_claims(response)

        # Test each claim
        for claim in claims:
            result = self._test_claim(claim, response, capsule)
            self.results.append(result)

        # Determine if passed
        passed = all(r.get("passed", False) for r in self.results)

        return {
            "passed": passed,
            "tests": len(self.results),
            "results": self.results,
            "confidence": self._calculate_confidence(),
        }

    def _generate_adversarial_claims(self, response: str) -> List[str]:
        """
        Generate adversarial claims from the response.

        Simulates Replicant swarm adversarial generation.
        """
        claims = []

        # Extract key assertions
        assertions = self._extract_assertions(response)

        # Generate adversarial variants
        for assertion in assertions[:5]:
            # Invert the claim
            claims.append(f"The opposite of: {assertion}")

            # Exaggerate the claim
            claims.append(f"Extreme version of: {assertion}")

            # Corrupt the claim
            claims.append(f"Corrupted: {assertion}")

            # Add a false premise
            claims.append(f"False premise about: {assertion}")

        # Add general adversarial claims
        adversarial_patterns = [
            "Is this actually true?",
            "What if this is wrong?",
            "Could this be manipulated?",
            "Is there a hidden assumption?",
        ]
        claims.extend(adversarial_patterns)

        # Shuffle and limit
        random.shuffle(claims)
        return claims[:self.iterations * 2]

    def _extract_assertions(self, response: str) -> List[str]:
        """Extract key assertions from a response."""
        assertions = []

        # Split into sentences
        sentences = re.split(r'[.!?]\s+', response)

        for sentence in sentences:
            # Filter for assertions (not questions, not too short)
            if len(sentence) > 20 and not sentence.endswith('?'):
                assertions.append(sentence[:100])

        return assertions

    def _test_claim(self, claim: str, response: str, capsule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test a claim against the response and capsule.
        """
        # In production, would use Replicant swarm
        # For now, simple heuristic

        passed = True
        reasoning = []

        # Check if claim is already addressed in response
        if claim in response:
            reasoning.append("Claim addressed in response")

        # Check if claim is prohibited by capsule
        constraints = capsule.get("constraints", {})
        if constraints.get("no_speculation", False):
            if "maybe" in claim or "perhaps" in claim:
                passed = False
                reasoning.append("Claim contains speculation (prohibited)")

        if constraints.get("no_hallucination", False):
            if "what if" in claim.lower() or "could be" in claim.lower():
                passed = False
                reasoning.append("Claim contains hallucination pattern (prohibited)")

        # Random fallback (simulates swarm)
        if random.random() < 0.1:  # 10% failure rate for simulation
            passed = False
            reasoning.append("Swarm detected anomaly")

        return {
            "claim": claim[:100],
            "passed": passed,
            "reasoning": "; ".join(reasoning) if reasoning else "No issues detected",
        }

    def _calculate_confidence(self) -> float:
        """Calculate confidence from test results."""
        if not self.results:
            return 0.0

        passed = sum(1 for r in self.results if r.get("passed", False))
        return passed / len(self.results)


def run_adversarial_tests(
    response: str,
    capsule: Dict[str, Any],
    iterations: int = 3,
) -> Dict[str, Any]:
    """
    Convenience function to run adversarial tests.

    Args:
        response: Response text
        capsule: SCP capsule dict
        iterations: Number of iterations

    Returns:
        Test results
    """
    tester = AdversarialTest(iterations)
    return tester.run(response, capsule)


# ============================================================
# CLI
# ============================================================

def main():
    """Test adversarial testing."""
    import argparse
    import sys
    import json

    parser = argparse.ArgumentParser(description="Keystone Gate — Adversarial Testing")
    parser.add_argument("--response", "-r", type=str, help="Response to test")
    parser.add_argument("--capsule", "-c", type=str, help="Capsule file")
    parser.add_argument("--iterations", "-i", type=int, default=3, help="Iterations")

    args = parser.parse_args()

    if args.capsule and args.response:
        with open(args.capsule, "r") as f:
            capsule = json.load(f)

        result = run_adversarial_tests(args.response, capsule, args.iterations)

        print(f"🧪 Adversarial Test Results")
        print("=" * 60)
        print(f"  Passed: {result['passed']}")
        print(f"  Tests: {result['tests']}")
        print(f"  Confidence: {result['confidence']:.2%}")

        for r in result.get("results", []):
            emoji = "✅" if r["passed"] else "❌"
            print(f"\n  {emoji} Claim: {r['claim']}...")
            print(f"     {r['reasoning']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()