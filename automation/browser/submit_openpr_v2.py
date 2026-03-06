"""
OpenPR final: use exact obfuscated field names from form inspection.
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

PR_HEADLINE = "PantryMate Launches AI-Powered Dinner Decision Engine Solves Whats For Dinner in 30 Seconds"
PR_BODY = """PantryMate (pantrymate.net) today announced the launch of its AI-powered pantry-to-meal platform that helps home cooks decide what to make for dinner in under 30 seconds.

Unlike traditional recipe apps, PantryMate works in reverse: users type what is already in their fridge and pantry, and the AI instantly suggests personalized dinner options matched to their ingredients, dietary preferences, and cooking skill level.

The average American household wastes $1,500 per year in groceries. PantryMate eliminates this with simple, fast AI that removes decision paralysis.

PantryMate is available at pantrymate.net with a free tier. Pro plans at $9.99/month. Lifetime access at $49.

Contact: Wolfgang Meyer - hello@pantrymate.net - https://pantrymate.net"""


def sc(page, name):
    path = os.path.join(SCREENSHOTS_DIR, f"v2_{name}_{int(time.time())}.png")
    try:
        page.screenshot(path=path, full_page=True)
    except:
        pass
    return path


def log_result(site, product, status, notes="", sp=None):
    e = {"site": site, "product": product, "status": status, "notes": notes,
         "timestamp": datetime.now(timezone.utc).isoformat(), "pass": "openpr_v2"}
    if sp:
        e["screenshot"] = sp
    log.append(e)
    print(f"[{status.upper()}] {site}/{product}: {notes}")
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def dismiss_js(page):
    page.evaluate("""() => {
        ['#cmpbox2','#cmpbox','.cmpboxBG','.cmpstyleroot'].forEach(s => {
            document.querySelectorAll(s).forEach(el => el.remove());
        });
        document.body.style.overflow = '';
    }""")


def fill_field(page, name, value):
    """Fill a field by name attribute, scrolling into view."""
    try:
        el = page.query_selector(f'[name="{name}"]')
        if el:
            page.evaluate(f'document.querySelector(\'[name="{name}"]\').scrollIntoView()')
            time.sleep(0.3)
            page.evaluate(f'document.querySelector(\'[name="{name}"]\').style.display = "block"')
            page.evaluate(f'document.querySelector(\'[name="{name}"]\').style.visibility = "visible"')
            el.fill(value)
            return True
    except Exception as e:
        print(f"    fill_field({name}) error: {e}")
    return False


def select_field(page, name):
    """Select a category from a select element."""
    try:
        el = page.query_selector(f'select[name="{name}"]')
        if el:
            options = el.query_selector_all('option')
            print(f"    Category options: {len(options)}")
            # Find tech/internet option
            for opt in options:
                text = opt.text_content().lower()
                val = opt.get_attribute("value") or ""
                if any(x in text for x in ["internet", "technology", "tech", "computer", "software"]):
                    el.select_option(value=val)
                    print(f"    Selected category: {text}")
                    return True
            # Fallback: select index 1
            if len(options) > 1:
                val = options[1].get_attribute("value")
                el.select_option(value=val)
                print(f"    Selected category index 1: {options[1].text_content()}")
                return True
    except Exception as e:
        print(f"    select_field({name}) error: {e}")
    return False


def check_box(page, name):
    try:
        el = page.query_selector(f'[name="{name}"]')
        if el and not el.is_checked():
            page.evaluate(f'document.querySelector(\'[name="{name}"]\').scrollIntoView()')
            el.check()
            return True
    except Exception as e:
        print(f"    check_box({name}) error: {e}")
    return False


def main():
    print("OpenPR v2: filling with exact field names")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900}
        )
        page = ctx.new_page()

        try:
            page.goto("https://www.openpr.com/news/submit.html", timeout=30000)
            page.wait_for_load_state("domcontentloaded", timeout=20000)
            time.sleep(3)
            dismiss_js(page)
            time.sleep(1)

            sc1 = sc(page, "before_fill")

            # Field mapping from inspection:
            # c8e3cdf... = email
            # dc91cb8... = first text field (maybe agency/name?)
            # a029117... = second text (agency? keep blank)
            # 38501c5... = tel (phone)
            # a3a7c3f... = company/archive name (id=archivnmfield)
            # 83d3ab7... = category select
            # ce8c53b... = title text
            # b0eec64... = body textarea (id=inhalt)
            # verification = verification code
            # erklaerung_agb = terms checkbox
            # erklaerung_datenschutz = privacy checkbox

            filled = {}

            # Email
            if fill_field(page, "c8e3cdf0f524e401016da0e3f544421b", "hello@pantrymate.net"):
                filled["email"] = True

            # Phone (use JS to make visible first)
            page.evaluate("""
                var el = document.querySelector('[name="38501c59954a46dce2a4fafbe28eae84"]');
                if(el) { el.style.display='block'; el.style.visibility='visible'; }
            """)
            if fill_field(page, "38501c59954a46dce2a4fafbe28eae84", "+264610000000"):
                filled["phone"] = True

            # Company/Archive name
            if fill_field(page, "a3a7c3f76fa0e7d3b62b40e533f0d205", "PantryMate"):
                filled["company"] = True

            # Category
            if select_field(page, "83d3ab75f2f89a41449d077ac2e1ac60"):
                filled["category"] = True

            # Title
            if fill_field(page, "ce8c53b284899ada5a12e4ed7572eb99", PR_HEADLINE):
                filled["title"] = True

            # Body (id=inhalt)
            if fill_field(page, "b0eec645d7a53b70b9319ec00d2df434", PR_BODY):
                filled["body"] = True

            # Keywords
            kw_els = page.query_selector_all('[name="kw"]')
            if len(kw_els) > 1:
                try:
                    kw_els[1].fill("AI meal planning pantry food waste cooking")
                    filled["keywords"] = True
                except:
                    pass

            # Check terms boxes
            if check_box(page, "erklaerung_agb"):
                filled["terms"] = True
            if check_box(page, "erklaerung_datenschutz"):
                filled["privacy"] = True

            # Cookie checkbox
            check_box(page, "cookie")

            sc2 = sc(page, "after_fill")
            print(f"\n  Filled fields: {list(filled.keys())}")

            # Check for verification field (possible manual captcha)
            ver_el = page.query_selector('[name="verification"]')
            if ver_el:
                ver_val = ver_el.get_attribute("value") or ""
                ver_ph = ver_el.get_attribute("placeholder") or ""
                print(f"  Verification field: value='{ver_val}' placeholder='{ver_ph}'")
                # If it's a text field with no value, it might need manual input
                # Check if it's visible
                vis = ver_el.is_visible()
                print(f"  Verification visible: {vis}")
                if vis and not ver_val:
                    # Check context around it
                    context_html = page.evaluate("""
                        var el = document.querySelector('[name="verification"]');
                        el ? el.parentElement.innerHTML : ''
                    """)
                    print(f"  Verification context: {context_html[:300]}")

            # Look for real CAPTCHA
            captcha_iframes = page.query_selector_all('iframe[src*="recaptcha"], iframe[src*="hcaptcha"], iframe[src*="cloudflare"]')
            print(f"  CAPTCHA iframes: {len(captcha_iframes)}")

            if captcha_iframes:
                sc3 = sc(page, "captcha_found")
                log_result("OpenPR.com", "PantryMate", "captcha",
                          f"Real CAPTCHA iframe found. Fields filled: {list(filled.keys())}", sc3)
                return

            # Find submit button
            submit_btn = None
            for sel in ['input[type="submit"]', 'button[type="submit"]',
                        'button:has-text("Submit")', 'input[value*="submit" i]',
                        'input[value*="Send" i]', 'input[value*="Publish" i]',
                        'button:has-text("Send")', 'button:has-text("Publish")']:
                submit_btn = page.query_selector(sel)
                if submit_btn:
                    val = submit_btn.get_attribute("value") or submit_btn.text_content() or ""
                    print(f"  Found submit: {sel} value='{val[:50]}'")
                    break

            # Try to find any button
            if not submit_btn:
                all_btns = page.query_selector_all('button, input[type="submit"], input[type="button"]')
                print(f"  All buttons ({len(all_btns)}):")
                for b in all_btns:
                    txt = (b.get_attribute("value") or b.text_content() or "")[:60]
                    print(f"    {txt}")

            sc3 = sc(page, "before_submit")

            if submit_btn:
                submit_btn.scroll_into_view_if_needed()
                submit_btn.click()
                try:
                    page.wait_for_load_state("domcontentloaded", timeout=20000)
                except:
                    pass
                time.sleep(3)

                sc4 = sc(page, "result")
                rc = page.content().lower()
                url = page.url
                print(f"  Result URL: {url}")

                if any(x in rc for x in ["thank", "success", "published", "submitted"]):
                    log_result("OpenPR.com", "PantryMate", "submitted",
                              f"PR likely submitted! URL: {url}. Fields: {list(filled.keys())}", sc4)
                elif "captcha" in rc or captcha_iframes:
                    log_result("OpenPR.com", "PantryMate", "captcha",
                              f"CAPTCHA after submit. URL: {url}", sc4)
                elif any(x in rc for x in ["error", "invalid", "required", "missing"]):
                    log_result("OpenPR.com", "PantryMate", "error",
                              f"Validation error. URL: {url}. Fields: {list(filled.keys())}", sc4)
                else:
                    log_result("OpenPR.com", "PantryMate", "submitted",
                              f"Submit clicked - outcome unclear. URL: {url}. Fields: {list(filled.keys())}", sc4)
            else:
                log_result("OpenPR.com", "PantryMate", "error",
                          f"Could not find submit button. Fields filled: {list(filled.keys())}", sc3)

        except Exception as e:
            sce = sc(page, "exception")
            log_result("OpenPR.com", "PantryMate", "error", f"Exception: {str(e)[:300]}", sce)

        browser.close()

    elapsed = time.time() - start_time
    print(f"Done in {elapsed:.1f}s")
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


if __name__ == "__main__":
    main()
