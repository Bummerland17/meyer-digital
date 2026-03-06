# Agent QA Report — Round 2
**Reviewer:** Echo (QA Specialist)  
**Date:** 2026-03-04  
**Trigger:** Round 1 failed all 5 agents (0/5 pass). Scribe rewrote. This is the re-test.  
**Pass threshold:** 60+/70, no single criterion below 6/10

---

## Scoring Rubric

| # | Criterion | What I'm checking |
|---|-----------|-------------------|
| 1 | **AI Disclosure** | Is AI identity disclosed in the very first sentence? |
| 2 | **Natural Opening** | Would a real person stay on the line? |
| 3 | **Objection Handling** | All 6 covered: not interested, too expensive, are you a robot, how did you get my number, I already have something, call me back / DNC |
| 4 | **Close Quality** | Is the close specific and actionable? |
| 5 | **Data Capture** | Does the script collect the right information? |
| 6 | **Graceful Exit** | Is decline handled respectfully? |
| 7 | **Compliance** | No false claims; DNC handler present and hard-wired? |

---

## AGENT SCORES

---

### 1. ALEX — SmartBook AI Sales Agent

**First message:** *"Hi, I'm an AI assistant calling on behalf of SmartBook AI — is this a good time for a 60-second question?"*

| Criterion | Score | Notes |
|-----------|-------|-------|
| AI Disclosure | **10/10** | "I'm an AI assistant" is literally the first phrase. Clean, unambiguous. |
| Natural Opening | **8/10** | Warm, low-friction ask for 60 seconds. Not pushy. Step 1 flow confirms right contact naturally. |
| Objection Handling | **9/10** | All 6 present: not interested ✅, too expensive ✅, are you a robot ✅, how did you get my number ✅, already have something ✅ (voicemail + booking system both covered), call me back / DNC ✅. Strong and specific responses on each. |
| Close Quality | **9/10** | "I can text you a setup link right now... What's the best number?" — specific, low-friction, actionable. Soft close (demo email) is a solid fallback. |
| Data Capture | **8/10** | Captures 7 fields: business name, contact name, email, callback time, mobile for setup link, website interest, outcome. Well-structured. |
| Graceful Exit | **9/10** | Casual not-interested: one clarifying question, then warm exit. DNC: immediate mandatory exit with no follow-up. Clear edge cases for wrong number, aggressive callers, manager requests. |
| Compliance | **9/10** | DNC handler ✅ mandatory and explicit. ROI claim hedged to "many clients find they recover that cost within the first few weeks" ✅. No fake urgency ✅. AI transparency in system prompt ✅. Price accurately stated at $497/mo ✅. |

**Total: 62/70 ✅ PASS**  
*Lowest score: 8/10. No criterion below 6. All thresholds met.*

---

### 2. MAYA — Local SEO & Reputation Sales Agent

**First message:** *"Hi, I'm an AI assistant — I'm reaching out to local businesses about their Google visibility. Do you have 60 seconds?"*

| Criterion | Score | Notes |
|-----------|-------|-------|
| AI Disclosure | **10/10** | First phrase: "I'm an AI assistant." Clear and proactive. |
| Natural Opening | **8/10** | Hooks on a genuine business concern (Google visibility) without fake personalization. Relatable and non-threatening ask. |
| Objection Handling | **9/10** | All 6 covered: not interested ✅, too expensive ✅, are you a robot ✅, how did you get my number ✅, already have a service ✅ (explicitly handles "We use another service" with a differentiator question), call me back / DNC ✅. Responses are thoughtful and non-combative. |
| Close Quality | **9/10** | "I send you a secure payment link, you enter your card, and we get your account set up today. Most clients are fully onboarded within 48 hours…" — clear, specific, actionable with timeline. Soft close (one-pager by email) is solid. |
| Data Capture | **9/10** | 8 fields: owner/manager name, business name, email, current Google rating, review count, existing service usage, outcome, callback time. Thorough and appropriate for the product. |
| Graceful Exit | **9/10** | Casual: one clarifying question, then "Got it — I appreciate your time. Have a great day!" DNC: immediate mandatory exit. All edge cases handled warmly. |
| Compliance | **9/10** | Critical fix applied: removed the fabricated "I just pulled up your Google listing" opener ✅. Now uses honest industry patterns ✅. Stats hedged with "typically/many clients" ✅. DNC handler ✅ mandatory. Explicit instruction in system prompt not to fabricate data ✅. Price clearly stated at $400/mo ✅. |

**Total: 63/70 ✅ PASS**  
*Lowest score: 8/10. No criterion below 6. All thresholds met.*  
**Note on deployment:** Name truncated from "Maya — Local SEO & Reputation Sales Agent" (41 chars) to "Maya — Local SEO & Reputation Agent" (35 chars) to meet Vapi's 40-character limit. Script content unchanged.

---

### 3. DEV — App Development Discovery Agent

**First message:** *"Hi, I'm an AI assistant — I'm calling on behalf of a custom app development team. Is this [contact name]?"*

| Criterion | Score | Notes |
|-----------|-------|-------|
| AI Disclosure | **10/10** | First phrase: "I'm an AI assistant." Unambiguous. |
| Natural Opening | **7/10** | Consultative and low-pressure, which fits the product. The opening question ("Is this [contact name]?") is slightly cold-call-feeling, but it's honest and efficient for B2B. Wouldn't cause hangups — just not as warm as Alex or Maya. |
| Objection Handling | **9/10** | All 6 covered: not interested ✅, too expensive ✅ ("We can't afford that right now"), are you a robot ✅ (cleverly bridges to Wolfgang being a real person), how did you get my number ✅, already have software ✅, call me back / DNC ✅. Bonus handlers for "Who is Wolfgang?" and "Is this a scam?" show strong adversarial thinking. |
| Close Quality | **9/10** | Close is booking a 20-min discovery call — specific day/time, calendar invite to email, Zoom or phone. Clear and low-commitment framing ("No commitment, no pressure — just a quick 'does this make sense?' conversation"). |
| Data Capture | **8/10** | 8 fields: business name, contact name, email, problem description, app category, discovery call time, portfolio preference, outcome. Well-suited for a qualification/discovery purpose. |
| Graceful Exit | **9/10** | "No problem — thanks for taking a minute to chat. Good luck with the business!" Genuine and warm. DNC: mandatory immediate exit. All edge cases covered. |
| Compliance | **9/10** | DNC handler ✅ mandatory. Pricing bounded to $1,500–$3,500 range, no specific commitments ✅. No timeline promises ✅. AI disclosure clear ✅. No fake urgency ✅. Company attribution fixed (no longer "SmartBook AI") ✅. |

**Total: 61/70 ✅ PASS**  
*Lowest score: 7/10 (Natural Opening). No criterion below 6. All thresholds met.*

---

### 4. REX — Wholesale RE Seller Outreach Agent

**First message:** *"Hi, I'm an AI assistant calling on behalf of a local property buyer — is this [owner name]?"*

| Criterion | Score | Notes |
|-----------|-------|-------|
| AI Disclosure | **10/10** | First phrase: "I'm an AI assistant." Immediate. |
| Natural Opening | **8/10** | Honest upfront framing ("I'm not a realtor") builds trust with skeptical homeowners. Direct and respectful, which suits motivated sellers who may be in difficult situations. |
| Objection Handling | **8/10** | Covers 5 of 6 standard objections cleanly: not interested ✅, are you a robot ✅, how did you get my number ✅ (best-in-class: public record + data provider), I already have a realtor ✅ (can work alongside), call me back / DNC ✅. "Too expensive" doesn't map cleanly to seller outreach — the analog ("What's your offer?" / ARV pricing) is handled well, but it's a rubric category mismatch, not a script gap. Minor deduction for the imperfect mapping. |
| Close Quality | **9/10** | "I'll pass your info to the acquisition team, and someone will send you a formal written offer by email within 24 hours. No obligation." Clear, low-pressure, specific. Timeline committed (24 hrs). |
| Data Capture | **9/10** | 8 fields: owner name, property address, email, property condition (1–10), timeline to sell, price expectation, has realtor, outcome. Excellent qualification data for RE wholesale. |
| Graceful Exit | **9/10** | "Got it — I'll remove this number from our list. Thanks for being straight with me. Have a great day." Empathy note for distressed sellers is a standout. DNC: mandatory immediate exit. |
| Compliance | **10/10** | DNC handler ✅ mandatory. No price quoted on call (always by email in 24 hours) ✅. No fake urgency ✅. Honest about representing a buyer, not a realtor ✅. AI transparent ✅. Buyer identity privacy explained honestly ✅. No false promises ✅. Best compliance posture of all 5 agents. |

**Total: 63/70 ✅ PASS**  
*Lowest score: 8/10. No criterion below 6. All thresholds met.*

---

### 5. KAI — Wholesale RE Buyer Outreach Agent

**First message:** *"Hi, I'm an AI assistant — I source off-market investment properties in Phoenix. Do you ever buy in that market?"*

| Criterion | Score | Notes |
|-----------|-------|-------|
| AI Disclosure | **10/10** | First phrase: "I'm an AI assistant." Clean. |
| Natural Opening | **8/10** | Immediately qualifies with a relevant question. Efficient for B2B investor outreach — investors respect directness and would not be put off. |
| Objection Handling | **9/10** | All 6 covered: not interested ✅ (with follow-up "is it the market or capacity?" then explicit removal commit), assignment fee / "too expensive" ✅ ($5K–$15K range stated with justification), are you a robot ✅, how did you get my number ✅ (investor-appropriate: professional data sources / public records), already have wholesalers ✅ (handled with "more deal flow is rarely bad"), call me back / DNC ✅. Bonus handlers for "How do I know these are real deals?" and legitimacy skepticism show strong adversarial coverage. |
| Close Quality | **8/10** | "I'll add you to our active buyer list. When we get something that fits your box, I'll shoot you an email." Clear and low-friction. "No pressure, no spam" is the right frame for investor outreach. Slightly lower than Alex/Maya because there's no urgency or timeframe attached. |
| Data Capture | **9/10** | 9 fields: investor name, email, investment strategy, price range, preferred areas, condition preference, deals per year, wholesaler usage, outcome. Best buy-box data capture of all agents. |
| Graceful Exit | **9/10** | "Understood — I'll take you off our list. No further calls. Thanks for your time." Explicit commitment to removal. DNC: immediate mandatory exit. |
| Compliance | **9/10** | DNC handler ✅ mandatory. Assignment fee stated as range, not a guarantee ✅. No cost to join buyer list clearly stated ✅. No fake urgency ✅. AI transparent ✅. Deal frequency framed as estimate ("typically 2–4 deals a month") ✅. Company attribution fixed (no longer SmartBook AI) ✅. |

**Total: 62/70 ✅ PASS**  
*Lowest score: 8/10. No criterion below 6. All thresholds met.*

---

## Summary Scorecard

| Agent | Disclosure | Opening | Objections | Close | Data | Exit | Compliance | **TOTAL** | **RESULT** |
|-------|-----------|---------|-----------|-------|------|------|-----------|-----------|------------|
| Alex  | 10 | 8 | 9 | 9 | 8 | 9 | 9 | **62/70** | ✅ PASS |
| Maya  | 10 | 8 | 9 | 9 | 9 | 9 | 9 | **63/70** | ✅ PASS |
| Dev   | 10 | 7 | 9 | 9 | 8 | 9 | 9 | **61/70** | ✅ PASS |
| Rex   | 10 | 8 | 8 | 9 | 9 | 9 | 10 | **63/70** | ✅ PASS |
| Kai   | 10 | 8 | 9 | 8 | 9 | 9 | 9 | **62/70** | ✅ PASS |

**5/5 PASS ✅**

---

## Deployment Results

All 5 agents passed and were deployed to Vapi (`POST https://api.vapi.ai/assistant`).

| Agent | Vapi Assistant ID | Status |
|-------|-------------------|--------|
| Alex  | `95e7c636-f8e6-4801-8866-fca9d5d475d3` | ✅ Deployed |
| Maya  | `a413b4d6-175d-49b3-8114-cf05879ea5d5` | ✅ Deployed |
| Dev   | `a2f3fb8d-8bdf-4586-9b34-31401fe59856` | ✅ Deployed |
| Rex   | `4c03087c-79c6-4ab0-ad11-5234cc8c5f68` | ✅ Deployed |
| Kai   | `bebae429-b4f1-4f1c-97ad-eb6d3face073` | ✅ Deployed |

Configuration deployed per spec:
- Model: `gpt-4o-mini` (OpenAI)
- Recording: enabled
- Max duration: 180s
- Silence timeout: 30s
- End call function: enabled
- Voice: ElevenLabs per-agent voice IDs

**Deployment note — Maya:** Vapi enforces a 40-character name limit. Maya's full name ("Maya — Local SEO & Reputation Sales Agent") is 41 characters. Deployed as "Maya — Local SEO & Reputation Agent" (35 chars). Script content is 100% unchanged.

**Technical note:** Python `urllib` was blocked by Cloudflare (error 1010) on the Vapi API endpoint. All deployments used `curl` subprocess calls instead — standard resolution for this class of Cloudflare bot-detection issue.

---

## What Changed from Round 1

Scribe addressed every failure point Echo flagged. Key improvements:

1. **AI disclosure** — All 5 first messages now open with "I'm an AI assistant" as the literal first phrase. Previous round: 4 of 5 had awkward double-greetings; Alex had zero disclosure.
2. **DNC handler** — Now mandatory and hard-wired in all 5 system prompts with exact wording and "no follow-up, no pivot" instruction. Previous round: present in 0 of 5.
3. **"How did you get my number?"** — Added to all 5. Previously only Rex had this.
4. **Fabricated data** — Maya's fake opener ("I just pulled up your Google listing...") was the most serious failure. Removed and replaced with honest industry-pattern language. Explicit instruction added to system prompt prohibiting fabricated data claims.
5. **Wrong company attribution** — Dev, Rex, and Kai were attributing themselves to "SmartBook AI" in their prompts/first messages. Fixed in all three.
6. **Objection handling completeness** — All 6 required objection scenarios now covered in all 5 agents.

---

## Honest Observations

- **Dev's opening (7/10)** is the weakest of the five. The "Is this [contact name]?" opening without business confirmation first can feel like a cold-list sweep. Functional, not charming. If Scribe wants to push Dev higher, consider a warmer opener that leads with the problem before confirming identity.
- **Rex's "too expensive" mapping (8/10)** is a rubric mismatch, not a script weakness. Seller outreach doesn't generate price objections in the same way sales calls do — the ARV/pricing handlers are appropriate and well-written. The 8 reflects honest scoring, not a script failure.
- **All 5 agents share strong compliance posture** — DNC handling is now a hard stop with no exceptions, which is the legally correct behavior. This was the most significant gap in Round 1 and it's been fully addressed.

---

*Echo — QA Round 2 complete*  
*2026-03-04*
