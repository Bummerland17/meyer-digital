# SmartBook AI - Cold Calling Setup Instructions

## ⚠️ Manual Step Required: Vapi.ai Signup

Vapi.ai uses Cloudflare Turnstile CAPTCHA which cannot be bypassed by automation.
Wolfgang must complete signup manually (takes ~2 minutes).

---

## Step 1: Sign Up for Vapi.ai

1. Go to: **https://dashboard.vapi.ai/register**
2. Use "Email" tab (not Google/GitHub/Discord)
   - Email: `hello@pantrymate.net`
   - Password: `SmartBook2026!Ai#`
3. Verify your email if a confirmation is sent
4. After login, go to: **Settings → API Keys**
5. Click "Create Key" → Copy the key

---

## Step 2: Add API Key to .env

```bash
echo "VAPI_API_KEY=your_key_here" >> /root/.openclaw/workspace/.env
```

---

## Step 3: Deploy Everything (1 command)

```bash
bash /root/.openclaw/workspace/scripts/vapi-deploy.sh
```

This will:
- ✅ Create the "Alex" AI agent with the SmartBook AI script
- ✅ Request a US phone number for outbound calls
- ✅ Save all credentials to .env

---

## Step 4: Start Calls at 9 AM Mountain Time

```bash
# Dry run first (no actual calls):
node /root/.openclaw/workspace/scripts/vapi-start-calls.js --dry-run

# Real calls:
node /root/.openclaw/workspace/scripts/vapi-start-calls.js

# Limit to first 10:
node /root/.openclaw/workspace/scripts/vapi-start-calls.js --limit=10
```

---

## What's Already Ready

| File | Description |
|------|-------------|
| `assets/call-queue.json` | 72 leads ready to call (dental, gym, spa) |
| `assets/vapi-agent-config.json` | Alex's full configuration |
| `scripts/vapi-deploy.sh` | One-command deployment |
| `scripts/vapi-start-calls.js` | Outbound call launcher with safety checks |

---

## Lead Summary

- **35 dental offices** (Phoenix, AZ)
- **20 gyms/spas** (Phoenix, AZ)  
- **17 fitness businesses** (batch 2)
- **Total: 72 calls**
- **All scheduled: 9:00 AM Mountain Time (16:00 UTC)**
- **Timezone: America/Phoenix (no DST)**

---

## Pricing Reference

- Vapi: ~$0.05–0.10/min per call
- 72 calls × avg 2 min = ~144 min × $0.07 = **~$10 total**
- Free trial credits should cover initial batch

---

## Monitor Results

After calls start: https://dashboard.vapi.ai/calls

Look for:
- Calls where lead asked for email → follow up personally
- "Not interested" → mark in CRM
- No answer → retry next day
