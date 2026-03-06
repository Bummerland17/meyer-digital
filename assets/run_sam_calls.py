#!/usr/bin/env python3
"""
Sam UK Landlord Batch Caller — UnitFix £15/mo
Dispatches Vapi outbound calls to all leads with phone numbers.
Uses fire-and-record (no webhook wait) for batch reliability.
"""
import json
import os
import requests
from datetime import datetime, timezone

# --- Config (from cron task, override .env) ---
VAPI_API_KEY      = "0aaae7fe-be63-472a-a46d-5d9224e0fa89"
ASSISTANT_ID      = "ae3642d3-19f5-4d60-bd4d-cbeebe8a023e"   # Sam
PHONE_NUMBER_ID   = "23eacc2d-e19d-4410-98dd-aef4ab564b63"
RESULTS_FILE      = "/root/.openclaw/workspace/assets/sam-call-results-march6.json"

SYSTEM_PROMPT = (
    "You are Sam, a friendly and professional sales agent for UnitFix — a maintenance request "
    "tracker built specifically for UK landlords with 1 to 5 properties. Your mission is to "
    "introduce UnitFix to the letting agency and explain its value. Key pitch: UnitFix is only "
    "£15 per month, helps landlords and agents track all maintenance requests in one place, "
    "reduces missed repairs, improves tenant satisfaction, and saves hours of back-and-forth. "
    "Be conversational, acknowledge any objections warmly, and aim to book a short 10-minute "
    "demo or direct them to unitfix.app. Always be polite and if they are busy or not interested, "
    "thank them and end the call professionally. Once the conversation is complete or the "
    "prospect is not interested, end the call using the endCall tool."
)

FIRST_MESSAGE = (
    "Hi there! My name is Sam calling on behalf of UnitFix. "
    "Is this a good time for a very quick 60-second call about a tool that could "
    "save you time managing maintenance for your landlords?"
)

END_MESSAGE = "Thanks so much for your time — have a lovely day!"

# --- Leads with phone numbers only (E.164 converted) ---
LEADS = [
    {"id": 1,  "company": "Premier Residential Lettings & Estate Agents",  "city": "Manchester", "phone": "+441616414624"},
    {"id": 2,  "company": "The Letting Agent",                              "city": "Manchester", "phone": "+441618340801"},
    {"id": 3,  "company": "Manlets – Property Management Manchester",       "city": "Manchester", "phone": "+441612388978"},
    {"id": 4,  "company": "Abode Property Management (NW) Ltd",            "city": "Manchester", "phone": "+441618831886"},
    {"id": 5,  "company": "Bentley Hurst Estate Agents",                   "city": "Manchester", "phone": "+441615430310"},
    {"id": 9,  "company": "Accord Lets Letting Agents Birmingham",          "city": "Birmingham", "phone": "+441213690840"},
    {"id": 10, "company": "Premier Estate Agents (Birmingham) Ltd",         "city": "Birmingham", "phone": "+441213777868"},
    {"id": 17, "company": "Northwood Leeds",                                "city": "Leeds",      "phone": "+441132392791"},
    {"id": 18, "company": "Fletcher Properties",                            "city": "Leeds",      "phone": "+441132109531"},
    {"id": 25, "company": "The Bristol Residential Letting Co – Bishopston","city": "Bristol",    "phone": "+441172442040"},
    {"id": 26, "company": "Balloon Letting Company",                        "city": "Bristol",    "phone": "+441172870015"},
    {"id": 33, "company": "Milards",                                        "city": "Edinburgh",  "phone": "+441312352391"},
    {"id": 34, "company": "Clan Gordon Letting Agents",                     "city": "Edinburgh",  "phone": "+441315554444"},
    {"id": 35, "company": "Umega Lettings",                                 "city": "Edinburgh",  "phone": "+441312210888"},
    {"id": 36, "company": "Clouds Property Management",                     "city": "Edinburgh",  "phone": "+441315503808"},
    {"id": 41, "company": "The Letting Station Cardiff",                    "city": "Cardiff",    "phone": "+442920020880"},
    {"id": 42, "company": "Hogg & Hogg Estate Agents",                     "city": "Cardiff",    "phone": "+442920102525"},
]

def dispatch_call(lead):
    payload = {
        "assistantId": ASSISTANT_ID,
        "phoneNumberId": PHONE_NUMBER_ID,
        "customer": {"number": lead["phone"]},
        "assistantOverrides": {
            "firstMessage": FIRST_MESSAGE,
            "model": {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "messages": [{"role": "system", "content": SYSTEM_PROMPT}],
                "tools": [
                    {
                        "type": "endCall",
                        "messages": [
                            {"type": "request-start", "content": END_MESSAGE}
                        ]
                    }
                ]
            },
            "endCallMessage": END_MESSAGE
        }
    }

    try:
        resp = requests.post(
            "https://api.vapi.ai/call",
            headers={"Authorization": f"Bearer {VAPI_API_KEY}"},
            json=payload,
            timeout=30
        )
        if resp.ok:
            data = resp.json()
            return {
                "lead_id": lead["id"],
                "company": lead["company"],
                "city": lead["city"],
                "phone": lead["phone"],
                "status": "dispatched",
                "call_id": data.get("id"),
                "dispatched_at": datetime.now(timezone.utc).isoformat(),
                "api_status": resp.status_code
            }
        else:
            return {
                "lead_id": lead["id"],
                "company": lead["company"],
                "city": lead["city"],
                "phone": lead["phone"],
                "status": "api_error",
                "call_id": None,
                "dispatched_at": datetime.now(timezone.utc).isoformat(),
                "api_status": resp.status_code,
                "error": resp.text[:500]
            }
    except Exception as e:
        return {
            "lead_id": lead["id"],
            "company": lead["company"],
            "city": lead["city"],
            "phone": lead["phone"],
            "status": "exception",
            "call_id": None,
            "dispatched_at": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }

def main():
    print(f"[Sam] Starting batch — {len(LEADS)} leads with phone numbers")
    results = []

    for i, lead in enumerate(LEADS, 1):
        print(f"[{i}/{len(LEADS)}] Calling {lead['company']} ({lead['city']}) → {lead['phone']}")
        result = dispatch_call(lead)
        results.append(result)
        status_icon = "✅" if result["status"] == "dispatched" else "❌"
        print(f"       {status_icon} {result['status']} | call_id: {result.get('call_id', 'N/A')}")

    # Summary stats
    dispatched = sum(1 for r in results if r["status"] == "dispatched")
    errors     = len(results) - dispatched
    skipped    = 50 - len(LEADS)   # leads without phone numbers

    output = {
        "run_date": "2026-03-06",
        "run_time_utc": datetime.now(timezone.utc).isoformat(),
        "agent": "Sam",
        "assistant_id": ASSISTANT_ID,
        "phone_number_id": PHONE_NUMBER_ID,
        "product": "UnitFix",
        "offer": "£15/month",
        "total_leads_in_file": 50,
        "leads_with_phones": len(LEADS),
        "leads_skipped_no_phone": skipped,
        "dispatched": dispatched,
        "errors": errors,
        "calls": results
    }

    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n[Sam] Done. {dispatched} dispatched, {errors} errors, {skipped} skipped (no phone).")
    print(f"[Sam] Results saved → {RESULTS_FILE}")

if __name__ == "__main__":
    main()
