# 🔄 Feedback Loop System

> Every product gets 1% better every week. Compounding over 52 weeks = 68% improvement. Over a year with consistent iteration, each product becomes unrecognizably better.

---

## What This Is

A continuous improvement system that automatically collects performance data from all of Wolfgang's products and agents, identifies what's working and what isn't, and queues (or applies) specific fixes. It runs every Friday, takes ~2 minutes, and generates a plain-English summary.

The philosophy: **data → diagnosis → prescription → application → measurement → repeat.**

---

## How It Works (Plain English)

### Step 1: Collect (`feedback-tracker.py`)

Every Friday, the system pulls data from four sources:

| Source | What it collects |
|--------|-----------------|
| **Vapi (cold calls)** | Call duration, hangup rate, warm conversation rate, booking signals |
| **Email outreach** | Reply rates per subject line, reply rates per business type |
| **Stripe** | Active subscribers, MRR, churn, refund requests |
| **GitHub Issues** | Bug reports, UX friction complaints, feature requests, hot issues |

This data is saved as a dated JSON snapshot in `weekly-snapshots/YYYY-MM-DD.json`.
Over time, these snapshots become a performance history you can trend.

---

### Step 2: Analyze (`improvement-engine.py`)

The engine reads the latest snapshot and applies specific rules to generate tasks:

**For Scribe (call scripts):**
- Hangup rate > 30% → "Rewrite the opener"
- Interest rate < 5% → "Fix the close sequence"
- Warm calls > 15% → "Mine transcripts for what's working"

**For Quill (email outreach):**
- Subject line with 0 replies after 50 sends → "Kill it"
- One subject line 2x better than another → "Retire the loser, go all-in on the winner"
- Business type never replies → "Remove from targeting"

**For Pixel (landing pages / UX):**
- High churn → "Onboarding flow is broken — simplify it"
- Hot GitHub UX issues → "Priority fix with user-facing impact"
- Multiple UX friction reports → "Do a walkthrough, map pain points"

**For Spark (growth / campaigns):**
- MRR below target → "Run a limited-time offer"
- MRR declining week-over-week → "Win-back campaign for lapsed users"

Tasks are written to `improvement-queue.md` in a clean, actionable format:
```
🔴 [HIGH] SCRIBE TASK: Rewrite Alex's opener — 34% hangup in first 30s.
  Current: "Hey this is Alex..."
  Suggested fix: Lead with a specific local pain point...
```

---

### Step 3: Auto-Apply (`auto-apply.py`)

Some improvements are safe to apply automatically (no QA needed):

| What | Auto-applied? | Why |
|------|--------------|-----|
| Retire dead email subject lines | ✅ Yes | Pure data — 0 replies = dead |
| Promote winning subject line (2x+ better) | ✅ Yes | Clear winner, no risk |
| Remove zero-reply business types from targeting | ✅ Yes | Data-driven, reversible |
| Rewrite call scripts | 🚩 Flag only | Scripts need human QA |
| Change landing page copy | 🚩 Flag only | Brand/design decisions |
| Modify pricing | 🚩 Flag only | High-impact, needs judgment |

Auto-applied changes are logged to `auto-apply-log.json` with timestamps and before/after details. Every change is reversible (`.bak` files are created).

---

### Step 4: Report

After every run, a plain-English summary is saved to `latest-summary.txt` and sent to Wolfgang on Telegram:

```
🔄 Weekly Feedback Loop Report

✅ 3 improvements queued, 1 auto-applied
📞 Calls: 47 total | 28% hangup (↓6pp vs last week) | 8% interest
💰 Stripe: 8 subs | $112/mo MRR
🚩 2 items flagged for your review

Full task queue in improvement-queue.md
```

---

## File Structure

```
feedback-loop/
├── README.md                    ← You are here
├── feedback-tracker.py          ← Data collection (Vapi, email, Stripe, GitHub)
├── improvement-engine.py        ← Analysis → recommendations
├── auto-apply.py                ← Apply safe changes automatically
├── improvement-queue.md         ← Current task list (auto-generated Fridays)
├── improvement-history.json     ← History of all improvement runs
├── auto-apply-log.json          ← Log of every auto-applied change
├── latest-summary.txt           ← This week's summary (sent to Wolfgang)
└── weekly-snapshots/
    ├── 2026-03-07.json          ← First snapshot (after running)
    ├── 2026-03-14.json
    └── ...
```

---

## Data Sources: What's Live vs What Needs Vapi

### ✅ Live Now
| Source | Status | Notes |
|--------|--------|-------|
| **Stripe** | Live | Uses existing live key from HEARTBEAT.md |
| **GitHub Issues** | Live | honest-eats + unitfix-simple-maintenance |
| **Email outreach** | Live (if email-log.json exists) | Needs email-log.json with sent/replied tracking |

### ⏳ Needs Vapi Active First
| Source | Status | What to do |
|--------|--------|-----------|
| **Vapi calls** | Waiting for Vapi to go live | Once Vapi is active, `feedback-tracker.py` auto-detects and starts pulling data. No config changes needed. |
| **Email log** | Needs setup | Add logging to the outreach scripts. Each email send should append `{"subject": "...", "business_type": "...", "sent": true, "replied": false}` to `assets/email-log.json`. Reply tracking can be added later. |

---

## Running It Manually

```bash
# Full weekly run
python3 /root/.openclaw/workspace/feedback-loop/feedback-tracker.py
python3 /root/.openclaw/workspace/feedback-loop/improvement-engine.py
python3 /root/.openclaw/workspace/feedback-loop/auto-apply.py

# Just collect data
python3 feedback-tracker.py

# Just generate recommendations (from existing snapshot)
python3 improvement-engine.py

# Just apply safe changes
python3 auto-apply.py
```

---

## The Compounding Effect

The goal isn't to make one big change. It's to make 52 small improvements per year, each building on the last.

| Week | Hangup Rate | Email Reply Rate | MRR |
|------|-------------|-----------------|-----|
| 1    | 42%         | 1.2%            | $98 |
| 4    | 35%         | 1.8%            | $140|
| 12   | 24%         | 2.9%            | $285|
| 26   | 15%         | 4.1%            | $580|

The numbers above are illustrative, but the mechanism is real: each week's data informs next week's improvement. The feedback loop compounds.

---

## Agent Routing

| Agent | Gets tasks about |
|-------|-----------------|
| **Scribe** | Cold call scripts, openers, objection handlers, close sequences |
| **Quill** | Email subject lines, targeting, follow-up sequences |
| **Pixel** | Landing pages, onboarding flows, UX friction, visual design |
| **Spark** | Growth campaigns, promotions, win-back offers |
| **GENERAL** | Bugs, refunds, infrastructure, things that don't fit neatly |

---

## Adding New Data Sources

To plug in a new data source (e.g. website analytics, ad performance):

1. Add a `collect_yourdata()` function to `feedback-tracker.py`
2. Call it in the `run()` function and add to the snapshot dict
3. Add a `analyze_yourdata()` function to `improvement-engine.py`
4. Done. The rest of the pipeline handles it automatically.

---

*Built for Wolfgang Meyer's product ecosystem. Runs every Friday via HEARTBEAT.md.*
