# SmartBook AI — Complete Business Setup Guide
### AI Appointment Setting for Dental Offices | 2026 Edition

---

## PART 1: PLATFORM RESEARCH — FREE TIERS & WHAT YOU GET

### Retell AI (retellai.com) ✅ BEST FREE START
**Confirmed from their pricing page (March 2026):**

| Feature | Free/Pay-As-You-Go |
|---|---|
| Starting cost | **$0 to start** |
| Free credits | **$10 free credits** (~143 minutes at base rate) |
| Voice agent rate | $0.07+/min (base infrastructure + voice) |
| Concurrent calls | 20 free concurrent calls |
| Knowledge Bases | 10 free knowledge bases |
| Credit card required? | **No** — sign up and start instantly |
| Support | Discord + Email |

**Real talk:** $10 free = ~140 minutes of call time. Enough to build and demo your agent, record sample calls, and show prospects. When you add a paying client, top up with their monthly fee.

**LLM/TTS add-ons (extra):**
- GPT-4o mini: ~$0.01/min extra
- ElevenLabs voices: ~$0.01-0.03/min extra
- Total realistic cost: **$0.09–0.12/min** all-in

---

### Synthflow AI (synthflow.ai) ✅ ALSO GOOD
**Confirmed from their pricing page (March 2026):**

| Feature | Pay-As-You-Go |
|---|---|
| Starting cost | **$0 to start** |
| Model | Usage-based billing only |
| Concurrent calls | 5 included, +$20/reserved slot after |
| Credit card required? | Required to add credits, but $0 upfront |
| Agents | Unlimited |
| Compliance | SOC2, GDPR, ISO 27001 (great for HIPAA conversations) |
| White label | Available (Enterprise add-on) |

**Pricing add-ons (optional):**
- Performance Routing: +$0.04/min
- Global Low Latency Edge (<600ms): +$0.04/min

**Verdict for beginners:** Synthflow requires a card to load credits but starts at $0. Good for HIPAA-adjacent use cases because of their compliance certs. Retell is easier to start with zero friction.

---

### Vapi.ai (vapi.ai) ✅ DEVELOPER FAVORITE
**From their docs (March 2026):**

| Feature | Free |
|---|---|
| Starting cost | **$0 — free account** |
| Free US phone number | **Yes, built into dashboard** (no Twilio needed) |
| Credit card required? | **No — sign up and start** |
| Billing | Usage-based after free credits |

**Why Vapi is great for demos:**
- Free US phone number directly in the dashboard — no Twilio setup needed
- Create assistant in 5 minutes using their template system
- Can record calls natively for demo playback

---

### Make.com (make.com) ✅ FREE AUTOMATION
| Feature | Free Tier |
|---|---|
| Operations/month | 1,000 |
| Active scenarios | 2 |
| Credit card required? | No |
| Data history | 30 days |

**1,000 ops = plenty for a small dental office.** Each call → booking → SMS confirmation = ~3-5 operations. You'd need 200+ bookings/month to hit the limit (that's a busy office). Upgrade to Core ($9/mo) if you hit it.

---

### Bland AI (bland.ai) ❌ NOT FOR BEGINNERS ANYMORE
As of 2026, Bland AI has pivoted to enterprise-only. No public free tier. Pricing requires talking to sales. Skip it for starting out.

---

### Twilio (for SMS + phone numbers)
| Feature | Cost |
|---|---|
| US phone number | $1.15/month |
| SMS (outbound) | $0.0079/message |
| Inbound call minutes | $0.0085/min |

**For a dental office getting 20 calls/day and sending 20 SMS confirmations:**
- Phone: $1.15/mo
- SMS: ~$4.74/mo (600 messages)
- That's **~$6/month** for communications infrastructure

---

## PART 2: FREE TECH STACK TO DELIVER THE SERVICE

### Recommended Stack (Cheapest to Start, Scales to $497/client)

```
CALL COMES IN → Retell AI (or Vapi) → Dentrix/Google Calendar API
                      ↓
              Make.com automation
                      ↓
              Twilio SMS confirmation → Patient's phone
```

**Component breakdown:**

| Component | Tool | Monthly Cost |
|---|---|---|
| AI Voice Agent | Retell AI | ~$8–15/client (at 100 calls/mo) |
| Phone Number | Vapi built-in OR Twilio | $0–1.15 |
| Calendar Integration | Google Calendar API (free) | $0 |
| Booking automation | Make.com Core | $9 |
| SMS confirmations | Twilio | ~$5 |
| CRM/tracking | Notion or Google Sheets | $0 |
| **Total per client** | | **~$22–30/month** |
| **Your price** | | **$497/month** |
| **Margin** | | **~$467/month (~94%)** |

---

### Option B: Vapi-Only Stack (Simplest for beginners)

Vapi handles everything in one place:
1. Sign up at dashboard.vapi.ai
2. Create assistant using "Customer Support" template — edit for dental
3. Get free US phone number inside Vapi dashboard (no Twilio needed)
4. Set up webhook → Make.com for SMS and calendar
5. **Cost: Vapi usage + Make.com $9/mo + Twilio SMS ~$5/mo = ~$20-30/mo/client**

---

## PART 3: THE SERVICE

### Business Name Options
- **SmartBook AI** ✅ (clean, clear, professional)
- **DentaVoice** (dental-specific, memorable)
- **ReceptionistAI** (generic but converts)
- **CallFill** (implies filling gaps/missed calls)

**Recommendation: SmartBook AI** — works beyond dental if you want to expand.

---

### The Core Pitch

> *"Your phones ring after hours. Patients hang up. You lose $200–500 per missed booking. SmartBook answers 24/7, books appointments, and sends confirmations automatically — all for less than the cost of one missed patient."*

**For the website/email header, shorter version:**
> *"Stop losing $500 every time your phone goes unanswered."*

---

### What You're Selling: $497/Month

**Everything included in $497/mo:**

✅ **24/7 AI phone agent** — answers every inbound call, day or night  
✅ **Natural conversation** — the AI sounds human, asks the right questions  
✅ **Appointment booking** — captures patient name, DOB, reason for visit, preferred time  
✅ **Real-time calendar sync** — checks availability, books directly into their schedule  
✅ **Automated SMS confirmation** — patient gets a text with appointment details  
✅ **SMS reminder** — day-before reminder to reduce no-shows  
✅ **Call recordings & transcripts** — the dentist can review every call  
✅ **Setup included** — you configure everything, they just forward their after-hours line  
✅ **Monthly reporting** — calls handled, appointments booked, revenue recovered  

---

### What You Actually Do (Setup Checklist)

**Week 1 — Onboarding (3–4 hours of work):**

- [ ] Get their Google Calendar or Dentrix calendar access
- [ ] Set up Retell AI (or Vapi) account, create AI agent
- [ ] Train agent on: office hours, services offered, insurance accepted, cancellation policy
- [ ] Configure Make.com: Retell webhook → Google Calendar → Twilio SMS
- [ ] Buy Twilio number (or port theirs) — $1.15/mo
- [ ] Write confirmation SMS template (merge name + date + time)
- [ ] Write reminder SMS (24h before appointment)
- [ ] Test 10 call scenarios: new patient, existing patient, after-hours, insurance question, emergency
- [ ] Do 3 live test calls with the dentist listening

**Ongoing (1–2 hours/month):**
- [ ] Review call logs for issues
- [ ] Update calendar availability if hours change
- [ ] Monthly report: # calls handled, # booked, estimated revenue recovered

---

### AI Agent Script (Copy This Into Retell/Vapi)

**System Prompt (paste into Retell AI "Agent Instructions"):**

```
You are a friendly dental receptionist for [OFFICE NAME]. Your name is [NAME - e.g., "Sarah"].

Your job is to:
1. Warmly greet callers
2. Determine if they want to book an appointment, ask a question, or need emergency guidance
3. For bookings: collect their name, date of birth (for existing patients), reason for visit, preferred date/time
4. Check availability and offer 2-3 time slots
5. Confirm the appointment and tell them they'll get a text confirmation
6. For emergencies: provide the on-call number [XXX-XXX-XXXX] and suggest the nearest emergency dental clinic

IMPORTANT RULES:
- Never diagnose conditions
- Never discuss pricing beyond "your insurance may cover this — we'll verify at your appointment"
- If asked about specific procedures, say "Dr. [Name] will discuss that at your visit"
- Keep calls under 3 minutes when possible
- Always end with: "You'll receive a text confirmation shortly. Is there anything else I can help you with?"

Office details:
- Name: [OFFICE NAME]
- Hours: [Mon-Fri 8am-5pm, closed weekends]
- Address: [ADDRESS]
- Insurance accepted: [LIST]
- Services: cleanings, fillings, crowns, extractions, emergency exams
```

**First message (what the AI says when the call connects):**
```
"Thank you for calling [OFFICE NAME]! This is Sarah. How can I help you today?"
```

---

## PART 4: HOW TO DEMO WITH NO EXISTING CLIENTS

### "Can we see it work?" — Your Answer

> *"Absolutely. I've already built a working demo for a dental office — I'll send you the number right now. Call it, say you want to book a cleaning next Tuesday, and see what happens. It takes about 90 seconds. Then let's talk."*

### Setting Up Your Demo Agent (Do This Before Any Outreach)

**Step 1: Create a demo dental office**
- Name: "Bright Smile Dental" (generic enough to work universally)
- Hours: Mon–Fri 9am–5pm, Sat 9am–1pm

**Step 2: Build in Vapi (free US number included)**
1. Go to dashboard.vapi.ai → Sign up (no card needed)
2. Create Assistant → use "Customer Support" template
3. Edit system prompt with the dental script above (use "Bright Smile Dental")
4. Go to Phone Numbers → "Create New" → Free US number
5. Assign your assistant to that number
6. Test call it from your own phone

**Step 3: Record a clean demo call**
1. Call your demo number
2. Say: *"Hi, I'd like to schedule a cleaning"*
3. Let the AI handle the full booking flow
4. Record on your phone OR use the built-in Vapi call recording
5. Save the mp3 — you'll email this to prospects

**Step 4: Trim and use**
- Use Descript (free tier) or Audacity (free) to trim to the best 60–90 seconds
- Upload to Google Drive or Loom
- Include the link in your cold emails

### The Demo CTA Script (For Sales Calls)
> *"Before we get into pricing, I want you to actually hear it. Can you call this number right now? [Give them the number.] Just say you want to book a cleaning. I'll wait."*

[Pause while they call]

> *"So — that's what your patients would hear at 8pm on a Tuesday when they're lying in bed with a toothache and decide they finally need to call a dentist. Instead of voicemail, they get Sarah. And that patient gets booked. That's the product."*

---

## PART 5: COLD OUTREACH

### 10 Cold Email Subject Lines (Dental Offices)

1. `Your phones are costing you $3,000/month`
2. `Missed calls = missed fillings (a quick fix)`
3. `[PRACTICE NAME] — what happens when patients call at 8pm?`
4. `Your voicemail doesn't book appointments`
5. `I recorded an AI answering a dental phone — want to hear it?`
6. `One missed patient call = $300 lost. Here's the math.`
7. `Does [PRACTICE NAME] answer calls after 5pm?`
8. `The thing your front desk can't do (AI can)`
9. `I built something for [CITY] dental offices — 60-second listen?`
10. `[DOCTOR NAME] — your after-hours calls are going to voicemail`

---

### Core Outreach Email

**Subject:** `Your voicemail doesn't book appointments`

---

Hi [Dr. Last Name],

Quick question — when a patient calls [Practice Name] at 7pm on a Wednesday and gets voicemail, what happens?

They hang up. They call the next dentist on Google. You lose the booking.

The average dental appointment is worth $200–500. If your phone goes unanswered 10–15 times a month (conservative), that's $2,000–7,500 in lost revenue quietly disappearing.

I built SmartBook AI specifically for practices like yours. It's an AI receptionist that:

- **Answers every call, 24/7** — nights, weekends, holidays
- **Books appointments in real time** — checks your calendar, grabs a slot
- **Sends an SMS confirmation** — the patient gets it before they hang up

I recorded a 90-second demo of it handling a new patient call. [▶ Listen here →](YOUR_LOOM_LINK)

Flat rate: **$497/month**, everything included. No setup fees, no contracts.

Want me to set up a live demo on your actual phone number?

[Your Name]  
SmartBook AI  
[Phone] | [Website]

P.S. — The demo is live right now. You can call it: [YOUR DEMO NUMBER]. Say you want to book a cleaning.

---

### Follow-Up Sequence

---

**Day 1 Follow-Up (send 24h after initial email)**

**Subject:** `Re: Your voicemail doesn't book appointments`

---

Hi [Dr. Last Name],

Did you get a chance to call the demo number? I want to make sure it actually came through.

[DEMO NUMBER] — takes 60 seconds. Just say you want to schedule a cleaning.

If you're curious about how it connects to your calendar, I can show you a 10-minute walkthrough on Zoom this week — no pitch, just the product.

[Your Name]

---

**Day 3 Follow-Up**

**Subject:** `The math on missed dental calls`

---

Hi [Dr. Last Name],

I work with a few dental offices now, and the pattern I see is always the same:

The front desk is great during business hours. But 30–40% of patient calls happen outside those hours — evenings, early mornings, weekends. Those callers want to book *now*. When they hit voicemail, most don't leave a message. They try the next option on Google.

SmartBook handles those calls. $497/month. You keep the patients.

If this isn't a fit for [Practice Name], no problem at all. But if you do want to see the numbers on your specific call volume, I can pull that together in about 5 minutes.

Worth a quick chat?

[Your Name]

---

**Day 7 Follow-Up (final)**

**Subject:** `Closing the loop on [Practice Name]`

---

Hi [Dr. Last Name],

Last note from me — I don't want to fill your inbox.

If the timing is wrong or you've already solved the after-hours coverage problem, I completely understand. Just let me know and I'll stop reaching out.

But if you're still losing calls to voicemail and want a fix that runs itself, I'm here.

Either way — the demo line is always open: [DEMO NUMBER]

[Your Name]  
SmartBook AI

---

## PART 6: OBJECTION HANDLING

### "We already have a voicemail system."
> *"Voicemail records messages — it doesn't book appointments. SmartBook actually gets the patient onto your calendar. There's a big difference between a message that says 'call us back' and a confirmed appointment in your system."*

### "What if the AI says something wrong?"
> *"It's trained on your exact office information — hours, services, insurance, policies. It doesn't improvise. For anything it can't handle (billing disputes, specific diagnosis questions), it tells the patient to call back during office hours. You also get a recording of every call."*

### "We're not sure about HIPAA."
> *"SmartBook collects name, contact info, and appointment details — the same thing your front desk captures over the phone. It does not access medical records. The data is encrypted and stored securely. Most dental offices find this meets their operational requirements, but I'd encourage you to review with your compliance person. I can provide our data handling documentation."*

> *(Note for you: Retell AI and Synthflow both have SOC2/GDPR compliance. For strict HIPAA BAA requirements, use Synthflow — they offer BAA agreements. This can be an upsell: "HIPAA-compliant plan: $697/mo.")*

### "Can we try it before committing?"
> *"Yes. I'll set it up on a test number for your office for 2 weeks. You don't pay anything until you see it work on your actual calls. If you want to continue, we go to $497/month. If not, nothing owed."*

### "That seems expensive."
> *"One new patient appointment is $200–500. If SmartBook books two extra patients a month that would have hung up on your voicemail, it pays for itself. At 10 saved calls a month, you're netting $1,500–4,500 over the $497 cost."*

---

## PART 7: OPERATIONAL SETUP CHECKLIST

### Tools to Sign Up For (All Free to Start)
- [ ] **Retell AI** — retellai.com (free, $10 credits, no card) OR **Vapi.ai** — vapi.ai (free number included)
- [ ] **Make.com** — make.com (free, 1,000 ops/mo)
- [ ] **Twilio** — twilio.com ($15 free trial credit, then pay-as-you-go)
- [ ] **Google Calendar** — for your demo office (free)
- [ ] **Loom** — loom.com (free tier, 5-min videos — for demo recordings)
- [ ] **Descript** — descript.com (free tier — for trimming demo audio)
- [ ] **Notion** — notion.so (free — for client tracking)
- [ ] **Stripe** — for billing clients (2.9% + $0.30/transaction)

### First Week Action Plan

**Day 1 (2 hours):**
- Sign up for Retell AI + Vapi
- Build "Bright Smile Dental" demo agent
- Record 3 test calls

**Day 2 (1 hour):**
- Set up Make.com
- Build automation: call ends → SMS sent via Twilio
- Test end-to-end flow

**Day 3 (1 hour):**
- Edit demo recording in Descript
- Upload to Loom
- Write your outreach email (use template above)

**Day 4 (2 hours):**
- Research 20 dental offices in your city (Google Maps)
- Get owner/office manager name + email (LinkedIn, website contact page)
- Personalize subject lines

**Day 5 (1 hour):**
- Send first 20 emails
- Set up follow-up reminders in Notion

**Week 2:**
- Send follow-ups
- Aim for 2–3 demo calls booked
- Close first client → $497 hits Stripe → start their setup

---

## PART 8: PRICING LADDER (OPTIONAL UPSELLS)

| Tier | Price | What's Included |
|---|---|---|
| **SmartBook Starter** | $297/mo | AI answers calls, collects info, no calendar sync |
| **SmartBook AI** | $497/mo | Full booking + SMS confirmations (your core offer) |
| **SmartBook Pro** | $697/mo | + HIPAA BAA, SMS reminders, monthly reporting call |
| **SmartBook Multi** | $997/mo | 2 locations, priority support, custom voice |

**Upsell after 60 days:**
> *"Now that we're booking consistently, would you want us to add automated recall texts? We can remind patients when they're due for their 6-month cleaning. That's a $200/month add-on and it runs itself."*

---

## QUICK REFERENCE CARD

| Item | Detail |
|---|---|
| Service name | SmartBook AI |
| Core pitch | "Stop losing $500 every time your phone goes unanswered." |
| Price | $497/month (no setup fee, no contract) |
| Your cost to deliver | ~$22–30/month per client |
| Margin | ~94% |
| Platform | Retell AI (primary) + Make.com + Twilio |
| Free credits to start | $10 (Retell) = ~140 demo minutes |
| Demo number | Set up in Vapi (free US number) |
| Onboarding time | 3–4 hours per client |
| Monthly maintenance | 1–2 hours per client |

---

*Document created: March 2026 | SmartBook AI Setup Guide v1.0*
