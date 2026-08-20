#!/usr/bin/env python3
"""
BuddAI — CLI

Command-line interface for BuddAI.

Usage:
    buddai chat "thinking about a spinner robot"
    buddai learn "ESP32 uses ledcWrite, not analogWrite"
    buddai validate code.ino
    buddai memory
    buddai patterns "esp32"
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Optional


def chat_command(message: str, session_id: Optional[str] = None) -> None:
    """Chat with BuddAI."""
    try:
        from intelligence.buddai.personality import PersonalityEngine
        from intelligence.buddai.memory import MemorySystem

        personality = PersonalityEngine()
        memory = MemorySystem()

        intent = personality.detect_intent(message)
        response = personality.get_persona_response(intent)

        # Store short-term memory
        memory.remember(message, "short_term", tags=[intent.get("type", "general")])

        print(f"\n🧠 BuddAI: {response}")
        print(f"\n📋 Intent: {intent.get('type')} (confidence: {intent.get('confidence', 0):.2f})")

        if session_id:
            print(f"🔑 Session: {session_id}")

    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Make sure BuddAI is installed correctly.")
        sys.exit(1)


def learn_command(correction: str, tags: Optional[List[str]] = None) -> None:
    """Learn a correction."""
    try:
        from intelligence.buddai.learning import LearningEngine

        engine = LearningEngine()
        pattern_id = engine.learn(correction, tags)

        print(f"✅ Learned pattern #{pattern_id}")
        print(f"   Correction: {correction}")
        if tags:
            print(f"   Tags: {', '.join(tags)}")

    except ImportError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def validate_command(file_path: str, target: str = "esp32"):
    """Validate code file."""
    try:
        from intelligence.buddai.validators import ValidatorEngine

        path = Path(file_path)
        if not path.exists():
            print(f"❌ File not found: {file_path}")
            sys.exit(1)

        code = path.read_text()
        engine = ValidatorEngine()
        issues = engine.validate(code, target)

        if not issues:
            print(f"✅ Code validated: {file_path}")
            print("   No issues found.")
            return

        print(f"🔍 Code validation: {file_path}")
        print("=" * 60)

        for issue in issues:
            emoji = "❌" if issue["type"] == "error" else "⚠️" if issue["type"] == "warning" else "ℹ️"
            print(f"{emoji} {issue['validator']}: {issue['message']}")
            if issue.get("fix"):
                print(f"   💡 {issue['fix']}")
            if issue.get("line"):
                print(f"   📍 Line: {issue['line']}")

    except ImportError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def memory_command():
    """Show memory statistics."""
    try:
        from intelligence.buddai.memory import MemorySystem

        memory = MemorySystem()
        stats = memory.get_stats()

        print("🧠 BuddAI Memory")
        print("=" * 60)
        print(f"Short-term: {stats['short_term']['count']} memories (avg weight: {stats['short_term']['avg_weight']:.2f})")
        print(f"Long-term:  {stats['long_term']['count']} memories (avg weight: {stats['long_term']['avg_weight']:.2f})")
        print(f"Decay rate: {stats['decay_k']}")

        # Show recent memories
        memories = memory.recall("", limit=5)
        if memories:
            print("\n📝 Recent memories:")
            for m in memories:
                print(f"   - {m['content'][:60]}... (weight: {m['weight']:.2f})")

    except ImportError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def patterns_command(query: str = ""):
    """Show learned patterns."""
    try:
        from intelligence.buddai.learning import LearningEngine

        engine = LearningEngine()
        patterns = engine.get_patterns(query)

        if not patterns:
            print("No patterns found.")
            if query:
                print(f"Query: '{query}'")
            return

        print(f"📚 Learned patterns ({len(patterns)})")
        print("=" * 60)

        for p in patterns:
            print(f"#{p['id']}: {p['pattern']}")
            print(f"   Applied: {p.get('applied_count', 0)} times")
            print(f"   Created: {p.get('created', 'unknown')}")

    except ImportError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="BuddAI — Personal AI Exocortex",
        prog="buddai"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Chat with BuddAI")
    chat_parser.add_argument("message", type=str, help="Your message")
    chat_parser.add_argument("--session", "-s", type=str, help="Session ID")

    # Learn command
    learn_parser = subparsers.add_parser("learn", help="Learn a correction")
    learn_parser.add_argument("correction", type=str, help="Correction text")
    learn_parser.add_argument("--tags", "-t", nargs="+", help="Tags")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate code file")
    validate_parser.add_argument("file", type=str, help="Code file path")
    validate_parser.add_argument("--target", "-t", default="esp32", help="Target hardware")

    # Memory command
    subparsers.add_parser("memory", help="Show memory statistics")

    # Patterns command
    patterns_parser = subparsers.add_parser("patterns", help="Show learned patterns")
    patterns_parser.add_argument("query", nargs="?", default="", help="Search query")

    args = parser.parse_args()

    if args.command == "chat":
        chat_command(args.message, args.session)
    elif args.command == "learn":
        learn_command(args.correction, args.tags)
    elif args.command == "validate":
        validate_command(args.file, args.target)
    elif args.command == "memory":
        memory_command()
    elif args.command == "patterns":
        patterns_command(args.query)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
