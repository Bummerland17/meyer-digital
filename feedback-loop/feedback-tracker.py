#!/usr/bin/env python3
"""
feedback-tracker.py — Weekly performance data collector
Collects from: Vapi calls, Email outreach, Stripe, GitHub Issues
Saves snapshot to: weekly-snapshots/YYYY-MM-DD.json
"""

import os
import json
import datetime
import requests
from collections import defaultdict

# ─── Config ───────────────────────────────────────────────────────────────────

VAPI_TOKEN      = "0aaae7fe-be63-472a-a46d-5d9224e0fa89"
GITHUB_TOKEN    = "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"
STRIPE_KEY      = os.getenv("STRIPE_SECRET_KEY", "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")

SNAPSHOT_DIR    = os.path.join(os.path.dirname(__file__), "weekly-snapshots")
EMAIL_QUEUE     = os.path.join(os.path.dirname(__file__), "..", "assets", "email-queue.json")
EMAIL_LOG       = os.path.join(os.path.dirname(__file__), "..", "assets", "email-log.json")

GITHUB_REPOS    = [
    "Bummerland17/honest-eats",
    "Bummerland17/unitfix-simple-maintenance",
]

os.makedirs(SNAPSHOT_DIR, exist_ok=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def safe_get(url, headers=None, params=None):
    """GET with graceful error handling — never crash the whole run."""
    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"_error": str(e)}


# ─── 1. Vapi Calls ────────────────────────────────────────────────────────────

def collect_vapi():
    """Fetch all calls from Vapi and compute engagement metrics."""
    headers = {"Authorization": f"Bearer {VAPI_TOKEN}"}
    data = safe_get("https://api.vapi.ai/call", headers=headers, params={"limit": 500})

    if "_error" in data:
        return {"status": "error", "error": data["_error"], "note": "Vapi may not be live yet"}

    calls = data if isinstance(data, list) else data.get("results", data.get("calls", []))

    total            = len(calls)
    short_hangups    = []   # < 30s — bad opener or wrong number
    warm_calls       = []   # > 3 min — worth studying
    booked           = []   # expressed interest / booked
    durations        = []

    for call in calls:
        duration = call.get("duration") or call.get("durationSeconds") or 0
        call_id  = call.get("id", "unknown")
        summary  = str(call.get("summary", "") or "")
        transcript= str(call.get("transcript", "") or "")
        combined = (summary + " " + transcript).lower()

        durations.append(duration)

        if duration < 30:
            short_hangups.append({
                "id":       call_id,
                "duration": duration,
                "created":  call.get("createdAt", ""),
                "flag":     "IMMEDIATE_HANGUP"
            })
        elif duration > 180:
            warm_calls.append({
                "id":       call_id,
                "duration": duration,
                "created":  call.get("createdAt", ""),
                "summary":  summary[:200],
                "flag":     "WARM_CONVERSATION"
            })

        interest_signals = ["interested", "book", "schedule", "send me", "tell me more",
                            "sounds good", "yes", "let's do it", "when can"]
        if any(sig in combined for sig in interest_signals):
            booked.append({"id": call_id, "signal": "expressed_interest"})

    avg_duration    = sum(durations) / len(durations) if durations else 0
    hangup_rate     = len(short_hangups) / total * 100 if total else 0
    warm_rate       = len(warm_calls) / total * 100 if total else 0
    interest_rate   = len(booked) / total * 100 if total else 0

    return {
        "status":           "live",
        "total_calls":      total,
        "avg_duration_sec": round(avg_duration, 1),
        "short_hangups":    len(short_hangups),
        "hangup_rate_pct":  round(hangup_rate, 1),
        "warm_calls":       len(warm_calls),
        "warm_rate_pct":    round(warm_rate, 1),
        "expressed_interest": len(booked),
        "interest_rate_pct": round(interest_rate, 1),
        "flagged_short":    short_hangups[:20],    # first 20 for inspection
        "flagged_warm":     warm_calls[:20],
        "flags": {
            "hook_needs_rewrite":   hangup_rate > 30,
            "close_needs_work":     interest_rate < 5 and total >= 20,
        }
    }


# ─── 2. Email Outreach ────────────────────────────────────────────────────────

def collect_email():
    """
    Parse email-log.json for reply-rate stats by subject line and business type.
    Falls back to email-queue.json if no log exists.
    Expected email-log.json format:
    [
      {"subject": "...", "business_type": "restaurant", "sent": true, "replied": false, "sent_at": "..."},
      ...
    ]
    """
    log_data = []

    for path in [EMAIL_LOG, EMAIL_QUEUE]:
        if os.path.exists(path):
            try:
                with open(path) as f:
                    raw = json.load(f)
                if isinstance(raw, list):
                    log_data = raw
                    break
                elif isinstance(raw, dict):
                    # queue format: {"emails": [...]}
                    log_data = raw.get("emails", raw.get("queue", []))
                    break
            except Exception:
                continue

    if not log_data:
        return {"status": "no_data", "note": "email-log.json not found — add logging to outreach scripts"}

    # Aggregate by subject line
    by_subject = defaultdict(lambda: {"sent": 0, "replied": 0})
    by_biz_type = defaultdict(lambda: {"sent": 0, "replied": 0})

    for entry in log_data:
        subj = entry.get("subject", "unknown")
        biz  = entry.get("business_type", "unknown")
        sent = bool(entry.get("sent", True))
        replied = bool(entry.get("replied", False))

        if sent:
            by_subject[subj]["sent"] += 1
            by_biz_type[biz]["sent"] += 1
        if replied:
            by_subject[subj]["replied"] += 1
            by_biz_type[biz]["replied"] += 1

    subject_stats = {}
    dead_subjects = []
    for subj, counts in by_subject.items():
        rate = counts["replied"] / counts["sent"] * 100 if counts["sent"] else 0
        subject_stats[subj] = {
            "sent":       counts["sent"],
            "replied":    counts["replied"],
            "reply_rate": round(rate, 2),
        }
        if counts["sent"] >= 50 and counts["replied"] == 0:
            dead_subjects.append(subj)

    biz_stats = {}
    dead_biz_types = []
    for biz, counts in by_biz_type.items():
        rate = counts["replied"] / counts["sent"] * 100 if counts["sent"] else 0
        biz_stats[biz] = {
            "sent":       counts["sent"],
            "replied":    counts["replied"],
            "reply_rate": round(rate, 2),
        }
        if counts["sent"] >= 20 and counts["replied"] == 0:
            dead_biz_types.append(biz)

    # Find best/worst subject lines
    ranked = sorted(subject_stats.items(), key=lambda x: x[1]["reply_rate"], reverse=True)
    best_subject = ranked[0] if ranked else None
    worst_subject = ranked[-1] if len(ranked) > 1 else None

    return {
        "status":           "live",
        "total_emails":     sum(v["sent"] for v in by_subject.values()),
        "total_replies":    sum(v["replied"] for v in by_subject.values()),
        "by_subject":       subject_stats,
        "by_business_type": biz_stats,
        "dead_subjects":    dead_subjects,
        "dead_biz_types":   dead_biz_types,
        "best_subject":     {"subject": best_subject[0], **best_subject[1]} if best_subject else None,
        "worst_subject":    {"subject": worst_subject[0], **worst_subject[1]} if worst_subject else None,
        "flags": {
            "dead_subject_lines": dead_subjects,
            "zero_reply_biz_types": dead_biz_types,
        }
    }


# ─── 3. Stripe ────────────────────────────────────────────────────────────────

def collect_stripe():
    """Fetch subscriptions, charges, and refunds from Stripe."""
    headers = {}
    auth    = (STRIPE_KEY, "")

    def stripe_get(path, params=None):
        try:
            r = requests.get(f"https://api.stripe.com/v1{path}",
                             auth=auth, params=params, timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    # Active subscriptions
    subs_data = stripe_get("/subscriptions", {"limit": 100, "status": "active"})
    subs = subs_data.get("data", [])

    # Cancelled (last 30 days)
    cancelled_data = stripe_get("/subscriptions", {"limit": 100, "status": "canceled"})
    cancelled = cancelled_data.get("data", [])

    # Refunds (last 30 days)
    refunds_data = stripe_get("/refunds", {"limit": 50})
    refunds = refunds_data.get("data", [])

    # Product conversion — group by product/price
    product_counts = defaultdict(int)
    mrr = 0
    for sub in subs:
        items = sub.get("items", {}).get("data", [])
        for item in items:
            plan = item.get("plan", {})
            product = plan.get("product", "unknown")
            amount  = plan.get("amount", 0)
            interval = plan.get("interval", "month")
            product_counts[product] += 1
            monthly = amount / 100 if interval == "month" else (amount / 100 / 12)
            mrr += monthly

    return {
        "status":               "live" if not subs_data.get("error") else "error",
        "error":                subs_data.get("error"),
        "active_subscribers":   len(subs),
        "mrr_usd":              round(mrr, 2),
        "cancelled_last_30d":   len(cancelled),
        "refund_requests":      len(refunds),
        "refund_amount_usd":    round(sum(r.get("amount", 0) for r in refunds) / 100, 2),
        "by_product":           dict(product_counts),
        "flags": {
            "refunds_flagged":  [{"id": r.get("id"), "amount": r.get("amount", 0)/100,
                                   "reason": r.get("reason")} for r in refunds],
            "churn_rate_approx": round(len(cancelled) / (len(subs) + len(cancelled)) * 100, 1)
                                  if (len(subs) + len(cancelled)) > 0 else 0,
        }
    }


# ─── 4. GitHub Issues ─────────────────────────────────────────────────────────

def collect_github():
    """Fetch open issues from all repos, categorize and flag hot issues."""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    all_repos = {}

    for repo in GITHUB_REPOS:
        data = safe_get(
            f"https://api.github.com/repos/{repo}/issues",
            headers=headers,
            params={"state": "open", "per_page": 100}
        )

        if "_error" in data or isinstance(data, dict):
            all_repos[repo] = {"status": "error", "error": data.get("_error", "unexpected format")}
            continue

        issues = data  # list
        categorized = {"bug": [], "ux": [], "feature": [], "other": []}
        hot_issues  = []

        for issue in issues:
            title    = (issue.get("title") or "").lower()
            body     = (issue.get("body") or "").lower()
            labels   = [l.get("name", "").lower() for l in issue.get("labels", [])]
            comments = issue.get("comments", 0)
            reactions = issue.get("reactions", {}).get("total_count", 0)
            engagement = comments + reactions

            combined = title + " " + body + " " + " ".join(labels)

            # Categorize
            if any(w in combined for w in ["bug", "error", "crash", "broken", "fix", "fail"]):
                cat = "bug"
            elif any(w in combined for w in ["ux", "ui", "design", "confus", "friction",
                                              "hard to", "difficult", "unclear"]):
                cat = "ux"
            elif any(w in combined for w in ["feature", "request", "add", "would be nice",
                                              "suggest", "enhancement"]):
                cat = "feature"
            else:
                cat = "other"

            entry = {
                "id":        issue.get("number"),
                "title":     issue.get("title"),
                "category":  cat,
                "comments":  comments,
                "reactions": reactions,
                "url":       issue.get("html_url"),
                "labels":    labels,
            }
            categorized[cat].append(entry)

            if engagement >= 3:
                hot_issues.append({**entry, "engagement": engagement, "flag": "HIGH_ENGAGEMENT"})

        all_repos[repo] = {
            "status":       "live",
            "total_issues": len(issues),
            "bugs":         len(categorized["bug"]),
            "ux_issues":    len(categorized["ux"]),
            "features":     len(categorized["feature"]),
            "other":        len(categorized["other"]),
            "hot_issues":   sorted(hot_issues, key=lambda x: x["engagement"], reverse=True),
            "by_category":  categorized,
        }

    return all_repos


# ─── 5. Assemble & Save Snapshot ──────────────────────────────────────────────

def run():
    today = datetime.date.today().isoformat()
    snapshot_path = os.path.join(SNAPSHOT_DIR, f"{today}.json")

    print(f"📊 Collecting feedback data for {today}...")

    print("  → Vapi calls...")
    vapi = collect_vapi()

    print("  → Email outreach...")
    email = collect_email()

    print("  → Stripe...")
    stripe = collect_stripe()

    print("  → GitHub issues...")
    github = collect_github()

    snapshot = {
        "date":       today,
        "generated":  datetime.datetime.utcnow().isoformat() + "Z",
        "vapi":       vapi,
        "email":      email,
        "stripe":     stripe,
        "github":     github,
    }

    with open(snapshot_path, "w") as f:
        json.dump(snapshot, f, indent=2, default=str)

    print(f"\n✅ Snapshot saved → {snapshot_path}")

    # Quick summary
    print("\n── Summary ──────────────────────────────────────")
    if vapi.get("status") == "live":
        print(f"  Calls:    {vapi['total_calls']} total | "
              f"{vapi['hangup_rate_pct']}% hangups | "
              f"{vapi['interest_rate_pct']}% interest")
    else:
        print(f"  Calls:    {vapi.get('note', 'unavailable')}")

    if stripe.get("status") == "live":
        print(f"  Stripe:   {stripe['active_subscribers']} subs | "
              f"${stripe['mrr_usd']}/mo MRR | "
              f"{stripe['cancelled_last_30d']} cancellations")
    else:
        print(f"  Stripe:   {stripe.get('error', 'unavailable')}")

    for repo, rd in github.items():
        if rd.get("status") == "live":
            print(f"  {repo.split('/')[1]}: "
                  f"{rd['total_issues']} issues | "
                  f"{rd['bugs']} bugs | "
                  f"{rd['ux_issues']} UX | "
                  f"{len(rd['hot_issues'])} hot")

    return snapshot_path


if __name__ == "__main__":
    run()
