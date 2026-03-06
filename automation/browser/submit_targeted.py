#!/usr/bin/env python3
"""
Targeted submission script for directories with real forms.
Based on investigation results.
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


# ─── AIcyclopedia (multi-step form) ─────────────────────────────────────────

def submit_aicyclopedia(page, product):
    name = product["name"]
    safe = name.replace(" ", "_")
    try:
        page.goto("https://aicyclopedia.com/submit-your-ai-tool/", timeout=30000, wait_until="domcontentloaded")
        time.sleep(4)

        screenshot(page, f"aicyclopedia2_{safe}_step1_before")

        # Step 1: Tool Name, Tagline, Category, Website
        # Tool Name
        name_field = page.query_selector('input[name="form_fields[name]"]')
        if name_field and name_field.is_visible():
            name_field.fill(product["name"])

        # Tagline
        tagline_field = page.query_selector('input[name="form_fields[field_18f75f2]"]')
        if tagline_field and tagline_field.is_visible():
            tagline_field.fill(product["tagline"])

        # Category dropdown
        cat_select = page.query_selector('select[name="form_fields[field_65f5ab7]"]')
        if cat_select and cat_select.is_visible():
            # Try to select a relevant option
            options = cat_select.query_selector_all("option")
            option_texts = []
            for opt in options:
                txt = opt.inner_text().strip()
                option_texts.append(txt)
            print(f"    Category options: {option_texts[:10]}")
            
            # Pick best option
            keywords = ["AI", "Productivity", "Business", "Tools", "SaaS", "Food"]
            selected = False
            for kw in keywords:
                for opt in options:
                    txt = opt.inner_text().strip()
                    if kw.lower() in txt.lower() and txt:
                        val = opt.get_attribute("value")
                        if val:
                            cat_select.select_option(value=val)
                            selected = True
                            print(f"    Selected category: {txt}")
                            break
                if selected:
                    break
            if not selected and len(options) > 1:
                val = options[1].get_attribute("value")
                if val:
                    cat_select.select_option(value=val)

        # Website
        url_field = page.query_selector('input[name="form_fields[field_34b2203]"]')
        if url_field and url_field.is_visible():
            url_field.fill(product["url"])

        screenshot(page, f"aicyclopedia2_{safe}_step1_filled")

        # Click NEXT
        next_btn = page.query_selector('button:has-text("NEXT")')
        if not next_btn:
            next_btn = page.get_by_role("button", name="NEXT")
        if next_btn and next_btn.is_visible():
            next_btn.click()
            time.sleep(3)
            screenshot(page, f"aicyclopedia2_{safe}_step2")
        else:
            log_result("AIcyclopedia", name, "partial", "Step 1 filled but NEXT button not found")
            return

        # Step 2: Description and optional fields
        desc_field = page.query_selector('textarea[name="form_fields[field_0ae884c]"]')
        if desc_field:
            desc_field.scroll_into_view_if_needed()
            desc_field.fill(product["description"])

        # Email (if visible)
        email_field = page.query_selector('input[name="form_fields[field_2dac996]"]')
        if email_field:
            email_field.scroll_into_view_if_needed()
            if email_field.is_visible():
                email_field.fill(product["email"])

        screenshot(page, f"aicyclopedia2_{safe}_step2_filled")

        # Click NEXT again or look for Send
        next_btn2 = page.query_selector('button:has-text("NEXT")')
        if next_btn2 and next_btn2.is_visible():
            next_btn2.click()
            time.sleep(3)
            screenshot(page, f"aicyclopedia2_{safe}_step3")

        # Look for Send button
        send_btn = page.query_selector('button:has-text("Send")')
        if send_btn and send_btn.is_visible():
            # Check for CAPTCHA before submitting
            content = page.content().lower()
            if "recaptcha" in content or "hcaptcha" in content:
                screenshot(page, f"aicyclopedia2_{safe}_captcha_prefinal")
                log_result("AIcyclopedia", name, "captcha_blocked", "CAPTCHA on final step — form filled through step 2, captcha on submit")
                return
            send_btn.click()
            time.sleep(4)
            screenshot(page, f"aicyclopedia2_{safe}_submitted")
            final_content = page.content().lower()
            if any(k in final_content for k in ["thank", "success", "submitted", "received"]):
                log_result("AIcyclopedia", name, "submitted", "Form fully submitted — success message detected")
            else:
                log_result("AIcyclopedia", name, "submitted_unconfirmed", "Clicked Send but no explicit success message")
        else:
            content = page.content().lower()
            if "recaptcha" in content or "hcaptcha" in content:
                screenshot(page, f"aicyclopedia2_{safe}_captcha_final")
                log_result("AIcyclopedia", name, "captcha_blocked", "CAPTCHA blocking final submit button")
            else:
                screenshot(page, f"aicyclopedia2_{safe}_no_send")
                log_result("AIcyclopedia", name, "partial", "Filled steps 1-2 but no Send button found")

    except PlaywrightTimeoutError:
        log_result("AIcyclopedia", name, "error", "Page load timeout")
    except Exception as e:
        log_result("AIcyclopedia", name, "error", str(e))


# ─── Additional directories to try ──────────────────────────────────────────

def submit_futurepedia(page, product):
    """Futurepedia.io - large AI tools directory"""
    name = product["name"]
    safe = name.replace(" ", "_")
    try:
        page.goto("https://www.futurepedia.io/submit-tool", timeout=30000, wait_until="domcontentloaded")
        time.sleep(4)
        screenshot(page, f"futurepedia_{safe}_landing")

        content = page.content().lower()
        if any(k in content for k in ["sign in", "log in", "login", "sign up"]):
            screenshot(page, f"futurepedia_{safe}_login")
            log_result("Futurepedia.io", name, "requires_account", "Login required")
            return
        if "recaptcha" in content or "hcaptcha" in content or "captcha" in content:
            screenshot(page, f"futurepedia_{safe}_captcha")
            log_result("Futurepedia.io", name, "captcha_blocked", "CAPTCHA on page")
            return

        inputs = page.query_selector_all("input:visible, textarea:visible")
        if len(inputs) == 0:
            log_result("Futurepedia.io", name, "requires_account", "No visible form fields")
            return

        filled = 0
        for sel, val in [
            (['input[name="name"]', 'input[placeholder*="name" i]'], product["name"]),
            (['input[name="url"]', 'input[type="url"]', 'input[placeholder*="url" i]', 'input[placeholder*="link" i]'], product["url"]),
            (['textarea', 'input[placeholder*="description" i]'], product["description"]),
            (['input[type="email"]', 'input[name="email"]'], product["email"]),
        ]:
            for s in sel:
                try:
                    el = page.query_selector(s)
                    if el and el.is_visible():
                        el.fill(val)
                        filled += 1
                        break
                except Exception:
                    pass

        screenshot(page, f"futurepedia_{safe}_filled")
        if filled == 0:
            log_result("Futurepedia.io", name, "requires_account", "No fillable fields")
            return

        for btn_sel in ['button[type="submit"]', 'button:has-text("Submit")', 'input[type="submit"]']:
            try:
                btn = page.query_selector(btn_sel)
                if btn and btn.is_visible():
                    btn.click()
                    time.sleep(3)
                    screenshot(page, f"futurepedia_{safe}_submitted")
                    log_result("Futurepedia.io", name, "submitted", f"Filled {filled} fields and clicked submit")
                    return
            except Exception:
                pass
        log_result("Futurepedia.io", name, "partial", f"Filled {filled} fields but no submit button")

    except PlaywrightTimeoutError:
        log_result("Futurepedia.io", name, "error", "Timeout")
    except Exception as e:
        log_result("Futurepedia.io", name, "error", str(e))


def submit_theresanaiforthat(page, product):
    """There's An AI For That"""
    name = product["name"]
    safe = name.replace(" ", "_")
    try:
        page.goto("https://theresanaiforthat.com/get-listed/", timeout=30000, wait_until="domcontentloaded")
        time.sleep(4)
        screenshot(page, f"theresanai_{safe}_landing")

        content = page.content().lower()
        if any(k in content for k in ["sign in", "log in", "login"]):
            log_result("TAAFT", name, "requires_account", "Login required")
            return
        if "captcha" in content:
            log_result("TAAFT", name, "captcha_blocked", "CAPTCHA detected")
            return

        inputs = page.query_selector_all("input:visible, textarea:visible")
        if len(inputs) == 0:
            log_result("TAAFT", name, "requires_account", "No visible form fields")
            return

        filled = 0
        for sel, val in [
            (['input[name="name"]', 'input[placeholder*="name" i]'], product["name"]),
            (['input[name="url"]', 'input[type="url"]', 'input[placeholder*="url" i]'], product["url"]),
            (['textarea'], product["description"]),
            (['input[type="email"]'], product["email"]),
        ]:
            for s in sel:
                try:
                    el = page.query_selector(s)
                    if el and el.is_visible():
                        el.fill(val)
                        filled += 1
                        break
                except Exception:
                    pass

        screenshot(page, f"theresanai_{safe}_filled")
        if filled == 0:
            log_result("TAAFT", name, "requires_account", "No fillable fields")
            return

        for btn_sel in ['button[type="submit"]', 'button:has-text("Submit")', 'input[type="submit"]']:
            try:
                btn = page.query_selector(btn_sel)
                if btn and btn.is_visible():
                    btn.click()
                    time.sleep(3)
                    screenshot(page, f"theresanai_{safe}_submitted")
                    log_result("TAAFT", name, "submitted", f"Filled {filled} fields and clicked submit")
                    return
            except Exception:
                pass
        log_result("TAAFT", name, "partial", f"Filled {filled} fields but no submit button")

    except PlaywrightTimeoutError:
        log_result("TAAFT", name, "error", "Timeout")
    except Exception as e:
        log_result("TAAFT", name, "error", str(e))


def submit_aitoptools(page, product):
    """AI Top Tools"""
    name = product["name"]
    safe = name.replace(" ", "_")
    try:
        page.goto("https://aitoptools.com/submit-tool/", timeout=30000, wait_until="domcontentloaded")
        time.sleep(4)
        screenshot(page, f"aitoptools_{safe}_landing")

        content = page.content().lower()
        if any(k in content for k in ["sign in", "log in", "login"]):
            log_result("AI Top Tools", name, "requires_account", "Login required")
            return
        if "captcha" in content:
            log_result("AI Top Tools", name, "captcha_blocked", "CAPTCHA detected")
            return

        inputs = page.query_selector_all("input:visible, textarea:visible")
        if len(inputs) == 0:
            log_result("AI Top Tools", name, "requires_account", "No visible form fields")
            return

        filled = 0
        for sel, val in [
            (['input[name="tool_name"]', 'input[name="name"]', 'input[placeholder*="name" i]'], product["name"]),
            (['input[name="tool_url"]', 'input[name="url"]', 'input[type="url"]'], product["url"]),
            (['input[name="short_description"]', 'input[placeholder*="tagline" i]', 'input[placeholder*="short" i]'], product["tagline"]),
            (['textarea[name="description"]', 'textarea'], product["description"]),
            (['input[type="email"]', 'input[name="email"]'], product["email"]),
        ]:
            for s in sel:
                try:
                    el = page.query_selector(s)
                    if el and el.is_visible():
                        el.fill(val)
                        filled += 1
                        break
                except Exception:
                    pass

        screenshot(page, f"aitoptools_{safe}_filled")
        if filled == 0:
            log_result("AI Top Tools", name, "requires_account", "No fillable fields")
            return

        for btn_sel in ['button[type="submit"]', 'button:has-text("Submit")', 'input[type="submit"]']:
            try:
                btn = page.query_selector(btn_sel)
                if btn and btn.is_visible():
                    btn.click()
                    time.sleep(3)
                    screenshot(page, f"aitoptools_{safe}_submitted")
                    log_result("AI Top Tools", name, "submitted", f"Filled {filled} fields and clicked submit")
                    return
            except Exception:
                pass
        log_result("AI Top Tools", name, "partial", f"Filled {filled} fields but no submit button")

    except PlaywrightTimeoutError:
        log_result("AI Top Tools", name, "error", "Timeout")
    except Exception as e:
        log_result("AI Top Tools", name, "error", str(e))


def submit_aitoolsguide(page, product):
    """AI Tools Guide - free listing"""
    name = product["name"]
    safe = name.replace(" ", "_")
    try:
        page.goto("https://aitoolsguide.com/submit-ai-tool/", timeout=30000, wait_until="domcontentloaded")
        time.sleep(4)
        screenshot(page, f"aitoolsguide_{safe}_landing")

        content = page.content().lower()
        if any(k in content for k in ["sign in", "log in", "login"]):
            log_result("AI Tools Guide", name, "requires_account", "Login required")
            return
        if "captcha" in content:
            log_result("AI Tools Guide", name, "captcha_blocked", "CAPTCHA detected")
            return

        inputs = page.query_selector_all("input:visible, textarea:visible")
        if len(inputs) == 0:
            log_result("AI Tools Guide", name, "requires_account", "No visible form fields")
            return

        filled = 0
        for sel, val in [
            (['input[name="name"]', 'input[placeholder*="name" i]', 'input[placeholder*="tool" i]'], product["name"]),
            (['input[name="url"]', 'input[type="url"]', 'input[placeholder*="url" i]', 'input[placeholder*="website" i]'], product["url"]),
            (['textarea', 'input[placeholder*="description" i]'], product["description"]),
            (['input[type="email"]'], product["email"]),
        ]:
            for s in sel:
                try:
                    el = page.query_selector(s)
                    if el and el.is_visible():
                        el.fill(val)
                        filled += 1
                        break
                except Exception:
                    pass

        screenshot(page, f"aitoolsguide_{safe}_filled")
        if filled == 0:
            log_result("AI Tools Guide", name, "requires_account", "No fillable fields")
            return

        for btn_sel in ['button[type="submit"]', 'button:has-text("Submit")', 'input[type="submit"]', 'input[value*="Submit" i]']:
            try:
                btn = page.query_selector(btn_sel)
                if btn and btn.is_visible():
                    btn.click()
                    time.sleep(3)
                    screenshot(page, f"aitoolsguide_{safe}_submitted")
                    log_result("AI Tools Guide", name, "submitted", f"Filled {filled} fields and clicked submit")
                    return
            except Exception:
                pass
        log_result("AI Tools Guide", name, "partial", f"Filled {filled} fields but no submit button")

    except PlaywrightTimeoutError:
        log_result("AI Tools Guide", name, "error", "Timeout")
    except Exception as e:
        log_result("AI Tools Guide", name, "error", str(e))


def submit_producthunt_check(page, product):
    """Check Product Hunt submit page"""
    name = product["name"]
    safe = name.replace(" ", "_")
    try:
        page.goto("https://www.producthunt.com/posts/new", timeout=30000, wait_until="domcontentloaded")
        time.sleep(4)
        screenshot(page, f"producthunt_{safe}_landing")
        content = page.content().lower()
        if any(k in content for k in ["sign in", "log in", "login", "sign up"]):
            log_result("Product Hunt", name, "requires_account", "Login required (expected)")
        elif "captcha" in content:
            log_result("Product Hunt", name, "captcha_blocked", "CAPTCHA")
        else:
            inputs = page.query_selector_all("input:visible, textarea:visible")
            log_result("Product Hunt", name, "requires_account", f"Page loaded but form state unclear — {len(inputs)} inputs visible")
    except Exception as e:
        log_result("Product Hunt", name, "error", str(e))


def submit_startupstash(page, product):
    """Startup Stash submit"""
    name = product["name"]
    safe = name.replace(" ", "_")
    try:
        page.goto("https://startupstash.com/add-listing/", timeout=30000, wait_until="domcontentloaded")
        time.sleep(4)
        screenshot(page, f"startupstash_{safe}_landing")

        content = page.content().lower()
        if any(k in content for k in ["sign in", "log in", "login"]):
            log_result("Startup Stash", name, "requires_account", "Login required")
            return
        if "captcha" in content:
            log_result("Startup Stash", name, "captcha_blocked", "CAPTCHA")
            return

        inputs = page.query_selector_all("input:visible, textarea:visible")
        if len(inputs) == 0:
            log_result("Startup Stash", name, "requires_account", "No visible form fields")
            return

        filled = 0
        for sel, val in [
            (['input[name="name"]', 'input[placeholder*="name" i]'], product["name"]),
            (['input[name="url"]', 'input[type="url"]'], product["url"]),
            (['textarea'], product["description"]),
            (['input[type="email"]'], product["email"]),
        ]:
            for s in sel:
                try:
                    el = page.query_selector(s)
                    if el and el.is_visible():
                        el.fill(val)
                        filled += 1
                        break
                except Exception:
                    pass

        screenshot(page, f"startupstash_{safe}_filled")
        if filled == 0:
            log_result("Startup Stash", name, "requires_account", "No fillable fields")
            return

        for btn_sel in ['button[type="submit"]', 'button:has-text("Submit")', 'input[type="submit"]']:
            try:
                btn = page.query_selector(btn_sel)
                if btn and btn.is_visible():
                    btn.click()
                    time.sleep(3)
                    screenshot(page, f"startupstash_{safe}_submitted")
                    log_result("Startup Stash", name, "submitted", f"Filled {filled} fields and submitted")
                    return
            except Exception:
                pass
        log_result("Startup Stash", name, "partial", f"Filled {filled} fields but no submit button")

    except PlaywrightTimeoutError:
        log_result("Startup Stash", name, "error", "Timeout")
    except Exception as e:
        log_result("Startup Stash", name, "error", str(e))


# ─── Main ────────────────────────────────────────────────────────────────────

DIRECTORY_FUNCS = [
    ("AIcyclopedia", submit_aicyclopedia),
    ("Futurepedia.io", submit_futurepedia),
    ("TAAFT", submit_theresanaiforthat),
    ("AI Top Tools", submit_aitoptools),
    ("AI Tools Guide", submit_aitoolsguide),
    ("Startup Stash", submit_startupstash),
]

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

# ─── Merge with existing log ─────────────────────────────────────────────────

try:
    with open(LOG_FILE, "r") as f:
        existing = json.load(f)
except Exception:
    existing = {"all_results": []}

all_results = existing.get("all_results", []) + new_results

# Update summary
summary = {
    "run_at": datetime.now(timezone.utc).isoformat(),
    "elapsed_seconds_round2": round(elapsed, 1),
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
print("ROUND 2 SUMMARY (new + previous combined)")
print(f"{'='*60}")
print(f"Total attempted  : {summary['total_attempted']}")
print(f"Submitted        : {len(summary['submitted'])}")
print(f"Submitted (unconf): {len(summary['submitted_unconfirmed'])}")
print(f"Captcha blocked  : {len(summary['captcha_blocked'])}")
print(f"Requires account : {len(summary['requires_account'])}")
print(f"Partial          : {len(summary['partial'])}")
print(f"Errors           : {len(summary['errors'])}")
print(f"Elapsed (this run): {elapsed:.1f}s")
print(f"\nLog saved to: {LOG_FILE}")
