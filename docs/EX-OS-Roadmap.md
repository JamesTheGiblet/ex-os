# The Starting Point

**What we know:**

1. **SCP** works — context engine, not file format
2. **Mimir** is sc-bound — no fine-tuning needed
3. **The Forge Stack** is the spine — Declare → Classify → Trust-score → Audit → Act
4. **Ex-OS** is the integration layer — the thing we're building
5. **Everything is sovereign** — no cloud, no data leaving hardware
6. **Everything is free** — MSL-1.0 licence

**What we're building:**

A complete, sovereign, self-learning, self-healing semantic operating system.

---

## Status Update — 2026-08-21

The phase plan below was written before the build started and still reads
"BUILDING" throughout. Per [`CHANGELOG.md`](../CHANGELOG.md), v0.1.0
(2026-08-20) shipped with all 13 core components built and 14/14 fresh-clone
tests passing. Actual phase status, cross-referenced against the changelog's
Good/Bad/Ugly lists:

| Phase | Status | Notes |
|-------|--------|-------|
| 0 — Foundation | ✅ Done | SCP, signing, ChronoSCRIBE, Leighton, DataCube lenses, HAL, UBVM interpreter all built and operational |
| 1 — Intelligence | 🔄 Partial | BuddAI memory/personality working; Mimir built but **not yet LLM-bound** (Ollama integration still missing); LEGION trading primitives not evidenced as built |
| 2 — Enforcement | 🔄 Partial | Leighton trust scoring and HAL seal operational; Replicant swarm runs but population dies out without manual food; Keystone Gate status unconfirmed |
| 3 — Knowledge | 🔄 Partial | Anchor and DataCube lenses working; DataCube bulk ingestion and Justitia not confirmed |
| 4 — Hardware | ❌ Stubbed | Bare-metal networking (UBVM-OS `net.c`) remains unfinished — this is the reason UBVM-OS was split off as its own effort |
| 5 — Integration | 🔄 Partial | Network daemon and dashboard built (dashboard shows OFFLINE until the daemon runs); one-command install existed but was broken in several places — repaired 2026-08-21, see Changelog |
| 6 — Distribution | ❌ Not started | No enterprise pilots yet; Ex-OS only validated on the phone/Termux it was built on |

The per-task tables below are the original pre-build plan and are kept for
history; treat the table above as the authoritative current status.

---

## The New Roadmap (From Scratch)

---

### Phase 0: Foundation — The Core (✅ DONE per v0.1.0 — see Status Update above)

| Task | Status | Validation |
| SCP v1.2 schema | 📅 | `scp.json` validator works |
| Ed25519 signing pipeline | 📅 | `sign.py` produces deterministic sigs |
| ChronoSCRIBE root ledger | 📅 | `ledger.py anchor-root` passes |
| Leighton Weight Engine | 📅 | λ formula implemented |
| DataCube five lenses | 📅 | FACT/OPINION/FICTION/CONTEXT/UNKNOWN |
| HAL seal command | 📅 | `hal.py seal` requires score file |
| UBVM interpreter | 📅 | Runs capsules, dispatches primitives |
| Event bus | 📅 | `queue.jsonl` append-only |

**Checkpoint:** All tests passing, fresh clone verifies

---

### Phase 1: Intelligence — The Mind (📅 BUILDING)

| Task | Status | Validation |
| Mimir binding capsule | 📅 | Binds to Phi-3-mini |
| Mimir persona defined | 📅 | Terse, direct, Forge-style |
| Mimir trust threshold | 📅 | λ < 0.6 not cited |
| BuddAI personality engine | 📅 | Intent detection, context awareness |
| BuddAI memory (SQLite) | 📅 | Short/long-term with decay |
| BuddAI 8 validators | 📅 | Hardware-specific checks |
| LEGION trading primitives | 📅 | fetch_ohlcv, backtest, validate |
| LEGION strategy pipeline | 📅 | generate → backtest → select → dry-run |

**Checkpoint:** Mimir answers, BuddAI reflects, LEGION trades

---

### Phase 2: Enforcement — The Immune System (📅 BUILDING)

| Task | Status | Validation |
| Keystone Gate | 📅 | Binds LLM to SCP, enforces compliance |
| Keystone Gate threshold | 📅 | λ > 0.85 confidence |
| HAL tiers 1–5 | 📅 | λ thresholds mapped |
| HAL seal enforcement | 📅 | Refuses below threshold |
| ChronoSCRIBE hard-fail | 📅 | No silent pass-through |
| Plasticity route learning | 📅 | Routes weight 0.1–2.0 |
| Replicant swarm core | 📅 | 7-phase tick: SENSE → DECIDE → RESOLVE → CLASSIFY → SCORE → WITNESS → DECAY |

**Checkpoint:** Keystone Gate blocks non-compliance, HAL seals, ChronoSCRIBE records

---

### Phase 3: Knowledge — The Memory (📅 BUILDING)

| Task | Status | Validation |
| Anchor expert system | 📅 | Rule-based, deterministic |
| Anchor genesis | 📅 | Constitution sealed |
| Anchor source registry | 📅 | Every claim traced to source |
| Anchor BEDROCK criteria | 📅 | Weight + independent corroboration |
| DataCube bulk ingestion | 📅 | One cube per record/row |
| DataCube lenses | 📅 | FACT/OPINION/FICTION/CONTEXT/UNKNOWN |
| Justitia legal ingestion | 📅 | Authority hierarchy decay |

**Checkpoint:** Anchor answers with 100% accuracy, DataCube classifies claims

---

### Phase 4: Hardware — The Body (📅 BUILDING)

| Task | Status | Validation |
| UEFI USB bootloader | 📅 | `BOOTX64.EFI` boots bare metal |
| UBVM-OS core interpreter | 📅 | C interpreter, containment classes |
| UBVM-OS shell | 📅 | REPL commands become capsules |
| ESP32 edge firmware | 📅 | 96-byte UDP protocol |
| ESP32 Fletcher-32 checksum | 📅 | Packet verification |
| Phone edge (Termux) | 📅 | Python UDP transmitter |
| Bare-metal networking | 📅 | lwIP or picoTCP port |

**Checkpoint:** USB boots, ESP32 sends events, phone transmits packets

---

### Phase 5: Integration — The Nervous System (📅 BUILDING)

| Task | Status | Validation |
| Network daemon | 📅 | Port 8080, unified API |
| Unified dashboard | 📅 | Single UI for all components |
| One-command install | 📅 | `curl | bash` deployment |
| API bridges | 📅 | SCP ↔ DataCube ↔ Leighton ↔ Chrono ↔ HAL |
| Nginx gateway | 📅 | Single entry point |
| Service orchestration | 📅 | systemd services |

**Checkpoint:** Dashboard shows all components, API returns full state

---

### Phase 6: Distribution — The Reach (📅 BUILDING)

| Task | Status | Validation |
| VPS production | 📅 | Hetzner CX22 operational |
| USB boot image | 📅 | On any x86_64 PC |
| ESP32 mesh | 📅 | 10+ nodes |
| Mobile edge | 📅 | S24 Ultra Termux |
| Enterprise pilot | 📅 | Healthcare or legal domain |

**Checkpoint:** Ex-OS deployed on all targets

---

## The Validation Philosophy

**Every phase must pass:**

| Gate | Criteria |
| **Code Complete** | All tasks implemented |
| **Tests Passing** | All unit/integration tests pass |
| **Fresh Clone Verified** | `git clone` → install → tests pass |
| **Documentation Updated** | Everything documented |
| **ChronoSCRIBE Anchored** | State recorded immutably |
| **HAL Sealed** | Phase completion signed |

---

## The Starting Point (Right Now)

We have:

- ✅ The vision (Ex-OS)
- ✅ The architecture (Forge Stack)
- ✅ The philosophy (sovereignty, trust, audit)
- ✅ The licence (MSL-1.0)
- ✅ The documentation (14 files)
- ✅ The proof (independent projects worked)

We are building:

- 🔄 The code (all of it)
- 🔄 The integration layer
- 🔄 The deployment

---

## Next Steps

Superseded by the v0.1.0 build (see [Status Update](#status-update--2026-08-21)
above) — the P0/P1/P2 items below were all written before the phase 0 build.
Current real priorities, drawn from `CHANGELOG.md`'s Bad/Ugly lists:

| Priority | Task |
|----------|------|
| **P0** | Fix relative-import fragility across `core/*/cli.py` (chronoscribe, datacube, hal, keystone, leighton, watermark, mimir) — same class of bug already fixed in `core/scp/cli.py`, still breaks `scripts/sign-everything.py` |
| **P0** | Reconcile `docs/EX-OS-deployment-guide.md` with the current `integration/` layout (it still describes the old root-level `UBVM-os` daemons) |
| **P1** | Integrate Ollama so Mimir and BuddAI have LLM support |
| **P1** | Give Leighton Weight Engine an automatic feedback loop (currently manual attestation only) |
| **P1** | Fix Replicant swarm energy economics so population doesn't die out without manual food |
| **P2** | Resolve the single-operator honesty problem (one `did:key` signs everything) |
| **P2** | Bare-metal networking for UBVM-OS (`net.c` still stubs) |
| **P3** | PostgreSQL backend for DataCube scaling beyond ~500 nodes |
| **P3** | Cross-VPS ChronoSCRIBE synchronisation |
| **P3** | First enterprise pilot (Axiom is packaged but unproven at scale) |

---

## The Starting Line

**We're at the starting line.**

The foundation is ready. The vision is clear. The code is waiting to be written.

**Everything is free. Everything is sovereign.**

Now we build.

---

*Ex-OS: Building from scratch.*
*With everything we've learned.*
*Because the ideas don't stop.*
