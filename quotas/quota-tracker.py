#!/usr/bin/env python3
"""
Quota Tracker — Daily production quota system
Usage:
  quota-tracker.py status          — show today's progress
  quota-tracker.py log <metric> <n> — log n units for metric
  quota-tracker.py check            — check quotas, flag misses, auto-raise if needed
  quota-tracker.py reset            — reset today's counters (called at midnight)

Metrics: apps_built, outreach_emails, social_posts, cold_calls, content_pieces

State saved to: quotas/quota-state.json
"""

import json, sys, datetime, os
from pathlib import Path

WORKSPACE  = Path("/root/.openclaw/workspace")
STATE_FILE = WORKSPACE / "quotas/quota-state.json"
TODAY      = str(datetime.date.today())

# Default targets
DEFAULT_TARGETS = {
    "apps_built":       1,
    "outreach_emails":  10,
    "social_posts":     5,
    "cold_calls":       10,
    "content_pieces":   3,
}

METRIC_LABELS = {
    "apps_built":      "Apps/Sites Built",
    "outreach_emails": "Outreach Emails",
    "social_posts":    "Social Posts",
    "cold_calls":      "Cold Calls (Vapi)",
    "content_pieces":  "Content Pieces",
}

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def ensure_today(state):
    """Initialize today's entry if it doesn't exist."""
    if "today" not in state or state.get("today_date") != TODAY:
        # Archive yesterday before resetting
        if "today" in state and "today_date" in state:
            history = state.setdefault("history", {})
            history[state["today_date"]] = state["today"].copy()
        state["today"] = {k: 0 for k in DEFAULT_TARGETS}
        state["today_date"] = TODAY
    return state

def get_targets(state):
    """Get current targets (may be auto-raised)."""
    return state.get("targets", DEFAULT_TARGETS.copy())

def check_auto_raise(state):
    """If any metric exceeded 3 days in a row, raise target by 20%."""
    history = state.get("history", {})
    targets = get_targets(state)
    changes = []
    
    for metric in DEFAULT_TARGETS:
        # Get last 3 days
        dates = sorted(history.keys())[-3:]
        if len(dates) < 3:
            continue
        exceeded_all = all(
            history.get(d, {}).get(metric, 0) >= targets.get(metric, DEFAULT_TARGETS[metric])
            for d in dates
        )
        if exceeded_all:
            old = targets[metric]
            new = round(old * 1.2)
            if new != old:
                targets[metric] = new
                changes.append(f"{METRIC_LABELS[metric]}: {old} → {new} (+20%)")
    
    if changes:
        state["targets"] = targets
        state.setdefault("target_history", []).append({
            "date": TODAY,
            "reason": "exceeded 3 days in a row",
            "changes": changes
        })
    
    return changes

def cmd_status(state):
    """Print today's quota status."""
    state = ensure_today(state)
    targets = get_targets(state)
    today = state["today"]
    
    print(f"\n📊 Quota Status — {TODAY}")
    print("=" * 45)
    all_met = True
    for metric, label in METRIC_LABELS.items():
        actual = today.get(metric, 0)
        target = targets.get(metric, DEFAULT_TARGETS[metric])
        pct = int((actual / target * 100)) if target > 0 else 0
        bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
        status = "✅" if actual >= target else "❌"
        print(f"{status} {label:<25} {actual:>3}/{target:<3}  [{bar}] {pct}%")
        if actual < target:
            all_met = False
    
    print("=" * 45)
    if all_met:
        print("🏆 All quotas met today!")
    else:
        print("⚠️  Some quotas not yet met.")
    
    # Show streak info
    history = state.get("history", {})
    if history:
        recent = sorted(history.keys())[-7:]
        streak_days = 0
        for d in reversed(recent):
            day_data = history[d]
            tgts = get_targets(state)
            if all(day_data.get(m, 0) >= tgts.get(m, DEFAULT_TARGETS[m]) for m in DEFAULT_TARGETS):
                streak_days += 1
            else:
                break
        if streak_days > 0:
            print(f"\n🔥 Current streak: {streak_days} day(s) with all quotas met")
    
    return all_met

def cmd_log(state, metric, count):
    """Log n units for a metric."""
    state = ensure_today(state)
    if metric not in DEFAULT_TARGETS:
        print(f"❌ Unknown metric: {metric}")
        print(f"   Valid: {', '.join(DEFAULT_TARGETS.keys())}")
        return state
    
    state["today"][metric] = state["today"].get(metric, 0) + count
    label = METRIC_LABELS[metric]
    new_val = state["today"][metric]
    target = get_targets(state).get(metric, DEFAULT_TARGETS[metric])
    print(f"✅ Logged {count} {label}(s) — now at {new_val}/{target}")
    return state

def cmd_check(state):
    """Check quotas, flag misses, auto-raise if needed. Returns flag data."""
    state = ensure_today(state)
    targets = get_targets(state)
    today = state["today"]
    
    misses = []
    for metric, label in METRIC_LABELS.items():
        actual = today.get(metric, 0)
        target = targets.get(metric, DEFAULT_TARGETS[metric])
        if actual < target:
            misses.append({
                "metric": metric,
                "label": label,
                "actual": actual,
                "target": target,
                "shortfall": target - actual
            })
    
    # Check auto-raise
    raises = check_auto_raise(state)
    
    # Save flags for daily review to pick up
    state["last_check"] = {
        "date": TODAY,
        "misses": misses,
        "auto_raises": raises
    }
    
    if misses:
        print(f"\n⚠️  {len(misses)} quota(s) not met today:")
        for m in misses:
            print(f"   {m['label']}: {m['actual']}/{m['target']} (short by {m['shortfall']})")
    else:
        print("✅ All quotas met!")
    
    if raises:
        print(f"\n📈 Auto-raised {len(raises)} target(s) (exceeded 3 days in a row):")
        for r in raises:
            print(f"   {r}")
    
    return state, misses

def cmd_reset(state):
    """Reset today's counters (called at midnight cron)."""
    state = ensure_today(state)
    history = state.setdefault("history", {})
    history[TODAY] = state["today"].copy()
    
    # Check auto-raises before resetting
    raises = check_auto_raise(state)
    
    # Reset for new day
    tomorrow = str(datetime.date.today() + datetime.timedelta(days=1))
    state["today"] = {k: 0 for k in DEFAULT_TARGETS}
    state["today_date"] = tomorrow
    
    print(f"✅ Daily quotas reset for {tomorrow}")
    if raises:
        print(f"📈 Auto-raised: {', '.join(raises)}")
    return state

def main():
    state = load_state()
    args = sys.argv[1:]
    
    if not args or args[0] == "status":
        state = ensure_today(state)
        cmd_status(state)
        save_state(state)
    
    elif args[0] == "log":
        if len(args) < 3:
            print("Usage: quota-tracker.py log <metric> <count>")
            sys.exit(1)
        metric = args[1]
        try:
            count = int(args[2])
        except ValueError:
            print(f"Count must be a number, got: {args[2]}")
            sys.exit(1)
        state = cmd_log(state, metric, count)
        save_state(state)
    
    elif args[0] == "check":
        state, misses = cmd_check(state)
        save_state(state)
        sys.exit(1 if misses else 0)
    
    elif args[0] == "reset":
        state = cmd_reset(state)
        save_state(state)
    
    else:
        print(f"Unknown command: {args[0]}")
        print("Usage: quota-tracker.py [status|log|check|reset]")
        sys.exit(1)

if __name__ == "__main__":
    main()
