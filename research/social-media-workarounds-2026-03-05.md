# Social Media Account Creation & Automation Research
**Date:** 2026-03-05  
**Purpose:** Solo founder (Wolfgang) needs business accounts on all major platforms without using personal phone numbers, plus autonomous posting automation.

---

## TL;DR: What Actually Works Right Now (Top 3 Actions)

### 🥇 Action 1: Get a real-SIM virtual number from sms-activate.io (~$1-3)
VoIP numbers (TextNow, Google Voice) are **blocked by Twitter/X and Instagram** as of 2025/2026. You need real SIM-based numbers. Buy one-time SMS codes from **sms-activate.io** for each platform (~$0.10–$2 per verification). One number typically works for ONE platform only.

### 🥈 Action 2: Set up Postiz (self-hosted, free) or Buffer (free tier)
**Postiz** is open-source and supports every major platform including TikTok — deploy it on your server for free. Buffer's free tier covers 3 channels with 10 scheduled posts each. For a solo founder doing 1-2 posts/day, either works without spending money.

### 🥉 Action 3: Start with LinkedIn + Pinterest + Facebook (easiest to create + automate)
These three have the lowest friction for account creation (no phone required or VoIP works) and the best official API support for autonomous posting. Tackle Twitter and Instagram after.

---

## Platform-by-Platform Breakdown

---

### 1. 🐦 X / Twitter

#### Account Creation
- **Phone required?** Yes, mandatory since 2026. Twitter/X explicitly blocks VoIP numbers.
- **What works:** Real SIM-based number services:
  - **sms-activate.io** — $0.20–$0.50 per Twitter SMS, high success rate
  - **MobileSMS.io** — $3.50+ per use, claims 99.2% Twitter success rate
  - **TextVerified.com** — another solid option, similar pricing
- **What doesn't work:** TextNow, Google Voice, Hushed, MySudo (all VoIP, all blocked)
- **Setup tip:** Create account via email first, then add phone verification when prompted. Use incognito/fresh IP to avoid IP-based flags.

#### Posting Automation
- **X API status (2026):** Pay-per-usage model, NO free tier for writing. Costs money per post via API.
- **Best free option:** **Buffer** — free tier supports scheduling for X (Twitter) free/premium profiles with push notification publishing
- **Postiz** — self-hosted open source, supports X natively
- **Posting limits (new accounts):** Start slow: 1-2 posts/day for first week, then ramp up

#### Risk Level: 🟡 MEDIUM
- New accounts posting heavily get flagged. Best practices:
  - Don't post more than 5-10x/day
  - Add a bio and profile pic before posting anything
  - Follow some accounts first, engage organically
  - Don't use automation tools that simulate browsing/clicks (browser automation = high ban risk)
  - Space posts out; don't bulk-schedule 10 posts at once

#### One-time Setup
1. Buy real SIM number from sms-activate.io (~$0.50)
2. Create account with email + that number
3. Fill out profile (avatar, bio, link to product)
4. Connect to Buffer or Postiz via OAuth
5. Queue posts — runs forever after that

---

### 2. 🎵 TikTok

#### Account Creation
- **Phone required?** Yes. TikTok is stricter than most platforms.
- **What works:** Real SIM numbers (sms-activate.io) tend to work better. Some reports of VoIP working but unreliable.
- **Account type needed:** Create a **TikTok Business Account** (not personal) for API/automation access

#### Posting Automation
- **Official TikTok API:** Requires developer app approval. Can take 2-4 weeks with back-and-forth on privacy policy, ToS, app review. **No reliable shortcut.**
- **Buffer supports TikTok:** TikTok Business profiles — automatic publishing + notification publishing (both work). Buffer is the cleanest path.
- **Postiz supports TikTok:** Yes, confirmed in their feature list. Self-hosted = free.
- **Later supports TikTok:** Auto-publishing for TikTok Business profiles with precision scheduling.
- **Puppeteer/Playwright automation:** Technically possible but extremely high ban risk. TikTok has aggressive bot detection. Not recommended for a legitimate business account.

#### Developer API Approval — Faster Path
- Apply via [developers.tiktok.com](https://developers.tiktok.com)
- Use your business website with a real privacy policy and terms of service
- Select "Content Posting API" scope
- Average wait: 2-6 weeks
- **Pro tip:** Buffer/Later/Postiz have already gone through TikTok's approval process. Connecting your account to their platforms (even self-hosted Postiz) means you piggyback on their approved app credentials.

#### Risk Level: 🟡 MEDIUM
- Posting via official tools (Buffer/Later/Postiz OAuth) = low risk
- Avoid: browser automation, third-party tools that use unofficial APIs
- Fresh accounts: post 1x/day for first week, then increase gradually
- Use real content (actual product videos), not low-effort reposts

#### One-time Setup
1. Create TikTok Business account (phone needed)
2. Connect to Buffer (free tier) or self-hosted Postiz
3. Schedule posts — runs autonomously

---

### 3. 📸 Instagram

#### Account Creation
- **Phone required?** Usually yes for verification (can be email-only initially, but phone gets required quickly)
- **What works:** Same real SIM services — sms-activate.io, MobileSMS.io
- **VoIP status:** Mixed reports — sometimes works initially, often fails on re-verification
- **Account type:** Create as **Business** (not Personal) by linking to a Facebook Page for full API access

#### Posting Automation
- **Official path:** Meta Graph API, accessed via Facebook Developer App. Requires connecting Instagram Business account to a Facebook Page.
- **Buffer** — full support for Instagram Business + Creator accounts (auto-publish photos, Reels, Stories via notification)
- **Later** — excellent Instagram support including auto-publish, hashtag manager, first comment scheduling
- **Postiz** — supports Instagram
- **Instagrapi (unofficial Python library):** 
  - Status in 2026: Still works but HIGH ban risk. Meta actively detects and bans unofficial API usage.
  - **Not recommended for legitimate business accounts.** Use official tools.
- **Safest approach for 1-2 posts/day:** Buffer or Later via official Meta API. Zero ban risk if you stay within Meta's rate limits.

#### Risk Level: 🟢 LOW (with official tools)
- Official API posting via Buffer/Later = very safe
- Stay under 25 posts/day (you won't come close at 1-2/day)
- Add varied content types (photos, Reels, carousels)

#### One-time Setup
1. Create Instagram account (real SIM number likely needed)
2. Create a Facebook Page (free, no phone needed if you have a Facebook account)
3. Link Instagram Business to Facebook Page
4. Connect to Buffer or Later
5. Queue content — fully autonomous

---

### 4. 💼 LinkedIn

#### Account Creation
- **Phone required?** No — email only usually works. LinkedIn occasionally asks for phone verification on new accounts but it's not mandatory at signup.
- **VoIP works?** Yes — Google Voice or TextNow typically work for LinkedIn verification if asked
- **Risk:** LinkedIn watches for fake accounts. Use a real name, real profile photo, legitimate bio.

#### Posting Automation
- **Buffer** — supports LinkedIn Profiles and Pages natively. Free tier works.
- **Postiz** — supports LinkedIn
- **LinkedIn native scheduler** — LinkedIn itself has post scheduling built in (free, no API needed)
- **Phantombuster:**
  - Cost: $56/mo (Starter) to $160/mo (Pro)
  - Can do: auto-connect, message sequences, profile scraping, like/comment automation
  - **Ban risk: HIGH for aggressive automation.** Connection requests at scale get restricted.
  - For just daily posting: overkill and risky. Buffer is better.
- **Free LinkedIn automation:** LinkedIn's own scheduling is free. For posting, no third-party tool is needed beyond what Buffer offers for free.

#### Realistic Posting Assessment
- Fresh LinkedIn accounts CAN post daily without restriction **if**:
  - Profile is complete (photo, headline, summary, work history)
  - Account is a few weeks old before heavy posting
  - Content is genuine (not repetitive spam)
  - Posting via official tools, not browser automation
- Avoid: mass connecting, InMail blasts, auto-liking

#### Risk Level: 🟢 LOW (posting only, via official tools)

#### One-time Setup
1. Create LinkedIn account with email (no phone usually needed)
2. Complete profile with real details
3. Connect to Buffer or use LinkedIn's built-in scheduler
4. Queue posts — runs autonomously

---

### 5. 📘 Facebook

#### Account Creation
- **Phone required?** Sometimes. Facebook increasingly requires phone for new personal accounts.
- **VoIP works?** Mixed in 2025/2026 — TextNow and Google Voice have variable success. Real SIM numbers from sms-activate.io more reliable.
- **Business accounts:** Facebook Pages don't require a separate phone — they're tied to a personal account. Create one personal account (real SIM if needed), then create unlimited Pages from it.

#### Posting Automation
- **Facebook Graph API:** Supports posting to Pages you manage. Does NOT support posting to Groups you don't admin via API.
- **Buffer:** 
  - Facebook Pages: ✅ Auto-publish
  - Facebook Groups: ⚠️ Notification publishing only (you get a push notification, tap to publish)
  - Personal profiles: ❌ Not supported
- **Postiz** — supports Facebook Pages
- **Group posting:** If Wolfgang wants to post in Facebook Groups (not his own), this cannot be automated via official API. Third-party tools that do this use unofficial methods = ban risk.
- **For product promotion:** Create a Facebook Page for PantryMate/ClosetMate. Auto-post to the Page via Buffer. Much cleaner than group spam anyway.

#### Risk Level: 🟢 LOW (Page posting via official API)

#### One-time Setup
1. Create Facebook personal account (real SIM if needed, ~$0.20 via sms-activate.io)
2. Create Facebook Page for the business
3. Connect Page to Buffer
4. Queue posts — runs autonomously

---

### 6. 📌 Pinterest (Bonus)

#### Is it Worth It for PantryMate/ClosetMate?
**Yes — very much so.** Pinterest users actively search for:
- "pantry organization ideas"
- "closet organization systems"
- "meal planning tools"
- "wardrobe management"

Pinterest drives **high purchase intent traffic** and pins have a much longer lifespan than tweets or Instagram posts. A well-optimized pin can drive traffic for months/years.

#### Account Creation
- **Phone required?** No — email or Google/Apple sign-in works. Very low friction.
- **Business account:** Free to create, just select "Business" during signup or convert later.

#### Posting Automation
- **Buffer** — supports Pinterest Business accounts for auto-publishing ✅
- **Postiz** — supports Pinterest ✅
- **Pinterest's own scheduler** — built into the platform, free
- **Tailwind** — Pinterest-specific tool, $12.99/mo, excellent for scheduling + analytics

#### Risk Level: 🟢 LOW
Pinterest is very automation-friendly. Official API is stable and well-documented.

#### One-time Setup
1. Create Pinterest Business account (email only, no phone)
2. Connect to Buffer (covers it in the free 3-channel plan)
3. Upload product images with keyword-rich descriptions
4. Queue pins — fully autonomous

---

## Virtual Phone Number Comparison Table

| Service | Type | Cost | Twitter/X | Instagram | TikTok | Facebook | LinkedIn | Notes |
|---------|------|------|-----------|-----------|--------|----------|----------|-------|
| **sms-activate.io** | Real SIM | $0.10–$2/use | ✅ Works | ✅ Works | ✅ Works | ✅ Works | ✅ Works | Best overall. Pay per use. 500+ services. |
| **MobileSMS.io** | Real SIM | $3.50+/use | ✅ 99.2% | ✅ Works | ✅ Works | ✅ Works | ✅ Works | Premium, higher success rate guarantee |
| **TextVerified** | Real SIM | $1–3/use | ✅ Works | ✅ Works | ✅ Works | ✅ Works | ✅ Works | US numbers, reliable |
| **5sim.net** | Real SIM | $0.10–$1/use | ✅ Works | ✅ Works | ✅ Works | ✅ Works | ✅ Works | Similar to sms-activate |
| **Google Voice** | VoIP | Free (US only) | ❌ Blocked | ❌ Often blocked | ⚠️ Unreliable | ⚠️ Sometimes | ✅ Usually | Good for LinkedIn/FB only |
| **TextNow** | VoIP | Free | ❌ Blocked | ❌ Blocked | ⚠️ Unreliable | ⚠️ Sometimes | ✅ Usually | Often blocked by major platforms |
| **Hushed** | VoIP | $1.99/mo | ❌ Blocked | ❌ Blocked | ⚠️ Unreliable | ⚠️ Sometimes | ✅ Usually | Not worth it for social media |
| **MySudo** | VoIP | $0.99–$14.99/mo | ❌ Blocked | ❌ Blocked | ⚠️ Unreliable | ⚠️ Sometimes | ✅ Usually | Privacy-focused but limited social use |

### Key Insight on Reusability
**One virtual number = one platform.** Each platform ties the number to the account during verification. Once used, a temporary number from sms-activate.io expires. You need a fresh number for each platform. At ~$0.50/platform × 6 platforms = **~$3 total for all verifications.**

---

## Recommended Setup Order (Easiest Wins First)

### Week 1: The Easy Three
1. **LinkedIn** — email only, no phone. Complete profile, connect to Buffer. Start posting immediately.
2. **Pinterest** — email only. Create Business account. Add product imagery. Connect to Buffer.
3. **Facebook** — create account (may need VoIP/real SIM). Create Facebook Page. Connect to Buffer.

**Tools:** Buffer free tier (3 channels). You're covered for LinkedIn + Pinterest + Facebook Page.

### Week 2: The Visual Ones
4. **Instagram** — get real SIM number from sms-activate.io (~$0.50). Create account, link to Facebook Page (Business), connect to Buffer or Later.
5. **TikTok** — get real SIM number (~$0.30). Create Business account. Connect to Buffer (no developer app needed — Buffer is pre-approved).

**Tools:** Upgrade to Buffer Essentials ($5/mo per channel) for unlimited scheduling, OR deploy Postiz self-hosted (free) to cover all channels.

### Week 3: The Hard One
6. **Twitter/X** — get real SIM from sms-activate.io (~$0.50). Create account. Wait 3-5 days before heavy posting. Connect to Buffer/Postiz.

---

## Automation Stack Recommendation

### Option A: All-Free (Self-Hosted)
- **Postiz** self-hosted on a VPS (~$5/mo for a cheap Hetzner/DigitalOcean instance)
  - Supports: X, LinkedIn, Instagram, Facebook, TikTok, YouTube, Pinterest, Reddit, Bluesky, Discord, Mastodon, Threads
  - Cost: Free software + server cost
  - Best for: developers comfortable with Docker

### Option B: Budget Cloud ($5-29/mo)
- **Buffer Essentials** — $5/channel/month
  - 6 channels × $5 = $30/mo
  - OR use Buffer free tier (3 channels) + LinkedIn native scheduler + Pinterest native scheduler
  - Effective cost: ~$10-15/mo for the channels that matter most

### Option C: Visual-First ($18/mo)
- **Later Starter** — better Instagram/Pinterest/TikTok analytics, visual calendar
  - Supports: Instagram, TikTok, Pinterest, Facebook, LinkedIn (NOT Twitter/X on all plans)
  - ~$18-25/mo for 1 profile per platform

### Wolfgang's Recommended Stack (Pragmatic)
**Phase 1 (Month 1, ~$0-5/mo):**
- Buffer Free (3 channels: LinkedIn + Pinterest + Facebook)
- LinkedIn native scheduler for overflow
- Total: **$0**

**Phase 2 (Month 2+, ~$15-30/mo):**
- Postiz self-hosted (all 6 platforms) OR
- Buffer Essentials for the 3 most important channels ($15/mo)
- Total: **$5-30/mo**

---

## Total Cost Estimate to Get All Platforms Running

| Item | Cost |
|------|------|
| Real SIM numbers for verification (6 platforms × ~$0.50) | ~$3 one-time |
| Buffer free tier (covers 3 channels) | $0/mo |
| Buffer Essentials for remaining channels OR Postiz VPS | $5-30/mo |
| **Total first month** | **~$3-33** |
| **Total ongoing** | **$5-30/mo** |

The virtual number costs are essentially negligible. The main ongoing cost is the scheduling tool.

---

## Important Caveats

1. **Account warming matters.** New accounts on Twitter/X and TikTok need 1-2 weeks of gentle activity before heavy automation. Start slow.

2. **Each platform's ToS technically prohibits "automated posting."** In practice, every major scheduling tool (Buffer, Later, Postiz, Hootsuite) operates within the official API — this is allowed. What's prohibited is browser automation that impersonates human behavior.

3. **TikTok developer approval takes time.** Buffer/Later/Postiz have pre-approved developer credentials, so connecting your account to them bypasses the approval process entirely.

4. **Instagram requires a Facebook Page.** There's no way around this for official API access. Create a simple Facebook Page for each product.

5. **Instagrapi and similar unofficial libraries** are NOT recommended for a real business account. The ban risk has increased significantly in 2025/2026 as Meta has upgraded detection.

6. **Pinterest is underrated.** For physical/visual products like PantryMate and ClosetMate, Pinterest may deliver better ROI than Twitter/TikTok. Don't skip it.

---

*Research compiled: 2026-03-05*
*Sources: sms-activate.io, mobilesms.io, buffer.com/pricing, postiz.com/pricing, later.com/pricing, developer.x.com, Reddit community reports*
