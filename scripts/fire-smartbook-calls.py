#!/usr/bin/env python3
"""SmartBook AI — Daily outbound call campaign — fires 10 leads/day at 16:00 UTC (9am MST)
Vapi daily limit ~10 outbound calls. Tracks progress across days."""
import requests, json, time
from datetime import datetime, timezone

VAPI_KEY = open('/root/.openclaw/workspace/.env').read().split('VAPI_API_KEY=')[1].split('\n')[0].strip()
# Use Twilio number for outbound (own number, higher limits)
PHONE_NUMBER_ID = "23eacc2d-e19d-4410-98dd-aef4ab564b63"  # +18449940365 Twilio
ALEX_AGENT_ID = "95e7c636-f8e6-4801-8866-fca9d5d475d3"
BOT_TOKEN = json.load(open('/root/.openclaw/openclaw.json'))['channels']['telegram']['botToken']
TELEGRAM_CHAT_ID = "8654703697"
RESULTS_FILE = '/root/.openclaw/workspace/assets/call-results-smartbook.json'
QUEUE_FILE = '/root/.openclaw/workspace/assets/smartbook-call-queue.json'
DAILY_LIMIT = 10  # Vapi outbound daily limit

def send_telegram(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                     json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=5)
    except: pass

def fire_call(lead):
    name = lead.get('name', 'the practice')
    payload = {
        "phoneNumberId": PHONE_NUMBER_ID,
        "assistantId": ALEX_AGENT_ID,
        "customer": {"number": lead["phone"], "name": name},
        "assistantOverrides": {
            "firstMessage": f"Hi, this is Alex calling from SmartBook AI — is this {name}? Quick 60-second question about your front desk coverage — is now an okay time?"
        }
    }
    r = requests.post("https://api.vapi.ai/call",
                      headers={"Authorization": f"Bearer {VAPI_KEY}"},
                      json=payload, timeout=15)
    result = r.json()
    success = 'id' in result
    ok = '✅' if success else '❌'
    reason = result.get('id', result.get('message', 'ERROR'))[:30]
    print(f"{ok} {name} ({lead.get('city','?')}) → {reason}")
    return success, result

if __name__ == "__main__":
    # Load queue
    with open(QUEUE_FILE) as f:
        queue_data = json.load(f)
    all_leads = queue_data.get('leads', [])
    
    # Load existing results to skip already-called leads
    try:
        with open(RESULTS_FILE) as f:
            past_results = json.load(f)
        called_phones = {r.get('phone') for r in past_results if r.get('success')}
    except:
        past_results = []
        called_phones = set()
    
    # Filter to uncalled leads
    pending = [l for l in all_leads if l.get('phone') not in called_phones]
    batch = pending[:DAILY_LIMIT]
    
    if not batch:
        print("✅ All leads called! Queue exhausted.")
        send_telegram("✅ SmartBook AI: All leads in queue have been called.")
        exit()
    
    print(f"\n🔥 Daily SmartBook AI call batch — {len(batch)}/{len(pending)} remaining leads\n{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n")
    send_telegram(f"📞 *SmartBook AI calling batch starting*\n{len(batch)} leads today | {len(pending)-len(batch)} remaining after this\nAlex is dialing now — warm leads flagged immediately.")
    
    results = []
    fired = 0
    for i, lead in enumerate(batch):
        success, result = fire_call(lead)
        if success: fired += 1
        results.append({
            "lead": lead.get('name'),
            "phone": lead.get('phone'),
            "city": lead.get('city'),
            "type": lead.get('type'),
            "success": success,
            "call_id": result.get('id'),
            "error": result.get('message') if not success else None,
            "fired_at": datetime.now(timezone.utc).isoformat()
        })
        if i < len(batch) - 1:
            time.sleep(15)  # 15s between calls
    
    # Save results
    past_results.extend(results)
    with open(RESULTS_FILE, 'w') as f:
        json.dump(past_results, f, indent=2)
    
    total_called = len([r for r in past_results if r.get('success')])
    days_remaining = -(-len(pending - set(r.get('phone') for r in results if r.get('success'))) // DAILY_LIMIT)
    
    summary = f"📞 *Daily batch complete*\n{fired}/{len(batch)} calls fired today\n{len(pending)-len(batch)} leads still pending (~{days_remaining} more days)\nResults → call-results-smartbook.json"
    print(f"\n{summary}")
    send_telegram(summary)
