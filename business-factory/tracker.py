#!/usr/bin/env python3
"""
Business Factory — Tracker
Checks Stripe revenue for all active businesses, applies kill/keep/grow/invest
criteria, and generates a weekly performance report.

Usage: python3 tracker.py
"""

import json
import datetime
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
STRIPE_KEY        = "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"
WORKSPACE         = Path(__file__).parent
ACTIVE_BUSINESSES = WORKSPACE / "active-businesses.json"
REPORT_FILE       = WORKSPACE / "performance-report.md"

# Kill/keep/grow thresholds (all in USD MRR equiv)
CRITERIA = {
    30:  {"keep": 50,  "kill_below": 1,   "action_keep": "KEEP",  "action_kill": "KILL"},
    60:  {"keep": 200, "kill_below": 50,  "action_keep": "GROW",  "action_kill": "KILL"},
    90:  {"keep": 500, "kill_below": None, "action_keep": "INVEST", "action_kill": None},
}

# Fast ROI rule: if no sale by first_sale_deadline → flag for kill review
FAST_ROI_GRACE_DAYS = 7


# ── Stripe helpers ────────────────────────────────────────────────────────────

def stripe_get(endpoint: str, params: dict = None) -> dict:
    url = f"https://api.stripe.com/v1/{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {STRIPE_KEY}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return {"ok": True, "data": json.loads(resp.read().decode())}
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": e.read().decode(), "status": e.code}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def get_product_revenue(product_id: str, since_date: str) -> dict:
    """
    Returns total revenue and estimated MRR for a Stripe product.
    since_date: ISO date string (launch date).

    Queries payment_intents filtered by metadata or charges for the product.
    """
    if not product_id or product_id in ("", "dry_run", None):
        return {"total_revenue": 0, "mrr": 0, "sale_count": 0, "error": "No product ID"}

    # Convert since_date to unix timestamp
    try:
        dt = datetime.datetime.fromisoformat(since_date)
        since_ts = int(dt.timestamp())
    except Exception:
        since_ts = 0

    # List all charges for this product via the price
    result = stripe_get("charges", {
        "limit": 100,
        "created[gte]": since_ts,
    })

    if not result["ok"]:
        return {"total_revenue": 0, "mrr": 0, "sale_count": 0, "error": result.get("error")}

    # Filter charges that mention our product (via metadata or description)
    total_cents = 0
    sale_count  = 0
    charges     = result["data"].get("data", [])

    for charge in charges:
        if charge.get("status") != "succeeded":
            continue
        # Check if this charge is for our product
        meta = charge.get("metadata", {})
        desc = charge.get("description", "")
        if product_id in str(meta) or product_id in str(desc):
            total_cents += charge.get("amount", 0)
            sale_count  += 1

    total_revenue = total_cents / 100

    # Estimate MRR: if one-time, annualize and divide by 12 for context
    # If recurring, total = MRR
    mrr = total_revenue  # simplified: treat all revenue as MRR equiv for scoring

    return {
        "total_revenue": total_revenue,
        "mrr":           mrr,
        "sale_count":    sale_count,
        "error":         None,
    }


def get_payment_link_revenue(payment_link_id: str) -> dict:
    """Alternative: query via payment link ID."""
    if not payment_link_id:
        return {"total_revenue": 0, "mrr": 0, "sale_count": 0}

    # Extract ID from URL if full URL given
    if payment_link_id.startswith("https://"):
        payment_link_id = payment_link_id.split("/")[-1]

    result = stripe_get(f"payment_links/{payment_link_id}/line_items")
    if not result["ok"]:
        return {"total_revenue": 0, "mrr": 0, "sale_count": 0,
                "error": result.get("error")}

    return {"total_revenue": 0, "mrr": 0, "sale_count": 0}  # Simplified


# ── Decision engine ───────────────────────────────────────────────────────────

def apply_criteria(business: dict, days_live: int, mrr: float, total_revenue: float) -> dict:
    """Returns recommended action and reasoning."""
    today_str = datetime.date.today().isoformat()

    # Fast ROI check first
    deadline = business.get("first_sale_deadline", "")
    if deadline and today_str > deadline and total_revenue == 0:
        return {
            "action":    "KILL",
            "reason":    f"No sales by first_sale_deadline ({deadline}). Fast ROI rule: kill after 7 days with $0.",
            "priority":  "HIGH",
        }

    # Milestone checks
    for milestone_day in sorted(CRITERIA.keys()):
        if days_live >= milestone_day:
            criteria = CRITERIA[milestone_day]
            if mrr >= criteria["keep"]:
                return {
                    "action": criteria["action_keep"],
                    "reason": f"Day {milestone_day}+ milestone: MRR ${mrr:.0f} ≥ threshold ${criteria['keep']}",
                    "priority": "NORMAL",
                }
            elif criteria["kill_below"] is not None and mrr < criteria["kill_below"]:
                return {
                    "action": criteria["action_kill"],
                    "reason": f"Day {milestone_day}+ milestone: MRR ${mrr:.0f} < kill threshold ${criteria['kill_below']}",
                    "priority": "HIGH",
                }

    # Within first 7 days — still in validation window
    if days_live <= 7:
        return {
            "action": "WATCH",
            "reason": f"Day {days_live}: still in 7-day validation window",
            "priority": "LOW",
        }

    # Between milestones — keep watching
    return {
        "action": "WATCH",
        "reason": f"Day {days_live}: MRR ${mrr:.0f} — between milestone checks",
        "priority": "LOW",
    }


def grow_actions(business: dict) -> list[str]:
    """Return a list of growth actions for a business hitting GROW milestone."""
    return [
        f"Add meta description + OG tags to {business['url']}/index.html",
        f"Post case study in r/entrepreneur: 'How I built {business['name']} in a weekend'",
        f"Submit to ProductHunt",
        f"Add affiliate/referral incentive (offer 20% for referrals)",
        f"Write a short tutorial/blog post targeting SEO: '{business['name']} alternative'",
    ]


def invest_actions(business: dict) -> list[str]:
    """Return expansion actions for $500+/mo businesses."""
    return [
        f"List on Gumroad (keep Stripe as primary, use Gumroad for discovery)",
        f"Submit to AppSumo marketplace",
        f"Create a lifetime deal at 10× monthly price",
        f"Run a paid Reddit/Twitter ad ($50 test budget)",
        f"Reach out to 3 newsletters in your niche for sponsored mention",
    ]


# ── Report generator ──────────────────────────────────────────────────────────

def generate_report(businesses: list, results: list) -> str:
    today    = datetime.date.today().isoformat()
    total_mrr = sum(r["mrr"] for r in results)
    total_rev = sum(r["total_revenue"] for r in results)

    kills  = [r for r in results if r["recommendation"]["action"] == "KILL"]
    grows  = [r for r in results if r["recommendation"]["action"] == "GROW"]
    invests = [r for r in results if r["recommendation"]["action"] == "INVEST"]
    watches = [r for r in results if r["recommendation"]["action"] == "WATCH"]
    keeps  = [r for r in results if r["recommendation"]["action"] == "KEEP"]

    lines = [
        f"# Business Factory — Weekly Report",
        f"**Generated:** {today}  ",
        f"**Active businesses:** {len(businesses)}  ",
        f"**Total MRR:** ${total_mrr:.2f}  ",
        f"**Total revenue (all time):** ${total_rev:.2f}",
        "",
        "---",
        "",
    ]

    # Executive summary
    lines += [
        "## Summary",
        "",
        f"- 🟢 **KEEP/INVEST/GROW:** {len(keeps) + len(invests) + len(grows)}",
        f"- 👀 **WATCH:** {len(watches)}",
        f"- 🔴 **KILL:** {len(kills)}",
        "",
    ]

    # Kills — highest priority
    if kills:
        lines += ["## 🔴 Kill List (action required)", ""]
        for r in kills:
            b = r["business"]
            lines += [
                f"### {b['name']} (`{b['id']}`)",
                f"- **URL:** {b['url']}",
                f"- **Days live:** {r['days_live']}",
                f"- **Revenue:** ${r['total_revenue']:.2f} total / ${r['mrr']:.2f} MRR",
                f"- **Reason:** {r['recommendation']['reason']}",
                f"- **Action:** Archive GitHub repo, deactivate Stripe product.",
                "",
            ]

    # Invest
    if invests:
        lines += ["## 🚀 Invest (scale these up)", ""]
        for r in invests:
            b = r["business"]
            lines += [
                f"### {b['name']} (`{b['id']}`)",
                f"- **URL:** {b['url']}",
                f"- **Days live:** {r['days_live']}",
                f"- **MRR:** ${r['mrr']:.2f} | **Total:** ${r['total_revenue']:.2f}",
                f"- **Reason:** {r['recommendation']['reason']}",
                "- **Next actions:**",
            ] + [f"  - {a}" for a in invest_actions(b)] + [""]

    # Grow
    if grows:
        lines += ["## 📈 Grow (add fuel)", ""]
        for r in grows:
            b = r["business"]
            lines += [
                f"### {b['name']} (`{b['id']}`)",
                f"- **URL:** {b['url']}",
                f"- **Days live:** {r['days_live']}",
                f"- **MRR:** ${r['mrr']:.2f} | **Total:** ${r['total_revenue']:.2f}",
                f"- **Reason:** {r['recommendation']['reason']}",
                "- **Next actions:**",
            ] + [f"  - {a}" for a in grow_actions(b)] + [""]

    # Keep
    if keeps:
        lines += ["## ✅ Keep (healthy, no action needed)", ""]
        for r in keeps:
            b = r["business"]
            lines += [
                f"- **{b['name']}** — MRR ${r['mrr']:.2f} | Day {r['days_live']} | {b['url']}",
            ]
        lines += [""]

    # Watch
    if watches:
        lines += ["## 👀 Watch (in validation window)", ""]
        for r in watches:
            b = r["business"]
            deadline = b.get("first_sale_deadline", "?")
            lines += [
                f"- **{b['name']}** — Day {r['days_live']} | First sale deadline: {deadline} | {b['url']}",
            ]
        lines += [""]

    # Full detail table
    lines += [
        "---",
        "",
        "## All Businesses Detail",
        "",
        "| Name | Days | MRR | Total | Status | Action |",
        "|------|------|-----|-------|--------|--------|",
    ]
    for r in results:
        b = r["business"]
        lines.append(
            f"| {b['name']} | {r['days_live']} | ${r['mrr']:.0f} | ${r['total_revenue']:.0f} | {b['status']} | {r['recommendation']['action']} |"
        )

    lines += [
        "",
        "---",
        f"*Report generated by Business Factory tracker.py — {today}*",
    ]

    return "\n".join(lines)


# ── Main pipeline ─────────────────────────────────────────────────────────────

def run_tracker():
    print("Business Factory Tracker — starting run")
    print("=" * 60)

    if not ACTIVE_BUSINESSES.exists():
        print("No active-businesses.json found. Nothing to track.")
        return

    with open(ACTIVE_BUSINESSES) as f:
        businesses = json.load(f)

    if not businesses:
        print("No active businesses to track.")
        return

    today    = datetime.date.today()
    results  = []
    updated  = []

    for b in businesses:
        if b["status"] == "killed":
            print(f"  Skipping {b['name']} (killed)")
            updated.append(b)
            continue

        print(f"\nChecking {b['name']}…")

        # Calculate days live
        try:
            launched = datetime.date.fromisoformat(b["launched_date"])
            days_live = (today - launched).days
        except Exception:
            days_live = 0

        # Get revenue from Stripe
        rev = get_product_revenue(b.get("stripe_product_id", ""), b["launched_date"])
        if rev.get("error"):
            print(f"  ⚠ Stripe error: {rev['error']}")

        mrr           = rev["mrr"]
        total_revenue = rev["total_revenue"]

        # Get recommendation
        recommendation = apply_criteria(b, days_live, mrr, total_revenue)

        print(f"  Days live: {days_live}")
        print(f"  MRR: ${mrr:.2f} | Total: ${total_revenue:.2f}")
        print(f"  → {recommendation['action']}: {recommendation['reason']}")

        # Update business record
        b_updated = dict(b)
        b_updated["mrr"]           = mrr
        b_updated["total_revenue"] = total_revenue
        b_updated["last_checked"]  = today.isoformat()

        if recommendation["action"] == "KILL":
            b_updated["status"] = "killed"
            print(f"  ✗ Marking as KILLED")

        updated.append(b_updated)

        results.append({
            "business":       b,
            "days_live":      days_live,
            "mrr":            mrr,
            "total_revenue":  total_revenue,
            "recommendation": recommendation,
            "stripe_error":   rev.get("error"),
        })

    # Save updated businesses
    with open(ACTIVE_BUSINESSES, "w") as f:
        json.dump(updated, f, indent=2)

    # Generate report
    report = generate_report([b for b in businesses if b["status"] != "killed"], results)
    with open(REPORT_FILE, "w") as f:
        f.write(report)

    print(f"\n{'='*60}")
    print(f"Report saved to {REPORT_FILE}")

    # Print kill list to stdout for immediate attention
    kills = [r for r in results if r["recommendation"]["action"] == "KILL"]
    if kills:
        print(f"\n⚠ KILL LIST ({len(kills)} businesses):")
        for r in kills:
            print(f"  • {r['business']['name']}: {r['recommendation']['reason']}")
    else:
        print("\n✓ No kills recommended this week.")

    total_mrr = sum(r["mrr"] for r in results)
    print(f"\nTotal MRR across all active businesses: ${total_mrr:.2f}")


if __name__ == "__main__":
    run_tracker()
