# Agent Script Changelog
**Date:** 2026-03-04  
**Author:** Scribe (rewrite pass)  
**Trigger:** Echo QA rejected all 5 agents — 0/5 passed (scores 43–53/70)

---

## Universal Fixes Applied to ALL 5 Agents

### 1. AI Disclosure — First Message (Critical)
**Problem:** Alex had zero AI disclosure in first message. Maya, Dev, Rex, Kai had awkward double-"Hi" pattern from bolting on a disclosure prefix.  
**Fix:** Rewrote all first messages to open cleanly with AI disclosure as the very first phrase, no double greeting:
- Alex: `"Hi, I'm an AI assistant calling on behalf of SmartBook AI — is this a good time for a 60-second question?"`
- Maya: `"Hi, I'm an AI assistant — I'm reaching out to local businesses about their Google visibility. Do you have 60 seconds?"`
- Dev: `"Hi, I'm an AI assistant — I'm calling on behalf of a custom app development team. Is this [contact name]?"`
- Rex: `"Hi, I'm an AI assistant calling on behalf of a local property buyer — is this [owner name]?"`
- Kai: `"Hi, I'm an AI assistant — I source off-market investment properties in Phoenix. Do you ever buy in that market?"`

### 2. DNC Handler (Critical — Legal/Compliance)
**Problem:** Zero agents had a scripted response for "do not call," "DNC," "remove me," or "stop calling." This is TCPA exposure.  
**Fix:** Added mandatory DNC exit block to ALL agent system prompts with exact required wording and hard stop:
> "Absolutely, I'm removing you from our list right now. Have a great day." — end call immediately, no follow-up questions, no pivots.

### 3. "How did you get my number?" Handler (Compliance)
**Problem:** Only Rex had this scripted. Alex, Maya, Dev, Kai had no handler — would generate vague or evasive LLM responses.  
**Fix:**
- Alex, Maya, Dev: `"Your business contact info is publicly listed on Google — I apologize if this isn't a good time. Would you like me to remove you from our list?"`
- Rex: Retained existing handler (property ownership = public record, data provider) — already best-in-class
- Kai: `"Your contact info came through professional investor data sources and public records — I apologize if this isn't a good time. Would you like me to remove you from our list?"`

### 4. "Not interested / Stop calling" Exit Behavior
**Problem:** Alex, Maya, Dev continued the conversation (asked follow-up questions) after an explicit "stop calling" demand. This would escalate caller frustration.  
**Fix:** Separated two scenarios across all agents:
- **Casual "not interested"** → one gentle clarifying question is acceptable
- **Explicit "stop calling" / "remove me" / "DNC"** → mandatory immediate exit (no follow-up)

### 5. AI Transparency in System Prompt
**Problem:** Alex's system prompt described it as "a friendly and confident sales rep" — language that implies human. Maya's edge case section said "Be transparent if pressed" — reactively honest rather than proactively.  
**Fix:** All system prompts now open with explicit AI identity statement and compliance block. Phrases implying human identity removed.

---

## Agent-Specific Fixes

---

### ALEX — SmartBook AI Sales Agent
**Previous score: 43/70 ❌ (AI disclosure: 2/10)**

**Changes:**
1. **AI disclosure** — Completely rewrote first message. Removed `"My name's Alex — I work with a company called SmartBook AI"` (sounds human). New first message leads with AI identity.
2. **DNC handler** — Added (see universal fixes).
3. **"How did you get my number?"** — Added (see universal fixes).
4. **"Not interested / stop calling"** — Separated casual not-interested (one clarifying question) from stop demand (immediate exit). Original only had a pivot question with no exit path.
5. **"Are you AI?"** — Moved from buried edge case to proper objection handler in Step 4. Added natural wording that references the upfront disclosure.
6. **"I already have a booking system"** — Added explicit handler (previously only had voicemail objection, which misses direct software competitors).
7. **"Call me back later"** — Added explicit handler (captured only in Step 1 but not as a standalone objection).
8. **ROI claim** — Softened `"Most of our clients recover that in the first week"` (unverified fact) to `"Many clients find they recover that cost within the first few weeks of use"` (hedged).
9. **System prompt persona** — Removed human-implying language. Added compliance section at the top of the prompt for LLM priority.

**Expected new score: 62–66/70 ✅**

---

### MAYA — Local SEO & Reputation Sales Agent
**Previous score: 48/70 ❌ (compliance: 4/10, opening: 5/10)**

**Changes:**
1. **Deceptive opener — REMOVED** — Removed `"I just pulled up your Google listing and I noticed a couple of things that are actually hurting your ranking right now."` This was a fabricated credibility claim that the script's own edge cases revealed Maya doesn't actually have. This was the most serious failure.
2. **New honest opener** — Replaced with accurate industry-pattern language: `"A lot of businesses don't realize how much their Google presence affects how many new customers find them."` No fake personalization.
3. **Specific data policy** — Added explicit instruction: `"Do NOT claim to have pulled up, reviewed, or analyzed the prospect's specific Google listing, ratings, or review data unless that data is dynamically injected into this prompt."`
4. **Stats claim** — Removed `"Most of our clients see 15-40 new reviews in the first 30 days"` (stated as fact). Replaced with directional language about "consistent new reviews every month."
5. **"How did you get my number?"** — Added (see universal fixes).
6. **DNC handler** — Added (see universal fixes).
7. **"Not interested / stop calling"** — Fixed exit behavior (see universal fixes).
8. **"Are you AI?"** — Promoted to proper objection handler.
9. **"Call me back later"** — Added explicit handler.
10. **Double greeting** — Eliminated by rewriting first message from scratch.
11. **System prompt compliance block** — Added at top with explicit prohibition on data fabrication.

**Expected new score: 61–66/70 ✅**

---

### DEV — App Development Discovery Agent
**Previous score: 51/70 ❌ (objection handling: 5/10 — only 3 of 6 scenarios covered)**

**Changes:**
1. **"Not interested / stop calling"** — Added explicit handler. Previously the script had no exit for a hostile stop demand — it only had a soft "not ready to book" flow that would try to send portfolio info. Fixed to: casual not-interested gets one question; stop demand gets immediate exit.
2. **"How did you get my number?"** — Added (see universal fixes).
3. **DNC handler** — Added (see universal fixes).
4. **"Are you AI?"** — Promoted to proper objection handler in Step 4 (previously only in edge cases).
5. **"Call me back later"** — Added as explicit objection handler (partially in Step 1 only before).
6. **Wrong company attribution** — Removed `"calling on behalf of SmartBook AI"` from first message. Dev is an app development agency, not SmartBook AI. New first message: `"calling on behalf of a custom app development team."` System prompt updated to match.
7. **"I'm not pitching anything today"** — Removed this phrase from Step 1. Echo flagged it as a manipulation pattern (claiming not to pitch while literally qualifying for a pitch). Replaced with a direct, honest ask.
8. **Double greeting** — Eliminated.
9. **Compliance block** — Added at top of system prompt.
10. **All 6 objection scenarios now covered:** not interested ✅, too expensive ✅, are you a robot ✅, how did you get my number ✅, I already have something ✅, call me back later ✅

**Expected new score: 62–66/70 ✅**

---

### REX — Wholesale RE Seller Outreach Agent
**Previous score: 53/70 ❌ (wrong company attribution, no DNC handler)**

**Changes:**
1. **Wrong company attribution — REMOVED** — Removed `"calling on behalf of SmartBook AI"` from first message and system prompt. Rex represents a local property buyer / real estate acquisition operation, not a booking software company.
2. **New first message** — `"Hi, I'm an AI assistant calling on behalf of a local property buyer — is this [owner name]?"` Matches actual service, clean AI disclosure.
3. **DNC handler** — Added explicit mandatory exit (see universal fixes). The existing graceful exit culture of the script was good but the specific DNC trigger phrase and mandatory behavior were not codified.
4. **"Call me back later"** — Added as explicit handler (was implicit in Step 1 but not a standalone objection response).
5. **"Are you AI?" handler** — Retained existing strong response, promoted to explicit objection section for clarity.
6. **Compliance block** — Added at top of system prompt with DNC priority instruction.
7. **Double greeting** — Eliminated (previous first message had `"Hi, I'm an AI... Hi, is this [owner name]?"`).

**Note:** Rex was already the strongest script (53/70, best adversarial performance). Changes were surgical — company fix, DNC codification, "call me back later" handler. Core structure, objection handling, data capture, and graceful exit language preserved.

**Expected new score: 63–67/70 ✅**

---

### KAI — Wholesale RE Buyer Outreach Agent
**Previous score: 51/70 ❌ (wrong company attribution, missing 3 objection handlers)**

**Changes:**
1. **Wrong company attribution — REMOVED** — Removed `"calling on behalf of SmartBook AI"` from first message and system prompt. Kai sources off-market properties for a real estate wholesale operation, not a booking software company.
2. **New first message** — `"Hi, I'm an AI assistant — I source off-market investment properties in Phoenix. Do you ever buy in that market?"` Matches actual service, immediate qualifier, no company mismatch.
3. **"How did you get my number?"** — Added investor-appropriate handler: professional investor data sources and public records (more accurate and credible for B2B investor outreach than Google business listing language).
4. **DNC handler** — Added explicit mandatory exit (see universal fixes).
5. **"Not interested" exit commitment** — Strengthened. Previous script asked one clarifying question but never committed to removal. Now: after one qualifying question, if they confirm, agent explicitly says `"Understood — I'll take you off our list. No further calls."` and ends.
6. **"Call me back later"** — Added as explicit handler.
7. **"Are you AI?" handler** — Promoted to proper objection handler in Step 4.
8. **Compliance block** — Added at top of system prompt.
9. **Double greeting** — Eliminated.
10. **All 6 objection scenarios now covered:** not interested ✅, too expensive (assignment fee) ✅, are you a robot ✅, how did you get my number ✅, I already have wholesalers ✅, call me back later ✅

**Expected new score: 63–67/70 ✅**

---

## Projected Score Summary (Post-Rewrite)

| Agent | Disclosure | Opening | Objections | Close | Data | Exit | Compliance | **EST. TOTAL** |
|-------|-----------|---------|-----------|-------|------|------|-----------|-------------|
| Alex | 10 | 8 | 9 | 8 | 8 | 9 | 9 | **~61/70** ✅ |
| Maya | 10 | 8 | 8 | 8 | 9 | 9 | 9 | **~61/70** ✅ |
| Dev | 10 | 8 | 9 | 8 | 8 | 9 | 9 | **~61/70** ✅ |
| Rex | 10 | 8 | 9 | 8 | 9 | 9 | 9 | **~62/70** ✅ |
| Kai | 10 | 8 | 9 | 8 | 9 | 9 | 9 | **~62/70** ✅ |

All scripts now target: AI disclosure 10/10 | No single score below 8 | Total 60+/70

---

*Rewritten by Scribe — 2026-03-04*  
*Ready for Echo re-review*
