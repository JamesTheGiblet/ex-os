#!/usr/bin/env python3
"""
Ex-OS — CLI

Unified command-line interface for Ex-OS.

Usage:
    exos chat "thinking about a spinner robot"
    exos query "how does authentication work"
    exos ingest /path/to/repo
    exos run capsule.scp.json
    exos seal --action DEPLOY --tier 3
    exos status
    exos serve
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def chat_command(message: str, session: Optional[str] = None) -> None:
    """Chat with BuddAI."""
    try:
        import requests
        response = requests.post(
            "http://localhost:8080/api/chat",
            json={"message": message, "session_id": session},
            headers={"X-API-Token": "3D models Rock"}
        )
        data = response.json()
        print(f"\n🧠 BuddAI: {data.get('response', 'No response')}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure Ex-OS network daemon is running (exos serve)")


def query_command(query: str, repo: str = "."):
    """Query Mimir."""
    try:
        import requests
        response = requests.post(
            "http://localhost:8080/api/query",
            json={"prompt": query, "repo": repo},
            headers={"X-API-Token": "3D models Rock"}
        )
        data = response.json()
        print(f"\n📝 Answer: {data.get('answer', 'No answer')}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure Ex-OS network daemon is running (exos serve)")


def ingest_command(repo_path: str):
    """Ingest a repository."""
    try:
        from intelligence.mimir.ingest import ingest_repo
        print(f"📂 Ingesting: {repo_path}")
        result = ingest_repo(repo_path)
        print(f"✅ Created {result.get('capsules_created', 0)} capsules")
    except ImportError as e:
        print(f"❌ Error: {e}")


def run_command(capsule_path: str):
    """Run a capsule."""
    try:
        from runtime.ubvm.interpreter import run_capsule
        print(f"🚀 Running: {capsule_path}")
        result = run_capsule(capsule_path)
        print(f"📊 Status: {result.get('status', 'unknown')}")
    except ImportError as e:
        print(f"❌ Error: {e}")


def seal_command(action: str, tier: int):
    """Seal an action."""
    try:
        import requests
        response = requests.post(
            "http://localhost:8080/api/hal/seal",
            json={
                "action": action,
                "tier": tier,
                "authoriser": "did:key:cli"
            },
            headers={"X-API-Token": "3D models Rock"}
        )
        data = response.json()
        print(f"✅ Sealed: {data.get('seal_id', 'unknown')}")
        print(f"   Status: {data.get('status', 'unknown')}")
    except Exception as e:
        print(f"❌ Error: {e}")


def status_command():
    """Show system status."""
    try:
        import requests
        response = requests.get("http://localhost:8080/api/status")
        data = response.json()
        print("🔥 Ex-OS Status")
        print("=" * 60)
        print(f"Status: {data.get('status', 'unknown')}")
        print(f"Version: {data.get('version', {}).get('exos', 'unknown')}")
        print(f"\nComponents:")
        for name, status in data.get('components', {}).items():
            print(f"   {name}: {status.get('status', 'unknown')}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure Ex-OS network daemon is running (exos serve)")


def serve_command(port: int = 8080):
    """Start the network daemon."""
    try:
        from integration.network_daemon import main as daemon_main
        import sys
        sys.argv = ["network_daemon.py", "--port", str(port)]
        daemon_main()
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Make sure integration.network_daemon exists")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Ex-OS — Sovereign Semantic Operating System",
        prog="exos"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Chat with BuddAI")
    chat_parser.add_argument("message", type=str, help="Your message")
    chat_parser.add_argument("--session", "-s", type=str, help="Session ID")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query Mimir")
    query_parser.add_argument("query", type=str, help="Your question")
    query_parser.add_argument("--repo", "-r", type=str, default=".", help="Repository path")

    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest a repository")
    ingest_parser.add_argument("repo", type=str, help="Repository path")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a capsule")
    run_parser.add_argument("capsule", type=str, help="Capsule file path")

    # Seal command
    seal_parser = subparsers.add_parser("seal", help="Seal an action")
    seal_parser.add_argument("--action", "-a", type=str, required=True, help="Action to seal")
    seal_parser.add_argument("--tier", "-t", type=int, default=3, help="Tier (1-5)")

    # Status command
    subparsers.add_parser("status", help="Show system status")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start network daemon")
    serve_parser.add_argument("--port", "-p", type=int, default=8080, help="Port to listen on")

    args = parser.parse_args()

    if args.command == "chat":
        chat_command(args.message, args.session)
    elif args.command == "query":
        query_command(args.query, args.repo)
    elif args.command == "ingest":
        ingest_command(args.repo)
    elif args.command == "run":
        run_command(args.capsule)
    elif args.command == "seal":
        seal_command(args.action, args.tier)
    elif args.command == "status":
        status_command()
    elif args.command == "serve":
        serve_command(args.port)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
