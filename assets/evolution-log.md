# Pipeline Evolution Log

Resources found, evaluated, and tracked. Updated by heartbeat.

---

## Installed ✅

### 9x Marketing Team Template (2026-03-04)
- **Source:** https://www.youtube.com/watch?v=7UaQB325EqU (58k views)
- **What:** 15 OpenClaw skills — competitor research, brand analysis, campaign planning, ad creation, Meta Ads publishing
- **Installed at:** /root/.openclaw/workspace/skills/marketing-team/
- **Skills:** ads-analyst, head-of-marketing, creative-director, performance-marketer, meta-ads-extractor, meta-ads-analyser, ad-creative-analysis, landing-page-analysis, website-brand-analysis, campaign-planner, ad-designer, scriptwriter, page-designer, frontend-design, meta-ads-publisher
- **Status:** Installed. Needs GEMINI_API_KEY + META credentials to activate ad pipeline
- **Next step:** Wolfgang gets free Gemini API key at aistudio.google.com/app/apikey → adds to .env → full pipeline active

---

## Queue (found, not yet implemented)

_Nothing queued yet._

---

## Rejected (reviewed, not worth implementing)

_Nothing rejected yet._

---

## Sources Monitored

| Source | Last checked | Frequency |
|---|---|---|
| go9x YouTube channel | 2026-03-04 | Every 48h |
| ClawhHub new skills | 2026-03-04 | Every 48h |
| r/ClaudeAI + r/OpenClaw | - | Every 48h |
| Hacker News "Show HN" | - | Every 48h |
| Product Hunt (AI tools) | - | Every 48h |

---

## Installed ✅ (2026-03-04 — Batch 2)

### 6 ClawhHub Skills
- **vapi-calls** — Orchestrate Vapi campaigns from Telegram
- **real-estate-lead-machine** — Auto-scrape Phoenix motivated sellers
- **ai-cold-email-machine** — AI-personalized outreach sequences
- **meta-ads** — Full Meta API control
- **afrexai-saas-metrics** — SaaS health dashboard
- **lead-hunter** — Auto-enriched leads for SmartBook/Wolfpack/UnitFix

### Vapi Webhook Handler
- Built at: /root/.openclaw/workspace/scripts/vapi-webhook.py
- Auto-logs call outcomes, flags warm leads (>90s), tracks quick hangups

## Queue (found, not yet implemented)

### n8n Cold Call Pipeline (Score: 9/10)
- Template: https://n8n.io/workflows/5008
- What: Reads leads from Google Sheets → fires Vapi calls → logs status → retries
- Setup: `docker run -d -p 5678:5678 n8nio/n8n` → import template
- Effort: 2hrs | Cost: $0

### Vapi End-of-Call → CRM Auto-Update (Score: 10/10)
- Webhook handler built, needs public URL (ngrok or Supabase Edge Function)
- Closes CRM loop on every call automatically
- Effort: 1hr | Cost: $0

### SmartBook AI — Vapi Dental/Gym Templates (Score: 8/10)
- Official Vapi templates at vapi.ai/library
- Upgrades Alex agent with production-tested dental system prompts
- Effort: 30min | Cost: $0

### Cal.com Voice Booking via n8n (Score: 8/10)
- Template: https://n8n.io/workflows/6895
- SmartBook AI calls → actually book appointments end-to-end
- Effort: 2hrs | Cost: $0

### Resendly Drip Sequences (Score: 8/10)
- Site: resend.ly
- Visual drip builder on top of existing Resend API key
- Adds proper onboarding sequences to PantryMate/UnitFix/FollowUpFox
- Effort: 1hr | Cost: $0
