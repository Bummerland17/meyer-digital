#!/usr/bin/env python3
"""
Monthly Review — runs 1st of each month at 08:00 UTC
Full MRR report, product rankings, kill list, promote list
Saves to /reviews/monthly/YYYY-MM.md
"""

import json, os, datetime, re, requests
from pathlib import Path
from collections import defaultdict

WORKSPACE   = Path("/root/.openclaw/workspace")
STRIPE_KEY  = "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"
BOT_TOKEN   = json.load(open("/root/.openclaw/openclaw.json"))["channels"]["telegram"]["botToken"]
CHAT_ID     = "8654703697"
TODAY       = datetime.date.today()
LAST_MONTH  = TODAY.replace(day=1) - datetime.timedelta(days=1)
MONTH_LABEL = LAST_MONTH.strftime("%Y-%m")
OUTPUT_DIR  = WORKSPACE / "reviews/monthly"
DAILY_DIR   = WORKSPACE / "reviews/daily"
PRODUCTS_FILE = WORKSPACE / "assets/products.json"

def tg(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"},
            timeout=10
        )
    except Exception as e:
        print(f"Telegram error: {e}")

def stripe_full_report():
    """Pull full Stripe subscription data for monthly MRR breakdown."""
    try:
        r = requests.get(
            "https://api.stripe.com/v1/subscriptions",
            params={"limit": 100, "status": "active", "expand[]": "data.plan.product"},
            auth=(STRIPE_KEY, ""),
            timeout=15
        )
        subs = r.json().get("data", [])
        
        # Also get products for names
        prod_r = requests.get(
            "https://api.stripe.com/v1/products",
            params={"limit": 100, "active": "true"},
            auth=(STRIPE_KEY, ""),
            timeout=15
        )
        products = {p["id"]: p["name"] for p in prod_r.json().get("data", [])}
        
        mrr_by_product = defaultdict(float)
        subs_by_product = defaultdict(int)
        
        for s in subs:
            for item in s.get("items", {}).get("data", []):
                plan = item.get("plan", {})
                amount = plan.get("amount", 0) / 100
                interval = plan.get("interval", "month")
                if interval == "year":
                    amount = amount / 12
                prod_id = plan.get("product", "unknown")
                prod_name = products.get(prod_id, prod_id)
                mrr_by_product[prod_name] += amount
                subs_by_product[prod_name] += 1
        
        total_mrr = sum(mrr_by_product.values())
        return dict(mrr_by_product), dict(subs_by_product), round(total_mrr, 2), len(subs)
    except Exception as e:
        print(f"Stripe error: {e}")
        return {}, {}, 0, 0

def get_monthly_daily_average(month_str):
    """Get average MRR readings from daily reviews for a given month."""
    mrr_values = []
    for path in DAILY_DIR.glob(f"{month_str}-*.md"):
        text = path.read_text()
        m = re.search(r"\*\*MRR:\*\*\s*\$?([\d.]+)", text)
        if m:
            mrr_values.append(float(m.group(1)))
    return sum(mrr_values) / len(mrr_values) if mrr_values else 0

def load_products():
    """Load known products from products.json or derive from Stripe data."""
    if PRODUCTS_FILE.exists():
        return json.loads(PRODUCTS_FILE.read_text())
    return []

def save_monthly_state(mrr_by_product):
    """Save current month's MRR for next month's comparison."""
    monthly_state_file = WORKSPACE / "assets/monthly-mrr-history.json"
    history = {}
    if monthly_state_file.exists():
        history = json.loads(monthly_state_file.read_text())
    history[MONTH_LABEL] = mrr_by_product
    monthly_state_file.write_text(json.dumps(history, indent=2))
    return history

def load_last_month_mrr():
    """Load previous month's MRR for comparison."""
    state_file = WORKSPACE / "assets/monthly-mrr-history.json"
    if not state_file.exists():
        return {}
    history = json.loads(state_file.read_text())
    two_months_ago = (LAST_MONTH.replace(day=1) - datetime.timedelta(days=1)).strftime("%Y-%m")
    return history.get(two_months_ago, {})

def main():
    print(f"[monthly-review] Running for {MONTH_LABEL}")
    
    mrr_by_product, subs_by_product, total_mrr, total_subs = stripe_full_report()
    last_month_mrr = load_last_month_mrr()
    history = save_monthly_state(mrr_by_product)
    
    # Rank products
    ranked = sorted(mrr_by_product.items(), key=lambda x: -x[1])
    
    # Kill list: $0 MRR after 30 days
    kill_list = []
    promote_list = []
    
    for prod, mrr_val in ranked:
        last_val = last_month_mrr.get(prod, 0)
        if mrr_val == 0 and last_val == 0:
            kill_list.append(prod)
        elif mrr_val > last_val * 1.2:  # 20%+ growth
            promote_list.append((prod, mrr_val, last_val))
    
    # Also check products.json for any that have been live 30+ days with $0
    known_products = load_products()
    for p in known_products:
        name = p.get("name", "")
        launch_date = p.get("launched", "")
        if launch_date:
            days_live = (TODAY - datetime.date.fromisoformat(launch_date)).days
            if days_live >= 30 and mrr_by_product.get(name, 0) == 0:
                if name not in kill_list:
                    kill_list.append(f"{name} (launched {launch_date}, {days_live}d ago)")
    
    # Build report
    total_delta = total_mrr - sum(last_month_mrr.values())
    sign = "+" if total_delta >= 0 else ""
    
    lines = [
        f"# Monthly Review — {MONTH_LABEL}",
        f"*Generated: {TODAY}*",
        "",
        "## 💰 MRR Summary",
        f"- **Total MRR:** ${total_mrr:.2f} ({sign}${total_delta:.2f} vs last month)",
        f"- **Active Subscriptions:** {total_subs}",
        "",
        "## 🏆 Products Ranked by MRR",
    ]
    
    if ranked:
        for i, (prod, mrr_val) in enumerate(ranked, 1):
            last_val = last_month_mrr.get(prod, 0)
            delta = mrr_val - last_val
            sign2 = "+" if delta >= 0 else ""
            subs = subs_by_product.get(prod, 0)
            lines.append(f"{i}. **{prod}** — ${mrr_val:.2f}/mo ({subs} subs, {sign2}${delta:.2f} MoM)")
    else:
        lines.append("- No active subscriptions found")
    
    lines += ["", "## 📈 Promote List (showing traction)"]
    if promote_list:
        for prod, mrr_val, last_val in promote_list:
            growth_pct = ((mrr_val - last_val) / last_val * 100) if last_val > 0 else 100
            lines.append(f"- **{prod}**: ${mrr_val:.2f}/mo (+{growth_pct:.0f}% MoM) → 🚀 increase marketing")
    else:
        lines.append("- No standout growers this month")
    
    lines += ["", "## 💀 Kill List ($0 MRR — review/kill)"]
    if kill_list:
        for k in kill_list:
            lines.append(f"- ⚠️ {k}")
    else:
        lines.append("- None — all products showing some revenue")
    
    lines += [
        "",
        "## 📊 MRR History",
    ]
    for month, prods in sorted(history.items(), reverse=True)[:6]:
        month_total = sum(prods.values())
        lines.append(f"- {month}: ${month_total:.2f}")
    
    report = "\n".join(lines)
    
    # Save
    out_path = OUTPUT_DIR / f"{MONTH_LABEL}.md"
    out_path.write_text(report)
    print(f"Saved: {out_path}")
    
    # Telegram
    tg_msg = f"📋 *Monthly Review — {MONTH_LABEL}*\n\n"
    tg_msg += f"💰 Total MRR: *${total_mrr:.2f}* ({sign}${total_delta:.2f} MoM)\n"
    tg_msg += f"👥 Active subs: {total_subs}\n\n"
    
    if ranked[:3]:
        tg_msg += "*Top products:*\n"
        for i, (prod, mrr_val) in enumerate(ranked[:3], 1):
            tg_msg += f"{i}. {prod}: ${mrr_val:.2f}/mo\n"
    
    if kill_list:
        tg_msg += f"\n💀 *Kill list ({len(kill_list)} products):*\n"
        for k in kill_list[:3]:
            tg_msg += f"• {k}\n"
    
    if promote_list:
        tg_msg += f"\n🚀 *Promote ({len(promote_list)} products showing traction):*\n"
        for prod, mrr_val, _ in promote_list[:3]:
            tg_msg += f"• {prod}: ${mrr_val:.2f}/mo\n"
    
    tg_msg += f"\n📄 Full: reviews/monthly/{MONTH_LABEL}.md"
    
    tg(tg_msg)
    print("Telegram alert sent.")

if __name__ == "__main__":
    main()
