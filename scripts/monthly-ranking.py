#!/usr/bin/env python3
"""
Monthly Product Ranking — runs 1st of each month at 00:00 UTC
Ranks all products by MRR, growth rate, engagement signals
Flags top performers for more marketing, bottom performers for review/kill
"""

import json, datetime, re, requests
from pathlib import Path
from collections import defaultdict

WORKSPACE   = Path("/root/.openclaw/workspace")
STRIPE_KEY  = "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"
BOT_TOKEN   = json.load(open("/root/.openclaw/openclaw.json"))["channels"]["telegram"]["botToken"]
CHAT_ID     = "8654703697"
TODAY       = datetime.date.today()
OUTPUT_DIR  = WORKSPACE / "reviews/monthly"
DAILY_DIR   = WORKSPACE / "reviews/daily"
MRR_HISTORY = WORKSPACE / "assets/monthly-mrr-history.json"
PRODUCTS_F  = WORKSPACE / "assets/products.json"
RANKING_F   = WORKSPACE / "assets/product-rankings.json"

def tg(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"},
            timeout=10
        )
    except Exception as e:
        print(f"Telegram error: {e}")

def get_stripe_mrr_by_product():
    """Pull MRR broken down by product from Stripe."""
    try:
        r = requests.get(
            "https://api.stripe.com/v1/subscriptions",
            params={"limit": 100, "status": "active"},
            auth=(STRIPE_KEY, ""),
            timeout=15
        )
        prod_r = requests.get(
            "https://api.stripe.com/v1/products",
            params={"limit": 100},
            auth=(STRIPE_KEY, ""),
            timeout=15
        )
        products = {p["id"]: p["name"] for p in prod_r.json().get("data", [])}
        
        mrr = defaultdict(float)
        subs_count = defaultdict(int)
        
        for s in r.json().get("data", []):
            created = s.get("created", 0)
            for item in s.get("items", {}).get("data", []):
                plan = item.get("plan", {})
                amount = plan.get("amount", 0) / 100
                interval = plan.get("interval", "month")
                if interval == "year":
                    amount /= 12
                prod_id = plan.get("product", "unknown")
                prod_name = products.get(prod_id, prod_id)
                mrr[prod_name] += amount
                subs_count[prod_name] += 1
        
        return dict(mrr), dict(subs_count)
    except Exception as e:
        print(f"Stripe error: {e}")
        return {}, {}

def get_engagement_signals():
    """
    Load engagement data: email replies, demo clicks from daily reviews.
    Returns dict of product -> signal count.
    """
    signals = defaultdict(int)
    
    # Check last 30 days of daily reviews
    for i in range(30):
        day = TODAY - datetime.timedelta(days=i)
        path = DAILY_DIR / f"{day}.md"
        if path.exists():
            text = path.read_text()
            # Extract email replies from review
            m = re.search(r"Email Replies:\s*(\d+)", text)
            if m and int(m.group(1)) > 0:
                signals["email_outreach"] += int(m.group(1))
            # Extract warm Vapi leads
            m = re.search(r"\((\d+) warm\)", text)
            if m:
                signals["vapi_calls"] += int(m.group(1))
    
    # Load from known warm leads file
    warm_leads_file = WORKSPACE / "assets/warm-leads.json"
    if warm_leads_file.exists():
        try:
            leads = json.loads(warm_leads_file.read_text())
            for lead in leads:
                product = lead.get("product", "unknown")
                signals[product] += 1
        except Exception:
            pass
    
    return dict(signals)

def get_mrr_history():
    """Load historical MRR data for growth rate calculation."""
    if MRR_HISTORY.exists():
        return json.loads(MRR_HISTORY.read_text())
    return {}

def calculate_growth_rate(product, current_mrr, history):
    """Calculate MoM growth rate for a product."""
    months = sorted(history.keys())[-2:]
    if len(months) < 2:
        return 0.0
    
    prev_month = months[0]
    prev_data = history.get(prev_month, {})
    prev_mrr = prev_data.get(product, 0)
    
    if prev_mrr == 0:
        return 100.0 if current_mrr > 0 else 0.0
    
    return round(((current_mrr - prev_mrr) / prev_mrr) * 100, 1)

def rank_products(mrr_by_product, subs_count, engagement, history):
    """
    Rank products on 3 dimensions:
    1. MRR (0-40 points)
    2. Growth rate (0-35 points)
    3. Engagement (0-25 points)
    """
    all_products = set(mrr_by_product.keys())
    
    # Load known products (may include $0 ones)
    if PRODUCTS_F.exists():
        known = json.loads(PRODUCTS_F.read_text())
        for p in known:
            all_products.add(p.get("name", ""))
    
    max_mrr = max(mrr_by_product.values()) if mrr_by_product else 1
    max_eng = max(engagement.values()) if engagement else 1
    
    ranked = []
    for prod in all_products:
        if not prod:
            continue
        mrr = mrr_by_product.get(prod, 0)
        subs = subs_count.get(prod, 0)
        growth = calculate_growth_rate(prod, mrr, history)
        eng = max(engagement.get(prod, 0), engagement.get("email_outreach", 0) // max(len(all_products), 1))
        
        # Score (0-100)
        mrr_score = (mrr / max_mrr) * 40 if max_mrr > 0 else 0
        growth_score = min(max(growth, 0), 100) / 100 * 35
        eng_score = (eng / max_eng) * 25 if max_eng > 0 else 0
        total_score = round(mrr_score + growth_score + eng_score, 1)
        
        # Days since launch
        days_live = None
        if PRODUCTS_F.exists():
            known = json.loads(PRODUCTS_F.read_text())
            for p in known:
                if p.get("name") == prod and p.get("launched"):
                    days_live = (TODAY - datetime.date.fromisoformat(p["launched"])).days
        
        ranked.append({
            "name": prod,
            "mrr": round(mrr, 2),
            "subs": subs,
            "growth_rate": growth,
            "engagement": eng,
            "score": total_score,
            "days_live": days_live,
        })
    
    ranked.sort(key=lambda x: -x["score"])
    return ranked

def determine_actions(ranked):
    """Assign actions based on ranking."""
    actions = {}
    total = len(ranked)
    
    for i, prod in enumerate(ranked):
        rank_pct = (i / total) if total > 0 else 0
        
        if prod["mrr"] == 0 and (prod["days_live"] or 0) >= 60:
            actions[prod["name"]] = {
                "action": "KILL",
                "reason": f"$0 MRR after {prod['days_live']} days",
                "icon": "💀"
            }
        elif rank_pct < 0.33:  # Top third
            actions[prod["name"]] = {
                "action": "INVEST",
                "reason": f"Top performer — score {prod['score']}, MRR ${prod['mrr']:.2f}",
                "icon": "🚀",
                "recommendations": [
                    "Increase social post frequency (target 2x)",
                    "Double outreach volume for this product",
                    "Consider paid ads if ROAS > 3x"
                ]
            }
        elif rank_pct < 0.66:  # Middle third
            actions[prod["name"]] = {
                "action": "MAINTAIN",
                "reason": "Steady — keep current marketing level",
                "icon": "🔄"
            }
        else:  # Bottom third
            if prod["mrr"] == 0 and (prod["days_live"] or 0) >= 30:
                actions[prod["name"]] = {
                    "action": "REVIEW",
                    "reason": f"$0 MRR, {prod['days_live'] or '?'} days live — needs attention",
                    "icon": "⚠️"
                }
            else:
                actions[prod["name"]] = {
                    "action": "IMPROVE",
                    "reason": "Low ranking — review messaging, pricing, channels",
                    "icon": "🔧"
                }
    
    return actions

def main():
    print(f"[monthly-ranking] Running for {TODAY}")
    
    mrr, subs = get_stripe_mrr_by_product()
    engagement = get_engagement_signals()
    history = get_mrr_history()
    ranked = rank_products(mrr, subs, engagement, history)
    actions = determine_actions(ranked)
    
    # Build report
    label = TODAY.strftime("%Y-%m")
    lines = [
        f"# Product Rankings — {label}",
        f"*Generated: {TODAY} | {len(ranked)} products tracked*",
        "",
        "## 🏆 Full Rankings",
        "",
        "| Rank | Product | MRR | Growth | Score | Action |",
        "|------|---------|-----|--------|-------|--------|",
    ]
    
    for i, p in enumerate(ranked, 1):
        growth_str = f"+{p['growth_rate']}%" if p['growth_rate'] >= 0 else f"{p['growth_rate']}%"
        action = actions.get(p["name"], {})
        lines.append(
            f"| {i} | {p['name']} | ${p['mrr']:.2f} | {growth_str} | {p['score']} | {action.get('icon', '')} {action.get('action', '?')} |"
        )
    
    lines += ["", "## 📋 Action Plan"]
    
    invest = [p for p in ranked if actions.get(p["name"], {}).get("action") == "INVEST"]
    kill   = [p for p in ranked if actions.get(p["name"], {}).get("action") == "KILL"]
    review = [p for p in ranked if actions.get(p["name"], {}).get("action") == "REVIEW"]
    
    lines += ["", "### 🚀 Invest More (Top Performers)"]
    for p in invest:
        a = actions[p["name"]]
        lines.append(f"**{p['name']}** — {a['reason']}")
        for rec in a.get("recommendations", []):
            lines.append(f"  - {rec}")
    if not invest:
        lines.append("- None in top tier yet")
    
    lines += ["", "### ⚠️ Review (Need Attention)"]
    for p in review:
        a = actions[p["name"]]
        lines.append(f"- **{p['name']}** — {a['reason']}")
    if not review:
        lines.append("- None")
    
    lines += ["", "### 💀 Kill List ($0 MRR 60+ days)"]
    for p in kill:
        a = actions[p["name"]]
        lines.append(f"- **{p['name']}** — {a['reason']}")
    if not kill:
        lines.append("- None — all products have some revenue")
    
    report = "\n".join(lines)
    
    # Save ranking
    out_path = OUTPUT_DIR / f"ranking-{label}.md"
    out_path.write_text(report)
    print(f"Saved: {out_path}")
    
    # Save JSON state
    RANKING_F.write_text(json.dumps({
        "date": str(TODAY),
        "rankings": ranked,
        "actions": actions
    }, indent=2))
    
    # Telegram
    tg_msg = f"🏆 *Monthly Rankings — {label}*\n\n"
    if ranked:
        tg_msg += "*Top 5 products:*\n"
        for i, p in enumerate(ranked[:5], 1):
            a = actions.get(p["name"], {})
            tg_msg += f"{i}. {a.get('icon','')} *{p['name']}* — ${p['mrr']:.2f}/mo (score: {p['score']})\n"
    
    if invest:
        tg_msg += f"\n🚀 *Invest more in ({len(invest)}):* {', '.join(p['name'] for p in invest)}\n"
    if kill:
        tg_msg += f"\n💀 *Kill list ({len(kill)}):* {', '.join(p['name'] for p in kill)}\n"
    if review:
        tg_msg += f"\n⚠️ *Review needed ({len(review)}):* {', '.join(p['name'] for p in review)}\n"
    
    tg_msg += f"\n📄 Full: reviews/monthly/ranking-{label}.md"
    tg(tg_msg)
    print("Telegram alert sent.")

if __name__ == "__main__":
    main()
