#!/usr/bin/env python3
"""
AIcyclopedia v3 - JS-based form filling, full diagnostic.
"""
import json, time, os
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

SCREENSHOTS_DIR = "/root/.openclaw/workspace/automation/screenshots"
LOG_FILE = "/root/.openclaw/workspace/automation/submission-log-round2.json"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

PRODUCTS = [
    {
        "name": "PantryMate",
        "url": "https://pantrymate.net",
        "tagline": "Type what's in your fridge, get dinner in 30 seconds",
        "description": "AI-powered pantry-to-meal decision engine. Eliminates dinner decision paralysis — type your ingredients, get personalized dinner ideas instantly. No more staring at a full fridge and ordering takeout.",
        "category": "FREEMIUM",
        "email": "hello@pantrymate.net",
    },
    {
        "name": "SmartBook AI",
        "url": "https://bummerland17.github.io/smartbook-ai/",
        "tagline": "AI phone agent that books appointments 24/7",
        "description": "SmartBook AI answers every call after hours, books appointments directly into your calendar, and sends SMS confirmations. $497/month flat. No contracts.",
        "category": "PAID",
        "email": "hello@pantrymate.net",
    },
]

new_results = []

def log(directory, product, status, notes=""):
    new_results.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "directory": directory, "product": product,
        "status": status, "notes": notes,
    })
    print(f"[{status.upper()}] {directory} — {product}: {notes}")

def ss(page, name):
    path = os.path.join(SCREENSHOTS_DIR, f"{name}.png")
    try: page.screenshot(path=path, full_page=True)
    except: page.screenshot(path=path)

def js_fill(page, selector, value):
    """Fill a field using JS to bypass visibility restrictions."""
    return page.evaluate(f"""
        (function() {{
            var el = document.querySelector('{selector}');
            if (!el) return false;
            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value') ||
                                         Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value');
            if (nativeInputValueSetter) nativeInputValueSetter.set.call(el, {json.dumps(value)});
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            return true;
        }})()
    """)

def js_select(page, selector, value):
    return page.evaluate(f"""
        (function() {{
            var el = document.querySelector('{selector}');
            if (!el) return false;
            el.value = {json.dumps(value)};
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            return true;
        }})()
    """)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 900},
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    )

    for prod in PRODUCTS:
        name = prod["name"]
        safe = name.replace(" ", "_")
        page = ctx.new_page()
        try:
            print(f"\n{'='*50}\n{name}\n{'='*50}")
            page.goto("https://aicyclopedia.com/submit-your-ai-tool/", timeout=30000, wait_until="domcontentloaded")
            time.sleep(5)
            ss(page, f"aicv3_{safe}_loaded")

            # Count all form fields (visible + hidden)
            all_fields = page.evaluate("""
                () => Array.from(document.querySelectorAll('input, textarea, select'))
                    .filter(e => e.name)
                    .map(e => ({name: e.name, type: e.type || e.tagName, visible: e.offsetParent !== null}))
            """)
            print(f"  Total named fields: {len(all_fields)}")
            for f in all_fields:
                print(f"    {f}")

            # Fill all fields via JS (bypasses visibility)
            js_fill(page, 'input[name="form_fields[name]"]', prod["name"])
            js_fill(page, 'input[name="form_fields[field_18f75f2]"]', prod["tagline"])
            js_select(page, 'select[name="form_fields[field_65f5ab7]"]', prod["category"])
            js_fill(page, 'input[name="form_fields[field_34b2203]"]', prod["url"])
            js_fill(page, 'input[name="form_fields[field_2dac996]"]', prod["email"])  # email (hidden step)
            # Textarea for description - try both input and textarea setter
            page.evaluate(f"""
                (function() {{
                    var el = document.querySelector('textarea[name="form_fields[field_0ae884c]"]');
                    if (!el) return;
                    var nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value');
                    if (nativeSetter) nativeSetter.set.call(el, {json.dumps(prod['description'])});
                    el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }})()
            """)

            ss(page, f"aicv3_{safe}_js_filled")
            time.sleep(1)

            # Now click NEXT (only on visible step)
            print("  Clicking NEXT (step 1 → 2)...")
            try:
                page.locator('button:has-text("NEXT")').first.click(timeout=5000)
                time.sleep(4)
                ss(page, f"aicv3_{safe}_after_next1")
            except Exception as e:
                print(f"  NEXT click error: {e}")

            # Check what's visible now
            visible_fields = page.evaluate("""
                () => Array.from(document.querySelectorAll('input, textarea, select'))
                    .filter(e => e.name && e.offsetParent !== null)
                    .map(e => ({name: e.name, value: e.value ? e.value.substring(0, 30) : ''}))
            """)
            print(f"  Visible fields after NEXT: {visible_fields}")

            # Check for another NEXT or Send
            buttons = page.evaluate("""
                () => Array.from(document.querySelectorAll('button'))
                    .filter(b => b.offsetParent !== null)
                    .map(b => b.innerText.trim())
            """)
            print(f"  Visible buttons: {buttons}")

            # Try clicking NEXT again if present
            try:
                next_btns = page.locator('button:has-text("NEXT")').all()
                for nb in next_btns:
                    if nb.is_visible():
                        nb.click(timeout=3000)
                        time.sleep(3)
                        print("  Clicked NEXT step 2→3")
                        break
            except Exception:
                pass

            ss(page, f"aicv3_{safe}_pre_send")

            # Check for captcha
            content = page.content()
            has_recaptcha = "recaptcha" in content.lower() or "g-recaptcha" in content.lower()
            has_hcaptcha = "hcaptcha" in content.lower()

            # Try to find and click Send
            try:
                send_btns = page.locator('button:has-text("Send")').all()
                visible_sends = [b for b in send_btns if b.is_visible()]
                if visible_sends:
                    if has_recaptcha or has_hcaptcha:
                        captcha_type = "reCAPTCHA" if has_recaptcha else "hCaptcha"
                        log("AIcyclopedia", name, "captcha_blocked",
                            f"Form fully filled (all fields via JS) but {captcha_type} required to submit")
                    else:
                        visible_sends[0].click(timeout=5000)
                        time.sleep(5)
                        ss(page, f"aicv3_{safe}_sent")
                        final = page.content().lower()
                        if any(k in final for k in ["thank", "success", "submitted", "received"]):
                            log("AIcyclopedia", name, "submitted", "Success message confirmed")
                        else:
                            log("AIcyclopedia", name, "submitted_unconfirmed", "Clicked Send — awaiting confirmation")
                else:
                    # Dump final page state
                    all_visible_btns = page.evaluate("""
                        () => Array.from(document.querySelectorAll('button, input[type=submit]'))
                            .filter(b => b.offsetParent !== null)
                            .map(b => b.innerText.trim() || b.value || '')
                    """)
                    print(f"  All visible buttons: {all_visible_btns}")
                    ss(page, f"aicv3_{safe}_no_send")
                    captcha_note = f" — reCAPTCHA present" if has_recaptcha else ""
                    log("AIcyclopedia", name, "partial",
                        f"JS-filled all fields{captcha_note}, but Send not visible (gated by captcha or validation)")
            except Exception as e:
                log("AIcyclopedia", name, "partial", f"JS fill done; Send action error: {e}")

        except Exception as e:
            log("AIcyclopedia", name, "error", str(e))
        finally:
            page.close()
        time.sleep(2)

    browser.close()

elapsed_note = "AIcyclopedia v3 run"

# Merge with existing
try:
    with open(LOG_FILE) as f:
        existing = json.load(f)
except:
    existing = {"all_results": []}

# Update only AIcyclopedia entries with new results
old_results = [r for r in existing.get("all_results", []) if r["directory"] != "AIcyclopedia" or "v3" not in r.get("notes", "")]
# Actually just append the new results
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

print(f"\n{'='*50}")
print("AIcyclopedia v3 results:")
for r in new_results:
    print(f"  [{r['status']}] {r['product']}: {r['notes']}")
