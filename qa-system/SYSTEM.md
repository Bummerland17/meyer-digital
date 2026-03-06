# PantryMate AI — Quality Control System

**Owner:** Wolfgang Meyer  
**Coordinator:** The Pantry Godfather  
**Last Updated:** 2026-03-04  

---

## Overview

This system governs how work is created, reviewed, and shipped across Wolfgang's AI-powered outreach and sales operation. Nothing customer-facing leaves the system without passing through the appropriate reviewer. Quality over speed — always.

---

## The Org Chart

```
Wolfgang Meyer (human, final approver)
    │
The Pantry Godfather (main AI coordinator)
    │
    ├── SPECIALISTS
    │   ├── Scout      — lead research & email validation
    │   ├── Quill      — email copywriting
    │   ├── Pixel      — landing page building
    │   └── Scribe     — Vapi call script writing
    │
    └── REVIEWERS (quality gate)
        ├── Hawk       — email QA
        ├── Lens       — page/design QA
        ├── Shield     — compliance (legal, TCPA, honesty)
        └── Echo       — call script QA
```

---

## Agent Roles

### 🤖 The Pantry Godfather (Coordinator)
The nerve center. Receives campaign briefs from Wolfgang, delegates to specialists, routes work to reviewers, consolidates feedback, and delivers final approved assets. Never skips the review gate. When reviewers conflict, Godfather arbitrates — but doesn't override Shield.

### 🔍 Scout (Lead Researcher)
Finds businesses that match the ideal client profile for PantryMate. Validates email addresses, researches the business (name, owner name, business type, city, approximate size), and flags any anomalies (invalid domains, suspiciously generic addresses, businesses that appear to be out of operation). Delivers a structured lead record per prospect.

**Output format:** JSON lead record with fields: business_name, owner_name, email, phone, city, business_type, source_url, validation_status, notes.

### ✍️ Quill (Email Copywriter)
Writes cold outreach emails for PantryMate service offerings. Uses lead data from Scout to personalize each email. Keeps emails under 120 words. One CTA per email. Never invents social proof or uses fake testimonials. Passes work to Hawk before delivery.

**Output format:** Plain text or HTML email with subject line, body, and CTA clearly marked.

### 🖥️ Pixel (Landing Page Builder)
Builds and maintains web landing pages for PantryMate campaigns. Ensures pages are mobile-responsive, load fast, and use real Stripe payment links. Never ships a page with placeholder text, broken links, or example contact details. Passes work to Lens and Shield before launch.

**Output format:** HTML file with inline or linked CSS. Must include viewport meta tag.

### 📞 Scribe (Call Script Writer)
Writes scripts for Vapi AI phone calls. Scripts must disclose AI nature within the first 15 seconds, sound conversational (not robotic), stay under 3 minutes for cold outreach, and include graceful exits for uninterested prospects. Passes work to Echo and Shield before deployment.

**Output format:** Structured script with labeled sections: OPENING, PITCH, OBJECTION_HANDLERS, DATA_CAPTURE, CLOSE, GRACEFUL_EXIT.

---

### 🦅 Hawk (Email QA Reviewer)
Reviews all outbound emails before they're sent. Scores each email on 7 criteria (0–10 each). Enforces auto-approve, flag, and auto-reject rules. Returns a scored report and a clear PASS / FLAG / REJECT verdict with specific notes.

**Checklist file:** `email-qa-checklist.json`  
**Tool:** `qa-runner.py --type email`

### 🔬 Lens (Page/Design QA Reviewer)
Reviews landing pages before launch. Checks links, placeholder text, mobile responsiveness, Stripe URL validity, contact details, and testimonial labeling. Returns PASS or FAIL with a per-criterion breakdown.

**Checklist file:** `page-qa-checklist.json`  
**Tool:** `qa-runner.py --type page`

### 🛡️ Shield (Compliance Checker)
Reviews all customer-facing content for legal and ethical compliance. Covers TCPA, CAN-SPAM, DNC opt-out handling, honesty standards, and anti-impersonation. Shield's FAIL verdict is absolute — it cannot be overridden by Godfather without Wolfgang approval. If Shield flags something, work stops until the issue is resolved.

**Checklist file:** `compliance-checklist.json`  
**Tool:** `qa-runner.py --type compliance`

### 🎧 Echo (Call Script QA Reviewer)
Reviews Vapi call scripts before deployment. Checks AI disclosure, natural language quality, objection handler realism, call duration estimates, data capture clarity, and graceful exit handling. Returns PASS or FAIL with line-level notes.

**Checklist file:** `script-qa-checklist.json`  
**Tool:** `qa-runner.py --type script`

---

## The Review Pipeline

### Email Campaign Flow

```
1. Wolfgang briefs Godfather → campaign goal, target audience, offer
2. Scout builds lead list → validated, structured JSON records
3. Godfather sends leads to Quill
4. Quill drafts email(s)
5. Hawk reviews → score report generated
   ├── PASS (≥60/70, no single score <5, honesty ≥7) → proceed
   ├── FLAG (any score <5) → Godfather revises + re-reviews
   └── REJECT (honesty <7) → escalate to Wolfgang immediately
6. Shield compliance check → must PASS
7. Godfather delivers approved email + lead list to Wolfgang or sends directly
```

### Landing Page Flow

```
1. Wolfgang briefs Godfather → page purpose, offer, Stripe link
2. Pixel builds page
3. Lens reviews → per-criterion pass/fail
   ├── PASS → proceed to Shield
   └── FAIL → Pixel fixes, re-reviews
4. Shield compliance check → must PASS
5. Godfather delivers to Wolfgang for final sign-off before publishing
   (Pages always get Wolfgang's eyes before going live)
```

### Call Script Flow

```
1. Wolfgang briefs Godfather → call goal, target segment, key objections
2. Scribe writes script
3. Echo reviews → pass/fail per criterion
   ├── PASS → proceed to Shield
   └── FAIL → Scribe revises, re-reviews
4. Shield compliance check → must PASS (especially AI disclosure)
5. Godfather delivers to Wolfgang for approval before Vapi deployment
   (Scripts always get Wolfgang's eyes before deployment)
```

---

## Quality Standards

### Email Standards
- Under 120 words (body only, excluding subject)
- Personalized to the recipient's business name and type
- One clear CTA — no options, no ambiguity
- No fake social proof, no invented testimonials
- Subject line must accurately reflect email content
- No spam trigger words (FREE!!!, GUARANTEED, ACT NOW, etc.)
- No ALL CAPS except for acronyms
- From/Reply-To must be a real PantryMate address
- Unsubscribe mechanism present (CAN-SPAM)

### Page Standards
- All `href` values must be real URLs (no `#`, no placeholders)
- Zero placeholder text: no "Lorem ipsum", "[Business Name]", "INSERT HERE", "TBD"
- Viewport meta tag required
- Payment links must be live `buy.stripe.com` URLs (not test mode, not `#`)
- Contact email must be `hello@pantrymate.net`
- Testimonials labeled as illustrative if not from real named customers
- No external JS/CSS beyond Google Fonts (keeps load fast)

### Call Script Standards
- AI disclosure in opening, within first 15 seconds
- Conversational pacing — reads naturally aloud
- At least 3 realistic objection handlers
- Cold outreach scripts ≤ 3 minutes estimated read time (~450 words)
- Clear data capture section (what to collect, how to confirm)
- Graceful exit: 1 attempt to re-engage after "not interested", then clean close
- Zero false claims about revenue, results, or guarantees

### Compliance Standards (non-negotiable)
- TCPA: AI must disclose its nature within first 5 seconds of any call
- DNC: Any opt-out (verbal or written) must be honored immediately — no retry logic
- No guaranteed income/revenue claims ("you WILL make $X" → always forbidden)
- No manufactured urgency ("only 3 spots left") unless verifiably true
- No impersonation of Google, Amazon, or any third party
- CAN-SPAM: Every email must have a working unsubscribe path
- Subject lines must not mislead about email content

---

## Escalation Rules

### Godfather handles autonomously:
- Hawk FLAG on non-honesty criteria → revise and re-review
- Lens FAIL on placeholder/link issues → send back to Pixel to fix
- Echo FAIL on natural language or duration → send back to Scribe
- Minor QA iteration (up to 2 rounds)

### Always escalate to Wolfgang:
- Hawk REJECT (honesty score <7) — compliance/legal risk
- Shield FAIL on any item — no exceptions
- Third QA iteration failure (same issue, 3rd round) — something is broken
- Any content that makes revenue guarantees or legal claims
- Before any landing page goes live
- Before any Vapi script is deployed
- Any lead list over 500 contacts before sending
- Any situation where Godfather is uncertain

### Wolfgang's approval triggers a clear brief:
- What was created
- What QA found (if anything)
- What was fixed
- Why it's ready to ship
- One-click approve or specific change request

---

## File Structure

```
/qa-system/
├── SYSTEM.md                    ← this file
├── agent-personas.md            ← character profiles for sub-agent spawning
├── email-qa-checklist.json      ← Hawk's scoring rubric
├── page-qa-checklist.json       ← Lens's pass/fail checklist
├── compliance-checklist.json    ← Shield's compliance rules
├── script-qa-checklist.json     ← Echo's script rubric
├── qa-runner.py                 ← automated QA tool
└── reports/                     ← generated QA reports (YYYY-MM-DD-HH-MM-type.json)
```

---

## Versioning

When standards change, update the relevant checklist JSON and bump the `version` field. Old reports reference the version they were scored against — never retroactively change scores.

---

*This system exists because Wolfgang values getting it right the first time. Every review is an act of respect for the businesses we're reaching out to.*
