#!/usr/bin/env python3
"""
Daily Review — runs every day at 21:00 UTC (11pm Namibia)
Pulls: Stripe MRR, Zoho email replies, Vapi calls, GitHub issues
Sends summary to Wolfgang Telegram
Saves to /reviews/daily/YYYY-MM-DD.md
"""

import json, os, datetime, requests, imaplib, email
from email.header import decode_header
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────────────
WORKSPACE = Path("/root/.openclaw/workspace")
STRIPE_KEY = "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"
BOT_TOKEN  = json.load(open("/root/.openclaw/openclaw.json"))["channels"]["telegram"]["botToken"]
CHAT_ID    = "8654703697"
QUOTA_FILE = WORKSPACE / "quotas/quota-state.json"
STATE_FILE = WORKSPACE / "assets/heartbeat-state.json"
TODAY      = datetime.date.today()
OUTPUT_DIR = WORKSPACE / "reviews/daily"

# ─── Helpers ──────────────────────────────────────────────────────────────────
def tg(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"},
            timeout=10
        )
    except Exception as e:
        print(f"Telegram error: {e}")

def stripe_mrr():
    """Pull current MRR from Stripe active subscriptions."""
    try:
        r = requests.get(
            "https://api.stripe.com/v1/subscriptions",
            params={"limit": 100, "status": "active"},
            auth=(STRIPE_KEY, ""),
            timeout=15
        )
        data = r.json()
        subs = data.get("data", [])
        mrr = 0.0
        product_mrr = {}
        for s in subs:
            for item in s.get("items", {}).get("data", []):
                plan = item.get("plan", {})
                amount = plan.get("amount", 0) / 100
                interval = plan.get("interval", "month")
                if interval == "year":
                    amount = amount / 12
                mrr += amount
                prod = plan.get("product", "unknown")
                product_mrr[prod] = product_mrr.get(prod, 0) + amount
        return round(mrr, 2), len(subs), product_mrr
    except Exception as e:
        return None, None, {}

def zoho_email_replies(limit=50):
    """Count email replies via Zoho IMAP."""
    try:
        creds_file = WORKSPACE / "credentials/zoho-creds.json"
        if not creds_file.exists():
            return [], "No Zoho creds file found"
        creds = json.loads(creds_file.read_text())
        mail = imaplib.IMAP4_SSL("imap.zoho.com", 993)
        mail.login(creds["email"], creds["password"])
        mail.select("INBOX")
        # Search for today's emails
        date_str = TODAY.strftime("%d-%b-%Y")
        _, ids = mail.search(None, f'(SINCE {date_str})')
        reply_count = 0
        replies = []
        for num in ids[0].split()[-limit:]:
            _, msg_data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            subject = decode_header(msg["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode(errors="replace")
            sender = msg.get("From", "")
            if "re:" in subject.lower():
                reply_count += 1
                replies.append({"from": sender, "subject": subject})
        mail.logout()
        return replies, None
    except Exception as e:
        return [], str(e)

def vapi_call_results():
    """Load today's Vapi call results from local log."""
    try:
        results_file = WORKSPACE / "assets/call-results-live.json"
        if not results_file.exists():
            return [], 0, 0
        data = json.loads(results_file.read_text())
        today_str = str(TODAY)
        today_calls = [c for c in data if c.get("date", "")[:10] == today_str]
        warm = [c for c in today_calls if c.get("outcome") in ("warm", "interested", "callback")]
        return today_calls, len(today_calls), len(warm)
    except Exception as e:
        return [], 0, 0

def github_issues():
    """Check GitHub for new issues today."""
    try:
        headers = {}
        token_file = WORKSPACE / "credentials/github-token.txt"
        if token_file.exists():
            headers["Authorization"] = f"token {token_file.read_text().strip()}"
        # Check known repos
        repos = ["bummerland17/pantrymate-ai", "bummerland17/unitfix"]
        issues_today = []
        for repo in repos:
            r = requests.get(
                f"https://api.github.com/repos/{repo}/issues",
                params={"state": "open", "sort": "created", "per_page": 10},
                headers=headers, timeout=10
            )
            if r.status_code == 200:
                for iss in r.json():
                    created = iss.get("created_at", "")[:10]
                    if created == str(TODAY):
                        issues_today.append({"repo": repo, "title": iss["title"], "number": iss["number"]})
        return issues_today
    except Exception as e:
        return []

def load_quota_state():
    if QUOTA_FILE.exists():
        return json.loads(QUOTA_FILE.read_text())
    return {}

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    print(f"[daily-review] Running for {TODAY}")

    # Load previous MRR from state
    state = {}
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text())
    prev_mrr = state.get("stripe", {}).get("lastKnownMRR", 0)
    prev_subs = state.get("stripe", {}).get("lastKnownSubCount", 0)

    # Pull all data
    mrr, sub_count, product_mrr = stripe_mrr()
    email_replies, email_err = zoho_email_replies()
    all_calls, call_count, warm_count = vapi_call_results()
    new_issues = github_issues()
    quota_state = load_quota_state()

    # MRR delta
    mrr_str = f"${mrr:.2f}" if mrr is not None else "N/A"
    mrr_delta = ""
    if mrr is not None and prev_mrr:
        delta = mrr - prev_mrr
        sign = "+" if delta >= 0 else ""
        mrr_delta = f" ({sign}${delta:.2f} vs yesterday)"

    # Quota flags
    quota_flags = []
    quotas = quota_state.get("today", {})
    targets = {"apps_built": 1, "outreach_emails": 10, "social_posts": 5, "cold_calls": 10, "content_pieces": 3}
    for k, target in targets.items():
        actual = quotas.get(k, 0)
        if actual < target:
            quota_flags.append(f"⚠️ {k.replace('_',' ').title()}: {actual}/{target}")

    # Build review
    wins = []
    blockers = []

    if mrr is not None and mrr > prev_mrr:
        wins.append(f"MRR grew to {mrr_str} 🎉")
    if warm_count > 0:
        wins.append(f"{warm_count} warm Vapi leads today")
    if len(email_replies) > 0:
        wins.append(f"{len(email_replies)} email replies received")

    if email_err:
        blockers.append(f"Zoho IMAP error: {email_err}")
    if quota_flags:
        blockers.extend(quota_flags)

    # Format report
    lines = [
        f"# Daily Review — {TODAY}",
        "",
        "## 📊 Numbers",
        f"- **MRR:** {mrr_str}{mrr_delta}",
        f"- **Active Subs:** {sub_count if sub_count is not None else 'N/A'}",
        f"- **Vapi Calls Today:** {call_count} ({warm_count} warm)",
        f"- **Email Replies:** {len(email_replies)}",
        f"- **New GitHub Issues:** {len(new_issues)}",
        "",
        "## 🏆 Wins",
    ]
    lines += [f"- {w}" for w in wins] if wins else ["- None logged today"]
    lines += ["", "## 🚧 Blockers"]
    lines += [f"- {b}" for b in blockers] if blockers else ["- None"]

    if email_replies:
        lines += ["", "## 📬 Email Replies"]
        for r in email_replies[:5]:
            lines.append(f"- **{r['from']}**: {r['subject']}")

    if new_issues:
        lines += ["", "## 🐛 New GitHub Issues"]
        for iss in new_issues:
            lines.append(f"- [{iss['repo']} #{iss['number']}] {iss['title']}")

    if quota_flags:
        lines += ["", "## ⚠️ Quota Misses"]
        lines += [f"- {f}" for f in quota_flags]

    # Product MRR breakdown
    if product_mrr:
        lines += ["", "## 💰 MRR by Product"]
        for prod, amt in sorted(product_mrr.items(), key=lambda x: -x[1]):
            lines.append(f"- {prod}: ${amt:.2f}/mo")

    report = "\n".join(lines)

    # Save to file
    out_path = OUTPUT_DIR / f"{TODAY}.md"
    out_path.write_text(report)
    print(f"Saved: {out_path}")

    # Send Telegram summary
    tg_msg = f"📋 *Daily Review — {TODAY}*\n\n"
    tg_msg += f"💰 MRR: *{mrr_str}*{mrr_delta}\n"
    tg_msg += f"📞 Calls: {call_count} ({warm_count} warm)\n"
    tg_msg += f"📬 Email replies: {len(email_replies)}\n"
    tg_msg += f"🐛 New issues: {len(new_issues)}\n"
    if wins:
        tg_msg += f"\n🏆 *Wins:*\n" + "\n".join(f"• {w}" for w in wins) + "\n"
    if blockers:
        tg_msg += f"\n🚧 *Blockers:*\n" + "\n".join(f"• {b}" for b in blockers[:5]) + "\n"
    tg_msg += f"\n📄 Full report: reviews/daily/{TODAY}.md"

    tg(tg_msg)
    print("Telegram alert sent.")

    # Update state
    if mrr is not None:
        state.setdefault("stripe", {})
        state["stripe"]["lastKnownMRR"] = mrr
        state["stripe"]["lastKnownSubCount"] = sub_count
        STATE_FILE.write_text(json.dumps(state, indent=2))

if __name__ == "__main__":
    main()
