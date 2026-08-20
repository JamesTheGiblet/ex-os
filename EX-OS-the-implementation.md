# Ex-OS — The Implementation

---

## 1. The Code

### 1.1 Repository Structure

```txt
Ex-OS/
├── README.md                    # The Origin Story
├── ARCHITECTURE.md              # The Extended Documentation
├── MANIFESTO.md                 # The Philosophy
├── IMPLEMENTATION.md            # This Document
│
├── core/
│   ├── scp/                     # Semantic Capsule Protocol
│   │   ├── schema/
│   │   ├── sign/
│   │   └── canonicalise/
│   │
│   ├── datacube/                # Five Lenses
│   │   ├── lenses/
│   │   ├── namespaces/
│   │   └── bulk/
│   │
│   ├── leighton/                # Leighton Weight Engine
│   │   ├── score/
│   │   ├── decay/
│   │   └── attest/
│   │
│   ├── chronoscribe/            # Immutable Ledger
│   │   ├── ledger/
│   │   ├── anchor/
│   │   └── stream/
│   │
│   └── hal/                     # Human Accountability Layer
│       ├── seal/
│       ├── tiers/
│       └── verify/
│
├── runtime/
│   ├── ubvm/                    # Universal Behavioural VM
│   │   ├── interpreter/
│   │   ├── primitives/
│   │   ├── extensions/
│   │   └── event_bus/
│   │
│   └── ubvm-os/                 # Bare-Metal Build
│       ├── kernel/
│       ├── boot/
│       └── net/
│
├── intelligence/
│   ├── mimir/                   # Codebase Intelligence
│   │   ├── ingest/
│   │   ├── query/
│   │   └── model/
│   │
│   └── buddai/                  # Personal Exocortex
│       ├── memory/
│       ├── validators/
│       └── personality/
│
├── enforcement/
│   └── keystone/                # The Gate
│       ├── bind/
│       ├── validate/
│       └── swarm/
│
├── applications/
│   ├── replicant/               # Bio-Inspired Swarm
│   │   ├── python/
│   │   ├── rust/
│   │   └── wasm/
│   │
│   ├── anchor/                  # Expert System
│   │   ├── genesis/
│   │   ├── rules/
│   │   └── knowledge/
│   │
│   └── axiom/                   # Enterprise Sovereign
│       ├── ingest/
│       ├── justify/
│       └── present/
│
├── hardware/
│   ├── esp32/                   # Edge Nodes
│   │   ├── firmware/
│   │   └── protocol/
│   │
│   └── uefi/                    # Boot USB
│       ├── bootx64/
│       └── capsule/
│
├── integration/
│   ├── api/                     # Unified API
│   ├── dashboard/               # Web Interface
│   └── cli/                     # Command Line
│
└── docs/
    ├── README.md
    ├── ARCHITECTURE.md
    ├── MANIFESTO.md
    ├── IMPLEMENTATION.md
    ├── DEPLOYMENT.md
    └── CONTRIBUTING.md
```

---

## 2. The Code Patterns

### 2.1 The Capsule Pattern

Every component in Ex-OS is defined as an SCP capsule.

```json
{
  "scp_version": "0.1",
  "scp_id": "exos/component-name",
  "object_class": "Safe | Euclid | Keter | Thaumiel",
  "intent": "What this component does.",
  "containment": {
    "read_only": false,
    "audit_log": true,
    "kill_switch": false
  },
  "behaviours": [
    {
      "trigger": "on_load | cron | on_event",
      "schedule": "*/5 * * * *",
      "event": "event.name",
      "actions": [
        { "primitive": "primitive_name", "params": {} }
      ]
    }
  ]
}
```

### 2.2 The Primitive Pattern

Every action in Ex-OS is a primitive.

```python
def primitive_name(params: dict, context: dict) -> dict:
    """
    Atomic behaviour in the system.
    
    params: Arguments from the capsule action
    context: Runtime context (scp_id, ubvm_home, timestamp, env)
    
    Returns: {"status": "ok", ...}
    """
    # Do the work
    return {"status": "ok", "result": result}
```

### 2.3 The Event Pattern

Every event in Ex-OS is a JSON object in the queue.

```json
{
  "event": "exos.component.event",
  "source": "exos/component-name",
  "payload": {
    "key": "value"
  },
  "ts": "2026-08-19T04:47:00Z"
}
```

### 2.4 The Ledger Pattern

Every event is recorded in ChronoSCRIBE.

```json
{
  "entry_id": "sha256(previous + payload + timestamp)",
  "event": "exos.component.event",
  "source": "exos/component-name",
  "payload": {},
  "ts": "2026-08-19T04:47:00Z",
  "previous": "sha256(previous_entry)",
  "signature": {
    "key_id": "did:key:z6MktudRY5LBZJeE13BiF4BeisAwWs7gvg6srh2GwLAMKDwJ",
    "algorithm": "Ed25519",
    "value": "base64_signature"
  }
}
```

### 2.5 The Trust Pattern

Every entity has a Leighton Weight.

```python
def compute_trust(entity_id: str, domain: str) -> float:
    """
    Compute λ for an entity.
    
    λ(t) = 1.00 + (λ₀ − 1.00) × e^(−kt)
    """
    # Load observation stream
    observations = get_observations(entity_id, domain)
    
    # Compute current λ
    λ = 1.00
    for obs in observations:
        λ = decay(λ, obs.time)
        λ = update(λ, obs.outcome)
    
    return λ
```

### 2.6 The Seal Pattern

Every action is sealed by HAL.

```python
def seal(action: str, authoriser: str, tier: int) -> dict:
    """
    Authorise an action.
    
    Requires verified authoriser-score-file.
    Refuses if λ insufficient for tier.
    """
    # Load verified score file
    score = load_score_file(authoriser)
    
    # Check λ threshold
    if score['λ'] < TIER_THRESHOLDS[tier]:
        return {"status": "refused", "reason": "Insufficient trust"}
    
    # Create seal
    seal = {
        "action": action,
        "authoriser": authoriser,
        "tier": tier,
        "λ": score['λ'],
        "ts": datetime.now().isoformat(),
        "separation": "none"  # or "verified"
    }
    
    # Record in ChronoSCRIBE
    chronoscribe.append("event.hal.seal", seal)
    
    return {"status": "sealed", "seal": seal}
```

---

## 3. The Integration Points

### 3.1 SCP → DataCube

When a capsule enters Ex-OS, DataCube classifies it.

```txt
SCP Capsule
    ↓
DataCube: Classify
    ↓
Lens Assigned (FACT/OPINION/FICTION/CONTEXT/UNKNOWN)
    ↓
Namespace Assigned (event.*/state.*/domain.*/behaviour.*)
    ↓
Cube Created (16% per lens + 20% human validation)
```

### 3.2 DataCube → Leighton Weight

When a cube is classified, Leighton Weight scores it.

```txt
Cube Created
    ↓
Leighton Weight: Compute λ
    ↓
λ = 1.00 (neutral)
    ↓
Observation Stream Begins
    ↓
λ Updates on Every Event
```

### 3.3 Leighton Weight → ChronoSCRIBE

Every trust event is recorded.

```txt
λ Update
    ↓
ChronoSCRIBE: Append Event
    ↓
event.attestation.issued
    ↓
Hash-Linked to Previous Entry
    ↓
Immutable Record
```

### 3.4 ChronoSCRIBE → HAL

When a seal is requested, HAL checks the ledger.

```txt
Seal Request
    ↓
HAL: Load Score File
    ↓
HAL: Check λ Against Tier
    ↓
HAL: Append Event (seal) or Refusal
    ↓
ChronoSCRIBE: Record Seal
```

### 3.5 HAL → Consumers

When a seal is issued, consumers execute the action.

```txt
Seal Issued
    ↓
Consumer: Execute Action
    ↓
UBVM: Dispatch Capsule
    ↓
Mimir: Answer Query
    ↓
BuddAI: Generate Response
    ↓
Replicant: Simulate Tick
    ↓
Anchor: Conclude Fact
    ↓
Axiom: Package Provenance
```

---

## 4. The Deployment Patterns

### 4.1 Local Development (S24 Ultra / Termux)

```bash
# Clone everything
git clone https://github.com/JamesTheGiblet/UBVM-os
git clone https://github.com/JamesTheGiblet/mimir
git clone https://github.com/JamesTheGiblet/BuddAI
git clone https://github.com/JamesTheGiblet/Ex-OS

# Install dependencies
pkg install python
pip install -r requirements.txt

# Start daemons
python ubvm schedule
python network_daemon.py 8080
python buddai_server.py --server

# Open dashboard
# http://localhost:8080
```

### 4.2 VPS Production (Hetzner CX22)

```bash
# Deploy
curl -sSL https://raw.githubusercontent.com/JamesTheGiblet/Ex-OS/main/install.sh | bash

# Or manual
git clone https://github.com/JamesTheGiblet/Ex-OS
cd Ex-OS
pip install -r requirements.txt
python leighton_weight.py init --k-per-day 0.01
python ledger.py anchor-root
systemctl enable --now exos-network exos-scheduler

# Access
# http://178.105.96.89
```

### 4.3 Bare-Metal (Ryzen 3300U)

```bash
# Build UEFI bootloader
cd UBVM-OS
make bootx64.efi

# Copy to USB
cp bootx64.efi /media/usb/EFI/BOOT/

# Boot from USB
# Select UEFI: USB Drive from BIOS boot menu
```

### 4.4 Edge Node (ESP32-C3)

```bash
# Flash
esptool.py --port COM7 --baud 460800 write_flash -z 0x0 firmware.bin

# Upload edge firmware
python ubvm_edge.py --ip 192.168.1.130 --port 8080
```

---

## 5. The Testing Patterns

### 5.1 Unit Tests

```bash
# UBVM
python ubvm test

# BuddAI
python -m pytest tests/

# Replicant (Python)
python -m pytest python/tests/

# Replicant (Rust)
cd rust && cargo test

# Anchor
python cli.py qa
```

### 5.2 Integration Tests

```bash
# Test SCP → DataCube → Leighton Weight → ChronoSCRIBE → HAL
python integration_test.py

# Test Full Pipeline
python test_pipeline.py

# Test All Consumers
python test_consumers.py
```

### 5.3 Fresh Clone Verification

> *"Verifies on a fresh clone is the real test."*

```bash
# Clone fresh
git clone https://github.com/JamesTheGiblet/Ex-OS
cd Ex-OS

# Install fresh
pip install -r requirements.txt

# Run tests
python ubvm test
python -m pytest tests/
python cli.py qa
```

---

## 6. The Error Patterns

### 6.1 Hard Fail

If something is wrong, fail loudly.

```python
def check_capsule(capsule):
    if not capsule.get('scp_id'):
        raise ValueError("Capsule missing scp_id")
    
    if not capsule.get('behaviours'):
        raise ValueError("Capsule missing behaviours")
    
    # Never silently pass
    return True
```

### 6.2 Audit Log

Every error is recorded in ChronoSCRIBE.

```json
{
  "event": "system.error",
  "source": "exos/component-name",
  "payload": {
    "error": "Capsule missing scp_id",
    "capsule": "ubvm/example"
  },
  "ts": "2026-08-19T04:47:00Z"
}
```

### 6.3 Quarantine

Errors can lead to quarantine.

```python
def handle_error(entity_id: str):
    # Record error in ChronoSCRIBE
    chronoscribe.append("system.error", {"entity": entity_id})
    
    # Decrease λ
    leighton_weight.decrease(entity_id, 0.1)
    
    # Check if quarantine threshold reached
    if leighton_weight.get(entity_id) < 0.60:
        quarantine(entity_id)
```

---

## 7. The Security Patterns

### 7.1 Authentication

Every identity has a `did:key` signature.

```python
def verify_signature(capsule: dict) -> bool:
    """
    Verify Ed25519 signature on a capsule.
    
    deterministic: re-running sign.py over unchanged content produces
    byte-identical signatures.
    """
    signature = capsule.get('signature')
    if not signature:
        return False
    
    key_id = signature.get('key_id')
    algorithm = signature.get('algorithm')
    value = signature.get('value')
    
    if algorithm != 'Ed25519':
        return False
    
    # Verify signature
    return ed25519_verify(key_id, canonicalise(capsule), value)
```

### 7.2 Authorisation

Every action is gated by HAL.

```python
def authorise_action(action: str, authoriser: str, tier: int) -> bool:
    """
    HAL checks λ against tier threshold.
    """
    # Load verified score file
    score = load_score_file(authoriser)
    λ = score['λ']
    
    # Check threshold
    if λ < TIER_THRESHOLDS[tier]:
        return False
    
    return True
```

### 7.3 Audit Trail

Every action is recorded in ChronoSCRIBE.

```python
def record_action(action: str, authoriser: str, result: dict):
    """
    ChronoSCRIBE records every action.
    """
    chronoscribe.append("event.hal.action", {
        "action": action,
        "authoriser": authoriser,
        "result": result,
        "separation": "none"  # or "verified"
    })
```

---

## 8. The Performance Patterns

### 8.1 Sub-50kb Core

The SCP core is sub-50kb, fitting in L2 cache.

```c
// ubvm_edge.h — 96-byte sovereign UDP protocol
typedef struct {
    uint8_t version;        // 1 byte
    uint8_t message_type;   // 1 byte
    uint16_t payload_len;   // 2 bytes
    uint32_t sequence;      // 4 bytes
    uint8_t payload[84];    // 84 bytes
    uint32_t checksum;      // 4 bytes
} __attribute__((packed)) ubvm_packet_t;
// Total: 96 bytes
```

### 8.2 SQLite for Memory

BuddAI's memory is stored in SQLite for performance.

```sql
CREATE TABLE short_term (
    id INTEGER PRIMARY KEY,
    content TEXT,
    weight REAL,
    created TIMESTAMP,
    tags TEXT
);

CREATE TABLE long_term (
    id INTEGER PRIMARY KEY,
    content TEXT,
    weight REAL,
    created TIMESTAMP,
    promoted_from INTEGER,
    tags TEXT
);
```

### 8.3 Event Bus for Communication

UBVM's event bus is append-only JSONL.

```python
def emit_event(event: str, source: str, payload: dict):
    """
    Append an event to the event bus.
    """
    entry = {
        "event": event,
        "source": source,
        "payload": payload,
        "ts": datetime.now().isoformat()
    }
    
    with open("logs/events/queue.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")
```

---

## 9. The Evolution Patterns

### 9.1 Correction → Capsule

Errors become capsules.

```python
def handle_correction(correction: str):
    """
    Capture a correction as a new capsule.
    """
    capsule = {
        "scp_version": "0.1",
        "scp_id": f"exos/correction/{uuid4()}",
        "object_class": "Safe",
        "intent": correction,
        "containment": {"read_only": false, "audit_log": true},
        "behaviours": []
    }
    
    # Sign the capsule
    sign(capsule)
    
    # Append to ChronoSCRIBE
    chronoscribe.append("event.correction.issued", capsule)
```

### 9.2 Learning → Plasticity

Successful routes become reflexes.

```python
def record_route(route: str, outcome: str):
    """
    Plasticity records route outcomes.
    """
    if outcome == "success":
        weight = leighton_weight.get(route) + 0.3
    elif outcome == "failure":
        weight = leighton_weight.get(route) - 0.3
    else:
        weight = leighton_weight.get(route) + 0.1
    
    weight = clamp(weight, 0.1, 2.0)
    
    if weight > 1.8:
        promote_to_reflex(route)
```

### 9.3 Trust → Quarantine

Untrusted entities are quarantined.

```python
def quarantine(entity_id: str):
    """
    Quarantine an entity.
    """
    # Emit quarantine event
    emit_event("entity.quarantined", "exos/hal", {
        "entity": entity_id,
        "reason": "λ below 0.60",
        "timestamp": datetime.now().isoformat()
    })
    
    # Record in ChronoSCRIBE
    chronoscribe.append("event.entity.quarantined", {
        "entity": entity_id,
        "λ": leighton_weight.get(entity_id)
    })
```

---

## 10. The Ex-OS Commandments

### 10.1 The Ten Rules

1. **Declare everything.** Nothing exists without a capsule.
2. **Classify everything.** Every claim has a lens.
3. **Trust-score everything.** Every entity has a λ.
4. **Audit everything.** Every action is recorded in ChronoSCRIBE.
5. **Seal everything.** Every action is authorised by HAL.
6. **Fail loudly.** No silent pass-through.
7. **Correct with capsules.** Don't retrain, declare.
8. **Learn from outcomes.** Plasticity adapts.
9. **Heal automatically.** Quarantine and route around damage.
10. **Trust the pattern.** The system emerges.

### 10.2 The Ex-OS Prayer

> *"I built each one because I had to.*
> *The ideas came and I couldn't stop.*
> *To do anything less would be like a singer not singing, a dancer not dancing.*
> *I don't fight the system. I follow the flow.*
> *Everything I build leads to the next idea.*
> *And I come full circle to the original idea—but with so much more."*

---

## 11. The Ex-OS Verdict

### 11.1 What Works

- **Declare → Classify → Trust-score → Audit → Act** is the spine
- **SCP** is the context engine
- **UBVM** is the runtime
- **ChronoSCRIBE** is the audit trail
- **HAL** is the seal
- **The architecture is substrate-agnostic**

### 11.2 What's Missing

- **The Integration Layer** — still being defined
- **The Unified Dashboard** — single pane of glass
- **One-Command Install** — deploy anywhere
- **Enterprise Pilots** — prove at scale

### 11.3 What's Coming

- **The pattern will continue to emerge**
- **The system will continue to grow**
- **The ideas will continue to come**

### 11.4 The Final Word

> *"I have always felt, deep down, I know what to build but I can't see it.*
> *Now I can see it.*
> *Ex-OS is the thing I've been circling."*

---

*Ex-OS: Your thoughts, staying yours, everywhere, verified, audited, and trusted.*

---

*Built by JamesTheGiblet.*
*On a phone. In Termux. Around a full-time job.*
*Because the ideas didn't stop.*
