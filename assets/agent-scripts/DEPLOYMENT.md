# 🚀 DEPLOYMENT GUIDE — Wolfgang Meyer's AI Sales Agents
## Vapi.ai — 5 Agent Setup

---

## Prerequisites

Before you start, you'll need:
- **Vapi.ai account** → [https://vapi.ai](https://vapi.ai)
- **Vapi API key** (from your Vapi dashboard under Settings → API Keys)
- **ElevenLabs account** connected to Vapi (for voice cloning/selection)
- A terminal or API client (curl examples below work in any Unix shell)
- The 5 JSON files in this folder

---

## Step 1 — Set Your API Key

Set your Vapi API key as an environment variable so you don't have to paste it into every command:

```bash
export VAPI_API_KEY="your_vapi_api_key_here"
```

> 💡 Add this to your `~/.bashrc` or `~/.zshrc` to persist it across sessions.

---

## Step 2 — Verify Voice IDs (ElevenLabs)

Each agent uses an ElevenLabs voice. The voice IDs in the JSON files are defaults — verify these are still valid in your ElevenLabs library or swap in your preferred voices.

| Agent | Voice Name | Voice ID |
|-------|-----------|----------|
| Alex  | Adam      | `pNInz6obpgDQGcFmaJgB` |
| Maya  | Bella     | `EXAVITQu4vr4xnSDxMaL` |
| Dev   | Arnold    | `VR6AewLTigWG4xSOukaG` |
| Rex   | Josh      | `TxGEqnHWrfWFTfGW9XjX` |
| Kai   | Sam       | `yoZ06aMxZJJ28mfd3POQ`  |

To swap a voice, edit the `voiceId` field in the JSON file before deploying.

---

## Step 3 — Deploy Each Agent

Run these curl commands from the directory containing the JSON files. Each command creates one assistant in Vapi.

### 🤖 Agent 1: Alex — SmartBook AI

```bash
curl -X POST https://api.vapi.ai/assistant \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d @agent-alex.json
```

Save the returned `id` — you'll need it to make calls with Alex.

---

### 🤖 Agent 2: Maya — Local SEO & Reputation

```bash
curl -X POST https://api.vapi.ai/assistant \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d @agent-maya.json
```

---

### 🤖 Agent 3: Dev — App Development Discovery

```bash
curl -X POST https://api.vapi.ai/assistant \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d @agent-dev.json
```

---

### 🤖 Agent 4: Rex — RE Seller Outreach

```bash
curl -X POST https://api.vapi.ai/assistant \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d @agent-rex.json
```

---

### 🤖 Agent 5: Kai — RE Buyer Outreach

```bash
curl -X POST https://api.vapi.ai/assistant \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d @agent-kai.json
```

---

## Step 4 — Note Your Assistant IDs

After each POST, Vapi returns a JSON object with an `id` field. Save them:

```
Alex  → asst_xxxxxxxxxxxxxxxx
Maya  → asst_xxxxxxxxxxxxxxxx
Dev   → asst_xxxxxxxxxxxxxxxx
Rex   → asst_xxxxxxxxxxxxxxxx
Kai   → asst_xxxxxxxxxxxxxxxx
```

---

## Step 5 — Make Outbound Calls

Use these curl templates to trigger outbound calls. Replace `ASSISTANT_ID` with the relevant agent's ID, and fill in the phone numbers.

### Single outbound call template:

```bash
curl -X POST https://api.vapi.ai/call/phone \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "assistantId": "ASSISTANT_ID",
    "customer": {
      "number": "+1XXXXXXXXXX",
      "name": "Contact Name"
    },
    "phoneNumberId": "YOUR_VAPI_PHONE_NUMBER_ID"
  }'
```

> 💡 You need to provision a phone number in Vapi first (Settings → Phone Numbers → Buy Number). This gives you the `phoneNumberId`.

---

### For Rex (seller calls) — include property address in metadata:

```bash
curl -X POST https://api.vapi.ai/call/phone \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "assistantId": "REX_ASSISTANT_ID",
    "customer": {
      "number": "+1XXXXXXXXXX",
      "name": "Owner Name"
    },
    "phoneNumberId": "YOUR_VAPI_PHONE_NUMBER_ID",
    "assistantOverrides": {
      "variableValues": {
        "owner_name": "John Smith",
        "property_address": "1234 W Camelback Rd, Phoenix AZ 85013"
      }
    }
  }'
```

> ⚠️ For Rex and Kai, make sure you insert the correct owner name and property address via `variableValues` so the first message is personalized.

---

## Step 6 — Bulk Calling (with a CSV list)

For calling from a lead list, use this bash script pattern:

```bash
#!/bin/bash
# bulk-call.sh — Call a list of prospects
# CSV format: phone_number,contact_name,extra_field
# Usage: ./bulk-call.sh agent-rex ASSISTANT_ID leads.csv

ASSISTANT_ID=$2
CSV_FILE=$3
PHONE_NUMBER_ID="YOUR_VAPI_PHONE_NUMBER_ID"

while IFS=',' read -r phone name address; do
  echo "Calling $name at $phone..."
  curl -s -X POST https://api.vapi.ai/call/phone \
    -H "Authorization: Bearer $VAPI_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"assistantId\": \"$ASSISTANT_ID\",
      \"customer\": {\"number\": \"$phone\", \"name\": \"$name\"},
      \"phoneNumberId\": \"$PHONE_NUMBER_ID\",
      \"assistantOverrides\": {
        \"variableValues\": {
          \"owner_name\": \"$name\",
          \"property_address\": \"$address\"
        }
      }
    }"
  sleep 2  # Rate limit: 2 seconds between calls
done < "$CSV_FILE"
```

---

## Step 7 — Retrieve Call Logs & Summaries

### List recent calls:
```bash
curl https://api.vapi.ai/call \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  | jq '.[] | {id: .id, status: .status, duration: .duration, summary: .summary}'
```

### Get details for a specific call:
```bash
curl https://api.vapi.ai/call/CALL_ID \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  | jq '{transcript: .transcript, summary: .summary, recordingUrl: .recordingUrl}'
```

### Get recording download URL:
```bash
curl https://api.vapi.ai/call/CALL_ID \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  | jq '.recordingUrl'
```

---

## Step 8 — Update an Agent's Prompt

To update a deployed agent (e.g., refine a prompt or change voice):

```bash
curl -X PATCH https://api.vapi.ai/assistant/ASSISTANT_ID \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": {
      "systemPrompt": "Updated prompt text here..."
    }
  }'
```

---

## Step 9 — Delete an Agent

```bash
curl -X DELETE https://api.vapi.ai/assistant/ASSISTANT_ID \
  -H "Authorization: Bearer $VAPI_API_KEY"
```

---

## Agent Quick Reference

| Agent | File | Purpose | Price Point | Goal |
|-------|------|---------|-------------|------|
| Alex  | agent-alex.json | SmartBook AI sales | $497/mo | Close or capture email |
| Maya  | agent-maya.json | Local SEO & Reviews | $400/mo | Close or send payment link |
| Dev   | agent-dev.json  | App dev qualification | $1,500–$3,500 | Book discovery call with Wolfgang |
| Rex   | agent-rex.json  | RE seller outreach | N/A | Qualify seller, collect email for offer |
| Kai   | agent-kai.json  | RE buyer list building | N/A | Add investor to buyer list |

---

## Compliance Notes ⚠️

- **TCPA Compliance**: Only call numbers you have consent to contact, or that are on a properly acquired B2B or public-record list. Consult a telemarketing attorney if unsure.
- **Do-Not-Call (DNC) List**: Scrub your lists against the National DNC Registry before calling consumers.
- **AI Disclosure**: All agents are configured to disclose they are AI if directly asked. Do not modify this behavior.
- **Real Estate**: Rex and Kai call property owners and investors — ensure your data sources (MLS, public record, etc.) are used in compliance with their terms.
- **Recording**: All calls are recorded via Vapi. Ensure you comply with one-party or two-party consent laws in your state. Arizona is a one-party consent state.

---

## Support

- **Vapi docs**: [https://docs.vapi.ai](https://docs.vapi.ai)
- **ElevenLabs voices**: [https://elevenlabs.io/voice-library](https://elevenlabs.io/voice-library)
- **Vapi Discord**: [https://discord.gg/pUFNcf37](https://discord.gg/pUFNcf37)
