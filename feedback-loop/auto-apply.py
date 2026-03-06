#!/usr/bin/env python3
"""
auto-apply.py — Automatically applies low-risk improvements where data is clear.

Safe to auto-apply:
  ✅ Email subject line swaps (when one outperforms 2x+, 50+ sends each)
  ✅ Retiring dead subject lines from the email queue
  ✅ Removing zero-reply business types from targeting

Requires human QA (flags only):
  🚩 Agent call scripts (Scribe)
  🚩 Landing page copy (Pixel)
  🚩 Pricing / product changes (Spark)
"""

import os
import json
import glob
import datetime
import shutil

SNAPSHOT_DIR  = os.path.join(os.path.dirname(__file__), "weekly-snapshots")
EMAIL_QUEUE   = os.path.join(os.path.dirname(__file__), "..", "assets", "email-queue.json")
EMAIL_TEMPLATES = os.path.join(os.path.dirname(__file__), "..", "assets", "email-templates.json")
APPLY_LOG     = os.path.join(os.path.dirname(__file__), "auto-apply-log.json")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def load_latest_snapshot():
    files = sorted(glob.glob(os.path.join(SNAPSHOT_DIR, "*.json")))
    if not files:
        return None
    with open(files[-1]) as f:
        return json.load(f)


def load_json_safe(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        print(f"  ⚠ Could not load {path}: {e}")
        return None


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    backup = path + ".bak"
    if os.path.exists(path):
        shutil.copy2(path, backup)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def log_action(action, detail, result):
    log = load_json_safe(APPLY_LOG) or []
    log.append({
        "date":   datetime.datetime.utcnow().isoformat() + "Z",
        "action": action,
        "detail": detail,
        "result": result,
    })
    save_json(APPLY_LOG, log)
    print(f"  ✅ AUTO-APPLIED: {action} — {detail[:80]}")


# ─── Email Subject Line Optimization ──────────────────────────────────────────

def apply_email_optimizations(snapshot):
    """
    Auto-apply email improvements where data is conclusive:
    1. Retire subject lines with 0 replies after 50+ sends
    2. Promote winning subject line when 2x+ better with 50+ sends each
    """
    email = snapshot.get("email", {})
    if email.get("status") != "live":
        print("  ℹ Email data not available — skipping")
        return 0

    applied = 0
    by_subject = email.get("by_subject", {})
    dead_subjects = email.get("dead_subjects", [])
    best = email.get("best_subject")
    worst = email.get("worst_subject")

    # Load email templates
    templates = load_json_safe(EMAIL_TEMPLATES)
    if not templates:
        print("  ℹ No email-templates.json found — creating stub for future use")
        stub = {
            "_note": "Auto-managed by auto-apply.py. Subject lines are updated based on performance.",
            "active_subjects": [],
            "retired_subjects": [],
            "last_updated": datetime.date.today().isoformat(),
        }
        # populate with current subjects
        for subj, stats in by_subject.items():
            stub["active_subjects"].append({
                "subject":    subj,
                "sent":       stats["sent"],
                "reply_rate": stats["reply_rate"],
                "status":     "active",
            })
        save_json(EMAIL_TEMPLATES, stub)
        templates = stub

    changed = False

    # Retire dead subject lines
    for dead_subj in dead_subjects:
        active = templates.get("active_subjects", [])
        still_active = [s for s in active if s["subject"] != dead_subj]
        if len(still_active) < len(active):
            retired = templates.get("retired_subjects", [])
            retired.append({
                "subject":      dead_subj,
                "retired_date": datetime.date.today().isoformat(),
                "reason":       f"0 replies after {by_subject.get(dead_subj, {}).get('sent', '50+')} sends",
                "sent":         by_subject.get(dead_subj, {}).get("sent", 0),
            })
            templates["active_subjects"] = still_active
            templates["retired_subjects"] = retired
            templates["last_updated"] = datetime.date.today().isoformat()
            changed = True
            log_action(
                "RETIRE_SUBJECT_LINE",
                f"'{dead_subj}' — 0 replies after {by_subject.get(dead_subj,{}).get('sent','?')} sends",
                "Moved to retired_subjects in email-templates.json"
            )
            applied += 1

    # Promote winning subject line
    if best and worst and best["subject"] != worst["subject"]:
        best_rate  = best.get("reply_rate", 0)
        worst_rate = worst.get("reply_rate", 0)
        best_sent  = best.get("sent", 0)
        worst_sent = worst.get("sent", 0)

        # Only auto-apply if: 2x+ better, 50+ sends each, not already retired
        if (worst_rate > 0 and best_rate / worst_rate >= 2.0
                and best_sent >= 50 and worst_sent >= 50):
            active = templates.get("active_subjects", [])
            to_retire = [s for s in active if s["subject"] == worst["subject"]]
            still_active = [s for s in active if s["subject"] != worst["subject"]]

            # Ensure winner is first (highest priority)
            for s in still_active:
                if s["subject"] == best["subject"]:
                    s["promoted_date"] = datetime.date.today().isoformat()
                    s["promoted_reason"] = f"{best_rate:.1f}% vs {worst_rate:.1f}% reply rate"

            if to_retire:
                retired = templates.get("retired_subjects", [])
                retired.append({
                    "subject":      worst["subject"],
                    "retired_date": datetime.date.today().isoformat(),
                    "reason":       f"Outperformed by '{best['subject']}' ({best_rate:.1f}% vs {worst_rate:.1f}%)",
                    "sent":         worst_sent,
                    "reply_rate":   worst_rate,
                })
                templates["active_subjects"] = still_active
                templates["retired_subjects"] = retired
                templates["last_updated"] = datetime.date.today().isoformat()
                changed = True
                log_action(
                    "PROMOTE_SUBJECT_LINE",
                    f"'{best['subject']}' ({best_rate:.1f}%) beats '{worst['subject']}' ({worst_rate:.1f}%)",
                    f"Retired loser, winner marked as primary. Ratio: {best_rate/worst_rate:.1f}x"
                )
                applied += 1

    if changed:
        save_json(EMAIL_TEMPLATES, templates)

    # Also update email-queue.json if it exists (remove dead subject emails from future sends)
    queue_data = load_json_safe(EMAIL_QUEUE)
    if queue_data and dead_subjects:
        original_count = 0
        updated_count = 0

        if isinstance(queue_data, list):
            original_count = len(queue_data)
            updated = [e for e in queue_data
                       if e.get("subject") not in dead_subjects or e.get("sent", False)]
            updated_count = len(updated)
            if updated_count < original_count:
                save_json(EMAIL_QUEUE, updated)
                removed = original_count - updated_count
                log_action(
                    "CLEAN_EMAIL_QUEUE",
                    f"Removed {removed} unsent emails with dead subject lines",
                    f"{original_count} → {updated_count} queued emails"
                )
                applied += 1

    return applied


# ─── Business Type Targeting ───────────────────────────────────────────────────

def apply_targeting_cleanup(snapshot):
    """Remove zero-reply business types from targeting list."""
    email = snapshot.get("email", {})
    if email.get("status") != "live":
        return 0

    dead_biz = email.get("dead_biz_types", [])
    if not dead_biz:
        return 0

    # Look for a targeting config file
    targeting_paths = [
        os.path.join(os.path.dirname(__file__), "..", "assets", "targeting.json"),
        os.path.join(os.path.dirname(__file__), "..", "assets", "outreach-config.json"),
    ]

    applied = 0
    for path in targeting_paths:
        data = load_json_safe(path)
        if not data:
            continue

        business_types = data.get("business_types", data.get("target_types", []))
        if not business_types:
            continue

        updated = [b for b in business_types if b not in dead_biz]
        if len(updated) < len(business_types):
            removed = [b for b in business_types if b in dead_biz]
            data["business_types"] = updated
            data["retired_types"] = data.get("retired_types", []) + [
                {"type": b, "retired_date": datetime.date.today().isoformat(),
                 "reason": "0 replies after 20+ sends"}
                for b in removed
            ]
            save_json(path, data)
            log_action(
                "RETIRE_BUSINESS_TYPE",
                f"Removed {removed} from targeting",
                f"Updated {os.path.basename(path)}"
            )
            applied += 1

    if not applied and dead_biz:
        # No targeting file found — just log it
        log_action(
            "FLAG_BUSINESS_TYPE_CLEANUP",
            f"Dead business types identified but no targeting.json found: {dead_biz}",
            "Manual: remove from outreach targeting list"
        )

    return applied


# ─── Flags for Human Review ───────────────────────────────────────────────────

def flag_for_human_review(snapshot):
    """
    Generate a human-review section for things that need QA before applying.
    These go into the auto-apply log as FLAGGED items.
    """
    flags = []
    today = datetime.date.today().isoformat()

    # Call script issues (Scribe must QA)
    vapi = snapshot.get("vapi", {})
    if vapi.get("flags", {}).get("hook_needs_rewrite"):
        flags.append({
            "date":   today,
            "action": "FLAG_FOR_SCRIBE",
            "detail": f"Hangup rate {vapi.get('hangup_rate_pct')}% — call opener needs QA rewrite",
            "result": "⚠️ FLAGGED — requires Scribe review before applying",
        })

    if vapi.get("flags", {}).get("close_needs_work"):
        flags.append({
            "date":   today,
            "action": "FLAG_FOR_SCRIBE",
            "detail": f"Interest rate {vapi.get('interest_rate_pct')}% — close sequence needs QA review",
            "result": "⚠️ FLAGGED — requires Scribe review before applying",
        })

    # Stripe refunds (Pixel/product review)
    stripe = snapshot.get("stripe", {})
    for refund in stripe.get("flags", {}).get("refunds_flagged", []):
        flags.append({
            "date":   today,
            "action": "FLAG_FOR_PIXEL",
            "detail": f"Refund ${refund['amount']:.2f} — possible UX/onboarding issue",
            "result": "⚠️ FLAGGED — review onboarding flow",
        })

    # Hot GitHub issues
    github = snapshot.get("github", {})
    for repo, repo_data in github.items():
        for issue in repo_data.get("hot_issues", [])[:3]:
            if issue.get("category") == "ux":
                flags.append({
                    "date":   today,
                    "action": "FLAG_FOR_PIXEL",
                    "detail": f"[{repo.split('/')[1]}] Hot UX issue #{issue['id']}: {issue['title']}",
                    "result": f"⚠️ FLAGGED — {issue['url']}",
                })

    # Log all flags
    if flags:
        log = load_json_safe(APPLY_LOG) or []
        log.extend(flags)
        save_json(APPLY_LOG, log)
        for f in flags:
            print(f"  🚩 FLAGGED FOR HUMAN REVIEW: {f['action']} — {f['detail'][:70]}")

    return len(flags)


# ─── Summary Report ───────────────────────────────────────────────────────────

def generate_summary(snapshot, applied_count, flagged_count):
    """Build a human-readable summary for Wolfgang's Telegram alert."""
    vapi   = snapshot.get("vapi", {})
    stripe = snapshot.get("stripe", {})

    prev_log = load_json_safe(APPLY_LOG) or []
    # Find last week's metrics in log (crude — compare by date)
    prev_hangup  = None
    prev_mrr     = None
    for entry in reversed(prev_log):
        if "hangup_rate" in str(entry.get("detail", "")):
            try:
                prev_hangup = float(entry["detail"].split("hangup_rate=")[1].split("%")[0])
                break
            except Exception:
                pass

    call_line = ""
    if vapi.get("status") == "live":
        hangup = vapi.get("hangup_rate_pct", "?")
        interest = vapi.get("interest_rate_pct", "?")
        call_line = f"📞 Calls: {vapi.get('total_calls')} total | {hangup}% hangup | {interest}% interest"
        if prev_hangup:
            delta = float(hangup) - prev_hangup
            call_line += f" (hangup {'+' if delta>0 else ''}{delta:.1f}pp vs last week)"

    stripe_line = ""
    if stripe.get("status") == "live":
        stripe_line = f"💰 Stripe: {stripe.get('active_subscribers')} subs | ${stripe.get('mrr_usd')}/mo MRR"

    summary = f"""📊 Weekly Feedback Loop Summary — {datetime.date.today().isoformat()}

✅ {applied_count} improvement(s) auto-applied
🚩 {flagged_count} item(s) flagged for human review
📝 Full queue → feedback-loop/improvement-queue.md

{call_line}
{stripe_line}

Run `cat /root/.openclaw/workspace/feedback-loop/improvement-queue.md` for full task list.
""".strip()

    return summary


# ─── Main ─────────────────────────────────────────────────────────────────────

def run():
    print("⚡ Running auto-apply...")

    snapshot = load_latest_snapshot()
    if not snapshot:
        print("  ✗ No snapshot found. Run feedback-tracker.py first.")
        return

    print(f"  → Snapshot date: {snapshot.get('date', 'unknown')}")
    print()

    print("── Email optimizations ──────────────────────────")
    email_applied = apply_email_optimizations(snapshot)

    print()
    print("── Targeting cleanup ────────────────────────────")
    targeting_applied = apply_targeting_cleanup(snapshot)

    print()
    print("── Flagging items for human review ─────────────")
    flagged = flag_for_human_review(snapshot)

    total_applied = email_applied + targeting_applied

    print()
    summary = generate_summary(snapshot, total_applied, flagged)
    print("── Weekly Summary ───────────────────────────────")
    print(summary)

    # Save summary for heartbeat to pick up
    summary_path = os.path.join(os.path.dirname(__file__), "latest-summary.txt")
    with open(summary_path, "w") as f:
        f.write(summary)
    print(f"\n✅ Summary saved → {summary_path}")

    return {
        "applied": total_applied,
        "flagged": flagged,
        "summary": summary,
    }


if __name__ == "__main__":
    run()
