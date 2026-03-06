# Deal Finder — Spec & Decision

> *Which version should Veldt build next?*

---

## The Three Options

### Version A: Local Deal Map
An interactive city map showing deals from Craigslist RSS + Facebook Marketplace.  
Click a pin → see the deal. Filter by category.

### Version B: Africa Flight Deal Finder
Beautiful UI showing cheapest flights from African airports.  
"Best time to fly Windhoek → Amsterdam." Free flight APIs.

### Version C: "Good Price?" Checker
Paste a Craigslist/Facebook listing URL.  
AI compares it against historical sales and tells you: good deal / fair / overpriced.

---

## Evaluation Matrix

| Criterion | Version A: Local Deal Map | Version B: Africa Flights | Version C: Good Price? |
|---|---|---|---|
| **Technical feasibility** | 🟡 Medium | 🟡 Medium | 🟠 Hard |
| **Free API availability** | 🟡 Craigslist RSS yes; Facebook no | 🟢 Aviationstack free tier, Kiwi.com | 🔴 Needs LLM backend |
| **No-backend possible?** | 🔴 No — scraping needs proxy | 🟡 Partial (CORS issues with APIs) | 🔴 No — needs AI + comparison logic |
| **Viral / shareable?** | 🟡 Local = limited audience | 🟢 High — underserved niche | 🟢 High — "look how overpaying people are" |
| **Reputation value** | 🟡 Medium | 🟢 High — first of its kind | 🟢 High — immediately useful |
| **Revenue potential** | 🟡 Affiliate/ads | 🟢 Affiliate commissions (flights) | 🟢 Freemium / API monetization |
| **Wolfgang's connection** | 🟡 Anyone flips deals | 🟢 🟢 Lives this — flies Africa routes | 🟡 Universally useful |
| **Differentiation** | 🔴 Craigslist apps exist | 🟢 Nothing quite like this | 🟡 Some AI price checkers exist |
| **Build complexity** | Medium | Medium | Hard |

---

## Analysis

### Version A: Local Deal Map
**The problem:** Facebook Marketplace has an unofficial API but aggressively blocks scraping. Building a reliable data pipeline without a backend is not feasible without either a server-side proxy or a paid API. Craigslist RSS exists but coverage varies by city and the data is inconsistent. The experience would feel fragile.

**The bigger problem:** Local deal maps already exist — OfferUp, Facebook's built-in map view, Craigslist's own listings. We'd be competing directly with well-funded incumbents with far more inventory.

**Verdict:** 🔴 Don't build. Feasibility is shaky, differentiation is weak, and the audience is fragmented by city.

---

### Version C: "Good Price?" Checker
**The appeal:** Immediately useful. Everyone buying secondhand wants to know if they're getting ripped off. Simple input → useful output. Very shareable ("this site told me I almost overpaid $400").

**The problem:** Real comparative pricing requires either:
1. A database of recent comparable sales (requires a backend)
2. LLM inference on listing descriptions (requires an API key + server)
3. Scraping live data at query time (fragile, blocked)

A static HTML experience can't do this credibly. A serverless function + LLM API gets expensive fast. To do this *well* you'd need a real backend — which is fine, but it's not a quick build, and the data quality would be inconsistent without major investment.

**Verdict:** 🟡 Build later. Worth building, but needs more infrastructure than Version B. Could work well as a freemium web app once Veldt has backend capacity.

---

### Version B: Africa Flight Deal Finder ⭐
**Why this wins:**

1. **Wolfgang lives this problem.** Flying from Namibia or South Africa to Europe is expensive, opaque, and poorly served by existing tools. Google Flights works, but it doesn't surface patterns — *when* to fly, *which routes* are consistently cheap, *which stops* are worth it. This comes from personal experience, not market research.

2. **The niche is underserved.** There is no beautiful, purpose-built flight deal finder for African travelers. African airports, African routes, African travel patterns. First mover in a growing market.

3. **Free APIs exist and are usable.** Options:
   - **Kiwi.com Tequila API** — free tier, flight search by route/date range, reasonable CORS
   - **Aviationstack** — free tier for current flight data
   - **Skyscanner Affiliate API** — commission-based
   - **Fallback:** Curated static data (like the music map) showing historical best times to fly specific routes — no API needed for v1

4. **Shareable.** "Best times to fly Windhoek → Amsterdam on a budget" is the kind of thing that gets posted on Namibian travel forums, r/solotravel, WhatsApp travel groups. It spreads organically.

5. **Revenue path is clear.** Flight affiliate programs pay $5–$40 per booking. Every "Book this flight" click = potential commission. Skyscanner, Google Flights affiliate, Kiwi.com all have programs.

6. **V1 can be zero-backend.** Start with static curated data for 10–15 key African routes, beautiful UI, YouTube-style "best time" charts. Add live API data in V2. Ship fast.

**Verdict:** 🟢 Build this next.

---

## Recommendation: Build Version B — Africa Flight Deal Finder

### What to call it
**"Drift"** — *African flight deals, beautifully surfaced.*  
Or: **"Runway"** — clean, travel-adjacent, memorable.

### V1 Scope (static, no backend — ship in 1 session)
- Beautiful dark UI (same aesthetic as the music map)
- 12 key routes: Windhoek, Johannesburg, Nairobi, Lagos, Addis Ababa, Cairo → London, Amsterdam, Frankfurt, Dubai, New York
- For each route: best months to fly (chart), rough price range, main airlines, tips
- "Plan my trip" CTA → links to Kiwi.com or Skyscanner with affiliate tag
- Branding: "Built by Veldt · veldt.io"

### V2 Scope (with live API — build after V1 validates)
- Live price search via Kiwi.com Tequila API
- Price calendar: visualize cheapest 30-day window
- Route comparison: "Windhoek vs Johannesburg as your departure city"
- Price alert signup (email capture = Veldt list growth)

### Why this fits the Veldt reputation filter
- ✅ Would someone screenshot this and post it? — Yes, travel groups will share it
- ✅ Does it do one thing really well? — Yes: Africa flight deals
- ✅ Is there anything quite like it? — No
- ✅ Would it make Veldt look impressive? — Yes: "those are the people who built that Africa travel tool"

---

## Files
- This spec: `website-factory/deal-finder-spec.md`
- When built, save to: `drift/index.html` (or `runway/index.html`)
- Deploy to: `Bummerland17/drift` on GitHub Pages

---

*Spec written: 2026-03-04*  
*Recommendation: Version B — Africa Flight Deal Finder (codename: Drift)*
