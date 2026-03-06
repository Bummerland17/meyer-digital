# Email QA Report — Hawk
**Reviewed:** 2026-03-04  
**Batches:** `outreach-batch3.json` (50 emails sent) · `new-leads-batch2.json` (28 leads)  
**Reviewer:** Hawk — Email Quality Assurance  
**Status:** ⚠️ CRITICAL ISSUES FOUND

---

## ⚠️ Executive Summary — Read This First

Three mission-critical failures were found in this outreach program that require immediate attention before any future batches go out:

1. **32% of outreach-batch3 emails went out with a broken `{biz_type}` template variable** in the subject line — unrendered, visible to every recipient.
2. **4 emails were sent to wrong/third-party addresses** — reaching SEO agencies, web designers, and a university instead of the intended businesses.
3. **The `new-leads-batch2.json` file contains no email content whatsoever** — it is a raw leads file that was apparently not run through QA before being treated as a completed batch. This may indicate a process gap where emails are sent without being stored or reviewed.

These are not nitpicks. These are sender-reputation killers.

---

## Part 1: Individual Email Scoring

> **Note on methodology:** Neither file contains actual email body content — only metadata, subject lines, and lead data. Scores for *Brevity*, *Tone*, and *CTA Clarity* below are estimated from subject line and context where possible, and marked as **[ASSUMED]** where the body was unavailable. This itself is a red flag — see Section 3.

### Scoring Key
| Category | Max | Notes |
|----------|-----|-------|
| Personalization | 10 | Business name + type mentioned? |
| Honesty | 10 | No fake stats, no false guarantees? |
| Brevity | 10 | Under ~120 words? |
| CTA Clarity | 10 | Is the next step unambiguous? |
| Tone | 10 | Professional but human, not pushy? |
| Subject Line | 10 | Relevant, non-clickbait, not spam-triggering? |
| Spam Risk | 10 | Would pass spam filters? (10 = low risk) |

---

### BATCH 1: outreach-batch3.json — Sample of 5

#### Email 1 — Benson Orthodontics (Dr. Ross Schwartz)
**Subject:** *"After-hours calls are costing you bookings — quick question"*  
**Sent to:** bensonortho@earthlink.net

| Category | Score | Notes |
|----------|-------|-------|
| Personalization | 3/10 | Subject mentions no business name; body unknown |
| Honesty | 7/10 | Claim is plausible but unverified — no body to check |
| Brevity | 7/10 | [ASSUMED] Subject suggests a soft opener |
| CTA Clarity | 6/10 | "Quick question" implies ask but is vague |
| Tone | 7/10 | Subject is human-sounding, not robotic |
| Subject Line | 7/10 | Relevant, problem-focused, not clickbait |
| Spam Risk | 6/10 | "Costing you" phrasing is mild risk |
| **TOTAL** | **43/70** | **⚠️ FLAGGED — below 60** |

**Notes:** earthlink.net domain suggests an older, possibly neglected inbox — deliverability risk. Subject-to-business mismatch (no name). Body not available for review.

---

#### Email 2 — Barotz Dental
**Subject:** *"Your phone is losing you $2,000/week — here's how to fix it"*  
**Sent to:** barotzdental@barotzdental.com

| Category | Score | Notes |
|----------|-------|-------|
| Personalization | 2/10 | No business name anywhere in subject |
| Honesty | 3/10 | **"$2,000/week" is a specific, unsubstantiated monetary claim** — no data cited, applies universally to all recipients regardless of size |
| Brevity | 7/10 | [ASSUMED] |
| CTA Clarity | 6/10 | "Here's how to fix it" implies a reveal, but no specific ask |
| Tone | 4/10 | Fear/loss-framing is pushy and adversarial |
| Subject Line | 3/10 | Specific dollar figure is clickbait-adjacent and a known spam trigger |
| Spam Risk | 2/10 | **HIGH SPAM RISK** — dollar amounts in subject lines are flagged by nearly every major spam filter (Gmail, Outlook, SpamAssassin) |
| **TOTAL** | **27/70** | **🚨 RED FLAG — severe** |

**Notes:** This subject line is the most damaging in the rotation. "$2,000/week" is sent to every third recipient regardless of business size — Coors Fitness Center (a university gym) and Ashtanga Yoga Denver (34 reviews, tiny operation) both received this claim. It's both dishonest in its universality and a near-certain spam filter trigger.

---

#### Email 3 — Bissell Dental Group
**Subject:** *"AI answering service for {biz_type} — 48hr setup, $497/mo"*  
**Sent to:** info@bisselldentalgroup.com

| Category | Score | Notes |
|----------|-------|-------|
| Personalization | 0/10 | Broken template, no name, type shows as literal `{biz_type}` |
| Honesty | 5/10 | Price ($497/mo) visible, setup time stated — but body unavailable |
| Brevity | 5/10 | [ASSUMED] |
| CTA Clarity | 5/10 | Subject implies a product offer but no clear next step |
| Tone | 1/10 | **Broken template destroys professional credibility instantly** |
| Subject Line | 0/10 | **Unrendered variable `{biz_type}` sent to recipient — catastrophic** |
| Spam Risk | 2/10 | "AI answering service" + dollar amount = dual spam triggers |
| **TOTAL** | **18/70** | **🚨 CRITICAL FAILURE** |

**Affected businesses (all 16 with this subject):**
Bissell Dental Group, Denver Youth Dentistry, Endorphin City Park, Yoga Center of Denver, LoHi Athletic Club, Glendale Sports Center, Karma Yoga Center, Uncommon Practice Pilates, Transform Colorado, Woodhouse Spa, Grossman Capraro Plastic Surgery, The Eyebrow Lady, Bronzed, Hand & Stone Downtown LoDo, Denver Regenerative Medicine, Cherry Medical

**This is 16 out of 50 emails (32%) from this batch.**

---

#### Email 4 — Grossman | Capraro Plastic Surgery
**Subject:** *"AI answering service for {biz_type} — 48hr setup, $497/mo"*  
**Sent to:** seo.loginuser@growth99.com

| Category | Score | Notes |
|----------|-------|-------|
| Personalization | 0/10 | Broken template + wrong recipient entirely |
| Honesty | 4/10 | Cannot verify body |
| Brevity | 5/10 | [ASSUMED] |
| CTA Clarity | 3/10 | Irrelevant to the SEO agency that received it |
| Tone | 1/10 | Sending to a random SEO firm is unprofessional |
| Subject Line | 0/10 | Broken + wrong recipient |
| Spam Risk | 1/10 | SEO companies report cold outreach spam aggressively |
| **TOTAL** | **14/70** | **🚨 CRITICAL FAILURE** |

**Notes:** `growth99.com` is a marketing/SEO company. This email landed in a competitor's inbox. They now know Wolfgang is running outreach campaigns to plastic surgery clinics, and they may report it as spam or poach the lead.

---

#### Email 5 — Cherry Medical (MediSpa)
**Subject:** *"AI answering service for {biz_type} — 48hr setup, $497/mo"*  
**Sent to:** %20reception@cherrymedispa.com *(invalid address)*

| Category | Score | Notes |
|----------|-------|-------|
| Personalization | 0/10 | Broken template + bounced/invalid address |
| Honesty | 5/10 | Cannot verify |
| Brevity | 5/10 | [ASSUMED] |
| CTA Clarity | 0/10 | Email bounced — no one received it |
| Tone | 0/10 | N/A — undelivered |
| Subject Line | 0/10 | Broken template |
| Spam Risk | 0/10 | Invalid email = hard bounce = **damages sender reputation** |
| **TOTAL** | **10/70** | **🚨 CRITICAL FAILURE** |

**Notes:** The `%20` prefix is a URL-encoding artifact from scraping. This email generated a hard bounce, which directly harms the sending domain's reputation with ISPs. Even one hard bounce in a batch is significant; this needs to be resolved before future sends.

---

### BATCH 2: new-leads-batch2.json — Sample of 5

> ⚠️ **CRITICAL FINDING:** This file is a raw leads list — it contains no subject lines, no email body content, and no `sent_at` or `status` fields. It cannot be reviewed as an email batch because there is no email content to review. This file should NOT have been classified as a sent batch.

> The 5 entries below are evaluated as **lead quality and targeting fitness** only.

---

#### Lead 1 — EōS Fitness (Phoenix, AZ)
*(Appears 4 times in the file — 4 different locations)*

| Issue | Severity |
|-------|----------|
| Chain gym — individual location emails go to location managers | Medium |
| High review count (1,476–2,114) suggests large chain — AI answering pitch needs different angle | Medium |
| Duplicate entries in same batch | High — could send 4x to same brand |

**Lead fitness score: 4/10** — Corporate chain. Outreach should target the regional ops manager, not individual gym managers.

---

#### Lead 2 — Anytime Fitness (Phoenix, AZ)
**Email:** mediainquiries@sebrands.com *(SE Brands — Anytime Fitness corporate PR)*

| Issue | Severity |
|-------|----------|
| Email is a **media inquiries** address at the parent franchise company | Critical |
| Cold sales email to a PR inbox invites spam complaints | Critical |
| Anytime Fitness has 5,000+ locations — they have enterprise vendor solutions | High |

**Lead fitness score: 1/10** — Wrong contact at wrong organizational level. Disqualify.

---

#### Lead 3 — FLEX Spas Phoenix
**Email:** info@flexspas.com  
**Type:** Spa

| Issue | Severity |
|-------|----------|
| FLEX Spas is an adults-only gay bathhouse/men's club — not a medical or beauty spa | Critical |
| Sending an AI booking/answering pitch to this venue is contextually inappropriate | Critical |
| Potential embarrassment if the recipient replies publicly | High |

**Lead fitness score: 0/10** — **Remove immediately.** Wrong business category, inappropriate context for this product.

---

#### Lead 4 — Revive Spa (JW Marriott, Phoenix)
**Email:** PHXDR-SpaSupervisors@marriott.com

| Issue | Severity |
|-------|----------|
| This is a Marriott hotel spa — managed by corporate hospitality, not an independent owner | High |
| Purchasing decisions at hotel spas go through procurement, not spa supervisors | High |
| Email format is hotel-internal distribution list | Medium |

**Lead fitness score: 3/10** — Wrong decision-maker. Low probability lead.

---

#### Lead 5 — North Kenilworth Veterinary Care (Phoenix, AZ)
**Type:** Vet

| Issue | Severity |
|-------|----------|
| Veterinary clinics are not in the current stated target verticals (dental, gym, spa) | High |
| The product pitch (AI answering for after-hours bookings) can work for vets, but copy/messaging would need to be completely different | Medium |
| Indicates scope creep in lead sourcing | Medium |

**Lead fitness score: 5/10** — Potentially viable vertical, but messaging isn't calibrated for it.

---

## Part 2: Overall Quality Assessment

### Score Summary

| Email / Lead | Total | Flag |
|-------------|-------|------|
| Benson Orthodontics | 43/70 | ⚠️ |
| Barotz Dental | 27/70 | 🚨 |
| Bissell Dental Group | 18/70 | 🚨 |
| Grossman \| Capraro (to SEO agency) | 14/70 | 🚨 |
| Cherry Medical (invalid address) | 10/70 | 🚨 |
| EōS Fitness (lead) | 4/10 | ⚠️ |
| Anytime Fitness (lead) | 1/10 | 🚨 |
| FLEX Spas Phoenix | 0/10 | 🚨 |
| Revive Spa / Marriott | 3/10 | ⚠️ |
| North Kenilworth Vet | 5/10 | ⚠️ |

**Overall program quality: 3.5/10**

This outreach program has a technically functional pipeline, but the execution has serious quality control gaps that are actively damaging Wolfgang's sender reputation and wasting outreach opportunities on unreachable or disqualified contacts.

---

## Part 3: Top 3 Improvements for Future Batches

### #1 — Fix Template Rendering Before Any Send
The `{biz_type}` bug is the highest-urgency fix. This is a pre-send validation failure. **Add a mandatory check:** before any batch is sent, scan every subject line and body for unrendered `{variable}` patterns and halt the send if any are found. A 30-second automated check would have caught 16 broken emails.

### #2 — Validate Email Addresses Before Sending
Implement a pre-send email validation step:
- Strip leading/trailing whitespace and URL-encoded characters (`%20`)
- Flag emails that don't belong to the target business domain (e.g., `growth99.com`, `denverwebsitedesigns.com`, `du.edu`)
- Use a simple MX record lookup or a service like ZeroBounce/Hunter to verify deliverability before sending
- Hard bounces from bad addresses directly harm your sending domain's reputation

### #3 — Replace the "$2,000/week" Subject Line
The subject line *"Your phone is losing you $2,000/week — here's how to fix it"* is the most damaging element in the current rotation:
- **It triggers spam filters** (dollar amounts in subject lines are a top spam signal)
- **It's not honest** — a yoga studio with 34 reviews is not losing $2,000/week from missed calls; this claim is applied universally regardless of business size
- **It's fear-based and pushy** — it starts the relationship from a place of manufactured anxiety
- Replace it with something curiosity-based and specific to the business (see template below)

---

## Part 4: Red Flags Needing Immediate Attention

### 🚨 Red Flag 1: No Email Body Content Is Stored
**Impact:** Cannot audit what was actually sent to 50 businesses. If a legal dispute, spam complaint, or compliance review arises, there is no retrievable record of what the email body said.  
**Action:** Store the full email body (plain text at minimum) in every batch record going forward.

### 🚨 Red Flag 2: 16 Businesses Received Visibly Broken Emails (32% of batch)
**Impact:** 16 dental offices, gyms, and spas in Denver received a subject line that literally reads *"AI answering service for {biz_type}"*. This signals unprofessionalism and damages the brand. Any recipient who forwards it internally ("look at this AI spam") multiplies the damage.  
**Action:** Consider sending a brief, honest follow-up: *"Apologies — our last email had a formatting error in the subject line. Here's what we actually meant to say..."* Done well, this actually converts better than the original.

### 🚨 Red Flag 3: FLEX Spas Phoenix in the Lead Pipeline
**Impact:** FLEX Spas Phoenix is an adult gay bathhouse. Sending a cold outreach email for an "AI answering service" would be at best confusing and at worst embarrassing if the recipient replies publicly or posts it.  
**Action:** Remove immediately. Review the lead sourcing process — how did this get classified as a "spa"? The scraper is pulling on category labels without filtering for business type appropriateness.

### ⚠️ Red Flag 4: Emails Sent to Third-Party Vendors
Three businesses had emails pointing to their marketing/web vendors instead of the business itself:
- Grossman | Capraro Plastic Surgery → `growth99.com` (SEO agency)
- Sabai Thai Massage → `denverwebsitedesigns.com`
- Cherry Medical → `%20reception@cherrymedispa.com` (invalid)
**Action:** Before sending, cross-check email domains against business website domains. If they don't match and it's not a well-known provider (Google, Outlook, etc.), flag for manual review.

### ⚠️ Red Flag 5: Large Chains and Franchise Targets
Multiple targets are franchises or chains where individual location managers don't make purchasing decisions:
- Orangetheory Fitness (franchisee location)
- Anytime Fitness (corporate PR email)
- EōS Fitness (4x locations in batch2, chain gym)
- Aveda Institute Denver (corporate school, categorized as "spa")
**Action:** Either craft a different message for franchise locations (acknowledging they may need to run it up the chain) or explicitly exclude chains from cold outreach targeting.

---

## Part 5: Recommended Email Template (Target: 70/70)

This template is written for dental practices but the structure applies to any vertical. Fill in `[BUSINESS_NAME]`, `[VERTICAL]`, and `[SPECIFIC_PAIN_POINT]` before sending.

---

**Subject:** `[BUSINESS_NAME] — quick question about after-hours calls`

*(Personalized with business name — not a generic hook. Low spam-trigger risk. Curiosity-based, not fear-based.)*

---

**Body:**

> Hi [First Name or Team],
>
> Noticed [BUSINESS_NAME] has some great reviews — clearly you're doing right by your patients.
>
> Quick question: what happens when someone calls after hours to book an appointment? If it's going to voicemail, there's a good chance they're booking somewhere else before morning.
>
> We built an AI answering service specifically for [VERTICAL] practices — it books appointments, answers FAQs, and hands off to your team the next morning. Setup takes 48 hours, no contracts.
>
> Worth a 10-minute call to see if it fits? I can do [DAY] at [TIME] or find a time that works for you: [CALENDAR_LINK]
>
> — Wolfgang
>
> P.S. Happy to share what a few other Denver [VERTICAL] practices said after their first month.

---

**Scoring this template:**

| Category | Score | Rationale |
|----------|-------|-----------|
| Personalization | 9/10 | Business name in subject + body, vertical-specific |
| Honesty | 10/10 | No fake stats, no dollar claims — only asks a question |
| Brevity | 10/10 | ~110 words |
| CTA Clarity | 9/10 | Calendar link + specific time offer |
| Tone | 9/10 | Human, direct, not pushy — leads with a compliment + question |
| Subject Line | 10/10 | Business name, no spam triggers, not clickbait |
| Spam Risk | 9/10 | No dollar amounts, no trigger phrases, plain text friendly |
| **TOTAL** | **66/70** | **Near-perfect — achieves 70 with real personalization** |

*(The remaining 4 points come from actual personalization in the body — referencing something specific about the business, their reviews, or their city context. That turns a 66 into a 70.)*

---

## Appendix: Full Issue Inventory

### outreach-batch3.json
| Issue | Count | Severity |
|-------|-------|----------|
| Unrendered `{biz_type}` in subject | 16/50 (32%) | 🚨 Critical |
| Email sent to wrong/third-party address | 4/50 (8%) | 🚨 Critical |
| Invalid email address (hard bounce risk) | 1/50 (2%) | 🚨 Critical |
| Unsubstantiated "$2,000/week" claim | 17/50 (34%) | 🚨 Critical |
| No business name in any subject line | 50/50 (100%) | ⚠️ High |
| Business miscategorized (Oxford Club, Aveda) | 2/50 (4%) | ⚠️ Medium |
| No email body stored for audit | 50/50 (100%) | 🚨 Critical |

### new-leads-batch2.json
| Issue | Count | Severity |
|-------|-------|----------|
| File contains no email content | N/A | 🚨 Critical |
| Inappropriate/wrong vertical lead (FLEX Spas) | 1/28 (4%) | 🚨 Critical |
| Corporate/franchise with wrong decision-maker | 6/28 (21%) | ⚠️ High |
| Duplicate brand entries (EōS Fitness × 4) | 4/28 (14%) | ⚠️ Medium |
| Out-of-vertical lead (vet clinic) | 1/28 (4%) | ⚠️ Medium |

---

*Report prepared by Hawk — Email QA Specialist*  
*Generated: 2026-03-04 | Next review recommended before any future batch sends*
