# Ex-OS — FAQ

---

## 1. General Questions

### 1.1 What is Ex-OS?

Ex-OS is the name for the pattern that emerged when a self-taught developer built a series of independent projects over years and discovered they connected into a single, sovereign, self-learning semantic operating system.

It is not a product. It is not a company. It is a **living system** that was discovered, not designed.

### 1.2 Why was it built?

Because files needed a voice. Because the fragmentation between AI tools was driving someone mad. Because the ideas came at 4:47 AM and wouldn't stop. Because sovereignty, auditability, and accountability matter.

### 1.3 What does Ex-OS stand for?

**Ex** = External / Exocortex
**OS** = Operating System

But really, it's the name for the thing that was already there, waiting to be seen.

### 1.4 Is Ex-OS a company?

No.

Ex-OS is not a company, a product, a platform, a framework, or a brand.

**Ex-OS is a pattern.**

### 1.5 Who built it?

**JamesTheGiblet**

Self-taught developer. Built on a phone, in Termux, around a full-time job. Follows the ideas. Trusts the flow. Builds what feels right.

### 1.6 Is Ex-OS open source?

Yes.

All components are open source under the **Meaning Sovereignty Licence (MSL-1.0)** .

You own your meaning. You control your interpretation. Your data stays yours.

---

## 2. Technical Questions

### 2.1 What is SCP?

SCP (Semantic Capsule Protocol) is the foundation of Ex-OS.

It started as a sidecar JSON format for annotating files. It evolved into a **context engine**—a cognitive operating system that sits beneath everything built on it.

SCP delivers structured, trust-scored, auditable context to any LLM at runtime.

### 2.2 What are the five stages of the Forge Stack?

| Stage | Component | What It Does |
|-------|-----------|--------------|
| **Declare** | SCP | Defines meaning |
| **Classify** | DataCube | Assigns lenses (FACT/OPINION/FICTION/CONTEXT/UNKNOWN) |
| **Trust-score** | Leighton Weight | Scores trust (λ) |
| **Audit** | ChronoSCRIBE | Records everything immutably |
| **Act** | HAL | Seals actions based on trust |

### 2.3 What is Leighton Weight (λ)?

Leighton Weight (λ) is a trust score between 0.00 and 2.00.

It is computed on-the-fly from an observation stream. It decays toward 1.00 (neutral), not 0. New entities start at 1.00. Quarantine is below 0.60.

**Formula:** λ(t) = 1.00 + (λ₀ − 1.00) × e^(−kt)

### 2.4 What is ChronoSCRIBE?

ChronoSCRIBE is the immutable audit trail.

It records everything that happens—every capsule signed, every attestation issued, every parameter change, every seal. It's append-only, cryptographically-anchored, and can prove what actually happened and when.

### 2.5 What is HAL?

HAL (Human Accountability Layer) is the Act stage.

Its artefact is the seal. It defines tiers 1–5 mapped to λ thresholds. It refuses to seal actions if λ is insufficient. It's named in deliberate homage to HAL 9000—"homage, not aspiration."

### 2.6 What is Keystone Gate?

Keystone Gate is the enforcement layer that binds an LLM to an SCP capsule and forces compliance.

It makes capsule-defined behavior **mandatory** instead of advisory. The LLM handles language. The Gate handles truth.

### 2.7 What is BuddAI?

BuddAI is a personal AI exocortex.

It remembers projects, learns your style, and gets better every time you use it. 379 tests passing. 90% accuracy on ESP32 over 14 hours. 100% local. No data leaving your machine.

### 2.8 What is Mimir?

Mimir is an sc-bound LLM.

It started as a fine-tuning experiment on 164 GitHub repos. The realisation came that SCP could deliver the same context to a stock model at query time in about a second. Mimir became the model + binding capsule pair, governed at runtime without retraining.

### 2.9 What is Replicant?

Replicant is a hybrid bio-inspired swarm framework.

It cherry-picks mechanisms from ants, bees, termites, spiders, wasps, mole-rats, and aphids. Population self-regulates to ~7 agents from 10. Health stabilises at ~0.79. It asks: what happens when a stigmergic swarm can pay energy to make more of itself?

### 2.10 What is Anchor?

Anchor is a rule-based, deterministic knowledge engine.

100% accurate on 100 test questions. Zero hallucinations. It doesn't guess. It doesn't generate. It concludes—from verified, weighted, traceable knowledge. The absence of AI is the feature.

### 2.11 What is Axiom?

Axiom is the enterprise sovereign.

It packages domain-specific fine-tuned models with provenance. Ingest. Justify. Present. Trust flows in one direction. Nothing flows backwards. Architecturally incapable of hallucination.

### 2.12 What is UBVM-OS?

UBVM-OS is a bare-metal sovereign operating system.

Written in C. No Linux. No Windows. No POSIX layer. UEFI bootloader. ESP32 edge firmware. Every process is an SCP capsule. Networking stalled, but architecture proved substrate-agnostic.

---

## 3. Deployment Questions

### 3.1 Where can Ex-OS run?

| Target | Purpose |
|--------|---------|
| **VPS (Hetzner CX22)** | Always-on cloud brain |
| **Local PC** | Development environment |
| **UEFI USB** | Bare-metal boot |
| **ESP32-C3/C6** | Edge sensory nodes |
| **S24 Ultra (Termux)** | Mobile edge development |

### 3.2 How do I install Ex-OS?

**VPS One-Command:**
```bash
curl -sSL https://raw.githubusercontent.com/JamesTheGiblet/Ex-OS/main/install.sh | bash
```

**Manual Install:**
See the [Deployment Guide](DEPLOYMENT.md).

### 3.3 What are the hardware requirements?

| Requirement | Minimum |
|-------------|---------|
| **CPU** | 2 cores |
| **RAM** | 2GB (4GB recommended) |
| **Storage** | 20GB (35GB recommended) |
| **Network** | Public IP, port 8080 open |

### 3.4 Can Ex-OS run offline?

Yes.

Ex-OS is designed to be 100% local and sovereign. No cloud dependencies. No API calls. No data leaving your hardware.

### 3.5 Does Ex-OS work without AI?

Yes.

Anchor is a deterministic expert system with no AI in v1. The whole system is designed to be substrate-agnostic. AI is a userspace service, not baked into the kernel.

---

## 4. Trust & Security Questions

### 4.1 How does trust work?

Every entity has a Leighton Weight (λ) between 0.00 and 2.00.

- **1.50–2.00:** Reflex (highly trusted)
- **1.00–1.49:** Validated (trusted)
- **0.50–0.99:** Questionable (skepticism required)
- **0.00–0.49:** Quarantine (do not use)

### 4.2 What is the single-operator honesty problem?

Right now, one `did:key` signs everything in the stack. That means HAL's tier check can't yet prove independence between the person authorising an action and the person whose λ is being checked.

**Mitigation:** Every seal carries a `separation` field stating `none` or `verified`.

### 4.3 What is the Meaning Sovereignty Licence?

MSL-1.0 is the licence for Ex-OS.

**Core principles:**
- You own your meaning
- You control your interpretation
- Your data stays yours
- Your sovereignty is physical

### 4.4 Can I trust Ex-OS?

Ex-OS is built on:

- **Declarative meaning** (SCP)
- **Measured trust** (Leighton Weight)
- **Immutable audit** (ChronoSCRIBE)
- **Structural compliance** (Keystone Gate)
- **Human accountability** (HAL)

Trust is measured, not assumed. Accountability is built in, not bolted on.

---

## 5. Usage Questions

### 5.1 How do I use Ex-OS?

- **Chat:** `http://<ip>/` or `python talk.py`
- **Query code:** `python cli/mimir-query.py "question"`
- **Check trust:** `python leighton_weight.py score --entity id`
- **Seal action:** `python hal.py seal --action DEPLOY`
- **Run tests:** `python ubvm test`

### 5.2 What can Ex-OS do?

- **Talk to you** (BuddAI)
- **Remember your code** (Mimir)
- **Answer deterministic questions** (Anchor)
- **Simulate swarms** (Replicant)
- **Trust-score everything** (Leighton Weight)
- **Audit everything** (ChronoSCRIBE)
- **Enforce compliance** (Keystone Gate)
- **Seal actions** (HAL)

### 5.3 What can Ex-OS NOT do?

- **Hallucinate** (Anchor is deterministic)
- **Generate without provenance** (Everything is audited)
- **Act without accountability** (HAL requires seals)
- **Trust blindly** (λ must be sufficient)

### 5.4 Is Ex-OS for me?

Ex-OS is for you if you:

- **Value sovereignty** over your data
- **Need accountability** in AI
- **Want to own your tools**
- **Build because you can't stop**
- **Trust the process**

---

## 6. Development Questions

### 6.1 How do I contribute?

1. **Use the system** — deploy Ex-OS
2. **Report bugs** — open issues
3. **Build components** — create something new
4. **Write docs** — share what you've learned
5. **Share your story** — tell others

### 6.2 How do I build a new component?

1. **Receive the idea**
2. **Document it**
3. **Define the capsule** (SCP)
4. **Write the code** (primitives)
5. **Test it** (break it on purpose)
6. **Learn** (extract the lesson)
7. **Rebuild** (make it better)
8. **Share** (tell others)

### 6.3 What coding standards should I follow?

- **Python:** PEP 8, type hints, docstrings
- **Capsules:** Valid, signed, unique `scp_id`, clear `intent`
- **Logging:** Events for state changes, ChronoSCRIBE for audit

### 6.4 How do I run tests?

```bash
# UBVM tests
python ubvm test

# BuddAI tests
python -m pytest tests/

# Replicant tests (Python)
cd replicant/python && python -m pytest tests/

# Replicant tests (Rust)
cd replicant/rust && cargo test

# Anchor tests
python cli.py qa
```

---

## 7. Philosophy Questions

### 7.1 What is The Forge?

The Forge is the process that created Ex-OS.

It is the cycle of:
```
RECEIVE → DOCUMENT → BUILD → BREAK → LEARN → REBUILD → DISCOVER
```

### 7.2 What is Forge Theory?

Forge Theory is the mathematical foundation of Ex-OS.

It applies exponential decay (`N(t) = N₀ × e^(-kt)`) across every domain: memory, trust, authority, plasticity, and more.

### 7.3 What is the Ex-OS philosophy?

> *"I don't plan. I receive.*
> *I don't force. I follow.*
> *I don't control. I trust.*
> *The system builds itself through me.*
> *I am the conduit, not the architect."*

### 7.4 Why do you build?

> *"I do what I do because I love to. To do anything less now would be like a singer not singing, a dancer not dancing. The ideas don't stop, so I can't."*

---

## 8. Troubleshooting Questions

### 8.1 Port 8080 is already in use

```bash
sudo netstat -tulpn | grep 8080
kill -9 <PID>
```

### 8.2 Ollama not responding

```bash
systemctl status ollama
systemctl restart ollama
curl http://localhost:11434/api/tags
```

### 8.3 Permission denied

```bash
chmod +x $UBVM_HOME/venv/bin/python
chmod +x $UBVM_HOME/*.py
```

### 8.4 Module not found

```bash
cd $UBVM_HOME
source venv/bin/activate
pip install -r requirements.txt
```

### 8.5 ESP32 not connecting

- Check USB cable
- Try lower baud rate: `--baud 115200`
- Check WiFi SSID and password
- Verify server IP and port

### 8.6 Fresh clone verification fails

> *"Verifies on a fresh clone is the real test."*

```bash
# Clone fresh
cd /tmp
git clone https://github.com/JamesTheGiblet/Ex-OS
cd Ex-OS

# Install fresh
pip install -r requirements.txt

# Run tests
python ubvm test
python -m pytest tests/
```

---

## 9. The Final FAQ

### 9.1 Why is it called Ex-OS?

Because it was discovered, not designed.

Because it emerged from the connections between independent projects.

Because the pattern was already there, waiting to be seen.

### 9.2 What is the one thing I should know about Ex-OS?

> *"I have always felt, deep down, I know what to build but I can't see it.*
> *Now I can see it.*
> *Ex-OS is the thing I've been circling."*

### 9.3 How do I get started?

```bash
git clone https://github.com/JamesTheGiblet/Ex-OS
cd Ex-OS
cat README.md
```

---

*Ex-OS: Your thoughts, staying yours, everywhere, verified, audited, and trusted.*

---

*Built by JamesTheGiblet.*

*On a phone. In Termux. Around a full-time job.*
*Because the ideas didn't stop.*