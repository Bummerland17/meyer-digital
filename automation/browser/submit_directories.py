#!/usr/bin/env python3
"""
Directory submission script for PantryMate and SmartBook AI.
Uses Playwright (headless Chromium) to submit to free AI/startup directories.
"""

import json
import time
import os
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

SCREENSHOTS_DIR = "/root/.openclaw/workspace/automation/screenshots"
LOG_FILE = "/root/.openclaw/workspace/automation/submission-log-round2.json"

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

PRODUCTS = {
    "PantryMate": {
        "url": "https://pantrymate.net",
        "tagline": "Type what's in your fridge, get dinner in 30 seconds",
        "description": "AI-powered pantry-to-meal decision engine. Eliminates dinner decision paralysis — type your ingredients, get personalized dinner ideas instantly. No more staring at a full fridge and ordering takeout.",
        "category": "AI Tools / Food & Meal Planning / Productivity",
        "email": "hello@pantrymate.net",
        "name": "PantryMate",
    },
    "SmartBook AI": {
        "url": "https://bummerland17.github.io/smartbook-ai/",
        "tagline": "AI phone agent that books appointments 24/7",
        "description": "SmartBook AI answers every call after hours, books appointments directly into your calendar, and sends SMS confirmations. $497/month flat. No contracts.",
        "category": "AI Tools / Business / Scheduling",
        "email": "hello@pantrymate.net",
        "name": "SmartBook AI",
    },
}

results = []

def log_result(directory, product, status, notes=""):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "directory": directory,
        "product": product,
        "status": status,
        "notes": notes,
    }
    results.append(entry)
    print(f"[{status.upper()}] {directory} — {product}: {notes}")


def screenshot(page, name):
    path = os.path.join(SCREENSHOTS_DIR, f"{name}.png")
    page.screenshot(path=path)
    return path


def has_captcha(page):
    content = page.content().lower()
    return any(k in content for k in ["recaptcha", "hcaptcha", "cf-turnstile", "captcha", "i am not a robot"])


def fill_if_exists(page, selectors, value):
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el and el.is_visible():
                el.fill(value)
                return True
        except Exception:
            pass
    return False


def click_if_exists(page, selectors):
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el and el.is_visible():
                el.click()
                return True
        except Exception:
            pass
    return False


# ─── 1. Uneed.be ────────────────────────────────────────────────────────────

def submit_uneed(page, product):
    name = product["name"]
    try:
        page.goto("https://www.uneed.be/submit-a-tool", timeout=30000, wait_until="domcontentloaded")
        time.sleep(3)

        if has_captcha(page):
            screenshot(page, f"uneed_{name.replace(' ', '_')}_captcha")
            log_result("Uneed.be", name, "captcha_blocked", "CAPTCHA detected on page load")
            return

        content = page.content().lower()
        if any(k in content for k in ["sign in", "log in", "login", "create account", "register"]):
            if "submit" not in content:
                screenshot(page, f"uneed_{name.replace(' ', '_')}_login")
                log_result("Uneed.be", name, "requires_account", "Login/signup wall detected")
                return

        # Try filling the form
        filled = 0
        filled += fill_if_exists(page, ['input[name="name"]', 'input[placeholder*="name" i]', '#name'], name)
        filled += fill_if_exists(page, ['input[name="url"]', 'input[placeholder*="url" i]', 'input[type="url"]', '#url'], product["url"])
        filled += fill_if_exists(page, ['input[name="tagline"]', 'input[placeholder*="tagline" i]', '#tagline'], product["tagline"])
        filled += fill_if_exists(page, ['textarea[name="description"]', 'textarea', '#description'], product["description"])
        filled += fill_if_exists(page, ['input[name="email"]', 'input[type="email"]', '#email'], product["email"])

        screenshot(page, f"uneed_{name.replace(' ', '_')}_filled")

        if filled == 0:
            log_result("Uneed.be", name, "requires_account", "No fillable fields found — likely requires login")
            return

        # Try submit
        submitted = click_if_exists(page, [
            'button[type="submit"]', 'input[type="submit"]',
            'button:has-text("Submit")', 'button:has-text("submit")',
        ])
        if submitted:
            time.sleep(3)
            screenshot(page, f"uneed_{name.replace(' ', '_')}_submitted")
            log_result("Uneed.be", name, "submitted", f"Filled {filled} fields and clicked submit")
        else:
            log_result("Uneed.be", name, "partial", f"Filled {filled} fields but no submit button found")

    except PlaywrightTimeoutError:
        log_result("Uneed.be", name, "error", "Page load timeout")
    except Exception as e:
        log_result("Uneed.be", name, "error", str(e))


# ─── 2. AI Tools Directory ───────────────────────────────────────────────────

def submit_aitoolsdirectory(page, product):
    name = product["name"]
    try:
        page.goto("https://aitoolsdirectory.com", timeout=30000, wait_until="domcontentloaded")
        time.sleep(3)

        # Look for a submit link
        submit_link = None
        for text in ["Submit", "submit", "Add Tool", "Add a Tool", "Submit Tool"]:
            try:
                el = page.get_by_text(text, exact=False).first
                if el:
                    submit_link = el
                    break
            except Exception:
                pass

        if submit_link:
            submit_link.click()
            time.sleep(3)
        else:
            page.goto("https://aitoolsdirectory.com/submit", timeout=30000, wait_until="domcontentloaded")
            time.sleep(3)

        if has_captcha(page):
            screenshot(page, f"aitoolsdir_{name.replace(' ', '_')}_captcha")
            log_result("AI Tools Directory", name, "captcha_blocked", "CAPTCHA detected")
            return

        content = page.content().lower()
        if any(k in content for k in ["sign in", "log in", "login"]) and "submit" not in content:
            screenshot(page, f"aitoolsdir_{name.replace(' ', '_')}_login")
            log_result("AI Tools Directory", name, "requires_account", "Login wall detected")
            return

        filled = 0
        filled += fill_if_exists(page, ['input[name="name"]', 'input[placeholder*="name" i]', '#name', 'input[placeholder*="tool" i]'], name)
        filled += fill_if_exists(page, ['input[name="url"]', 'input[type="url"]', 'input[placeholder*="url" i]', '#url'], product["url"])
        filled += fill_if_exists(page, ['input[name="tagline"]', 'input[placeholder*="tagline" i]', '#tagline', 'input[placeholder*="short" i]'], product["tagline"])
        filled += fill_if_exists(page, ['textarea', 'textarea[name="description"]', '#description'], product["description"])
        filled += fill_if_exists(page, ['input[type="email"]', 'input[name="email"]'], product["email"])

        screenshot(page, f"aitoolsdir_{name.replace(' ', '_')}_filled")

        if filled == 0:
            log_result("AI Tools Directory", name, "requires_account", "No form fields accessible")
            return

        submitted = click_if_exists(page, [
            'button[type="submit"]', 'input[type="submit"]',
            'button:has-text("Submit")', 'button:has-text("Add")',
        ])
        if submitted:
            time.sleep(3)
            screenshot(page, f"aitoolsdir_{name.replace(' ', '_')}_submitted")
            log_result("AI Tools Directory", name, "submitted", f"Filled {filled} fields and clicked submit")
        else:
            log_result("AI Tools Directory", name, "partial", f"Filled {filled} fields but no submit button")

    except PlaywrightTimeoutError:
        log_result("AI Tools Directory", name, "error", "Page load timeout")
    except Exception as e:
        log_result("AI Tools Directory", name, "error", str(e))


# ─── 3. Toolify.ai ──────────────────────────────────────────────────────────

def submit_toolify(page, product):
    name = product["name"]
    try:
        page.goto("https://www.toolify.ai/submit", timeout=30000, wait_until="domcontentloaded")
        time.sleep(4)

        if has_captcha(page):
            screenshot(page, f"toolify_{name.replace(' ', '_')}_captcha")
            log_result("Toolify.ai", name, "captcha_blocked", "CAPTCHA detected")
            return

        content = page.content().lower()
        if any(k in content for k in ["sign in", "log in", "login"]):
            screenshot(page, f"toolify_{name.replace(' ', '_')}_login")
            log_result("Toolify.ai", name, "requires_account", "Login required before submission")
            return

        filled = 0
        filled += fill_if_exists(page, ['input[placeholder*="name" i]', 'input[name="name"]', '#name'], name)
        filled += fill_if_exists(page, ['input[placeholder*="url" i]', 'input[type="url"]', 'input[name="url"]'], product["url"])
        filled += fill_if_exists(page, ['textarea', 'input[placeholder*="description" i]'], product["description"])
        filled += fill_if_exists(page, ['input[type="email"]', 'input[placeholder*="email" i]'], product["email"])

        screenshot(page, f"toolify_{name.replace(' ', '_')}_filled")

        if filled == 0:
            log_result("Toolify.ai", name, "requires_account", "No form fields accessible")
            return

        submitted = click_if_exists(page, [
            'button[type="submit"]', 'input[type="submit"]',
            'button:has-text("Submit")',
        ])
        if submitted:
            time.sleep(3)
            screenshot(page, f"toolify_{name.replace(' ', '_')}_submitted")
            log_result("Toolify.ai", name, "submitted", f"Filled {filled} fields and clicked submit")
        else:
            log_result("Toolify.ai", name, "partial", f"Filled {filled} fields but no submit button")

    except PlaywrightTimeoutError:
        log_result("Toolify.ai", name, "error", "Page load timeout")
    except Exception as e:
        log_result("Toolify.ai", name, "error", str(e))


# ─── 4. AIcyclopedia ────────────────────────────────────────────────────────

def submit_aicyclopedia(page, product):
    name = product["name"]
    try:
        page.goto("https://www.aicyclopedia.com/submit", timeout=30000, wait_until="domcontentloaded")
        time.sleep(4)

        if has_captcha(page):
            screenshot(page, f"aicyclopedia_{name.replace(' ', '_')}_captcha")
            log_result("AIcyclopedia", name, "captcha_blocked", "CAPTCHA detected")
            return

        content = page.content().lower()
        if any(k in content for k in ["sign in", "log in", "login"]):
            screenshot(page, f"aicyclopedia_{name.replace(' ', '_')}_login")
            log_result("AIcyclopedia", name, "requires_account", "Login required")
            return

        filled = 0
        filled += fill_if_exists(page, ['input[name="name"]', 'input[placeholder*="name" i]', '#name'], name)
        filled += fill_if_exists(page, ['input[name="url"]', 'input[type="url"]', 'input[placeholder*="url" i]'], product["url"])
        filled += fill_if_exists(page, ['textarea', 'input[placeholder*="description" i]'], product["description"])
        filled += fill_if_exists(page, ['input[type="email"]', 'input[name="email"]'], product["email"])

        screenshot(page, f"aicyclopedia_{name.replace(' ', '_')}_filled")

        if filled == 0:
            log_result("AIcyclopedia", name, "requires_account", "No form fields accessible")
            return

        submitted = click_if_exists(page, [
            'button[type="submit"]', 'input[type="submit"]',
            'button:has-text("Submit")',
        ])
        if submitted:
            time.sleep(3)
            screenshot(page, f"aicyclopedia_{name.replace(' ', '_')}_submitted")
            log_result("AIcyclopedia", name, "submitted", f"Filled {filled} fields and clicked submit")
        else:
            log_result("AIcyclopedia", name, "partial", f"Filled {filled} fields but no submit button")

    except PlaywrightTimeoutError:
        log_result("AIcyclopedia", name, "error", "Page load timeout")
    except Exception as e:
        log_result("AIcyclopedia", name, "error", str(e))


# ─── 5. OpenFuture.ai ────────────────────────────────────────────────────────

def submit_openfuture(page, product):
    name = product["name"]
    try:
        page.goto("https://openfuture.ai/submit", timeout=30000, wait_until="domcontentloaded")
        time.sleep(4)

        if has_captcha(page):
            screenshot(page, f"openfuture_{name.replace(' ', '_')}_captcha")
            log_result("OpenFuture.ai", name, "captcha_blocked", "CAPTCHA detected")
            return

        content = page.content().lower()
        if any(k in content for k in ["sign in", "log in", "login"]):
            screenshot(page, f"openfuture_{name.replace(' ', '_')}_login")
            log_result("OpenFuture.ai", name, "requires_account", "Login required")
            return

        filled = 0
        filled += fill_if_exists(page, ['input[name="name"]', 'input[placeholder*="name" i]', '#name'], name)
        filled += fill_if_exists(page, ['input[name="url"]', 'input[type="url"]', 'input[placeholder*="url" i]'], product["url"])
        filled += fill_if_exists(page, ['textarea'], product["description"])
        filled += fill_if_exists(page, ['input[type="email"]', 'input[name="email"]'], product["email"])

        screenshot(page, f"openfuture_{name.replace(' ', '_')}_filled")

        if filled == 0:
            log_result("OpenFuture.ai", name, "requires_account", "No form fields accessible")
            return

        submitted = click_if_exists(page, [
            'button[type="submit"]', 'input[type="submit"]',
            'button:has-text("Submit")',
        ])
        if submitted:
            time.sleep(3)
            screenshot(page, f"openfuture_{name.replace(' ', '_')}_submitted")
            log_result("OpenFuture.ai", name, "submitted", f"Filled {filled} fields and clicked submit")
        else:
            log_result("OpenFuture.ai", name, "partial", f"Filled {filled} fields but no submit button")

    except PlaywrightTimeoutError:
        log_result("OpenFuture.ai", name, "error", "Page load timeout")
    except Exception as e:
        log_result("OpenFuture.ai", name, "error", str(e))


# ─── 6. SaaSHub ─────────────────────────────────────────────────────────────

def submit_saashub(page, product):
    name = product["name"]
    try:
        page.goto("https://www.saashub.com/submit", timeout=30000, wait_until="domcontentloaded")
        time.sleep(4)

        if has_captcha(page):
            screenshot(page, f"saashub_{name.replace(' ', '_')}_captcha")
            log_result("SaaSHub", name, "captcha_blocked", "CAPTCHA detected")
            return

        content = page.content().lower()
        if any(k in content for k in ["sign in", "log in", "login", "sign up"]):
            screenshot(page, f"saashub_{name.replace(' ', '_')}_login")
            log_result("SaaSHub", name, "requires_account", "Login/account required")
            return

        filled = 0
        filled += fill_if_exists(page, ['input[name="name"]', 'input[placeholder*="name" i]'], name)
        filled += fill_if_exists(page, ['input[name="url"]', 'input[type="url"]', 'input[placeholder*="url" i]'], product["url"])
        filled += fill_if_exists(page, ['textarea', 'input[placeholder*="description" i]'], product["description"])
        filled += fill_if_exists(page, ['input[type="email"]', 'input[name="email"]'], product["email"])

        screenshot(page, f"saashub_{name.replace(' ', '_')}_filled")

        if filled == 0:
            log_result("SaaSHub", name, "requires_account", "No form fields accessible")
            return

        submitted = click_if_exists(page, [
            'button[type="submit"]', 'input[type="submit"]',
            'button:has-text("Submit")',
        ])
        if submitted:
            time.sleep(3)
            screenshot(page, f"saashub_{name.replace(' ', '_')}_submitted")
            log_result("SaaSHub", name, "submitted", f"Filled {filled} fields and clicked submit")
        else:
            log_result("SaaSHub", name, "partial", f"Filled {filled} fields but no submit button")

    except PlaywrightTimeoutError:
        log_result("SaaSHub", name, "error", "Page load timeout")
    except Exception as e:
        log_result("SaaSHub", name, "error", str(e))


# ─── 7. BetaList ─────────────────────────────────────────────────────────────

def submit_betalist(page, product):
    name = product["name"]
    try:
        page.goto("https://betalist.com/submit", timeout=30000, wait_until="domcontentloaded")
        time.sleep(4)

        if has_captcha(page):
            screenshot(page, f"betalist_{name.replace(' ', '_')}_captcha")
            log_result("BetaList", name, "captcha_blocked", "CAPTCHA detected")
            return

        content = page.content().lower()
        if any(k in content for k in ["sign in", "log in", "login", "sign up", "create account"]):
            screenshot(page, f"betalist_{name.replace(' ', '_')}_login")
            log_result("BetaList", name, "requires_account", "Account required to submit")
            return

        filled = 0
        filled += fill_if_exists(page, ['input[name="startup[name]"]', 'input[name="name"]', 'input[placeholder*="name" i]'], name)
        filled += fill_if_exists(page, ['input[name="startup[website]"]', 'input[name="url"]', 'input[type="url"]'], product["url"])
        filled += fill_if_exists(page, ['textarea[name="startup[tagline]"]', 'input[name="tagline"]', 'input[placeholder*="tagline" i]'], product["tagline"])
        filled += fill_if_exists(page, ['textarea', 'textarea[name="startup[description]"]'], product["description"])
        filled += fill_if_exists(page, ['input[type="email"]', 'input[name="email"]'], product["email"])

        screenshot(page, f"betalist_{name.replace(' ', '_')}_filled")

        if filled == 0:
            log_result("BetaList", name, "requires_account", "No form fields accessible")
            return

        submitted = click_if_exists(page, [
            'button[type="submit"]', 'input[type="submit"]',
            'button:has-text("Submit")', 'button:has-text("Send")',
        ])
        if submitted:
            time.sleep(3)
            screenshot(page, f"betalist_{name.replace(' ', '_')}_submitted")
            log_result("BetaList", name, "submitted", f"Filled {filled} fields and clicked submit")
        else:
            log_result("BetaList", name, "partial", f"Filled {filled} fields but no submit button")

    except PlaywrightTimeoutError:
        log_result("BetaList", name, "error", "Page load timeout")
    except Exception as e:
        log_result("BetaList", name, "error", str(e))


# ─── 8. Launching Next ───────────────────────────────────────────────────────

def submit_launchingnext(page, product):
    name = product["name"]
    try:
        page.goto("https://www.launchingnext.com/submit", timeout=30000, wait_until="domcontentloaded")
        time.sleep(4)

        if has_captcha(page):
            screenshot(page, f"launchingnext_{name.replace(' ', '_')}_captcha")
            log_result("Launching Next", name, "captcha_blocked", "CAPTCHA detected")
            return

        content = page.content().lower()
        if any(k in content for k in ["sign in", "log in", "login"]) and "submit" not in content:
            screenshot(page, f"launchingnext_{name.replace(' ', '_')}_login")
            log_result("Launching Next", name, "requires_account", "Login required")
            return

        filled = 0
        filled += fill_if_exists(page, ['input[name="startup_name"]', 'input[name="name"]', 'input[placeholder*="name" i]', '#startup_name'], name)
        filled += fill_if_exists(page, ['input[name="url"]', 'input[type="url"]', 'input[placeholder*="url" i]'], product["url"])
        filled += fill_if_exists(page, ['input[name="tagline"]', 'input[placeholder*="tagline" i]', 'input[placeholder*="one liner" i]'], product["tagline"])
        filled += fill_if_exists(page, ['textarea', 'textarea[name="description"]'], product["description"])
        filled += fill_if_exists(page, ['input[type="email"]', 'input[name="email"]', 'input[placeholder*="email" i]'], product["email"])

        screenshot(page, f"launchingnext_{name.replace(' ', '_')}_filled")

        if filled == 0:
            log_result("Launching Next", name, "requires_account", "No form fields accessible")
            return

        submitted = click_if_exists(page, [
            'button[type="submit"]', 'input[type="submit"]',
            'button:has-text("Submit")', 'input[value="Submit"]',
        ])
        if submitted:
            time.sleep(3)
            screenshot(page, f"launchingnext_{name.replace(' ', '_')}_submitted")
            log_result("Launching Next", name, "submitted", f"Filled {filled} fields and clicked submit")
        else:
            log_result("Launching Next", name, "partial", f"Filled {filled} fields but no submit button")

    except PlaywrightTimeoutError:
        log_result("Launching Next", name, "error", "Page load timeout")
    except Exception as e:
        log_result("Launching Next", name, "error", str(e))


# ─── Main ────────────────────────────────────────────────────────────────────

DIRECTORY_FUNCS = [
    ("Uneed.be", submit_uneed),
    ("AI Tools Directory", submit_aitoolsdirectory),
    ("Toolify.ai", submit_toolify),
    ("AIcyclopedia", submit_aicyclopedia),
    ("OpenFuture.ai", submit_openfuture),
    ("SaaSHub", submit_saashub),
    ("BetaList", submit_betalist),
    ("Launching Next", submit_launchingnext),
]

start_time = time.time()

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
    )
    context = browser.new_context(
        viewport={"width": 1280, "height": 900},
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    )

    for dir_name, dir_func in DIRECTORY_FUNCS:
        print(f"\n{'='*60}")
        print(f"Directory: {dir_name}")
        print(f"{'='*60}")
        for prod_key, prod_data in PRODUCTS.items():
            print(f"  Submitting: {prod_key}")
            page = context.new_page()
            try:
                dir_func(page, prod_data)
            except Exception as e:
                log_result(dir_name, prod_key, "error", f"Unhandled: {str(e)}")
            finally:
                page.close()
            time.sleep(2)

    browser.close()

elapsed = time.time() - start_time

# ─── Summary ─────────────────────────────────────────────────────────────────

summary = {
    "run_at": datetime.utcnow().isoformat(),
    "elapsed_seconds": round(elapsed, 1),
    "total_attempted": len(results),
    "submitted": [r for r in results if r["status"] == "submitted"],
    "captcha_blocked": [r for r in results if r["status"] == "captcha_blocked"],
    "requires_account": [r for r in results if r["status"] == "requires_account"],
    "errors": [r for r in results if r["status"] == "error"],
    "partial": [r for r in results if r["status"] == "partial"],
    "all_results": results,
}

with open(LOG_FILE, "w") as f:
    json.dump(summary, f, indent=2)

print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
print(f"Total attempted : {summary['total_attempted']}")
print(f"Submitted       : {len(summary['submitted'])}")
print(f"Captcha blocked : {len(summary['captcha_blocked'])}")
print(f"Requires account: {len(summary['requires_account'])}")
print(f"Partial         : {len(summary['partial'])}")
print(f"Errors          : {len(summary['errors'])}")
print(f"Elapsed         : {elapsed:.1f}s")
print(f"\nLog saved to: {LOG_FILE}")
