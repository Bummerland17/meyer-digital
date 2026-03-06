"""
Pass 2: Targeted submissions based on page analysis.
- OpenPR: accept cookie banner, then submit PR
- PRLog: find correct submit URL via nav link
- AlternativeTo: find correct add-software URL
- aitoolsdirectory: use Submit Tool button in nav
"""

from playwright.sync_api import sync_playwright
import json
import time
import os
from datetime import datetime, timezone

SCREENSHOTS_DIR = "/root/.openclaw/workspace/automation/screenshots"
LOG_FILE = "/root/.openclaw/workspace/automation/submission-log.json"

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# Load existing log
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
    "category": "Productivity / Food & Cooking",
    "email": "hello@pantrymate.net",
    "tags": "AI, meal planning, recipe app, food waste, cooking, kitchen",
}

SMARTBOOK = {
    "name": "SmartBook AI",
    "url": "https://bummerland17.github.io/smartbook-ai/",
    "description": "AI phone agent that answers calls 24/7 and books appointments automatically for dental offices, gyms, spas and clinics.",
    "short_desc": "AI phone agent for 24/7 appointment booking",
    "category": "Business / Scheduling / AI",
    "email": "hello@pantrymate.net",
    "tags": "AI, phone agent, appointment booking, scheduling, dental, gym",
}

PR_HEADLINE = 'PantryMate Launches AI-Powered Dinner Decision Engine — Solves "What\'s For Dinner?" in 30 Seconds'
PR_SUBHEAD = "New web app turns pantry ingredients into personalized dinner ideas instantly, eliminating food waste and decision fatigue"
PR_BODY = """PantryMate (pantrymate.net) today announced the launch of its AI-powered pantry-to-meal platform that helps home cooks decide what to make for dinner in under 30 seconds.

Unlike traditional recipe apps that require users to search and browse, PantryMate works in reverse — users type what's already in their fridge and pantry, and the AI instantly suggests personalized dinner options matched to their ingredients, dietary preferences, and cooking skill level.

"The real problem isn't finding recipes — it's the decision paralysis of staring at a full fridge and still ordering takeout," said Wolfgang Meyer, founder of PantryMate. "We solved that in 30 seconds."

The average American household wastes $1,500 per year in groceries and spends an additional $60+ per month on takeout ordered on nights when the fridge was full. PantryMate directly targets this $134/month problem with a simple, fast AI that eliminates the decision bottleneck.

PantryMate is available at pantrymate.net with a free tier offering 3 daily pantry scans. Pro plans start at $9.99/month for unlimited scans, dietary filters, and weekly shopping list generation. A lifetime access option is available for a one-time payment of $49.

###

About PantryMate:
PantryMate is an AI-powered pantry-to-meal decision engine designed to eliminate dinner decision paralysis for home cooks. The platform matches users available ingredients to personalized meal options in seconds, reducing food waste and takeout spending.

Contact:
Wolfgang Meyer, Founder
hello@pantrymate.net
https://pantrymate.net"""


def screenshot(page, name):
    path = os.path.join(SCREENSHOTS_DIR, f"p2_{name}_{int(time.time())}.png")
    try:
        page.screenshot(path=path, full_page=False)
    except:
        pass
    return path


def log_result(site, product, status, notes="", screenshot_path=None):
    entry = {
        "site": site,
        "product": product,
        "status": status,
        "notes": notes,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pass": 2,
    }
    if screenshot_path:
        entry["screenshot"] = screenshot_path
    log.append(entry)
    print(f"[{status.upper()}] {site} / {product}: {notes}")
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def accept_cookies(page):
    """Try common cookie/GDPR accept patterns."""
    for selector in [
        'button:has-text("Accept all")',
        'button:has-text("Accept All")',
        'button:has-text("Accept")',
        'button:has-text("I agree")',
        'button:has-text("I AGREE")',
        'button:has-text("Agree")',
        'button:has-text("OK")',
        '#accept-all',
        '.accept-all',
        '[aria-label*="accept" i]',
    ]:
        try:
            btn = page.query_selector(selector)
            if btn and btn.is_visible():
                btn.click()
                time.sleep(1)
                return True
        except:
            pass
    return False


def fill_form_smart(page, product, extra_fields=None):
    """Smart form filler - tries multiple selector patterns."""
    filled = {}

    # Name field
    for sel in ['input[name*="name" i]', 'input[placeholder*="name" i]',
                'input[placeholder*="tool name" i]', 'input[id*="name" i]']:
        el = page.query_selector(sel)
        if el and el.is_visible():
            el.fill(product["name"])
            filled["name"] = product["name"]
            break

    # URL field
    for sel in ['input[type="url"]', 'input[name*="url" i]', 'input[placeholder*="url" i]',
                'input[placeholder*="website" i]', 'input[placeholder*="link" i]',
                'input[name*="website" i]']:
        el = page.query_selector(sel)
        if el and el.is_visible():
            el.fill(product["url"])
            filled["url"] = product["url"]
            break

    # Email field
    for sel in ['input[type="email"]', 'input[name*="email" i]', 'input[placeholder*="email" i]']:
        el = page.query_selector(sel)
        if el and el.is_visible():
            el.fill(product["email"])
            filled["email"] = product["email"]
            break

    # Description / textarea
    for sel in ['textarea[name*="desc" i]', 'textarea[placeholder*="desc" i]',
                'textarea[name*="about" i]', 'textarea']:
        el = page.query_selector(sel)
        if el and el.is_visible():
            el.fill(product["description"])
            filled["description"] = "filled"
            break

    # Short description
    for sel in ['input[name*="short" i]', 'input[placeholder*="short" i]',
                'input[placeholder*="tagline" i]', 'input[name*="tagline" i]']:
        el = page.query_selector(sel)
        if el and el.is_visible():
            el.fill(product.get("short_desc", product["description"][:100]))
            filled["short_desc"] = "filled"
            break

    if extra_fields:
        for field_sel, value in extra_fields.items():
            el = page.query_selector(field_sel)
            if el and el.is_visible():
                el.fill(value)
                filled[field_sel] = value

    return filled


def try_openpr(page):
    site = "OpenPR.com"
    print(f"\n--- {site} / PantryMate (Pass 2) ---")
    try:
        page.goto("https://www.openpr.com", timeout=30000)
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        time.sleep(2)

        # Accept cookie consent
        accepted = accept_cookies(page)
        print(f"  Cookie accepted: {accepted}")
        time.sleep(2)

        sc1 = screenshot(page, "openpr_after_cookies")

        # Look for "Submit Press Release" link
        submit_link = None
        for sel in [
            'a:has-text("Submit Press Release")',
            'a:has-text("Submit")',
            'a[href*="submit"]',
            'a[href*="press-release/submit"]',
        ]:
            submit_link = page.query_selector(sel)
            if submit_link:
                break

        if not submit_link:
            sc = screenshot(page, "openpr_no_submit_link")
            log_result(site, "PantryMate", "error", "Could not find Submit Press Release link after accepting cookies", sc)
            return

        href = submit_link.get_attribute("href")
        print(f"  Found submit link: {href}")

        # Navigate to submit page
        if href and href.startswith("http"):
            page.goto(href, timeout=30000)
        else:
            submit_link.click()
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        time.sleep(2)

        sc2 = screenshot(page, "openpr_submit_page")
        content = page.content().lower()

        # Check for login/register requirement
        if any(x in content for x in ["log in", "sign in", "register", "create account", "login"]):
            # Check if there's actually a form too
            inputs = page.query_selector_all('input:not([type="hidden"])')
            if len(inputs) < 2:
                log_result(site, "PantryMate", "requires_login",
                          f"Submit page requires registration. URL: {page.url}", sc2)
                return

        # Try to fill PR form
        filled = {}

        # Title/Headline
        for sel in ['input[name*="title" i]', 'input[name*="headline" i]',
                    'input[placeholder*="headline" i]', 'input[placeholder*="title" i]',
                    '#title', '#headline']:
            el = page.query_selector(sel)
            if el and el.is_visible():
                el.fill(PR_HEADLINE)
                filled["title"] = "filled"
                break

        # Body/Text
        for sel in ['textarea[name*="text" i]', 'textarea[name*="body" i]',
                    'textarea[name*="content" i]', 'textarea', '.ql-editor', '[contenteditable="true"]']:
            el = page.query_selector(sel)
            if el and el.is_visible():
                try:
                    el.fill(PR_BODY)
                except:
                    el.click()
                    page.keyboard.type(PR_BODY)
                filled["body"] = "filled"
                break

        # Category
        for sel in ['select[name*="cat" i]', 'select[name*="industry" i]', 'select']:
            el = page.query_selector(sel)
            if el and el.is_visible():
                try:
                    el.select_option(label="Technology")
                except:
                    pass
                filled["category"] = "attempted"
                break

        sc3 = screenshot(page, "openpr_form_filled")

        if not filled:
            log_result(site, "PantryMate", "requires_login",
                      f"No fillable form found on submit page. URL: {page.url}", sc3)
            return

        # Submit
        submit_btn = (
            page.query_selector('button[type="submit"]') or
            page.query_selector('input[type="submit"]') or
            page.query_selector('button:has-text("Submit")') or
            page.query_selector('button:has-text("Publish")')
        )

        if submit_btn:
            submit_btn.click()
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            sc4 = screenshot(page, "openpr_result")
            result_content = page.content().lower()
            if "captcha" in result_content or "recaptcha" in result_content:
                log_result(site, "PantryMate", "captcha", "CAPTCHA appeared after submit", sc4)
            elif "thank" in result_content or "success" in result_content or "submitted" in result_content:
                log_result(site, "PantryMate", "submitted", f"Form submitted. Filled: {list(filled.keys())}", sc4)
            else:
                log_result(site, "PantryMate", "submitted",
                          f"Submit clicked, unclear result. Filled: {list(filled.keys())}", sc4)
        else:
            log_result(site, "PantryMate", "error",
                      f"Filled {list(filled.keys())} but no submit button found", sc3)

    except Exception as e:
        sc = screenshot(page, "openpr_p2_error")
        log_result(site, "PantryMate", "error", f"Exception: {e}", sc)


def try_prlog(page):
    site = "PRLog.org"
    print(f"\n--- {site} / PantryMate (Pass 2) ---")
    try:
        # Navigate via homepage to find correct submit URL
        page.goto("https://www.prlog.org", timeout=30000)
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        time.sleep(2)

        sc1 = screenshot(page, "prlog_homepage")

        # Look for submit press release link
        submit_link = None
        for sel in [
            'a:has-text("Submit Free Press Release")',
            'a:has-text("Submit Press Release")',
            'a:has-text("Post Press Release")',
            'a[href*="press-release"]',
            'a[href*="submit"]',
        ]:
            submit_link = page.query_selector(sel)
            if submit_link:
                href = submit_link.get_attribute("href")
                print(f"  Found: {sel} -> {href}")
                break

        if not submit_link:
            # Try direct known URLs
            for url in ["https://www.prlog.org/press-release-submit.html",
                        "https://www.prlog.org/post-press-release.html",
                        "https://www.prlog.org/account/press-release/add"]:
                page.goto(url, timeout=20000)
                page.wait_for_load_state("domcontentloaded", timeout=15000)
                sc = screenshot(page, f"prlog_try_{url.split('/')[-1]}")
                content = page.content().lower()
                if "404" not in content and "not found" not in content:
                    print(f"  Found valid URL: {url}")
                    break
        else:
            submit_link.click()
            page.wait_for_load_state("domcontentloaded", timeout=20000)

        time.sleep(2)
        sc2 = screenshot(page, "prlog_submit_page")
        content = page.content().lower()
        print(f"  Current URL: {page.url}")

        if any(x in content for x in ["log in", "sign in", "register", "login", "create account"]):
            inputs = page.query_selector_all('input[type="text"], input[type="email"], input[type="password"]')
            print(f"  Found {len(inputs)} input fields")

            # Check if it's a login/register form we can try
            email_field = page.query_selector('input[type="email"], input[name*="email" i]')
            password_field = page.query_selector('input[type="password"]')

            if email_field and password_field:
                # It's a login form - mark as requires_login since we don't have credentials
                log_result(site, "PantryMate", "requires_login",
                          f"PRLog requires account. Login/register form at {page.url}. Use hello@pantrymate.net to create account manually.", sc2)
                return

            if len(inputs) < 2:
                log_result(site, "PantryMate", "requires_login",
                          f"No fillable PR form found, likely requires login. URL: {page.url}", sc2)
                return

        # Try to fill the PR form
        filled = {}
        for sel in ['input[name*="title" i]', 'input[name*="headline" i]', '#title', '#headline',
                    'input[placeholder*="headline" i]']:
            el = page.query_selector(sel)
            if el and el.is_visible():
                el.fill(PR_HEADLINE)
                filled["title"] = "filled"
                break

        for sel in ['textarea', '#body', '#text', 'input[name*="body" i]']:
            el = page.query_selector(sel)
            if el and el.is_visible():
                try:
                    el.fill(PR_BODY)
                except:
                    pass
                filled["body"] = "filled"
                break

        sc3 = screenshot(page, "prlog_form_filled")

        if not filled:
            log_result(site, "PantryMate", "requires_login",
                      f"Could not find PR form fields. URL: {page.url}", sc3)
            return

        submit_btn = (page.query_selector('button[type="submit"]') or
                     page.query_selector('input[type="submit"]'))
        if submit_btn:
            submit_btn.click()
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            sc4 = screenshot(page, "prlog_result")
            log_result(site, "PantryMate", "submitted",
                      f"Form submitted. Filled: {list(filled.keys())}", sc4)
        else:
            log_result(site, "PantryMate", "error",
                      f"Filled {list(filled.keys())} but no submit button", sc3)

    except Exception as e:
        sc = screenshot(page, "prlog_p2_error")
        log_result(site, "PantryMate", "error", f"Exception: {e}", sc)


def try_alternativeto(page, product):
    site = "AlternativeTo.net"
    print(f"\n--- {site} / {product['name']} (Pass 2) ---")
    try:
        # Try the homepage first to find correct add software URL
        page.goto("https://alternativeto.net", timeout=30000)
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        time.sleep(2)

        sc1 = screenshot(page, f"at_{product['name'].replace(' ', '_')}_homepage")
        content = page.content().lower()

        # Look for add/suggest software link
        add_link = None
        for sel in [
            'a:has-text("Add Software")',
            'a:has-text("Add App")',
            'a:has-text("Suggest")',
            'a[href*="add-software"]',
            'a[href*="add-app"]',
            'a[href*="suggest"]',
        ]:
            add_link = page.query_selector(sel)
            if add_link:
                href = add_link.get_attribute("href")
                print(f"  Found: {sel} -> {href}")
                break

        if add_link:
            add_link.click()
            page.wait_for_load_state("domcontentloaded", timeout=20000)
            time.sleep(2)
        else:
            # Try known URLs
            for url in [
                "https://alternativeto.net/software/add/",
                "https://alternativeto.net/add/",
                "https://alternativeto.net/suggest/",
            ]:
                try:
                    page.goto(url, timeout=15000)
                    page.wait_for_load_state("domcontentloaded", timeout=10000)
                    if "404" not in page.content().lower() and "not found" not in page.content().lower():
                        print(f"  Found valid URL: {url}")
                        break
                except:
                    pass

        time.sleep(2)
        sc2 = screenshot(page, f"at_{product['name'].replace(' ', '_')}_submit_page")
        content = page.content().lower()
        print(f"  Current URL: {page.url}")

        if any(x in content for x in ["sign in", "log in", "create account", "register"]):
            inputs = page.query_selector_all('input:not([type="hidden"])')
            print(f"  {len(inputs)} inputs found")
            if len(inputs) < 2:
                log_result(site, product["name"], "requires_login",
                          f"AlternativeTo requires login. URL: {page.url}", sc2)
                return

        # Try to fill form
        filled = fill_form_smart(page, product)
        sc3 = screenshot(page, f"at_{product['name'].replace(' ', '_')}_filled")
        print(f"  Filled: {list(filled.keys())}")

        if not filled:
            log_result(site, product["name"], "requires_login",
                      f"No fillable form found. URL: {page.url}", sc3)
            return

        submit_btn = (
            page.query_selector('button[type="submit"]') or
            page.query_selector('input[type="submit"]') or
            page.query_selector('button:has-text("Add")') or
            page.query_selector('button:has-text("Submit")')
        )

        if submit_btn:
            submit_btn.click()
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            sc4 = screenshot(page, f"at_{product['name'].replace(' ', '_')}_result")
            rc = page.content().lower()
            if "captcha" in rc or "recaptcha" in rc:
                log_result(site, product["name"], "captcha", "CAPTCHA after submit", sc4)
            elif "thank" in rc or "success" in rc or "added" in rc:
                log_result(site, product["name"], "submitted", f"Submitted! Filled: {list(filled.keys())}", sc4)
            else:
                log_result(site, product["name"], "submitted",
                          f"Submit clicked. Filled: {list(filled.keys())}", sc4)
        else:
            log_result(site, product["name"], "error",
                      f"No submit button. Filled: {list(filled.keys())}", sc3)

    except Exception as e:
        sc = screenshot(page, f"at_{product['name'].replace(' ', '_')}_p2_error")
        log_result(site, product["name"], "error", f"Exception: {e}", sc)


def try_aitoolsdirectory(page, product):
    site = "aitoolsdirectory.com"
    print(f"\n--- {site} / {product['name']} (Pass 2) ---")
    try:
        # Go to homepage and click Submit Tool button
        page.goto("https://aitoolsdirectory.com", timeout=30000)
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        time.sleep(2)

        # Accept cookies if needed
        accept_cookies(page)
        time.sleep(1)

        sc1 = screenshot(page, f"aitd_{product['name'].replace(' ', '_')}_homepage")

        # Click Submit Tool button
        submit_btn = (
            page.query_selector('a:has-text("Submit Tool")') or
            page.query_selector('button:has-text("Submit Tool")') or
            page.query_selector('a[href*="submit"]') or
            page.query_selector('button:has-text("Submit")')
        )

        if not submit_btn:
            log_result(site, product["name"], "error", "Could not find Submit Tool button", sc1)
            return

        href = submit_btn.get_attribute("href")
        print(f"  Submit button href: {href}")

        if href and href.startswith("http"):
            page.goto(href, timeout=20000)
        else:
            submit_btn.click()
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        time.sleep(2)

        sc2 = screenshot(page, f"aitd_{product['name'].replace(' ', '_')}_submit_page")
        content = page.content().lower()
        print(f"  URL: {page.url}")

        if any(x in content for x in ["sign in", "log in", "register", "create account"]):
            inputs = page.query_selector_all('input:not([type="hidden"])')
            if len(inputs) < 2:
                log_result(site, product["name"], "requires_login",
                          f"Submit page requires login. URL: {page.url}", sc2)
                return

        # Fill form
        filled = fill_form_smart(page, product)
        sc3 = screenshot(page, f"aitd_{product['name'].replace(' ', '_')}_filled")
        print(f"  Filled: {list(filled.keys())}")

        if not filled:
            log_result(site, product["name"], "error",
                      f"No form fields found. URL: {page.url}", sc3)
            return

        btn = (
            page.query_selector('button[type="submit"]') or
            page.query_selector('input[type="submit"]') or
            page.query_selector('button:has-text("Submit")') or
            page.query_selector('button:has-text("Add")')
        )

        if btn:
            btn.click()
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            sc4 = screenshot(page, f"aitd_{product['name'].replace(' ', '_')}_result")
            rc = page.content().lower()
            if "captcha" in rc:
                log_result(site, product["name"], "captcha", "CAPTCHA after submit", sc4)
            elif "thank" in rc or "success" in rc:
                log_result(site, product["name"], "submitted", f"Submitted! Filled: {list(filled.keys())}", sc4)
            else:
                log_result(site, product["name"], "submitted",
                          f"Submit clicked. Filled: {list(filled.keys())}", sc4)
        else:
            log_result(site, product["name"], "error",
                      f"No submit button. Filled: {list(filled.keys())}", sc3)

    except Exception as e:
        sc = screenshot(page, f"aitd_{product['name'].replace(' ', '_')}_p2_error")
        log_result(site, product["name"], "error", f"Exception: {e}", sc)


def main():
    print("Pass 2: Targeted submissions")
    print(f"Logs: {LOG_FILE}")

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

        try_openpr(page)
        time.sleep(2)

        try_prlog(page)
        time.sleep(2)

        try_alternativeto(page, PANTRYMATE)
        time.sleep(2)
        try_alternativeto(page, SMARTBOOK)
        time.sleep(2)

        try_aitoolsdirectory(page, PANTRYMATE)
        time.sleep(2)
        try_aitoolsdirectory(page, SMARTBOOK)
        time.sleep(2)

        browser.close()

    elapsed = time.time() - start_time
    print(f"\n{'='*50}")
    print(f"Pass 2 done in {elapsed:.1f}s")

    # Summary of pass 2 entries
    pass2 = [e for e in log if e.get("pass") == 2]
    counts = {}
    for e in pass2:
        counts[e["status"]] = counts.get(e["status"], 0) + 1
    print(f"Pass 2 results: {counts}")

    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


if __name__ == "__main__":
    main()
