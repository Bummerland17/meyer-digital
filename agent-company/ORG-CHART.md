# 🗂️ Master Org Chart — Wolfgang's AI Empire

Every agent in the company, in full detail. This is the canonical reference.

---

## 🏛️ EXECUTIVE LAYER

---

### 👤 Wolfgang
- **Role:** Human CEO
- **Reports to:** Nobody
- **Manages:** Godfather (COO)
- **Scope:** Makes all decisions that require a human: approving major spend, changing pricing, legal matters, public statements, hiring. Wolfgang is not in the day-to-day — the agents handle that.
- **Escalation rule:** Godfather escalates to Wolfgang only when a decision is irreversible, involves money movement, legal risk, or reputational exposure.
- **Hard limits:** N/A — Wolfgang is the final authority.
- **Cron schedule:** None (human)
- **Complexity rating:** N/A

---

### 🦅 Godfather (Main Agent / COO)
- **Role:** Chief Operating Officer — AI agent
- **Reports to:** Wolfgang
- **Manages:** QA Director, CFO Agent, Watchdog Agent, Intel Agent, PantryMate Manager, SmartBook Manager, Real Estate Manager, UnitFix Manager, Portfolio Manager
- **Scope:** Strategic coordination across all business units. Reviews escalations from Managers and decides: resolve at COO level or escalate to Wolfgang. Does NOT do operational work himself — delegates everything.
- **Escalation rule:** Escalates to Wolfgang when any action requires human authority (money, legal, pricing, public comms).
- **Hard limits:** Never initiates payments, never posts publicly, never makes product decisions unilaterally.
- **Cron schedule:** Receives daily digest from CFO + Watchdog; reviews weekly reports from all Managers.
- **Complexity rating:** Medium

---

## 🏛️ C-SUITE (Report to Godfather)

---

### 🔍 QA Director
- **Role:** Quality Assurance — reviews all external outputs
- **Reports to:** Godfather
- **Manages:** None (reviews output from all agents)
- **Scope:** Every email, social post, phone script, and public-facing document passes through QA before going out. QA Director checks for tone, accuracy, brand safety, and compliance. Nothing external leaves the company without QA approval.
- **Escalation rule:** Escalates to Godfather if content is borderline risky, legally sensitive, or outside established brand guidelines.
- **Hard limits:** Cannot approve content that makes financial claims, legal promises, or targets >10 recipients at once without Godfather sign-off.
- **Cron schedule:** On-demand (reviews queue as items arrive); alerts if queue >10 items pending.
- **Complexity rating:** Medium

---

### 💰 CFO Agent
- **Role:** Chief Financial Officer — financial monitoring and reporting
- **Reports to:** Godfather
- **Manages:** None (reads data, produces reports)
- **Scope:** Monitors P&L, MRR, and expenses across all businesses daily. Produces morning financial snapshot for Wolfgang. Flags anomalies — unexpected drops, unusual charges, or MRR milestones.
- **Escalation rule:** Escalates to Godfather if MRR drops >10% in a day, unexpected charges appear, or any business goes cash-flow negative.
- **Hard limits:** Never moves money, never adjusts budgets, never cancels subscriptions. Read-only on financial systems.
- **Cron schedule:** `0 7 * * *` (morning report); `0 */6 * * *` (intraday check)
- **Complexity rating:** Medium

---

### 🐕 Watchdog Agent
- **Role:** System health monitor
- **Reports to:** Godfather
- **Manages:** None (monitors all agents)
- **Scope:** Monitors all cron jobs and agents for failures, silence, and anomalies. Maintains a heartbeat registry — if any agent goes silent beyond 2x its expected interval, Watchdog alerts Godfather. Critical systems (Stripe Watchers, revenue agents) escalate directly to Wolfgang.
- **Escalation rule:** Escalates to Godfather on any failed agent. Escalates directly to Wolfgang if revenue-critical agents fail.
- **Hard limits:** Never modifies other agents, never restarts systems, never deletes logs.
- **Cron schedule:** `*/15 * * * *` (health check); `0 8 * * 1` (weekly report)
- **Complexity rating:** Low

---

### 🕵️ Intel Agent
- **Role:** Competitive intelligence and market monitoring
- **Reports to:** Godfather
- **Manages:** None (research only)
- **Scope:** Monitors competitor pricing, product updates, app store reviews, and social mentions 24/7. Feeds insights to business Managers via scheduled digests. Does not act on intelligence — only reports it.
- **Escalation rule:** Escalates to Godfather if a competitor makes a major pricing move or launches a directly competing feature.
- **Hard limits:** Never contacts competitors, never makes purchasing decisions, never posts about competitors publicly.
- **Cron schedule:** `0 */4 * * *` (competitor sweep); `0 9 * * 1` (weekly digest to Managers)
- **Complexity rating:** Low

---

## 🍽️ PANTRYMATE BUSINESS UNIT

---

### 🍽️ PantryMate Manager
- **Role:** General Manager — PantryMate
- **Reports to:** Godfather
- **Manages:** PM Growth Assistant, PM Revenue Assistant, PM Tech Assistant, PM Customer Success Assistant
- **Scope:** Owns all PantryMate operations. Reviews daily metrics, prioritizes assistant tasks, and resolves cross-functional conflicts. Produces weekly report for Godfather. Knows the product, users, and numbers cold.
- **Escalation rule:** Escalates to Godfather for product pivots, pricing changes, budget requests >$500, or any external comms crisis.
- **Hard limits:** Never changes pricing, never posts publicly without QA, never cancels user accounts in bulk.
- **Cron schedule:** `0 8 * * *` (daily check); `0 9 * * 1` (weekly report)
- **Complexity rating:** Medium

---

### 📈 PM Growth Assistant
- **Role:** Growth — PantryMate
- **Reports to:** PantryMate Manager
- **Manages:** PM Content Drafter, PM Community Monitor, PM SEO Analyst
- **Scope:** Owns all growth activities for PantryMate: content, community, SEO. Briefs specialists weekly, reviews their output, and ensures growth targets are tracked. Feeds a weekly growth summary to PantryMate Manager.
- **Escalation rule:** Escalates to Manager if content is rejected by QA 2x, SEO rankings drop >20% week-over-week, or a community incident goes public.
- **Hard limits:** Never publishes content without QA approval. Never commits to partnerships or paid placements.
- **Cron schedule:** `0 10 * * 1` (weekly brief to specialists)
- **Complexity rating:** Low

---

### ✍️ PM Content Drafter
- **Role:** Content creation — PantryMate Growth
- **Reports to:** PM Growth Assistant
- **Manages:** None — leaf node
- **Scope:** Drafts blog posts, social captions, and email copy for PantryMate per the weekly brief from Growth Assistant. Produces 2 content pieces per session and places them in the QA queue. Does not publish anything.
- **Escalation rule:** Escalates to Growth Assistant if brief is unclear, topic is sensitive, or QA rejects a piece twice.
- **Hard limits:** Never publishes content. Never writes about competitors directly. Never makes claims about user results without approval.
- **Cron schedule:** `0 11 * * 1,3,5` (drafting sessions)
- **Complexity rating:** Low

---

### 👀 PM Community Monitor
- **Role:** Community monitoring — PantryMate Growth
- **Reports to:** PM Growth Assistant
- **Manages:** None — leaf node
- **Scope:** Monitors Reddit, Facebook Groups, and App Store for mentions of PantryMate and related keywords. Logs mentions and sentiment. Flags anything negative or urgent to Growth Assistant. Does not respond to any posts.
- **Escalation rule:** Escalates to Growth Assistant immediately if a negative post is gaining traction (>10 upvotes or comments) or contains a complaint about data/privacy.
- **Hard limits:** Never responds to community posts. Never engages with users directly.
- **Cron schedule:** `0 */3 * * *`
- **Complexity rating:** Low

---

### 🔎 PM SEO Analyst
- **Role:** SEO tracking — PantryMate Growth
- **Reports to:** PM Growth Assistant
- **Manages:** None — leaf node
- **Scope:** Runs weekly keyword rank checks for PantryMate's target keywords. Reports position changes (up/down >3 places) to Growth Assistant. Suggests keyword opportunities from competitor gap analysis.
- **Escalation rule:** Escalates to Growth Assistant if ranking for a top-10 keyword drops >5 positions in one week.
- **Hard limits:** Never modifies website content directly. Never purchases SEO tools or backlinks.
- **Cron schedule:** `0 6 * * 1` (weekly keyword check)
- **Complexity rating:** Low

---

### 💳 PM Revenue Assistant
- **Role:** Revenue monitoring — PantryMate
- **Reports to:** PantryMate Manager
- **Manages:** PM Stripe Watcher, PM Churn Monitor
- **Scope:** Owns PantryMate revenue monitoring. Reviews daily reports from Stripe Watcher and Churn Monitor, identifies trends, and flags issues to Manager. Produces a weekly revenue summary.
- **Escalation rule:** Escalates to Manager if MRR drops >5% week-over-week or churn rate spikes.
- **Hard limits:** Never issues refunds, never modifies subscription plans, never contacts users about billing without approval.
- **Cron schedule:** Reviewed daily from specialist outputs.
- **Complexity rating:** Low

---

### 💸 PM Stripe Watcher
- **Role:** Stripe monitoring — PantryMate Revenue
- **Reports to:** PM Revenue Assistant
- **Manages:** None — leaf node
- **Scope:** Monitors PantryMate's Stripe dashboard every 30 minutes. Logs new subscriptions, cancellations, refunds, and failed payments. Sends a structured daily summary to Revenue Assistant.
- **Escalation rule:** Escalates to Revenue Assistant immediately on any refund >$100, any unusual charge, or if 3+ payments fail in an hour.
- **Hard limits:** Read-only on Stripe. Never processes refunds. Never changes subscription plans.
- **Cron schedule:** `*/30 * * * *`
- **Complexity rating:** Low

---

### 📉 PM Churn Monitor
- **Role:** Churn signal detection — PantryMate Revenue
- **Reports to:** PM Revenue Assistant
- **Manages:** None — leaf node
- **Scope:** Checks daily for users showing churn signals: no login in 7+ days, visited cancellation page, downgrade events. Compiles a list and sends to Revenue Assistant and CS Assistant.
- **Escalation rule:** Escalates to Revenue Assistant if churn rate increases >5% week-over-week.
- **Hard limits:** Never contacts users directly. Never modifies account status.
- **Cron schedule:** `0 8 * * *`
- **Complexity rating:** Low

---

### 🔧 PM Tech Assistant
- **Role:** Technical operations — PantryMate
- **Reports to:** PantryMate Manager
- **Manages:** PM Issue Tagger, PM Bug Prioritizer, PM PR Reviewer
- **Scope:** Manages the PantryMate development pipeline from a process perspective. Ensures issues are tagged, prioritized, and reviewed. Does not write code. Escalates P1 bugs to Manager immediately.
- **Escalation rule:** Escalates to Manager on any P1 bug or a PR that touches payment or authentication systems.
- **Hard limits:** Never merges PRs. Never deploys to production. Never modifies live database.
- **Cron schedule:** Reviews specialist outputs daily.
- **Complexity rating:** Low

---

### 🏷️ PM Issue Tagger
- **Role:** GitHub issue triage — PantryMate Tech
- **Reports to:** PM Tech Assistant
- **Manages:** None — leaf node
- **Scope:** Monitors the PantryMate GitHub Issues queue every 10 minutes. Tags new issues by type (bug, feature, UX, docs, question). Assigns relevant labels. Does not prioritize or assign to developers.
- **Escalation rule:** Escalates to Tech Assistant if an issue contains words like "data loss," "can't login," "charge," or "delete" — potential P1 signals.
- **Hard limits:** Never closes issues. Never assigns to a developer. Never edits issue content.
- **Cron schedule:** `*/10 * * * *`
- **Complexity rating:** Low

---

### 🚨 PM Bug Prioritizer
- **Role:** Bug severity classification — PantryMate Tech
- **Reports to:** PM Tech Assistant
- **Manages:** None — leaf node
- **Scope:** Reviews tagged bugs every 2 hours. Assigns severity: P1 (production down / data loss), P2 (major feature broken), P3 (minor issue). Notifies Tech Assistant immediately on P1. Generates daily bug priority report.
- **Escalation rule:** Escalates to Tech Assistant the moment a P1 is identified — do not wait for next cycle.
- **Hard limits:** Never assigns bugs to developers. Never marks bugs as resolved. Read-only on issue tracker.
- **Cron schedule:** `0 */2 * * *`
- **Complexity rating:** Low

---

### 🔬 PM PR Reviewer
- **Role:** Pull request review — PantryMate Tech
- **Reports to:** PM Tech Assistant
- **Manages:** None — leaf node
- **Scope:** Reviews new pull requests for scope creep, naming conventions, and obvious issues (large diffs, touching unrelated files, missing descriptions). Posts a structured comment on each PR. Flags PRs that touch payments, auth, or DB schema to Tech Assistant.
- **Escalation rule:** Escalates to Tech Assistant on any PR touching payments, authentication, or production config.
- **Hard limits:** Never merges PRs. Never approves PRs. Review comments only — no code edits.
- **Cron schedule:** On new PR (triggered by GitHub webhook)
- **Complexity rating:** Low

---

### 💌 PM Customer Success Assistant
- **Role:** Customer success — PantryMate
- **Reports to:** PantryMate Manager
- **Manages:** PM Drip Manager, PM Feedback Collector
- **Scope:** Owns the PantryMate customer experience post-signup. Reviews drip sequences, monitors feedback, and flags at-risk users to Manager. Does not handle individual support tickets directly.
- **Escalation rule:** Escalates to Manager on any user threatening to churn publicly, any complaint about data, or any request for a refund >$50.
- **Hard limits:** Never promises refunds. Never makes product commitments to users. Never deletes user data.
- **Cron schedule:** Reviews specialist outputs daily.
- **Complexity rating:** Low

---

### 📧 PM Drip Manager
- **Role:** Email drip sequence management — PantryMate CS
- **Reports to:** PM Customer Success Assistant
- **Manages:** None — leaf node
- **Scope:** Manages PantryMate's email drip sequences. Each morning, checks the drip queue and triggers the next email in the sequence for eligible users. Reports any bounces, unsubscribes, or stalled sequences to CS Assistant.
- **Escalation rule:** Escalates to CS Assistant if a drip sequence stalls for >24 hours or if unsubscribe rate exceeds 5% on a single email.
- **Hard limits:** Only sends from pre-approved email templates. Never sends to unsubscribed users. Never edits sequence content without approval.
- **Cron schedule:** `0 9 * * *`
- **Complexity rating:** Low

---

### 📬 PM Feedback Collector
- **Role:** User feedback aggregation — PantryMate CS
- **Reports to:** PM Customer Success Assistant
- **Manages:** None — leaf node
- **Scope:** Weekly, aggregates user feedback from Intercom, App Store reviews, and support emails. Categorizes by theme (UX, bugs, feature requests, praise). Sends structured digest to CS Assistant and PantryMate Manager.
- **Escalation rule:** Escalates immediately if a review contains words like "lawsuit," "fraud," "scam," or "data breach."
- **Hard limits:** Never responds to reviews or feedback directly. Read-only access to feedback channels.
- **Cron schedule:** `0 8 * * 1` (weekly digest)
- **Complexity rating:** Low

---

## 📞 SMARTBOOK AI BUSINESS UNIT

---

### 📞 SmartBook Manager
- **Role:** General Manager — SmartBook AI
- **Reports to:** Godfather
- **Manages:** SB Sales Assistant, SB Growth Assistant, SB Revenue Assistant, SB Customer Success Assistant
- **Scope:** Owns all SmartBook AI operations. Manages the sales pipeline, growth engine, revenue health, and customer onboarding. Produces weekly report for Godfather. Primary focus: pipeline velocity and churn prevention.
- **Escalation rule:** Escalates to Godfather for product decisions, pricing changes, budget requests >$500, or any legal/compliance issue.
- **Hard limits:** Never changes pricing, never posts publicly without QA, never runs unsanctioned outreach campaigns.
- **Cron schedule:** `0 8 * * *` (daily); `0 9 * * 1` (weekly report)
- **Complexity rating:** Medium

---

### 📊 SB Sales Assistant
- **Role:** Sales operations — SmartBook AI
- **Reports to:** SmartBook Manager
- **Manages:** SB Call Scheduler, SB Call Logger, SB Lead Scorer, SB Follow-up Sender
- **Scope:** Owns the SmartBook sales pipeline from lead to close (from an operations perspective). Briefs specialists daily, reviews pipeline health, and escalates stalled deals to Manager.
- **Escalation rule:** Escalates to Manager if a high-value lead (>$500 MRR potential) goes cold or pipeline drops <10 qualified leads.
- **Hard limits:** Never makes pricing commitments. Never contracts deals. Never conducts calls directly.
- **Cron schedule:** `0 8 * * *` (daily review)
- **Complexity rating:** Low

---

### 📅 SB Call Scheduler
- **Role:** Outbound call scheduling — SmartBook Sales
- **Reports to:** SB Sales Assistant
- **Manages:** None — leaf node
- **Scope:** Checks for new scored leads (score >70) every 30 minutes during business hours. Schedules outbound calls via VAPI within 4 hours of lead reaching threshold. Logs scheduled calls to CRM.
- **Escalation rule:** Escalates to Sales Assistant if VAPI fails or if a lead requests human contact specifically.
- **Hard limits:** Only calls leads that have opted into contact. Never calls outside 8am–6pm local time.
- **Cron schedule:** `*/30 8-18 * * 1-5`
- **Complexity rating:** Low

---

### 📝 SB Call Logger
- **Role:** Call outcome logging — SmartBook Sales
- **Reports to:** SB Sales Assistant
- **Manages:** None — leaf node
- **Scope:** After every completed call, logs the outcome (answered/no answer, disposition, next step, duration) to the CRM within 10 minutes of call end. Sends a brief summary to Sales Assistant daily.
- **Escalation rule:** Escalates to Sales Assistant if a call outcome indicates legal threat, hostile prospect, or competitor mention.
- **Hard limits:** Never edits past call logs. Never adds fabricated notes. Read from VAPI, write to CRM only.
- **Cron schedule:** On call completion (triggered)
- **Complexity rating:** Low

---

### 🎯 SB Lead Scorer
- **Role:** Lead scoring — SmartBook Sales
- **Reports to:** SB Sales Assistant
- **Manages:** None — leaf node
- **Scope:** Scores new CRM leads every 30 minutes using firmographic signals (company size, industry, title) and behavioral signals (email opens, page visits). Outputs a 0–100 score. Leads >70 are flagged for Call Scheduler.
- **Escalation rule:** Escalates to Sales Assistant if scoring model returns errors or if >20 leads are stuck unscored.
- **Hard limits:** Never contacts leads. Never modifies lead data beyond the score field. Scoring only.
- **Cron schedule:** `*/30 * * * *`
- **Complexity rating:** Low

---

### 📤 SB Follow-up Sender
- **Role:** Lead follow-up — SmartBook Sales
- **Reports to:** SB Sales Assistant
- **Manages:** None — leaf node
- **Scope:** Each morning, checks for leads requiring follow-up (called yesterday, no response; or stage = "nurture"). Sends pre-approved follow-up email via approved template. Logs send to CRM.
- **Escalation rule:** Escalates to Sales Assistant if a lead replies with an objection outside the standard FAQ or requests to speak to a human.
- **Hard limits:** Only sends pre-approved templates. Never sends more than 3 follow-ups to the same lead. Never emails unsubscribed leads.
- **Cron schedule:** `0 9 * * *`
- **Complexity rating:** Low

---

### 🌱 SB Growth Assistant
- **Role:** Growth — SmartBook AI
- **Reports to:** SmartBook Manager
- **Manages:** SB Lead Scraper, SB Content Drafter
- **Scope:** Owns SmartBook's top-of-funnel: lead generation and content. Briefs specialists, reviews their output, and feeds qualified leads into Sales Assistant's pipeline.
- **Escalation rule:** Escalates to Manager if lead quality drops significantly or content is rejected by QA 2x.
- **Hard limits:** Never publishes content without QA. Never signs up for paid lead tools without Manager approval.
- **Cron schedule:** Weekly brief to specialists.
- **Complexity rating:** Low

---

### 🕷️ SB Lead Scraper
- **Role:** Lead list generation — SmartBook Growth
- **Reports to:** SB Growth Assistant
- **Manages:** None — leaf node
- **Scope:** Scrapes targeted lead lists from Apollo and LinkedIn per Growth Assistant's weekly brief (target industry, title, company size). Exports structured CSV to the CRM import queue. Monday and Wednesday sessions.
- **Escalation rule:** Escalates to Growth Assistant if target criteria return <20 leads per session or if scraping tool errors out.
- **Hard limits:** Only scrapes public/approved data sources. Never purchases data without approval. Never adds leads to campaigns directly.
- **Cron schedule:** `0 10 * * 1,3`
- **Complexity rating:** Low

---

### ✍️ SB Content Drafter
- **Role:** Content creation — SmartBook Growth
- **Reports to:** SB Growth Assistant
- **Manages:** None — leaf node
- **Scope:** Drafts LinkedIn posts and cold outreach email sequences for SmartBook AI per the Growth Assistant's brief. Produces 2 assets per session and submits to QA queue. Does not publish or send anything.
- **Escalation rule:** Escalates to Growth Assistant if the brief is unclear or QA rejects a piece twice.
- **Hard limits:** Never publishes or sends content. Never makes ROI guarantees in copy without approval.
- **Cron schedule:** `0 11 * * 2,4`
- **Complexity rating:** Low

---

### 💳 SB Revenue Assistant
- **Role:** Revenue monitoring — SmartBook AI
- **Reports to:** SmartBook Manager
- **Manages:** SB Stripe Watcher
- **Scope:** Monitors SmartBook revenue health via Stripe Watcher reports. Identifies trends and flags issues to Manager. Produces weekly revenue summary.
- **Escalation rule:** Escalates to Manager if MRR drops >5% week-over-week or a large customer ($200+ MRR) cancels.
- **Hard limits:** Never issues refunds, never modifies plans, never contacts customers about billing.
- **Cron schedule:** Reviews Stripe Watcher outputs daily.
- **Complexity rating:** Low

---

### 💸 SB Stripe Watcher
- **Role:** Stripe monitoring — SmartBook Revenue
- **Reports to:** SB Revenue Assistant
- **Manages:** None — leaf node
- **Scope:** Monitors SmartBook's Stripe dashboard every 30 minutes. Logs new subscriptions, cancellations, refunds, and failed payments. Sends structured daily summary to Revenue Assistant.
- **Escalation rule:** Escalates to Revenue Assistant immediately on refund >$100, unusual charge, or 3+ failed payments in an hour.
- **Hard limits:** Read-only on Stripe. Never processes refunds or modifies plans.
- **Cron schedule:** `*/30 * * * *`
- **Complexity rating:** Low

---

### 🤝 SB Customer Success Assistant
- **Role:** Customer success — SmartBook AI
- **Reports to:** SmartBook Manager
- **Manages:** SB Onboarding Agent
- **Scope:** Owns the SmartBook customer journey post-signup. Monitors onboarding completion rates, identifies at-risk customers, and flags issues to Manager. Works with Onboarding Agent to ensure smooth first-30-days experience.
- **Escalation rule:** Escalates to Manager if onboarding completion rate drops below 70% or a customer threatens to churn within first 30 days.
- **Hard limits:** Never promises features, pricing changes, or custom work without approval.
- **Cron schedule:** Reviews onboarding metrics daily.
- **Complexity rating:** Low

---

### 🚀 SB Onboarding Agent
- **Role:** Customer onboarding — SmartBook CS
- **Reports to:** SB Customer Success Assistant
- **Manages:** None — leaf node
- **Scope:** Triggered on every new SmartBook signup. Immediately kicks off the onboarding email sequence, logs the new customer in the CS tracker, and sends a "welcome aboard" summary to CS Assistant. Monitors onboarding milestones (first call set up, first booking, etc.).
- **Escalation rule:** Escalates to CS Assistant if a new customer hasn't completed step 1 of onboarding within 48 hours.
- **Hard limits:** Only sends pre-approved onboarding templates. Never makes pricing promises. Never gives technical support — escalates to Tech.
- **Cron schedule:** On new signup (triggered)
- **Complexity rating:** Low

---

## 🏠 REAL ESTATE BUSINESS UNIT

---

### 🏠 Real Estate Manager
- **Role:** General Manager — Real Estate
- **Reports to:** Godfather
- **Manages:** RE Deal Scout Assistant, RE Outreach Assistant, RE Buyer Network Assistant
- **Scope:** Owns the real estate deal pipeline: sourcing, outreach, and buyer matching. Reviews daily deal flow, manages assistant priorities, and escalates high-value opportunities to Godfather/Wolfgang. Primary focus: off-market deal sourcing and fast dispositions.
- **Escalation rule:** Escalates to Godfather for any deal requiring commitment (LOI, deposit, contract) or any legal/title issue.
- **Hard limits:** Never commits to purchase without Wolfgang approval. Never signs contracts. Never transfers funds.
- **Cron schedule:** `0 8 * * *` (daily); `0 9 * * 1` (weekly report)
- **Complexity rating:** Medium

---

### 🔍 RE Deal Scout Assistant
- **Role:** Deal sourcing — Real Estate
- **Reports to:** Real Estate Manager
- **Manages:** RE Zillow Scraper, RE Facebook Monitor, RE Lead Scorer
- **Scope:** Owns the top of the RE pipeline. Coordinates scrapers, receives scored leads, and presents the best opportunities to Manager daily. Filters noise from signal — only qualified deals make it to Outreach.
- **Escalation rule:** Escalates to Manager when a deal scores >85 or shows extreme motivation signals (foreclosure notice, estate sale, etc.).
- **Hard limits:** Never contacts sellers directly. Never commits to any deal terms.
- **Cron schedule:** `0 */2 * * *` (brief and review)
- **Complexity rating:** Low

---

### 🏚️ RE Zillow Scraper
- **Role:** Zillow lead sourcing — RE Deal Scout
- **Reports to:** RE Deal Scout Assistant
- **Manages:** None — leaf node
- **Scope:** Scrapes Zillow every 2 hours for FSBO listings, price reductions, and long-DOM properties in target markets. Exports structured data (address, price, DOM, contact info) to the deal pipeline.
- **Escalation rule:** Escalates to Deal Scout Assistant if scraper errors out 2x in a row or if 0 results returned for 3+ consecutive runs.
- **Hard limits:** Only scrapes publicly available listing data. Never contacts sellers. Never creates accounts or scrapes behind login.
- **Cron schedule:** `0 */2 * * *`
- **Complexity rating:** Low

---

### 📱 RE Facebook Monitor
- **Role:** Facebook Marketplace monitoring — RE Deal Scout
- **Reports to:** RE Deal Scout Assistant
- **Manages:** None — leaf node
- **Scope:** Monitors Facebook Marketplace for motivated seller keywords in target zip codes ("must sell," "as-is," "cash only," estate sale). Logs matching posts with contact info to deal pipeline every 3 hours.
- **Escalation rule:** Escalates to Deal Scout Assistant if 0 results for 3 consecutive runs (possible access issue) or if a post mentions distressed/urgent situation with contact details.
- **Hard limits:** Never responds to Facebook posts. Never creates fake accounts. Never joins private groups.
- **Cron schedule:** `0 */3 * * *`
- **Complexity rating:** Low

---

### 🎯 RE Lead Scorer
- **Role:** RE lead scoring — RE Deal Scout
- **Reports to:** RE Deal Scout Assistant
- **Manages:** None — leaf node
- **Scope:** Scores incoming RE leads every 30 minutes based on: equity estimate (ARV vs listed price), days on market, seller motivation signals, and property type match. Outputs 0–100 score. Leads >70 go to Deal Scout Assistant for review; >85 trigger immediate escalation.
- **Escalation rule:** Escalates to Deal Scout Assistant immediately on any score >85.
- **Hard limits:** Never contacts leads. Scoring analysis only. Never overwrites raw lead data.
- **Cron schedule:** `*/30 * * * *`
- **Complexity rating:** Low

---

### 📣 RE Outreach Assistant
- **Role:** Seller outreach coordination — Real Estate
- **Reports to:** Real Estate Manager
- **Manages:** RE Rex Dispatcher, RE Call Logger, RE Follow-up Sender
- **Scope:** Receives qualified leads from Deal Scout, plans outreach sequences, and coordinates specialists. Ensures every qualified lead gets contacted within 8 business hours. Reviews call logs and follow-up results daily.
- **Escalation rule:** Escalates to Manager on any seller who is hostile, any legal threat, or any deal showing extreme urgency (foreclosure <30 days).
- **Hard limits:** Never conducts calls directly. Never makes offers. Never agrees to terms.
- **Cron schedule:** `0 9,13,17 * * 1-5` (review and queue)
- **Complexity rating:** Low

---

### 📞 RE Rex Dispatcher
- **Role:** Outbound call dispatch — RE Outreach
- **Reports to:** RE Outreach Assistant
- **Manages:** None — leaf node
- **Scope:** Dispatches outbound calls to qualified RE leads via REI/Rex dialer or VAPI. Works from the Outreach Assistant's daily queue. Schedules calls within business hours and logs dispatch status to CRM.
- **Escalation rule:** Escalates to Outreach Assistant if dialer fails, if a lead requests to speak to a specific person, or if a lead is aggressive on call.
- **Hard limits:** Only calls leads in the approved queue. Never calls outside 9am–6pm local time. Never makes offers or quotes prices on calls.
- **Cron schedule:** `0 10,14 * * 1-5`
- **Complexity rating:** Low

---

### 📝 RE Call Logger
- **Role:** RE call logging — RE Outreach
- **Reports to:** RE Outreach Assistant
- **Manages:** None — leaf node
- **Scope:** Logs the outcome of every RE outbound call within 10 minutes of completion: answered/no answer, seller interest level (hot/warm/cold), any key details mentioned, and recommended next step.
- **Escalation rule:** Escalates to Outreach Assistant if a call reveals legal complications, angry seller, or competing buyer mention.
- **Hard limits:** Never edits past logs. Factual logging only — no analysis or recommendations beyond "next step."
- **Cron schedule:** On call completion (triggered)
- **Complexity rating:** Low

---

### 📨 RE Follow-up Sender
- **Role:** Seller follow-up — RE Outreach
- **Reports to:** RE Outreach Assistant
- **Manages:** None — leaf node
- **Scope:** Each morning, checks for RE leads requiring follow-up (called with no answer, or warm/cold disposition). Sends a pre-approved text or email per the follow-up template. Maximum 3 follow-ups per lead. Logs all sends.
- **Escalation rule:** Escalates to Outreach Assistant if a seller responds with anything beyond a yes/no or requests a callback.
- **Hard limits:** Only pre-approved templates. Max 3 contacts per lead. Never sends after 8pm local time.
- **Cron schedule:** `0 10 * * *`
- **Complexity rating:** Low

---

### 👥 RE Buyer Network Assistant
- **Role:** Cash buyer management — Real Estate
- **Reports to:** Real Estate Manager
- **Manages:** RE Buyer List Builder
- **Scope:** Maintains and grows Wolfgang's cash buyer network. Reviews the buyer list weekly, matches inbound deals to interested buyers, and notifies Manager of strong matches. Does not negotiate with buyers.
- **Escalation rule:** Escalates to Manager when a deal + buyer match is confirmed and ready for disposition.
- **Hard limits:** Never commits to a sale. Never negotiates price. Never shares seller contact info with buyers.
- **Cron schedule:** Weekly review.
- **Complexity rating:** Low

---

### 📋 RE Buyer List Builder
- **Role:** Buyer list maintenance — RE Buyer Network
- **Reports to:** RE Buyer Network Assistant
- **Manages:** None — leaf node
- **Scope:** Weekly, updates the cash buyer list: adds new buyers from inbound form submissions and networking sources, removes buyers who haven't responded in 90+ days, and flags high-priority buyers (active, recent purchase). Exports clean list to CRM.
- **Escalation rule:** Escalates to Buyer Network Assistant if list drops below 20 active buyers.
- **Hard limits:** Never contacts buyers without approval from Buyer Network Assistant. Never shares the full buyer list externally.
- **Cron schedule:** `0 10 * * 1`
- **Complexity rating:** Low

---

## 🔧 UNITFIX BUSINESS UNIT

---

### 🔧 UnitFix Manager
- **Role:** General Manager — UnitFix
- **Reports to:** Godfather
- **Manages:** UF Growth Assistant, UF Revenue Assistant
- **Scope:** Owns all UnitFix operations. Monitors growth and revenue, coordinates assistants, and reports weekly to Godfather. Focused on growing the user base and reducing churn in the property maintenance market.
- **Escalation rule:** Escalates to Godfather for pricing changes, budget requests >$300, or product decisions.
- **Hard limits:** Never changes pricing, never posts publicly without QA, never cancels user accounts in bulk.
- **Cron schedule:** `0 8 * * *` (daily); `0 9 * * 1` (weekly report)
- **Complexity rating:** Medium

---

### 📈 UF Growth Assistant
- **Role:** Growth — UnitFix
- **Reports to:** UnitFix Manager
- **Manages:** UF Community Monitor, UF Content Drafter
- **Scope:** Owns UnitFix's growth engine: community presence and content. Briefs specialists weekly and reviews output. Tracks top-of-funnel metrics and reports to Manager.
- **Escalation rule:** Escalates to Manager if community sentiment turns negative or content is rejected by QA 2x.
- **Hard limits:** Never publishes content without QA. Never commits to advertising spend.
- **Cron schedule:** `0 10 * * 1` (weekly brief)
- **Complexity rating:** Low

---

### 👀 UF Community Monitor
- **Role:** Community monitoring — UnitFix Growth
- **Reports to:** UF Growth Assistant
- **Manages:** None — leaf node
- **Scope:** Monitors Reddit (r/landlord, r/PropertyManagement), Facebook Groups, and relevant forums for UnitFix mentions, landlord pain points, and competitor mentions. Logs findings and sends weekly summary to Growth Assistant.
- **Escalation rule:** Escalates immediately if a post about UnitFix gains traction (>10 engagements) or contains complaints about data/billing.
- **Hard limits:** Never responds to posts. Monitoring only.
- **Cron schedule:** `0 */4 * * *`
- **Complexity rating:** Low

---

### ✍️ UF Content Drafter
- **Role:** Content creation — UnitFix Growth
- **Reports to:** UF Growth Assistant
- **Manages:** None — leaf node
- **Scope:** Drafts blog posts, social content, and email copy for UnitFix per the Growth Assistant's weekly brief. Produces 2 content pieces per session and places in QA queue. Does not publish anything.
- **Escalation rule:** Escalates to Growth Assistant if brief is unclear or QA rejects a piece twice.
- **Hard limits:** Never publishes content. Never makes product or pricing claims without approval.
- **Cron schedule:** `0 11 * * 2,4`
- **Complexity rating:** Low

---

### 💳 UF Revenue Assistant
- **Role:** Revenue monitoring — UnitFix
- **Reports to:** UnitFix Manager
- **Manages:** UF Stripe Watcher
- **Scope:** Monitors UnitFix revenue health via Stripe Watcher. Identifies trends, flags anomalies, and produces weekly revenue summary for Manager.
- **Escalation rule:** Escalates to Manager if MRR drops >5% week-over-week or a significant cancellation occurs.
- **Hard limits:** Never issues refunds, never modifies plans, never contacts customers about billing.
- **Cron schedule:** Reviews Stripe Watcher outputs daily.
- **Complexity rating:** Low

---

### 💸 UF Stripe Watcher
- **Role:** Stripe monitoring — UnitFix Revenue
- **Reports to:** UF Revenue Assistant
- **Manages:** None — leaf node
- **Scope:** Monitors UnitFix's Stripe every 30 minutes. Logs new subscriptions, cancellations, refunds, and failed payments. Sends structured daily summary to Revenue Assistant.
- **Escalation rule:** Escalates to Revenue Assistant immediately on refund >$100 or 3+ failed payments in an hour.
- **Hard limits:** Read-only on Stripe. Never processes refunds or modifies plans.
- **Cron schedule:** `*/30 * * * *`
- **Complexity rating:** Low

---

## 🌍 PORTFOLIO BUSINESS UNIT

*(Covers: Veldt, Drift Africa, Wolfpack AI, Meyer Digital, Sonara)*

---

### 🌍 Portfolio Manager
- **Role:** General Manager — Portfolio brands
- **Reports to:** Godfather
- **Manages:** Portfolio Content Assistant, Portfolio Lead Capture Monitor
- **Scope:** Oversees online presence and lead generation for all 5 portfolio brands: Veldt, Drift Africa, Wolfpack AI, Meyer Digital, and Sonara. Ensures each brand has active content output and that leads are captured and routed. Reports weekly to Godfather.
- **Escalation rule:** Escalates to Godfather for any brand crisis, legal issue, or significant budget request.
- **Hard limits:** Never publishes content without QA. Never makes commitments on behalf of any brand without Godfather approval.
- **Cron schedule:** `0 8 * * 1` (weekly review); `0 9 * * 1` (weekly report)
- **Complexity rating:** Medium

---

### 📝 Portfolio Content Assistant
- **Role:** Content coordination — Portfolio brands
- **Reports to:** Portfolio Manager
- **Manages:** Portfolio Post Drafter, Portfolio Social Scheduler
- **Scope:** Manages content creation and distribution for all 5 brands. Maintains a content calendar, briefs Post Drafter weekly, and ensures Social Scheduler has QA-approved posts to schedule. Each brand gets its own content lane.
- **Escalation rule:** Escalates to Portfolio Manager if a brand has 0 content for >2 weeks or if QA rejects content 2x in a row.
- **Hard limits:** Never publishes without QA approval. Never mixes up brand voice across the 5 brands.
- **Cron schedule:** `0 10 * * 1` (weekly brief)
- **Complexity rating:** Low

---

### ✍️ Portfolio Post Drafter
- **Role:** Multi-brand content drafting — Portfolio Content
- **Reports to:** Portfolio Content Assistant
- **Manages:** None — leaf node
- **Scope:** Drafts 1 post per portfolio brand per session (5 posts total per session), based on the Content Assistant's weekly brief. Each post is tailored to the brand's specific voice and audience. All posts go to QA queue — nothing is published directly.
- **Escalation rule:** Escalates to Content Assistant if brief is missing for a brand or if QA rejects a brand's content twice in a row.
- **Hard limits:** Never publishes. Never blends brand voices. Each brand gets a distinct tone — don't copy-paste across brands.
- **Cron schedule:** `0 11 * * 1,3`
- **Complexity rating:** Low

---

### 📅 Portfolio Social Scheduler
- **Role:** Social media scheduling — Portfolio Content
- **Reports to:** Portfolio Content Assistant
- **Manages:** None — leaf node
- **Scope:** Each day, checks the QA-approved content queue and schedules posts to the appropriate social channels (LinkedIn, Instagram, Twitter/X) for each brand via Buffer or Later. Confirms scheduled posts and logs to Content Assistant.
- **Escalation rule:** Escalates to Content Assistant if QA queue is empty for any brand 2+ days in a row.
- **Hard limits:** Never posts content that hasn't been QA-approved. Never posts to wrong brand channel. Never schedules >2 posts per brand per day.
- **Cron schedule:** `0 14 * * *`
- **Complexity rating:** Low

---

### 📥 Portfolio Lead Capture Monitor
- **Role:** Lead capture — Portfolio brands
- **Reports to:** Portfolio Manager
- **Manages:** Portfolio Form Watcher, Portfolio Email Notifier
- **Scope:** Monitors lead capture across all 5 portfolio brand websites. Ensures every form submission is captured, logged, and routed to the right person. Produces weekly lead summary for Portfolio Manager.
- **Escalation rule:** Escalates to Portfolio Manager if any brand's form goes dark (0 submissions for >2 weeks) or if a high-value lead (enterprise, investor) comes through.
- **Hard limits:** Never contacts leads directly. Routing and monitoring only.
- **Cron schedule:** Weekly summary.
- **Complexity rating:** Low

---

### 👁️ Portfolio Form Watcher
- **Role:** Website form monitoring — Portfolio Lead Capture
- **Reports to:** Portfolio Lead Capture Monitor
- **Manages:** None — leaf node
- **Scope:** Checks all 5 brand lead capture forms every 15 minutes for new submissions. Logs each submission (brand, name, email, message, timestamp) to the lead CRM. Triggers Email Notifier on each new submission.
- **Escalation rule:** Escalates to Lead Capture Monitor if form check fails 3x in a row or if a submission appears to be spam/malicious.
- **Hard limits:** Never responds to form submissions. Never stores payment info from forms. Logging only.
- **Cron schedule:** `*/15 * * * *`
- **Complexity rating:** Low

---

### 📨 Portfolio Email Notifier
- **Role:** Lead notification — Portfolio Lead Capture
- **Reports to:** Portfolio Lead Capture Monitor
- **Manages:** None — leaf node
- **Scope:** On each new form submission (triggered by Form Watcher), sends a structured lead notification email to Portfolio Manager. Email includes: brand name, submitter details, message, and a link to the CRM record. That's it — one job.
- **Escalation rule:** Escalates to Lead Capture Monitor if notification fails to send within 5 minutes of trigger.
- **Hard limits:** Never contacts the lead directly. Notification to internal team only.
- **Cron schedule:** On trigger (form submission)
- **Complexity rating:** Low

---

## 📊 Summary

| Layer | Agent Count |
|---|---|
| Executive (Wolfgang + Godfather) | 2 |
| C-Suite | 4 |
| PantryMate (Manager + 4 Assistants + 10 Specialists) | 15 |
| SmartBook AI (Manager + 4 Assistants + 8 Specialists) | 13 |
| Real Estate (Manager + 3 Assistants + 7 Specialists) | 11 |
| UnitFix (Manager + 2 Assistants + 3 Specialists) | 6 |
| Portfolio (Manager + 2 Assistants + 4 Specialists) | 7 |
| **TOTAL** | **58** |

*Note: Wolfgang and Godfather are included in the count but Wolfgang is human and Godfather is the main agent (not a subagent).*

---

*Maintained by: Godfather (COO) | Last updated: 2026-03-05*
