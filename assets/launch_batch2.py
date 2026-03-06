#!/usr/bin/env python3
"""
Batch 2 cold call launcher.
Waits until 23:00 UTC (4pm Phoenix), then:
  - Batch 1 @ 23:00 UTC: 10 dental offices (Alex agent)
  - Batch 2 @ 23:20 UTC: 10 gym/spa (Maya agent)
Then checks results 30 min after batch 1.
"""

import json
import time
import datetime
import requests
import sys

QUEUE_FILE = "/root/.openclaw/workspace/assets/call-queue.json"
RESULTS_FILE = "/root/.openclaw/workspace/assets/call-results-batch2.json"
LOG_FILE = "/root/.openclaw/workspace/assets/batch2.log"

VAPI_KEY = "0aaae7fe-be63-472a-a46d-5d9224e0fa89"
PHONE_NUMBER_ID = "3f6ef946-452f-4b16-85cf-9e2d5b041df5"
ALEX_AGENT_ID = "95e7c636-f8e6-4801-8866-fca9d5d475d3"
MAYA_AGENT_ID = "a413b4d6-175d-49b3-8114-cf05879ea5d5"

HEADERS = {
    "Authorization": f"Bearer {VAPI_KEY}",
    "Content-Type": "application/json"
}

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_queue():
    with open(QUEUE_FILE) as f:
        return json.load(f)

def save_queue(data):
    with open(QUEUE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def wait_until_utc(hour, minute=0):
    now = datetime.datetime.utcnow()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += datetime.timedelta(days=1)
    wait_secs = (target - now).total_seconds()
    log(f"Waiting {wait_secs:.0f}s until {target.strftime('%Y-%m-%d %H:%M UTC')}...")
    
    # Sleep in chunks so we can log progress
    while True:
        now = datetime.datetime.utcnow()
        remaining = (target - now).total_seconds()
        if remaining <= 0:
            break
        chunk = min(300, remaining)  # log every 5 min
        if remaining > 60:
            log(f"  ... {remaining/60:.1f} min remaining until launch")
        time.sleep(chunk)
    
    log(f"Target time reached: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")

def make_call(business, agent_id):
    payload = {
        "assistantId": agent_id,
        "phoneNumberId": PHONE_NUMBER_ID,
        "customer": {
            "number": business["phone"],
            "name": business["business_name"]
        }
    }
    try:
        r = requests.post("https://api.vapi.ai/call/phone", headers=HEADERS, json=payload, timeout=30)
        r.raise_for_status()
        resp = r.json()
        call_id = resp.get("id")
        log(f"  ✅ Called {business['business_name']} ({business['phone']}) → call_id={call_id}")
        return call_id, None
    except Exception as e:
        log(f"  ❌ Failed {business['business_name']} ({business['phone']}): {e}")
        return None, str(e)

def check_call_result(call_id):
    try:
        r = requests.get(f"https://api.vapi.ai/call/{call_id}", headers=HEADERS, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log(f"  ⚠️  Could not fetch result for {call_id}: {e}")
        return None

def launch_batch(businesses, agent_id, batch_name):
    log(f"\n=== Launching {batch_name} ({len(businesses)} calls, agent={'Alex' if agent_id==ALEX_AGENT_ID else 'Maya'}) ===")
    queue_data = load_queue()
    launched = []
    
    for i, biz in enumerate(businesses):
        if i > 0:
            log(f"  Waiting 30s before next call...")
            time.sleep(30)
        
        call_id, error = make_call(biz, agent_id)
        
        # Update queue file
        for entry in queue_data:
            if entry["phone"] == biz["phone"] and entry["business_name"] == biz["business_name"]:
                if call_id:
                    entry["status"] = "called"
                    entry["vapi_call_id"] = call_id
                else:
                    entry["status"] = "error"
                    entry["error"] = error
                break
        
        save_queue(queue_data)
        
        if call_id:
            launched.append({
                "business_name": biz["business_name"],
                "phone": biz["phone"],
                "type": biz.get("type"),
                "vapi_call_id": call_id,
                "agent": "Alex" if agent_id == ALEX_AGENT_ID else "Maya",
                "launched_at": datetime.datetime.utcnow().isoformat() + "Z"
            })
    
    log(f"  Batch complete: {len(launched)}/{len(businesses)} calls launched")
    return launched

def check_results(batch1_calls, check_label):
    log(f"\n=== Checking results for {check_label} ===")
    results = []
    
    for call_info in batch1_calls:
        call_id = call_info["vapi_call_id"]
        log(f"  Fetching {call_info['business_name']} ({call_id})...")
        data = check_call_result(call_id)
        
        if not data:
            results.append({**call_info, "result": "fetch_error"})
            continue
        
        duration = data.get("duration") or data.get("durationSeconds") or 0
        ended_reason = data.get("endedReason") or data.get("status") or "unknown"
        transcript = ""
        
        # Try to extract transcript snippet
        if data.get("transcript"):
            transcript = data["transcript"][:300]
        elif data.get("messages"):
            msgs = data["messages"]
            snippet_parts = []
            for m in msgs[-6:]:
                role = m.get("role", "?")
                content = m.get("content") or m.get("message") or ""
                snippet_parts.append(f"{role}: {content[:100]}")
            transcript = " | ".join(snippet_parts)
        
        # Flag warm/bad calls
        flag = None
        if duration > 90:
            flag = "WARM_LEAD"
        elif duration < 15 and duration > 0:
            flag = "QUICK_HANGUP"
        elif duration == 0:
            flag = "NO_DURATION"
        
        result_entry = {
            **call_info,
            "duration_seconds": duration,
            "ended_reason": ended_reason,
            "transcript_snippet": transcript,
            "flag": flag,
            "raw_status": data.get("status")
        }
        results.append(result_entry)
        
        flag_str = f" ⚠️ [{flag}]" if flag else ""
        log(f"    {call_info['business_name']}: {duration}s | {ended_reason}{flag_str}")
    
    return results

def main():
    log("=" * 60)
    log("Batch 2 Cold Call Launcher starting")
    log(f"Current UTC: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 60)
    
    # Load queue and pick next 10 dental + 10 gym/spa
    queue_data = load_queue()
    queued = [b for b in queue_data if b["status"] == "queued"]
    
    dental_types = {"dental_office", "dental"}
    gym_spa_types = {"gym", "spa", "gym_spa"}
    
    dental_queued = [b for b in queued if b.get("type") in dental_types]
    gym_spa_queued = [b for b in queued if b.get("type") in gym_spa_types]
    
    batch1_biz = dental_queued[:10]
    batch2_biz = gym_spa_queued[:10]
    
    log(f"Batch 1 (dental, Alex): {len(batch1_biz)} businesses")
    for b in batch1_biz:
        log(f"  - {b['business_name']} ({b['phone']})")
    log(f"Batch 2 (gym/spa, Maya): {len(batch2_biz)} businesses")
    for b in batch2_biz:
        log(f"  - {b['business_name']} ({b['phone']})")
    
    # Wait until 23:00 UTC (4pm Phoenix)
    wait_until_utc(23, 0)
    
    # Launch Batch 1
    batch1_launched = launch_batch(batch1_biz, ALEX_AGENT_ID, "Batch 1 - Dental Offices")
    
    # Wait 20 min for batch 2
    log("\nWaiting 20 minutes before Batch 2...")
    wait_until_utc(23, 20)
    
    # Launch Batch 2
    batch2_launched = launch_batch(batch2_biz, MAYA_AGENT_ID, "Batch 2 - Gyms/Spas")
    
    # Wait 30 min after batch 1 to check results
    # Batch 1 started at 23:00, 30 min = 23:30
    log("\nWaiting until 23:30 UTC to check Batch 1 results (30 min after launch)...")
    wait_until_utc(23, 30)
    
    batch1_results = check_results(batch1_launched, "Batch 1 - Dental Offices")
    
    # Save results
    all_results = {
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "batch1": {
            "label": "Dental Offices - Alex Agent",
            "count_launched": len(batch1_launched),
            "calls": batch1_results,
            "warm_leads": [r for r in batch1_results if r.get("flag") == "WARM_LEAD"],
            "quick_hangups": [r for r in batch1_results if r.get("flag") == "QUICK_HANGUP"]
        },
        "batch2": {
            "label": "Gyms/Spas - Maya Agent",
            "count_launched": len(batch2_launched),
            "calls": batch2_launched  # No results check yet for batch 2
        },
        "summary": {
            "total_launched": len(batch1_launched) + len(batch2_launched),
            "batch1_warm_leads": len([r for r in batch1_results if r.get("flag") == "WARM_LEAD"]),
            "batch1_quick_hangups": len([r for r in batch1_results if r.get("flag") == "QUICK_HANGUP"])
        }
    }
    
    with open(RESULTS_FILE, "w") as f:
        json.dump(all_results, f, indent=2)
    
    log(f"\n✅ Results saved to {RESULTS_FILE}")
    
    # Print summary
    log("\n" + "=" * 60)
    log("FINAL SUMMARY")
    log("=" * 60)
    log(f"Total calls launched: {all_results['summary']['total_launched']}")
    log(f"  Batch 1 (Dental/Alex): {len(batch1_launched)} calls")
    log(f"  Batch 2 (Gym-Spa/Maya): {len(batch2_launched)} calls")
    log(f"Batch 1 Results:")
    log(f"  🔥 Warm leads (>90s): {all_results['summary']['batch1_warm_leads']}")
    log(f"  ❌ Quick hangups (<15s): {all_results['summary']['batch1_quick_hangups']}")
    
    warm = all_results["batch1"]["warm_leads"]
    if warm:
        log("\nWARM LEADS:")
        for w in warm:
            log(f"  🔥 {w['business_name']} | {w['duration_seconds']}s | {w['ended_reason']}")
            if w.get("transcript_snippet"):
                log(f"     Transcript: {w['transcript_snippet'][:200]}")
    
    log("\nDone.")

if __name__ == "__main__":
    main()
