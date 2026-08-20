# EX-OS — Extended Documentation

This document provides deeper technical detail, component specifications, integration notes, and deployment guidance for the Ex-OS ecosystem.

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Component Specifications](#2-component-specifications)
3. [The Five-Stage Spine](#3-the-five-stage-spine)
4. [Integration Layer](#4-integration-layer)
5. [Deployment Guide](#5-deployment-guide)
6. [The Relationship Map](#6-the-relationship-map)
7. [API Reference](#7-api-reference)
8. [Security Model](#8-security-model)
9. [Development Workflow](#9-development-workflow)
10. [Future Roadmap](#10-future-roadmap)

---

## 1. System Architecture

### Overview

Ex-OS is a distributed, sovereign, self-learning semantic operating system built from independently evolved components that share a common foundation.

### High-Level Architecture

```bash
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EX-OS ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    THE FIVE-STAGE SPINE                              │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │   │
│  │  │ DECLARE  │→│CLASSIFY  │→│ TRUST-   │→│  AUDIT   │→│   ACT    │ │   │
│  │  │  (SCP)   │ │(DataCube)│ │  SCORE   │ │(Chrono)  │ │  (HAL)   │ │   │
│  │  └──────────┘ └──────────┘ │(Leighton)│ └──────────┘ └──────────┘ │   │
│  │                              └──────────┘                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                       │
│  ┌─────────────────────────────────▼─────────────────────────────────┐   │
│  │                         CONSUMERS                                  │   │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐│   │
│  │  │ UBVM   │ │ Mimir  │ │ BuddAI │ │Keystone│ │Replicant│ │ Anchor ││   │
│  │  │(Runtime)│ │(LLM)   │ │(Exo)   │ │(Gate)  │ │(Swarm) │ │(Expert)││   │
│  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘│   │
│  │  ┌────────┐ ┌────────┐                                            │   │
│  │  │ Axiom  │ │UBVM-OS │                                            │   │
│  │  │(Product)│ │(Bare)  │                                            │   │
│  │  └────────┘ └────────┘                                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                       │
│  ┌─────────────────────────────────▼─────────────────────────────────┐   │
│  │                         HARDWARE LAYER                             │   │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐         │   │
│  │  │ UEFI   │ │ ESP32  │ │ Ryzen  │ │ VPS    │ │ S24    │         │   │
│  │  │ USB    │ │ C3/C6  │ │ 3300U  │ │(Hetzner)│ │ Ultra  │         │   │
│  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Specifications

### 2.1 SCP — Semantic Capsule Protocol

| Attribute | Specification |
| **Version** | v1.2 (v2 planned) |
| **Format** | `.sc.json` (canonicalised JSON) |
| **Signature** | Ed25519, deterministic |
| **Key ID** | `did:key:z6MktudRY5LBZJeE13BiF4BeisAwWs7gvg6srh2GwLAMKDwJ` |
| **Schema Fields** | `scp_id`, `scp_version`, `created`, `inherits`, `declaration`, `licence`, `signature` |
| **Canonicalisation** | `forge-c14n-1` (interim), RFC 8785/JCS (target v2) |
| **Non-JSON Artefacts** | Hash-pin + `.sig` sidecar |
| **SCP Lite** | Minimal subset omitting `inherits`/`licence` |

### 2.2 DataCube — Five Lenses

| Attribute | Specification |
| **Lenses** | FACT, OPINION, FICTION, CONTEXT, UNKNOWN |
| **Relational Field** | `contradicts` (between cubes) |
| **Namespaces** | `event.*`, `state.*`, `domain.*`, `behaviour.*` |
| **Completeness** | 16% per lens + 20% human validation |
| **Trust Gating** | Completeness gates Leighton Weight attestation |
| **Bulk Ingestion** | `datacube::bulk` (`bulk_ingest_json`, `bulk_ingest_csv`) |

### 2.3 Leighton Weight Engine

| Attribute | Specification |
| **λ Range** | 0.00 – 2.00 |
| **Default λ₀** | 1.00 (neutral) |
| **Decay Function** | λ(t) = 1.00 + (λ₀ − 1.00) × e^(−kt) |
| **Update Rule** | λ-weighted increment, asymmetric step size |
| **Parameters** | ρ = 2.0, σ = 3.0, β₊ = 0.10 |
| **Policy** | Forward-only parameters, no retroactive changes |
| **Evidence Mass** | `n` travels with λ, gates HAL tiers |

### 2.4 ChronoSCRIBE

| Attribute | Specification |
| **Structure** | Per-consumer ledgers + root chain |
| **Anchoring** | `event.ledger.anchor.root` |
| **Pinning** | `scp_id` + `sha256` (not file paths) |
| **Entry** | `entry_id = hash(previous_entry_id + event_payload + timestamp)` |
| **Rule** | Published rows immutable; unpublished rows discardable |
| **Enforcement** | Hard-fail on unresolved placeholders |

### 2.5 HAL — Human Accountability Layer

| Attribute | Specification |
| **Tiers** | 1–5 mapped to λ thresholds |
| **Quarantine** | λ < 0.60 |
| **Sealing** | `hal.py seal` requires verified `--authoriser-score-file` |
| **Separation** | `none` (single operator) or `verified` (distinct identities) |
| **Consumer-Defined** | Tiers mapped to consequences by consumer |

### 2.6 UBVM — Universal Behavioural Virtual Machine

| Attribute | Specification |
| **Version** | 1.0 |
| **Primitives** | 73 |
| **Extensions** | 11 |
| **Capsules** | 88 (production) + 252 compliance fixtures |
| **Tests** | 250 passing |
| **Triggers** | `on_load`, `cron`, `on_event` |
| **Event Bus** | `logs/events/queue.jsonl` (append-only) |
| **Containment Classes** | Safe, Euclid, Keter, Thaumiel |

### 2.7 Mimir

| Attribute | Specification |
| **Model** | Phi-3-mini, Q4_K_M quantisation |
| **Binding Capsule** | Mimir Behavioural Binding v1 |
| **Constraints** | `condition.min_capsule_trust_to_cite: 0.6` |
| **Persona** | Terse, direct, Forge-style |
| **Infrastructure** | Ollama or llama.cpp |

### 2.8 BuddAI

| Attribute | Specification |
| **Version** | v5.0 |
| **Tests** | 379 passing |
| **Accuracy** | 90% (ESP32, 14-hour validation) |
| **Validators** | 8 hardware-specific, 29 checks total |
| **Memory** | SQLite, short/long-term with Forge Theory decay |
| **Model** | Qwen 2.5 Coder (3B) via Ollama |

### 2.9 Keystone Gate

| Attribute | Specification |
| **Confidence Threshold** | λ > 0.85 |
| **Integration** | Replicant swarm for adversarial testing |
| **Enforcement** | Blocks non-compliant responses |
| **Scope** | Local LLM only (sovereign path first) |
| **Open Questions** | 4 unresolved decisions |

### 2.10 Replicant

| Attribute | Specification |
| **Version** | v1.0 |
| **Language** | Python + Rust (parallel implementations) |
| **Population** | Self-regulates ~7 agents from 10 |
| **Health** | ~0.79 across seasons and seeds |
| **Energy** | Only currency, no free lunch |
| **Attestation** | Costs energy (load-bearing design decision) |
| **Ticks** | 7 phases: SENSE, DECIDE, RESOLVE, CLASSIFY, SCORE, WITNESS, DECAY |

### 2.11 Anchor

| Attribute | Specification |
| **Version** | v1.0 |
| **Accuracy** | 100% on 100 test questions |
| **Hallucinations** | Zero |
| **Validation** | 2,000 mathematical proofs |
| **Architecture** | 7 core systems: GENESIS, AUDITOR IDENTITY, SOURCE REGISTRY, INGESTION PIPELINE, RULE FIRING ENGINE, WEIGHT ENGINE, CHRONOSCRIBE |
| **Statuses** | BEDROCK, ACTIVE, PROVISIONAL, DECAYING, QUARANTINED |

### 2.12 Axiom

| Attribute | Specification |
| **Components** | Ingest, Justify, Present |
| **Lenses** | 6 epistemic dimensions |
| **The Hook** | "I've been selling highly trained, domain-specific LLM models. The accountability and auditability was a success. Axiom is how I did it." |
| **Target** | Regulated industries (healthcare, legal, finance) |

### 2.13 UBVM-OS

| Attribute | Specification |
| **Language** | Bare-metal C |
| **Hardware** | Ryzen 3300U, ESP32-C6, S24 Ultra |
| **Boot** | UEFI (`BOOTX64.EFI`) |
| **Edge Protocol** | 96-byte UDP, Fletcher-32 checksums |
| **Status** | Networking stalled; pivoted to Linux substrate |
| **Proved** | Architecture is substrate-agnostic |

---

## 3. The Five-Stage Spine

### 3.1 Declare (SCP)

**Purpose:** Define meaning and intent.

**Artefact:** `sc` (`.sc.json` file)

**Key Functions:**

- Declare `scp_id`, `scp_version`, `created`, `inherits`, `declaration`, `licence`, `signature`
- Sign with Ed25519
- Canonicalise JSON
- Pin `scp_id` + `sha256`

### 3.2 Classify (DataCube)

**Purpose:** Assign epistemic status to claims.

**Artefact:** Cube

**Key Functions:**

- Project claim onto five lenses (FACT, OPINION, FICTION, CONTEXT, UNKNOWN)
- Assign namespace (`event.*`, `state.*`, `domain.*`, `behaviour.*`)
- Self-fill faces (16% per lens + 20% human validation)
- Bulk ingest JSON/CSV

### 3.3 Trust-Score (Leighton Weight Engine)

**Purpose:** Compute trustworthiness of entities.

**Artefact:** λ (computed on-the-fly)

**Key Functions:**

- Compute λ from observation stream
- Apply neutral-attractor decay: λ(t) = 1.00 + (λ₀ − 1.00) × e^(−kt)
- Process attestations: `event.attestation.issued`
- Update λ per event: decay-then-update

### 3.4 Audit (ChronoSCRIBE)

**Purpose:** Immutable record of everything.

**Artefact:** Ledger

**Key Functions:**

- Append events to per-consumer ledgers
- Anchor to root chain: `event.ledger.anchor.root`
- Pin `scp_id` + `sha256`
- Hard-fail on unresolved placeholders

### 3.5 Act (HAL)

**Purpose:** Authorise actions based on trust.

**Artefact:** Seal

**Key Functions:**

- Require verified `--authoriser-score-file`
- Check λ against tier thresholds (1–5)
- Refuse seal if λ insufficient
- Record `separation` field (`none` or `verified`)

---

## 4. Integration Layer

### 4.1 How Components Connect

```txt

┌─────────────────────────────────────────────────────────────────────────────┐
│                            EX-OS INTEGRATION MAP                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SCP ──────────────────────────────────────────────────────────────────────┐│
│    │                                                                       ││
│    ├──→ DataCube (Classifies claims into lenses)                           ││
│    ├──→ Leighton Weight (Trust-scored by λ)                                ││
│    ├──→ ChronoSCRIBE (Audited via ledger)                                  ││
│    ├──→ HAL (Sealed via tiered action)                                     ││
│    ├──→ UBVM (Executed via runtime)                                        ││
│    ├──→ Mimir (Bound to LLM via binding capsule)                           ││
│    ├──→ Keystone Gate (Enforced via compliance check)                      ││
│    ├──→ Replicant (Born as signed genome capsule)                          ││
│    ├──→ Anchor (Stored as knowledge capsule)                               ││
│    ├──→ Axiom (Packaged with provenance)                                   ││
│    └──→ UBVM-OS (Executed as bare-metal capsule)                           ││
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Data Flow

```txt

RAW INPUT
    ↓
SCP: Declare (create .sc.json)
    ↓
DataCube: Classify (assign lens, namespace)
    ↓
Leighton Weight: Trust-score (compute λ)
    ↓
ChronoSCRIBE: Audit (append to ledger)
    ↓
HAL: Act (seal if λ sufficient)
    ↓
Consumers: Execute (UBVM, Mimir, BuddAI, etc.)
```

### 4.3 The Leighton Loop

```txt

SCORE → OBSERVE OUTCOMES → UPDATE
  ↑           ↓
  └─── ChronoSCRIBE ───┘
       (Attestations)
```

---

## 5. Deployment Guide

### 5.1 VPS Deployment (Hetzner CX22)

```bash
# Clone repositories
git clone https://github.com/JamesTheGiblet/UBVM-os
git clone https://github.com/JamesTheGiblet/mimir

# Install dependencies
cd UBVM-os
pip install -r requirements.txt

# Initialize Leighton Weight Engine
python leighton_weight.py init --k-per-day 0.01 --beta-plus 0.10 --rho 2.0

# Anchor ChronoSCRIBE root ledger
python ledger.py anchor-root

# Start daemons
systemctl enable --now ubvm-network ubvm-scheduler mimir-api forge-init
```

### 5.2 UEFI USB Boot

```bash
# Build UEFI bootloader
cd UBVM-OS
make bootx64.efi

# Copy to FAT32 USB
cp bootx64.efi /media/usb/EFI/BOOT/

# Boot from USB
# Select UEFI: USB Drive from BIOS boot menu
```

### 5.3 ESP32 Edge Node

```bash
# Flash ESP32-C3
esptool.py --port COM7 --baud 460800 write_flash -z 0x0 firmware.bin

# Upload edge firmware
python ubvm_edge.py --ip 192.168.1.130 --port 8080
```

### 5.4 Mobile Edge Node (S24 Ultra / Termux)

```bash
# Start Termux
pkg install python
git clone https://github.com/JamesTheGiblet/UBVM-os
cd UBVM-os
python edge_node.py --ip 192.168.1.130 --port 8080
```

---

## 6. The Relationship Map

### 6.1 Dependency Matrix

| Component | Depends On | Consumed By |
| **SCP** | None (foundation) | DataCube, Leighton Weight, ChronoSCRIBE, HAL, UBVM, Mimir, Keystone Gate, Replicant, Anchor, Axiom, UBVM-OS |
| **DataCube** | SCP | Replicant, Anchor, Keystone Gate |
| **Leighton Weight** | DataCube, ChronoSCRIBE | Replicant, Anchor, Keystone Gate, HAL |
| **ChronoSCRIBE** | SCP, Leighton Weight | Replicant, Anchor, HAL |
| **HAL** | Leighton Weight, ChronoSCRIBE | Replicant, Anchor |
| **UBVM** | SCP | Everything that runs capsules |
| **Keystone Gate** | SCP, DataCube, Leighton Weight, Replicant | Mimir, BuddAI |
| **Mimir** | SCP, Keystone Gate | Axiom |
| **BuddAI** | SQLite, Ollama | Personal exocortex |
| **Replicant** | SCP, DataCube, Leighton Weight, ChronoSCRIBE, HAL | None |
| **Anchor** | SCP, DataCube, Leighton Weight, ChronoSCRIBE, HAL | None |
| **Axiom** | Mimir, SCP, Leighton Weight, ChronoSCRIBE | None |
| **UBVM-OS** | SCP, UBVM | None |

### 6.2 Consumer Types

| Type | Components |
| **Infrastructure** | SCP, DataCube, Leighton Weight, ChronoSCRIBE, HAL |
| **Runtime** | UBVM, UBVM-OS |
| **Intelligence** | Mimir, BuddAI |
| **Enforcement** | Keystone Gate |
| **Applications** | Replicant, Anchor, Axiom |

---

## 7. API Reference

### 7.1 Network Daemon API

| Endpoint | Method | Description |
| `/api/status` | GET | System status |
| `/api/chat` | POST | BuddAI conversation |
| `/api/query` | POST | Mimir codebase query |
| `/api/trust` | GET | Leighton Weight λ statistics |
| `/api/ledger` | GET | ChronoSCRIBE audit stream |
| `/api/validate` | POST | Keystone Gate enforcement |

### 7.2 CLI Commands

| Command | Description |
| `ubvm boot` | Run all `on_load` capsules |
| `ubvm schedule` | Start cron + event daemon |
| `ubvm run <capsule>` | Execute a capsule immediately |
| `ubvm test` | Run compliance test suite |
| `leighton_weight.py score` | Compute λ for an entity |
| `ledger.py append-pins` | Witness capsules |
| `sign.py` | Sign a capsule |
| `hal.py seal` | Seal an action |
| `mimir-ingest` | Ingest a repo into capsules |
| `mimir-query` | Ask a codebase question |

---

## 8. Security Model

### 8.1 Trust Chain

```txt

SCP (Declare) → DataCube (Classify) → Leighton Weight (Trust-score) → ChronoSCRIBE (Audit) → HAL (Act)
```

**Trust flows in one direction.** Nothing flows backwards.

### 8.2 Containment Classes

| Class | Meaning |
| **Safe** | Low risk, runs freely |
| **Euclid** | Moderate complexity, monitored |
| **Keter** | High risk, requires kill switch |
| **Thaumiel** | System-level, governs other capsules |

### 8.3 Quarantine Thresholds

| Threshold | Meaning |
| λ < 0.60 | Quarantine — no seal can be issued |
| λ < 0.15 | Expulsion — permanently excluded |
| λ > 0.85 | Confidence threshold for Keystone Gate |

### 8.4 Single-Operator Disclosure

> *"Right now, one `did:key` signs everything in the stack. That means HAL's tier check can't yet prove independence between the person authorising an action and the person whose λ is being checked."*

**Mitigation:** Every seal carries a `separation` field stating `none` or `verified`.

---

## 9. Development Workflow

### 9.1 Primary Development Environment

| Device | Role |
| **Samsung S24 Ultra** | Primary build device (Termux) |
| **Hetzner CX22 VPS** | Production deployment |
| **Ryzen 3300U** | Bare-metal testing |
| **ESP32-C3/C6** | Edge node testing |

### 9.2 Session Scripts

```bash
./termux-start.sh   # pull, set env vars, start daemons
./termux-finish.sh  # stop daemons, commit, push
```

### 9.3 Test Suites

| Component | Tests |
| **UBVM** | 250 passing |
| **BuddAI** | 379 passing |
| **Replicant** | 35 passing (Python), 26 passing (Rust) |
| **Anchor** | 2,000 mathematical proofs |

---

## 10. Future Roadmap

### 10.1 Ex-OS Integration (Current)

| Task | Status |
| Document Ex-OS | ⚙️ In Progress |
| Write Relationship Map | ⚙️ In Progress |
| Build Integration Layer | 📅 Planned |
| Unified Dashboard | 📅 Planned |
| One-Command Install | 📅 Planned |

### 10.2 Component Roadmap

| Component | Next Milestone |
| **SCP** | v2: RFC 8785/JCS canonicalisation |
| **UBVM** | PostgreSQL backend for DataCube |
| **Mimir** | Full VPS deployment (off Colab) |
| **BuddAI** | Load all patterns on startup |
| **Keystone Gate** | Resolve four open decisions |
| **Replicant** | WASM build, Agent 74 integration |
| **Anchor** | v2: LLM-assisted extraction |
| **Axiom** | Enterprise pilots |

### 10.3 Vision

> *"A world where every AI answer comes with provenance. Where trust is measured, not assumed. Where accountability is built in, not bolted on."*

---

## Appendix A: Glossary

| Term | Definition |
| **SCP** | Semantic Capsule Protocol — context engine |
| **sc** | The artefact (`.sc.json`) |
| **λ (Leighton Weight)** | Trust score (0.00–2.00) |
| **Cube** | DataCube artefact |
| **Ledger** | ChronoSCRIBE artefact |
| **Seal** | HAL artefact |
| **Capsule** | Prose-only term for an `sc` |
| **Primitive** | Atomic Python function in UBVM |
| **Consumer** | A system built on the Forge Stack |

---

## Appendix B: Version Compatibility

| Component | Version | `scp_version` |
| **SCP** | v1.2 | 0.1 |
| **UBVM** | v1.0 | 0.1 |
| **Mimir** | v1.0 | 0.1 |
| **BuddAI** | v5.0 | N/A |
| **Keystone Gate** | v1.0 | 0.1 |
| **Replicant** | v1.0 | 0.1 |
| **Anchor** | v1.0 | 0.1 |
| **Axiom** | v1.0 | 0.1 |

---

## Appendix C: Key Files and Locations

| File | Location | Purpose |
| `interpreter.py` | `UBVM_HOME/` | Core runtime |
| `scheduler_daemon.py` | `UBVM_HOME/` | Cron + event daemon |
| `queue.jsonl` | `UBVM_HOME/logs/events/` | Event bus |
| `ledger.py` | `UBVM_HOME/` | ChronoSCRIBE |
| `hal.py` | `UBVM_HOME/` | HAL sealing |
| `leighton_weight.py` | `UBVM_HOME/` | Leighton Weight Engine |
| `mimir-ingest` | `MIMIR_HOME/` | Ingestion pipeline |
| `mimir-query` | `MIMIR_HOME/` | Query engine |

---

*Ex-OS: Your thoughts, staying yours, everywhere, verified, audited, and trusted.*
