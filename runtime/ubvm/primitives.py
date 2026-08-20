#!/usr/bin/env python3
"""
UBVM — Core Primitives

The only place executable logic lives in UBVM.

Primitives are registered in DISPATCH and called by capsules.

Core primitives:
- log: Write a message
- emit_event: Append to event bus
- http_request: HTTP GET/POST
- read_file: Read a file
- write_file: Write a file
- exec: Run a shell command (requires UBC_ALLOW_EXEC=1)
- validate_self: Validate the running capsule

Usage:
    from runtime.ubvm.primitives import DISPATCH, register_primitive

    # Register a new primitive
    register_primitive("my_primitive", my_function)
"""

import os
import json
import subprocess
from typing import Dict, Any, Callable, Optional
from datetime import datetime

try:
    import requests
except ImportError:
    requests = None


# ============================================================
# Dispatch Table
# ============================================================

DISPATCH: Dict[str, Callable] = {}


def register_primitive(name: str, func: Callable):
    """
    Register a primitive in the dispatch table.

    Args:
        name: Primitive name (snake_case)
        func: Function with signature (params: dict, context: dict) -> dict
    """
    DISPATCH[name] = func


def get_primitive(name: str) -> Optional[Callable]:
    """Get a primitive from the dispatch table."""
    return DISPATCH.get(name)


# ============================================================
# Core Primitives
# ============================================================

def primitive_log(params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Write a message to stdout.

    Params:
        message: Text to log

    Returns:
        {"status": "ok", "logged": message}
    """
    message = params.get("message")
    if not message or not isinstance(message, str):
        return {"status": "error", "error": "Invalid or missing 'message' parameter"}

    scp_id = context.get("scp_id", "unknown")
    timestamp = context.get("timestamp", datetime.utcnow().isoformat() + "Z")

    print(f"[{timestamp}] [{scp_id}] {message}")

    return {"status": "ok", "logged": message}


def primitive_emit_event(params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Append an event to the event bus.

    Params:
        event: Event name
        payload: Event payload (dict)
        source: Event source (optional)

    Returns:
        {"status": "ok", "event": event_name}
    """
    event = params.get("event")
    if not event or not isinstance(event, str):
        return {"status": "error", "error": "Invalid or missing 'event' parameter"}

    payload = params.get("payload", {})
    source = params.get("source", context.get("scp_id", "unknown"))

    entry = {
        "event": event,
        "source": source,
        "payload": payload,
        "ts": datetime.utcnow().isoformat() + "Z",
    }

    # Write to event bus
    ubvm_home = context.get("ubvm_home", os.getcwd())
    event_dir = os.path.join(ubvm_home, "logs", "events")
    os.makedirs(event_dir, exist_ok=True)

    queue_path = os.path.join(event_dir, "queue.jsonl")
    with open(queue_path, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return {"status": "ok", "event": event, "entry": entry}


def primitive_http_request(params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make an HTTP request.

    Params:
        url: Request URL
        method: HTTP method (GET, POST, etc.)
        headers: Request headers (dict)
        data: Request body (dict)
        timeout: Timeout in seconds

    Returns:
        {"status": "ok", "response": response_json, "status_code": code}
    """
    if requests is None:
        return {"status": "error", "error": "requests module not installed"}

    url = params.get("url")
    if not url:
        return {"status": "error", "error": "Missing 'url' parameter"}

    method = params.get("method", "GET").upper()
    headers = params.get("headers", {})
    data = params.get("data")
    timeout = params.get("timeout", 30)

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=timeout)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=timeout)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=timeout)
        else:
            return {"status": "error", "error": f"Unsupported method: {method}"}

        return {
            "status": "ok",
            "status_code": response.status_code,
            "response": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}


def primitive_read_file(params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Read a file.

    Params:
        path: File path (relative to UBVM_HOME)

    Returns:
        {"status": "ok", "content": content}
    """
    file_path = params.get("path")
    if not file_path:
        return {"status": "error", "error": "Missing 'path' parameter"}

    ubvm_home = context.get("ubvm_home", os.getcwd())
    full_path = os.path.join(ubvm_home, file_path)

    # Security: prevent path traversal
    real_path = os.path.realpath(full_path)
    real_home = os.path.realpath(ubvm_home)
    if not real_path.startswith(real_home):
        return {"status": "error", "error": "Path traversal not allowed"}

    try:
        with open(full_path, "r") as f:
            content = f.read()
        return {"status": "ok", "content": content}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def primitive_write_file(params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Write to a file.

    Params:
        path: File path (relative to UBVM_HOME)
        content: Content to write

    Returns:
        {"status": "ok", "written": bytes}
    """
    file_path = params.get("path")
    content = params.get("content", "")

    if not file_path:
        return {"status": "error", "error": "Missing 'path' parameter"}

    ubvm_home = context.get("ubvm_home", os.getcwd())
    full_path = os.path.join(ubvm_home, file_path)

    # Security: prevent path traversal
    real_path = os.path.realpath(full_path)
    real_home = os.path.realpath(ubvm_home)
    if not real_path.startswith(real_home):
        return {"status": "error", "error": "Path traversal not allowed"}

    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
        return {"status": "ok", "written": len(content)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def primitive_exec(params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a shell command.

    Params:
        command: Command string
        timeout: Timeout in seconds

    Returns:
        {"status": "ok", "stdout": output, "stderr": error}

    Note:
        Requires UBC_ALLOW_EXEC=1 environment variable
    """
    if os.environ.get("UBC_ALLOW_EXEC") != "1":
        return {"status": "error", "error": "UBC_ALLOW_EXEC not set to 1"}

    command = params.get("command")
    if not command:
        return {"status": "error", "error": "Missing 'command' parameter"}

    timeout = params.get("timeout", 30)

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "status": "ok" if result.returncode == 0 else "error",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": f"Command timed out after {timeout}s"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def primitive_validate_self(params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate the running capsule.

    Returns:
        {"status": "ok", "valid": True/False, "errors": []}
    """
    # This is a placeholder — actual validation is done by the interpreter
    # We just echo the context
    return {
        "status": "ok",
        "valid": True,
        "scp_id": context.get("scp_id", "unknown"),
        "timestamp": context.get("timestamp", datetime.utcnow().isoformat() + "Z"),
    }


# ============================================================
# Register All Primitives
# ============================================================

def _register_core_primitives():
    """Register all core primitives."""
    register_primitive("log", primitive_log)
    register_primitive("emit_event", primitive_emit_event)
    register_primitive("http_request", primitive_http_request)
    register_primitive("read_file", primitive_read_file)
    register_primitive("write_file", primitive_write_file)
    register_primitive("exec", primitive_exec)
    register_primitive("validate_self", primitive_validate_self)


# Register on import
_register_core_primitives()


# ============================================================
# CLI
# ============================================================

def main():
    """Test primitives."""
    print("🔧 UBVM — Core Primitives")
    print("=" * 60)

    print(f"\n📋 Registered primitives ({len(DISPATCH)}):")
    for name in sorted(DISPATCH.keys()):
        print(f"   - {name}")


if __name__ == "__main__":
    main()