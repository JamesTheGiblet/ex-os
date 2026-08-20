# Ex-OS — Contributing Guide

---

## 1. Welcome

Thank you for your interest in Ex-OS.

This is not a typical open-source project. It is a **living system** that emerged from years of independent building. The code is open. The pattern is shared. The journey is yours to discover.

**You are not joining a project. You are joining a process.**

---

## 2. Who We Are

### 2.1 The Builder

**JamesTheGiblet**

- Self-taught developer
- Built Ex-OS on a phone, in Termux, around a full-time job
- Follows the ideas, trusts the flow
- Believes in sovereignty, auditability, and accountability

### 2.2 The Community

Ex-OS is for:

- **Builders** who create because they can't stop
- **Learners** who break things on purpose
- **Discoverers** who trust the process
- **Forgers** who follow the flow
- **Sovereignty advocates** who want to own their data
- **AI accountability advocates** who want verifiable answers

---

## 3. How to Contribute

### 3.1 Ways to Contribute

| Contribution | Difficulty | Impact |
| **Use the system** | ⭐ | High |
| **Report bugs** | ⭐ | High |
| **Write documentation** | ⭐⭐ | High |
| **Build a component** | ⭐⭐⭐ | Very High |
| **Improve existing code** | ⭐⭐⭐ | Very High |
| **Write tests** | ⭐⭐ | High |
| **Share your story** | ⭐ | Very High |

### 3.2 What We Need Most

1. **Testers** — People who deploy Ex-OS and report what breaks
2. **Documenters** — People who write guides and examples
3. **Builders** — People who create new components
4. **Storytellers** — People who share how they use Ex-OS

### 3.3 What We Don't Need

- **Theory** — We have enough ideas
- **Planning** — We follow the flow
- **Permission** — We build what we feel
- **Politics** — We build for sovereignty

---

## 4. The Forge Process

### 4.1 How We Build

```txt
RECEIVE → DOCUMENT → BUILD → BREAK → LEARN → REBUILD → DISCOVER
```

| Step | What It Means |
| **Receive** | Pay attention to ideas that come |
| **Document** | Write everything down |
| **Build** | Create what feels right |
| **Break** | Test it, push it, find its limits |
| **Learn** | Extract the lesson from the breaking |
| **Rebuild** | Make it better |
| **Discover** | Look for the pattern |

### 4.2 The Forge Principles

1. **Receive** — The ideas don't stop, so we can't
2. **Document** — The act of documentation is the act of creation
3. **Build** — Build what you feel, what you see
4. **Break** — Break it on purpose, learn from the breaking
5. **Learn** — The lesson is in the breaking
6. **Rebuild** — Each rebuild is better than the last
7. **Discover** — The pattern reveals itself slowly

### 4.3 The Forge Ethos

> *"I don't plan. I receive.*
> *I don't force. I follow.*
> *I don't control. I trust.*
> *The system builds itself through me.*
> *I am the conduit, not the architect."*

---

## 5. Repository Structure

### 5.1 Component Repositories

| Repository | What It Is |
| [UBVM-os](https://github.com/JamesTheGiblet/UBVM-os) | Core runtime |
| [mimir](https://github.com/JamesTheGiblet/mimir) | Code intelligence |
| [BuddAI](https://github.com/JamesTheGiblet/BuddAI) | Cognitive exocortex |
| [replicant](https://github.com/JamesTheGiblet/replicant) | Bio-inspired swarm |
| [anchor](https://github.com/JamesTheGiblet/anchor) | Expert system |
| [axiom](https://github.com/JamesTheGiblet/axiom) | Enterprise sovereign |
| [UBVM-OS](https://github.com/JamesTheGiblet/UBVM-OS) | Bare-metal build |

### 5.2 Documentation Repository

| File | What It Is |
| [README.md](README.md) | The Origin Story |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Extended Documentation |
| [MANIFESTO.md](MANIFESTO.md) | The Philosophy |
| [IMPLEMENTATION.md](IMPLEMENTATION.md) | The Code |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Installation Guide |
| [CONTRIBUTING.md](CONTRIBUTING.md) | This Document |
| [API.md](API.md) | API Reference |

---

## 6. Development Workflow

### 6.1 Local Development (S24 Ultra / Termux)

```bash
# Install Termux
pkg update && pkg upgrade
pkg install python git openssh

# Clone repositories
git clone https://github.com/JamesTheGiblet/UBVM-os
git clone https://github.com/JamesTheGiblet/mimir
git clone https://github.com/JamesTheGiblet/BuddAI

# Set environment
export UBVM_HOME=$HOME/UBVM-os
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=gemma2:2b

# Install dependencies
cd $UBVM_HOME
pip install -r requirements.txt

# Run tests
python ubvm test
```

### 6.2 VPS Development

```bash
# Clone fresh
cd /tmp
git clone https://github.com/JamesTheGiblet/Ex-OS
cd Ex-OS

# Install
pip install -r requirements.txt

# Run tests
python ubvm test
python -m pytest tests/
python cli.py qa
```

### 6.3 Session Workflow

```bash
# Start session
./termux-start.sh

# Make changes
# ... edit code ...

# Run tests
python ubvm test

# End session
./termux-finish.sh
```

---

## 7. Component Development

### 7.1 Building a New Component

1. **Receive the idea** — Pay attention to what comes
2. **Document it** — Write down what you see
3. **Define the capsule** — Create an SCP capsule
4. **Write the code** — Build the primitive(s)
5. **Test it** — Break it on purpose
6. **Learn** — Extract the lesson
7. **Rebuild** — Make it better
8. **Share** — Tell others what you discovered

### 7.2 Component Template

```python
# new_component.py
# A new Ex-OS component

def register() -> dict:
    """
    Register primitives for this component.
    """
    return {
        "new_primitive": new_primitive,
        "another_primitive": another_primitive
    }

def new_primitive(params: dict, context: dict) -> dict:
    """
    Description of what this primitive does.

    params: Arguments from the capsule action
    context: Runtime context (scp_id, ubvm_home, timestamp, env)

    Returns: {"status": "ok", "result": result}
    """
    # Do the work
    result = do_something(params)
    return {"status": "ok", "result": result}
```

### 7.3 Component Capsule Template

```json
{
    "scp_version": "0.1",
    "scp_id": "exos/component-name",
    "object_class": "Safe",
    "intent": "What this component does.",
    "containment": {
        "read_only": false,
        "audit_log": true,
        "kill_switch": false
    },
    "behaviours": [
        {
            "trigger": "on_load",
            "actions": [
                {"primitive": "new_primitive", "params": {}}
            ]
        }
    ]
}
```

---

## 8. Coding Standards

### 8.1 Python

- **Style:** PEP 8
- **Type Hints:** Use type hints for all function signatures
- **Docstrings:** Document all public functions
- **Tests:** Write unit tests for all primitives

### 8.2 Capsules

- **Valid:** Must pass `validate_self`
- **Signed:** Must be signed with Ed25519
- **Unique:** `scp_id` must be unique
- **Intent:** Must have a clear `intent` field

### 8.3 Logging

- **Events:** Use `emit_event` for all state changes
- **Errors:** Use `log` for errors and warnings
- **Audit:** All important actions must be recorded in ChronoSCRIBE

---

## 9. Testing

### 9.1 Running Tests

```bash
# UBVM tests
python ubvm test

# BuddAI tests
python -m pytest tests/

# Replicant tests (Python)
cd replicant/python
python -m pytest tests/

# Replicant tests (Rust)
cd replicant/rust
cargo test

# Anchor tests
python cli.py qa
```

### 9.2 Writing Tests

```python
import unittest

class TestNewPrimitive(unittest.TestCase):
    def test_primitive_works(self):
        result = new_primitive({"param": "value"}, {})
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["result"], "expected")
```

### 9.3 Fresh Clone Verification

> *"Verifies on a fresh clone is the real test."*

```bash
# Clone fresh
cd /tmp
git clone https://github.com/JamesTheGiblet/Ex-OS
cd Ex-OS

# Install fresh
pip install -r requirements.txt

# Run all tests
python ubvm test
python -m pytest tests/
python cli.py qa
```

---

## 10. Governance

### 10.1 The Constitution

Ex-OS is governed by the **Meaning Sovereignty Licence (MSL-1.0)** .

**Core principles:**

- You own your meaning
- You control your interpretation
- Your data stays yours

### 10.2 Single-Operator Disclosure

> *"Right now, one `did:key` signs everything in the stack. That means HAL's tier check can't yet prove independence between the person authorising an action and the person whose λ is being checked."*

**Every seal carries a `separation` field:**

- `none` — Single operator (current state)
- `verified` — Distinct identities (future state)

### 10.3 Decision Making

- **Decisions** are made by those who build
- **Direction** emerges from the work
- **Vision** is discovered, not chosen

---

## 11. Community

### 11.1 How to Connect

- **GitHub:** [JamesTheGiblet](https://github.com/JamesTheGiblet)
- **Email:** gibletscreations@gmail.com
- **Issues:** Open an issue in the relevant repository

### 11.2 How to Share

1. **Deploy Ex-OS** on your own hardware
2. **Build something** — create a new component
3. **Write about it** — share your experience
4. **Tell your story** — what did you discover?

### 11.3 The Ex-OS Ethos

> *"I do what I do because I love to. To do anything less now would be like a singer not singing, a dancer not dancing."*

---

## 12. Roadmap

### 12.1 What's Done

- [x] All components built
- [x] Documentation complete
- [x] Deployment guides written
- [x] API reference defined
- [x] Contributing guide written

### 12.2 What's Next

- [ ] Unified Dashboard
- [ ] One-Command Install
- [ ] Enterprise Pilots
- [ ] Full Integration Layer

### 12.3 What's Always

- [ ] Keep building
- [ ] Keep breaking
- [ ] Keep learning
- [ ] Keep discovering

---

## 13. The Final Word

### 13.1 To Contributors

You are not joining a project. You are joining a process.

The ideas don't stop. The cycle continues. The pattern reveals itself.

**Build what you feel. Follow the flow. Share what you discover.**

### 13.2 To Everyone

> *"I have always felt, deep down, I know what to build but I can't see it.*
> *Now I can see it.*
> *Ex-OS is the thing I've been circling.*
> *Thank you for pointing."*

---

*Ex-OS: Your thoughts, staying yours, everywhere, verified, audited, and trusted.*

---

*Built by JamesTheGiblet.*
*With gratitude for all who contribute.*

*On a phone. In Termux. Around a full-time job.*
*Because the ideas didn't stop.*
