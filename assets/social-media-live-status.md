# PantryMate Social Media — Live Status Report
**Generated:** 2026-03-05
**Goal:** $500 MRR this month

---

## Postiz Status

| Item | Status |
|---|---|
| Postiz URL | http://103.98.214.106:4007 ✅ Running |
| Account | hello@pantrymate.net — created and verified ✅ |
| Tier | ULTIMATE (10,000 channels allowed) ✅ |
| Social channels connected | **0** — all require OAuth setup |
| Posts scheduled | 0 (waiting for channel connections) |

### Connected Channels (Current)
**None yet.** All major platforms require OAuth authorization from within Postiz. This is the only remaining blocker.

### Available Integrations in Postiz
X/Twitter, LinkedIn, LinkedIn Page, Reddit, Instagram (Facebook Business), Instagram (Standalone), Facebook Page, Threads, YouTube, Pinterest, TikTok, Discord, Bluesky, and more.

---

## 30-Day Content Calendar

**File:** `/root/.openclaw/workspace/assets/30-day-content-calendar.json`

| Platform | Posts Generated | Date Range |
|---|---|---|
| Twitter/X | 60 | Mar 6 – Apr 4, 2026 |
| Instagram | 60 | Mar 6 – Apr 4, 2026 |
| LinkedIn | 60 | Mar 6 – Apr 4, 2026 |
| Facebook | 59 | Mar 6 – Apr 4, 2026 |
| Pinterest | 58 | Mar 6 – Apr 4, 2026 |
| **TOTAL** | **297 posts** | **30 days** |

**Schedule:** 07:00 UTC (9am Namibia) and 16:00 UTC (6pm Namibia)

**Content themes covered:**
- ✅ "I had [ingredient] and didn't know what to make" → PantryMate solved it
- ✅ Decision fatigue / dinner paralysis (relatable pain)
- ✅ Food waste stats + PantryMate as solution
- ✅ Feature highlights (dietary filters, meal history, effort filter)
- ✅ Social proof / testimonials (generic until real ones come in)
- ✅ Seasonal/trending food topics (St. Patrick's Day, spring produce)
- ✅ "What would YOU make with [ingredient]?" engagement posts

---

## Assets Generated

| File | Status |
|---|---|
| `30-day-content-calendar.json` | ✅ Complete — 297 posts |
| `pinterest-setup-guide.md` | ✅ Complete |
| `pinterest-pins-30days.md` | ✅ Complete — 30 pins |
| `twitter-dev-setup-guide.md` | ✅ Complete |
| `hn-followup-comments.md` | ✅ Complete — 3 comments |
| `social-media-live-status.md` | ✅ This file |

---

## Wolfgang's Action List

Everything below is what Wolfgang needs to do manually (requires browser OAuth/logins). Each step unblocks a platform.

---

### 🔴 PRIORITY 1: Connect X/Twitter (Biggest reach, builds-in-public audience)
**Time estimate: 30–45 minutes**

1. Go to https://developer.twitter.com/en/portal/dashboard — create a dev account
2. Create a new Project → new App (name: "PantryMate Postiz Scheduler")
3. Set App permissions to "Read and Write"
4. Add Callback URL: `http://103.98.214.106:4007/integrations/social/x/callback`
5. Copy API Key + API Key Secret
6. SSH into server: `nano /root/.openclaw/workspace/postiz/docker-compose.yaml`
7. Add `X_API_KEY` and `X_API_SECRET` to environment variables
8. Restart: `cd /root/.openclaw/workspace/postiz && docker compose restart postiz`
9. Go to http://103.98.214.106:4007 → Add Channel → X → Connect
10. Authorize via OAuth popup
11. Load 30-day Twitter content from calendar file

**Full guide:** `/root/.openclaw/workspace/assets/twitter-dev-setup-guide.md`

---

### 🔴 PRIORITY 2: Connect LinkedIn (Professional audience, solo founder story)
**Time estimate: 10 minutes**

1. Go to http://103.98.214.106:4007
2. Click "Add Channel" → LinkedIn (personal) OR LinkedIn Page
3. Click "Connect" → OAuth popup
4. Log in to your LinkedIn account → Authorize
5. LinkedIn is already configured in Postiz — no API keys needed

**Note:** LinkedIn works immediately via OAuth. No developer setup required.

---

### 🔴 PRIORITY 3: Connect Facebook + Instagram (Largest audiences)
**Time estimate: 20–30 minutes**

Facebook and Instagram connect together via Meta's Business Manager:

1. You need a **Facebook Page** (not a personal profile) for PantryMate
   - Go to https://www.facebook.com/pages/create/
   - Create page: "PantryMate" | Category: App | Link: pantrymate.net

2. For Instagram: you need a **Business/Creator Instagram account** connected to that Facebook Page
   - Convert your Instagram to Business at Settings → Account → Switch to Professional

3. In Postiz: Add Channel → Instagram (Facebook Business) → Connect → OAuth flow
4. Add Channel → Facebook Page → Connect → OAuth flow

---

### 🟡 PRIORITY 4: Create Pinterest Business Account
**Time estimate: 30 minutes**

1. Go to https://www.pinterest.com/business/create/
2. Email: hello@pantrymate.net
3. Business name: PantryMate | Website: pantrymate.net
4. Create 5 boards: "Dinner Tonight", "Pantry Meal Ideas", "Easy Weeknight Dinners", "Zero Waste Cooking", "Budget Meals"
5. In Postiz: Add Channel → Pinterest → Connect → OAuth
6. No API key required for basic scheduling

**Full guide:** `/root/.openclaw/workspace/assets/pinterest-setup-guide.md`
**30 pin descriptions ready:** `/root/.openclaw/workspace/assets/pinterest-pins-30days.md`

---

### 🟡 PRIORITY 5: Load Content Into Postiz

Once each platform is connected:

1. Go to Postiz calendar view
2. Use the calendar JSON at `/root/.openclaw/workspace/assets/30-day-content-calendar.json`
3. For each platform connected, create posts from the calendar
4. Or use the Postiz bulk import if available in your version

**Note:** Postiz API for creating posts requires channel IDs (obtained after OAuth connection). Once channels are connected, API bulk upload is possible.

---

### 🟢 PRIORITY 6: HN Follow-up Comments
**Time estimate: 5 minutes per comment**

Post 1 comment per day for 3 days on: https://news.ycombinator.com/item?id=47253332

Comments ready at: `/root/.openclaw/workspace/assets/hn-followup-comments.md`

**Recommended order:**
- Day 1: Comment 3 (Community question — most likely to get replies)
- Day 2: Comment 2 (Food waste data — most substantive)
- Day 3: Comment 1 (Founder story — personal but longer)

---

## What Starts Posting Automatically Once Connected

Once each platform is connected to Postiz and content is scheduled:

- **X/Twitter:** 2 posts/day at 07:00 UTC and 16:00 UTC — automatically
- **LinkedIn:** 2 posts/day — automatically
- **Facebook:** 2 posts/day — automatically
- **Instagram:** 2 posts/day — automatically
- **Pinterest:** 2 pins/day — automatically

**Total:** 10 posts/day across all platforms — all on autopilot.
**Zero manual work** after initial setup and content loading.

---

## Revenue Connection

| Channel | Path to $500 MRR |
|---|---|
| X/Twitter | Build-in-public posts drive direct sign-ups from dev/founder community |
| LinkedIn | Founder story posts resonate with professionals who cook at home |
| Facebook | Group sharing potential (Frugal Living, Zero Waste groups) |
| Instagram | Visual food content drives pantrymate.net clicks |
| Pinterest | Long-tail search traffic from "easy weeknight meals" etc. |

**The math:** 50 Pro subscribers at $9.99/month = $499.50 MRR. The content calendar is built to drive exactly this conversion.

---

## Total Time to Get Everything Live

| Task | Time |
|---|---|
| X/Twitter setup | 45 min |
| LinkedIn connect | 10 min |
| Facebook + Instagram setup | 30 min |
| Pinterest setup | 30 min |
| Content loading into Postiz | 30 min |
| HN comments (3 days) | 15 min total |
| **TOTAL** | **~2.5 hours** |

Everything can be live by end of today.
