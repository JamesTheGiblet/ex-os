# Changelog

All notable changes to Ex-OS are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Each entry follows the **Good / Bad / Ugly** pattern:

- **Good** — What worked, what was achieved, what succeeded
- **Bad** — What broke, what was difficult, what failed
- **Ugly** — What was painful, what needs revisiting, what is technical debt

---

## [Unreleased]

### Install & CLI Hardening

**Good:**

- Fixed a fatal bug in `install.sh`: `mkdir -p buddai_memory.db` collided with the real SQLite file of the same name and aborted every install under `set -e`
- Added the missing `requirements.txt` (`requests`, `cryptography`) — previously every `pip install -r requirements.txt` in `install.sh` silently no-op'd
- Corrected the four "initialise" steps in `install.sh` (signing key, Leighton engine, ChronoSCRIBE, BuddAI memory) to match the real `sign.py` / `engine.py` / `ledger.py` / `memory.py` interfaces instead of calling subcommands that never existed
- Removed `install.sh` references to `scheduler_daemon.py` and an `exos-scheduler` systemd service — neither exists anywhere in the repo
- Fixed `core/scp/cli.py` to run as a plain script (`python core/scp/cli.py ...`) as well as via `-m core.scp.cli` — it previously only worked in module form
- Fixed a Windows-only crash where the ✅/❌ status emoji broke on `cp1252`-encoded consoles immediately after a successful operation (e.g. `generate-key` would create the key, then crash on its own confirmation message)

**Bad:**

- `docs/EX-OS-deployment-guide.md` still describes the old `UBVM-os` layout (root-level `network_daemon.py`/`scheduler_daemon.py`) rather than the current `integration/` layout — not yet reconciled

**Ugly:**

- The same relative-import fragility that broke `core/scp/cli.py` exists across most `core/*/cli.py` entry points (`chronoscribe`, `datacube`, `hal`, `keystone`, `leighton`, `watermark`, `mimir`) — `scripts/sign-everything.py` shells out to several of these directly (`python core/chronoscribe/cli.py anchor ...`) and hits the identical `ImportError` / `UnicodeEncodeError` pair. Only `core/scp/cli.py` has been fixed so far; the rest is outstanding.

---

## [0.1.0] — 2026-08-20

### The Build — Ex-OS Complete

**Good:**

- All 13 core components built and tested
- 14/14 fresh clone verification tests passing
- Complete documentation suite (14 files)
- MSL-1.0 licence applied
- All components work offline, no cloud dependencies
- Built entirely on a phone (Samsung S24 Ultra, Termux)
- Swarm (Replicant) self-regulates population to ~16 agents
- BuddAI memory system functional with Forge Theory decay
- Anchor deterministic expert system answers with provenance
- Axiom enterprise packaging working
- Leighton Weight Engine trust scoring (λ) operational
- ChronoSCRIBE ledger append-only, cryptographically-anchored
- HAL seal command enforces λ thresholds
- DataCube five lenses: FACT, OPINION, FICTION, CONTEXT, UNKNOWN
- Mimir context engine ready for LLM integration
- UBVM interpreter runs capsules, dispatches primitives
- Network daemon exposes API on port 8080
- Dashboard web UI shows system status

**Bad:**

- Bare-metal networking (UBVM-OS) remains unfinished — `net.c` still stubs
- Ollama not yet integrated — Mimir and BuddAI don't have LLM support
- Dashboard shows OFFLINE until network daemon is running
- Replicant swarm population dies out without food added manually
- Leighton Weight Engine requires manual attestation — no automatic feedback loop yet
- Single-operator honesty problem — one `did:key` signs everything
- No PostgreSQL backend for DataCube scaling (>500 nodes)
- No cross-VPS ChronoSCRIBE synchronisation
- No mobile app or browser WASM build yet

**Ugly:**

- Bare-metal networking is genuinely hard — NIC drivers from scratch
- The networking wall is the reason UBVM-OS was split off
- Line-ending corruption (`core.autocrlf`) can break `.sig` sidecar verification
- Only a fresh clone catches this — local passes can be false
- Replicant energy economics require manual tuning to sustain population
- No enterprise pilots yet — Axiom is packaged but unproven at scale
- Documentation is complete but needs real-world validation
- The entire system was built on a phone with no CI/CD

---

## What Was Built

### Core Components

| Component | File | Status |
|-----------|------|--------|
| SCP | `core/scp/sign.py` | ✅ |
| ChronoSCRIBE | `core/chronoscribe/ledger.py` | ✅ |
| Leighton Weight | `core/leighton/engine.py` | ✅ |
| HAL | `core/hal/seal.py` | ✅ |
| DataCube | `core/datacube/lenses.py` | ✅ |
| UBVM | `runtime/ubvm/interpreter.py` | ✅ |
| UBVM Primitives | `runtime/ubvm/primitives.py` | ✅ |
| Network Daemon | `integration/network_daemon.py` | ✅ |
| Dashboard | `integration/dashboard/index.html` | ✅ |
| Mimir | `intelligence/mimir/` | ✅ |
| BuddAI | `intelligence/buddai/` | ✅ |
| Anchor | `applications/anchor/anchor.py` | ✅ |
| Replicant | `applications/replicant/swarm.py` | ✅ |
| Axiom | `applications/axiom/axiom.py` | ✅ |

### Documentation

| File | Status |
|------|--------|
| `README.md` | ✅ |
| `LICENCE` | ✅ |
| `EX-OS-extended-documentation.md` | ✅ |
| `EX-OS-the-implementation.md` | ✅ |
| `EX-OS-the-living-system.md` | ✅ |
| `EX-OS-the-companion.md` | ✅ |
| `EX-OS-the-forge.md` | ✅ |
| `EX-OS-the-missing-pieces.md` | ✅ |
| `EX-OS-deployment-guide.md` | ✅ |
| `EX-OS-API-reference.md` | ✅ |
| `EX-OS-contributing-guide.md` | ✅ |
| `EX-OS-FAQ.md` | ✅ |
| `EX-OS-glossary.md` | ✅ |
| `EX-OS-video-script.md` | ✅ |

---

## Leighton Weight — Trust Scoring

### Overview

Leighton Weight (λ) is the trust score between 0.00 and 2.00. It is computed on-the-fly from an observation stream and decays toward 1.00 (neutral).

**Formula:**y
-
