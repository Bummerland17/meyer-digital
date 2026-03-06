# App Launch Playbook: From Idea to $1k MRR
**The exact process used to launch multiple apps — validated, built, and marketed without a traditional dev team**

---

## Who This Is For

You have an app idea. You're not a developer, or you are but you don't want to spend 6 months building something nobody wants. You want to validate fast, build lean, and get to paying customers before you burn out or run out of money.

This is what actually worked. Real numbers, real timelines, real mistakes.

---

## The Stack (What You'll Use)

| Tool | Purpose | Cost |
|------|---------|------|
| ChatGPT / Claude | Ideation, copy, research | $20/mo |
| Scout (or similar AI validator) | Market research & validation | Free–$49/mo |
| Lovable.dev | App builder (no-code/AI) | $25–$100/mo |
| Supabase | Backend, database, auth | Free tier |
| Stripe | Payments | 2.9% + $0.30 per transaction |
| Product Hunt | Launch day traffic | Free |
| AppSumo | Lifetime deal launch | Revenue share |
| GoHighLevel / Instantly | Outreach & pipeline | $97/mo |

Total monthly cost at launch: ~$150-200

---

## Phase 1: Validate Before You Build (Week 1-2)

This is the step most people skip. Don't.

### What You're Actually Validating

You need to know three things before writing a single line of code (or prompting a single line):
1. Do people have this problem?
2. Are they currently paying to solve it?
3. Will they pay YOU to solve it?

### The 48-Hour Validation Process

**Day 1: Reddit + Google Mining**

Search Reddit for your problem. Not your solution — the problem.

Example: If you're building a maintenance tracker for landlords, search:
- "landlord maintenance tracking reddit"
- "how do landlords track repairs"
- "property management spreadsheet"

Look for posts with 50+ upvotes and comments where people describe workarounds. If people have built their own spreadsheet hacks to solve the problem, that's a green flag.

**Day 2: Competitor Analysis**

Search Google for "[your solution] software" and "[your problem] app."

List every competitor. Note:
- Pricing (what's the cheapest tier?)
- Reviews (what do they complain about on G2/Capterra?)
- Traffic (use SimilarWeb free tier for rough estimates)

If there are 3+ competitors charging $30+/mo and their reviews mention missing features or bad UX — you have a gap to fill.

**Day 3: The Landing Page Test (Optional but Powerful)**

Build a one-page landing page with a "Join Waitlist" CTA. Run $50 in Google Ads targeting your exact keyword. If you get 20+ email signups in 48 hours, you have demand.

If you get zero — either the problem isn't urgent, or your messaging is off. Figure out which.

### Using AI for Validation

Prompt for Claude/ChatGPT:

```
I want to build [your app idea]. 

Research the following and give me honest answers:
1. What are the top 5 existing solutions in this space and their pricing?
2. What do their negative reviews say (based on what you know)?
3. What's the realistic market size for this problem?
4. What would make someone switch from a spreadsheet or existing tool to something new?
5. What's a realistic price point that solves the problem without scaring buyers?

Be direct. Tell me if this is a bad idea.
```

---

## Phase 2: Build the MVP (Week 2-4)

### Use Lovable to Build, Not Code

Lovable.dev is an AI app builder that generates real React + Supabase applications from plain English descriptions. It's not a no-code toy — it produces real, deployable code.

**The Right Way to Prompt Lovable**

Don't say: "Build me an app for landlords"

Say:
```
Build a web app with the following features:

1. User authentication (email/password) via Supabase
2. A maintenance request form with fields: property address, unit number, issue description, priority (low/medium/high), date submitted
3. A dashboard showing all open requests sorted by priority
4. Status updates: Open → In Progress → Resolved
5. A contractor directory where users can save name, phone, trade (plumber, electrician, etc.)
6. Export to CSV

Design: Clean, mobile-responsive. Use Tailwind CSS. Primary color: #2563EB.

No AI features needed. Just a solid CRUD app with good UX.
```

**What Lovable Is Bad At**

- Complex business logic with many edge cases
- Real-time features (it works, but gets messy)
- Anything requiring custom integrations out of the box

Plan around these limitations. Ship what works, improve later.

### Connect Stripe in 20 Minutes

1. Create a Stripe account
2. Go to Products → Add Product → set your price
3. Copy the Payment Link
4. Drop it on your landing page/app as "Subscribe" button

That's it. You don't need a custom Stripe integration for your first 50 customers. Payment links work.

### What Your MVP Needs (And Doesn't)

**Needs:**
- The core thing that solves the problem (one feature, done well)
- User signup / login
- A way to pay

**Doesn't need:**
- Mobile app
- API
- Integrations
- Admin dashboard
- Analytics

Ship without those. Add them when customers ask.

---

## Phase 3: Launch Day (Week 4-6)

### Product Hunt Launch

Product Hunt works. Not as a magic traffic generator, but as a credibility signal and a concentrated burst of early adopters.

**Preparation (2 weeks before)**

1. Create your Product Hunt profile if you haven't
2. Build a maker community: comment on 10 other products/day for 2 weeks — this warms the algorithm
3. Line up 20-30 people who will upvote you on launch day (this is normal — everyone does it)
4. Write your tagline: "[App Name] — [one-sentence problem statement]" (not a feature list)

**Launch Day**

- Post at 12:01 AM Pacific (that's when the daily ranking resets)
- Post your launch in 3-5 relevant Slack communities / Discord servers in the first 2 hours
- Text/DM your 20-30 upvote contacts personally — "Hey, launching today, would mean a lot if you could check it out: [link]"
- Respond to EVERY comment, even one-word ones

**What to Expect**

Realistic outcomes for a first-time PH launch with effort:
- Top 10 of the day: 200-600 visitors
- Signups: 5-15% conversion
- Paying customers from PH alone: 2-10

That's not a lot. But it's not the point. PH gives you:
- Social proof ("Featured on Product Hunt")
- Your first unfiltered feedback
- A few early adopters who will tell you what's broken

### AppSumo Launch (Optional, High-Risk/High-Reward)

AppSumo sells lifetime deals to their 1M+ subscriber audience. A successful AppSumo launch can bring in $20k-$200k in a few weeks.

The catch: you're selling lifetime access at a steep discount ($49-$99 one-time vs. $30/mo). This is a tradeoff — cash now vs. recurring revenue later.

**When AppSumo Makes Sense**
- Your app is mostly stable (bugs kill AppSumo launches)
- You need cash to build out features
- Your niche is something AppSumo's audience would buy (software tools, productivity, SaaS)

**How to Apply**
- Go to appsumo.com/sell
- Fill out the form — they'll get back to you in 1-4 weeks
- Be honest about MAUs, revenue, and what makes you different

**The AppSumo Gauntlet**

If you get accepted, expect:
- 300-800 support tickets in the first week
- Feature requests that weren't on your roadmap
- A few refund requests (3-5% is normal)
- And also: real cash, real users, and real feedback

Hire a VA for support before AppSumo launches. Non-negotiable.

---

## Phase 4: Get to $1k MRR (Week 6-12)

### The Honest Math

$1k MRR at $29/mo = 35 customers
$1k MRR at $49/mo = 21 customers
$1k MRR at $9/mo = 112 customers

Pick your price point accordingly. $29-49/mo is the sweet spot for solo operators — low enough to not require a committee decision, high enough to matter.

### What Actually Gets You Customers

**1. Outbound (Fastest)**

Use Instantly.ai or a similar tool to run cold email campaigns. Build a list of your target customer from Apollo, LinkedIn Sales Nav, or hand-research.

A cold email that works:
```
Subject: [Specific problem] — [Business Name]

Hi [Name],

I noticed [specific thing about their business that relates to the problem].

We built [App Name] specifically for [their type of business] — it handles [core problem] without [common workaround they're probably using].

If that's relevant, I can send you a 2-minute video walkthrough. No demo call required.

[Your name]
```

Expect: 5-10% reply rate, 2-4% trial conversion. At 100 emails/day, that's 2-4 trials/day.

**2. Content + SEO (Slowest Start, Best Long-Term)**

Write 10-20 landing pages targeting long-tail keywords your customers search. "maintenance request tracker for landlords" gets real searches from real landlords with real credit cards.

Use Lovable or Webflow to build these pages. Each one is a 24/7 salesperson.

**3. Reddit + Communities (Free, High-Intent)**

Find the 3-5 subreddits and Facebook groups where your customers hang out. Spend 30 minutes/day being genuinely helpful. Don't pitch. After 2-3 weeks of real participation, mention your tool when relevant.

This converts at a higher rate than ads because the trust is already there.

**4. Partnership Outreach**

Find complementary tools/services and propose simple cross-promotions:
- Guest in their newsletter
- Affiliate deal (30% lifetime commission works well)
- Bundle offer

One good partnership can deliver 20-50 signups in a week.

### Milestone Targets

| Week | Goal |
|------|------|
| Week 1-2 | Validated idea, landing page live |
| Week 3-4 | MVP built, 5 beta users |
| Week 5-6 | PH launch, first 10 paying customers |
| Week 7-8 | $300-500 MRR, product stable |
| Week 9-10 | Outbound running, content live |
| Week 11-12 | $1,000 MRR |

These are achievable. They're not guaranteed. The difference between people who hit $1k MRR in 12 weeks and people who don't is usually one thing: they talk to customers every week.

---

## Mistakes I Made (So You Don't Have To)

**Building before validating.** Spent 3 weeks building a feature nobody asked for. The validation step takes 2 days. There is no excuse to skip it.

**Pricing too low.** $9/mo feels safe. It isn't. At $9/mo you need 112 customers to hit $1k MRR. At $29/mo you need 35. Lower price doesn't mean more customers — it means less money and more support tickets.

**Waiting for "done."** The version that converts is never the polished version in your head. Ship something that solves the core problem and nothing else.

**Ignoring churn.** Getting to $1k MRR means nothing if you're at 20% monthly churn. Talk to customers who cancel. One pattern will emerge. Fix it.

**Not doing outbound.** SEO and social media are real, but slow. If you need revenue in 90 days, you need outbound. Cold email still works.

---

## Quick Reference: Tools + Links

- **Lovable:** lovable.dev
- **Supabase:** supabase.com
- **Stripe:** stripe.com
- **Product Hunt:** producthunt.com
- **AppSumo Sell:** appsumo.com/sell
- **Instantly:** instantly.ai
- **Apollo (leads):** apollo.io
- **Beehiiv (newsletter):** beehiiv.com

---

*Playbook by Wolfgang Meyer. Built from real launches, real numbers, real failures.*
