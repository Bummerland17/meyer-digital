# Website Factory — Veldt

> **Build things people WANT to use. Not brochure sites.**

The old Website Factory made templates for service businesses. That era is over.

The new Website Factory builds **unique interactive web experiences** — tools, maps, finders, visualizations — that people screenshot, bookmark, post on Reddit, and share with their friends. Reputation comes first. Revenue follows naturally when the thing is genuinely good.

---

## The Philosophy

### What We Build Now

| Type | Example |
|---|---|
| 🗺️ **Interactive maps** | Music Around the World, Local Deal Scout |
| 🧮 **Calculators / tools** | "Good Price?" Deal Checker |
| 📊 **Data visualizations** | Flight routes, price trends |
| 🎮 **Mini web apps** | One-thing-well experiences |
| 🔗 **Veldt tie-ins** | Tools that organically drive Sonara / PantryMate signups |

### The Filter (apply before building anything)

Ask these 4 questions. If you get 4 YES answers, build it:

1. **"Would someone screenshot this and post it?"** → YES = build it
2. **"Does it do one thing really well?"** → YES = build it
3. **"Is there anything quite like it?"** → NO = build it
4. **"Would it make Veldt look impressive?"** → YES = build it

If any answer is NO — redesign it until all 4 are YES, or kill it.

### Why This Works

Conversion-optimized brochure sites are commoditized. Every freelancer and Wix template competes there. But *genuinely useful interactive experiences* are rare, shareable, and memorable. When someone shares your tool, they're vouching for Veldt. That's worth more than any ad spend.

**Reputation >> Direct conversion.**  
Revenue comes naturally when the thing is genuinely good.

---

## What's Been Built

| Experience | URL | Status |
|---|---|---|
| 🌍 Music Around the World | https://bummerland17.github.io/music-map/ | ✅ Live |

---

## What's Coming

| Experience | Type | Priority |
|---|---|---|
| Deal Finder (TBD — see spec) | Interactive tool | 🔜 Next |
| Sonara "Discover Your Sound" | Music personality quiz | Planned |
| PantryMate Recipe Finder | Ingredient-based search | Planned |

See `deal-finder-spec.md` for the full analysis of the next build.

---

## Build Stack

Every experience is built with:
- **Zero backend** — pure HTML/CSS/JS, deploys to GitHub Pages
- **Leaflet.js** for maps (open source, beautiful)
- **Google Fonts** for typography (Inter + display fonts)
- **Dark-first design** — atmospheric, not corporate
- **Mobile-first** — works on phone, looks stunning on desktop

---

## Legacy: Template Sites

The old template system (service businesses, $599/site) still lives here:

```
templates/
├── service-business.html
├── saas-app.html
├── agency-consultant.html
├── real-estate-local.html
└── digital-product.html
```

Use `builder.py` + a JSON config to deploy a client site.  
This is now a **secondary** use of the factory. Reputation experiences come first.

---

## Guiding Principle

> *The goal isn't to build more websites. The goal is to build fewer, better things that make people say "who made this?" — and then find Veldt.*

---

Built by Veldt · [veldt.io](https://veldt.io)

---

## The Golden Rule: Never Copy. Always Improve.

When Scout finds inspiration from a viral site or successful app:

1. **Understand WHY it works** — what's the core mechanic? What job is it doing for people?
2. **Find where it fails** — who does it miss? What does it do badly? What's frustrating about it?
3. **Build for the gap** — our version serves the underserved audience or solves the frustration

### Examples of this in practice:

**Scott's Cheap Flights** → Popular because people want flight deals without searching. Fails because: US-centric, email-only, ugly UX, no African routes.
→ **Drift**: Beautiful web-first experience, African travelers specifically, global + niche, interactive not just email.

**Generic music maps** → People like exploring music by country. Fails because: hard to find, ugly, no audio preview, US/Europe focused.
→ **Music Around the World**: Beautiful, dark, immersive, 42 countries including Africa, ties to Sonara.

**Every SaaS tool** → Solves A problem. Fails because: too complex, too expensive, wrong audience.
→ **PantryMate/UnitFix/FollowUpFox**: Strip it to one job, do it perfectly, price it honestly.

### The question to ask before building anything:
*"Who does the existing version leave behind, and what would they love instead?"*

That answer is what we build.
