#!/usr/bin/env python3
"""
Tools Radar — runs every Monday at 09:00 UTC
Searches Brave for new AI tools, scores them, alerts if 8+
Logs all finds to research/tools-radar-log.md
"""

import json, datetime, requests
from pathlib import Path

WORKSPACE    = Path("/root/.openclaw/workspace")
BRAVE_KEY    = "BSA106jyrhl-5L1J4pkHQrw8H0BcesL"
BOT_TOKEN    = json.load(open("/root/.openclaw/openclaw.json"))["channels"]["telegram"]["botToken"]
CHAT_ID      = "8654703697"
TODAY        = datetime.date.today()
LOG_FILE     = WORKSPACE / "research/tools-radar-log.md"
SEARCH_QUERIES = [
    "new AI tools 2026",
    "best AI automation tools for entrepreneurs 2026",
    "openclaw new skills site:clawhub.com",
    "AI productivity tools indie hacker 2026",
    "no-code AI tools launch 2026",
]

def tg(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"},
            timeout=10
        )
    except Exception as e:
        print(f"Telegram error: {e}")

def brave_search(query, count=10):
    """Search Brave API and return results."""
    try:
        r = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": query, "count": count, "freshness": "pw"},  # past week
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": BRAVE_KEY
            },
            timeout=15
        )
        if r.status_code == 200:
            results = r.json().get("web", {}).get("results", [])
            return results
        else:
            print(f"Brave search error {r.status_code}: {r.text[:200]}")
            return []
    except Exception as e:
        print(f"Brave search exception: {e}")
        return []

def score_tool(title, description, url):
    """
    Score a tool on relevance (1-10) and additive value (1-10).
    Returns total score and reasoning.
    """
    text = f"{title} {description} {url}".lower()
    
    # Relevance scoring
    relevance = 3  # base
    if any(kw in text for kw in ["ai", "automation", "gpt", "llm", "openai", "claude"]):
        relevance += 2
    if any(kw in text for kw in ["business", "revenue", "mrr", "saas", "startup"]):
        relevance += 2
    if any(kw in text for kw in ["no-code", "nocode", "workflow", "agent", "bot"]):
        relevance += 2
    if "openclaw" in text or "clawhub" in text:
        relevance += 3  # high relevance
    relevance = min(relevance, 10)
    
    # Additive value scoring
    additive = 3  # base
    if any(kw in text for kw in ["free", "open source", "api", "webhook"]):
        additive += 2
    if any(kw in text for kw in ["outreach", "email", "cold call", "lead"]):
        additive += 2
    if any(kw in text for kw in ["stripe", "payment", "monetize"]):
        additive += 2
    if any(kw in text for kw in ["telegram", "slack", "discord", "notification"]):
        additive += 1
    additive = min(additive, 10)
    
    total = (relevance + additive) / 2
    
    # Cost estimate
    cost = "unknown"
    if any(kw in text for kw in ["free", "open source"]):
        cost = "$0"
    elif any(kw in text for kw in ["$9", "$10", "$15", "$19", "$20", "$29"]):
        cost = "< $30/mo"
    elif any(kw in text for kw in ["$49", "$50", "$99", "$100"]):
        cost = "$50-100/mo"
    elif "enterprise" in text or "custom pricing" in text:
        cost = "Enterprise"
    
    return relevance, additive, round(total, 1), cost

def deduplicate_results(results):
    """Remove duplicate URLs/titles from combined results."""
    seen_urls = set()
    seen_titles = set()
    unique = []
    for r in results:
        url = r.get("url", "")
        title = r.get("title", "")[:50]
        if url not in seen_urls and title not in seen_titles:
            seen_urls.add(url)
            seen_titles.add(title)
            unique.append(r)
    return unique

def main():
    print(f"[tools-radar] Running for {TODAY}")
    
    all_results = []
    for q in SEARCH_QUERIES:
        print(f"  Searching: {q}")
        results = brave_search(q)
        all_results.extend(results)
    
    # Deduplicate
    unique_results = deduplicate_results(all_results)
    print(f"  Found {len(unique_results)} unique results")
    
    # Score each
    scored_tools = []
    for r in unique_results:
        title = r.get("title", "Untitled")
        description = r.get("description", "")
        url = r.get("url", "")
        relevance, additive, score, cost = score_tool(title, description, url)
        scored_tools.append({
            "title": title,
            "url": url,
            "description": description[:200],
            "relevance": relevance,
            "additive": additive,
            "score": score,
            "cost": cost,
        })
    
    # Sort by score
    scored_tools.sort(key=lambda x: -x["score"])
    
    # Immediate alert for 8+ scored tools
    high_value = [t for t in scored_tools if t["score"] >= 8.0]
    if high_value:
        msg = f"🛠 *Tools Radar Alert — {TODAY}*\n\n"
        msg += f"🔥 *{len(high_value)} high-value tool(s) found (score 8+):*\n\n"
        for t in high_value[:5]:
            msg += f"*{t['title']}*\n"
            msg += f"Score: {t['score']}/10 (R:{t['relevance']} A:{t['additive']}) | Cost: {t['cost']}\n"
            msg += f"{t['url']}\n"
            if t['description']:
                msg += f"_{t['description'][:100]}..._\n"
            msg += "\n"
        tg(msg)
        print(f"  🔥 Alerted Wolfgang: {len(high_value)} high-value tools")
    else:
        print(f"  No tools scored 8+ this week")
    
    # Build log entry
    log_lines = [
        f"\n## Tools Radar — {TODAY}",
        f"*Queries: {len(SEARCH_QUERIES)} | Results: {len(unique_results)} | High-value (8+): {len(high_value)}*",
        "",
    ]
    
    for t in scored_tools[:20]:  # Log top 20
        stars = "⭐" * int(t["score"])
        log_lines.append(f"### {t['title']}")
        log_lines.append(f"- **Score:** {t['score']}/10 (Relevance: {t['relevance']}, Additive: {t['additive']}) {stars}")
        log_lines.append(f"- **Cost:** {t['cost']}")
        log_lines.append(f"- **URL:** {t['url']}")
        if t['description']:
            log_lines.append(f"- **About:** {t['description'][:150]}")
        log_lines.append("")
    
    # Append to log file
    log_entry = "\n".join(log_lines)
    existing = LOG_FILE.read_text() if LOG_FILE.exists() else "# Tools Radar Log\n\n"
    LOG_FILE.write_text(existing + log_entry)
    print(f"  Logged to: {LOG_FILE}")
    
    # Weekly summary Telegram (even if no 8+ tools)
    if not high_value:
        top3 = scored_tools[:3]
        if top3:
            summary_msg = f"🔭 *Tools Radar — {TODAY}*\n\n"
            summary_msg += f"Scanned {len(unique_results)} results — no 8+ scores this week.\n\n"
            summary_msg += "*Top 3 finds:*\n"
            for t in top3:
                summary_msg += f"• *{t['title']}* — Score: {t['score']}/10 | {t['url']}\n"
            tg(summary_msg)
    
    print(f"[tools-radar] Done. {len(scored_tools)} tools scored, {len(high_value)} high-value.")

if __name__ == "__main__":
    main()
