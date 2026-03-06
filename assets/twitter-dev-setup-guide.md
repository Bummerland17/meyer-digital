# X/Twitter Developer App Setup Guide for PantryMate + Postiz

## Overview
To schedule posts to X (Twitter) via Postiz, you need a Twitter Developer App with OAuth 2.0 credentials. This guide walks through every step.

**Time required:** ~30 minutes
**Cost:** Free (Basic tier is sufficient for scheduling)

---

## Step 1: Create a Twitter Developer Account

1. Go to: **https://developer.twitter.com/en/portal/dashboard**
2. Log in with your Twitter/X account (create one at x.com if needed — use @PantryMateApp or similar)
3. If you don't have developer access yet, click **"Sign up for Free Account"**
4. Fill in:
   - **Use case:** "I'm building a tool to schedule and publish social media posts for my app, PantryMate (pantrymate.net)"
   - Be honest and specific — generic answers get flagged
5. Accept the Developer Agreement
6. Verify your email if prompted

---

## Step 2: Create a New Project

1. In the Developer Portal dashboard, click **"+ Add Project"**
2. **Project name:** PantryMate Social
3. **Use case:** Select "Making a bot" or "Creator tools" — closest to scheduling
4. **Project description:** "Scheduled content publishing for PantryMate (pantrymate.net), a food/cooking app. Posting food tips and product updates."
5. Click through to complete project creation

---

## Step 3: Create a New App Within the Project

1. After creating the project, you'll be prompted to **create an App**
2. **App name:** PantryMate Postiz Scheduler
3. **App environment:** Select **Production** (not Development — Production allows OAuth to work properly)
4. Click **"Create"**

---

## Step 4: Configure App Settings (Critical)

After app creation, go to **App Settings → User authentication settings**:

1. Click **"Set up"** next to User authentication settings
2. Configure:
   - **App permissions:** Read and Write (required for posting)
   - **Type of App:** Web App, Automated App or Bot
   - **Callback URI / Redirect URL:**
     ```
     http://103.98.214.106:4007/integrations/social/x/callback
     ```
   - **Website URL:** https://pantrymate.net
3. Click **Save**

---

## Step 5: Get Your API Keys and Tokens

Go to **App Settings → Keys and Tokens**:

You need these four values:

| Key | Where to find it |
|---|---|
| API Key (Consumer Key) | "Consumer Keys" section — click "Regenerate" if needed |
| API Key Secret (Consumer Secret) | Same section as API Key |
| Bearer Token | "Authentication Tokens" section |
| Access Token + Secret | Optional for now — Postiz uses OAuth flow |

**Copy these immediately** — the Secret only shows once. Paste into a secure file.

---

## Step 6: Add Keys to Postiz Docker Compose

SSH into your server and edit the Postiz config:

```bash
cd /root/.openclaw/workspace/postiz
nano docker-compose.yaml
```

Find the environment variables section and add/update:

```yaml
environment:
  # ... existing variables ...
  X_API_KEY: "your_api_key_here"
  X_API_SECRET: "your_api_key_secret_here"
  # These may also be labeled as:
  # TWITTER_API_KEY
  # TWITTER_API_SECRET
```

**Save the file** (Ctrl+X, Y, Enter in nano)

---

## Step 7: Restart Postiz

```bash
cd /root/.openclaw/workspace/postiz
docker compose restart postiz
```

Wait ~30 seconds for the container to fully restart.

Verify it's running:
```bash
docker compose ps
```

---

## Step 8: Connect Your X Account via Postiz OAuth

1. Go to **http://103.98.214.106:4007**
2. Log in with hello@pantrymate.net / PantryMate2026!
3. Click **"Add Channel"** (or the "+" button for new channels)
4. Select **"X"**
5. Click **"Connect"**
6. A Twitter OAuth popup will appear
7. Log in with the @PantryMate (or your X account)
8. Click **"Authorize app"**
9. You'll be redirected back to Postiz with X connected

---

## Step 9: Verify Connection

1. In Postiz, you should see the X channel in your connected channels list
2. Try creating a test post: click **"New Post"** → select X → write something short → schedule for 1 minute from now
3. Check your X profile to confirm it published

---

## Troubleshooting

**"Callback URL mismatch" error:**
- Double-check the Callback URL in Step 4 exactly matches: `http://103.98.214.106:4007/integrations/social/x/callback`
- No trailing slash, exact match

**"App not authorized for Read/Write":**
- Go back to App Settings → User authentication settings
- Confirm permissions are set to "Read and Write"
- After changing permissions, regenerate Access Tokens (old ones don't inherit new permissions)

**OAuth popup doesn't redirect back:**
- The server at 103.98.214.106:4007 must be accessible from the browser you're using
- If testing locally, make sure the port is open

**API Key not found in docker-compose:**
- Check the Postiz documentation for the exact environment variable names
- Run `docker compose exec postiz env | grep -i twitter` to see what's currently set

---

## Free Tier Limits (Basic Dev Account)

| Limit | Value |
|---|---|
| App posts per month | 1,500 |
| Posts per 15 minutes | 300 |
| Reads per month | 500,000 |

1,500 posts/month is plenty for a 2x/day schedule (30 days × 2 = 60 posts/month).

---

## What You'll Have When Done

- Postiz connected to X/Twitter
- All 30 days of PantryMate X content pre-loaded and scheduled
- Posts auto-publishing at 07:00 UTC and 16:00 UTC daily
- No manual posting required for 30 days
