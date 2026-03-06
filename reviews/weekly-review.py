#!/usr/bin/env python3
"""
Weekly Review — runs every Sunday at 18:00 UTC
Aggregates 7 daily reviews, MRR WoW change, best channel, new tools, priorities
Sends to Wolfgang Telegram + saves to /reviews/weekly/YYYY-WXX.md
"""

import json, os, datetime, re, requests, glob
from pathlib import Path

WORKSPACE  = Path("/root/.openclaw/workspace")
BOT_TOKEN  = json.load(open("/root/.openclaw/openclaw.json"))["channels"]["telegram"]["botToken"]
CHAT_ID    = "8654703697"
TODAY      = datetime.date.today()
WEEK_NUM   = TODAY.isocalendar()[1]
YEAR       = TODAY.year
OUTPUT_DIR = WORKSPACE / "reviews/weekly"
DAILY_DIR  = WORKSPACE / "reviews/daily"
RADAR_LOG  = WORKSPACE / "research/tools-radar-log.md"

def tg(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"},
            timeout=10
        )
    except Exception as e:
        print(f"Telegram error: {e}")

def parse_daily_review(path):
    """Extract key numbers from a daily review markdown file."""
    text = Path(path).read_text()
    data = {"date": Path(path).stem}
    
    # MRR
    m = re.search(r"\*\*MRR:\*\*\s*\$?([\d.]+)", text)
    if m: data["mrr"] = float(m.group(1))
    
    # Calls
    m = re.search(r"Vapi Calls Today:\s*(\d+)\s*\((\d+) warm\)", text)
    if m:
        data["calls"] = int(m.group(1))
        data["warm"] = int(m.group(2))
    
    # Email replies
    m = re.search(r"Email Replies:\s*(\d+)", text)
    if m: data["email_replies"] = int(m.group(1))
    
    # Wins / blockers count
    data["has_wins"] = "None logged" not in text and "## 🏆 Wins" in text
    
    return data

def get_week_daily_reviews():
    """Load all 7 daily reviews for the past week."""
    reviews = []
    for i in range(7):
        day = TODAY - datetime.timedelta(days=i)
        path = DAILY_DIR / f"{day}.md"
        if path.exists():
            reviews.append(parse_daily_review(path))
    return reviews

def get_new_tools_this_week():
    """Parse tools-radar-log.md for this week's entries."""
    if not RADAR_LOG.exists():
        return []
    text = RADAR_LOG.read_text()
    # Find entries from past 7 days
    tools = []
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if "Score:" in line:
            # grab context
            tool_block = " ".join(lines[max(0,i-2):i+3])
            tools.append(tool_block.strip())
    return tools[:5]

def get_top_priorities():
    """Load from a priorities file if it exists, else return defaults."""
    prio_file = WORKSPACE / "assets/priorities.json"
    if prio_file.exists():
        data = json.loads(prio_file.read_text())
        return data.get("weekly_top3", [])
    return [
        "Keep MRR momentum — send 10 outreach emails daily",
        "Ship 1 new product or feature this week",
        "Research 3 new AI tools and evaluate fit"
    ]

def main():
    print(f"[weekly-review] Running for week {YEAR}-W{WEEK_NUM:02d}")
    
    reviews = get_week_daily_reviews()
    new_tools = get_new_tools_this_week()
    priorities = get_top_priorities()
    
    # Aggregate numbers
    total_calls   = sum(r.get("calls", 0) for r in reviews)
    total_warm    = sum(r.get("warm", 0) for r in reviews)
    total_replies = sum(r.get("email_replies", 0) for r in reviews)
    mrr_values    = [r["mrr"] for r in reviews if "mrr" in r]
    
    start_mrr = mrr_values[-1] if mrr_values else 0
    end_mrr   = mrr_values[0] if mrr_values else 0
    mrr_delta = end_mrr - start_mrr
    
    # Best channel
    best_channel = "Unknown"
    if total_replies > total_warm:
        best_channel = f"Email outreach ({total_replies} replies)"
    elif total_warm > 0:
        best_channel = f"Vapi cold calls ({total_warm} warm leads)"
    else:
        best_channel = "No clear winner — need more data"
    
    # Build report
    sign = "+" if mrr_delta >= 0 else ""
    lines = [
        f"# Weekly Review — {YEAR}-W{WEEK_NUM:02d}",
        f"*{TODAY - datetime.timedelta(days=6)} → {TODAY}*",
        "",
        "## 📊 Weekly Numbers",
        f"- **MRR Start:** ${start_mrr:.2f}",
        f"- **MRR End:** ${end_mrr:.2f} ({sign}${mrr_delta:.2f} WoW)",
        f"- **Total Vapi Calls:** {total_calls} ({total_warm} warm)",
        f"- **Total Email Replies:** {total_replies}",
        f"- **Daily Reviews Captured:** {len(reviews)}/7",
        "",
        "## 🏆 Best Performing Channel",
        f"- {best_channel}",
        "",
        "## 🛠 New Tools Discovered This Week",
    ]
    
    if new_tools:
        for t in new_tools:
            lines.append(f"- {t}")
    else:
        lines.append("- None logged — run tools-radar.py to research")
    
    lines += [
        "",
        "## 🎯 Top 3 Priorities Next Week",
    ]
    for i, p in enumerate(priorities, 1):
        lines.append(f"{i}. {p}")
    
    lines += [
        "",
        "## 📅 Daily Breakdown",
    ]
    for r in reversed(reviews):
        mrr_str = f"${r['mrr']:.2f}" if "mrr" in r else "N/A"
        calls = r.get("calls", 0)
        warm = r.get("warm", 0)
        replies = r.get("email_replies", 0)
        lines.append(f"- **{r['date']}**: MRR={mrr_str}, Calls={calls} ({warm} warm), Emails={replies}")
    
    report = "\n".join(lines)
    
    # Save
    out_path = OUTPUT_DIR / f"{YEAR}-W{WEEK_NUM:02d}.md"
    out_path.write_text(report)
    print(f"Saved: {out_path}")
    
    # Telegram
    sign_emoji = "📈" if mrr_delta >= 0 else "📉"
    tg_msg = f"📋 *Weekly Review — {YEAR}-W{WEEK_NUM:02d}*\n\n"
    tg_msg += f"{sign_emoji} MRR: *${end_mrr:.2f}* ({sign}${mrr_delta:.2f} WoW)\n"
    tg_msg += f"📞 Calls: {total_calls} ({total_warm} warm)\n"
    tg_msg += f"📬 Email replies: {total_replies}\n"
    tg_msg += f"🏅 Best channel: {best_channel}\n"
    if new_tools:
        tg_msg += f"\n🛠 New tools: {len(new_tools)} found this week\n"
    tg_msg += f"\n🎯 *Next week priorities:*\n"
    for i, p in enumerate(priorities, 1):
        tg_msg += f"{i}. {p}\n"
    tg_msg += f"\n📄 Full report: reviews/weekly/{YEAR}-W{WEEK_NUM:02d}.md"
    
    tg(tg_msg)
    print("Telegram alert sent.")

if __name__ == "__main__":
    main()
