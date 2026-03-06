#!/usr/bin/env python3
"""
Business Factory — Scanner
Runs weekly (Sundays). Finds autonomous business opportunities from Reddit pain points,
validates demand via Brave Search, scores them, and saves top picks to opportunities.json.

Usage: python3 scanner.py
"""

import json
import time
import datetime
import urllib.request
import urllib.parse
import urllib.error
import re
import os
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
BRAVE_API_KEY = "BSA106jyrhl-5L1J4pkHQrw8H0BcesL"
OUTPUT_FILE   = Path(__file__).parent / "opportunities.json"
LOG_FILE      = Path(__file__).parent / "scanner.log"

SUBREDDITS = [
    "entrepreneur",
    "smallbusiness",
    "freelance",
    "SideProject",
    "passive_income",
    "indiehackers",
    "startups",
]

PAIN_QUERIES = [
    "I wish there was a tool",
    "does anyone know an app",
    "I just pay for",
    "there's no good way to",
    "I manually",
    "I can't find a good",
    "why is there no",
    "I hate that I have to",
    "looking for a simple way to",
    "anyone else frustrated by",
]

MIN_SCORE = 7          # Must score 7+ on all four dimensions
MAX_DAYS_TO_SALE = 14  # Hard cut: estimated > 14 days → rejected


# ── Helpers ──────────────────────────────────────────────────────────────────

def log(msg: str):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def safe_get(url: str, headers: dict = None, retries: int = 2) -> dict | None:
    """HTTP GET with retry, returns parsed JSON or None."""
    req = urllib.request.Request(url, headers=headers or {})
    req.add_header("User-Agent", "BusinessFactory/1.0 (scanner)")
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                log(f"  Rate limited on {url}, sleeping 30s…")
                time.sleep(30)
            elif attempt < retries:
                time.sleep(2 ** attempt)
            else:
                log(f"  HTTP {e.code} fetching {url}")
        except Exception as e:
            if attempt < retries:
                time.sleep(2 ** attempt)
            else:
                log(f"  Error fetching {url}: {e}")
    return None


# ── Reddit scraping ───────────────────────────────────────────────────────────

def search_reddit(subreddit: str, query: str) -> list[dict]:
    """Search a subreddit via the public JSON API."""
    encoded = urllib.parse.quote(query)
    url = f"https://www.reddit.com/r/{subreddit}/search.json?q={encoded}&restrict_sr=1&sort=relevance&limit=25&t=month"
    data = safe_get(url)
    if not data:
        return []

    posts = []
    try:
        for child in data["data"]["children"]:
            p = child["data"]
            posts.append({
                "title":     p.get("title", ""),
                "selftext":  p.get("selftext", ""),
                "score":     p.get("score", 0),
                "comments":  p.get("num_comments", 0),
                "url":       "https://reddit.com" + p.get("permalink", ""),
                "subreddit": subreddit,
                "query":     query,
            })
    except (KeyError, TypeError):
        pass

    return posts


def collect_reddit_signals() -> list[dict]:
    """Scrape all subreddits × queries, deduplicate by URL."""
    seen_urls = set()
    results = []

    for sub in SUBREDDITS:
        for query in PAIN_QUERIES:
            log(f"  Scanning r/{sub} for '{query}'…")
            posts = search_reddit(sub, query)
            for p in posts:
                if p["url"] not in seen_urls:
                    seen_urls.add(p["url"])
                    results.append(p)
            time.sleep(1.5)  # be polite to Reddit

    log(f"  Total raw signals collected: {len(results)}")
    return results


# ── Brave Search validation ───────────────────────────────────────────────────

def brave_search(query: str) -> list[dict]:
    """Query Brave Search API. Returns list of result snippets."""
    encoded = urllib.parse.quote(query)
    url = f"https://api.search.brave.com/res/v1/web/search?q={encoded}&count=10"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY,
    }
    data = safe_get(url, headers=headers)
    if not data:
        return []
    try:
        return data.get("web", {}).get("results", [])
    except (KeyError, TypeError):
        return []


def check_competition(idea: str) -> dict:
    """
    Returns:
      gap_score: 1–10 (10 = almost no existing solutions)
      competitor_count: int
      notes: str
    """
    results = brave_search(idea)
    count = len(results)

    # Look for paid products in results
    paid_indicators = ["pricing", "plans", "buy now", "subscribe", "per month", "checkout"]
    paid_hits = sum(
        1 for r in results
        if any(kw in (r.get("description", "") + r.get("title", "")).lower() for kw in paid_indicators)
    )

    # Higher competition → lower gap_score
    if paid_hits >= 5:
        gap = 2
        notes = "Market saturated — multiple paid products exist."
    elif paid_hits >= 3:
        gap = 4
        notes = "Some competition, but room for a simpler/cheaper option."
    elif paid_hits >= 1:
        gap = 6
        notes = "Light competition. A focused solution could win on simplicity."
    elif count >= 5:
        gap = 7
        notes = "No obvious paid products. Organic solutions only."
    else:
        gap = 9
        notes = "Virtually no solutions. High gap."

    return {"gap_score": gap, "competitor_count": paid_hits, "notes": notes}


# ── Idea extraction ───────────────────────────────────────────────────────────

def extract_idea(post: dict) -> str | None:
    """
    Very light NLP: pull the most likely 'idea' noun phrase from a Reddit post.
    Returns a short description string or None if nothing useful found.
    """
    text = (post["title"] + " " + post["selftext"])[:800].lower()

    # Common structural patterns
    patterns = [
        r"i wish (?:there was )?(?:a |an )?tool (?:that |to )?([^.!?\n]{10,80})",
        r"looking for (?:a |an )?(?:tool|app|software|way) (?:to |that )?([^.!?\n]{10,80})",
        r"there(?:'s| is) no (?:good )?(?:tool|app|way) to ([^.!?\n]{10,80})",
        r"i manually ([^.!?\n]{10,60})",
        r"does anyone know (?:a |an )?(?:tool|app) (?:that |to )?([^.!?\n]{10,80})",
        r"why is there no ([^.!?\n]{10,80})",
        r"can't find (?:a |an )?(?:good )?(?:tool|app|way) to ([^.!?\n]{10,80})",
    ]

    for pat in patterns:
        m = re.search(pat, text)
        if m:
            idea = m.group(1).strip().rstrip(".,;")
            if len(idea) > 8:
                return idea

    return None


# ── Scoring ───────────────────────────────────────────────────────────────────

def score_opportunity(post: dict, idea: str, competition: dict) -> dict:
    """
    Score on four 1–10 dimensions. Returns dict with scores + composite.
    Also estimates days_to_first_sale — hard reject if > MAX_DAYS_TO_SALE.
    """

    # 1. Demand evidence
    upvotes  = post["score"]
    comments = post["comments"]
    if upvotes >= 500 or comments >= 100:
        demand = 9
    elif upvotes >= 100 or comments >= 30:
        demand = 7
    elif upvotes >= 30 or comments >= 10:
        demand = 5
    elif upvotes >= 10 or comments >= 3:
        demand = 3
    else:
        demand = 1

    # 2. Simplicity (can it be landing page + Stripe?)
    text = (post["title"] + " " + post["selftext"]).lower()
    complex_signals = ["api integration", "machine learning", "real-time", "database", "oauth", "scraping at scale"]
    simple_signals  = ["template", "checklist", "guide", "pdf", "spreadsheet", "notion", "email", "script"]

    simple = 6  # baseline
    if any(s in text for s in simple_signals):
        simple = min(10, simple + 3)
    if any(s in text for s in complex_signals):
        simple = max(1, simple - 3)

    # 3. Autonomous potential
    auto_good = ["template", "pdf", "guide", "checklist", "email", "download", "bundle"]
    auto_bad  = ["custom", "bespoke", "consultation", "hands-on", "service", "managed"]
    auto = 7
    if any(s in text for s in auto_good):
        auto = min(10, auto + 2)
    if any(s in text for s in auto_bad):
        auto = max(1, auto - 3)

    # 4. Revenue ceiling ($500+/mo potential?)
    # Rough heuristic: demand × gap
    ceiling_raw = (demand * competition["gap_score"]) / 10
    if ceiling_raw >= 7:
        ceiling = 9
    elif ceiling_raw >= 5:
        ceiling = 7
    elif ceiling_raw >= 3:
        ceiling = 5
    else:
        ceiling = 3

    # Fast ROI: estimate days to first sale
    # Formula: starts at 7 days, modifiers based on demand + simplicity + price range
    days_to_sale = 7
    if demand >= 7:
        days_to_sale -= 2
    if simple >= 8:
        days_to_sale -= 1
    if competition["gap_score"] >= 7:
        days_to_sale += 2   # high gap = less existing demand to tap
    if demand <= 3:
        days_to_sale += 7
    days_to_sale = max(1, days_to_sale)

    # Community launch plan heuristic
    sub = post.get("subreddit", "")
    community_map = {
        "entrepreneur":    "r/entrepreneur, r/startups",
        "smallbusiness":   "r/smallbusiness, r/entrepreneur",
        "freelance":       "r/freelance, r/forhire",
        "SideProject":     "r/SideProject, r/indiehackers",
        "passive_income":  "r/passive_income, r/SideProject",
        "indiehackers":    "r/indiehackers, IndieHackers.com",
        "startups":        "r/startups, r/entrepreneur",
    }
    community = community_map.get(sub, f"r/{sub}")

    # Composite (min of all four — weakest link matters)
    composite = min(demand, simple, auto, ceiling)
    all_pass   = all(s >= MIN_SCORE for s in [demand, simple, auto, ceiling])
    fast_roi   = days_to_sale <= MAX_DAYS_TO_SALE

    # ── Factory type routing ──────────────────────────────────────────────────
    # Determine which pipeline should handle this opportunity
    text_full = (post["title"] + " " + post["selftext"]).lower()

    course_signals   = ["course", "tutorial", "teach", "learn", "how to", "guide", "training",
                        "workshop", "masterclass", "ebook", "bootcamp"]
    app_signals      = ["app", "saas", "tool", "software", "extension", "plugin", "dashboard",
                        "automate", "integration", "api", "bot"]
    service_signals  = ["consulting", "agency", "freelance", "done-for-you", "managed",
                        "coaching", "retainer", "service", "hire"]
    digital_signals  = ["template", "checklist", "pdf", "spreadsheet", "notion", "bundle",
                        "kit", "pack", "script", "swipe file", "prompt"]

    course_hits  = sum(1 for s in course_signals  if s in text_full)
    app_hits     = sum(1 for s in app_signals      if s in text_full)
    service_hits = sum(1 for s in service_signals  if s in text_full)
    digital_hits = sum(1 for s in digital_signals  if s in text_full)

    hits = {
        "course":         course_hits,
        "app":            app_hits,
        "service":        service_hits,
        "digital_product": digital_hits,
    }
    factory_type = max(hits, key=hits.get)
    # Tie-break: prefer digital_product (fastest to build/sell)
    if list(hits.values()).count(max(hits.values())) > 1:
        for preferred in ["digital_product", "course", "app", "service"]:
            if hits[preferred] == max(hits.values()):
                factory_type = preferred
                break

    return {
        "demand_score":      demand,
        "simplicity_score":  simple,
        "autonomy_score":    auto,
        "ceiling_score":     ceiling,
        "composite_score":   composite,
        "days_to_first_sale": days_to_sale,
        "all_scores_pass":   all_pass,
        "fast_roi_pass":     fast_roi,
        "launch_community":  community,
        "competition":       competition,
        "factory_type":      factory_type,
        "factory_hits":      hits,
    }


# ── Main pipeline ─────────────────────────────────────────────────────────────

def run_scanner():
    log("═" * 60)
    log("Business Factory Scanner — starting run")
    log("═" * 60)

    # 1. Collect Reddit signals
    log("STEP 1: Collecting Reddit signals…")
    posts = collect_reddit_signals()

    # 2. Extract ideas and filter obvious duds
    log("STEP 2: Extracting ideas from posts…")
    candidates = []
    for post in posts:
        idea = extract_idea(post)
        if idea:
            candidates.append((post, idea))

    log(f"  Extracted {len(candidates)} candidate ideas")

    # 3. Validate + score
    log("STEP 3: Validating and scoring opportunities…")
    opportunities = []
    seen_ideas = set()

    for post, idea in candidates:
        # Deduplicate similar ideas
        idea_key = idea[:40].lower()
        if idea_key in seen_ideas:
            continue
        seen_ideas.add(idea_key)

        competition = check_competition(idea + " tool software app")
        scores = score_opportunity(post, idea, competition)

        opp = {
            "id":                 re.sub(r"[^a-z0-9]+", "-", idea[:50].lower()).strip("-"),
            "idea":               idea,
            "source_post":        post["url"],
            "source_subreddit":   post["subreddit"],
            "source_query":       post["query"],
            "post_score":         post["score"],
            "post_comments":      post["comments"],
            "competition_notes":  competition["notes"],
            "competitor_count":   competition["competitor_count"],
            "scores":             scores,
            "qualifies":          scores["all_scores_pass"] and scores["fast_roi_pass"],
            "reject_reason":      (
                "Scores below 7" if not scores["all_scores_pass"]
                else "Days to first sale > 14" if not scores["fast_roi_pass"]
                else None
            ),
            "scanned_at":         datetime.datetime.utcnow().isoformat(),
        }
        opportunities.append(opp)
        time.sleep(0.5)  # be gentle with Brave

    # 4. Sort: qualified first, then by composite score desc
    opportunities.sort(key=lambda o: (
        int(o["qualifies"]),
        o["scores"]["composite_score"],
        o["post_score"],
    ), reverse=True)

    qualified = [o for o in opportunities if o["qualifies"]]
    log(f"  Total scored: {len(opportunities)}")
    log(f"  Qualified (7+ all dimensions, ≤14 days to sale): {len(qualified)}")

    # 5. Save
    output = {
        "generated_at": datetime.datetime.utcnow().isoformat(),
        "total_scanned": len(opportunities),
        "total_qualified": len(qualified),
        "fast_roi_rule": f"Hard reject if estimated days_to_first_sale > {MAX_DAYS_TO_SALE}",
        "opportunities": opportunities,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    log(f"  Saved {len(opportunities)} opportunities to {OUTPUT_FILE}")

    # 6. Print top picks
    log("\nTOP QUALIFIED OPPORTUNITIES:")
    for i, opp in enumerate(qualified[:5], 1):
        s = opp["scores"]
        log(f"  {i}. {opp['idea'][:60]}")
        log(f"     Composite: {s['composite_score']}/10 | Days to sale: {s['days_to_first_sale']}")
        log(f"     Community: {s['launch_community']}")
        log(f"     Competition: {opp['competition_notes']}")

    log("\nScanner run complete.")
    return opportunities


if __name__ == "__main__":
    run_scanner()
