#!/usr/bin/env python3
"""
Jake - Australia Dental Batch Caller
SmartBook AI A$780/mo pitch via Vapi
March 6, 2026
"""
import os, sys, json, time, requests
from datetime import datetime

VAPI_API_KEY   = "0aaae7fe-be63-472a-a46d-5d9224e0fa89"
ASSISTANT_ID   = "97a15a94-e4d4-4b80-8db5-0d6e62ff3121"   # Jake
PHONE_ID       = "23eacc2d-e19d-4410-98dd-aef4ab564b63"
HEADERS        = {"Authorization": f"Bearer {VAPI_API_KEY}", "Content-Type": "application/json"}

RESULTS_FILE   = "/root/.openclaw/workspace/assets/jake-call-results-march6.json"

# --- Leads with real phone numbers (15/30) ---
LEADS = [
    {"id": 1,  "name": "Spa Dental Sydney CBD",           "city": "Sydney",    "phone_raw": "(02) 9221 8348", "priority": "high",   "reviews": 507,  "e164": "+61292218348"},
    {"id": 2,  "name": "Dental Boutique Sydney",          "city": "Sydney",    "phone_raw": "1300 327 645",   "priority": "high",   "reviews": 917,  "e164": "+611300327645"},
    {"id": 3,  "name": "Pitt Street Dental Centre",       "city": "Sydney",    "phone_raw": "(02) 8000 1832", "priority": "high",   "reviews": 522,  "e164": "+61280001832"},
    {"id": 4,  "name": "Paramount Dental Sydney",         "city": "Sydney",    "phone_raw": "(02) 9131 8078", "priority": "high",   "reviews": 674,  "e164": "+61291318078"},
    {"id": 5,  "name": "The Paddington Dental Surgery",   "city": "Sydney",    "phone_raw": "(02) 9331 2555", "priority": "high",   "reviews": 501,  "e164": "+61293312555"},
    {"id": 16, "name": "Gorgeous Smiles Melbourne",       "city": "Melbourne", "phone_raw": "(03) 9042 0483", "priority": "high",   "reviews": 1494, "e164": "+61390420483"},
    {"id": 17, "name": "Smile Solutions Melbourne",       "city": "Melbourne", "phone_raw": "(03) 9650 4920", "priority": "high",   "reviews": 942,  "e164": "+61396504920"},
    {"id": 18, "name": "Australian Dentists Clinic",      "city": "Melbourne", "phone_raw": "(03) 9088 0257", "priority": "high",   "reviews": 1802, "e164": "+61390880257"},
    {"id": 19, "name": "Melbourne Dentist Clinic",        "city": "Melbourne", "phone_raw": "(03) 9999 9703", "priority": "high",   "reviews": 488,  "e164": "+61399999703"},
    {"id": 20, "name": "MC Dental Melbourne Central",     "city": "Melbourne", "phone_raw": "(03) 8608 8971", "priority": "high",   "reviews": 2129, "e164": "+61386088971"},
    {"id": 23, "name": "Brisbane Smiles",                 "city": "Brisbane",  "phone_raw": "(07) 3870 3333", "priority": "high",   "reviews": 1152, "e164": "+61738703333"},
    {"id": 24, "name": "Brisbane Dental",                 "city": "Brisbane",  "phone_raw": "(07) 3236 2984", "priority": "high",   "reviews": 968,  "e164": "+61732362984"},
    {"id": 25, "name": "Precision Dental",                "city": "Brisbane",  "phone_raw": "(07) 3852 1160", "priority": "high",   "reviews": 481,  "e164": "+61738521160"},
    {"id": 26, "name": "Dental Boutique Brisbane",        "city": "Brisbane",  "phone_raw": "1300 327 645",   "priority": "high",   "reviews": 465,  "e164": "+611300327645"},
    {"id": 27, "name": "Smileologie",                     "city": "Brisbane",  "phone_raw": "(07) 3392 1942", "priority": "high",   "reviews": 456,  "e164": "+61733921942"},
]

SKIPPED_LEADS = [
    {"id": 6,  "name": "Lumina Dental Clinic Sydney",          "city": "Sydney",    "reason": "lookup-required"},
    {"id": 7,  "name": "Dental 99",                            "city": "Sydney",    "reason": "lookup-required"},
    {"id": 8,  "name": "Smile Concepts",                       "city": "Sydney",    "reason": "lookup-required"},
    {"id": 9,  "name": "North Sydney Dentistry – Cosmetique",  "city": "Sydney",    "reason": "lookup-required"},
    {"id": 10, "name": "Macquarie Dental",                     "city": "Sydney",    "reason": "lookup-required"},
    {"id": 11, "name": "TLC Dental",                           "city": "Sydney",    "reason": "lookup-required"},
    {"id": 12, "name": "City Dental – Experteeth Dental",      "city": "Sydney",    "reason": "lookup-required"},
    {"id": 13, "name": "Hyde Park Dental Care",                "city": "Sydney",    "reason": "lookup-required"},
    {"id": 14, "name": "Sydney Dental Aesthetics & Implants",  "city": "Sydney",    "reason": "lookup-required"},
    {"id": 15, "name": "Lumiere Dental and Implants Centre",   "city": "Sydney",    "reason": "lookup-required"},
    {"id": 21, "name": "Happy Dentistry",                      "city": "Melbourne", "reason": "lookup-required"},
    {"id": 22, "name": "Dental On Flinders",                   "city": "Melbourne", "reason": "lookup-required"},
    {"id": 28, "name": "North Brisbane Dental Clinic",         "city": "Brisbane",  "reason": "lookup-required"},
    {"id": 29, "name": "Newnham Dental & Cosmetics",           "city": "Brisbane",  "reason": "lookup-required"},
    {"id": 30, "name": "Dentistry on George",                  "city": "Brisbane",  "reason": "lookup-required"},
]

def initiate_call(lead):
    payload = {
        "assistantId": ASSISTANT_ID,
        "phoneNumberId": PHONE_ID,
        "customer": {"number": lead["e164"], "name": lead["name"]},
        "assistantOverrides": {
            "variableValues": {
                "practice_name": lead["name"],
                "city": lead["city"],
                "offer": "SmartBook AI A$780/mo",
                "review_count": str(lead["reviews"])
            }
        }
    }
    resp = requests.post("https://api.vapi.ai/call", headers=HEADERS, json=payload, timeout=30)
    if resp.ok:
        data = resp.json()
        return {"call_id": data.get("id"), "status": data.get("status", "queued"), "error": None}
    else:
        return {"call_id": None, "status": "api_error", "error": f"{resp.status_code}: {resp.text[:200]}"}

def poll_call(call_id, max_wait=300, poll_interval=10):
    """Poll call status until ended/failed or timeout."""
    deadline = time.time() + max_wait
    while time.time() < deadline:
        try:
            resp = requests.get(f"https://api.vapi.ai/call/{call_id}", headers=HEADERS, timeout=15)
            if resp.ok:
                data = resp.json()
                status = data.get("status", "")
                if status in ("ended", "failed"):
                    ended_reason = data.get("endedReason", "")
                    cost = data.get("cost", 0)
                    transcript = data.get("transcript", "")
                    summary = data.get("summary", "")
                    started_at = data.get("startedAt", "")
                    ended_at   = data.get("endedAt", "")
                    duration = 0
                    if started_at and ended_at:
                        try:
                            from datetime import timezone
                            s = datetime.fromisoformat(started_at.replace('Z','+00:00'))
                            e = datetime.fromisoformat(ended_at.replace('Z','+00:00'))
                            duration = round((e - s).total_seconds(), 1)
                        except: pass
                    return {
                        "final_status": status,
                        "ended_reason": ended_reason,
                        "duration_sec": duration,
                        "cost_usd": cost,
                        "transcript": transcript[:500] if transcript else "",
                        "summary": summary
                    }
            time.sleep(poll_interval)
        except Exception as ex:
            time.sleep(poll_interval)
    return {"final_status": "poll_timeout", "ended_reason": "exceeded wait time", "duration_sec": 0, "cost_usd": 0, "transcript": "", "summary": ""}

def main():
    run_ts = datetime.utcnow().isoformat() + "Z"
    print(f"[{run_ts}] Jake Dental Calls — {len(LEADS)} dialable leads")
    
    results = []
    call_log = []

    for i, lead in enumerate(LEADS, 1):
        print(f"\n[{i}/{len(LEADS)}] Calling {lead['name']} ({lead['city']}) → {lead['e164']}")
        initiated = initiate_call(lead)
        
        entry = {
            "lead_id":   lead["id"],
            "name":      lead["name"],
            "city":      lead["city"],
            "phone_raw": lead["phone_raw"],
            "phone_e164": lead["e164"],
            "priority":  lead["priority"],
            "reviews":   lead["reviews"],
            "call_id":   initiated["call_id"],
            "initiate_status": initiated["status"],
            "initiate_error":  initiated["error"],
            "call_details":    None,
            "called_at": datetime.utcnow().isoformat() + "Z"
        }

        if initiated["call_id"] and initiated["status"] != "api_error":
            print(f"  ✓ Call initiated — ID: {initiated['call_id']} — polling...")
            details = poll_call(initiated["call_id"])
            entry["call_details"] = details
            outcome = details["final_status"]
            print(f"  → {outcome} | reason: {details.get('ended_reason','')} | {details.get('duration_sec',0)}s | ${details.get('cost_usd',0):.4f}")
        else:
            print(f"  ✗ Error: {initiated['error']}")
        
        results.append(entry)
        call_log.append(entry)

        # Brief pause between calls to avoid rate limits
        if i < len(LEADS):
            time.sleep(3)

    # Build final report
    successful   = [r for r in results if r.get("call_details") and r["call_details"].get("final_status") == "ended"]
    failed_api   = [r for r in results if r.get("initiate_status") == "api_error"]
    timed_out    = [r for r in results if r.get("call_details") and r["call_details"].get("final_status") == "poll_timeout"]
    call_failed  = [r for r in results if r.get("call_details") and r["call_details"].get("final_status") == "failed"]
    total_cost   = sum(r["call_details"].get("cost_usd", 0) for r in results if r.get("call_details"))

    report = {
        "run_metadata": {
            "agent":         "Jake",
            "assistant_id":  ASSISTANT_ID,
            "phone_id":      PHONE_ID,
            "offer":         "SmartBook AI A$780/mo",
            "run_timestamp": run_ts,
            "completed_at":  datetime.utcnow().isoformat() + "Z"
        },
        "summary": {
            "total_leads":      30,
            "leads_with_phone": len(LEADS),
            "leads_skipped_no_phone": len(SKIPPED_LEADS),
            "calls_attempted":  len(results),
            "calls_completed":  len(successful),
            "calls_failed_api": len(failed_api),
            "calls_failed_vapi": len(call_failed),
            "calls_timed_out":  len(timed_out),
            "total_cost_usd":   round(total_cost, 4)
        },
        "call_results": results,
        "skipped_no_phone": SKIPPED_LEADS
    }

    with open(RESULTS_FILE, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n{'='*60}")
    print(f"DONE — Results saved to {RESULTS_FILE}")
    print(f"Calls completed: {len(successful)}/{len(LEADS)}")
    print(f"Total cost: ${total_cost:.4f} USD")
    print(f"{'='*60}")

    return report

if __name__ == "__main__":
    main()
