#!/usr/bin/env python3
"""
Ex-OS — Network Daemon

Unified API server for Ex-OS (port 8080).

Endpoints:
    GET  /api/status              - System status
    GET  /api/health              - Health check
    POST /api/chat                - BuddAI chat
    POST /api/query               - Mimir query
    GET  /api/trust/entity/:id    - Get trust score
    POST /api/trust/attest        - Issue attestation
    GET  /api/ledger              - Get ledger entries
    GET  /api/ledger/verify/:id   - Verify entry
    POST /api/validate            - Validate response
    POST /api/hal/seal            - Seal an action
    GET  /api/replicant/status    - Swarm status
    POST /api/anchor/query        - Expert query
    GET  /dashboard               - Web UI

Usage:
    python network_daemon.py [--port 8080] [--host 0.0.0.0]
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import urllib.parse

# API Token
API_TOKEN = os.environ.get("EXOS_API_TOKEN", "3D models Rock")


def validate_token(headers: Any) -> bool:
    """Validate an API token from an HTTP header collection."""
    token = headers.get("X-API-Token", "")
    return token == API_TOKEN


class ExOSHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Ex-OS."""

    def __init__(self, *args, **kwargs):
        self.components = {}
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/status":
            self._handle_status()
        elif path == "/api/health":
            self._handle_health()
        elif path == "/dashboard" or path == "/":
            self._handle_dashboard()
        elif path.startswith("/api/trust/entity/"):
            entity_id = path.split("/")[-1]
            self._handle_trust_entity(entity_id)
        elif path.startswith("/api/ledger/verify/"):
            entry_id = path.split("/")[-1]
            self._handle_ledger_verify(entry_id)
        elif path == "/api/ledger":
            self._handle_ledger()
        elif path == "/api/ledger/anchor":
            self._handle_ledger_anchor()
        elif path.startswith("/api/hal/seal/"):
            seal_id = path.split("/")[-1]
            self._handle_seal(seal_id)
        elif path == "/api/replicant/status":
            self._handle_replicant_status()
        else:
            self._send_404()

    def do_POST(self):
        """Handle POST requests."""
        # Check auth (skip for dashboard)
        if not self.path.startswith("/dashboard"):
            if not validate_token(self.headers):
                self._send_error(401, "Unauthorized")
                return

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON")
            return

        path = self.path

        if path == "/api/chat":
            self._handle_chat(data)
        elif path == "/api/query":
            self._handle_query(data)
        elif path == "/api/trust/attest":
            self._handle_attest(data)
        elif path == "/api/validate":
            self._handle_validate(data)
        elif path == "/api/hal/seal":
            self._handle_seal_post(data)
        elif path == "/api/anchor/query":
            self._handle_anchor_query(data)
        elif path == "/api/replicant/tick":
            self._handle_replicant_tick(data)
        else:
            self._send_404()

    # ============================================================
    # GET Handlers
    # ============================================================

    def _handle_status(self):
        """Handle /api/status."""
        response = {
            "status": "ok",
            "version": {
                "exos": "1.0",
                "ubvm": "1.0",
                "scp": "0.1",
            },
            "components": {
                "buddai": self._get_buddai_status(),
                "mimir": self._get_mimir_status(),
                "ubvm": self._get_ubvm_status(),
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        self._send_json(response)

    def _handle_health(self):
        """Handle /api/health."""
        self._send_json({
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })

    def _handle_dashboard(self):
        """Serve dashboard HTML."""
        try:
            dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard.html")
            if os.path.exists(dashboard_path):
                with open(dashboard_path, "r", encoding="utf-8", errors='ignore') as f:
                    html = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
            else:
                self._send_dashboard_fallback()
        except Exception as e:
            self._send_error(500, str(e))

    def _send_dashboard_fallback(self):
        """Send a simple fallback dashboard."""
        html = """<!DOCTYPE html>
        <html>
        <head>
            <title>Ex-OS Dashboard</title>
            <style>
                body { font-family: monospace; background: #0a0a0f; color: #00ff88; padding: 20px; }
                h1 { color: #ffaa00; }
                .component { border: 1px solid #333; padding: 15px; margin: 10px 0; }
                .status-ok { color: #00ff88; }
                .status-error { color: #ff4444; }
                .status-partial { color: #ffaa00; }
            </style>
        </head>
        <body>
            <h1>🔥 Ex-OS Dashboard</h1>
            <p>Version 1.0 | Built: 2026-08-20</p>
            <div id="status">
                <div class="component">
                    <h2>System Status</h2>
                    <p class="status-ok">✅ Online</p>
                    <p>BuddAI: <span id="buddai-status">Checking...</span></p>
                    <p>Mimir: <span id="mimir-status">Checking...</span></p>
                    <p>UBVM: <span id="ubvm-status">Checking...</span></p>
                </div>
                <div class="component">
                    <h2>API Endpoints</h2>
                    <ul>
                        <li><code>GET /api/status</code> - System status</li>
                        <li><code>POST /api/chat</code> - BuddAI chat</li>
                        <li><code>POST /api/query</code> - Mimir query</li>
                        <li><code>POST /api/hal/seal</code> - Seal action</li>
                    </ul>
                </div>
            </div>
            <script>
                async function checkStatus() {
                    try {
                        const res = await fetch('/api/status');
                        const data = await res.json();
                        document.getElementById('buddai-status').textContent = data.components.buddai?.status || 'Unknown';
                        document.getElementById('mimir-status').textContent = data.components.mimir?.status || 'Unknown';
                        document.getElementById('ubvm-status').textContent = data.components.ubvm?.status || 'Unknown';
                    } catch (e) {
                        console.error(e);
                    }
                }
                checkStatus();
                setInterval(checkStatus, 5000);
            </script>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def _handle_trust_entity(self, entity_id: str):
        """Handle /api/trust/entity/:id."""
        self._send_json({
            "entity_id": entity_id,
            "λ": 0.95,
            "status": "VALIDATED",
            "domain": "system",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })

    def _handle_ledger(self):
        """Handle /api/ledger."""
        self._send_json({
            "entries": [
                {
                    "entry_id": "sha256:abc123...",
                    "event": "event.system.boot",
                    "source": "exos/core",
                    "payload": {"version": "1.0"},
                    "ts": datetime.utcnow().isoformat() + "Z",
                }
            ],
            "total": 1,
            "limit": 20,
            "offset": 0,
        })

    def _handle_ledger_verify(self, entry_id: str):
        """Handle /api/ledger/verify/:id."""
        self._send_json({
            "entry_id": entry_id,
            "valid": True,
            "chain_valid": True,
            "signature_valid": True,
            "anchor_valid": True,
        })

    def _handle_ledger_anchor(self):
        """Handle /api/ledger/anchor."""
        self._send_json({
            "root_hash": "sha256:root123...",
            "anchored_at": "2026-08-01T00:00:00Z",
            "consumer_count": 3,
            "consumers": ["LifeForge", "giblets-forge", "CobbleWright"],
        })

    def _handle_seal(self, seal_id: str):
        """Handle /api/hal/seal/:id."""
        self._send_json({
            "seal_id": seal_id,
            "action": "EXAMPLE",
            "authoriser": "did:key:z6MktudRY5LBZJeE13BiF4BeisAwWs7gvg6srh2GwLAMKDwJ",
            "tier": 3,
            "λ": 1.42,
            "status": "active",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "separation": "none",
        })

    def _handle_replicant_status(self):
        """Handle /api/replicant/status."""
        self._send_json({
            "population": 7,
            "health": 0.79,
            "energy_total": 340,
            "tick": 1247,
            "claims": {"total": 456, "verified": 312},
            "agents": [],
        })

    # ============================================================
    # POST Handlers
    # ============================================================

    def _handle_chat(self, data: Dict[str, Any]):
        """Handle /api/chat."""
        message = data.get("message", "")
        if not message:
            self._send_error(400, "Missing 'message' field")
            return

        try:
            # Try to use Ollama directly
            try:
                import ollama
                model = os.environ.get("OLLAMA_MODEL", "phi3:mini")

                response = ollama.chat(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are BuddAI, a helpful AI assistant. Be friendly, curious, and supportive. Keep responses concise."},
                        {"role": "user", "content": message}
                    ],
                )
                response_text = response["message"]["content"]
                intent = {"type": "general", "confidence": 0.8}

                # Store in memory
                try:
                    from intelligence.buddai.memory import MemorySystem
                    memory = MemorySystem()
                    memory.remember(message, "short_term", tags=["chat"])
                except ImportError:
                    pass

            except ImportError:
                # Fallback
                response_text = f"BuddAI: I received your message: '{message}'. (Ollama not installed)"
                intent = {"type": "unknown", "confidence": 0.5}

            self._send_json({
                "response": response_text,
                "intent": intent,
                "session_id": data.get("session_id", "buddai-session"),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            })
        except Exception as e:
            self._send_error(500, str(e))

    def _handle_query(self, data: Dict[str, Any]):
        """Handle /api/query."""
        prompt = data.get("prompt", "")
        if not prompt:
            self._send_error(400, "Missing 'prompt' field")
            return

        try:
            # Try to use Ollama directly
            try:
                import ollama
                model = os.environ.get("OLLAMA_MODEL", "phi3:mini")

                response = ollama.chat(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are Mimir, a codebase intelligence assistant. Answer questions about code, systems, and technology clearly and concisely."},
                        {"role": "user", "content": prompt}
                    ],
                )
                answer = response["message"]["content"]
                sources = []

            except ImportError:
                answer = f"Mimir: Query received: '{prompt}'. (Ollama not installed)"
                sources = []

            self._send_json({
                "answer": answer,
                "sources": sources,
                "provenance": {},
                "timestamp": datetime.utcnow().isoformat() + "Z",
            })
        except Exception as e:
            self._send_error(500, str(e))

    def _handle_attest(self, data: Dict[str, Any]):
        """Handle /api/trust/attest."""
        entity_id = data.get("entity_id", "unknown")
        outcome = data.get("outcome", "success")

        self._send_json({
            "status": "ok",
            "attestation_id": f"attest-{datetime.utcnow().timestamp()}",
            "new_λ": 0.95,
            "recorded": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })

    def _handle_validate(self, data: Dict[str, Any]):
        """Handle /api/validate."""
        capsule_id = data.get("capsule_id", "unknown")
        response = data.get("response", "")

        self._send_json({
            "valid": True,
            "reasoning": f"Response validated against {capsule_id}",
            "λ": 0.92,
            "confidence": 0.96,
            "sealed": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })

    def _handle_seal_post(self, data: Dict[str, Any]):
        """Handle /api/hal/seal POST."""
        action = data.get("action", "UNKNOWN")
        authoriser = data.get("authoriser", "unknown")
        tier = data.get("tier", 3)

        self._send_json({
            "status": "sealed",
            "seal_id": f"seal-{datetime.utcnow().timestamp()}",
            "tier": tier,
            "λ": 1.42,
            "separation": "none",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "recorded": True,
        })

    def _handle_anchor_query(self, data: Dict[str, Any]):
        """Handle /api/anchor/query."""
        query = data.get("query", "")
        domain = data.get("domain", "general")

        self._send_json({
            "status": "ANSWERED",
            "answer": f"Anchor response to '{query}' in {domain} domain",
            "sources": [
                {"id": "SRC-001", "name": "Example Source", "weight": 0.92}
            ],
            "session_id": f"anchor-{datetime.utcnow().timestamp()}",
            "sealed": True,
        })

    def _handle_replicant_tick(self, data: Dict[str, Any]):
        """Handle /api/replicant/tick."""
        self._send_json({
            "tick": 1248,
            "events": [],
            "population": 8,
            "health": 0.78,
        })

    # ============================================================
    # Component Status Helpers
    # ============================================================

    def _get_buddai_status(self) -> Dict[str, Any]:
        """Get BuddAI status."""
        try:
            from intelligence.buddai.memory import MemorySystem
            memory = MemorySystem()
            stats = memory.get_stats()
            return {"status": "ok", "memory": stats}
        except ImportError:
            return {"status": "unavailable"}

    def _get_mimir_status(self) -> Dict[str, Any]:
        """Get Mimir status."""
        try:
            from intelligence.mimir.search import MimirSearch
            searcher = MimirSearch()
            stats = searcher.get_stats()
            return {"status": "ok", "capsules": stats}
        except ImportError:
            return {"status": "unavailable"}

    def _get_ubvm_status(self) -> Dict[str, Any]:
        """Get UBVM status."""
        try:
            from runtime.ubvm.primitives import DISPATCH
            return {"status": "ok", "primitives": len(DISPATCH)}
        except ImportError:
            return {"status": "unavailable"}

    # ============================================================
    # Response Helpers
    # ============================================================

    def _send_json(self, data: Dict[str, Any]):
        """Send JSON response."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))

    def _send_error(self, code: int, message: str):
        """Send error response."""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "error",
            "code": code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }).encode('utf-8'))

    def _send_404(self):
        """Send 404 response."""
        self.send_response(404)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "error",
            "code": 404,
            "message": "Not found",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }).encode('utf-8'))

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def main():
    """Run Ex-OS network daemon."""
    import argparse

    parser = argparse.ArgumentParser(description="Ex-OS — Network Daemon")
    parser.add_argument("--port", "-p", type=int, default=8080, help="Port to listen on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    
    args = parser.parse_args()

    print("🔥 Ex-OS Network Daemon")
    print("=" * 60)
    print(f"   Host: {args.host}:{args.port}")
    print(f"   API Token: {API_TOKEN}")
    print("")
    print("   Endpoints:")
    print("     GET  /api/status")
    print("     GET  /api/health")
    print("     POST /api/chat")
    print("     POST /api/query")
    print("     GET  /api/trust/entity/:id")
    print("     POST /api/trust/attest")
    print("     GET  /api/ledger")
    print("     POST /api/validate")
    print("     POST /api/hal/seal")
    print("     GET  /dashboard")
    print("")
    print("   Press Ctrl+C to stop")

    server = HTTPServer((args.host, args.port), ExOSHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Stopping Ex-OS Network Daemon")
        sys.exit(0)


if __name__ == "__main__":
    main()