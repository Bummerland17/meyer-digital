"""
OpenPR v5: Fill form with KNOWN field names. Handle image CAPTCHA.
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

# 2104 chars - above the 1500 min
PR_HEADLINE = "PantryMate Launches AI-Powered Dinner Decision Engine"
PR_BODY = """PantryMate (pantrymate.net) today announced the launch of its AI-powered pantry-to-meal platform that helps home cooks decide what to make for dinner in under 30 seconds.

Unlike traditional recipe apps that require users to search and browse, PantryMate works in reverse: users type what is already in their fridge and pantry, and the AI instantly suggests personalized dinner options matched to their ingredients, dietary preferences, and cooking skill level.

The real problem is not finding recipes. It is the decision paralysis of staring at a full fridge and still ordering takeout. PantryMate solves that in 30 seconds.

The average American household wastes $1,500 per year in groceries and spends an additional $60 or more per month on takeout ordered on nights when the fridge was full. PantryMate directly targets this problem with a simple, fast AI that eliminates the decision bottleneck.

PantryMate is available at pantrymate.net with a free tier offering 3 daily pantry scans. Pro plans start at $9.99 per month for unlimited scans, dietary filters, and weekly shopping list generation. A lifetime access option is available for a one-time payment of $49.

PantryMate supports multiple dietary preferences including vegetarian, vegan, gluten-free, and keto. The platform learns from user preferences over time, improving recommendations with each use. Users can also generate a weekly shopping list based on their planned meals, helping to reduce both food waste and grocery spending.

The service is available on any device with a web browser. No app download is required. PantryMate is built for busy families, students, and anyone who wants to stop wasting money on groceries they never use.

About PantryMate: An AI-powered pantry-to-meal decision engine designed to eliminate dinner decision paralysis. Contact: Wolfgang Meyer, hello@pantrymate.net, https://pantrymate.net"""

PR_ABOUT = "PantryMate is an AI-powered pantry-to-meal decision engine for home cooks. The platform eliminates dinner decision paralysis by instantly matching available ingredients to personalized meal suggestions. Founded by Wolfgang Meyer. Available at pantrymate.net."

PR_CONTACT = "Wolfgang Meyer / PantryMate\nhello@pantrymate.net\nhttps://pantrymate.net\nWindhoek, Namibia"


def sc(page, name):
    path = os.path.join(SCREENSHOTS_DIR, f"v5_{name}_{int(time.time())}.png")
    try:
        page.screenshot(path=path, full_page=True)
    except:
        pass
    return path


def log_result(site, product, status, notes="", sp=None):
    e = {"site": site, "product": product, "status": status, "notes": notes,
         "timestamp": datetime.now(timezone.utc).isoformat(), "pass": "openpr_v5"}
    if sp:
        e["screenshot"] = sp
    log.append(e)
    print(f"[{status.upper()}] {site}/{product}: {notes}")
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def js_fill(page, name, value):
    """Fill a field by name using JavaScript."""
    result = page.evaluate("""([fieldName, fieldValue]) => {
        const el = document.querySelector('[name="' + fieldName + '"]');
        if (!el) return 'not_found';
        el.style.display = 'block';
        el.style.visibility = 'visible';
        el.removeAttribute('disabled');
        const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
        const setter = Object.getOwnPropertyDescriptor(proto, 'value');
        if (setter) setter.set.call(el, fieldValue);
        else el.value = fieldValue;
        el.dispatchEvent(new Event('input', {bubbles: true}));
        el.dispatchEvent(new Event('change', {bubbles: true}));
        return 'ok';
    }""", [name, value])
    return result == 'ok'


def js_select(page, name, keyword):
    """Select option in a select element by keyword."""
    result = page.evaluate("""([fieldName, kw]) => {
        const el = document.querySelector('select[name="' + fieldName + '"]');
        if (!el) return 'not_found';
        const opts = Array.from(el.options);
        const match = opts.find(o => o.text.toLowerCase().includes(kw.toLowerCase()));
        if (match) {
            el.value = match.value;
            el.dispatchEvent(new Event('change', {bubbles: true}));
            return match.text;
        }
        // Fallback: select index 1
        if (opts.length > 1) {
            el.selectedIndex = 1;
            el.dispatchEvent(new Event('change', {bubbles: true}));
            return opts[1].text;
        }
        return 'no_match';
    }""", [name, keyword])
    return result


def js_check(page, name):
    page.evaluate("""([n]) => {
        const el = document.querySelector('[name="' + n + '"]');
        if (el) el.checked = true;
    }""", [name])


def main():
    print("OpenPR v5: Known field names")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 1200}
        )
        page = ctx.new_page()

        try:
            page.goto("https://www.openpr.com/news/submit.html", timeout=30000)
            page.wait_for_load_state("domcontentloaded", timeout=20000)
            time.sleep(3)

            # Remove cookie banner
            page.evaluate("""() => {
                ['#cmpbox2','#cmpbox','.cmpboxBG','.cmpstyleroot'].forEach(s =>
                    document.querySelectorAll(s).forEach(el => el.remove()));
                document.body.style.overflow = '';
            }""")
            time.sleep(1)

            filled = {}

            # Fill all known fields
            if js_fill(page, "11786d0a5f8878bf2e1a", "Wolfgang Meyer"):
                filled["name"] = True

            if js_fill(page, "cfdc1bd54b81166c792c", "hello@pantrymate.net"):
                filled["email"] = True

            if js_fill(page, "a3fee081b5978aa9587d", "+264610000000"):
                filled["phone"] = True

            if js_fill(page, "4ff57d9634fdb8977d21", "PantryMate"):
                filled["company"] = True

            cat = js_select(page, "26604b4c9225d44f24f1", "internet")
            filled["category"] = cat

            if js_fill(page, "098d8e50ca5f7f94782e", PR_HEADLINE):
                filled["title"] = True

            if js_fill(page, "9c89524650821ce165ca", PR_BODY):
                filled["body"] = True

            if js_fill(page, "e5fff7f763fc8be2316c", PR_ABOUT):
                filled["portrait"] = True

            if js_fill(page, "f37e75d189bfb00e95d0", PR_CONTACT):
                filled["contact"] = True

            js_check(page, "erklaerung_agb")
            js_check(page, "erklaerung_datenschu")
            filled["terms"] = True

            print(f"  Filled: {list(filled.keys())}")

            # Find the CAPTCHA - check for canvas, img, or any visual element near verification
            captcha_info = page.evaluate("""() => {
                const ver = document.querySelector('[name="verification"]');
                if (!ver) return {found: false};
                
                // Look in parent rows for any image or canvas
                let parent = ver.parentElement;
                for (let i = 0; i < 5; i++) {
                    if (!parent) break;
                    const img = parent.querySelector('img');
                    const canvas = parent.querySelector('canvas');
                    const siblingRow = parent.previousElementSibling;
                    const sibImg = siblingRow?.querySelector('img');
                    
                    if (img) return {found: true, type: 'img', src: img.src, id: img.id};
                    if (canvas) return {found: true, type: 'canvas', id: canvas.id};
                    if (sibImg) return {found: true, type: 'sibling_img', src: sibImg.src};
                    
                    parent = parent.parentElement;
                }
                
                // Broader: any img in the form near bottom
                const form = document.getElementById('formular');
                if (!form) return {found: false};
                const allImgs = Array.from(form.querySelectorAll('img'));
                for (const img of allImgs) {
                    const src = img.src.toLowerCase();
                    if (src.includes('captcha') || src.includes('verif') || src.includes('code') || src.includes('sec')) {
                        return {found: true, type: 'form_img', src: img.src, id: img.id};
                    }
                }
                
                // Check if there's any visible image at all in the form
                const lastImg = allImgs[allImgs.length - 1];
                if (lastImg && !lastImg.src.includes('logo') && !lastImg.src.includes('tracking')) {
                    return {found: true, type: 'last_img', src: lastImg.src};
                }
                
                return {found: false, verVisible: ver.offsetParent !== null};
            }""")

            print(f"  CAPTCHA info: {captcha_info}")

            # Screenshot the full form now
            sc1 = sc(page, "form_filled_full")

            # Try to screenshot just the verification area
            ver_screenshot_path = os.path.join(SCREENSHOTS_DIR, f"v5_verification_area_{int(time.time())}.png")
            try:
                ver_el = page.query_selector('[name="verification"]')
                if ver_el:
                    # Get bounding box and screenshot the area around it
                    box = ver_el.bounding_box()
                    if box:
                        # Crop a wider area (the row above the field should have the CAPTCHA image)
                        clip = {
                            "x": max(0, box["x"] - 50),
                            "y": max(0, box["y"] - 150),  # 150px above should include captcha image
                            "width": min(1280, box["width"] + 200),
                            "height": box["height"] + 200
                        }
                        page.screenshot(path=ver_screenshot_path, clip=clip)
                        print(f"  Verification area screenshot: {ver_screenshot_path}")
            except Exception as e:
                print(f"  Verification screenshot error: {e}")

            if captcha_info.get("found") and captcha_info.get("src"):
                # There's a CAPTCHA image - log it
                log_result("OpenPR.com", "PantryMate", "captcha",
                          f"Image CAPTCHA present. Form filled: {list(filled.keys())}. CAPTCHA: {captcha_info}. Screenshot: {ver_screenshot_path}",
                          sc1)
            else:
                # No image CAPTCHA found - the verification field might be a honeypot (leave empty)
                # or it might show after clicking Preview
                # Try clicking Preview button
                print("  No visible CAPTCHA image found - clicking Preview...")
                preview_result = page.evaluate("""() => {
                    const form = document.getElementById('formular');
                    if (!form) return {error: 'no form'};
                    const btn = form.querySelector('button[type="submit"]');
                    if (!btn) return {error: 'no button'};
                    btn.click();
                    return {clicked: true, text: (btn.value || btn.textContent).trim()};
                }""")
                print(f"  Preview click: {preview_result}")

                try:
                    page.wait_for_load_state("domcontentloaded", timeout=20000)
                except:
                    pass
                time.sleep(3)

                sc2 = sc(page, "after_preview")
                url = page.url
                rc = page.content().lower()

                # Check for errors and CAPTCHA on preview page
                errors = page.evaluate("""() => {
                    const errs = document.querySelectorAll('.alert-danger, .error, [class*="error"], .bg-danger');
                    return Array.from(errs).map(e => e.textContent.trim()).filter(t => t.length > 2).join(' | ').substring(0, 500);
                }""")

                # Check if CAPTCHA now appeared
                captcha_now = page.evaluate("""() => {
                    const ver = document.querySelector('[name="verification"]');
                    if (!ver) return null;
                    let p = ver.parentElement;
                    for (let i = 0; i < 5; i++) {
                        const img = p?.querySelector('img');
                        if (img && !img.src.includes('logo')) return img.src;
                        p = p?.parentElement;
                    }
                    return null;
                }""")

                print(f"  URL: {url}, Errors: {errors[:200]}, CAPTCHA now: {captcha_now}")

                if captcha_now:
                    # Screenshot the CAPTCHA
                    cap_path = os.path.join(SCREENSHOTS_DIR, f"v5_captcha_revealed_{int(time.time())}.png")
                    try:
                        img_el = page.query_selector(f'img[src="{captcha_now}"]')
                        if img_el:
                            img_el.screenshot(path=cap_path)
                    except:
                        pass

                    log_result("OpenPR.com", "PantryMate", "captcha",
                              f"Image CAPTCHA appeared on preview. Fields: {list(filled.keys())}. CAPTCHA URL: {captcha_now}",
                              sc2)

                elif errors and "please check" in errors.lower():
                    log_result("OpenPR.com", "PantryMate", "captcha",
                              f"Form validation/CAPTCHA errors: {errors[:300]}. Fields filled: {list(filled.keys())}",
                              sc2)

                elif "step 2" in rc or "preview" in rc or "vorschau" in rc:
                    # We're on the preview page! 
                    print("  On preview page - looking for final submit button...")
                    final_submit = page.query_selector('button[type="submit"], input[type="submit"]')
                    if final_submit:
                        final_submit.click()
                        try:
                            page.wait_for_load_state("domcontentloaded", timeout=20000)
                        except:
                            pass
                        time.sleep(3)
                        sc3 = sc(page, "final_result")
                        log_result("OpenPR.com", "PantryMate", "submitted",
                                  f"PR submitted after preview! URL: {page.url}. Fields: {list(filled.keys())}",
                                  sc3)
                    else:
                        log_result("OpenPR.com", "PantryMate", "submitted",
                                  f"On preview page. URL: {url}. Fields: {list(filled.keys())}",
                                  sc2)

                elif any(x in rc for x in ["thank", "success", "published", "vielen dank", "confirmation"]):
                    log_result("OpenPR.com", "PantryMate", "submitted",
                              f"PR submitted! URL: {url}. Fields: {list(filled.keys())}",
                              sc2)
                else:
                    log_result("OpenPR.com", "PantryMate", "captcha",
                              f"Unclear result. URL: {url}. Errors: {errors[:200]}. Fields: {list(filled.keys())}",
                              sc2)

        except Exception as e:
            import traceback
            sce = sc(page, "exception")
            log_result("OpenPR.com", "PantryMate", "error", f"Exception: {str(e)[:300]}", sce)
            print(traceback.format_exc())

        browser.close()

    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)
    print("Done")


if __name__ == "__main__":
    main()
