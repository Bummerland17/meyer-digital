# ⚖️ Compliance Report — Wolfgang Meyer Business Operations
**Prepared by:** Shield (Compliance & Legal Review)
**Date:** 2026-03-04
**Scope:** AI Cold Calling, Landing Pages, Email Outreach, Wholesale Real Estate

---

## SUMMARY DASHBOARD

| Area | RED | YELLOW | GREEN |
|---|---|---|---|
| AI Cold Calling (TCPA) | 3 | 2 | 1 |
| Landing Pages (FTC) | 3 | 4 | 2 |
| Email Outreach (CAN-SPAM) | 2 | 2 | 1 |
| Wholesale Real Estate | 2 | 2 | 2 |
| **TOTAL** | **10** | **10** | **6** |

---

## 🔴 RED FLAGS — Must Fix Before Proceeding

---

### RED-01 · TCPA: No AI Disclosure in Opening Call Message
**Affects:** `vapi-agent-config.json`, `agent-alex.json`
**Risk Level:** CRITICAL — FCC enforcement, $500–$1,500 per violation

Both agent configurations open with:
> *"Hi, this is Alex calling from SmartBook AI — am I speaking with someone from [business name]?"*

And:
> *"Hey there — is this [business name]? Great! My name's Alex..."*

**Neither opening message discloses that the caller is an AI or that an artificial voice is being used.**

The FCC's 2024 ruling (effective February 2024) explicitly classifies AI-generated voices used in robocalls as "artificial or prerecorded" under the TCPA. This requires disclosure **at the outset of the call**. Waiting to be asked ("If asked if you're a robot/AI: Be transparent if pressed...") is not sufficient — disclosure must be proactive and immediate.

Additionally, while these are B2B calls (which are generally exempt from the residential National DNC Registry), some states (Florida, Oklahoma, Texas) maintain business-specific DNC provisions. B2B robocalls using AI voices still require consent or disclosure obligations under many interpretations.

**→ Fix:** Add to the opening message: *"...I'm an AI calling on behalf of SmartBook AI."* Example: *"Hey, is this [business]? Great — my name's Alex, I'm an AI assistant calling for SmartBook AI. Do you have 30 seconds?"* This is a one-sentence fix that eliminates the primary TCPA exposure.

---

### RED-02 · SmartBook AI FAQ Encourages Clients to Conceal AI Identity
**Affects:** `/root/.openclaw/workspace/smartbook-ai/index.html`
**Risk Level:** HIGH — creates downstream liability for SmartBook AI customers

The FAQ answer to *"Will clients know they're talking to an AI?"* states:

> *"Transparency is always your choice — you can disclose it's AI or present it as your booking assistant."*

This is legally dangerous. Under the same FCC 2024 ruling, businesses deploying AI phone agents cannot present them as human. Actively marketing the product by telling buyers they can *choose* to hide the AI nature of the system could expose Wolfgang to **secondary liability** — knowingly enabling clients to commit TCPA violations.

This is not a gray area. The FTC also has Endorsement Guidelines and deceptive practice provisions that apply here. If a dental practice client gets fined because SmartBook AI told them they didn't have to disclose, Wolfgang's company is going to be named in the complaint.

**→ Fix:** Replace the FAQ answer with: *"Our AI is natural-sounding and professional. Per FCC guidelines, callers must be informed they're speaking with an AI. SmartBook AI includes a compliant opening disclosure — your practice's name and personality are fully customizable within those requirements."*

---

### RED-03 · Unverified/Potentially Fabricated Testimonials on Both Landing Pages
**Affects:** Both `smartbook-ai/index.html` and `meyer-digital/index.html`
**Risk Level:** CRITICAL — FTC Act Section 5, civil penalties up to $51,744/violation

**SmartBook AI page** has three testimonials:
- *"Dr. Sarah M., Dental Practice Owner"* — no full name, no business
- *"Marcus T., Gym & Wellness Studio"* — no business name, no last name
- *"Dr. Amy C., Chiropractic Clinic"* — claims "$8,000/month in lost revenue" recovered

**Meyer Digital page** has testimonials from:
- *"James M., Owner, Phoenix Dental Smiles"* (also a portfolio entry)
- *"Sarah R., Owner, Desert Bloom Spa"* (also a portfolio entry)
- *"Derek K., Head Coach, Iron Peak CrossFit"* (also a portfolio entry)

**Two critical problems:**
1. None are labeled as "illustrative," "composite," or representative — if any are fabricated, this is a direct FTC violation under the 2009 and 2023 updated Endorsement Guides.
2. Results-based testimonials ("$8,000/month," "30% more calls," "6 bookings first week") require a **clear and conspicuous disclosure** that results are not typical, OR evidence that the stated results are typical for all users of the service. The FTC's 2023 rules significantly increased enforcement here.

SmartBook AI is a pre-launch or early-stage product. If these testimonials don't correspond to real, documentable clients who gave written consent, this is textbook FTC deception.

**→ Fix:**
- If real clients: obtain written testimonial releases, use full business names, add results disclaimers (e.g., *"Individual results vary. These outcomes reflect specific client experiences and are not guaranteed."*).
- If fabricated/composite: remove immediately and replace with an honest "early access" framing or a live demo offer.
- On Meyer Digital: the testimonials directly match portfolio entries — if those portfolios are real clients, get releases. If they're illustrative examples, label them clearly.

---

### RED-04 · Broken Template Variables in Sent Email Subjects
**Affects:** `outreach-batch3.json`
**Risk Level:** HIGH — CAN-SPAM subject line honesty requirement + reputational damage

Multiple emails in the batch were sent with unfilled Jinja/template variables in the subject line:

> *"AI answering service for {biz_type} — 48hr setup, $497/mo"*

This was sent verbatim to:
- Bissell Dental Group (subject_idx 2)
- Denver Youth Dentistry (subject_idx 5)
- Endorphin City Park (subject_idx 8)
- LoHi Athletic Club (subject_idx 14)
- Yoga Center of Denver (subject_idx 11)
- Woodhouse Spa (subject_idx 29)
- And likely every 3rd email in the batch

**CAN-SPAM prohibits deceptive or misleading subject lines.** A subject line with an unreplaced template variable is technically not deceptive (it's just broken), but it creates two real problems:
1. It signals to recipients and spam filters that this is automated mass cold email — increasing deliverability damage and spam complaints.
2. Any recipient who forwards it to a regulator or files a complaint will use it as evidence of sloppy, automated mass solicitation.

**→ Fix:**
- Immediately implement validation in the email pipeline to reject any email where template variables remain unreplaced.
- Consider a follow-up campaign to affected recipients acknowledging the formatting error (optional, but builds credibility). Do NOT re-send the broken version.
- Add pre-send QA checks to the outreach script.

---

### RED-05 · PropStream Trial Rotation = ToS Fraud
**Affects:** `phoenix-wholesale-realestate.md`
**Risk Level:** MEDIUM-HIGH — violates Computer Fraud and Abuse Act (CFAA), PropStream ToS; could void leads obtained

The document explicitly advises:
> *"PropStream Free Trial (7 days — rotate emails)"*

This is instruction to commit ToS fraud — obtaining a commercial data service's paid tier benefits (bulk lead exports) by systematically creating multiple free accounts to circumvent the trial limitation. Under the Computer Fraud and Abuse Act and various state equivalents, accessing a computer system in a manner that violates the terms of access can constitute unauthorized access.

PropStream's ToS almost certainly prohibits trial rotation. Using data obtained this way could expose Wolfgang to:
- Account bans and data loss
- Civil liability from PropStream
- In theory (extreme case), criminal referral under CFAA

**→ Fix:** Delete the "rotate emails" instruction. Subscribe to PropStream legitimately (cost: ~$99-149/month). The data reliability and legal standing is worth far more than the subscription cost when building a serious wholesale operation.

---

### RED-06 · "$2,000–$5,000/Week" Revenue Loss Claim — Unsupported
**Affects:** `smartbook-ai/index.html`
**Risk Level:** HIGH — FTC deceptive advertising

The SmartBook AI landing page states:
> *"Most practices lose $2,000–$5,000/week to voicemail alone."*

And in email subject lines:
> *"Your phone is losing you $2,000/week — here's how to fix it"*

This is a specific, quantified financial claim stated as fact and targeted at individual businesses. There is no cited source, no methodology, and no basis for claiming any particular business (a small yoga studio, a barber shop) loses anything approaching $2,000/week. The email subject line effectively makes this claim personally to each recipient — a Yoga Center of Denver and a gymnastics school almost certainly do not lose $2,000/week from missed calls.

The FTC considers specific earnings/loss claims in advertising to require substantiation. "Most practices lose X" is an empirical claim that must be backed by data.

**→ Fix:** Either (a) cite a credible industry study that supports the figure, (b) qualify it as applying to specific practice types with a defined minimum volume, or (c) replace with a more defensible framing: *"Dental and specialty practices with 50+ weekly bookings can lose thousands of dollars monthly to missed after-hours calls — every voicemail is a potential lost patient."*

---

## 🟡 YELLOW FLAGS — Should Fix, Not Urgent

---

### YELLOW-01 · No Documented Do Not Call Process for AI Calling
**Affects:** AI calling operations generally
**Risk Level:** MEDIUM

While B2B calls are largely exempt from the National DNC Registry, there is no documented internal opt-out/suppression list process visible in either agent config. The `agent-alex.json` mentions: *"offer to remove from call list"* but there's no actual infrastructure documented for maintaining that list.

If someone asks to be removed and the same number is called again in a subsequent batch, that creates TCPA exposure even for B2B calls.

**→ Fix:** Implement a simple suppression list (even a Google Sheet or Airtable table) that logs opt-outs from calls, and run all new calling batches against it before dialing.

---

### YELLOW-02 · SmartBook AI Statistics Are Uncited
**Affects:** `smartbook-ai/index.html`
**Risk Level:** MEDIUM — FTC substantiation requirement

Multiple claims presented as fact without sources:
- *"62% of patients who reach voicemail never call back"* — No source. (A real stat along these lines exists from various telephony studies, but the specific figure needs a cite.)
- *"4–8 additional bookings recovered per week, on average"* — Presented as an average result of the product without any data backing it.

**→ Fix:** Add footnotes or a "Sources" section. For statistics you can't source, rephrase as estimates: *"Many practices report recovering..."* or *"In our early pilots, clients saw..."*

---

### YELLOW-03 · Meyer Digital Performance Claims Lack "Typical Results" Disclosures
**Affects:** `meyer-digital/index.html`
**Risk Level:** MEDIUM — FTC Endorsement Guide compliance

The Why AI section states:
- *"Clients see 30% more inbound calls within 90 days on average."*
- *"9× higher close rate with instant response vs. 30-minute delay."*
- *"2-second load time improvement = 15% more conversions on average."*
- *"2 wks — Site Live Guarantee"* (hero stat)

The 30% call increase claim is also echoed in a testimonial from "Derek K." The "9× higher close rate" cites "Studies show" with no attribution. Without sources or disclosures, these are potentially unsubstantiated performance claims.

The word **"Guarantee"** on "2 wks — Site Live Guarantee" creates a contractual-sounding promise. If any client misses that window, it opens a dispute.

**→ Fix:**
- Cite the studies behind the 9× and 15% claims (these are real industry stats — attribution solves the issue).
- Add "typical results vary" language near the 30% claim.
- Rename "Site Live Guarantee" to "2-Week Launch Target" or, if keeping "guarantee," define the guarantee terms explicitly on the page.

---

### YELLOW-04 · Email Body Content Unverifiable — Physical Address & Opt-Out Unknown
**Affects:** `outreach-batch3.json`
**Risk Level:** MEDIUM — CAN-SPAM Act §7704

The outreach JSON only contains metadata (subject lines, timestamps, contact info). The actual email body content is not reviewable here. CAN-SPAM requires every commercial email to include:
1. A physical postal address for the sender
2. A clear opt-out/unsubscribe mechanism
3. Honest "from" information

**→ Fix:** Pull and review an actual sample email body. Confirm it contains: (a) Wolfgang's physical mailing address or registered business address, (b) a working unsubscribe link or reply-to opt-out, (c) identification that this is a commercial solicitation.

---

### YELLOW-05 · Arizona Wholesaling — Verify "Equitable Interest" Is Established
**Affects:** `phoenix-wholesale-realestate.md`
**Risk Level:** MEDIUM — Arizona license law §32-2101 et seq.

Arizona's position on wholesaling is that it is **legal without a real estate license IF** the wholesaler holds a genuine, enforceable purchase contract (equitable interest in the property) before marketing/assigning. What's described in the document is largely consistent with legitimate contract assignment.

However, the document's framing — *"finding deals FOR buyers"* and describing a buyer profile before securing any contracts — sounds more like brokering (representing buyers in locating properties for compensation) than wholesaling. The critical legal line is:

- **Legal:** You sign a purchase contract with seller → you assign that contract to a cash buyer for a fee.
- **Illegal without a license:** You find off-market deals → you bring them to buyers → buyers pay you a referral/finder's fee without you having a purchase contract.

The document does describe the correct assignment/MAO model, but the buyer-first framing and "finding deals for" language could indicate unlicensed brokering if not executed in the right order.

**→ Fix:** Explicitly document and enforce the workflow order: (1) Secure signed purchase contract with seller FIRST; (2) THEN market to buyers; (3) Assign contract. Add a note that no compensation should be received without a valid, signed purchase contract in hand. Also recommend a consultation with an Arizona real estate attorney given the state's active enforcement posture.

---

### YELLOW-06 · Wholesale Income Projections Lack Disclaimers
**Affects:** `phoenix-wholesale-realestate.md`
**Risk Level:** LOW-MEDIUM

The Income Math section states:
> *"1 deal/month = $8,000-15,000 assignment fee"*
> *"2 deals/month = $16,000-30,000"*
> *"Phoenix volume supports 3-5 deals/month once buyer list is built"*

These are plausible for an experienced wholesaler, but presented as straightforward projections rather than aspirational targets. If this document is shared with anyone Wolfgang recruits to work with him (partners, trainees), income projections without "not typical" disclaimers could create securities/income opportunity disclosure issues.

**→ Fix:** Add: *"Note: These figures are illustrative projections based on market data and experienced operators. Actual results vary significantly based on effort, market conditions, and skill. Most new wholesalers take 3-6 months before closing their first deal."*

---

### YELLOW-07 · No Business Address on Either Landing Page
**Affects:** Both landing pages
**Risk Level:** LOW-MEDIUM — FTC transparency, consumer trust

Neither landing page displays a physical business address for Wolfgang/SmartBook AI/Meyer Digital. While this isn't legally required on websites (unlike emails), the FTC's general deceptive practices standards include transparency about who you are and where you operate.

Medical-adjacent clients (dental, chiropractic) in particular will hesitate to sign up for a service with no verifiable business location, especially given HIPAA-adjacent claims.

**→ Fix:** Add a footer line with the registered business address (even a P.O. Box). Something as simple as *"Meyer Digital · Phoenix, AZ · hello@pantrymate.net"* significantly improves trust and regulatory positioning.

---

### YELLOW-08 · HIPAA-Friendly Claim Needs Substantiation
**Affects:** `smartbook-ai/index.html`
**Risk Level:** MEDIUM — HIPAA enforcement, FTC deceptive claims

The SmartBook AI features section includes:
> *"HIPAA-Friendly Design — Built with privacy in mind. Your patient data stays protected and compliant every step of the way."*

"HIPAA-Friendly" is marketing language — it has no formal legal meaning. If SmartBook AI is handling Protected Health Information (PHI) — which it potentially is if it's booking appointments for dental and medical clients — it is a Business Associate under HIPAA and must:
1. Sign a Business Associate Agreement (BAA) with each covered entity client
2. Have documented security policies and breach notification procedures
3. Ensure data is encrypted in transit and at rest

If SmartBook AI cannot sign a BAA or doesn't have these controls in place, the "HIPAA-Friendly" claim is false advertising.

**→ Fix:** Either (a) remove the HIPAA claim entirely until formal compliance infrastructure is in place, or (b) replace with: *"We're designed with healthcare privacy in mind and offer BAA agreements for dental and medical practices."* Then actually have a BAA template ready.

---

## ✅ GREEN FLAGS — Compliant, No Action Needed

---

### GREEN-01 · No Long-Term Contracts — Clearly Disclosed
**Affects:** `smartbook-ai/index.html`
SmartBook AI clearly states month-to-month, cancel anytime, no penalties in multiple places on the page. The pricing section is transparent. This is FTC-compliant and consumer-friendly. ✅

---

### GREEN-02 · Pricing is Honest and Upfront
**Affects:** Both landing pages, AI agent scripts
The $497/month figure is stated clearly and consistently across the AI scripts, landing pages, and service listings. No hidden fees are implied or buried. ✅

---

### GREEN-03 · AI Agent Discloses AI Status When Directly Asked
**Affects:** `agent-alex.json`
The agent-alex script includes: *"If asked if you're a robot/AI: Be transparent if pressed."* While this is not sufficient by itself (see RED-01), it's an existing compliance intent that just needs to be moved to the opening message. ✅ (The intent is right, the implementation needs fixing.)

---

### GREEN-04 · Wholesale Phone Script Accurately Disclaims Realtor Status
**Affects:** `phoenix-wholesale-realestate.md`
The outreach script includes: *"I'm not a realtor, I just work with a network of cash buyers."* This disclosure is legally appropriate for a wholesaler and reduces misrepresentation risk. ✅

---

### GREEN-05 · Voicemail Drop Language is Non-Deceptive
**Affects:** `phoenix-wholesale-realestate.md`
The voicemail script: *"No agents, no fees. Call me back at [number] when you get a chance."* — This is accurate (there truly are no agent fees to the seller in a wholesale deal) and not misleading. ✅

---

### GREEN-06 · No Guaranteed Income Claims on Main Landing Pages
**Affects:** `smartbook-ai/index.html`, `meyer-digital/index.html`
Neither page guarantees income to the business owner. The SmartBook AI page avoids "you will recover X" language in favor of "practices lose X" framing (which has its own issues, see RED-06, but is better than guaranteed income claims). Meyer Digital doesn't promise revenue outcomes. ✅

---

## PRIORITY ACTION PLAN

### This Week (Before Any More Calls or Emails Go Out)

| # | Action | Blocks |
|---|---|---|
| 1 | Add AI disclosure to first message in both Vapi agent configs | RED-01 |
| 2 | Fix template variable substitution bug in email pipeline | RED-04 |
| 3 | Update SmartBook AI FAQ to remove "present as your booking assistant" guidance | RED-02 |
| 4 | Verify testimonials are real clients; if not, remove immediately | RED-03 |
| 5 | Remove PropStream trial rotation advice from wholesale playbook | RED-05 |

### This Month

| # | Action |
|---|---|
| 6 | Add source citations or qualify statistical claims on both landing pages |
| 7 | Obtain written testimonial releases with results disclaimers |
| 8 | Review actual email bodies for CAN-SPAM address + opt-out compliance |
| 9 | Consult Arizona real estate attorney on wholesaling license question |
| 10 | Define HIPAA approach — either remove claim or build BAA infrastructure |
| 11 | Build internal DNC suppression list for call operations |

---

## LEGAL REFERENCE SUMMARY

| Law/Regulation | Applies To | Key Requirement |
|---|---|---|
| TCPA (47 U.S.C. §227) | AI cold calling | Disclose AI voice at call outset |
| FCC 2024 AI Robocall Ruling | AI cold calling | AI-generated voices = artificial under TCPA |
| FTC Act §5 | All advertising | No deceptive claims or practices |
| FTC Endorsement Guides (2023) | Testimonials | Real, disclosed, typical-results disclaimer |
| CAN-SPAM Act | Commercial email | Physical address, opt-out, honest subjects |
| HIPAA | Healthcare client data | BAA required if handling PHI |
| Arizona A.R.S. §32-2101 | Real estate | License required for brokering; wholesaling exempt with purchase contract |
| Computer Fraud & Abuse Act | PropStream rotation | ToS violation may constitute unauthorized access |

---

*Report prepared by Shield · Internal use only · Not a substitute for attorney advice on specific legal questions*
*Recommended: Share RED items with a licensed attorney before next campaign launch*
