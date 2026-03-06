# UnitFix — Full Audit
*March 4, 2026*

---

## What It Is
Maintenance request tracker for small landlords (1–5 units).
Core hook: each unit gets a **unique public URL** — tenants submit requests without needing an account.
Stack: React + Vite + TypeScript + Supabase + shadcn/ui (same as PantryMate)
Pricing: Free (1 unit) / $15/mo Landlord Plan (up to 5 units)

---

## Overall Verdict
**Solid concept, right niche, underpriced, under-marketed.**
The public tenant link idea is genuinely differentiated. Most competitors require tenants to create accounts — a friction point that kills adoption. This solves a real daily problem for a paying audience. It just needs the price raised, a few missing features added, and some targeted marketing.

---

## 🔴 Critical Issues

### 1. Underpriced — leaving real money on the table
$15/mo for a landlord managing 5 units is almost nothing. A landlord with 5 units grosses $6,000–$15,000/month in rent. $15 is rounding error.
**Fix:** Raise to $29/mo. Add an annual option at $249/yr ($20.75/mo). Test $49/mo for a "Pro" tier with unlimited units.

### 2. No photo/video upload on tenant requests
Tenant submits "toilet is leaking" — but landlord has no idea if it's a drip or a flood. Without photos, every request requires a follow-up call.
**Fix:** Add photo upload to the public request form. This is the #1 feature request in every property management forum.

### 3. No two-way tenant communication
Tenant submits a request and then... what? They have no way to check status or receive updates. They text the landlord anyway. The chaos continues.
**Fix:** Add an optional email field on tenant request form → send status update emails when landlord changes status. No account needed — just a notification.

### 4. Onboarding flow unclear
After signup, is there a guided setup? The Onboarding.tsx page exists but the flow from signup → add property → copy tenant link needs to be frictionless.
**Fix:** 3-step post-signup wizard: (1) Add your first property, (2) Add a unit, (3) Copy the link and text it to your tenant. Done in 2 minutes.

---

## 🟠 High Priority

### 5. Landing page headline is weak
"Maintenance requests, without the chaos" is fine but doesn't communicate the unique hook.
**Stronger:** *"Your tenant texts you a problem. They should text this link instead."*
Or: *"One link. Your tenant submits. You track. No more texts at 11pm."*

### 6. No competitor comparison / pricing anchoring
Buildium starts at $50/mo. AppFolio starts at $280/mo. Both require tenants to have accounts.
The landing page doesn't mention this at all — it should. "Not Buildium" is a positioning statement.
**Fix:** Add a simple comparison row: "UnitFix vs. the other guys" showing price, tenant account required (❌ them, ✅ you), complexity.

### 7. No social proof
No testimonials, no "X landlords use UnitFix", no review quotes. Cold landing page for a tool that requires trust.
**Fix:** Even 3 fake-looking real quotes from beta users would help. Add a counter ("Join 47 landlords who stopped getting 11pm texts").

### 8. No urgency / seasonal angle
Rental market has seasons. Spring = lease renewals + move-ins = highest landlord acquisition opportunity.
March/April is the best time to market this. The landing page has no urgency.
**Fix:** Add a banner: "Peak rental season is coming — get your units organized before new tenants move in."

---

## ✅ What's Working Well
- Public tenant request link is **genuinely unique** — the best feature, correctly highlighted
- Free tier with 1 unit is the right lead magnet
- Clean, professional UI — doesn't look like a side project
- Auth + subscription management is solid
- "Copy Tenant Link" button on dashboard is prominent and well-placed
- Status badges (Open / In Progress / Completed) are clean
- Urgency field on requests is thoughtful
- Email: support@unitfix.app suggests it has its own domain

---

## Growth Channels (ranked by ease)

### 1. Reddit — r/Landlord (1.1M members), r/Landlords, r/RealEstateInvesting
These communities post "how do you track maintenance?" threads constantly.
→ Post a genuine helpful answer mentioning UnitFix
→ Same 10-reply strategy we're using for PantryMate

### 2. BiggerPockets.com
Largest landlord/investor community online. Active forums, marketplace listings.
→ Post in "Tools & Software" forum
→ Profile should link to UnitFix

### 3. Facebook Groups
"Landlords" (500k+ members), "Small Landlords Network", state-specific landlord groups
→ Direct offer posts work here

### 4. ProductHunt
Clean UI + genuine niche = good PH candidate.
→ "The simplest maintenance tracker for small landlords" would perform well

### 5. AppSumo / Lifetime Deal
$99 lifetime for small landlords = low risk buy.
→ Same playbook we built for PantryMate

---

## Revenue Potential

| Scenario | Subs | MRR |
|----------|------|-----|
| Conservative | 50 | $750 |
| Target (6 months) | 200 | $3,000 |
| Raised price ($29) x 200 | 200 | $5,800 |

At $29/mo and 200 subscribers = **$5,800 MRR** — meaningful passive income alongside PantryMate.

---

## Recommended PR / Fix Order

1. **Raise price to $29/mo** — edit `Pricing.tsx` (15 min)
2. **Add photo upload to public request form** — biggest feature gap
3. **Add status email notifications to tenants** — completes the loop
4. **Rewrite landing page headline** — 20 min, high impact
5. **Add competitor comparison section** — 30 min
6. **Reddit marketing** — use same strategy as PantryMate

---

## Quick Revenue Play
Same as PantryMate lifetime deal:
- $79 lifetime access (1 property, unlimited units)
- Post in r/Landlord: *"Built a maintenance tracker for small landlords — offering lifetime access to the first 50 people for $79 one-time"*
- Target: 20 sales = $1,580 this week
