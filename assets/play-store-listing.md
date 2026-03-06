# PantryMate — Google Play Store Listing

---

## App Details

| Field | Value |
|---|---|
| **Package name** | `com.pantrymate.app` |
| **App name** | PantryMate — Meal Planner |
| **Category** | Food & Drink |
| **Content rating** | Everyone |
| **Privacy policy URL** | https://pantrymate.net/privacy |

---

## Short Description
*(80 characters max — Play Store shows this under the app name)*

```
Scan your pantry. Get dinner ideas in 30 seconds. Stop wasting food.
```
*(69 chars — within limit ✅)*

---

## Full Description
*(4000 characters max — use formatting; no markdown renders, use plain line breaks)*

```
🥦 What's for dinner? PantryMate already knows.

The average household throws away $1,500 of food every year — not because people don't care, but because nobody knows what's in the back of the fridge until it's already gone bad. And staring at a full pantry wondering what to cook is its own special kind of exhausting.

PantryMate fixes both problems in under a minute.

── HOW IT WORKS ──

1. Scan or type your ingredients (takes 30 seconds)
2. PantryMate matches them to real, practical recipes
3. Cook something good tonight — with what you already have

No special shopping trips. No wasted ingredients. No decision fatigue.

── KEY FEATURES ──

🔍 Smart Pantry Scanning
Quickly log what you have at home — fresh produce, pantry staples, leftovers. PantryMate remembers your inventory so you never start from scratch.

🍽️ Recipe Matching in Seconds
Get tailored recipe suggestions based on exactly what's in your pantry right now. Filter by cuisine, dietary preference, cooking time, and more.

🗓️ Weekly Meal Planning
Plan your whole week in minutes. Drag recipes onto your meal calendar, auto-generate a shopping list for what's missing, and stop over-buying.

📉 Food Waste Tracker
See which ingredients you use vs. throw away. PantryMate helps you build smarter shopping habits over time — saving money and reducing waste.

🔔 Expiry Reminders
Add expiry dates to your pantry items and get nudged before things go bad. Use it or lose it — PantryMate makes sure you use it.

📱 Works Offline
Your pantry data is yours. Core features work without an internet connection.

── PRO PLUS ──

Unlock the full PantryMate experience:

• Unlimited pantry items (free plan: up to 30)
• Advanced recipe filtering & cuisine explorer
• Household sharing — sync pantry with your partner or family
• Priority recipe matching with nutritional breakdowns
• Export shopping lists to Apple Reminders, Google Tasks, or PDF
• Ad-free experience

Pro Plus is a monthly or annual subscription, billed through Google Play. Cancel anytime — no tricks, no dark patterns.

── WHO IT'S FOR ──

✓ Busy parents who cook for a family and hate wasting groceries
✓ Singles and couples trying to eat well without over-shopping
✓ Meal-prep enthusiasts who want structure without spreadsheets
✓ Anyone who opens the fridge, sighs, and orders takeout instead

── HONEST NOTES ──

PantryMate is built by a small team that actually uses it. We're not trying to gamify cooking or send you 40 push notifications a day. We want to make the "what's for dinner?" question disappear — and help you waste less food in the process.

If something doesn't work the way you expect, email us. We read every message.

── PRIVACY ──

We collect only what we need: your email address and your pantry data. We don't sell your data. Full policy at pantrymate.net/privacy.

Download PantryMate free. Your pantry's been waiting.
```

*(Approx 2,850 chars — well within 4000 limit ✅)*

---

## Tags / Keywords
*(Use in Play Console keyword fields and ASO tools)*

- meal planning
- meal planner
- recipes
- food waste
- pantry tracker
- pantry organizer
- cooking
- dinner ideas
- grocery list
- what's for dinner
- weekly meal plan
- food inventory

---

## Screenshots — Exactly 8 Scenes
*(Play requires min 2, supports up to 8. Recommended: 1080×1920px portrait)*

| # | Screen | What to Show | Key UI Elements |
|---|---|---|---|
| 1 | **Onboarding / Hero** | "What's for dinner? PantryMate knows." | Splash with pantry scan prompt, tagline overlay |
| 2 | **Pantry Input** | User adding ingredients (tomatoes, pasta, garlic, chicken) | Ingredient chips, add button, search field |
| 3 | **Recipe Matches** | Grid of recipe cards generated from pantry | Recipe thumbnails, "3 ingredients match" badges, cook time |
| 4 | **Recipe Detail** | Full recipe view: ingredients, steps, macros | Ingredient checklist (highlighting what user has vs. needs), step-by-step instructions |
| 5 | **Meal Calendar** | Weekly meal plan filled in Mon–Sun | Drag-and-drop calendar, breakfast/lunch/dinner slots, colorful recipe cards |
| 6 | **Shopping List** | Auto-generated shopping list for the week | Grouped by store section (produce, dairy, pantry), checkboxes |
| 7 | **Expiry Tracker** | Items sorted by days-until-expiry, some flagged red | Warning badges, "use soon" section at top, food waste savings counter |
| 8 | **Pro Plus Upgrade** | Paywall / upgrade screen | Feature comparison (Free vs Pro Plus), monthly/annual price toggle, CTA button |

**Screenshot tips:**
- Use real content (real recipe names, real ingredient lists) — not Lorem Ipsum
- Screenshot 1 should work as a "featured" image — bold text, minimal UI
- Add subtle drop shadows or device frames for polish (optional but recommended)
- Localize screenshots if targeting non-English markets later

---

## Feature Graphic
*(1024×500px banner — required for Play Store)*

**Description for designer:**

- **Background:** Deep forest green (`#1B4332`) or warm cream (`#FEFAE0`) — earthy, food-forward
- **Left side (60%):** Stylized illustration of an open pantry/fridge with colorful ingredient icons floating out (tomatoes, herbs, eggs, pasta)
- **Right side (40%):** App name "PantryMate" in bold white/dark sans-serif, subtitle "Meal Planner" smaller underneath, small tagline: "Cook what you have."
- **Accent color:** Warm amber/orange (`#F4A261`) for highlights
- **No screenshots in the feature graphic** — Play often displays it without the app icon
- **Safe zone:** Keep all text within center 924×400px (50px inset each side)

---

## Release Notes (First Version)
*(What's new — shown on Play Store)*

```
Welcome to PantryMate! 🎉

- Scan your pantry and get recipe ideas in seconds
- Weekly meal planner with drag-and-drop simplicity
- Auto-generated shopping lists
- Expiry date reminders
- Pro Plus for unlimited pantry + household sharing

This is v1.0 — we're just getting started. Found a bug? Email us at hello@pantrymate.net
```

---

## Manual Steps for Wolfgang

### 1. Google Play Console Account ($25 one-time)
- Go to: https://play.google.com/console/signup
- Pay the $25 registration fee (Google account required)
- Takes 24–48h for account approval after ID verification

### 2. Create the App in Play Console
- New app → App name: "PantryMate — Meal Planner"
- Default language: English (United States)
- App or Game: App
- Free or paid: Free (with in-app purchases)
- Agree to declarations

### 3. Add GitHub Secrets (for CI/CD signing)
Run `scripts/generate-keystore.sh` first, then add to:
**Repo → Settings → Secrets and variables → Actions**
- `KEYSTORE_FILE` — base64-encoded keystore file
- `KEY_ALIAS` — `pantrymate`
- `KEY_PASSWORD` — your key password
- `STORE_PASSWORD` — your keystore password

### 4. Upload AAB
- After a successful GitHub Actions build, download the artifact
- Play Console → Production → Create new release → Upload AAB

### 5. Fill Store Listing
- Use content from this file
- Upload screenshots (8 recommended)
- Upload feature graphic (1024×500px)
- Add privacy policy URL: https://pantrymate.net/privacy

### 6. Content Rating
- Play Console → Content rating → Start questionnaire
- Answer: no violence, no adult content, no user-generated content (if applicable)
- Expected rating: Everyone

### 7. Review & Submit
- Play Console will flag any missing items in the checklist
- First review typically takes 3–7 days

---

*Generated for PantryMate v1.0 launch — March 2026*
