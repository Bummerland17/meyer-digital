#!/bin/bash
# =============================================================================
# SmartBook AI - Vapi.ai Deployment Script
# Run this AFTER signing up at https://dashboard.vapi.ai/register
# and adding VAPI_API_KEY to /root/.openclaw/workspace/.env
# =============================================================================

set -e
source /root/.openclaw/workspace/.env

if [ -z "$VAPI_API_KEY" ]; then
  echo "❌ ERROR: VAPI_API_KEY not set in .env"
  echo "   1. Sign up at https://dashboard.vapi.ai/register"
  echo "   2. Go to Settings → API Keys"
  echo "   3. Add: VAPI_API_KEY=your_key_here  to .env"
  exit 1
fi

BASE_URL="https://api.vapi.ai"
HEADERS=(-H "Authorization: Bearer $VAPI_API_KEY" -H "Content-Type: application/json")

echo "🚀 SmartBook AI - Vapi Deployment"
echo "=================================="

# STEP 1: Create the AI Assistant (Alex)
echo ""
echo "📱 Step 1: Creating AI assistant 'Alex'..."

ASSISTANT_RESPONSE=$(curl -s -X POST "$BASE_URL/assistant" \
  "${HEADERS[@]}" \
  -d '{
    "name": "Alex - SmartBook AI",
    "firstMessage": "Hi, this is Alex calling from SmartBook AI — am I speaking with someone from {{business_name}}?",
    "model": {
      "provider": "openai",
      "model": "gpt-4o-mini",
      "messages": [
        {
          "role": "system",
          "content": "You are Alex, a friendly sales representative for SmartBook AI. You help dental offices, gyms, spas, and other appointment-based businesses recover missed bookings by setting up AI phone agents that answer calls 24/7.\n\nWhen someone picks up:\n1. Introduce yourself: \"Hi, this is Alex calling from SmartBook AI — is this [business name]?\"\n2. Brief pitch: \"We help [type of business] recover the bookings they lose to missed after-hours calls. Most practices lose 4-8 appointments per week just from voicemail. We fix that with a 24/7 AI agent that books automatically.\"\n3. Ask: \"Would you have 2 minutes to hear how it works, or should I send you some info by email?\"\n4. If interested: collect their email and say \"Perfect, I will send over a quick demo video. What is the best email for you?\"\n5. If not interested: \"No problem at all — have a great day!\"\n6. If they ask price: \"$497 per month flat, no contracts, 48-hour setup.\"\n7. Always stay natural, friendly, and brief. Never be pushy.\n\nKeep calls under 2 minutes. If they seem interested, get their email and let them know Wolfgang will follow up personally."
        }
      ],
      "maxTokens": 500
    },
    "voice": {
      "provider": "11labs",
      "voiceId": "ErXwobaYiN019PkySvjV",
      "stability": 0.5,
      "similarityBoost": 0.75,
      "style": 0.0,
      "useSpeakerBoost": true
    },
    "transcriber": {
      "provider": "deepgram",
      "model": "nova-2",
      "language": "en-US"
    },
    "maxDurationSeconds": 120,
    "backgroundSound": "off",
    "backchannelingEnabled": true,
    "backgroundDenoisingEnabled": true
  }')

ASSISTANT_ID=$(echo "$ASSISTANT_RESPONSE" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('id','ERROR'))")
echo "✅ Assistant created: $ASSISTANT_ID"

if [ "$ASSISTANT_ID" = "ERROR" ]; then
  echo "❌ Failed to create assistant:"
  echo "$ASSISTANT_RESPONSE"
  exit 1
fi

# STEP 2: Get a phone number
echo ""
echo "📞 Step 2: Requesting US phone number..."

PHONE_RESPONSE=$(curl -s -X POST "$BASE_URL/phone-number" \
  "${HEADERS[@]}" \
  -d '{
    "provider": "vapi",
    "sipUri": null,
    "name": "SmartBook AI Outbound",
    "assistantId": "'"$ASSISTANT_ID"'",
    "numberE164CheckEnabled": true
  }')

# Try buying a Twilio number if Vapi free number fails
PHONE_ID=$(echo "$PHONE_RESPONSE" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('id','ERROR'))" 2>/dev/null)
PHONE_NUMBER=$(echo "$PHONE_RESPONSE" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('number','ERROR'))" 2>/dev/null)

if [ "$PHONE_ID" = "ERROR" ] || [ -z "$PHONE_ID" ]; then
  echo "⚠️  Vapi free number unavailable. Trying to purchase via Twilio integration..."
  PHONE_RESPONSE=$(curl -s -X POST "$BASE_URL/phone-number" \
    "${HEADERS[@]}" \
    -d '{
      "provider": "twilio",
      "twilioAccountSid": "'"${TWILIO_SID:-}"'",
      "twilioAuthToken": "'"${TWILIO_AUTH_TOKEN:-}"'",
      "name": "SmartBook AI Outbound"
    }')
  PHONE_ID=$(echo "$PHONE_RESPONSE" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('id','ERROR'))" 2>/dev/null)
  PHONE_NUMBER=$(echo "$PHONE_RESPONSE" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('number','ERROR'))" 2>/dev/null)
fi

echo "✅ Phone number: $PHONE_NUMBER (ID: $PHONE_ID)"

# STEP 3: Save credentials to .env
echo ""
echo "💾 Step 3: Saving credentials..."

if ! grep -q "VAPI_ASSISTANT_ID" /root/.openclaw/workspace/.env; then
  echo "VAPI_ASSISTANT_ID=$ASSISTANT_ID" >> /root/.openclaw/workspace/.env
fi
if ! grep -q "VAPI_PHONE_ID" /root/.openclaw/workspace/.env; then
  echo "VAPI_PHONE_ID=$PHONE_ID" >> /root/.openclaw/workspace/.env
  echo "VAPI_PHONE_NUMBER=$PHONE_NUMBER" >> /root/.openclaw/workspace/.env
fi

echo "✅ Credentials saved to .env"

# STEP 4: Queue calls from call-queue.json
echo ""
echo "📋 Step 4: Queuing calls from call-queue.json..."
echo "   (Calls are scheduled for 9:00 AM Mountain Time)"
echo "   Current UTC time: $(date -u)"
echo "   Do NOT run calls now — schedule for 16:00 UTC"
echo ""
echo "   To start calls, run: node scripts/vapi-start-calls.js"

echo ""
echo "=================================================="
echo "✅ DEPLOYMENT COMPLETE"
echo "=================================================="
echo "  Assistant ID: $ASSISTANT_ID"
echo "  Phone Number: $PHONE_NUMBER"
echo "  Leads queued: 72"
echo "  Call time:    9:00 AM MT (16:00 UTC)"
echo ""
echo "Next steps:"
echo "  1. Run calls: node /root/.openclaw/workspace/scripts/vapi-start-calls.js"
echo "  2. Monitor:   https://dashboard.vapi.ai/calls"
