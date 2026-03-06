#!/usr/bin/env python3
"""
Lila - Philippines Tourism Outbound Bulk Caller
Fires 50 calls via Vapi API, polls for results, logs to JSON.
Offer: Website $599 + SEO $200/mo
"""
import os, sys, json, time, re, requests
from datetime import datetime

# ─── Config ─────────────────────────────────────────────────────────────────
VAPI_API_KEY       = "0aaae7fe-be63-472a-a46d-5d9224e0fa89"
ASSISTANT_ID       = "1e54bb19-a423-4075-89b1-9e353bb2b6fe"   # Lila
PHONE_NUMBER_ID    = "23eacc2d-e19d-4410-98dd-aef4ab564b63"
LEADS_FILE         = "/root/.openclaw/workspace/real-estate/philippines-leads-2026-03-05.json"
RESULTS_FILE       = "/root/.openclaw/workspace/assets/lila-call-results-march6.json"
BATCH_SIZE         = 50
DELAY_BETWEEN_CALLS = 2   # seconds between each fire
POLL_INTERVAL      = 30   # seconds between status polls
MAX_POLL_ROUNDS    = 20   # 20 × 30s = 10 minutes max wait

HEADERS = {
    "Authorization": f"Bearer {VAPI_API_KEY}",
    "Content-Type": "application/json"
}

SYSTEM_PROMPT = """You are Lila, a friendly and professional digital marketing consultant calling tourism businesses in the Philippines.

Your goal: introduce a special website + SEO package and book a follow-up or get an email to send details.

OFFER:
- Professional Tourism Website: $599 one-time (custom-designed, mobile-friendly, booking-ready)
- SEO & Google Visibility Package: $200/month (rank on Google, get found by tourists)

KEY TALKING POINTS:
- Most travelers book online — businesses without a website lose customers to competitors
- A professional site builds trust and lets them take direct bookings (no commission to OTAs)
- SEO puts them in front of tourists searching Google for their type of activity/tour
- Package is affordable and designed specifically for Philippine tourism businesses

APPROACH:
1. Greet warmly, introduce yourself and the company
2. Ask if they currently have a website
3. Briefly explain how the package helps tourism businesses get more bookings
4. Pitch the offer: Website $599 + SEO $200/month
5. If interested: ask for their email to send full details, or offer to call back at a better time
6. Be respectful of their time; if not interested, thank them warmly and hang up

TONE: Friendly, conversational, confident but not pushy. Filipino-friendly (you can use light Taglish if it helps build rapport).

Always end the call gracefully once you have what you need or the prospect declines."""

def normalize_phone(raw: str) -> str:
    """Normalize Philippine numbers to E.164 format."""
    digits = re.sub(r'\D', '', raw)
    if digits.startswith('63'):
        return f'+{digits}'
    elif digits.startswith('0'):
        return f'+63{digits[1:]}'
    elif len(digits) == 10:
        return f'+63{digits}'
    return f'+{digits}'

def fire_call(lead: dict) -> dict:
    """Fire a single outbound call. Returns {call_id, lead_name, phone, status}."""
    raw_phone = lead.get('phone', '').strip()
    phone = normalize_phone(raw_phone)
    
    payload = {
        "assistantId": ASSISTANT_ID,
        "phoneNumberId": PHONE_NUMBER_ID,
        "customer": {"number": phone},
        "assistantOverrides": {
            "model": {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "messages": [{"role": "system", "content": SYSTEM_PROMPT}],
                "tools": [{
                    "type": "endCall",
                    "messages": [{"type": "request-start", "content": "Thank you so much! Have a wonderful day. Bye!"}]
                }]
            },
            "firstMessage": f"Hello! May I speak with the owner or manager of {lead.get('name', 'your business')}? Hi, this is Lila calling about a special digital package for tourism businesses here in the Philippines. Do you have just a minute?",
            "endCallMessage": "Thank you so much! Have a wonderful day. Goodbye!"
        }
    }
    
    try:
        resp = requests.post("https://api.vapi.ai/call", headers=HEADERS, json=payload, timeout=30)
        if resp.ok:
            data = resp.json()
            return {
                "call_id": data.get("id"),
                "lead_name": lead.get("name"),
                "phone_raw": raw_phone,
                "phone_e164": phone,
                "island": lead.get("island"),
                "business_type": lead.get("business_type"),
                "priority": lead.get("priority"),
                "fired_at": datetime.utcnow().isoformat() + "Z",
                "status": "fired",
                "api_status": data.get("status"),
            }
        else:
            return {
                "call_id": None,
                "lead_name": lead.get("name"),
                "phone_raw": raw_phone,
                "phone_e164": phone,
                "island": lead.get("island"),
                "business_type": lead.get("business_type"),
                "fired_at": datetime.utcnow().isoformat() + "Z",
                "status": "fire_error",
                "error": f"HTTP {resp.status_code}: {resp.text[:300]}"
            }
    except Exception as e:
        return {
            "call_id": None,
            "lead_name": lead.get("name"),
            "phone_raw": raw_phone,
            "phone_e164": phone,
            "island": lead.get("island"),
            "business_type": lead.get("business_type"),
            "fired_at": datetime.utcnow().isoformat() + "Z",
            "status": "fire_error",
            "error": str(e)
        }

def poll_call_status(call_id: str) -> dict:
    """Poll Vapi for call status/result."""
    try:
        resp = requests.get(f"https://api.vapi.ai/call/{call_id}", headers=HEADERS, timeout=15)
        if resp.ok:
            return resp.json()
    except:
        pass
    return {}

def main():
    print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Loading leads...")
    with open(LEADS_FILE) as f:
        all_leads = json.load(f)
    
    leads_with_phone = [l for l in all_leads if l.get('phone') and l['phone'].strip()]
    batch = leads_with_phone[:BATCH_SIZE]
    
    print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Firing {len(batch)} calls (Lila | Asst: {ASSISTANT_ID[:8]}... | Phone: {PHONE_NUMBER_ID[:8]}...)")
    
    results = []
    fired_count = 0
    error_count = 0
    
    # ── Phase 1: Fire all calls ──────────────────────────────────────────────
    for i, lead in enumerate(batch, 1):
        print(f"  [{i:02d}/{len(batch)}] {lead.get('name', '?')[:40]} | {lead.get('phone')}")
        result = fire_call(lead)
        results.append(result)
        
        if result["status"] == "fired":
            fired_count += 1
        else:
            error_count += 1
            print(f"         ⚠️  Error: {result.get('error','?')[:80]}")
        
        if i < len(batch):
            time.sleep(DELAY_BETWEEN_CALLS)
    
    print(f"\n[{datetime.utcnow().strftime('%H:%M:%S')}] Fired: {fired_count} | Errors: {error_count}")
    
    # Save initial state
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    summary = {
        "campaign": "Philippines Tourism - March 6 2026",
        "agent": "Lila",
        "assistant_id": ASSISTANT_ID,
        "phone_number_id": PHONE_NUMBER_ID,
        "offer": "Website $599 + SEO $200/mo",
        "batch_size": BATCH_SIZE,
        "fired_at": datetime.utcnow().isoformat() + "Z",
        "fired_count": fired_count,
        "error_count": error_count,
        "calls": results
    }
    with open(RESULTS_FILE, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Initial results saved → {RESULTS_FILE}")
    
    # ── Phase 2: Poll for completion ─────────────────────────────────────────
    active_ids = [r["call_id"] for r in results if r.get("call_id")]
    
    if not active_ids:
        print("No active call IDs to poll. Done.")
        return summary
    
    print(f"\n[{datetime.utcnow().strftime('%H:%M:%S')}] Polling {len(active_ids)} calls for completion...")
    
    completed_ids = set()
    
    for poll_round in range(1, MAX_POLL_ROUNDS + 1):
        time.sleep(POLL_INTERVAL)
        
        still_pending = [cid for cid in active_ids if cid not in completed_ids]
        if not still_pending:
            print(f"  All calls completed!")
            break
        
        print(f"  Round {poll_round}/{MAX_POLL_ROUNDS} — checking {len(still_pending)} pending calls...")
        
        newly_done = 0
        for cid in still_pending:
            data = poll_call_status(cid)
            api_status = data.get("status", "")
            
            # Find and update matching result
            for r in results:
                if r.get("call_id") == cid:
                    r["api_status"] = api_status
                    r["last_polled"] = datetime.utcnow().isoformat() + "Z"
                    
                    if api_status in ("ended", "failed", "no-answer", "busy", "cancelled", "error"):
                        r["status"] = "completed" if api_status == "ended" else api_status
                        r["ended_reason"] = data.get("endedReason", "")
                        r["duration_seconds"] = data.get("duration", 0)
                        
                        # Extract summary/transcript if available
                        analysis = data.get("analysis", {})
                        if analysis:
                            r["summary"] = analysis.get("summary", "")
                            r["structured_data"] = analysis.get("structuredData", {})
                        
                        artifact = data.get("artifact", {})
                        if artifact:
                            r["transcript"] = artifact.get("transcript", "")
                        
                        completed_ids.add(cid)
                        newly_done += 1
        
        # Update summary stats
        status_counts = {}
        for r in results:
            s = r.get("api_status") or r.get("status", "unknown")
            status_counts[s] = status_counts.get(s, 0) + 1
        
        print(f"    Done this round: {newly_done} | Status breakdown: {status_counts}")
        
        # Save updated results
        summary["calls"] = results
        summary["last_updated"] = datetime.utcnow().isoformat() + "Z"
        summary["status_breakdown"] = status_counts
        with open(RESULTS_FILE, 'w') as f:
            json.dump(summary, f, indent=2)
    
    # ── Final tally ──────────────────────────────────────────────────────────
    final_status = {}
    for r in results:
        s = r.get("api_status") or r.get("status", "unknown")
        final_status[s] = final_status.get(s, 0) + 1
    
    summary["final_status_breakdown"] = final_status
    summary["completed_at"] = datetime.utcnow().isoformat() + "Z"
    summary["calls"] = results
    
    with open(RESULTS_FILE, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n[{datetime.utcnow().strftime('%H:%M:%S')}] ✅ Campaign done!")
    print(f"  Final breakdown: {final_status}")
    print(f"  Results → {RESULTS_FILE}")
    
    return summary

if __name__ == "__main__":
    main()
