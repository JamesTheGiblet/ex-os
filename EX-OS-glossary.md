# Ex-OS — Glossary

---

## A

### Act

The fifth stage of the Forge Stack. Enforced by HAL. Its artefact is the **seal**. Where record-keeping becomes consequence.

### Anchor

A rule-based, deterministic knowledge engine. 100% accurate on 100 test questions. Zero hallucinations. Built in a 6-hour sprint with 2,000 mathematical proofs. The absence of AI is the feature.

### Attestation

A signed ledger event (`event.attestation.issued`) recording a judgement on a past event. Hash-linked to the event it judges. Fills the "observe outcomes" arrow in the Leighton Loop.

### Audit

The fourth stage of the Forge Stack. Enforced by ChronoSCRIBE. Its artefact is the **ledger**. The immutable record of everything that happened.

### Axiom

The enterprise sovereign product built on Mimir. Packages domain-specific fine-tuned models with provenance. Three components: Ingest, Justify, Present. Architecturally incapable of hallucination.

---

## B

### BEDROCK

The highest knowledge tier in Anchor. Requires weight above bedrock threshold AND corroboration from N independent sources across M distinct independence groups. Cannot be achieved by a single source alone.

### BuddAI

A personal AI exocortex. Local LLM partner that remembers projects, learns style, and gets better every time you use it. 379 tests passing. 90% accuracy on ESP32 over 14 hours. 100% local.

---

## C

### Capsule

The atomic unit of meaning in SCP. Prose-only term—never used in schemas, filenames, or code. The actual artefact is an `sc` (`.sc.json` file). Declares intent, triggers, actions.

### ChronoSCRIBE

The Audit stage of the Forge Stack. Its artefact is the **ledger**. Append-only, cryptographically-anchored record of everything that happens. Full backronym: Signed Chronological Record of Immutable Behavioural Events.

### Classify

The second stage of the Forge Stack. Enforced by DataCube. Its artefact is the **cube**. Assigns epistemic status (lens) to claims.

### Consumer

A system built on the Forge Stack. Examples: UBVM, Mimir, BuddAI, Replicant, Anchor, Axiom, UBVM-OS.

### Contradicts

A relational field in DataCube that sits outside the lens system. Links two cubes that contradict each other. Replaced the original COUNTER lens.

### Cube

The artefact produced by DataCube. A classified claim with a lens (FACT/OPINION/FICTION/CONTEXT/UNKNOWN) and a namespace (`event.*`, `state.*`, `domain.*`, `behaviour.*`).

---

## D

### DataCube

The Classify stage of the Forge Stack. Its artefact is the **cube**. Five lenses (FACT, OPINION, FICTION, CONTEXT, UNKNOWN) plus a `contradicts` relational field. Has a "store"—never a "ledger."

### Declare

The first stage of the Forge Stack. Enforced by SCP. Its artefact is the **sc** (`.sc.json` file). Defines meaning and intent.

### did:key

The identity format used for signing in Ex-OS. Current key: `did:key:z6MktudRY5LBZJeE13BiF4BeisAwWs7gvg6srh2GwLAMKDwJ`. Ed25519 signatures.

---

## E

### Ed25519

The deterministic signing algorithm used in Ex-OS. Re-running `sign.py` over unchanged content produces byte-identical signatures. A "no diff" confirms nothing changed.

### Evidence Mass (n)

A value that travels alongside λ in Leighton Weight Engine. Decays at the same rate `k`. Gates HAL tiers. Provides Sybil resistance.

### Ex-OS

The name for the pattern that emerged from independent projects. A sovereign, self-learning, self-healing semantic operating system. Discovered, not designed.

---

## F

### FACT

One of DataCube's five lenses. Verified, concrete claims. The highest epistemic status.

### FICTION

One of DataCube's five lenses. Speculative, imagined, not real. Claims that are hypothetical or unverified.

### Forge Stack

The five-stage spine of Ex-OS: Declare (SCP) → Classify (DataCube) → Trust-score (Leighton Weight) → Audit (ChronoSCRIBE) → Act (HAL).

### Forge Theory

The mathematical foundation of Ex-OS. Applies exponential decay (`N(t) = N₀ × e^(-kt)`) across every domain: memory, trust, authority, plasticity, and more.

### Forward-Only Parameters

Parameters `k`, `β₊`, and `ρ` in Leighton Weight Engine are forward-only, never retroactive. Each version carries an effective-from timestamp. Historical λ stays reproducible by construction.

---

## G

### Genesis

The sealed founding document of Anchor. Contains constitution, council, parameters. Written once. Never modified. Anchor will not boot against a broken genesis.

---

## H

### HAL

The Act stage of the Forge Stack. Its artefact is the **seal**. Tiers 1–5 mapped to λ thresholds. Refuses to seal if λ insufficient. Named in homage to HAL 9000—"homage, not aspiration."

### Human Accountability Layer

The full name of HAL. The Act stage. Where a human is made accountable for having let something happen.

---

## I

### Independence Group

A field in Anchor's source registry that prevents false corroboration. Ten datasheets from the same manufacturer are not ten independent sources. They share an independence_group.

### inherits

An SCP field that records the constitution in force at signing. Historical, not a live pointer. A later governance version doesn't retroactively invalidate an old capsule's `inherits` declaration.

---

## K

### Keystone Gate

The enforcement layer that binds an LLM to an SCP capsule and forces compliance. Makes capsule-defined behavior mandatory instead of advisory. Confidence threshold: λ > 0.85.

### k (Decay Constant)

The decay rate in Leighton Weight Engine and Forge Theory. Always per-domain. Never conflated with λ itself.

---

## L

### Leighton Loop

The trust update cycle: `score → observe outcomes → update`. The "observe outcomes" arrow is filled by attestations.

### Leighton Weight (λ)

A trust score between 0.00 and 2.00. Computed on-the-fly from an observation stream. Decays toward 1.00 (neutral) using λ(t) = 1.00 + (λ₀ − 1.00) × e^(−kt). Quarantine below 0.60.

### Leighton Weight Engine

The Trust-score stage of the Forge Stack. Computes λ for entities based on their observed track record. Feeds HAL.

### Lens

An epistemic status in DataCube. Five lenses: FACT, OPINION, FICTION, CONTEXT, UNKNOWN. Always spelled in caps.

### Ledger

The artefact of ChronoSCRIBE. Append-only, cryptographically-anchored. Never used for DataCube's store. Terms kept distinct.

---

## M

### Mimir

An sc-bound LLM. Started as a fine-tuning experiment on 164 GitHub repos. Realisation: SCP could deliver the same context to a stock model at query time in ~1 second. Became model + binding capsule pair.

### MSL-1.0

Meaning Sovereignty Licence v1.0. The licence for Ex-OS. Core principles: You own your meaning. You control your interpretation. Your data stays yours.

---

## N

### Namespace

A classification axis in DataCube. Independent of lenses. Four namespaces: `event.*`, `state.*`, `domain.*`, `behaviour.*`. Says what kind of thing, not epistemic status.

### Neutral-Attractor Decay

Leighton Weight's core trust model. λ decays toward 1.00 (neutral), not 0. New entities start at 1.00. Inactive entities drift toward "unknown," not "distrusted."

---

## O

### OPINION

One of DataCube's five lenses. Subjective, interpretive, based on judgement. Not verified as FACT.

### Observer

In the Leighton Loop, the entity that observes outcomes and feeds them into the trust update.

---

## P

### Plasticity

An Ex-OS component (extension in UBVM). Adaptive routing. Records capsule execution chains, updates route weights based on reward signals, promotes successful routes to reflexes.

### Primitive

A registered Python function that performs a single atomic operation in UBVM. The only place executable logic lives. Capsules call primitives; primitives do the work.

### Provenance

The tracking of source, trust, and lineage for every answer. Enforced by SCP capsules, Leighton Weight scoring, and ChronoSCRIBE auditing.

---

## Q

### Quarantine

A state where λ < 0.60. No HAL tier reachable. No seal can be issued. The entity is quarantined until λ recovers above 0.60.

---

## R

### Reflex

A route or entity with λ > 1.80 in Leighton Weight/Plasticity. Highly trusted. Promoted automatically.

### Replicant

A hybrid bio-inspired swarm framework built on the Forge Stack. Cherry-picks mechanisms from ants, bees, termites, spiders, wasps, mole-rats, and aphids. Population self-regulates to ~7 agents.

### Route

A capsule execution path in Plasticity. Has a weight (0.1–2.0). Successful routes gain weight. Routes above 1.8 become reflexes.

### Rule Engine

The deterministic rule evaluation system in Anchor. Rules are capsules. Fire in strict hierarchy: AXIOM → DERIVED → CONTEXTUAL. Same state, same input → same output.

---

## S

### sc

The artefact of SCP. Lowercase. `.sc.json`. Never called "capsule" in schemas or code. The atomic unit of meaning.

### SCP

Semantic Capsule Protocol. The Declare stage of the Forge Stack. A context engine / cognitive operating system. Delivers structured, trust-scored, auditable context to any LLM at runtime.

### SCP Lite

A signed minimal subset of SCP that omits `inherits`/`licence`. For quick sidecar use without full governance overhead.

### Seal

The artefact of HAL. An authorised action, sealed and recorded. Requires verified `--authoriser-score-file`. Refused if λ insufficient for requested tier.

### Separation

A field in every HAL seal. `none` = same key signed authoriser and seal. `verified` = distinct identities. Documents the single-operator honesty problem.

### Signature

Ed25519 signature on an SCP capsule. Deterministic. Over canonicalised JSON. Same key for everything in the stack.

### Sovereignty

The core principle of Ex-OS. Your thoughts are yours. No cloud. No API calls. No data leaving your hardware. Physical sovereignty is the goal.

### Source Registry

A system in Anchor that tracks every piece of knowledge to a registered source. No anonymous ingest. Sources have default weights, decay rates, and expiry dates.

### Store

The artefact of DataCube. Never called a "ledger." Kept distinct from ChronoSCRIBE's artefact to avoid conflating classification data with audit trail.

### supersedes

An SCP field that carries supersession information. Never by filename tricks. A `.SUPERSEDED` rename was tried once and reverted.

### Swarm

Replicant's collective of agents. Self-regulating population. Health stabilises at ~0.79. Every claim is classified, scored, and witnessed.

---

## T

### Thaumiel

The highest containment class in UBVM. System-level. Governs other capsules. One of four classes: Safe, Euclid, Keter, Thaumiel.

### Tier

HAL's action levels 1–5. Mapped to λ thresholds. Consumer-defined—what each tier authorises is up to the consumer.

### Trigger

An event that causes a capsule to execute in UBVM. Three types: `on_load` (once), `cron` (schedule), `on_event` (event match).

### Trust-score

The third stage of the Forge Stack. Enforced by Leighton Weight Engine. Its artefact is **λ** (Leighton Weight). Scores trustworthiness of entities.

---

## U

### UBVM

Universal Behavioural Virtual Machine. The runtime engine for SCP capsules. JSON-driven. Executes capsules, dispatches primitives, handles triggers, processes events. 73 primitives, 11 extensions, 88 capsules.

### UBVM-OS

The bare-metal sovereign operating system. Written in C. No Linux, Windows, or POSIX layer. UEFI bootloader. ESP32 edge firmware. Networking stalled; architecture proven substrate-agnostic.

### UNKNOWN

One of DataCube's five lenses. Not enough information yet. The default landing lens for bulk ingestion. Ready to be classified and validated.

---

## V

### validate_self

A UBVM primitive that validates the running capsule against its schema. Ensures capsules are valid, signed, and have all required fields.

### Verified

A HAL separation state. Indicates that a genuinely distinct identity issued the authorising score. Future state (not yet achieved in single-operator deployment).

---

## W

### Weight

In Leighton Weight Engine, λ is the trust weight. In Anchor, weight is earned or lost through events. In Plasticity, route weight is clamped 0.1–2.0.

### Witness

ChronoSCRIBE's role. The immutable witness. Records what happened, when, why, and what state the system was in when it did it.

---

## X, Y, Z

### λ (Lambda)

See Leighton Weight.

### β₊ (Beta Plus)

The upward step size in Leighton Weight Engine's update rule. Per-domain. Calibrated alongside `k`. Initial value: 0.10.

### ρ (Rho)

The asymmetry ratio in Leighton Weight Engine. `β₋ = ρ × β₊`. Stack-wide, not per-domain. Initial value: 2.0.

### σ (Sigma)

Evidence mass threshold in Leighton Weight Engine. Gates HAL tiers. Provides Sybil resistance. Initial value: 3.0.

---

## Quick Reference Table

| Term | Short Definition |
| **SCP** | Context engine / cognitive operating system |
| **sc** | The artefact (`.sc.json`) |
| **λ** | Trust score (0.00–2.00) |
| **Cube** | DataCube artefact |
| **Ledger** | ChronoSCRIBE artefact |
| **Seal** | HAL artefact |
| **Capsule** | Prose-only for `sc` |
| **Primitive** | Atomic UBVM function |
| **Consumer** | System built on Forge Stack |
| **Forge Stack** | Declare → Classify → Trust-score → Audit → Act |

---

*Ex-OS: Your thoughts, staying yours, everywhere, verified, audited, and trusted.*

---

*Built by JamesTheGiblet.*
*On a phone. In Termux. Around a full-time job.*
*Because the ideas didn't stop.*
