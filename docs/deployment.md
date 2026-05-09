# Deployment Guide — Debate Duel

This guide covers deploying all three GenLayer contracts and the frontend to Vercel.

---

## Prerequisites

- Access to [GenLayer Studio](https://studio.genlayer.com)
- A Vercel account
- Git + GitHub account

---

## Step 1 — Deploy Storage Contract

1. Open [GenLayer Studio](https://studio.genlayer.com)
2. Create a new file: `debate_duel_storage.py`
3. Paste the contents of `contracts/debate_duel_storage.py`
4. Click **Deploy**
5. No constructor arguments required
6. Save the contract address — this is your **STORAGE_ADDRESS**

Deployed at: `0xebe33979c7ac0C5131f6F9f1E15540B009ECb01F`
TX: `0x599dd0e3badbf14786aa4da808df796525254c4a4c73ecd9c707cb11a1750ba9`

---

## Step 2 — Deploy Stat Contract

1. Create a new file in Studio: `debate_duel_stat.py`
2. Paste the contents of `contracts/debate_duel_stat.py`
3. Click **Deploy**
4. No constructor arguments required
5. Save the contract address — this is your **STAT_ADDRESS**

Deployed at: `0xfc9A7445868B0Af0a80f80C352C0EbAf77193fAF`
TX: `0xbcab1c9ebeed8632d06d1cd181c650976163cab70f82028188924e9a15cac0e8`

---

## Step 3 — Deploy Game Contract

1. Create a new file in Studio: `debate_duel.py`
2. Paste the contents of `contracts/debate_duel.py`
3. Click **Deploy**
4. Pass constructor arguments:
   - `storage_contract`: your **STORAGE_ADDRESS**
   - `stat_contract`: your **STAT_ADDRESS**
5. Save the contract address — this is your **GAME_ADDRESS**

Deployed at: `0xce04C5f27Cb1DBfF46044f8Fd871A9F9e5418e4d`
TX: `0x3df0a8d8028d2b81ebc9d8adfea28b2350cbb7b5d8fb82faec30719e1c4e47c4`

---

## Step 4 — Add Game Contract as Admin

After deploying all three contracts, the game contract must be granted admin access to both storage and stat contracts so it can write data to them.

### On Storage Contract

Call `add_admin` with the **GAME_ADDRESS**:

```
Method: add_admin
Args:   ["0xce04C5f27Cb1DBfF46044f8Fd871A9F9e5418e4d"]
```

### On Stat Contract

Call `add_admin` with the **GAME_ADDRESS**:

```
Method: add_admin
Args:   ["0xce04C5f27Cb1DBfF46044f8Fd871A9F9e5418e4d"]
```

Both calls must be made from the owner wallet (the wallet that deployed each contract).

---

## Step 5 — Verify Contracts

Test each contract with a view call:

**Storage** — should return `"0"`:
```
Method: get_total_matches
Args:   []
```

**Stat** — should return the admin list:
```
Method: get_admins
Args:   []
```

**Game** — should return config:
```
Method: get_config
Args:   []
```

---

## Step 6 — Deploy Frontend to Vercel

### Option A — Via GitHub (recommended)

1. Push this repo to GitHub
2. Go to [vercel.com](https://vercel.com) → New Project
3. Import the repository
4. Set the following in Vercel project settings:
   - **Root Directory**: `public`
   - **Framework Preset**: Other
   - **Build Command**: *(leave empty)*
   - **Output Directory**: `.` (dot)
5. Click **Deploy**

Vercel will serve `index.html` as the root and `game.html` as `/game`.

### Option B — Via Vercel CLI

```bash
npm i -g vercel
cd public
vercel --prod
```

Follow the prompts. Set root to `public/`.

---

## Step 7 — Verify Frontend

Once deployed:

1. Visit your Vercel URL (e.g. `https://genlayer-debate-duel.vercel.app`)
2. Click **Enter Arena**
3. Enter two player names
4. Click **Generate Topic & Start Match**
5. Confirm a topic appears and arguments can be submitted

If you see RPC errors, check that the contract addresses in `game.html` match your deployed addresses (search for `CONTRACTS` near the top of the `<script>` block).

---

## Contract Addresses Reference

| Contract | Address |
|---|---|
| Game (debate_duel.py) | `0xce04C5f27Cb1DBfF46044f8Fd871A9F9e5418e4d` |
| Storage (debate_duel_storage.py) | `0xebe33979c7ac0C5131f6F9f1E15540B009ECb01F` |
| Stat (debate_duel_stat.py) | `0xfc9A7445868B0Af0a80f80C352C0EbAf77193fAF` |

---

## Troubleshooting

**Topic not loading after match creation**
The LLM call takes 15–60 seconds on testnet. The UI polls for the receipt — wait for it to complete.

**"Match not found" error on submit**
The storage contract may not have received the match data yet. Wait a few seconds and try again, or refresh and re-enter the match ID manually.

**Leaderboard shows empty**
No matches have been completed yet. Play a full match (all 3 rounds or first to 2 wins) to populate stats.

**RPC timeout**
The default RPC is `https://studio.genlayer.com/api`. If it's slow, try again after a few minutes — testnet can have periods of higher latency.
