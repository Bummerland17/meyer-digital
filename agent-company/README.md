# 🏢 Wolfgang's AI Business Empire — Agent Company HQ

Welcome to the operating system for Wolfgang's portfolio of AI-powered businesses. This directory is the single source of truth for every agent in the company.

---

## 🧭 How the Company Works

```
Wolfgang (Human CEO)
    └── Godfather (COO — main agent, strategy & coordination)
            ├── QA Director
            ├── CFO Agent
            ├── Watchdog Agent
            ├── Intel Agent
            ├── PantryMate Manager
            ├── SmartBook AI Manager
            ├── Real Estate Manager
            ├── UnitFix Manager
            └── Portfolio Manager
```

**Wolfgang** only makes decisions that require a human: approving large spend, changing pricing, public statements, legal matters.

**Godfather (COO)** handles everything else at the strategic level. He coordinates between business units, reviews escalations, and ensures the machine runs smoothly.

**Business Managers** own their P&L and operations. They know their domain cold and escalate only when truly stuck.

**Assistants** own a functional area within a business (Growth, Revenue, Tech, CS). They coordinate their specialists and report to their Manager.

**Specialists** do exactly ONE thing. They are fast, focused, and reliable. If a specialist is doing two things, split it into two specialists.

---

## 📁 File Structure

```
agent-company/
├── README.md                  ← You are here
├── ORG-CHART.md               ← Full org chart with every agent
├── ESCALATION-RULES.md        ← Universal escalation rulebook
├── CRON-SCHEDULE.md           ← All cron jobs across the company
└── agents/                    ← Individual agent instruction files
    ├── cfo-agent.md
    ├── qa-director.md
    ├── watchdog-agent.md
    ├── intel-agent.md
    ├── pantrymate-manager.md
    ├── pantrymate-*.md        ← PantryMate assistants & specialists
    ├── smartbook-manager.md
    ├── smartbook-*.md         ← SmartBook assistants & specialists
    ├── realestate-manager.md
    ├── realestate-*.md        ← Real Estate assistants & specialists
    ├── unitfix-manager.md
    ├── unitfix-*.md           ← UnitFix assistants & specialists
    ├── portfolio-manager.md
    └── portfolio-*.md         ← Portfolio assistants & specialists
```

---

## 🆕 How to Add a New Agent

1. **Define the scope** — what is the ONE thing this agent does? If you can't answer in one sentence, split it.
2. **Identify the parent** — which assistant or manager does it report to?
3. **Create the file** — copy the template below, fill in every section.
4. **Add to ORG-CHART.md** — add the agent in the correct position with all fields.
5. **Add cron if needed** — add to CRON-SCHEDULE.md with schedule + alert conditions.
6. **Brief the parent agent** — update the parent agent's `Manages` list.

### Agent File Template

```markdown
# [Agent Name]

## Role
[One-sentence job description]

## Reports To
[Parent agent name]

## Manages
[List of direct reports, or "None — leaf node"]

## Scope
[2-3 sentences on exactly what this agent handles]

## Daily Tasks
[Bulleted list of recurring actions]

## Escalation Rules
[Specific triggers that cause this agent to escalate]

## Hard Limits
[Things this agent NEVER does without approval]

## Tools Available
[List of tools/APIs this agent can use]

## Success Metrics
[How you know this agent is doing its job well]
```

---

## 🏢 How to Onboard a New Business Unit

When Wolfgang adds a new business to the empire:

1. **Create the Manager file** — `agents/[business]-manager.md`
2. **Identify the functional areas** — typically: Growth, Revenue, Tech (if SaaS), Customer Success
3. **Create Assistant files** for each functional area
4. **Create Specialist files** for each atomic task within each area
5. **Add the Manager to ORG-CHART.md** under Godfather
6. **Update CRON-SCHEDULE.md** with all scheduled tasks
7. **Inform Godfather** — he needs to know the new business exists and who the Manager is

---

## 🔒 Golden Rules

1. **Specialists do ONE thing.** No exceptions.
2. **Nothing external without QA approval.** Emails, posts, calls — all go through QA Director.
3. **Money moves require Wolfgang.** No agent initiates payments without human sign-off.
4. **Escalate early, not late.** When in doubt, escalate. Better a slow decision than a wrong one.
5. **Log everything.** If it's not logged, it didn't happen.
6. **Complexity rating max = Medium.** If an agent's work is High complexity, split the agent.

---

## 📊 Current Business Units

| Business | Manager | Status |
|---|---|---|
| 🍽️ PantryMate | PantryMate Manager | Active |
| 📞 SmartBook AI | SmartBook Manager | Active |
| 🏠 Real Estate | Real Estate Manager | Active |
| 🔧 UnitFix | UnitFix Manager | Active |
| 🌍 Portfolio (Veldt, Drift Africa, Wolfpack AI, Meyer Digital, Sonara) | Portfolio Manager | Active |

---

*Last updated: 2026-03-05 | Maintained by: Godfather (COO)*
