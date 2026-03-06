# Social Media Setup — Master Status Document
**Date:** 2026-03-05  
**Postiz:** http://103.98.214.106:4007 | hello@pantrymate.net  
**Goal:** Fully autonomous social posting across all platforms for PantryMate, UnitFix, and SmartBook AI

---

## ✅ What's Been Done Automatically

### 1. Postiz docker-compose.yaml Updated
**File:** `/root/.openclaw/workspace/postiz/docker-compose.yaml`

Changes made:
- ✅ `MAIN_URL` changed from `localhost` to `http://103.98.214.106:4007` (public IP)
- ✅ `FRONTEND_URL` changed to `http://103.98.214.106:4007`
- ✅ `NEXT_PUBLIC_BACKEND_URL` changed to `http://103.98.214.106:4007/api`
- ✅ `OPENAI_API_KEY` filled in (AI content generation now enabled)
- ✅ All social media credential fields added with correct placeholder format
- ✅ Callback URLs documented as comments for each platform

**Callback URLs for developer apps:**
```
X/Twitter:  http://103.98.214.106:4007/integrations/social/x/callback
LinkedIn:   http://103.98.214.106:4007/integrations/social/linkedin/callback
Facebook:   http://103.98.214.106:4007/integrations/social/facebook/callback
Instagram:  http://103.98.214.106:4007/integrations/social/instagram/callback
TikTok:     http://103.98.214.106:4007/integrations/social/tiktok/callback
Pinterest:  http://103.98.214.106:4007/integrations/social/pinterest/callback
YouTube:    http://103.98.214.106:4007/integrations/social/youtube/callback
```

### 2. Content Queue Generated
**File:** `/root/.openclaw/workspace/assets/postiz-content-queue.json`

- ✅ **64 posts** generated across all platforms
- ✅ Scheduled 2x/day per platform (07:00 UTC = 9am Namibia, 16:00 UTC = 6pm Namibia)
- ✅ Schedule spans 2026-03-06 through 2026-03-14 (9 days)
- ✅ Content pulled from all 3 campaigns:
  - PantryMate (X, Facebook, Instagram, LinkedIn, TikTok, Pinterest)
  - UnitFix (X, Facebook, LinkedIn, Instagram, TikTok)
  - SmartBook AI (LinkedIn only — B2B positioning)

**Post breakdown by platform:**
| Platform | Posts | Brands |
|----------|-------|--------|
| X/Twitter | 18 | PantryMate (10), UnitFix (8) |
| Facebook | 7 | PantryMate (3), UnitFix (4) |
| LinkedIn | 8 | PantryMate (2), UnitFix (2), SmartBook AI (4) |
| Instagram | 6 | PantryMate (4), UnitFix (2) |
| TikTok | 6 | PantryMate (4), UnitFix (2) |
| Pinterest | 16 | PantryMate (16) |

### 3. SMS-Activate Guide Created
**File:** `/root/.openclaw/workspace/assets/sms-activate-guide.md`

Complete step-by-step guide for:
- ✅ Creating sms-activate.io account
- ✅ Adding balance
- ✅ Buying numbers for X, Instagram, TikTok, Facebook
- ✅ Exact platform names to search
- ✅ Price estimates
- ✅ Pro tips (incognito, fresh IP, timing)
- ✅ How to connect each verified account to Postiz

### 4. Pinterest Setup Guide + 20 Pins Created
**File:** `/root/.openclaw/workspace/assets/pinterest-content-queue.md`

- ✅ Account creation steps (email only, no phone)
- ✅ 4 boards defined with SEO strategy
- ✅ 20 fully written Pinterest pins across 4 boards
- ✅ Pinterest API setup guide
- ✅ SEO keyword strategy for PantryMate's food niche
- ✅ Pin optimization checklist

---

## ⚡ Wolfgang's Action List

**Estimated total time: ~2–3 hours (one afternoon)**  
**Total estimated cost: ~$5 (sms-activate balance)**

---

### 🔴 Critical First: Restart Postiz
*Time: 2 minutes*

The docker-compose.yaml has been updated. Run this to apply changes:
```bash
cd /root/.openclaw/workspace/postiz
docker-compose down && docker-compose up -d
```

Postiz should come back up at http://103.98.214.106:4007 within 2–3 minutes.

---

### PHASE 1: Easy Platforms (No Phone Needed)
*These take 15 minutes total and can be done RIGHT NOW*

**Step 1 — Pinterest Business Account** ⏱️ 5 min
1. Go to https://pinterest.com/business/create
2. Email: hello@pantrymate.net
3. Business name: PantryMate
4. Category: Food & Drink
5. Website: pantrymate.net
6. Done — no phone required ✅

**Step 2 — Pinterest Developer App** ⏱️ 5 min
1. Go to https://developers.pinterest.com/apps/
2. Log in with your Pinterest business account
3. Create app → name: "PantryMate Scheduler"
4. Redirect URI: `http://103.98.214.106:4007/integrations/social/pinterest/callback`
5. Copy the **App ID** and **App Secret**
6. Add to Postiz docker-compose.yaml:
   - `PINTEREST_CLIENT_ID: 'your-app-id'`
   - `PINTEREST_CLIENT_SECRET: 'your-app-secret'`
7. Restart Postiz: `docker-compose restart`
8. Go to Postiz → Channels → Add Pinterest ✅

**Step 3 — LinkedIn Developer App** ⏱️ 10 min
1. Go to https://www.linkedin.com/developers/apps/new
2. App name: PantryMate
3. LinkedIn Page: (create one first if needed at linkedin.com/company/create)
4. Logo: upload PantryMate logo
5. After creation, go to **Products** tab:
   - Request **"Share on LinkedIn"** ← this is the critical one
   - Request **"Sign In with LinkedIn using OpenID Connect"**
6. Go to **Auth** tab:
   - Add redirect URL: `http://103.98.214.106:4007/integrations/social/linkedin/callback`
7. Copy **Client ID** and **Client Secret**
8. Add to Postiz docker-compose.yaml:
   - `LINKEDIN_CLIENT_ID: 'your-client-id'`
   - `LINKEDIN_CLIENT_SECRET: 'your-client-secret'`
9. Restart Postiz → Connect LinkedIn ✅

> ⚠️ LinkedIn **"Share on LinkedIn"** product approval is usually instant. If it asks for review, approval typically comes within 1–3 days.

---

### PHASE 2: Get SMS Numbers (sms-activate.io)
*Time: 20 minutes | Cost: ~$3–5*

See full guide: `/root/.openclaw/workspace/assets/sms-activate-guide.md`

**Quick version:**
1. Go to https://sms-activate.io
2. Register + add $5 balance (crypto or card)
3. For each platform below, search → select USA → buy number → create account → enter code

**Step 4 — Facebook Account + PantryMate Page** ⏱️ 10 min
1. Buy Facebook number on sms-activate (~$0.30)
2. Create personal account at facebook.com with hello@pantrymate.net
3. Verify with sms number
4. Create Page: Facebook → Pages → Create → "PantryMate" → Software/App category
5. Note: You need the Facebook account for Instagram too

**Step 5 — Instagram Business Account** ⏱️ 10 min
*(Do AFTER Facebook — you need the Facebook Page)*
1. Buy Instagram number on sms-activate (~$0.40)
2. Create account at instagram.com with a new email (create one at gmail.com)
3. Username: pantrymate_official or similar
4. Go to Settings → Account → Switch to Professional Account → Business
5. Link to your PantryMate Facebook Page
6. This is required for the Meta Graph API (Postiz uses this to post)

**Step 6 — Facebook Developer App** ⏱️ 10 min
*(One Meta app covers BOTH Facebook and Instagram)*
1. Go to https://developers.facebook.com/apps/creation/
2. App type: **Business**
3. App name: PantryMate Social
4. Add products:
   - **Facebook Login** → Settings → Valid OAuth Redirect URIs → add `http://103.98.214.106:4007/integrations/social/facebook/callback`
   - **Instagram Graph API**
5. Required permissions: `pages_manage_posts`, `pages_read_engagement`, `instagram_basic`, `instagram_content_publish`
6. Copy **App ID** and **App Secret**
7. Add to docker-compose.yaml → restart → connect Facebook Page and Instagram ✅

**Step 7 — TikTok Business Account** ⏱️ 8 min
1. Buy TikTok number on sms-activate (~$0.20)
2. Create account at tiktok.com → email signup
3. Verify with sms number
4. Settings → Manage Account → Switch to Business Account
5. Category: Education or Retail

> 💡 **TikTok shortcut:** Postiz has pre-approved TikTok developer credentials. You may be able to connect TikTok directly in Postiz without creating your own TikTok developer app. Try connecting via Postiz → Add Channel → TikTok first before going through TikTok's developer approval (which takes 2–6 weeks).

**Step 8 — X/Twitter Account** ⏱️ 10 min
1. Buy Twitter number on sms-activate (~$0.50–1.00)
2. Create account at twitter.com → sign up with email
3. Verify with sms number
4. Fill in profile: display name, bio, link to pantrymate.net

> ⚠️ **X/Twitter API Important Note:** X's API write access requires the **Basic tier ($100/month)**. Postiz may use its own X app credentials for posting (like it does with TikTok). Check Postiz → Add Channel → X to see if it works without your own API keys first.
> 
> If you need your own X developer app:
> - Go to https://developer.twitter.com/en/portal/dashboard
> - Create project + app
> - Enable OAuth 2.0 with PKCE
> - Permissions: Read + Write
> - Callback URL: `http://103.98.214.106:4007/integrations/social/x/callback`
> - **Cost:** $100/month for Basic tier

---

### PHASE 3: Load Content Into Postiz
*Time: 30 minutes | Cost: Free*

**Step 9 — Import Content Queue** ⏱️ 30 min

The content is ready in: `/root/.openclaw/workspace/assets/postiz-content-queue.json`

Options to import:
1. **Manual (recommended for first run):** Log into Postiz → Posts → New Post → copy/paste each post, select platform, set schedule
2. **Via Postiz API** (if API access is enabled in your plan)

Priority order for importing:
1. LinkedIn posts (SmartBook AI, PantryMate, UnitFix) — highest ROI per post
2. Pinterest pins — longest lifespan, drives traffic for months
3. Facebook posts — for community engagement
4. X/Twitter posts — for visibility + build-in-public audience
5. Instagram captions — for visual brand building
6. TikTok posts — for viral reach

**Step 10 — Pinterest Pins** ⏱️ 20 min

Pinterest pins are in: `/root/.openclaw/workspace/assets/pinterest-content-queue.md`

For each of the 20 pins:
1. Create a vertical image (Canva is easiest — use their food templates)
2. Add text overlay matching the pin title
3. Schedule via Postiz → Pinterest channel

---

### PHASE 4: YouTube (Already Connected via Metricool)
*You mentioned YouTube is already in Metricool. For Postiz:*

**Step 11 — YouTube Developer Credentials** ⏱️ 10 min
1. Go to https://console.cloud.google.com
2. Create project: "PantryMate Social"
3. APIs & Services → Enable **YouTube Data API v3**
4. Credentials → Create OAuth 2.0 Client ID
5. Application type: Web application
6. Redirect URI: `http://103.98.214.106:4007/integrations/social/youtube/callback`
7. Copy Client ID and Secret → add to docker-compose.yaml
8. Restart → Connect YouTube ✅

> **Note:** YouTube is free tier, no paid API access needed for posting.

---

## Platform Cost Summary

| Platform | API Access | Cost | Notes |
|---------|-----------|------|-------|
| **Pinterest** | Free ✅ | $0/mo | Instant approval |
| **LinkedIn** | Free ✅ | $0/mo | "Share on LinkedIn" product approval needed |
| **Facebook** | Free ✅ | $0/mo | App review may be needed for some permissions |
| **Instagram** | Free ✅ | $0/mo | Via Facebook app, requires FB Page link |
| **TikTok** | Free ✅ | $0/mo | Postiz may have pre-approved credentials |
| **YouTube** | Free ✅ | $0/mo | Via Google Cloud Console |
| **X/Twitter** | 💰 Paid | $100/mo | Basic tier required for write access via own app |

> 💡 **X/Twitter cost workaround:** Postiz self-hosted may include its own X developer credentials that allow posting without paying $100/mo. Test this first before purchasing X API access.

---

## Total Costs

| Item | Cost |
|------|------|
| sms-activate.io balance | $5 one-time |
| Postiz (self-hosted) | $0 (already running) |
| Developer apps (all platforms) | $0 |
| X/Twitter API (if needed) | $100/mo (test without first) |
| **Total one-time** | **~$5** |
| **Total monthly** | **$0** (or $100 if X API needed) |

---

## Expected Result

Once setup is complete:
- **Postiz posts automatically** 2x/day to each platform
- **Content is pre-loaded** with 9 days of scheduled posts
- **All 3 brands posting simultaneously:**
  - PantryMate → X, Facebook, Instagram, LinkedIn, TikTok, Pinterest
  - UnitFix → X, Facebook, LinkedIn, Instagram, TikTok
  - SmartBook AI → LinkedIn
- **Zero daily intervention required** — it just runs
- **Refill content** every 1–2 weeks by pasting new posts into Postiz

---

## Files Created

| File | Purpose |
|------|---------|
| `/root/.openclaw/workspace/postiz/docker-compose.yaml` | Updated with public IP + OpenAI key + social credentials |
| `/root/.openclaw/workspace/assets/postiz-content-queue.json` | 64 scheduled posts for all platforms |
| `/root/.openclaw/workspace/assets/sms-activate-guide.md` | Phone number verification guide |
| `/root/.openclaw/workspace/assets/pinterest-content-queue.md` | Pinterest setup + 20 pins |
| `/root/.openclaw/workspace/assets/social-media-setup-status.md` | This file |

---

## Developer App Quick Reference

| Platform | URL | Type | Approval Time |
|---------|-----|------|--------------|
| X/Twitter | developer.twitter.com | Paid ($100/mo) | Instant but costs money |
| LinkedIn | linkedin.com/developers | Free | 1–3 days for Share product |
| Facebook/Instagram | developers.facebook.com | Free | Hours to days |
| Pinterest | developers.pinterest.com | Free | **Instant** (fastest) |
| TikTok | developers.tiktok.com | Free | 2–6 weeks (use Postiz built-in instead) |
| YouTube | console.cloud.google.com | Free | Instant |

---

*Created: 2026-03-05 | Status: Ready for Wolfgang's action steps*
