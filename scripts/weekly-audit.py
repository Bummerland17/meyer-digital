#!/usr/bin/env python3
"""
Weekly Website/App Audit — runs every Sunday at 10:00 UTC
Checks all live sites: HTTP status, response time, key elements, broken links
Sends summary to Telegram + saves to /reviews/site-audits/YYYY-MM-DD.md
"""

import json, datetime, requests, time, re
from pathlib import Path
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser

WORKSPACE  = Path("/root/.openclaw/workspace")
BOT_TOKEN  = json.load(open("/root/.openclaw/openclaw.json"))["channels"]["telegram"]["botToken"]
CHAT_ID    = "8654703697"
TODAY      = datetime.date.today()
OUTPUT_DIR = WORKSPACE / "reviews/site-audits"

SITES = [
    "https://pantrymate.net",
    "https://unitfix.app",
    "https://bummerland17.github.io/smartbook-ai",
    "https://bummerland17.github.io/wolfpack-ai",
    "https://bummerland17.github.io/ai-sales-script-bundle",
    "https://bummerland17.github.io/app-launch-playbook",
    "https://bummerland17.github.io/landlord-maintenance-templates",
    "https://bummerland17.github.io/veldt",
    "https://bummerland17.github.io/sonara",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; WolfgangAuditBot/1.0)"
}

def tg(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"},
            timeout=10
        )
    except Exception as e:
        print(f"Telegram error: {e}")

class HTMLAnalyzer(HTMLParser):
    """Parse HTML to find title, meta description, CTA buttons, and links."""
    def __init__(self):
        super().__init__()
        self.title = ""
        self.description = ""
        self.cta_buttons = []
        self.links = []
        self._in_title = False
    
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == "title":
            self._in_title = True
        
        if tag == "meta":
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            if name == "description" or prop == "og:description":
                self.description = attrs_dict.get("content", "")
        
        if tag == "a":
            href = attrs_dict.get("href", "")
            if href and not href.startswith("#") and not href.startswith("mailto:"):
                self.links.append(href)
            # CTA detection
            cls = attrs_dict.get("class", "").lower()
            text_hint = attrs_dict.get("aria-label", "").lower()
            if any(kw in cls for kw in ["cta", "btn", "button", "signup", "get-started", "buy"]):
                self.cta_buttons.append({"tag": "a", "class": cls, "href": href})
        
        if tag == "button":
            cls = attrs_dict.get("class", "").lower()
            if any(kw in cls for kw in ["cta", "primary", "signup", "get-started", "buy"]):
                self.cta_buttons.append({"tag": "button", "class": cls})
    
    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
    
    def handle_data(self, data):
        if self._in_title:
            self.title += data.strip()

def check_site(url):
    """Run full audit on a single site."""
    result = {
        "url": url,
        "status": None,
        "response_time_ms": None,
        "title": "",
        "description": "",
        "has_cta": False,
        "cta_count": 0,
        "links_found": 0,
        "broken_links": [],
        "errors": [],
        "grade": "unknown"
    }
    
    # HTTP check
    try:
        start = time.time()
        r = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
        elapsed = int((time.time() - start) * 1000)
        result["status"] = r.status_code
        result["response_time_ms"] = elapsed
        
        if r.status_code != 200:
            result["errors"].append(f"HTTP {r.status_code}")
            result["grade"] = "F"
            return result
        
        # Parse HTML
        html = r.text
        analyzer = HTMLAnalyzer()
        try:
            analyzer.feed(html)
        except Exception as e:
            result["errors"].append(f"HTML parse error: {e}")
        
        result["title"] = analyzer.title[:100]
        result["description"] = analyzer.description[:200]
        result["has_cta"] = len(analyzer.cta_buttons) > 0
        result["cta_count"] = len(analyzer.cta_buttons)
        result["links_found"] = len(analyzer.links)
        
        # Check for broken links (first level, up to 10)
        domain = urlparse(url).netloc
        links_to_check = []
        for link in analyzer.links[:10]:
            if link.startswith("/"):
                links_to_check.append(urljoin(url, link))
            elif link.startswith("http") and domain in link:
                links_to_check.append(link)
        
        broken = []
        for link in links_to_check[:5]:  # max 5 link checks per site
            try:
                lr = requests.head(link, headers=HEADERS, timeout=8, allow_redirects=True)
                if lr.status_code >= 400:
                    broken.append({"url": link, "status": lr.status_code})
            except Exception:
                broken.append({"url": link, "status": "timeout"})
        
        result["broken_links"] = broken
        
        # Grade the site
        issues = 0
        if not result["title"]: issues += 2
        if not result["description"]: issues += 1
        if not result["has_cta"]: issues += 1
        if broken: issues += len(broken)
        if elapsed > 3000: issues += 1
        
        if issues == 0: result["grade"] = "A"
        elif issues == 1: result["grade"] = "B"
        elif issues == 2: result["grade"] = "C"
        elif issues <= 4: result["grade"] = "D"
        else: result["grade"] = "F"
        
    except requests.exceptions.ConnectionError:
        result["status"] = "DOWN"
        result["errors"].append("Connection refused / DNS failed")
        result["grade"] = "F"
    except requests.exceptions.Timeout:
        result["status"] = "TIMEOUT"
        result["errors"].append("Timed out after 20s")
        result["grade"] = "F"
    except Exception as e:
        result["status"] = "ERROR"
        result["errors"].append(str(e)[:100])
        result["grade"] = "F"
    
    return result

def main():
    print(f"[weekly-audit] Running for {TODAY}")
    
    audits = []
    for url in SITES:
        print(f"  Checking: {url}")
        result = check_site(url)
        audits.append(result)
        status_icon = "✅" if result["status"] == 200 else "❌"
        print(f"    {status_icon} {result['status']} | {result['response_time_ms']}ms | Grade: {result['grade']}")
        time.sleep(1)  # polite delay
    
    # Tally
    up = [a for a in audits if a["status"] == 200]
    down = [a for a in audits if a["status"] != 200]
    total_broken_links = sum(len(a["broken_links"]) for a in audits)
    no_cta = [a for a in audits if not a["has_cta"] and a["status"] == 200]
    no_desc = [a for a in audits if not a["description"] and a["status"] == 200]
    slow = [a for a in audits if (a["response_time_ms"] or 0) > 3000]
    
    # Build report
    lines = [
        f"# Site Audit — {TODAY}",
        f"*{len(up)}/{len(SITES)} sites healthy*",
        "",
        "## 📊 Summary",
        f"- Sites up: {len(up)}/{len(SITES)}",
        f"- Sites down/error: {len(down)}",
        f"- Broken links found: {total_broken_links}",
        f"- No CTA detected: {len(no_cta)}",
        f"- No meta description: {len(no_desc)}",
        f"- Slow sites (>3s): {len(slow)}",
        "",
        "## 🌐 Per-Site Results",
    ]
    
    for a in audits:
        grade_emoji = {"A": "🟢", "B": "🟡", "C": "🟠", "D": "🔴", "F": "💀"}.get(a["grade"], "❓")
        lines.append(f"\n### {grade_emoji} {a['url']}")
        lines.append(f"- **Status:** {a['status']} | **Response:** {a['response_time_ms']}ms | **Grade:** {a['grade']}")
        lines.append(f"- **Title:** {a['title'] or '⚠️ MISSING'}")
        lines.append(f"- **Description:** {a['description'][:80] + '...' if len(a['description']) > 80 else a['description'] or '⚠️ MISSING'}")
        lines.append(f"- **CTA Buttons:** {a['cta_count']} {'✅' if a['has_cta'] else '⚠️ None found'}")
        lines.append(f"- **Links checked:** {a['links_found']}")
        if a["broken_links"]:
            lines.append(f"- **Broken links:** {len(a['broken_links'])}")
            for bl in a["broken_links"]:
                lines.append(f"  - {bl['url']} → {bl['status']}")
        if a["errors"]:
            lines.append(f"- **Errors:** {'; '.join(a['errors'])}")
    
    report = "\n".join(lines)
    
    # Save
    out_path = OUTPUT_DIR / f"{TODAY}.md"
    out_path.write_text(report)
    print(f"Saved: {out_path}")
    
    # Telegram summary
    emoji_map = {"A": "🟢", "B": "🟡", "C": "🟠", "D": "🔴", "F": "💀"}
    tg_msg = f"🔍 *Weekly Site Audit — {TODAY}*\n\n"
    tg_msg += f"✅ Up: {len(up)}/{len(SITES)} | ❌ Down: {len(down)}\n"
    tg_msg += f"🔗 Broken links: {total_broken_links} | 🐢 Slow: {len(slow)}\n\n"
    
    if down:
        tg_msg += "*🚨 Sites Down:*\n"
        for a in down:
            tg_msg += f"• {a['url']} → {a['status']}\n"
        tg_msg += "\n"
    
    tg_msg += "*Grades:*\n"
    for a in audits:
        emoji = emoji_map.get(a["grade"], "❓")
        domain = urlparse(a["url"]).netloc + urlparse(a["url"]).path.rstrip("/")
        time_str = f"{a['response_time_ms']}ms" if a["response_time_ms"] else "N/A"
        tg_msg += f"{emoji} `{domain}` — {a['status']} | {time_str}\n"
    
    if no_cta:
        tg_msg += f"\n⚠️ No CTA found on {len(no_cta)} site(s)\n"
    
    tg_msg += f"\n📄 Full report: reviews/site-audits/{TODAY}.md"
    
    tg(tg_msg)
    print("Telegram alert sent.")

if __name__ == "__main__":
    main()
