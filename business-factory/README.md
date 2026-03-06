# Business Factory

**Unified factory system.** Give it any idea → it scores, routes to the right pipeline, and executes automatically.

```
router.py "any idea"
    ↓
Score (demand + buildability + revenue speed)
    ↓
≥7 → auto-invoke pipeline   5-6 → research brief   <5 → explain + pivots
    ↓
course-pipeline.py  |  builder.py  |  (future pipelines)
    ↓
products/[slug]/  ←  outline, scripts, sales page, Gumroad listing, marketing assets
```

## The golden rule

**If a business can't make its first sale within 7 days of launch, we don't build it.**

Speed of validation matters as much as potential ceiling. A business that earns $1 in 7 days is more valuable to this system than a business with "huge potential" that earns $0 in 30.

---

## Unified Factory System

```
router.py "idea"
   ↓ GPT-4o scoring
   ├── factory_type: course       → course-pipeline.py
   ├── factory_type: digital_product → builder.py
   ├── factory_type: app          → builder.py
   └── factory_type: service      → builder.py (spec saved to seeds/)
```

All runs logged to `factory-log.json`. Research briefs saved as `research-brief-[slug].md`.

### Usage

```bash
# Route any idea
python3 router.py "AI productivity course for freelancers"
python3 router.py "Notion template bundle for real estate investors"
python3 router.py "Automated invoice tool for solopreneurs" --dry-run

# Build a course directly
python3 course-pipeline.py "Course Title" --audience "who it's for" --price 97

# Weekly scanner (unchanged)
python3 scanner.py

# Track revenue
python3 tracker.py
```

---

## Original Factory Flow

```
scanner.py → opportunities.json → builder.py → GitHub Pages + Stripe → tracker.py → keep/kill/grow
```

### 1. Scout (scanner.py)
Runs weekly on Sundays. Searches Reddit for pain points across r/entrepreneur, r/smallbusiness, r/freelance, r/SideProject, r/passive_income. Validates each idea against Brave Search to check competition. Scores on four dimensions (1–10 each):

- **Demand evidence** — upvotes, comment count
- **Simplicity** — can it be a landing page + Stripe?
- **Autonomy** — can it run with zero human involvement?
- **Revenue ceiling** — $500+/month potential?

**Hard filters:**
- All four scores must be 7+
- `days_to_first_sale` estimate must be ≤ 14 days
- There must be a specific community to post in on day 1 (not "hope SEO works")

Results saved to `opportunities.json`.

### 2. Builder (builder.py)
Takes an approved spec and:
1. Creates a Stripe product + price + payment link via API
2. Builds a clean, minimal landing page HTML (no AI slop)
3. Deploys to `bummerland17.github.io/{slug}` via GitHub Contents API
4. Logs entry to `active-businesses.json`

### 3. Tracker (tracker.py)
Checks Stripe revenue for all active businesses and applies milestone criteria:

| Milestone | Keep if | Kill if | Action |
|-----------|---------|---------|--------|
| Day 7 | Any sale | $0 (Fast ROI rule) | KILL immediately |
| Day 30 | MRR > $50 | MRR = $0 | KEEP or KILL |
| Day 60 | MRR > $200 | MRR < $50 | GROW or KILL |
| Day 90 | MRR > $500 | — | INVEST |

GROW actions: SEO, case study posts, ProductHunt submission, affiliate incentive.
INVEST actions: Gumroad listing, AppSumo, lifetime deal, paid ads test, newsletter sponsorship.

Report saved to `performance-report.md` after each run.

---

## Fast ROI filter — must pass ALL before building

1. **Build cost:** $0 (GitHub Pages + free Stripe = always $0)
2. **Time to build:** under 4 hours
3. **Realistic first sale within 7 days:**
   - There's a specific community to post in on day 1 (not "hope SEO works")
   - Price is in the $9–49 impulse-buy range
   - OR there's an existing warm audience (email list, active community)
4. **Break-even:** 1 sale covers all costs (cost is $0, so literally 1 sale = profitable)

If `days_to_first_sale` estimate > 14 → rejected, regardless of other scores.

---

## File structure

```
business-factory/
├── router.py               # 🆕 Master orchestrator — routes any idea to the right pipeline
├── course-pipeline.py      # 🆕 Course factory — outline, scripts, sales page, marketing
├── scanner.py              # Weekly Reddit scanner (now includes factory_type in scores)
├── builder.py              # Landing page + Stripe + GitHub deployer (digital products/apps)
├── tracker.py              # Revenue tracker + kill/keep/grow engine
├── factory-log.json        # 🆕 Log of every idea routed + decision made
├── opportunities.json      # Scanner output (all opportunities, qualified + rejected)
├── active-businesses.json  # Live businesses with full metadata
├── performance-report.md   # Latest weekly tracker report
├── seeds/                  # JSON specs for seed businesses
│   ├── ai-sales-script-bundle.json
│   ├── landlord-maintenance-templates.json
│   └── app-launch-playbook.json
├── products/               # 🆕 Course output directory
│   └── [course-slug]/
│       ├── outline.md / outline.json
│       ├── scripts/module-01/  (lesson scripts)
│       ├── sales-page.md
│       ├── gumroad-listing.md
│       └── marketing/
│           ├── twitter-posts.md
│           ├── linkedin-posts.md
│           ├── email-broadcasts.md
│           ├── youtube-description.md
│           └── hackernews-post.md
├── sites/                  # Local copies of deployed landing pages
└── README.md
```

---

## Adding a new business manually

1. Create a spec JSON (see template below)
2. Run `python3 builder.py --file your-spec.json`
3. Builder handles Stripe, HTML, GitHub Pages, and logging

### Spec template

```json
{
  "slug": "my-product",
  "name": "My Product Name",
  "tagline": "One-sentence hook — the above-fold headline",
  "problem": "The specific pain point this solves. Be concrete.",
  "solution": "What they actually get when they buy. Be specific.",
  "price": 29.00,
  "price_type": "one-time",
  "category": "digital-product",
  "bullets": [
    "Specific thing they get",
    "Another specific thing",
    "Third thing"
  ],
  "guarantee": "Refund terms — keep it simple.",
  "day1_launch_plan": "Exactly where to post on day 1 (specific subreddit, community, email list)",
  "expected_first_sale": "Honest estimate — days, not 'soon'",
  "fast_roi_estimate_days": 3
}
```

---

## Success and kill criteria

### The 7-day rule (non-negotiable)
If a business has $0 revenue by its `first_sale_deadline` (launch date + 7 days), it gets killed. No exceptions, no extensions. The whole point is fast validation.

### The 30-day checkpoints

| Day | Revenue needed to survive | Action if met | Action if not |
|-----|---------------------------|---------------|---------------|
| 30 | MRR > $50 | KEEP — it's working | KILL — move on |
| 60 | MRR > $200 | GROW — add fuel | KILL |
| 90 | MRR > $500 | INVEST — scale it | Continue watching |

### What KILL means in practice
- Archive the GitHub repo (don't delete — keep for reference)
- Deactivate the Stripe product (don't delete — preserves history)
- Mark status `"killed"` in active-businesses.json
- Write one line in performance-report.md on why

---

## Weekly review process (Heartbeat — Sundays)

1. Run `python3 scanner.py` — find new opportunities
2. Review top 3 from `opportunities.json`
3. If score 8+ on all dimensions: run `python3 builder.py --file spec.json`
4. Run `python3 tracker.py` — check all active businesses
5. Review `performance-report.md`
6. Execute any kills, grow actions, or invest decisions
7. Report to Wolfgang: new builds, performance updates, kills

---

## Active businesses (as of launch)

| Business | URL | Price | Stripe | Kill if no sale by |
|----------|-----|-------|--------|-------------------|
| AI Sales Script Bundle | [bummerland17.github.io/ai-sales-script-bundle](https://bummerland17.github.io/ai-sales-script-bundle) | $49 | [Buy](https://buy.stripe.com/00w8wO6kY5ZOaQn016bsc08) | 2026-03-11 |
| Landlord Maintenance Kit | [bummerland17.github.io/landlord-maintenance-templates](https://bummerland17.github.io/landlord-maintenance-templates) | $9 | [Buy](https://buy.stripe.com/9B6aEWfVyewk5w35lqbsc09) | 2026-03-11 |
| App Launch Playbook | [bummerland17.github.io/app-launch-playbook](https://bummerland17.github.io/app-launch-playbook) | $29 | [Buy](https://buy.stripe.com/eVq3cueRu3RGf6DcNSbsc0a) | 2026-03-11 |

---

## Notes on the Stripe key

The key in use is a **restricted live key** (`rk_live_...`). It currently has permissions to create products, prices, and payment links. It does **not** have permission to issue refunds — those need to be done manually in the Stripe dashboard.

If Stripe API calls start failing, check the key's permissions at: https://dashboard.stripe.com/apikeys
