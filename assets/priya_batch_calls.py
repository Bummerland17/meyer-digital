#!/usr/bin/env python3
"""
Priya – UK Aesthetics Outbound Batch Caller
Fires calls via Vapi API, polls for results, logs to JSON.
"""
import os, sys, json, time, requests
from datetime import datetime

# ── Config ──────────────────────────────────────────────────────────────────
VAPI_API_KEY     = "0aaae7fe-be63-472a-a46d-5d9224e0fa89"
ASSISTANT_ID     = "0aa82051-fb76-43f0-95cf-310e6bca4914"   # Priya
PHONE_NUMBER_ID  = "23eacc2d-e19d-4410-98dd-aef4ab564b63"

LEADS_FILE  = "/root/.openclaw/workspace/real-estate/uk-aesthetics-leads-2026-03-05.json"
RESULTS_FILE = "/root/.openclaw/workspace/assets/priya-call-results-march6.json"

HEADERS = {"Authorization": f"Bearer {VAPI_API_KEY}", "Content-Type": "application/json"}

POLL_INTERVAL    = 10   # seconds between status polls
MAX_POLL_WAIT    = 420  # 7 min max per call before marking timeout
DELAY_BETWEEN_CALLS = 5 # seconds between firing each call

# ── UK → E.164 helper ───────────────────────────────────────────────────────
def to_e164(raw: str) -> str | None:
    n = raw.strip().replace(" ", "").replace("-", "")
    if not n or n == "lookup-required":
        return None
    if n.startswith("0"):
        return "+44" + n[1:]
    if n.startswith("+"):
        return n
    return None

# ── Fire a single call (no webhook dependency) ──────────────────────────────
def fire_call(lead: dict, e164: str) -> dict:
    payload = {
        "assistantId": ASSISTANT_ID,
        "phoneNumberId": PHONE_NUMBER_ID,
        "customer": {"number": e164, "name": lead.get("name", "")},
    }
    try:
        r = requests.post("https://api.vapi.ai/call", headers=HEADERS, json=payload, timeout=30)
        if r.ok:
            data = r.json()
            return {"fired": True, "call_id": data.get("id"), "raw": data}
        else:
            return {"fired": False, "error": f"HTTP {r.status_code}: {r.text[:300]}"}
    except Exception as ex:
        return {"fired": False, "error": str(ex)}

# ── Poll a call until terminal state ────────────────────────────────────────
def poll_call(call_id: str) -> dict:
    deadline = time.time() + MAX_POLL_WAIT
    while time.time() < deadline:
        try:
            r = requests.get(f"https://api.vapi.ai/call/{call_id}", headers=HEADERS, timeout=15)
            if not r.ok:
                time.sleep(POLL_INTERVAL)
                continue
            data = r.json()
            status = data.get("status", "")
            if status in ("ended", "failed", "cancelled"):
                return {
                    "status": status,
                    "ended_reason": data.get("endedReason", ""),
                    "duration": _calc_duration(data),
                    "cost": data.get("cost", 0),
                    "transcript": (data.get("transcript") or "")[:2000],
                    "summary": data.get("analysis", {}).get("summary", "") or data.get("summary", ""),
                    "raw_status": data,
                }
        except Exception:
            pass
        time.sleep(POLL_INTERVAL)
    return {"status": "timeout", "error": f"Did not reach terminal state within {MAX_POLL_WAIT}s"}

def _calc_duration(data):
    try:
        from datetime import datetime as dt
        s = data.get("startedAt") or data.get("createdAt")
        e = data.get("endedAt")
        if s and e:
            fmt = lambda x: dt.fromisoformat(x.replace("Z", "+00:00"))
            return round((fmt(e) - fmt(s)).total_seconds(), 1)
    except:
        pass
    return 0

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    with open(LEADS_FILE) as f:
        raw = json.load(f)
    leads = raw["leads"]

    # Filter to callable leads
    callable_leads = []
    skipped_leads  = []
    for lead in leads:
        e164 = to_e164(lead.get("phone", ""))
        if e164:
            callable_leads.append((lead, e164))
        else:
            skipped_leads.append({
                "id": lead["id"],
                "name": lead["name"],
                "city": lead["city"],
                "phone_raw": lead.get("phone", ""),
                "skip_reason": "no phone number / lookup-required"
            })

    print(f"[Priya Batch] {len(callable_leads)} callable | {len(skipped_leads)} skipped (no number)")
    print(f"[Priya Batch] Output → {RESULTS_FILE}\n")

    results = []
    fired_calls = []

    # Phase 1: Fire all calls
    for lead, e164 in callable_leads:
        print(f"  📞 Firing #{lead['id']} {lead['name']} ({lead['city']}) → {e164}")
        fire_resp = fire_call(lead, e164)
        entry = {
            "id": lead["id"],
            "name": lead["name"],
            "city": lead["city"],
            "phone_raw": lead.get("phone", ""),
            "phone_e164": e164,
            "priority": lead.get("priority", ""),
            "rating": lead.get("rating"),
            "review_count": lead.get("review_count"),
            "fired_at": datetime.utcnow().isoformat() + "Z",
        }
        if fire_resp["fired"]:
            entry["call_id"]     = fire_resp["call_id"]
            entry["fire_status"] = "queued"
            fired_calls.append((entry, fire_resp["call_id"]))
            print(f"     ✅ Queued  call_id={fire_resp['call_id']}")
        else:
            entry["call_id"]     = None
            entry["fire_status"] = "fire_error"
            entry["error"]       = fire_resp["error"]
            entry["outcome"]     = "fire_error"
            results.append(entry)
            print(f"     ❌ Fire error: {fire_resp['error']}")
        time.sleep(DELAY_BETWEEN_CALLS)

    # Phase 2: Poll for results
    print(f"\n[Priya Batch] Polling {len(fired_calls)} calls for results …\n")
    for entry, call_id in fired_calls:
        print(f"  ⏳ Polling {entry['name']} ({call_id[:8]}…)")
        poll = poll_call(call_id)
        entry.update({
            "outcome": poll.get("status"),
            "ended_reason": poll.get("ended_reason", ""),
            "duration_sec": poll.get("duration", 0),
            "cost_usd": poll.get("cost", 0),
            "summary": poll.get("summary", ""),
            "transcript_snippet": (poll.get("transcript") or "")[:500],
            "poll_error": poll.get("error", ""),
        })
        results.append(entry)
        icon = "✅" if poll.get("status") == "ended" else ("⏱️" if poll.get("status") == "timeout" else "❌")
        print(f"     {icon} {poll.get('status')} | reason={poll.get('ended_reason','')} | {poll.get('duration',0)}s")

    # Build final report
    completed   = [r for r in results if r.get("outcome") == "ended"]
    failed      = [r for r in results if r.get("outcome") in ("failed", "cancelled", "fire_error")]
    timed_out   = [r for r in results if r.get("outcome") == "timeout"]

    report = {
        "meta": {
            "run_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "run_time_utc": datetime.utcnow().isoformat() + "Z",
            "agent": "Priya",
            "assistant_id": ASSISTANT_ID,
            "phone_number_id": PHONE_NUMBER_ID,
            "product_pitched": "SmartBook AI £390/mo",
            "total_leads": len(leads),
            "callable_leads": len(callable_leads),
            "skipped_no_phone": len(skipped_leads),
            "calls_completed": len(completed),
            "calls_failed": len(failed),
            "calls_timed_out": len(timed_out),
        },
        "call_results": results,
        "skipped_leads": skipped_leads,
    }

    with open(RESULTS_FILE, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n{'='*60}")
    print(f"[Priya Batch] DONE")
    print(f"  Callable    : {len(callable_leads)}")
    print(f"  Completed   : {len(completed)}")
    print(f"  Failed/Error: {len(failed)}")
    print(f"  Timed out   : {len(timed_out)}")
    print(f"  Skipped     : {len(skipped_leads)}")
    print(f"  Results → {RESULTS_FILE}")

if __name__ == "__main__":
    main()
