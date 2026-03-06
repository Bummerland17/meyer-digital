# PantryMate & Services — Daily Automation

---

## ⚙️ Operations Backbone (Auto-Running — DO NOT DELETE)

### Daily Quota Check
Every heartbeat: run `python3 /root/.openclaw/workspace/quotas/quota-tracker.py status`
→ If any quota is 0 by 6pm Namibia time (16:00 UTC) — alert Wolfgang with what's missing
→ To log work done: `python3 /root/.openclaw/workspace/quotas/quota-tracker.py log <metric> <count>`
   Metrics: apps_built, outreach_emails, social_posts, cold_calls, content_pieces

### Continuous Improvement Directive
Wolfgang's system gets better every week. The operations backbone runs automatically:
- 📋 Daily review: 21:00 UTC → Stripe MRR + calls + emails + GitHub → Telegram
- 📊 Weekly review: Sunday 18:00 UTC → WoW MRR, best channel, priorities → Telegram
- 🗓 Monthly review: 1st 08:00 UTC → full MRR rankings, kill/promote list → file
- 🛠 Tools radar: Monday 09:00 UTC → Brave search for new AI tools → alert if 8+
- 🌐 Site audit: Sunday 10:00 UTC → check all 9 sites for uptime/speed/CTA → Telegram
- 🏆 Monthly ranking: 1st 00:00 UTC → rank all products by MRR/growth/engagement

If any script errors appear in `/root/.openclaw/workspace/assets/ops-log.txt` — flag to Wolfgang.

### Weekly Tool Research Reminder
Every Monday: tools-radar.py runs automatically at 09:00 UTC.
If you spot a new high-value tool (score 8+) during a heartbeat — alert Wolfgang immediately.
Check: `tail -50 /root/.openclaw/workspace/research/tools-radar-log.md`

---

## Wolfgang is in Namibia (CAT = UTC+2). Jackson WY = UTC-7. 9hr difference.
## Jackson business hours (9am-5pm MST) = 6pm-2am CAT. Alert immediately on replies.

---

## Every heartbeat — check and act:

### 1. Gmail Monitoring (PRIORITY)
→ Check for replies to outreach emails (reputation + website clients)
→ If any reply received: draft response immediately, send it, alert Wolfgang on WhatsApp
→ Hot leads: Jackson SouthTown Hotel (3.4⭐, 1783 reviews) — most motivated
→ Follow-up: if no reply in 3 days, send follow-up email automatically

### 2. Stripe MRR Check
→ Pull current subscriber count + MRR
→ Compare vs target ($1,500 MRR by March 31)
→ Flag if new subscriber or lifetime deal purchase — alert Wolfgang immediately

### 3. Reddit Listening (brave-search)

**PantryMate** — r/mealplanning, r/Frugal, r/EatCheapAndHealthy, r/MealPrepSunday, r/zerowaste
Keywords: "what to make", "don't know what to cook", "food waste", "DoorDash", "pantry", "what's for dinner"
→ Find posts from last 48h ONLY
→ Draft helpful reply naturally positioning PantryMate (pantrymate.net)
→ Flag top 2 fresh posts with ready-to-paste reply for Wolfgang

**UnitFix** — r/Landlord, r/Landlords, r/realestateinvesting, r/PropertyManagement
Keywords: "maintenance requests", "tenant texts", "track maintenance", "property management app", "tenant communication", "repair requests"
→ Find posts from last 48h ONLY
→ Draft reply positioning UnitFix (unitfix.app) — landlord-to-landlord tone
→ Flag top 2 fresh posts with ready-to-paste reply

**Local SEO leads** — r/smallbusiness, r/Entrepreneur, r/restaurantowners
Keywords: "Google reviews", "bad reviews", "star rating", "reputation management"
→ Flag 1 thread per day with reply positioning Wolfgang's $400/mo service

→ Batch all flagged threads → send to Wolfgang on Telegram 2x/day (9am + 6pm Namibia time)

### 4. GitHub Issues
→ Check honest-eats for new issues in last 24h
→ Categorize: bug / UX / feature request
→ Flag critical bugs immediately

### 5. User Feedback Loop
→ Check issues tagged "ux" or "feedback"
→ If 3+ users report same issue → flag as priority fix
→ Draft fix on branch, send Wolfgang PR link

### 6. Email Queue (Timezone-Aware)
→ Run: `python3 /root/.openclaw/workspace/email-scheduler.py`
→ Sends pending emails from assets/email-queue.json ONLY during 8am-5pm local time (Mon-Fri)
→ Currently queued: 24 dental follow-ups (days 3 + 7 after initial outreach)

### 7. Daily TikTok Hook
→ One fresh hook based on trending dinner/frugal conversation
→ Generate ElevenLabs voiceover → save to assets/voiceovers/

### 7. March Pace Check
→ Target: 100 Pro Plus subscribers by March 31
→ Pull from Stripe, calculate daily pace needed
→ Flag if off pace

---

## Feedback → Improvement Pipeline
1. User reports issue → heartbeat catches it
2. I draft fix on branch → send Wolfgang PR link
3. Wolfgang approves → merge
4. Log in docs/changelog.md

---

### 6. Stripe Monitoring
→ Run on every heartbeat:
```
curl -s "https://api.stripe.com/v1/subscriptions?limit=100&status=active" \
  -u "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:"
```
→ Compare count to heartbeat-state.json (baseline: 1 sub, $14 MRR)
→ New sub detected → Telegram alert with customer email + plan + MRR
→ Update heartbeat-state.json with new numbers

---

### Business Factory (weekly, Sundays)

**Fast ROI rule: any business with $0 revenue past its `first_sale_deadline` gets killed. No exceptions.**

→ **Run scanner:** `python3 /root/.openclaw/workspace/business-factory/scanner.py`
   - Reviews top 3 opportunities from `opportunities.json`
   - If any score 8+ on ALL dimensions AND days_to_first_sale ≤ 7: run builder automatically
   - If score 7-8: flag for Wolfgang to review before building

→ **Run tracker:** `python3 /root/.openclaw/workspace/business-factory/tracker.py`
   - Checks Stripe revenue for all active businesses
   - Applies kill/keep/grow/invest criteria
   - Generates `performance-report.md`

→ **Check kill list first** — any businesses past `first_sale_deadline` with $0 → kill immediately (archive repo, deactivate Stripe product, mark `"killed"` in active-businesses.json)

→ **Execute grow/invest actions** for businesses hitting milestones (see README for action lists)

→ **Report to Wolfgang:**
   - New businesses built this week (name, URL, Stripe link)
   - Performance of existing ones (MRR, days live, trajectory)
   - Any kills executed and why
   - Top 3 new opportunities if score 8+

**Active businesses to watch (first_sale_deadline: 2026-03-11):**
- AI Sales Script Bundle → day1: post in r/sales with 3 free example prompts
- Landlord Maintenance Kit → day1: post in r/Landlord, offer Notion board free
- App Launch Playbook → day1: post in r/SideProject + r/indiehackers

---

## Weekly Feedback Loop (Fridays only)

Check today's day first — only run if it's Friday.

```bash
python3 /root/.openclaw/workspace/feedback-loop/feedback-tracker.py
python3 /root/.openclaw/workspace/feedback-loop/improvement-engine.py
python3 /root/.openclaw/workspace/feedback-loop/auto-apply.py
```

After running, read `/root/.openclaw/workspace/feedback-loop/latest-summary.txt`
and send Wolfgang the contents as a Telegram message, prefixed with:
"🔄 **Weekly Feedback Loop Report**"

Example message format:
```
🔄 Weekly Feedback Loop Report

✅ 3 improvements queued, 1 auto-applied
📞 Call hangup rate improved from 42% → 31% (Scribe script is working)
💰 Stripe: 8 subs | $112/mo MRR (+$14 vs last week)

Full task queue in improvement-queue.md — 2 items need your review.
```

If any HIGH priority tasks exist in improvement-queue.md, alert immediately regardless of day.

---

### 6. Pipeline Evolution (every 48h — check lastEvolutionCheck in heartbeat-state.json)
Scan for new tools, tutorials, skills that improve the system.

Sources:
- Brave search: "clawdbot tutorial template 2026"
- Brave search: "openclaw new skills site:clawhub.com"  
- go9x.com for new releases (they built the 15-skill marketing team we installed)
- ClawhHub: `node /usr/lib/node_modules/openclaw/skills/clawhub/clawhub.js search "automation"`

Score anything found (1-10): relevance + additive + buildable
→ Score 8+: Telegram alert immediately with what + why + how to implement
→ Score <8: log to /root/.openclaw/workspace/assets/evolution-log.md for later review

**Installed skills:** /root/.openclaw/workspace/skills/marketing-team/ (15 skills, 9x template, 2026-03-04)
- Needs GEMINI_API_KEY (free at aistudio.google.com) + META_ACCESS_TOKEN to activate full ad pipeline
- Ready NOW (no keys): ads-analyst, landing-page-analysis, website-brand-analysis

---

## n8n Automation Stack (set up 2026-03-04)

**n8n dashboard:** http://localhost:5678 (user: wolfgang / Bummerland20)
**Status:** Running via Docker (`docker ps` to check, `docker start n8n` to restart)

**4 workflow files** at `/root/.openclaw/workspace/n8n-workflows/` — import via n8n UI:
1. `workflow-1-vapi-crm.json` — Vapi call end → warm lead detection → Telegram alert → follow-up queue
2. `workflow-2-lead-to-call.json` — Google Sheets new lead → validate → Vapi auto-call (needs phoneNumberId + Sheet ID)
3. `workflow-3-stripe-alert.json` — Stripe checkout → Telegram alert + Resend welcome email (needs Resend API key)
4. `workflow-4-email-reply-monitor.json` — Every 30min → Zoho IMAP → human reply filter → Telegram alert (needs IMAP creds)

**Credentials to add in n8n:**
- Telegram Bot (token in credentials/)
- Google Sheets OAuth2 (for workflow 2)
- Stripe webhook secret (for workflow 3)
- Zoho IMAP (host: imap.zoho.com, port: 993, TLS)
- Resend API key (for workflow 3 drip)

**Vapi webhook handler:** `python3 /root/.openclaw/workspace/scripts/vapi-webhook.py` (port 8765)
- All 5 Vapi assistants updated to POST end-of-call reports to http://localhost:8765
- Warm leads logged to assets/warm-leads.json, results to assets/call-results-live.json

**Start all services:** `/root/.openclaw/workspace/scripts/start-services.sh`

---

## Output:
- New Stripe subscriber: Telegram alert immediately 🎉 ("New subscriber! [email] signed up for [plan] — MRR now $X")
- New email reply from client: Telegram alert IMMEDIATELY
- Reddit opportunities: batch 2x/day
- New high-value resource (8+/10): Telegram alert immediately
- Urgent bug: Telegram alert immediately
- Routine: HEARTBEAT_OK
