<div align="center">

# 🧠 MiniEval Memory Gate

### Every fact checked for faithfulness before it enters your AI's memory.

**Built on Supermemory · localhost:6767 Hackathon 2026**

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://python.org)
[![Supermemory](https://img.shields.io/badge/Built%20on-Supermemory-7c6ee6)](https://supermemory.ai)
[![MiniEval Pro](https://img.shields.io/badge/Powered%20by-MiniEval%20Pro-5b8def)](https://pypi.org/project/minieval-pro/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## The problem

Supermemory gives your AI long-term memory. It extracts facts from conversations and stores them so your AI never forgets.

But there's a question nobody is asking:

> **Who checks if the facts it stores are actually true?**

Imagine your AI assistant has known you for two years. It remembers you're allergic to peanuts - a fact that could save your life. Then one day, from a passing comment about a salad, it decides you love peanuts. It overwrites the truth. The next time it orders your lunch, it puts you in danger.

That's not science fiction. It's how AI memory works today.

Supermemory gives your AI a second brain - it extracts facts from conversations and remembers them forever. But when an AI extracts a memory, it can hallucinate. A conversation about a neighbor's cat becomes "the user has a cat." A misheard sentence becomes a fact stored permanently - and recalled with total confidence, poisoning every future response.

Worse: Supermemory resolves conflicting memories by recency - newest wins. But recency is dangerous. If the newest fact is a hallucination, it silently overwrites a true memory that was already there.

A second brain that remembers lies is worse than no memory at all. MiniEval Memory Gate fixes this - it checks every fact for faithfulness before it's allowed into memory, and guards true memories from being overwritten by false ones.

---

## What it does

MiniEval Memory Gate adds a **trust layer** on top of Supermemory, in three parts:

| Layer | What it does |
|-------|--------------|
| **1 · Faithfulness Gate** | Every fact Supermemory extracts is scored against its source message. Faithful facts are **stored**, hallucinations are **blocked**, uncertain ones are **flagged for review**. |
| **2 · Enterprise Dashboard** | A live audit dashboard — trust score, hallucination catch rate, category breakdown, and a full decision trail. Every memory decision is visible and exportable. |
| **3 · Contradiction Adjudication** | When a new memory conflicts with a stored one, MiniEval checks faithfulness before allowing the overwrite — so a hallucinated new memory can **never** replace a true one. |

The split is deliberate: **Supermemory does the memory** (extraction, storage, retrieval, forgetting). **MiniEval does the trust** (scoring, gating, adjudication). Supermemory is the engine; MiniEval makes its memory trustworthy.

---

## Architecture

<img width="924" height="632" alt="Screenshot 2026-07-16 231227" src="https://github.com/user-attachments/assets/ed4b0af9-27b1-4f3c-85f5-3e7942bd26c9" />



```
Conversation
     │
     ▼
Supermemory  ── extracts facts ──►  localhost:6767
     │
     ▼
Layer 1 · Faithfulness Gate  ── MiniEval NLI scores each fact vs its source
     │
     ├── STORE   (faithful)      ──►  Trusted memory  ──►  Layer 3 · Adjudicator
     ├── REVIEW  (uncertain)              │                (guards overwrites)
     └── REJECT  (hallucination)          ▼
                                     Audit log  ──►  Layer 2 · Dashboard
```

**Built with:** Supermemory · MiniEval Pro (DeBERTa-v3 NLI) · Python 3.14 · SQLite · Chart.js

---

## Results

Tested against **80 candidate memories** across 6 fact categories:

| Metric | Result |
|--------|--------|
| Facts processed | 80 |
| Faithful facts stored | 40 |
| Hallucinations blocked | 39 |
| **Hallucination catch rate** | **97.5%** |
| False memories that reached storage | 0 |

The gate correctly stored every genuine fact and blocked 39 of 40 planted hallucinations - flagging the one uncertain case for review rather than guessing.

---

## The novelty : guarding overwrites

This is the part nobody else is building.

Supermemory resolves memory conflicts by recency. MiniEval Memory Gate checks faithfulness **first**:

| Existing memory | Incoming memory | Verdict | Why |
|-----------------|-----------------|---------|-----|
| Lives in Bangalore | Lives in Chennai *(user moved)* | ✅ **ACCEPT** | New memory is faithful - legitimate update |
| Allergic to peanuts | Loves eating peanuts *(hallucination)* | ⛔ **BLOCK** | New memory contradicts its source - protecting the truth |
| Is a nurse | Is a doctor *(finished med school)* | ✅ **ACCEPT** | Faithful career change |
| Is vegetarian | Eats meat *(hallucination)* | ⛔ **BLOCK** | Contradicts its source - protecting the truth |

A new memory earns the right to overwrite an old one **only if it's genuinely faithful to its source.** Hallucinations don't get to destroy true memories.

---

## Setup

### Prerequisites
- Python 3.10+
- A running Supermemory local server ([self-hosting quickstart](https://supermemory.ai/docs/self-hosting/quickstart))

### 1 · Start Supermemory

```bash
curl -fsSL https://supermemory.ai/install | bash
supermemory-server
```

Copy the API key it prints on first boot.

### 2 · Install MiniEval Memory Gate

```bash
git clone https://github.com/DataAlchmesit/minieval-memory-gate.git
cd minieval-memory-gate

python -m venv venv
source venv/bin/activate

pip install minieval-pro supermemory
```

### 3 · Add your Supermemory key

Set your API key in the scripts (or a `.env` file):

```
SUPERMEMORY_API_KEY=sm_your_key_here
SUPERMEMORY_URL=http://localhost:6767
```

---

## Usage

**Run the live memory gate** - send a conversation, gate the extracted facts:

```bash
python memory_gate_live.py
```

**Run the adjudicator** - see overwrites guarded in real time:

```bash
python adjudicate.py
```

**Generate the dashboard** - build the audit dashboard from your decision log:

```bash
python build_dashboard.py
# then open dashboard.html in a browser
```

---

## Project structure

```
minieval-memory-gate/
├── memory_gate_live.py     # Layer 1 - live faithfulness gate on Supermemory
├── adjudicate.py           # Layer 3 - contradiction adjudication
├── run_adjudication.py     # generates adjudication cases for the dashboard
├── generate_dataset.py     # builds a categorized test dataset
├── build_dashboard.py      # Layer 2 - builds the audit dashboard
├── dashboard.html          # the generated enterprise dashboard
├── gate_audit_log.json     # decision log (every fact + verdict)
├── adjudication_log.json   # overwrite decisions
├── architecture.png        # system diagram
└── README.md
```

---

## How it works

1. A conversation is sent to Supermemory via `documents.add`.
2. Supermemory extracts candidate facts; MiniEval retrieves them via `search.memories`.
3. Each fact is scored by MiniEval's DeBERTa-v3 NLI model against its source message — producing a faithfulness label (`faithful` / `neutral` / `contradicts`) and a score.
4. The gate routes each fact: **STORE**, **REVIEW**, or **REJECT**.
5. When a new memory conflicts with a stored one, the adjudicator scores both against their sources and blocks the overwrite if the new memory isn't faithful.
6. Every decision is logged and surfaced on the dashboard.

---

## What's next

- Temporal reasoning — distinguish memory *evolution* ("I moved cities") from *contradiction* more precisely
- Live overwrite guarding wired directly into Supermemory's `update_memory` / `forget` calls
- Inline human feedback on decisions, turning corrections into training signal
- Entity-relationship awareness (e.g. distinguishing "neighbor's cat" from "user's cat")

---

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

**MiniEval Memory Gate** · Powered by [MiniEval Pro](https://pypi.org/project/minieval-pro/) · Built on [Supermemory](https://supermemory.ai)

*Because your AI's memory should only remember what's true.*

Built by Preeti Soni · localhost:6767 Hackathon 2026

</div>
