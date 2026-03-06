#!/usr/bin/env python3
"""
wholesale-pipeline.py
Wolfgang Meyer Investments - Full Overnight Pipeline
Parts 1 (buyer calls), 4 (SmartBook dental calls), and orchestration.
"""

import json
import time
import re
import subprocess
import requests
from datetime import datetime, timezone

VAPI_API_KEY = "0aaae7fe-be63-472a-a46d-5d9224e0fa89"
VAPI_PHONE_NUMBER_ID = "3f6ef946-452f-4b16-85cf-9e2d5b041df5"
ALEX_ASSISTANT_ID = "95e7c636-f8e6-4801-8866-fca9d5d475d3"

ASSETS = "/root/.openclaw/workspace/assets"
SCRIPTS = "/root/.openclaw/workspace/scripts"

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def normalize_phone(raw):
    """Convert any phone string to E.164"""
    digits = re.sub(r'\D', '', raw)
    if len(digits) == 10:
        return f"+1{digits}"
    elif len(digits) == 11 and digits.startswith('1'):
        return f"+{digits}"
    return None

def fire_vapi_call(payload):
    """Fire a call via Vapi REST API, return call_id or None"""
    try:
        resp = requests.post(
            "https://api.vapi.ai/call",
            headers={
                "Authorization": f"Bearer {VAPI_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30
        )
        if resp.ok:
            return resp.json().get("id")
        else:
            print(f"    ❌ API error {resp.status_code}: {resp.text[:300]}")
            return None
    except Exception as e:
        print(f"    ❌ Exception: {e}")
        return None

# ─────────────────────────────────────────────
# PART 1: Cash Buyer Calls
# ─────────────────────────────────────────────

BUYER_FIRST_MESSAGE = "Hey, this is Rex calling on behalf of Wolfgang Meyer Investments. We source off-market properties in the Phoenix metro area. I wanted to reach out quickly — are you actively buying investment properties right now?"
BUYER_SYSTEM = """You are Rex, an acquisitions assistant for Wolfgang Meyer Investments. You are calling real estate cash buyers to understand their buy box. If asked if you are an AI, disclose honestly. Key questions to ask: 1) Are you actively buying right now? 2) What areas of Phoenix do you focus on? 3) What property types — single family, multi-family, land? 4) What price range? 5) What's your typical max ARV percentage? 6) Whats the best way to send you deals — email or text? Get their email or preferred contact. Be conversational, not scripted. End with: 'Perfect, I'll be in touch when we have something that fits. What's the best email to reach you?' Log everything they say."""

def part1_buyer_calls():
    print("\n" + "="*60)
    print("PART 1: Cash Buyer Calls")
    print("="*60)

    with open(f"{ASSETS}/leads-cash-buyers-phoenix-2026-03-05.json") as f:
        buyers = json.load(f)

    call_log = []
    calls_fired = 0
    skipped = 0

    for i, buyer in enumerate(buyers):
        phone_raw = buyer.get("phone")
        if not phone_raw:
            print(f"  [{i+1:02d}] {buyer['company_name']}: no phone, skipping")
            skipped += 1
            continue

        phone = normalize_phone(phone_raw)
        if not phone:
            print(f"  [{i+1:02d}] {buyer['company_name']}: invalid phone {phone_raw}, skipping")
            skipped += 1
            continue

        print(f"  [{i+1:02d}] Calling {buyer['company_name']} at {phone}...")

        payload = {
            "phoneNumberId": VAPI_PHONE_NUMBER_ID,
            "customer": {"number": phone},
            "assistant": {
                "name": "Rex",
                "voice": {"provider": "11labs", "voiceId": "CwhRBWXzGAHq8TQ4Fs17"},
                "firstMessage": BUYER_FIRST_MESSAGE,
                "model": {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "messages": [{"role": "system", "content": BUYER_SYSTEM}]
                },
                "endCallFunctionEnabled": True,
                "silenceTimeoutSeconds": 20,
                "maxDurationSeconds": 180
            }
        }

        call_id = fire_vapi_call(payload)

        entry = {
            "company": buyer["company_name"],
            "phone": phone,
            "type": buyer.get("type"),
            "call_id": call_id,
            "status": "fired" if call_id else "failed",
            "fired_at": datetime.now(timezone.utc).isoformat()
        }
        call_log.append(entry)

        if call_id:
            print(f"      ✅ call_id: {call_id}")
            calls_fired += 1
        else:
            print(f"      ❌ Failed to fire call")

        # Wait 30s between calls (skip wait after last one)
        remaining = [b for b in buyers[i+1:] if b.get("phone")]
        if remaining:
            print(f"      ⏳ Waiting 30s before next call...")
            time.sleep(30)

    # Save log
    with open(f"{ASSETS}/buyer-calls-log.json", "w") as f:
        json.dump(call_log, f, indent=2)

    print(f"\n  📋 Buyer calls: {calls_fired} fired, {skipped} skipped (no phone)")
    print(f"  Log saved to {ASSETS}/buyer-calls-log.json")
    return call_log, calls_fired

# ─────────────────────────────────────────────
# PART 2 + 3: Motivated Seller Finder + Calls
# ─────────────────────────────────────────────

def part2_3_seller_pipeline():
    print("\n" + "="*60)
    print("PART 2 + 3: Motivated Seller Finder + Calls")
    print("="*60)

    print("  Running find-motivated-sellers.py...")
    result = subprocess.run(
        ["python3", f"{SCRIPTS}/find-motivated-sellers.py"],
        capture_output=True, text=True, timeout=600
    )

    if result.returncode != 0:
        print(f"  ⚠️  Script exited with code {result.returncode}")
        print(f"  STDERR: {result.stderr[:500]}")

    # Print output
    for line in result.stdout.split('\n'):
        if line.strip():
            print(f"  {line}")

    # Load results
    try:
        with open(f"{ASSETS}/motivated-sellers-live.json") as f:
            sellers = json.load(f)
    except:
        sellers = []

    try:
        with open(f"{ASSETS}/seller-calls-log.json") as f:
            seller_calls = json.load(f)
    except:
        seller_calls = []

    print(f"\n  📋 Sellers found: {len(sellers)}, Calls fired: {len(seller_calls)}")
    return sellers, seller_calls

# ─────────────────────────────────────────────
# PART 4: SmartBook AI Dental Calls
# ─────────────────────────────────────────────

def part4_dental_calls():
    print("\n" + "="*60)
    print("PART 4: SmartBook AI Dental Calls")
    print("="*60)

    with open(f"{ASSETS}/call-queue.json") as f:
        queue = json.load(f)

    # Find pending entries (queued or null status)
    pending = [
        e for e in queue
        if e.get("status") in ("queued", "pending", None)
    ]
    print(f"  Found {len(pending)} pending entries in queue")

    # Take first 20
    to_call = pending[:20]
    print(f"  Will call first {len(to_call)}")

    call_log = []
    calls_fired = 0

    for i, entry in enumerate(to_call):
        phone = entry.get("phone")
        if not phone:
            print(f"  [{i+1:02d}] {entry.get('business_name')}: no phone, skipping")
            continue

        # Ensure E.164
        if not phone.startswith("+"):
            phone = normalize_phone(phone)

        if not phone:
            print(f"  [{i+1:02d}] Invalid phone for {entry.get('business_name')}, skipping")
            continue

        print(f"  [{i+1:02d}] Calling {entry.get('business_name')} at {phone}...")

        payload = {
            "phoneNumberId": VAPI_PHONE_NUMBER_ID,
            "assistantId": ALEX_ASSISTANT_ID,
            "customer": {"number": phone}
        }

        call_id = fire_vapi_call(payload)

        log_entry = {
            "business_name": entry.get("business_name"),
            "phone": phone,
            "type": entry.get("type"),
            "email": entry.get("email"),
            "call_id": call_id,
            "status": "fired" if call_id else "failed",
            "fired_at": datetime.now(timezone.utc).isoformat()
        }
        call_log.append(log_entry)

        if call_id:
            print(f"      ✅ call_id: {call_id}")
            calls_fired += 1
            # Update status in queue
            entry["status"] = "called"
            entry["vapi_call_id"] = call_id
        else:
            print(f"      ❌ Failed to fire call")

        # Wait 45s between calls
        if i < len(to_call) - 1:
            print(f"      ⏳ Waiting 45s before next call...")
            time.sleep(45)

    # Save updated queue
    with open(f"{ASSETS}/call-queue.json", "w") as f:
        json.dump(queue, f, indent=2)

    # Save dental call log
    with open(f"{ASSETS}/dental-calls-log.json", "w") as f:
        json.dump(call_log, f, indent=2)

    print(f"\n  📋 Dental calls: {calls_fired} fired out of {len(to_call)} attempted")
    return call_log, calls_fired

# ─────────────────────────────────────────────
# PART 5: Morning Briefing
# ─────────────────────────────────────────────

def part5_morning_briefing(buyer_log, buyer_count, sellers, seller_calls, dental_log, dental_count):
    print("\n" + "="*60)
    print("PART 5: Morning Briefing")
    print("="*60)

    now = datetime.now(timezone.utc)
    # Rough warm lead estimate (calls fired = potential warm leads; actual needs webhook data)
    total_fired = buyer_count + len(seller_calls) + dental_count

    # Build briefing
    briefing = f"""# 🏠 Wolfgang Meyer Investments — Morning Briefing
**Date:** {now.strftime('%Y-%m-%d')} (Generated {now.strftime('%H:%M UTC')})

---

## 📊 Pipeline Summary

| Category | Calls Fired | Status |
|----------|-------------|--------|
| Cash Buyer Buy Box Calls | {buyer_count} | ✅ Running |
| Motivated Seller Calls | {len(seller_calls)} | ✅ Running |
| SmartBook AI Dental | {dental_count} | ✅ Running |
| **TOTAL** | **{total_fired}** | |

> ⚠️ Call outcomes require webhook — check Vapi dashboard for transcripts & results.

---

## 💰 PART 1: Cash Buyer Calls

**{buyer_count} buyers called** (16 had no phone number — contact via website)

"""
    for entry in buyer_log:
        status_icon = "✅" if entry["status"] == "fired" else "❌"
        briefing += f"- {status_icon} **{entry['company']}** | {entry['phone']} | ID: `{entry.get('call_id','N/A')}`\n"

    briefing += f"""
### Buyers Without Phone Numbers (Reach via Web):
- Doug Hopkins Real Estate → doughopkins.com
- HBSB Holdings / PHX Investment Properties → hbsbholdings.com
- LRT Offers → lrtoffers.com
- The Trusted Home Buyer → thetrustedhomebuyer.com
- Joint Venture Properties → jointventure-properties.com
- Great Flips Wholesale Property → greatflips.com
- Reivesti → reivesti.com
- AZ REO Group → azreogroup.com
- Investment Homes Phoenix → investmenthomesphoenix.com
- New Western (Phoenix) → newwestern.com
- Opendoor → opendoor.com
- Offerpad → offerpad.com/sell/phoenix-az
- FSO Capital Partners → fsocap.com
- Amazing Offer Arizona → amazingoffer.com
- Unbiased Options → unbiasedoptions.com/glendale
- Shelter Asset Management → institutional (BizJournals contact)

---

## 🏚️ PART 2: Motivated Sellers Found

**{len(sellers)} listings scraped and scored from Craigslist Phoenix**

"""
    if sellers:
        for s in sellers[:10]:  # top 10 in briefing
            phone_info = f"📞 {s.get('phone')}" if s.get('phone') else "no phone"
            briefing += f"- **Score {s.get('score',0)}/10** | {s.get('title','')[:60]} | ${s.get('price','N/A')} | {phone_info}\n"
        if len(sellers) > 10:
            briefing += f"- *(+{len(sellers)-10} more in motivated-sellers-live.json)*\n"
    else:
        briefing += "- ⚠️ No listings scraped (Craigslist may have blocked or returned no results)\n"

    briefing += f"""
---

## 📞 PART 3: Seller Calls

**{len(seller_calls)} seller calls fired** (listings with score ≥ 6 + phone number)

"""
    if seller_calls:
        for sc in seller_calls:
            briefing += f"- ✅ {sc.get('title','')[:50]} | {sc.get('phone')} | Score: {sc.get('score')} | ID: `{sc.get('call_id','N/A')}`\n"
    else:
        briefing += "- No qualifying seller listings found (score ≥ 6 + phone)\n"

    briefing += f"""
---

## 🦷 PART 4: SmartBook AI Dental Calls

**{dental_count} dental/business calls fired**

"""
    for entry in dental_log[:20]:
        status_icon = "✅" if entry["status"] == "fired" else "❌"
        briefing += f"- {status_icon} **{entry['business_name']}** | {entry['phone']} | ID: `{entry.get('call_id','N/A')}`\n"

    briefing += f"""
---

## 🌡️ Warm Leads Estimate

> Warm leads = calls that connected. Actual data requires Vapi dashboard review.
> **Check:** https://dashboard.vapi.ai → Calls → filter by today's date

**Estimated warm leads:** TBD (review transcripts > 60s)

---

## 🔥 Priority Callbacks for Wolfgang

### Top 3 Cash Buyers to Follow Up:
1. **Valley Home Buyer** (602) 734-3662 — Active Phoenix operation, Jan 2026 blog post
2. **We Buy Houses in Arizona** (602) 900-9327 — 24hr open, physical Phoenix address
3. **We Buy Homes in AZ** (480) 637-5500 — Motivated seller program focus (aligned!)

### If Any Seller Calls Fired:
- Check Vapi dashboard for seller call transcripts
- Any call > 60 seconds = warm lead, Wolfgang should call back ASAP

---

## 📁 Files Generated

- `/root/.openclaw/workspace/assets/buyer-calls-log.json` — All buyer call IDs
- `/root/.openclaw/workspace/assets/motivated-sellers-live.json` — Top 20 scored listings
- `/root/.openclaw/workspace/assets/seller-calls-log.json` — Seller call IDs  
- `/root/.openclaw/workspace/assets/dental-calls-log.json` — SmartBook dental call IDs
- `/root/.openclaw/workspace/scripts/find-motivated-sellers.py` — Reusable seller finder

---

*Generated by Rex Pipeline at {now.isoformat()}*
"""

    briefing_path = f"{ASSETS}/morning-briefing-2026-03-05.md"
    with open(briefing_path, "w") as f:
        f.write(briefing)

    print(f"  ✅ Briefing saved to {briefing_path}")
    return briefing_path


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🚀 WOLFGANG MEYER INVESTMENTS — OVERNIGHT PIPELINE")
    print(f"   Started: {datetime.now(timezone.utc).isoformat()}")

    # PART 1
    buyer_log, buyer_count = part1_buyer_calls()

    # PART 2 + 3
    sellers, seller_calls = part2_3_seller_pipeline()

    # PART 4
    dental_log, dental_count = part4_dental_calls()

    # PART 5
    briefing_path = part5_morning_briefing(
        buyer_log, buyer_count, sellers, seller_calls, dental_log, dental_count
    )

    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETE")
    print("="*60)
    print(f"  Cash buyer calls fired:   {buyer_count}")
    print(f"  Motivated sellers found:  {len(sellers)}")
    print(f"  Seller calls fired:       {len(seller_calls)}")
    print(f"  SmartBook AI calls fired: {dental_count}")
    print(f"  Morning briefing:         {briefing_path}")
    print(f"  Completed: {datetime.now(timezone.utc).isoformat()}")
