#!/usr/bin/env python3
"""
BuddAI — Server

API server and chat interface for BuddAI.

Endpoints:
    GET /api/buddai/status
    POST /api/buddai/chat
    POST /api/buddai/learn
    POST /api/buddai/validate
    GET /api/buddai/memory

Usage:
    python server.py --port 8000
"""

from email import message
from email.mime import message
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from intelligence.buddai import memory

from http.server import BaseHTTPRequestHandler, HTTPServer


class BuddaiHandler(BaseHTTPRequestHandler):
    """HTTP request handler for BuddAI."""

    def __init__(self, *args, **kwargs):
        self.buddai = None
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/api/buddai/status":
            self._send_status()
        elif self.path == "/api/buddai/memory":
            self._send_memory()
        else:
            self._send_404()

    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON")
            return

        if self.path == "/api/buddai/chat":
            self._handle_chat(data)
        elif self.path == "/api/buddai/learn":
            self._handle_learn(data)
        elif self.path == "/api/buddai/validate":
            self._handle_validate(data)
        else:
            self._send_404()

    def _send_status(self):
        """Send status response."""
        response = {
            "status": "ok",
            "name": "BuddAI",
            "version": "5.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        self._send_json(response)

    def _send_memory(self):
        """Send memory stats."""
        try:
            from intelligence.buddai.memory import MemorySystem
            memory = MemorySystem()
            stats = memory.get_stats()
            self._send_json(stats)
        except Exception as e:
            self._send_error(500, str(e))

    def _handle_chat(self, data: Dict[str, Any]):
        """Handle chat request."""
        message = data.get("message", "")
        session_id = data.get("session_id")

        if not message:
            self._send_error(400, "Missing 'message' field")
            return

        try:
            from intelligence.buddai.personality import PersonalityEngine
            from intelligence.buddai.memory import MemorySystem
            from intelligence.buddai.learning import LearningEngine

            personality = PersonalityEngine()
            memory = MemorySystem()
            learning = LearningEngine()

            # Detect intent
            intent = personality.detect_intent(message)
            response = personality.get_persona_response(intent)

            intent_type = intent.get("type")
            if isinstance(intent_type, str) and intent_type in {"correction", "learning"}:
                memory.remember(message, "short_term", tags=[intent_type])

            # Apply learned patterns if code is present
            if "code" in data:
                code = data.get("code", "")
                patterns = learning.apply_patterns(code)
                if patterns != code:
                    response += "\n\n🔄 Applied learning patterns."

            result = {
                "response": response,
                "intent": intent,
                "session_id": session_id or "buddai-session",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
            self._send_json(result)

        except Exception as e:
            self._send_error(500, str(e))

    def _handle_learn(self, data: Dict[str, Any]):
        """Handle learn request."""
        correction = data.get("correction", "")
        tags = data.get("tags", [])

        if not correction:
            self._send_error(400, "Missing 'correction' field")
            return

        try:
            from intelligence.buddai.learning import LearningEngine
            learning = LearningEngine()
            pattern_id = learning.learn(correction, tags)

            result = {
                "status": "ok",
                "pattern_id": pattern_id,
                "message": "Pattern learned successfully",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
            self._send_json(result)

        except Exception as e:
            self._send_error(500, str(e))

    def _handle_validate(self, data: Dict[str, Any]):
        """Handle validate request."""
        code = data.get("code", "")
        target = data.get("target", "esp32")

        if not code:
            self._send_error(400, "Missing 'code' field")
            return

        try:
            from intelligence.buddai.validators import ValidatorEngine
            engine = ValidatorEngine()
            issues = engine.validate(code, target)

            result = {
                "status": "ok",
                "issues": issues,
                "count": len(issues),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
            self._send_json(result)

        except Exception as e:
            self._send_error(500, str(e))

    def _send_json(self, data: Dict[str, Any]):
        """Send JSON response."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))

    def _send_error(self, code: int, message: str):
        """Send error response."""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "error",
            "code": code,
            "message": message,
        }).encode('utf-8'))

    def _send_404(self):
        """Send 404 response."""
        self.send_response(404)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "error",
            "code": 404,
            "message": "Not found"
        }).encode('utf-8'))

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def main():
    """Run BuddAI server."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="BuddAI — API Server")
    parser.add_argument("--port", "-p", type=int, default=8000, help="Port to listen on")
    parser.add_argument("--host", "-h", type=str, default="0.0.0.0", help="Host to bind to")

    args = parser.parse_args()

    print(f"🔄 Starting BuddAI Server v5.0")
    print(f"   Host: {args.host}:{args.port}")
    print(f"   Endpoints:")
    print(f"     GET  /api/buddai/status")
    print(f"     POST /api/buddai/chat")
    print(f"     POST /api/buddai/learn")
    print(f"     POST /api/buddai/validate")
    print(f"     GET  /api/buddai/memory")

    server = HTTPServer((args.host, args.port), BuddaiHandler)
    print(f"\n✅ Server running at http://{args.host}:{args.port}")
    print("   Press Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")


if __name__ == "__main__":
    main()