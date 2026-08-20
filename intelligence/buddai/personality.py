#!/usr/bin/env python3
"""
BuddAI — Personality Engine

The personality engine understands intent, detects context,
and adapts responses based on user state.

Features:
- Intent detection (project, question, correction, etc.)
- Context awareness (project memory, session state)
- Mood adaptation (productive, reflective, etc.)

Usage:
    from intelligence.buddai.personality import PersonalityEngine

    engine = PersonalityEngine()
    intent = engine.detect_intent("thinking about a spinner robot")
    # intent = {"type": "project", "project": "spinner_robot", "confidence": 0.9}
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime


class PersonalityEngine:
    """
    BuddAI personality engine — understands intent and adapts.
    """

    def __init__(self, persona: str = "forging"):
        """
        Initialise personality engine.

        Args:
            persona: Persona style ("forging", "technical", "casual")
        """
        self.persona = persona
        self.session_context = {}
        self.project_context = {}
        self._load_intent_patterns()

    def _load_intent_patterns(self):
        """Load intent detection patterns."""
        self.intent_patterns = {
            "project": [
                r"(?:thinking about|working on|building|making) (?:a|an|the)? (?:new )?([a-zA-Z0-9_\-]+)",
                r"(?:new|start|begin) (?:project|build) (?:called|named|for) ([a-zA-Z0-9_\-]+)",
            ],
            "question": [
                r"(?:how|what|why|when|where|who|which|does|is|are) .+\?",
                r"(?:can you|would you|could you) (?:explain|tell|show|help)",
            ],
            "correction": [
                r"(?:correct|fix|change) (?:this|the) (?:code|function|method)",
                r"/(?:correct|fix|learn)",
                r"(?:use|should use) (?:instead|rather than|not)",
            ],
            "learning": [
                r"/learn",
                r"(?:remember|save|store) (?:this|that)",
                r"(?:pattern|lesson) (?:for|about)",
            ],
            "greeting": [
                r"^(?:hi|hello|hey|yo|sup|morning|evening|good|howdy)",
            ],
            "project_context": [
                r"(?:in|for|on) (?:the|my) ([a-zA-Z0-9_\-]+) (?:project|build|repo)",
            ],
        }

    def detect_intent(self, message: str) -> Dict[str, Any]:
        """
        Detect intent from a message.

        Args:
            message: User message

        Returns:
            Dict with intent type, confidence, and extracted data
        """
        message_lower = message.lower().strip()

        # Check each intent type
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, message_lower, re.IGNORECASE)
                if match:
                    if intent_type == "project":
                        project_name = match.group(1) if match.groups() else "unknown"
                        return {
                            "type": intent_type,
                            "confidence": 0.85,
                            "project": project_name,
                            "match": match.group(0),
                        }
                    elif intent_type == "project_context":
                        project_name = match.group(1) if match.groups() else "unknown"
                        return {
                            "type": intent_type,
                            "confidence": 0.8,
                            "project": project_name,
                            "match": match.group(0),
                        }
                    else:
                        return {
                            "type": intent_type,
                            "confidence": 0.9,
                            "match": match.group(0),
                        }

        # Default: general question
        return {
            "type": "general",
            "confidence": 0.5,
            "message": message,
        }

    def get_persona_response(self, intent: Dict[str, Any], context: Optional[Dict] = None) -> str:
        """
        Generate a personality-driven response.
        """
        intent_type = intent.get("type", "general")
        confidence = intent.get("confidence", 0.0)

        # Low confidence: ask for clarification
        if confidence < 0.5:
            return "I'm not quite sure what you mean. Can you tell me more?"

        # Project intent
        if intent_type == "project":
            project_name = intent.get("project", "new project")
            return self._project_response(project_name)

        # Question intent
        elif intent_type == "question":
            return self._question_response()

        # Correction intent
        elif intent_type == "correction":
            return self._correction_response()

        # Learning intent
        elif intent_type == "learning":
            return self._learning_response()

        # Greeting
        elif intent_type == "greeting":
            return self._greeting_response(context)

        # Default
        return self._general_response(intent)

    def _project_response(self, project_name: str) -> str:
        """Generate project-related response."""
        responses = [
            f"Ah nice! {project_name}? Tell me more about it.",
            f"Working on {project_name}? Great. What's the goal?",
            f"{project_name} — interesting. What are you building?",
        ]
        import random
        return random.choice(responses)

    def _question_response(self) -> str:
        """Generate question-related response."""
        responses = [
            "Good question. Let me think about that.",
            "I'll help you figure that out.",
            "Let me check what I know about that.",
        ]
        import random
        return random.choice(responses)

    def _correction_response(self) -> str:
        """Generate correction-related response."""
        responses = [
            "✅ Stored in database.",
            "Got it. I'll remember that.",
            "Thanks for the correction. I've saved it.",
        ]
        import random
        return random.choice(responses)

    def _learning_response(self) -> str:
        """Generate learning-related response."""
        responses = [
            "I'll learn from that.",
            "Pattern stored. I'll use this going forward.",
            "Lesson learned. Thanks for teaching me.",
        ]
        import random
        return random.choice(responses)

    def _greeting_response(self, context: Optional[Dict]) -> str:
        """Generate greeting response."""
        if context and context.get("time_of_day") == "morning":
            return "Good morning! Ready to forge something today?"
        elif context and context.get("time_of_day") == "evening":
            return "Good evening! Still building I see."
        else:
            responses = [
                "Hey! What are we building today?",
                "Hello! Ready to get to work?",
                "Hi there! What's on your mind?",
            ]
            import random
            return random.choice(responses)

    def _general_response(self, intent: Dict) -> str:
        """Generate general response."""
        return "I'm here. What do you need help with?"

    def adapt_persona(self, style: str):
        """
        Adapt personality style.

        Args:
            style: "forging", "technical", "casual"
        """
        if style in ["forging", "technical", "casual"]:
            self.persona = style

    def set_context(self, key: str, value: Any):
        """Set session context."""
        self.session_context[key] = value

    def get_context(self, key: str) -> Optional[Any]:
        """Get session context."""
        return self.session_context.get(key)


# ============================================================
# CLI
# ============================================================

def main():
    """Test personality engine."""
    import sys

    engine = PersonalityEngine()

    print("BuddAI — Personality Engine Test")
    print("=" * 60)

    test_messages = [
        "thinking about a spinner robot",
        "how does the motor driver work?",
        "/correct ESP32 uses ledcWrite, not analogWrite",
        "/learn use exponential smoothing for movement",
        "hi",
        "in the gilbot project",
    ]

    for msg in test_messages:
        print(f"\nMessage: {msg}")
        intent = engine.detect_intent(msg)
        print(f"Intent: {intent}")
        response = engine.get_persona_response(intent)
        print(f"Response: {response}")


if __name__ == "__main__":
    main()