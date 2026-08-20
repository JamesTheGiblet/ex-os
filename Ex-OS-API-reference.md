# Ex-OS — API Reference

---

## 1. Overview

Ex-OS exposes a unified API through the Network Daemon (port 8080) and specialized endpoints for individual components.

**Base URL:** `http://<exos-host>:8080`

**Authentication:** Token-based (`X-API-Token: <token>`)

**Format:** JSON request/response

---

## 2. Network Daemon API (Port 8080)

### 2.1 System Status

#### GET /api/status

Returns system status and metadata.

**Response:**

```json
{
    "status": "ok",
    "version": {
        "ubvm": "1.0",
        "scp": "0.1"
    },
    "components": {
        "capsules": 88,
        "extensions": 11,
        "primitives": 73
    },
    "memory": {
        "short_term": 0,
        "long_term": 83
    },
    "trust": {
        "average_λ": 0.91,
        "quarantined": 0
    },
    "ledger": {
        "anchored": true,
        "entries": 1247
    },
    "hardware": {
        "node_id": "exos-master",
        "device": "vps",
        "uptime": "14d 3h 22m"
    }
}
```

#### GET /api/health

Simple health check.

**Response:**

```json
{
    "status": "ok",
    "timestamp": "2026-08-19T04:47:00Z"
}
```

---

### 2.2 Chat (BuddAI)

#### POST /api/chat

Send a message to BuddAI.

**Request:**

```json
{
    "message": "thinking about a spinner robot",
    "session_id": "optional-uuid",
    "context": {
        "project": "gilbot",
        "focus": "mechanical"
    }
}
```

**Response:**

```json
{
    "response": "Ah nice! Full-body spinner? Reminds me of GilBot. New project or variant?",
    "session_id": "session-uuid",
    "memory": {
        "short_term": 3,
        "long_term": 83,
        "corrections_applied": 2
    },
    "provenance": {
        "capsule_id": "buddai/response-123",
        "λ": 0.92,
        "sealed": true
    }
}
```

---

### 2.3 Query (Mimir)

#### POST /api/query

Ask a codebase question.

**Request:**

```json
{
    "prompt": "how does authentication work",
    "repo": "/path/to/repo",
    "max_results": 5
}
```

**Response:**

```json
{
    "answer": "Authentication uses JWT tokens stored in Redis...",
    "sources": [
        {
            "file": "auth/middleware.py",
            "line": 42,
            "relevance": 0.95,
            "λ": 0.91
        },
        {
            "file": "config/settings.py",
            "line": 18,
            "relevance": 0.87,
            "λ": 0.88
        }
    ],
    "provenance": {
        "capsule_id": "mimir/query-456",
        "sealed": true,
        "timestamp": "2026-08-19T04:47:00Z"
    }
}
```

---

### 2.4 Trust (Leighton Weight)

#### GET /api/trust/entity/:id

Get trust score for an entity.

**Response:**

```json
{
    "entity_id": "capsule/ubvm-core",
    "domain": "system",
    "λ": 0.95,
    "status": "VALIDATED",
    "history": [
        {"event": "birth", "λ": 1.00, "timestamp": "2026-08-01T00:00:00Z"},
        {"event": "attestation", "λ": 0.98, "timestamp": "2026-08-05T12:00:00Z"},
        {"event": "seal", "λ": 0.95, "timestamp": "2026-08-19T04:47:00Z"}
    ],
    "decay": {
        "k": 0.01,
        "last_update": "2026-08-19T04:47:00Z"
    }
}
```

#### POST /api/trust/attest

Issue an attestation.

**Request:**

```json
{
    "entity_id": "capsule/ubvm-core",
    "outcome": "success",
    "message": "Validated against test suite",
    "attester": "did:key:z6MktudRY5LBZJeE13BiF4BeisAwWs7gvg6srh2GwLAMKDwJ"
}
```

**Response:**

```json
{
    "status": "ok",
    "attestation_id": "attest-789",
    "new_λ": 0.97,
    "recorded": true
}
```

#### GET /api/trust/status

Get overall trust statistics.

**Response:**

```json
{
    "total_entities": 156,
    "average_λ": 0.84,
    "distribution": {
        "reflex": 12,
        "validated": 89,
        "questionable": 43,
        "quarantined": 12
    },
    "tiers": {
        "tier_1": 45,
        "tier_2": 32,
        "tier_3": 18,
        "tier_4": 8,
        "tier_5": 3
    }
}
```

---

### 2.5 Audit (ChronoSCRIBE)

#### GET /api/ledger

Get the latest ledger entries.

**Query Parameters:**

- `limit` — Number of entries (default: 20, max: 100)
- `offset` — Pagination offset
- `consumer` — Filter by consumer

**Response:**

```json
{
    "entries": [
        {
            "entry_id": "sha256:abc123...",
            "event": "event.capsule.signed",
            "source": "exos/sign",
            "payload": {
                "scp_id": "ubvm/core-identity",
                "signature": "ed25519:xyz789..."
            },
            "ts": "2026-08-19T04:47:00Z",
            "previous": "sha256:def456..."
        }
    ],
    "total": 1247,
    "limit": 20,
    "offset": 0
}
```

#### GET /api/ledger/verify/:entry_id

Verify a specific ledger entry.

**Response:**

```json
{
    "entry_id": "sha256:abc123...",
    "valid": true,
    "chain_valid": true,
    "signature_valid": true,
    "anchor_valid": true
}
```

#### GET /api/ledger/anchor

Get the current root anchor.

**Response:**

```json
{
    "root_hash": "sha256:root123...",
    "anchored_at": "2026-08-01T00:00:00Z",
    "consumer_count": 3,
    "consumers": ["LifeForge", "giblets-forge", "CobbleWright"]
}
```

---

### 2.6 Enforcement (Keystone Gate)

#### POST /api/validate

Validate a response against a capsule.

**Request:**

```json
{
    "capsule_id": "mimir/binding-v1",
    "response": "Authentication uses JWT tokens...",
    "λ_threshold": 0.85
}
```

**Response:**

```json
{
    "valid": true,
    "reasoning": "Response follows Mimir Behavioural Binding v1. Persona matches.",
    "λ": 0.92,
    "confidence": 0.96,
    "audit_trail": "event.gate.validated",
    "sealed": true
}
```

#### POST /api/validate/adversarial

Run adversarial testing via Replicant swarm.

**Request:**

```json
{
    "capsule_id": "mimir/binding-v1",
    "claim": "The system authenticates via JWT",
    "iterations": 10
}
```

**Response:**

```json
{
    "valid": true,
    "adversarial_tests": 10,
    "passed": 9,
    "failed": 1,
    "failure_reason": "Edge case: expired token handling",
    "λ": 0.89,
    "sealed": true
}
```

---

### 2.7 Sealing (HAL)

#### POST /api/hal/seal

Authorise an action.

**Request:**

```json
{
    "action": "DEPLOY",
    "authoriser": "did:key:z6MktudRY5LBZJeE13BiF4BeisAwWs7gvg6srh2GwLAMKDwJ",
    "tier": 3,
    "description": "Deploy new capsule to production"
}
```

**Response:**

```json
{
    "status": "sealed",
    "seal_id": "seal-456",
    "tier": 3,
    "λ": 1.42,
    "separation": "none",
    "timestamp": "2026-08-19T04:47:00Z",
    "recorded": true,
    "ledger_entry": "sha256:seal123..."
}
```

#### GET /api/hal/seal/:id

Get seal details.

**Response:**

```json
{
    "seal_id": "seal-456",
    "action": "DEPLOY",
    "authoriser": "did:key:z6MktudRY5LBZJeE13BiF4BeisAwWs7gvg6srh2GwLAMKDwJ",
    "tier": 3,
    "λ": 1.42,
    "status": "active",
    "timestamp": "2026-08-19T04:47:00Z",
    "separation": "none",
    "ledger_entry": "sha256:seal123..."
}
```

---

### 2.8 Replicant

#### GET /api/replicant/status

Get Replicant swarm status.

**Response:**

```json
{
    "population": 7,
    "health": 0.79,
    "energy_total": 340,
    "tick": 1247,
    "claims": {
        "total": 456,
        "verified": 312,
        "contradicted": 89,
        "unknown": 55
    },
    "agents": [
        {
            "id": "agent-001",
            "λ": 0.85,
            "health": 0.92,
            "energy": 45,
            "children": 2
        }
    ]
}
```

#### POST /api/replicant/tick

Run one simulation tick.

**Response:**

```json
{
    "tick": 1248,
    "events": [
        {"type": "birth", "agent_id": "agent-008"},
        {"type": "death", "agent_id": "agent-003"},
        {"type": "claim", "agent_id": "agent-002", "claim": "Food at (45,67)"}
    ],
    "population": 8,
    "health": 0.78
}
```

---

### 2.9 Anchor

#### POST /api/anchor/query

Query the expert system.

**Request:**

```json
{
    "domain": "electronics",
    "query": "trace_width",
    "params": {
        "current": 3.0,
        "copper_weight": "1oz",
        "temperature_rise": 10
    }
}
```

**Response:**

```json
{
    "status": "ANSWERED",
    "answer": "Minimum trace width: 0.025 inches (0.64mm)",
    "sources": [
        {
            "id": "SRC-001",
            "name": "IPC Standards Library",
            "weight": 0.92,
            "independence_group": "IPC"
        }
    ],
    "evidence_chain": [
        {"capsule": "RULE-003", "weight": 0.91},
        {"capsule": "SRC-001", "weight": 0.92}
    ],
    "session_id": "anchor-session-789",
    "sealed": true
}
```

---

## 3. Component APIs

### 3.1 Mimir API (Port 5001)

#### POST /ingest

Ingest a repository.

**Request:**

```json
{
    "repo_path": "/path/to/repo",
    "force": false,
    "capsule_only": true
}
```

**Response:**

```json
{
    "status": "ok",
    "files_processed": 243,
    "capsules_created": 243,
    "duplicates_skipped": 12,
    "errors": 0
}
```

#### POST /generate

Generate code with context.

**Request:**

```json
{
    "prompt": "Write a function to parse JSON",
    "context": ["auth", "database"],
    "max_tokens": 500
}
```

**Response:**

```json
{
    "code": "def parse_json(data): ...",
    "sources": ["auth/middleware.py", "database/orm.py"],
    "λ": 0.88
}
```

---

### 3.2 BuddAI API (Port 8080 /api/chat)

*See Section 2.2*

---

### 3.3 Ollama API (Port 11434)

Standard Ollama API endpoints.

#### GET /api/tags

List available models.

#### POST /api/generate

Generate text.

**Request:**

```json
{
    "model": "gemma2:2b",
    "prompt": "Explain Ohm's law",
    "stream": false
}
```

## POST /api/chat

Chat with model.

**Request:**

```json
{
    "model": "gemma2:2b",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "What is Ex-OS?"}
    ]
}
```

---

## 4. Authentication

### 4.1 Token Header

```bash
curl -H "X-API-Token: <token>" http://localhost:8080/api/status
```

### 4.2 Default Token

```txt
"3D models Rock"
```

### 4.3 Setting Custom Token

```bash
# In network_daemon.py
API_TOKEN = "your-custom-token"
```

---

## 5. Error Responses

### 5.1 Standard Error

```json
{
    "status": "error",
    "code": 400,
    "message": "Missing required field: capsule_id",
    "timestamp": "2026-08-19T04:47:00Z"
}
```

### 5.2 Error Codes

| Code | Meaning |
| 400 | Bad request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not found |
| 429 | Rate limited |
| 500 | Internal error |
| 503 | Service unavailable |

---

## 6. WebSocket Endpoints

### 6.1 Event Stream

```txt
ws://<exos-host>:8080/ws/events
```

**Messages:**

```json
{
    "event": "sensor.button.press",
    "source": "esp32-001",
    "payload": {"pin": 0},
    "ts": "2026-08-19T04:47:00Z"
}
```

### 6.2 Ledger Stream

```txt
ws://<exos-host>:8080/ws/ledger
```

**Messages:**

```json
{
    "entry_id": "sha256:abc123...",
    "event": "event.hal.seal",
    "payload": {"seal_id": "seal-456"},
    "ts": "2026-08-19T04:47:00Z"
}
```

---

## 7. Rate Limiting

| Endpoint | Limit | Window |
#| `/api/chat` | 60/min | 1 minute |
| `/api/query` | 30/min | 1 minute |
| `/api/validate` | 100/min | 1 minute |
| `/api/hal/seal` | 10/min | 1 minute |
| `/api/replicant/tick` | 60/min | 1 minute |

---

## 8. CLI Equivalents

| API Endpoint | CLI Command |
| `POST /api/chat` | `python talk.py` |
| `POST /api/query` | `python cli/mimir-query.py "question"` |
| `GET /api/trust/entity/:id` | `python leighton_weight.py score --entity id` |
| `GET /api/ledger` | `python ledger.py status` |
| `POST /api/hal/seal` | `python hal.py seal --action DEPLOY` |

---

## 9. Example Usage

### 9.1 Chat with BuddAI

```bash
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Token: 3D models Rock" \
  -d '{"message": "what is Ex-OS?"}'
```

### 9.2 Query Mimir

```bash
curl -X POST http://localhost:8080/api/query \
  -H "Content-Type: application/json" \
  -H "X-API-Token: 3D models Rock" \
  -d '{"prompt": "how does authentication work", "repo": "/root/mimir"}'
```

### 9.3 Check Trust

```bash
curl -X GET http://localhost:8080/api/trust/entity/capsule/ubvm-core \
  -H "X-API-Token: 3D models Rock"
```

### 9.4 Seal Action

```bash
curl -X POST http://localhost:8080/api/hal/seal \
  -H "Content-Type: application/json" \
  -H "X-API-Token: 3D models Rock" \
  -d '{"action": "DEPLOY", "authoriser": "did:key:z6MktudRY5LBZJeE13BiF4BeisAwWs7gvg6srh2GwLAMKDwJ", "tier": 3}'
```

---

## 10. Complete API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | System status |
| `/api/health` | GET | Health check |
| `/api/chat` | POST | BuddAI chat |
| `/api/query` | POST | Mimir query |
| `/api/trust/entity/:id` | GET | Trust score |
| `/api/trust/attest` | POST | Issue attestation |
| `/api/trust/status` | GET | Trust statistics |
| `/api/ledger` | GET | Ledger entries |
| `/api/ledger/verify/:id` | GET | Verify entry |
| `/api/ledger/anchor` | GET | Root anchor |
| `/api/validate` | POST | Validate response |
| `/api/validate/adversarial` | POST | Adversarial test |
| `/api/hal/seal` | POST | Authorise action |
| `/api/hal/seal/:id` | GET | Seal details |
| `/api/replicant/status` | GET | Swarm status |
| `/api/replicant/tick` | POST | Run tick |
| `/api/anchor/query` | POST | Expert query |
| `/ws/events` | WS | Event stream |
| `/ws/ledger` | WS | Ledger stream |

---

*Ex-OS: Your thoughts, staying yours, everywhere, verified, audited, and trusted.*