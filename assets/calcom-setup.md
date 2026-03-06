# Cal.com Setup — SmartBook AI Demo Bookings

## Step 1: Create Your Free Cal.com Account

1. Go to **https://cal.com**
2. Click **"Get started for free"**
3. Sign up with your Google account or email (`hello@pantrymate.net` recommended for continuity)
4. Username: choose something clean like `smartbookai` or `wolfgangmeyer`
   - This sets your base URL: `cal.com/smartbookai`
5. Set your timezone: **Europe/Berlin** (or wherever Wolfgang is based)
6. Complete onboarding — skip team setup for now

---

## Step 2: Create the Demo Event Type

1. In the Cal.com dashboard, click **"+ New event type"**
2. Select **"One-on-One"**
3. Fill in:

| Field | Value |
|-------|-------|
| **Title** | SmartBook AI Demo — 15 minutes |
| **URL slug** | `smartbook-demo` |
| **Duration** | 15 minutes |
| **Location** | Google Meet (auto-generated) or Zoom |
| **Description** | See copy below |

---

## Step 3: Booking Page Description Copy

Paste this into the Cal.com event description field:

```
See SmartBook AI answer a live call in your business's name — in real time.

In 15 minutes, we'll:
✅ Show you exactly what callers hear when SmartBook answers
✅ Walk through how it books directly into your calendar (Google, Calendly, whatever you use)
✅ Answer any questions about setup, pricing, and cancellation

No slides. No pitch deck. Just a live demo so you can decide if it's right for you.

SmartBook AI is $497/month, no contract. Most clients recover the cost within the first 2 weeks.

Pick a time that works — we'll send you a confirmation with the meeting link.
```

---

## Step 4: Configure Availability

1. Go to **Availability** in the sidebar
2. Set your demo availability (recommended):
   - Monday–Friday: 9:00 AM – 5:00 PM
   - Weekends: Off
3. Add **buffer time**: 10 minutes after each meeting (prevents back-to-back demos)
4. Set **minimum notice**: 2 hours (prevents last-minute surprises)

---

## Step 5: Get Your Booking URL

After saving the event type, your URL will be:

```
https://cal.com/[YOUR-USERNAME]/smartbook-demo
```

Example: `https://cal.com/smartbookai/smartbook-demo`

**Copy this URL — you'll need it for Step 6.**

---

## Step 6: Add the Booking URL to Alex's Vapi System Prompt

In Alex's system prompt (Vapi assistant `95e7c636-f8e6-4801-8866-fca9d5d475d3`), the DEMO BOOKING section now reads:

> "If the prospect expresses interest, offer to text them the demo booking link:
> **https://cal.com/[YOUR-USERNAME]/smartbook-demo**
>
> Script: 'Great — I can text you a link right now to book a free 15-minute demo with our team. It takes 30 seconds to pick a time. What's your mobile number so I can send it?'"

Once you have your actual Cal.com URL:
1. Go to Vapi dashboard → Assistants → Alex
2. Find the `DEMO BOOKING LINK` placeholder in the system prompt
3. Replace `[CAL_COM_BOOKING_URL]` with your real URL
4. Or use the API: `PATCH https://api.vapi.ai/assistant/95e7c636-f8e6-4801-8866-fca9d5d475d3`

---

## Step 7: Optional — Enable Confirmations & Reminders

1. In the event type settings → **"Apps"** tab
2. Enable **Email confirmation** (Cal.com sends this automatically)
3. Add **SMS reminder** via Twilio integration (optional but recommended)
4. Connect **Google Calendar** so demos block your real calendar

---

## Quick Reference

| Item | Value |
|------|-------|
| Platform | cal.com (free tier) |
| Event name | SmartBook AI Demo — 15 minutes |
| Duration | 15 min |
| Slug | `/smartbook-demo` |
| Full URL template | `https://cal.com/[username]/smartbook-demo` |
| Vapi assistant ID | `95e7c636-f8e6-4801-8866-fca9d5d475d3` |
| Prompt placeholder | `[CAL_COM_BOOKING_URL]` |

**Next action:** Create the account, grab your URL, then update the placeholder in Alex's prompt.
