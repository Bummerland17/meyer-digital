#!/usr/bin/env python3
"""
AIcyclopedia specific submission + scan more directories.
"""

import json
import time
import os
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

SCREENSHOTS_DIR = "/root/.openclaw/workspace/automation/screenshots"
LOG_FILE = "/root/.openclaw/workspace/automation/submission-log-round2.json"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

PRODUCTS = {
    "PantryMate": {
        "url": "https://pantrymate.net",
        "tagline": "Type what's in your fridge, get dinner in 30 seconds",
        "description": "AI-powered pantry-to-meal decision engine. Eliminates dinner decision paralysis — type your ingredients, get personalized dinner ideas instantly. No more staring at a full fridge and ordering takeout.",
        "category": "FREEMIUM",
        "email": "hello@pantrymate.net",
        "name": "PantryMate",
    },
    "SmartBook AI": {
        "url": "https://bummerland17.github.io/smartbook-ai/",
        "tagline": "AI phone agent that books appointments 24/7",
        "description": "SmartBook AI answers every call after hours, books appointments directly into your calendar, and sends SMS confirmations. $497/month flat. No contracts.",
        "category": "PAID",
        "email": "hello@pantrymate.net",
        "name": "SmartBook AI",
    },
}

new_results = []

def log_result(directory, product, status, notes=""):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "directory": directory,
        "product": product,
        "status": status,
        "notes": notes,
    }
    new_results.append(entry)
    print(f"[{status.upper()}] {directory} — {product}: {notes}")


def screenshot(page, name):
    path = os.path.join(SCREENSHOTS_DIR, f"{name}.png")
    try:
        page.screenshot(path=path, full_page=True)
    except Exception:
        page.screenshot(path=path)
    return path


def submit_aicyclopedia_v2(page, product):
    """AIcyclopedia multi-step form with proper wait handling."""
    name = product["name"]
    safe = name.replace(" ", "_")
    try:
        page.goto("https://aicyclopedia.com/submit-your-ai-tool/", timeout=30000, wait_until="domcontentloaded")
        time.sleep(5)
        screenshot(page, f"aic3_{safe}_step1_start")

        # Fill Step 1 visible fields
        # Tool Name
        try:
            page.fill('input[name="form_fields[name]"]', product["name"])
            print(f"  Filled Tool Name: {product['name']}")
        except Exception as e:
            print(f"  Name field error: {e}")

        # Tagline
        try:
            page.fill('input[name="form_fields[field_18f75f2]"]', product["tagline"])
            print(f"  Filled Tagline")
        except Exception as e:
            print(f"  Tagline field error: {e}")

        # Category
        try:
            page.select_option('select[name="form_fields[field_65f5ab7]"]', label=product["category"])
            print(f"  Selected category: {product['category']}")
        except Exception as e:
            try:
                page.select_option('select[name="form_fields[field_65f5ab7]"]', index=1)
                print(f"  Selected category by index")
            except Exception as e2:
                print(f"  Category select error: {e2}")

        # Website URL
        try:
            page.fill('input[name="form_fields[field_34b2203]"]', product["url"])
            print(f"  Filled Website URL")
        except Exception as e:
            print(f"  URL field error: {e}")

        screenshot(page, f"aic3_{safe}_step1_filled")

        # Click NEXT — expect a JS state change, not full page navigation
        print(f"  Clicking NEXT...")
        try:
            next_btn = page.locator('button:has-text("NEXT")').first
            next_btn.scroll_into_view_if_needed()
            next_btn.click()
            # Wait for DOM change (next step content), not full page load
            page.wait_for_timeout(4000)
            screenshot(page, f"aic3_{safe}_step2_loaded")
        except PlaywrightTimeoutError:
            screenshot(page, f"aic3_{safe}_next_timeout")
            log_result("AIcyclopedia", name, "partial", "NEXT button click triggered timeout")
            return
        except Exception as e:
            print(f"  NEXT error: {e}")
            screenshot(page, f"aic3_{safe}_next_error")

        # Step 2 - fill description and email (scroll down to find them)
        print("  Filling step 2 fields...")
        page.evaluate("window.scrollTo(0, 500)")
        time.sleep(1)

        try:
            desc = page.locator('textarea[name="form_fields[field_0ae884c]"]').first
            if desc.count() > 0:
                desc.scroll_into_view_if_needed()
                desc.fill(product["description"])
                print("  Filled description")
        except Exception as e:
            print(f"  Description error: {e}")

        try:
            email = page.locator('input[name="form_fields[field_2dac996]"]').first
            if email.count() > 0:
                email.scroll_into_view_if_needed()
                email.fill(product["email"])
                print("  Filled email")
        except Exception as e:
            print(f"  Email error: {e}")

        screenshot(page, f"aic3_{safe}_step2_filled")

        # Click NEXT again if present, else look for Send
        try:
            next_btn2 = page.locator('button:has-text("NEXT")').first
            if next_btn2.is_visible():
                next_btn2.click()
                page.wait_for_timeout(3000)
                screenshot(page, f"aic3_{safe}_step3")
                print("  Clicked NEXT for step 3")
        except Exception:
            pass

        # Final: look for Send button
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
        screenshot(page, f"aic3_{safe}_before_send")

        try:
            send_btn = page.locator('button:has-text("Send")').first
            if send_btn.is_visible():
                # Check for CAPTCHA in current visible area
                content = page.content().lower()
                if "recaptcha" in content and "g-recaptcha-response" in content:
                    screenshot(page, f"aic3_{safe}_recaptcha_present")
                    log_result("AIcyclopedia", name, "captcha_blocked",
                               "reCAPTCHA required for final Send — form filled through all steps")
                else:
                    send_btn.click()
                    page.wait_for_timeout(4000)
                    screenshot(page, f"aic3_{safe}_after_send")
                    final_content = page.content().lower()
                    if any(k in final_content for k in ["thank", "success", "submitted", "received", "we'll review"]):
                        log_result("AIcyclopedia", name, "submitted", "Form submitted — success confirmed")
                    else:
                        log_result("AIcyclopedia", name, "submitted_unconfirmed", "Clicked Send — no clear success/fail message")
            else:
                screenshot(page, f"aic3_{safe}_no_send_visible")
                log_result("AIcyclopedia", name, "partial", "All steps filled but Send button not visible (captcha or step gating)")
        except Exception as e:
            log_result("AIcyclopedia", name, "partial", f"All fields filled; Send click error: {e}")

    except PlaywrightTimeoutError:
        log_result("AIcyclopedia", name, "error", "Initial page load timeout")
    except Exception as e:
        log_result("AIcyclopedia", name, "error", str(e))


# ─── More directories to probe ───────────────────────────────────────────────

PROBE_URLS = [
    ("Toolscout.ai", "https://toolscout.ai/submit"),
    ("AI Finder", "https://ai-finder.net/submit"),
    ("NerdyNav", "https://nerdynav.com/submit-an-ai-tool/"),
    ("AI Tools FYI", "https://aitools.fyi/submit"),
    ("GPT Forge", "https://gptforge.net/submit"),
    ("AI Tool Hunt", "https://aitoolhunt.com/submit"),
    ("PoweredByAI", "https://poweredbyai.app/submit"),
    ("Supertools", "https://supertools.therundown.ai/submit"),
]

def probe_and_submit(page, dir_name, url, product):
    name = product["name"]
    safe = name.replace(" ", "_")
    dir_safe = dir_name.replace(" ", "_").replace(".", "")
    try:
        page.goto(url, timeout=25000, wait_until="domcontentloaded")
        time.sleep(4)

        content = page.content().lower()
        url_final = page.url

        # Check if redirected to login
        if any(k in url_final.lower() for k in ["login", "signin", "sign-in", "auth"]):
            log_result(dir_name, name, "requires_account", f"Redirected to login: {url_final}")
            return

        if any(k in content for k in ["sign in to submit", "login to submit", "you must be logged"]):
            log_result(dir_name, name, "requires_account", "Explicit login-required message")
            return

        inputs = page.query_selector_all("input[type='text']:visible, input[type='url']:visible, input[type='email']:visible, textarea:visible")

        if len(inputs) < 2:
            screenshot(page, f"{dir_safe}_{safe}_landing")
            if any(k in content for k in ["sign in", "log in", "login", "sign up", "create account"]):
                log_result(dir_name, name, "requires_account", f"Login wall — {len(inputs)} visible inputs")
            elif "captcha" in content or "hcaptcha" in content:
                log_result(dir_name, name, "captcha_blocked", "CAPTCHA detected")
            elif "404" in page.title().lower() or "not found" in page.title().lower():
                log_result(dir_name, name, "error", "404 page not found")
            else:
                log_result(dir_name, name, "requires_account", f"Only {len(inputs)} visible inputs — likely gated")
            return

        # Has form fields — try to fill
        screenshot(page, f"{dir_safe}_{safe}_form")

        filled = 0
        for selectors, val in [
            (['input[name="name"]', 'input[placeholder*="name" i]', 'input[placeholder*="tool" i]', 'input[id*="name" i]'], product["name"]),
            (['input[name="url"]', 'input[type="url"]', 'input[placeholder*="url" i]', 'input[placeholder*="website" i]', 'input[placeholder*="link" i]'], product["url"]),
            (['input[placeholder*="tagline" i]', 'input[placeholder*="short" i]', 'input[placeholder*="one line" i]'], product["tagline"]),
            (['textarea', 'input[placeholder*="description" i]'], product["description"]),
            (['input[type="email"]', 'input[name="email"]', 'input[placeholder*="email" i]'], product["email"]),
        ]:
            for sel in selectors:
                try:
                    el = page.query_selector(sel)
                    if el and el.is_visible():
                        el.fill(val)
                        filled += 1
                        break
                except Exception:
                    pass

        if filled < 1:
            log_result(dir_name, name, "requires_account", "Form fields not fillable")
            return

        screenshot(page, f"{dir_safe}_{safe}_filled")

        # Try to submit
        for btn_sel in [
            'button[type="submit"]', 'input[type="submit"]',
            'button:has-text("Submit")', 'button:has-text("Add")',
            'button:has-text("Send")', 'input[value*="Submit" i]',
        ]:
            try:
                btn = page.query_selector(btn_sel)
                if btn and btn.is_visible():
                    btn.click()
                    page.wait_for_timeout(3000)
                    screenshot(page, f"{dir_safe}_{safe}_submitted")
                    final_content = page.content().lower()
                    if any(k in final_content for k in ["thank", "success", "submitted", "received"]):
                        log_result(dir_name, name, "submitted", f"Filled {filled} fields — success message seen")
                    else:
                        log_result(dir_name, name, "submitted_unconfirmed", f"Filled {filled} fields — clicked submit, no clear confirmation")
                    return
            except Exception:
                pass

        log_result(dir_name, name, "partial", f"Filled {filled} fields but no clickable submit button")

    except PlaywrightTimeoutError:
        log_result(dir_name, name, "error", "Timeout loading page")
    except Exception as e:
        log_result(dir_name, name, "error", str(e))


# ─── Run ─────────────────────────────────────────────────────────────────────

start_time = time.time()

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--ignore-certificate-errors", "--disable-dev-shm-usage"],
    )
    context = browser.new_context(
        viewport={"width": 1280, "height": 900},
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        ignore_https_errors=True,
    )

    # AIcyclopedia targeted
    print("\n" + "="*60)
    print("AIcyclopedia v2")
    print("="*60)
    for prod_key, prod_data in PRODUCTS.items():
        print(f"\n  Product: {prod_key}")
        page = context.new_page()
        try:
            submit_aicyclopedia_v2(page, prod_data)
        except Exception as e:
            log_result("AIcyclopedia", prod_key, "error", str(e))
        finally:
            page.close()
        time.sleep(2)

    # Probe additional directories
    print("\n" + "="*60)
    print("Probing additional directories")
    print("="*60)
    for dir_name, dir_url in PROBE_URLS:
        for prod_key, prod_data in PRODUCTS.items():
            print(f"\n  {dir_name} — {prod_key}")
            page = context.new_page()
            try:
                probe_and_submit(page, dir_name, dir_url, prod_data)
            except Exception as e:
                log_result(dir_name, prod_key, "error", str(e))
            finally:
                page.close()
            time.sleep(1)

    browser.close()

elapsed = time.time() - start_time

# Merge with existing log
try:
    with open(LOG_FILE, "r") as f:
        existing = json.load(f)
except Exception:
    existing = {"all_results": []}

all_results = existing.get("all_results", []) + new_results

summary = {
    "run_at": datetime.now(timezone.utc).isoformat(),
    "total_attempted": len(all_results),
    "submitted": [r for r in all_results if r["status"] == "submitted"],
    "submitted_unconfirmed": [r for r in all_results if r["status"] == "submitted_unconfirmed"],
    "captcha_blocked": [r for r in all_results if r["status"] == "captcha_blocked"],
    "requires_account": [r for r in all_results if r["status"] == "requires_account"],
    "errors": [r for r in all_results if r["status"] == "error"],
    "partial": [r for r in all_results if r["status"] == "partial"],
    "all_results": all_results,
}

with open(LOG_FILE, "w") as f:
    json.dump(summary, f, indent=2)

print(f"\n{'='*60}")
print("FINAL COMBINED SUMMARY")
print(f"{'='*60}")
print(f"Total attempted   : {summary['total_attempted']}")
print(f"Submitted         : {len(summary['submitted'])}")
print(f"Submitted (unconf): {len(summary['submitted_unconfirmed'])}")
print(f"Captcha blocked   : {len(summary['captcha_blocked'])}")
print(f"Requires account  : {len(summary['requires_account'])}")
print(f"Partial           : {len(summary['partial'])}")
print(f"Errors            : {len(summary['errors'])}")
print(f"This run elapsed  : {elapsed:.1f}s")

if summary['submitted']:
    print("\n✅ Successfully submitted:")
    for r in summary['submitted']:
        print(f"  - {r['directory']} / {r['product']}")
if summary['submitted_unconfirmed']:
    print("\n⚠️ Submitted (unconfirmed):")
    for r in summary['submitted_unconfirmed']:
        print(f"  - {r['directory']} / {r['product']}")
if summary['captcha_blocked']:
    print("\n🔒 CAPTCHA (needs manual):")
    for r in summary['captcha_blocked']:
        print(f"  - {r['directory']} / {r['product']}")
if summary['requires_account']:
    print("\n👤 Requires account (manual login needed):")
    for r in summary['requires_account']:
        print(f"  - {r['directory']} / {r['product']}")
