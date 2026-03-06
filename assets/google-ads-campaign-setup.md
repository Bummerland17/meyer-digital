# Google Ads Campaign Setup - PantryMate Lifetime Deal
## Status: 2FA Required — Manual Step Needed

**Generated:** 2026-03-04

---

## What Was Accomplished

1. ✅ Successfully navigated to ads.google.com
2. ✅ Entered email: olcowboy21@gmail.com
3. ✅ Password accepted (credentials are correct)
4. ⛔ BLOCKED at 2-Step Verification

## 2FA Status

Google required 2-Step Verification with these options:
- **Option A:** Tap "Yes" on phone/tablet → *Device can't be reached right now*
- **Option B:** Security code from phone/tablet app (offline mode)
- **Option C:** SMS verification code to phone ending in ••20 ← **EASIEST**
- **Option D:** Tap Yes on recovery email device
- **Option E:** Use passkey
- **Option F:** Try another way

**Recommended:** Use Option C — request SMS code to your phone ending in ••20

---

## What Wolfgang Needs to Do

### Step 1: Sign in yourself
1. Go to **https://ads.google.com**
2. Sign in with: `olcowboy21@gmail.com` / `Bummerland20`
3. When 2FA appears, choose **"Get a verification code"** to your phone (••20)
4. Enter the SMS code

### Step 2: Create the Campaign

After logging in, click **"+ New campaign"** and enter these details:

#### Campaign Goal
- Select: **Website traffic** (or "Sales" for conversion tracking)

#### Campaign Type
- Select: **Search**

#### Website
- Enter: `https://pantrymate.net`
- Click Continue

#### Campaign Settings
| Field | Value |
|-------|-------|
| Campaign name | `PantryMate Lifetime Deal` |
| Bidding | **Maximize clicks** (simple for first campaign) |
| Daily budget | `$10.00` |
| Networks | Uncheck "Include Google Search Partners" (optional) |
| Locations | United States (or target states) |
| Languages | English |

#### Ad Schedule
- All day (default is fine)

### Step 3: Create Ad Group

**Ad group name:** `Meal Planning - Pantry Ideas`

#### Keywords (use Phrase and Exact match):
```
"what to cook tonight"
[what to cook tonight]
"meal planning app"
[meal planning app]
"what can i make with what i have"
[what can i make with what i have]
"pantry meal ideas"
[pantry meal ideas]
"dinner ideas from ingredients I have"
[dinner ideas from ingredients I have]
```

*Tip: In Google Ads, phrase match = "keyword", exact match = [keyword]*

### Step 4: Create the Ad (Responsive Search Ad)

| Field | Value |
|-------|-------|
| Final URL | `https://pantrymate.net` |
| **Headline 1** | `Dinner Decided in 30 Seconds` |
| **Headline 2** | `Scan Your Pantry - Get Meals Tonight` |
| **Headline 3** | `No More "What's For Dinner?" Stress` |
| **Headline 4** (bonus) | `Lifetime Access - Just $49` |
| **Headline 5** (bonus) | `Try Free, No Credit Card` |
| **Description 1** | `Scan your pantry or receipt. Get meal ideas from what you already have. No extra shopping needed.` |
| **Description 2** | `Lifetime access for $49. Try free first. 30-second meal decisions starting tonight.` |

### Step 5: Billing

When you reach the billing page — **STOP and review options** before entering payment info.
You will likely see:
- Credit/debit card
- Bank account (in some regions)
- Google Pay

**Budget note:** $10/day = max $300/month experiment

---

## Alternative: Landing Page Note

The task mentioned using `https://buy.stripe.com/bJe14mfVyfAocYvg04bsc00` as the landing page but **Google Ads does not allow Stripe checkout pages as final URLs** — they require the advertiser's own domain. 

✅ **Use `https://pantrymate.net` as the Final URL** (already set above) — users can find the buy link from there.

---

## Screenshots Saved

- `101-v3-initial.png` — Google sign-in page
- `102-v3-email-typed.png` — Email entered
- `103-v3-after-email.png` — Password challenge page  
- `104-v3-password-typed.png` — Password entered
- `105-v3-after-login.png` — **2FA verification page** (shows all options)

All in: `/root/.openclaw/workspace/assets/screenshots/`
