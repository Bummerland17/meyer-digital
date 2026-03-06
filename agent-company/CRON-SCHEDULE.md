# ⏰ Cron Schedule — Wolfgang's AI Empire

All scheduled jobs across every business unit. Each job is owned by exactly one agent.

---

## 🔑 Legend

- **Runtime** = expected execution time
- **Alert if** = condition that triggers Watchdog notification
- **Owner** = the agent responsible for the job

---

## 🏛️ C-Suite Jobs

| Agent | Schedule | What It Does | Runtime | Alert If |
|---|---|---|---|---|
| CFO Agent | `0 7 * * *` | Morning P&L snapshot — pulls revenue, expenses, MRR from all businesses, sends report to Wolfgang | 3–5 min | Fails, or MRR drops >5% vs prior day |
| CFO Agent | `0 */6 * * *` | Intraday revenue check — flags unusual spikes or drops in Stripe across all businesses | 1–2 min | Revenue drops >20% in 6h window |
| Watchdog Agent | `*/15 * * * *` | Health check — pings all active cron jobs and agents, checks last-run timestamps | 30 sec | Any agent silent >2x its expected interval |
| Watchdog Agent | `0 8 * * 1` | Weekly system health report to Godfather | 2 min | Report fails to generate |
| Intel Agent | `0 */4 * * *` | Competitor monitoring sweep — checks competitor pricing pages, app store reviews, social mentions | 5–10 min | Fails 2x in a row |
| Intel Agent | `0 9 * * 1` | Weekly intel digest — summarizes top competitor moves and market trends, sends to all Managers | 5 min | Fails to deliver |
| QA Director | On-demand | Reviews all flagged outgoing content before release | Variable | Queue >10 items pending |

---

## 🍽️ PantryMate Jobs

| Agent | Schedule | What It Does | Runtime | Alert If |
|---|---|---|---|---|
| PantryMate Manager | `0 8 * * *` | Daily status check — reviews overnight metrics, queues tasks for assistants | 2 min | Fails |
| PantryMate Manager | `0 9 * * 1` | Weekly review — assembles weekly report for Godfather | 5 min | Fails |
| PM Growth Assistant | `0 10 * * 1` | Kicks off weekly content planning — briefs Content Drafter and SEO Analyst | 2 min | Fails |
| PM Content Drafter | `0 11 * * 1,3,5` | Drafts 2 content pieces (blog/social) for QA queue | 10–15 min | Fails or drafts 0 pieces |
| PM Community Monitor | `0 */3 * * *` | Scans Reddit, FB Groups, App Store for PantryMate mentions | 3–5 min | Fails 2x in a row |
| PM SEO Analyst | `0 6 * * 1` | Weekly keyword rank check — reports changes to Growth Assistant | 5 min | Fails |
| PM Stripe Watcher | `*/30 * * * *` | Monitors PantryMate Stripe — flags new subscribers, cancels, refunds | 1 min | Any error; or revenue event unlogged |
| PM Churn Monitor | `0 8 * * *` | Checks for users approaching churn signals (no login >7d, downgrade events) | 2 min | Fails; or churn rate >5% wk-over-wk |
| PM Issue Tagger | `*/10 * * * *` | Polls GitHub Issues and tags by type (bug, feature, UX, etc.) | 1 min | Fails; untagged issues >20 |
| PM Bug Prioritizer | `0 */2 * * *` | Scans tagged bugs, assigns severity P1/P2/P3, notifies Tech Assistant if P1 | 2 min | P1 bug unactioned >1h |
| PM PR Reviewer | On new PR | Reviews PRs for scope, naming, and obvious issues. Flags for human review. | 3–5 min per PR | Fails to review within 30 min of PR open |
| PM Drip Manager | `0 9 * * *` | Checks drip queue, triggers next email for users in sequences | 2 min | Fails; or drip sequence stalls >24h |
| PM Feedback Collector | `0 8 * * 1` | Aggregates feedback from Intercom, App Store, email — sends digest to CS Assistant | 5 min | Fails |

---

## 📞 SmartBook AI Jobs

| Agent | Schedule | What It Does | Runtime | Alert If |
|---|---|---|---|---|
| SmartBook Manager | `0 8 * * *` | Daily status check — reviews pipeline, revenue, open tasks | 2 min | Fails |
| SmartBook Manager | `0 9 * * 1` | Weekly report to Godfather | 5 min | Fails |
| SB Sales Assistant | `0 8 * * *` | Reviews daily call queue, briefs Call Scheduler and Follow-up Sender | 2 min | Fails |
| SB Call Scheduler | `*/30 8-18 * * 1-5` | Checks for new leads ready to call, schedules outbound calls via VAPI | 1 min | Fails; lead waiting >4h |
| SB Call Logger | On call completion | Logs call outcome, duration, disposition to CRM | 1 min | Fails to log within 10 min of call end |
| SB Lead Scorer | `*/30 * * * *` | Scores new leads in CRM based on firmographic + behavioral signals | 2 min | Fails; leads unscored >1h |
| SB Follow-up Sender | `0 9 * * *` | Sends scheduled follow-up emails to leads (pre-approved templates) | 3 min | Fails; follow-up >24h overdue |
| SB Lead Scraper | `0 10 * * 1,3` | Scrapes target lead lists from Apollo/LinkedIn per Growth Assistant brief | 10–20 min | Fails 2x in a row |
| SB Content Drafter | `0 11 * * 2,4` | Drafts 2 LinkedIn/email outreach assets for QA queue | 10 min | Fails |
| SB Stripe Watcher | `*/30 * * * *` | Monitors SmartBook Stripe — flags new subs, cancels, refunds | 1 min | Error; or event unlogged |
| SB Onboarding Agent | On new signup | Triggers onboarding sequence for new SmartBook customers | 2 min | Fails; new user not onboarded within 15 min |

---

## 🏠 Real Estate Jobs

| Agent | Schedule | What It Does | Runtime | Alert If |
|---|---|---|---|---|
| RE Manager | `0 8 * * *` | Daily pipeline review — deals in progress, new leads overnight | 2 min | Fails |
| RE Manager | `0 9 * * 1` | Weekly report to Godfather | 5 min | Fails |
| RE Deal Scout Assistant | `0 */2 * * *` | Briefs scrapers, collects new potential deals, scores and queues | 3 min | Fails; queue empty >12h |
| RE Zillow Scraper | `0 */2 * * *` | Scrapes Zillow for off-market and FSBO listings in target markets | 5–10 min | Fails 2x in a row |
| RE Facebook Monitor | `0 */3 * * *` | Monitors Facebook Marketplace for motivated seller posts in target zip codes | 5 min | Fails 2x; or 0 results 3x in a row |
| RE Lead Scorer | `*/30 * * * *` | Scores incoming RE leads by equity, motivation signals, property type | 2 min | Fails; leads unscored >2h |
| RE Outreach Assistant | `0 9,13,17 * * 1-5` | Reviews scored leads, queues outreach tasks for Rex Dispatcher and Follow-up Sender | 2 min | Fails |
| RE Rex Dispatcher | `0 10,14 * * 1-5` | Dispatches outbound calls via REI/Rex dialer for qualified leads | 5 min | Fails; leads waiting >8h |
| RE Call Logger | On call completion | Logs RE call outcome and notes to CRM | 1 min | Fails to log within 10 min |
| RE Follow-up Sender | `0 10 * * *` | Sends follow-up texts/emails to leads per approved templates | 3 min | Fails; follow-up >48h overdue |
| RE Buyer List Builder | `0 10 * * 1` | Updates cash buyer list — adds new buyers from inbound leads, removes stale entries | 5 min | Fails |

---

## 🔧 UnitFix Jobs

| Agent | Schedule | What It Does | Runtime | Alert If |
|---|---|---|---|---|
| UnitFix Manager | `0 8 * * *` | Daily status check | 2 min | Fails |
| UnitFix Manager | `0 9 * * 1` | Weekly report to Godfather | 5 min | Fails |
| UF Growth Assistant | `0 10 * * 1` | Weekly content plan — briefs Content Drafter and Community Monitor | 2 min | Fails |
| UF Community Monitor | `0 */4 * * *` | Monitors Reddit, Facebook Groups, local forums for UnitFix mentions and landlord pain points | 5 min | Fails 2x in a row |
| UF Content Drafter | `0 11 * * 2,4` | Drafts 2 content pieces for UnitFix channels | 10 min | Fails |
| UF Stripe Watcher | `*/30 * * * *` | Monitors UnitFix Stripe — flags new subs, cancels, refunds | 1 min | Error; or event unlogged |

---

## 🌍 Portfolio Jobs

| Agent | Schedule | What It Does | Runtime | Alert If |
|---|---|---|---|---|
| Portfolio Manager | `0 8 * * 1` | Weekly portfolio review — health check across all 5 brands | 5 min | Fails |
| Portfolio Manager | `0 9 * * 1` | Weekly report to Godfather | 5 min | Fails |
| Port Content Assistant | `0 10 * * 1` | Weekly brief to Post Drafter and Social Scheduler per brand calendar | 3 min | Fails |
| Port Post Drafter | `0 11 * * 1,3` | Drafts posts for all 5 brands (1 per brand per session) for QA queue | 20–30 min | Fails; drafts <3 brands |
| Port Social Scheduler | `0 14 * * *` | Checks QA-approved posts, schedules to Buffer/Later for each brand | 5 min | Fails; post misses schedule window |
| Port Form Watcher | `*/15 * * * *` | Checks all 5 brand lead capture forms for new submissions | 1 min | Fails 3x; or submission unprocessed >30 min |
| Port Email Notifier | On new form submission | Sends new lead notification to Portfolio Manager with lead details | 1 min | Fails; notification delayed >5 min |

---

## 📊 Watchdog Monitoring Summary

The Watchdog Agent monitors ALL of the above. Alert thresholds by severity:

| Severity | Condition | Action |
|---|---|---|
| 🟡 Warning | Agent silent 2x its schedule interval | Log + notify Godfather |
| 🟠 High | Agent failed 3x in a row | Notify Godfather + flag in daily report |
| 🔴 Critical | Revenue agent down >30 min | Notify Godfather + Wolfgang immediately |
| 🔴 Critical | Watchdog itself fails | Fallback alert directly to Wolfgang |

---

*Maintained by: Godfather (COO) | Last updated: 2026-03-05*
