# Debate Duel — GenLayer Intelligent Contract Game

> **Two players. One AI-generated topic. An on-chain LLM judge that reads your arguments and delivers a tamper-proof verdict.**

Live: [https://genlayer-debate-duel.vercel.app](https://genlayer-debate-duel.vercel.app)

---

## Overview

Debate Duel is a two-player battle game built on GenLayer — the first blockchain that supports **Intelligent Contracts**: smart contracts capable of accessing the internet, running large language models, and processing natural language, all with decentralized consensus guarantees.

Each match works as follows:

1. A fresh debate topic is generated on-chain by an LLM (never the same topic twice)
2. Players are assigned opposing sides — FOR or AGAINST the proposition
3. Each player writes their argument independently under a countdown timer
4. The AI judge evaluates both arguments on three axes: **Logic**, **Evidence**, and **Persuasion**
5. Scores and the full verdict reasoning are written permanently to the GenLayer blockchain
6. Best of 3 rounds wins the match

No human moderator. No rigged outcomes. The judge is an LLM running inside GenLayer's consensus protocol — its verdict is as tamper-proof as any on-chain transaction.

---

## What Makes This Different

Most blockchain games use randomness or simple state machines. Debate Duel uses **natural language reasoning** as the core game mechanic. The LLM doesn't just pick a winner — it scores each argument independently across three separate dimensions, then writes a 2–3 sentence explanation of its reasoning. That reasoning is stored on-chain.

This is only possible on GenLayer. No other blockchain can run LLM inference inside a smart contract with consensus guarantees.

---

## Contracts

Three separate contracts power the game, each with a distinct responsibility:

| Contract | Address | Role |
|---|---|---|
| `debate_duel.py` | `0xce04C5f27Cb1DBfF46044f8Fd871A9F9e5418e4d` | Game logic — topic generation, argument judging, match flow |
| `debate_duel_storage.py` | `0xebe33979c7ac0C5131f6F9f1E15540B009ECb01F` | Match and round data storage |
| `debate_duel_stat.py` | `0xfc9A7445868B0Af0a80f80C352C0EbAf77193fAF` | Player statistics — wins, losses, streaks, per-axis scores |

### debate_duel.py

The core game contract. Handles two write functions:

- `create_match(player_a, player_b, match_id, created_at)` — calls the LLM to generate a fresh debate topic with FOR/AGAINST positions, saves the match to the storage contract
- `submit_arguments(match_id, round_num, arg_a, arg_b)` — calls the LLM to judge both arguments, saves the round result to storage, updates match scores, and records player stats on match completion

Both LLM calls use `gl.eq_principle.strict_eq` to ensure all GenLayer validator nodes reach consensus on the AI output before it is written on-chain.

### debate_duel_storage.py

Dedicated storage contract using `Match` and `DebateRound` dataclasses. Stores 11 score fields per round (logic, evidence, persuasion per player, totals, winner, judgment text). Supports match update-in-place for score progression across rounds. Provides `get_recent_matches` sorted by creation timestamp.

### debate_duel_stat.py

Player statistics tracker. Stores a `DebaterProfile` per wallet address with: match wins/losses/draws, win streak, best streak, cumulative per-axis scores, win rate percentage, and average score per round. Leaderboard sorts by wins then rounds won. Players can set a nickname via `set_nickname`.

---

## LLM Contract Logic

### Topic Generation

The LLM is prompted to generate a thought-provoking debate topic from safe categories: technology ethics, environment, education policy, social media, science, space exploration, AI regulation, urban planning, food systems, privacy, and healthcare access.

Hard-filtered categories (never generated): gambling, alcohol, drugs, interest-based finance, sexual content, religious controversy, partisan political figures by name, violence glorification.

The LLM returns a JSON object with the topic and both sides' positions.

### Judgment

The LLM receives both arguments with their assigned positions and scores each independently:

- **Logic (0–10)**: Is the reasoning sound? Does the conclusion follow from the premises?
- **Evidence (0–10)**: Are claims supported by facts, examples, analogies, or real-world references?
- **Persuasion (0–10)**: Is the argument clear, structured, and compelling?

Total score = Logic + Evidence + Persuasion (max 30). Higher total wins the round. Ties are draws. The LLM also writes a 2–3 sentence judgment explaining the verdict — this is stored on-chain alongside the scores.

---

## Game Flow

```
Setup Screen
  └─ Enter player names → Generate Topic (on-chain LLM call)
       └─ Round 1: Player A writes argument (90 sec timer)
            └─ Player B writes argument (90 sec timer)
                 └─ Arguments submitted on-chain
                      └─ LLM judges → Verdict displayed
                           └─ Round 2 (if needed)
                                └─ Round 3 (if needed)
                                     └─ Match Over → Winner declared
```

Match ends when a player reaches 2 round wins, or after round 3 (whichever comes first).

---

## Repository Structure

```
genlayer-debate-duel/
├── public/
│   ├── index.html          # Landing page — game info + GenLayer explanation
│   └── game.html           # Game interface — full match flow
├── contracts/
│   ├── debate_duel.py          # Main game logic contract
│   ├── debate_duel_storage.py  # Match + round data storage
│   └── debate_duel_stat.py     # Player statistics + leaderboard
├── docs/
│   └── deployment.md       # Deployment guide
└── README.md
```

---

## Tech Stack

- **Smart Contracts**: GenLayer Intelligent Contracts (Python)
- **Frontend**: Vanilla HTML/CSS/JS — no framework dependencies
- **Fonts**: Playfair Display, DM Mono, Crimson Pro (Google Fonts)
- **Deployment**: Vercel (static)
- **Chain**: GenLayer Testnet

---

## Design Decisions

**Why three contracts?**
Separating game logic, storage, and statistics makes each contract independently auditable and upgradeable. The storage contract can be queried directly by any external tool. The stat contract is a standalone leaderboard that could serve multiple games.

**Why no token rewards?**
Debate Duel is a pure skill game. Points are bragging rights, not financial instruments. No staking, no entry fees, no economic incentives that could create perverse game dynamics.

**Why best of 3?**
One-round games are too volatile — a single strong argument shouldn't be decisive. Three rounds reward consistent reasoning and allow comeback mechanics, making matches more engaging.

**Why 90 seconds?**
Long enough to write a structured argument, short enough to prevent copy-pasting from external tools. The time pressure forces players to think and write — not search.

---

## Running Locally

No build step required. Open `public/index.html` in a browser, or serve the `public/` directory:

```bash
cd public
python3 -m http.server 8080
# open http://localhost:8080
```

Or with Node:

```bash
npx serve public
```

---

## Deployment

See [docs/deployment.md](docs/deployment.md) for full contract deployment and Vercel deployment instructions.

---

## License

MIT
