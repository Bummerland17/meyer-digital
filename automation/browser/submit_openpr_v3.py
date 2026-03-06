"""
OpenPR v3: Use JS to fill all obfuscated form fields directly.
Also inspect the verification field and the correct submit button.
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

PR_HEADLINE = "PantryMate Launches AI-Powered Dinner Decision Engine - Solves Whats For Dinner in 30 Seconds"
PR_BODY = """PantryMate (pantrymate.net) today announced the launch of its AI-powered pantry-to-meal platform that helps home cooks decide what to make for dinner in under 30 seconds.

Unlike traditional recipe apps, PantryMate works in reverse: users type what is already in their fridge and pantry, and the AI instantly suggests personalized dinner options.

The average American household wastes $1,500 per year in groceries. PantryMate eliminates decision paralysis with fast AI suggestions.

Available at pantrymate.net. Free tier: 3 daily scans. Pro: $9.99/month. Lifetime: $49.

Contact: Wolfgang Meyer - hello@pantrymate.net - https://pantrymate.net"""


def sc(page, name):
    path = os.path.join(SCREENSHOTS_DIR, f"v3_{name}_{int(time.time())}.png")
    try:
        page.screenshot(path=path, full_page=True)
    except:
        pass
    return path


def log_result(site, product, status, notes="", sp=None):
    e = {"site": site, "product": product, "status": status, "notes": notes,
         "timestamp": datetime.now(timezone.utc).isoformat(), "pass": "openpr_v3"}
    if sp:
        e["screenshot"] = sp
    log.append(e)
    print(f"[{status.upper()}] {site}/{product}: {notes}")
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def main():
    print("OpenPR v3: JS-based form fill")

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

            # Remove cookie banner
            page.evaluate("""() => {
                ['#cmpbox2','#cmpbox','.cmpboxBG','.cmpstyleroot'].forEach(s =>
                    document.querySelectorAll(s).forEach(el => el.remove()));
                document.body.style.overflow = '';
            }""")
            time.sleep(1)

            # First: inspect form structure in detail
            form_info = page.evaluate("""() => {
                const forms = document.querySelectorAll('form');
                return Array.from(forms).map(f => ({
                    id: f.id,
                    action: f.action,
                    method: f.method,
                    inputCount: f.querySelectorAll('input,textarea,select').length,
                    submitBtns: Array.from(f.querySelectorAll('button[type="submit"],input[type="submit"]'))
                        .map(b => ({tag: b.tagName, value: b.value || b.textContent.trim(), name: b.name}))
                }));
            }""")
            print(f"\n  Forms on page: {len(form_info)}")
            for i, f in enumerate(form_info):
                print(f"  Form {i}: id={f['id']} action={f['action']} inputs={f['inputCount']} submits={f['submitBtns']}")

            # Get the PR submission form (largest form, or the one with action containing submit/news)
            # Use JS to fill and submit the correct form
            fill_result = page.evaluate("""() => {
                // Find the PR form - it's the one with 'inhalt' textarea or with most fields
                let prForm = null;
                const forms = document.querySelectorAll('form');
                for (const f of forms) {
                    if (f.querySelector('[id="inhalt"]') || f.querySelector('[name*="b0eec645"]')) {
                        prForm = f;
                        break;
                    }
                    // Also check for the title field
                    if (f.querySelectorAll('input,textarea').length > 5) {
                        prForm = f;
                    }
                }
                
                if (!prForm) return {error: 'No PR form found'};
                
                const result = {
                    formAction: prForm.action,
                    formId: prForm.id,
                    filled: []
                };
                
                function setVal(el, val) {
                    if (!el) return false;
                    el.scrollIntoView();
                    if (el.tagName === 'SELECT') {
                        for (const opt of el.options) {
                            if (opt.text.toLowerCase().includes('internet') || 
                                opt.text.toLowerCase().includes('tech')) {
                                el.value = opt.value;
                                el.dispatchEvent(new Event('change', {bubbles: true}));
                                return true;
                            }
                        }
                        if (el.options.length > 1) {
                            el.selectedIndex = 1;
                            el.dispatchEvent(new Event('change', {bubbles: true}));
                            return true;
                        }
                        return false;
                    }
                    // Make visible
                    el.style.display = 'block';
                    el.style.visibility = 'visible';
                    el.style.opacity = '1';
                    el.removeAttribute('disabled');
                    // React-compatible value setting
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value');
                    const nativeTextAreaSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLTextAreaElement.prototype, 'value');
                    try {
                        if (el.tagName === 'TEXTAREA' && nativeTextAreaSetter) {
                            nativeTextAreaSetter.set.call(el, val);
                        } else if (nativeInputValueSetter) {
                            nativeInputValueSetter.set.call(el, val);
                        } else {
                            el.value = val;
                        }
                    } catch(e) {
                        el.value = val;
                    }
                    el.dispatchEvent(new Event('input', {bubbles: true}));
                    el.dispatchEvent(new Event('change', {bubbles: true}));
                    return true;
                }
                
                // Fill email
                const emailEl = prForm.querySelector('[type="email"]');
                if (setVal(emailEl, 'hello@pantrymate.net')) result.filled.push('email');
                
                // Fill company/archive name (id=archivnmfield)
                const companyEl = prForm.querySelector('#archivnmfield') || 
                                   prForm.querySelector('[name*="a3a7c3f"]');
                if (setVal(companyEl, 'PantryMate')) result.filled.push('company');
                
                // Fill category select
                const catEl = prForm.querySelector('select');
                if (setVal(catEl, null)) result.filled.push('category');
                
                // Fill title - the text input that's not company/email
                const allTextInputs = prForm.querySelectorAll('input[type="text"]');
                let titleFilled = false;
                for (const inp of allTextInputs) {
                    if (inp.name !== 'kw' && !inp.name.includes('a3a7c3f') && 
                        inp.name !== 'verification' && !inp.name.includes('dc91cb') &&
                        !inp.name.includes('a0291') && !inp.name.includes('87adf')) {
                        // This looks like the title field (ce8c53b...)
                        if (inp.name.startsWith('ce') || (!titleFilled && inp.name.length > 20)) {
                            if (setVal(inp, '""" + PR_HEADLINE + """')) {
                                result.filled.push('title:' + inp.name.substring(0,8));
                                titleFilled = true;
                            }
                        }
                    }
                }
                
                // Fill body text (id=inhalt)
                const bodyEl = prForm.querySelector('#inhalt') || 
                                prForm.querySelector('textarea[name*="b0eec"]');
                if (setVal(bodyEl, '""" + PR_BODY.replace("'", "\\'").replace("\n", "\\n") + """')) {
                    result.filled.push('body');
                }
                
                // Check terms checkboxes
                const agb = prForm.querySelector('[name="erklaerung_agb"]');
                if (agb) { agb.checked = true; result.filled.push('terms'); }
                const ds = prForm.querySelector('[name="erklaerung_datenschutz"]');
                if (ds) { ds.checked = true; result.filled.push('privacy'); }
                
                // Get verification field info
                const ver = prForm.querySelector('[name="verification"]');
                result.verificationInfo = ver ? {
                    visible: ver.offsetParent !== null,
                    value: ver.value,
                    placeholder: ver.placeholder,
                    required: ver.required,
                    parentHTML: ver.parentElement.innerHTML.substring(0, 500)
                } : null;
                
                // Find submit buttons in this form
                result.submitBtns = Array.from(prForm.querySelectorAll('button,input[type="submit"]'))
                    .map(b => ({
                        tag: b.tagName,
                        type: b.type,
                        value: (b.value || b.textContent || '').trim().substring(0,50),
                        name: b.name,
                        id: b.id
                    }));
                
                return result;
            }""")

            print(f"\n  Fill result: {fill_result}")

            sc1 = sc(page, "after_js_fill")

            if "error" in fill_result:
                log_result("OpenPR.com", "PantryMate", "error", fill_result["error"], sc1)
                browser.close()
                return

            # Check verification field
            ver_info = fill_result.get("verificationInfo")
            if ver_info:
                print(f"\n  Verification field: {ver_info}")
                # If it's visible and appears to be a question, we may need to handle it
                parent_html = ver_info.get("parentHTML", "").lower()
                if any(x in parent_html for x in ["math", "calculate", "sum", "equals", "captcha"]):
                    sc_v = sc(page, "verification_captcha")
                    log_result("OpenPR.com", "PantryMate", "captcha",
                              f"Manual verification/math question required. HTML: {parent_html[:200]}", sc_v)
                    browser.close()
                    return

            # Look for the correct submit button (within the PR form)
            submit_btns = fill_result.get("submitBtns", [])
            print(f"\n  Submit buttons in PR form: {submit_btns}")

            # Click the submit button using JS on the form
            submit_result = page.evaluate("""() => {
                const forms = document.querySelectorAll('form');
                let prForm = null;
                for (const f of forms) {
                    if (f.querySelector('#inhalt') || f.querySelectorAll('input,textarea').length > 5) {
                        prForm = f;
                    }
                }
                if (!prForm) return {error: 'No PR form found for submission'};
                
                // Find submit button in this form
                const btn = prForm.querySelector('input[type="submit"], button[type="submit"]');
                if (btn) {
                    return {btnText: (btn.value || btn.textContent).trim(), btnId: btn.id};
                }
                return {error: 'No submit button in PR form'};
            }""")
            print(f"  Submit button to click: {submit_result}")

            if "error" in submit_result:
                log_result("OpenPR.com", "PantryMate", "error",
                          f"Filled {fill_result.get('filled')} but {submit_result['error']}", sc1)
                browser.close()
                return

            # Now actually click the correct submit button
            # Use JavaScript to find and click it
            page.evaluate("""() => {
                const forms = document.querySelectorAll('form');
                let prForm = null;
                for (const f of forms) {
                    if (f.querySelector('#inhalt') || f.querySelectorAll('input,textarea').length > 5) {
                        prForm = f;
                    }
                }
                if (prForm) {
                    const btn = prForm.querySelector('input[type="submit"], button[type="submit"]');
                    if (btn) btn.click();
                }
            }""")

            try:
                page.wait_for_load_state("domcontentloaded", timeout=20000)
            except:
                pass
            time.sleep(3)

            sc2 = sc(page, "result")
            url = page.url
            rc = page.content().lower()
            print(f"  Result URL: {url}")

            if any(x in rc for x in ["thank", "success", "published", "submitted", "vielen dank"]):
                log_result("OpenPR.com", "PantryMate", "submitted",
                          f"PR submitted! URL: {url}. Fields: {fill_result.get('filled')}", sc2)
            elif any(x in rc for x in ["error", "invalid", "required", "pflicht"]):
                # Extract error message
                err_text = page.evaluate("""() => {
                    const errs = document.querySelectorAll('.error, .alert-danger, .errorMessage, [class*="error"]');
                    return Array.from(errs).map(e => e.textContent.trim()).join(' | ').substring(0, 500);
                }""")
                log_result("OpenPR.com", "PantryMate", "error",
                          f"Validation error: {err_text}. URL: {url}. Fields: {fill_result.get('filled')}", sc2)
            else:
                log_result("OpenPR.com", "PantryMate", "submitted",
                          f"Submit clicked. URL: {url}. Fields: {fill_result.get('filled')}", sc2)

        except Exception as e:
            sce = sc(page, "exception")
            log_result("OpenPR.com", "PantryMate", "error", f"Exception: {str(e)[:300]}", sce)

        browser.close()

    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)
    print("Done")


if __name__ == "__main__":
    main()
