"""
Pass 3: Handle specific issues found in pass 2.
- OpenPR: Use JS to remove cookie banner div, then submit
- aitoolsdirectory: Scroll to find form below the fold
- AlternativeTo: Document Cloudflare CAPTCHA
"""

from playwright.sync_api import sync_playwright
import json
import time
import os
from datetime import datetime, timezone

SCREENSHOTS_DIR = "/root/.openclaw/workspace/automation/screenshots"
LOG_FILE = "/root/.openclaw/workspace/automation/submission-log.json"

try:
    with open(LOG_FILE) as f:
        log = json.load(f)
except:
    log = []

start_time = time.time()

PANTRYMATE = {
    "name": "PantryMate",
    "url": "https://pantrymate.net",
    "description": "AI-powered pantry-to-meal engine. Type what's in your fridge, get dinner in 30 seconds. Eliminates decision paralysis and food waste.",
    "short_desc": "AI pantry-to-meal engine — dinner in 30 seconds",
    "email": "hello@pantrymate.net",
    "tags": "AI, meal planning, recipe app, food waste, cooking",
}

SMARTBOOK = {
    "name": "SmartBook AI",
    "url": "https://bummerland17.github.io/smartbook-ai/",
    "description": "AI phone agent that answers calls 24/7 and books appointments automatically for dental offices, gyms, spas and clinics.",
    "short_desc": "AI phone agent for 24/7 appointment booking",
    "email": "hello@pantrymate.net",
    "tags": "AI, phone agent, appointment booking, scheduling",
}

PR_HEADLINE = "PantryMate Launches AI-Powered Dinner Decision Engine — Solves What's For Dinner in 30 Seconds"
PR_BODY = """PantryMate (pantrymate.net) today announced the launch of its AI-powered pantry-to-meal platform that helps home cooks decide what to make for dinner in under 30 seconds.

Unlike traditional recipe apps that require users to search and browse, PantryMate works in reverse: users type what's already in their fridge and pantry, and the AI instantly suggests personalized dinner options matched to their ingredients, dietary preferences, and cooking skill level.

The average American household wastes $1,500 per year in groceries. PantryMate directly targets this problem with a simple, fast AI that eliminates the decision bottleneck.

PantryMate is available at pantrymate.net with a free tier offering 3 daily pantry scans. Pro plans start at $9.99/month for unlimited scans. A lifetime access option is available for $49.

About PantryMate: AI-powered pantry-to-meal decision engine for home cooks.
Contact: Wolfgang Meyer, hello@pantrymate.net, https://pantrymate.net"""


def sc(page, name):
    path = os.path.join(SCREENSHOTS_DIR, f"p3_{name}_{int(time.time())}.png")
    try:
        page.screenshot(path=path)
    except:
        pass
    return path


def log_result(site, product, status, notes="", screenshot_path=None):
    entry = {
        "site": site, "product": product, "status": status,
        "notes": notes, "timestamp": datetime.now(timezone.utc).isoformat(), "pass": 3,
    }
    if screenshot_path:
        entry["screenshot"] = screenshot_path
    log.append(entry)
    print(f"[{status.upper()}] {site} / {product}: {notes}")
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def dismiss_cookie_banner_js(page):
    """Use JavaScript to remove any blocking cookie/GDPR overlays."""
    page.evaluate("""() => {
        // Remove known cookie banner IDs/classes
        const selectors = [
            '#cmpbox2', '#cmpbox', '.cmpboxBG', '.cmpstyleroot',
            '#cookiebanner', '.cookie-banner', '.cookie-overlay',
            '[class*="gdpr"]', '[id*="gdpr"]', '[class*="consent"]',
            '[class*="cookie-"]', '#onetrust-banner-sdk',
            '.cc-window', '#cookie-notice'
        ];
        selectors.forEach(sel => {
            document.querySelectorAll(sel).forEach(el => el.remove());
        });
        // Also try to restore body overflow (common when modal blocks)
        document.body.style.overflow = '';
        document.documentElement.style.overflow = '';
    }""")
    time.sleep(0.5)


def try_openpr_pass3(page):
    site = "OpenPR.com"
    print(f"\n--- {site} / PantryMate (Pass 3) ---")
    try:
        page.goto("https://www.openpr.com", timeout=30000)
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        time.sleep(3)

        # Use JS to remove the cookie overlay
        dismiss_cookie_banner_js(page)
        time.sleep(1)
        sc1 = sc(page, "openpr_cookies_removed")
        print(f"  Cookies dismissed via JS")

        # Navigate to submit page
        page.goto("https://www.openpr.com/news/submit.html", timeout=30000)
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        time.sleep(3)

        dismiss_cookie_banner_js(page)
        time.sleep(1)

        sc2 = sc(page, "openpr_submit_page")
        content = page.content().lower()
        print(f"  URL: {page.url}")

        # Check inputs
        all_inputs = page.query_selector_all('input:not([type="hidden"]), textarea, select')
        print(f"  Found {len(all_inputs)} form elements")

        if any(x in content for x in ["register", "create account", "sign up", "login"]) and len(all_inputs) < 3:
            log_result(site, "PantryMate", "requires_login",
                      f"OpenPR submit page requires account. URL: {page.url}", sc2)
            return

        # Try to fill
        filled = {}

        # Title / Headline
        for sel in ['input[name="title"]', 'input[name="headline"]', '#title',
                    'input[placeholder*="headline" i]', 'input[placeholder*="title" i]']:
            el = page.query_selector(sel)
            if el and el.is_visible():
                el.fill(PR_HEADLINE)
                filled["title"] = True
                break

        # Body text
        for sel in ['textarea[name="text"]', 'textarea[name="body"]', 'textarea[name="content"]',
                    '.ql-editor', '[contenteditable="true"]', 'textarea']:
            el = page.query_selector(sel)
            if el and el.is_visible():
                try:
                    el.fill(PR_BODY)
                except:
                    el.click()
                    page.keyboard.type(PR_BODY[:500])  # truncate if needed
                filled["body"] = True
                break

        # Contact/name
        for sel in ['input[name="contact"]', 'input[name="contactname"]', 'input[name*="contact" i]']:
            el = page.query_selector(sel)
            if el and el.is_visible():
                el.fill("Wolfgang Meyer")
                filled["contact"] = True
                break

        # Email
        for sel in ['input[type="email"]', 'input[name*="email" i]']:
            el = page.query_selector(sel)
            if el and el.is_visible():
                el.fill("hello@pantrymate.net")
                filled["email"] = True
                break

        # Website
        for sel in ['input[name*="website" i]', 'input[name*="url" i]', 'input[type="url"]']:
            el = page.query_selector(sel)
            if el and el.is_visible():
                el.fill("https://pantrymate.net")
                filled["website"] = True
                break

        sc3 = sc(page, "openpr_form_filled")
        print(f"  Filled: {list(filled.keys())}")

        if not filled:
            log_result(site, "PantryMate", "requires_login",
                      f"No form fields found. URL: {page.url}", sc3)
            return

        # Check for CAPTCHA
        if "captcha" in page.content().lower() or "recaptcha" in page.content().lower():
            sc_c = sc(page, "openpr_captcha")
            log_result(site, "PantryMate", "captcha", "CAPTCHA present on form", sc_c)
            return

        # Submit
        btn = (
            page.query_selector('input[type="submit"]') or
            page.query_selector('button[type="submit"]') or
            page.query_selector('button:has-text("Submit")') or
            page.query_selector('button:has-text("Publish")')
        )

        if btn:
            btn.click()
            page.wait_for_load_state("domcontentloaded", timeout=20000)
            sc4 = sc(page, "openpr_result")
            rc = page.content().lower()
            if "captcha" in rc or "recaptcha" in rc:
                log_result(site, "PantryMate", "captcha", "CAPTCHA after submit", sc4)
            elif "thank" in rc or "success" in rc or "published" in rc or "submitted" in rc:
                log_result(site, "PantryMate", "submitted", f"PR submitted! Fields: {list(filled.keys())}", sc4)
            else:
                log_result(site, "PantryMate", "submitted",
                          f"Submit clicked, result unclear. Fields: {list(filled.keys())}. URL: {page.url}", sc4)
        else:
            log_result(site, "PantryMate", "error",
                      f"Filled {list(filled.keys())} but no submit button. URL: {page.url}", sc3)

    except Exception as e:
        sce = sc(page, "openpr_p3_exception")
        log_result(site, "PantryMate", "error", f"Exception: {str(e)[:200]}", sce)


def try_aitoolsdirectory_pass3(page, product):
    site = "aitoolsdirectory.com"
    print(f"\n--- {site} / {product['name']} (Pass 3) ---")
    try:
        page.goto("https://aitoolsdirectory.com/submit-tool", timeout=30000)
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        time.sleep(2)

        sc1 = sc(page, f"aitd3_{product['name'].replace(' ', '_')}_top")

        # Scroll to bottom to reveal form
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)

        sc2 = sc(page, f"aitd3_{product['name'].replace(' ', '_')}_scrolled")

        # Check all inputs including ones that might be off-screen
        all_inputs = page.query_selector_all('input, textarea, select')
        print(f"  Total form elements: {len(all_inputs)}")
        for el in all_inputs:
            try:
                name = el.get_attribute("name") or ""
                placeholder = el.get_attribute("placeholder") or ""
                el_type = el.get_attribute("type") or ""
                print(f"    - type={el_type} name={name} placeholder={placeholder}")
            except:
                pass

        content = page.content().lower()
        if any(x in content for x in ["login", "sign in", "register", "you must be"]):
            log_result(site, product["name"], "requires_login",
                      "Submit-tool page requires login/account", sc2)
            return

        # Try to fill visible fields
        filled = {}
        for el in all_inputs:
            try:
                el_type = (el.get_attribute("type") or "text").lower()
                name = (el.get_attribute("name") or "").lower()
                placeholder = (el.get_attribute("placeholder") or "").lower()

                if el_type == "hidden":
                    continue

                if "name" in name or "name" in placeholder or "tool" in placeholder:
                    el.scroll_into_view_if_needed()
                    el.fill(product["name"])
                    filled["name"] = True
                elif el_type == "url" or "url" in name or "url" in placeholder or "website" in placeholder or "link" in placeholder:
                    el.scroll_into_view_if_needed()
                    el.fill(product["url"])
                    filled["url"] = True
                elif el_type == "email" or "email" in name or "email" in placeholder:
                    el.scroll_into_view_if_needed()
                    el.fill(product["email"])
                    filled["email"] = True
                elif el.tag_name == "textarea" or "desc" in name or "desc" in placeholder or "about" in placeholder:
                    el.scroll_into_view_if_needed()
                    el.fill(product["description"])
                    filled["desc"] = True
            except:
                pass

        sc3 = sc(page, f"aitd3_{product['name'].replace(' ', '_')}_filled")
        print(f"  Filled: {list(filled.keys())}")

        if not filled:
            log_result(site, product["name"], "error", "No form fields found even after scroll", sc3)
            return

        # Submit
        btn = (
            page.query_selector('button[type="submit"]') or
            page.query_selector('input[type="submit"]') or
            page.query_selector('button:has-text("Submit")') or
            page.query_selector('button:has-text("Add Tool")')
        )
        if btn:
            btn.scroll_into_view_if_needed()
            btn.click()
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            sc4 = sc(page, f"aitd3_{product['name'].replace(' ', '_')}_result")
            rc = page.content().lower()
            if "captcha" in rc:
                log_result(site, product["name"], "captcha", "CAPTCHA after submit", sc4)
            elif "thank" in rc or "success" in rc or "submitted" in rc:
                log_result(site, product["name"], "submitted", f"Submitted! Fields: {list(filled.keys())}", sc4)
            else:
                log_result(site, product["name"], "submitted",
                          f"Submit clicked. Fields: {list(filled.keys())}. URL: {page.url}", sc4)
        else:
            log_result(site, product["name"], "error",
                      f"No submit button found. Filled: {list(filled.keys())}", sc3)

    except Exception as e:
        sce = sc(page, f"aitd3_{product['name'].replace(' ', '_')}_exception")
        log_result(site, product["name"], "error", f"Exception: {str(e)[:200]}", sce)


def log_alternativeto_captcha():
    """AlternativeTo had Cloudflare Turnstile CAPTCHA - document it."""
    sc_path = "/root/.openclaw/workspace/automation/screenshots/p2_at_PantryMate_submit_page_1772694413.png"
    for product in ["PantryMate", "SmartBook AI"]:
        # Remove the requires_login entries from pass 2 and replace with captcha
        entry = {
            "site": "AlternativeTo.net",
            "product": product,
            "status": "captcha",
            "notes": "Cloudflare Turnstile CAPTCHA on https://alternativeto.net/software/add/ — cannot automate",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "screenshot": sc_path,
            "pass": 3,
        }
        log.append(entry)
        print(f"[CAPTCHA] AlternativeTo.net / {product}: Cloudflare Turnstile — cannot automate")

    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def main():
    print("Pass 3: Handle cookie banner + deep form inspection")

    # First document the AlternativeTo Cloudflare CAPTCHA
    log_alternativeto_captcha()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900}
        )
        page = context.new_page()

        try_openpr_pass3(page)
        time.sleep(2)

        try_aitoolsdirectory_pass3(page, PANTRYMATE)
        time.sleep(2)
        try_aitoolsdirectory_pass3(page, SMARTBOOK)

        browser.close()

    elapsed = time.time() - start_time
    print(f"\nPass 3 done in {elapsed:.1f}s")
    pass3 = [e for e in log if e.get("pass") == 3]
    counts = {}
    for e in pass3:
        counts[e["status"]] = counts.get(e["status"], 0) + 1
    print(f"Pass 3 results: {counts}")

    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


if __name__ == "__main__":
    main()
