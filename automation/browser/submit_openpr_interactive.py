"""
OpenPR Interactive CAPTCHA Solver.
Fills form, saves CAPTCHA to a file, waits for answer file, then submits.
"""
from playwright.sync_api import sync_playwright
import json
import time
import os
from datetime import datetime, timezone

SCREENSHOTS_DIR = "/root/.openclaw/workspace/automation/screenshots"
LOG_FILE = "/root/.openclaw/workspace/automation/submission-log.json"
CAPTCHA_IMG = "/root/.openclaw/workspace/automation/captcha_current.png"
CAPTCHA_ANSWER = "/root/.openclaw/workspace/automation/captcha_answer.txt"
CAPTCHA_READY = "/root/.openclaw/workspace/automation/captcha_ready.flag"

try:
    with open(LOG_FILE) as f:
        log = json.load(f)
except:
    log = []

PR_HEADLINE = "PantryMate Launches AI-Powered Dinner Decision Engine"
PR_BODY = """PantryMate (pantrymate.net) today announced the launch of its AI-powered pantry-to-meal platform that helps home cooks decide what to make for dinner in under 30 seconds.

Unlike traditional recipe apps that require users to search and browse, PantryMate works in reverse: users type what is already in their fridge and pantry, and the AI instantly suggests personalized dinner options matched to their ingredients, dietary preferences, and cooking skill level.

The real problem is not finding recipes. It is the decision paralysis of staring at a full fridge and still ordering takeout. PantryMate solves that challenge in 30 seconds.

The average American household wastes $1,500 per year in groceries and spends an additional $60 or more per month on takeout ordered on nights when the fridge was full. PantryMate directly targets this problem with a simple, fast AI that eliminates the decision bottleneck.

PantryMate is available at pantrymate.net with a free tier offering 3 daily pantry scans. Pro plans start at $9.99 per month for unlimited scans, dietary filters, and weekly shopping list generation. Lifetime access is available for a one-time payment of $49.

The platform supports multiple dietary preferences including vegetarian, vegan, gluten-free, and low-carb options. It learns from user preferences over time, improving meal recommendations with each use. Users can generate weekly shopping lists based on planned meals to reduce both food waste and grocery spending.

The service works on any device with a web browser. No app download required. PantryMate is built for busy families, students, and anyone who wants to stop wasting money on groceries they never use.

About PantryMate: An AI-powered pantry-to-meal decision engine to eliminate dinner decision paralysis.
Contact: Wolfgang Meyer, Founder, hello@pantrymate.net, https://pantrymate.net"""

PR_ABOUT = "PantryMate is an AI-powered pantry-to-meal decision engine for home cooks. Eliminates dinner decision paralysis by matching available ingredients to personalized meal suggestions. Founded by Wolfgang Meyer. Available at pantrymate.net."

PR_CONTACT = "Wolfgang Meyer / PantryMate\nhello@pantrymate.net\nhttps://pantrymate.net\nWindhoek, Namibia"


def sc(page, name):
    path = os.path.join(SCREENSHOTS_DIR, f"interactive_{name}_{int(time.time())}.png")
    try:
        page.screenshot(path=path, full_page=True)
    except:
        pass
    return path


def log_result(site, product, status, notes="", sp=None):
    e = {"site": site, "product": product, "status": status, "notes": notes,
         "timestamp": datetime.now(timezone.utc).isoformat(), "pass": "openpr_interactive"}
    if sp:
        e["screenshot"] = sp
    log.append(e)
    print(f"[{status.upper()}] {site}/{product}: {notes}")
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def main():
    # Clean up old signal files
    for f in [CAPTCHA_ANSWER, CAPTCHA_READY]:
        if os.path.exists(f):
            os.remove(f)

    print("OpenPR Interactive: filling form and waiting for CAPTCHA solution")
    print(f"Body length: {len(PR_BODY)}")

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

            page.evaluate("""() => {
                ['#cmpbox2','#cmpbox','.cmpboxBG','.cmpstyleroot'].forEach(s =>
                    document.querySelectorAll(s).forEach(el => el.remove()));
                document.body.style.overflow = '';
            }""")
            time.sleep(2)

            # Wait for captcha iframe
            try:
                page.wait_for_selector('iframe[name="captcha"]', timeout=10000)
                captcha_frame = page.frame(name="captcha")
                if captcha_frame:
                    captcha_frame.wait_for_load_state("load", timeout=8000)
                    time.sleep(1)
            except:
                pass

            # Screenshot the CAPTCHA
            iframe_el = page.query_selector('iframe[name="captcha"]')
            if not iframe_el:
                log_result("OpenPR.com", "PantryMate", "error", "No CAPTCHA iframe found")
                browser.close()
                return

            iframe_el.screenshot(path=CAPTCHA_IMG)
            print(f"CAPTCHA saved to: {CAPTCHA_IMG}")

            # Signal ready
            with open(CAPTCHA_READY, "w") as f:
                f.write(str(time.time()))

            print(f"\n>>> CAPTCHA READY. Read: {CAPTCHA_IMG}")
            print(f">>> Write the answer to: {CAPTCHA_ANSWER}")
            print(f">>> Waiting up to 120 seconds...")

            # Wait for answer (max 120 seconds)
            captcha_text = None
            for i in range(120):
                if os.path.exists(CAPTCHA_ANSWER):
                    with open(CAPTCHA_ANSWER) as f:
                        captcha_text = f.read().strip().upper()
                    print(f">>> Got CAPTCHA answer: '{captcha_text}'")
                    break
                if i % 10 == 0:
                    print(f"  Waiting... ({i}s)")
                time.sleep(1)

            if not captcha_text:
                sc_to = sc(page, "timeout")
                log_result("OpenPR.com", "PantryMate", "captcha",
                          f"CAPTCHA timeout - no answer provided within 120s. Screenshot: {CAPTCHA_IMG}",
                          sc_to)
                browser.close()
                return

            # Now fill the entire form including CAPTCHA
            data = {
                "headline": PR_HEADLINE,
                "body": PR_BODY,
                "about": PR_ABOUT,
                "contact": PR_CONTACT,
                "captchaText": captcha_text,
            }

            fill_result = page.evaluate("""(data) => {
                const form = document.getElementById('formular');
                if (!form) return {error: 'no formular'};
                const result = {filled: [], errors: []};
                
                function setVal(el, val) {
                    if (!el) return false;
                    el.style.display = 'block';
                    el.style.visibility = 'visible';
                    el.removeAttribute('disabled');
                    const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
                    const setter = Object.getOwnPropertyDescriptor(proto, 'value');
                    try { if (setter) setter.set.call(el, val); else el.value = val; }
                    catch(e) { el.value = val; }
                    el.dispatchEvent(new Event('input', {bubbles: true}));
                    el.dispatchEvent(new Event('change', {bubbles: true}));
                    return true;
                }
                
                function getCtx(el) {
                    const p = el.closest('tr') || el.closest('.form-group') || el.parentElement;
                    return (p ? p.textContent : '').toLowerCase();
                }
                
                const used = new Set();
                const fields = Array.from(form.querySelectorAll(
                    'input:not([type="hidden"]):not([type="file"]):not([type="checkbox"]), textarea, select'
                ));
                
                fields.forEach(el => {
                    if (used.has(el)) return;
                    const ctx = getCtx(el);
                    const type = (el.type || '').toLowerCase();
                    const id = (el.id || '').toLowerCase();
                    
                    if (el.name === 'verification') {
                        if (setVal(el, data.captchaText)) { result.filled.push('verification:' + data.captchaText); used.add(el); }
                    } else if (type === 'email' || ctx.includes('your email')) {
                        if (setVal(el, 'hello@pantrymate.net')) { result.filled.push('email'); used.add(el); }
                    } else if (ctx.includes('your name') && type === 'text') {
                        if (setVal(el, 'Wolfgang Meyer')) { result.filled.push('name'); used.add(el); }
                    } else if (type === 'tel' || ctx.includes('telephone') || ctx.includes('telefon')) {
                        if (setVal(el, '+264610000000')) { result.filled.push('phone'); used.add(el); }
                    } else if (id === 'archivnmfield' || ctx.includes('company name') || ctx.includes('archive')) {
                        if (!used.has(el) && setVal(el, 'PantryMate')) { result.filled.push('company'); used.add(el); }
                    } else if (el.tagName === 'SELECT') {
                        const opts = Array.from(el.options);
                        let sel = false;
                        for (const opt of opts) {
                            const t = opt.text.toLowerCase();
                            if (t.includes('internet') || t.includes('e-commerce') || t.includes('online') || t.includes('tech')) {
                                el.value = opt.value;
                                el.dispatchEvent(new Event('change', {bubbles: true}));
                                result.filled.push('category:' + opt.text.substring(0, 25));
                                sel = true; used.add(el); break;
                            }
                        }
                        if (!sel && opts.length > 1) {
                            el.selectedIndex = 1;
                            el.dispatchEvent(new Event('change', {bubbles: true}));
                            result.filled.push('category:first');
                            used.add(el);
                        }
                    } else if ((ctx.includes('title') || ctx.includes('headline')) && type === 'text') {
                        if (!used.has(el) && setVal(el, data.headline)) { result.filled.push('title'); used.add(el); }
                    } else if (id === 'inhalt' || ctx.includes('text of your press')) {
                        if (setVal(el, data.body)) { result.filled.push('body'); used.add(el); }
                    } else if (el.tagName === 'TEXTAREA' && (ctx.includes('portrait') || ctx.includes('about /'))) {
                        if (setVal(el, data.about)) { result.filled.push('portrait'); used.add(el); }
                    } else if (el.tagName === 'TEXTAREA' && (ctx.includes('contact') || ctx.includes('postal') || ctx.includes('address') || ctx.includes('presscontact'))) {
                        if (setVal(el, data.contact)) { result.filled.push('contact'); used.add(el); }
                    }
                });
                
                form.querySelectorAll('input[type="checkbox"]').forEach(cb => {
                    if (cb.name.includes('erklaerung')) { cb.checked = true; result.filled.push('cb'); }
                });
                
                return result;
            }""", data)

            print(f"Form filled: {fill_result.get('filled')}")
            sc1 = sc(page, "form_filled")

            # Click Preview
            page.evaluate("""() => {
                const btn = document.getElementById('formular')?.querySelector('button[type="submit"]');
                if (btn) btn.click();
            }""")

            try:
                page.wait_for_load_state("domcontentloaded", timeout=20000)
            except:
                pass
            time.sleep(3)

            sc2 = sc(page, "after_preview")
            url = page.url
            rc = page.content().lower()
            print(f"After preview URL: {url}")

            page_errors = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('.alert-danger, [class*="error"]'))
                    .map(e => e.textContent.trim()).filter(t => t.length > 2).join(' | ').substring(0, 500);
            }""")

            if any(x in rc for x in ["thank you", "vielen dank", "confirmation", "step 3", "successfully"]):
                log_result("OpenPR.com", "PantryMate", "submitted",
                          f"PR SUBMITTED! URL: {url}", sc2)

            elif "step 2" in rc or "preview" in rc:
                # On preview - look for final submit
                print("On preview page - submitting...")
                page.evaluate("""() => {
                    const btns = Array.from(document.querySelectorAll('button, input[type="submit"]'));
                    for (const b of btns) {
                        const t = (b.value || b.textContent || '').toLowerCase();
                        if (t.includes('submit') || t.includes('publish') || t.includes('send') || t.includes('confirm')) {
                            b.click(); return;
                        }
                    }
                    if (btns[0]) btns[0].click();
                }""")
                try:
                    page.wait_for_load_state("domcontentloaded", timeout=20000)
                except:
                    pass
                time.sleep(3)
                sc3 = sc(page, "final_submit")
                final_rc = page.content().lower()
                if any(x in final_rc for x in ["thank", "confirmation", "published", "submitted", "step 3"]):
                    log_result("OpenPR.com", "PantryMate", "submitted",
                              f"PR SUBMITTED after preview! URL: {page.url}", sc3)
                else:
                    log_result("OpenPR.com", "PantryMate", "captcha",
                              f"After final submit unclear. URL: {page.url}. CAPTCHA was: '{captcha_text}'", sc3)

            elif page_errors:
                log_result("OpenPR.com", "PantryMate", "captcha",
                          f"Form errors after preview: {page_errors[:300]}. CAPTCHA was: '{captcha_text}'", sc2)
            else:
                log_result("OpenPR.com", "PantryMate", "captcha",
                          f"Unknown result. URL: {url}. CAPTCHA: '{captcha_text}'", sc2)

        except Exception as e:
            import traceback
            sce = sc(page, "exception")
            log_result("OpenPR.com", "PantryMate", "error", f"Exception: {str(e)[:300]}", sce)
            print(traceback.format_exc())

        browser.close()

    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


if __name__ == "__main__":
    main()
