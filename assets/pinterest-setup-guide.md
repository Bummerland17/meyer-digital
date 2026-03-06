# Pinterest Business Account Setup Guide for PantryMate

## Overview
Pinterest is email-only to sign up — no phone number required. A Business account unlocks analytics, Rich Pins, and API access. Pinterest drives significant long-term search traffic for recipe/food content because pins surface in Google image search.

---

## Step 1: Create a Pinterest Business Account

**URL:** https://www.pinterest.com/business/create/

**What to enter:**
- Email: hello@pantrymate.net
- Password: (use your standard secure password)
- Birthday: any valid date (required for account creation)
- Country: Namibia (or whichever you prefer)

**OR — convert an existing personal account:**
If you already have a personal Pinterest, go to:
https://www.pinterest.com/business/convert/

---

## Step 2: Set Up Your Business Profile

After creating the account:

1. **Business name:** PantryMate
2. **Website:** https://pantrymate.net
3. **Business type:** Select "Online store" or "Other"
4. **Profile photo:** Upload the PantryMate logo
5. **Bio:** "Tell us what's in your fridge → get dinner in 30 seconds. Free pantry-to-plate meal finder. Built by a solo founder in Namibia."

**Claim your website:**
- Go to Settings → Claim → Claim website
- Add a meta tag to pantrymate.net `<head>` or upload the provided HTML file
- This enables analytics for pins that link to pantrymate.net

---

## Step 3: Create Core Boards

Create these boards immediately (they act as content categories Pinterest uses for search):

| Board Name | Description | Category |
|---|---|---|
| "What to Make for Dinner Tonight" | Quick dinner ideas from whatever's in your fridge | Food & Drink |
| "Pantry Meal Ideas" | Real meals from pantry staples — no grocery run needed | Food & Drink |
| "Easy Weeknight Dinners" | Fast, simple meals for busy weeknights | Food & Drink |
| "Zero Waste Cooking" | Use what you have, waste nothing | Food & Drink |
| "Budget Meals That Don't Suck" | Cheap, good dinners from pantry basics | Food & Drink |

---

## Step 4: Apply for Pinterest API Access

**URL:** https://developers.pinterest.com/

### Process:
1. Go to https://developers.pinterest.com/apps/
2. Click **"Create App"**
3. Fill in:
   - **App name:** PantryMate
   - **App description:** Social scheduling integration for PantryMate food content. Used with Postiz self-hosted scheduler.
   - **Website URL:** https://pantrymate.net
   - **App type:** Web
4. For redirect URI (if using OAuth): `http://103.98.214.106:4007/integrations/social/pinterest/callback`
5. Accept Terms of Service
6. Submit

### What Happens Next:
- You get immediate access to a **sandbox/development environment**
- For production API access (to publish pins programmatically), you need to apply for **Enhanced Access**

**Enhanced Access URL:** https://developers.pinterest.com/docs/getting-started/set-up-app/

For Enhanced Access, you'll need to demonstrate the app use case. PantryMate's case is legitimate: automating content publishing via Postiz.

### Expected Approval Time:
- Sandbox access: **immediate**
- Enhanced (production) access: **1–4 weeks** (Pinterest reviews manually)
- You can connect Pinterest to Postiz via OAuth immediately once you have a Business account — API Enhanced Access is for custom integrations

---

## Step 5: Connect Pinterest to Postiz (No API Key Needed for Basic Use)

Postiz can connect to Pinterest via OAuth without needing the Developer API:

1. Go to **http://103.98.214.106:4007**
2. Log in with hello@pantrymate.net / PantryMate2026!
3. Click **"Add Channel"** → **Pinterest**
4. Click **"Connect"** — this will trigger a Pinterest OAuth flow
5. Log in to your Pinterest Business account in the popup
6. Authorize Postiz to post on your behalf
7. Select which boards to allow

**That's it** — Postiz can now schedule pins to your Pinterest boards without needing API developer credentials.

---

## Key Notes

- Pinterest content has a **long shelf life** — pins from months ago still drive traffic
- Food and cooking is Pinterest's #1 category — PantryMate content will find an audience here
- Use **vertical images** (2:3 ratio, e.g., 1000x1500px) — they perform significantly better
- Every pin should link to **pantrymate.net** to drive conversions
- Rich Pins (which pull metadata from your site automatically) require website verification (Step 2)

---

## Timeline Summary

| Action | Time Required |
|---|---|
| Create Business account | 10 minutes |
| Set up profile + boards | 20 minutes |
| Connect to Postiz via OAuth | 5 minutes |
| Developer API sandbox access | Immediate |
| Developer API Enhanced Access | 1–4 weeks |
| First pin scheduled via Postiz | Same day |
