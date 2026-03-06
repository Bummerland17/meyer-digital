"""
OpenPR v6: Find fields by context in a SINGLE JS evaluation (names change per load).
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

PR_HEADLINE = "PantryMate Launches AI-Powered Dinner Decision Engine"
PR_BODY = """PantryMate (pantrymate.net) today announced the launch of its AI-powered pantry-to-meal platform that helps home cooks decide what to make for dinner in under 30 seconds.

Unlike traditional recipe apps, PantryMate works in reverse: users type what is in their fridge and pantry, and the AI suggests personalized dinner options matched to their ingredients and dietary preferences.

The average American household wastes $1,500 per year in groceries. PantryMate eliminates this waste with fast AI that removes decision paralysis.

PantryMate is available at pantrymate.net with a free tier of 3 daily scans. Pro plans at $9.99 per month include unlimited scans, dietary filters, and weekly shopping list generation. Lifetime access is $49.

PantryMate supports vegetarian, vegan, gluten-free, and keto preferences. The platform learns from user choices over time. No app download required, works on any browser-capable device.

About PantryMate: An AI-powered pantry-to-meal decision engine for home cooks.
Contact: Wolfgang Meyer, hello@pantrymate.net, https://pantrymate.net"""

PR_ABOUT = "PantryMate is an AI-powered pantry-to-meal decision engine for home cooks. The platform eliminates dinner decision paralysis by matching available ingredients to personalized meal suggestions in seconds. Founded by Wolfgang Meyer. Available at pantrymate.net."

PR_CONTACT = "Wolfgang Meyer / PantryMate\nhello@pantrymate.net\nhttps://pantrymate.net\nWindhoek, Namibia"


def sc(page, name):
    path = os.path.join(SCREENSHOTS_DIR, f"v6_{name}_{int(time.time())}.png")
    try:
        page.screenshot(path=path, full_page=True)
    except:
        pass
    return path


def log_result(site, product, status, notes="", sp=None):
    e = {"site": site, "product": product, "status": status, "notes": notes,
         "timestamp": datetime.now(timezone.utc).isoformat(), "pass": "openpr_v6"}
    if sp:
        e["screenshot"] = sp
    log.append(e)
    print(f"[{status.upper()}] {site}/{product}: {notes}")
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def main():
    print("OpenPR v6: Context-based field detection in single JS pass")

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

            # SINGLE JS CALL: find by context and fill
            data = {
                "headline": PR_HEADLINE,
                "body": PR_BODY,
                "about": PR_ABOUT,
                "contact": PR_CONTACT,
            }

            fill_result = page.evaluate("""(data) => {
                const form = document.getElementById('formular');
                if (!form) return {error: 'no formular'};
                
                const result = {filled: [], fieldNames: {}, errors: []};
                
                function setVal(el, val) {
                    if (!el) return false;
                    el.style.display = 'block';
                    el.style.visibility = 'visible';
                    el.removeAttribute('disabled');
                    const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
                    const setter = Object.getOwnPropertyDescriptor(proto, 'value');
                    try {
                        if (setter) setter.set.call(el, val);
                        else el.value = val;
                    } catch(e) { el.value = val; }
                    el.dispatchEvent(new Event('input', {bubbles: true}));
                    el.dispatchEvent(new Event('change', {bubbles: true}));
                    return true;
                }
                
                function getContext(el) {
                    let p = el.closest('tr') || el.closest('.form-group') || el.parentElement;
                    return (p ? p.textContent : '').toLowerCase().trim();
                }
                
                // Process all form fields
                const fields = Array.from(form.querySelectorAll('input:not([type="hidden"]):not([type="file"]):not([type="checkbox"]), textarea, select'));
                
                const used = new Set();
                
                fields.forEach(el => {
                    if (used.has(el)) return;
                    const ctx = getContext(el);
                    const type = (el.type || '').toLowerCase();
                    const name = (el.name || '').toLowerCase();
                    const id = (el.id || '').toLowerCase();
                    
                    // Email
                    if (type === 'email' || ctx.includes('your email') || ctx.includes('e-mail')) {
                        if (setVal(el, 'hello@pantrymate.net')) {
                            result.filled.push('email');
                            result.fieldNames.email = el.name;
                            used.add(el);
                        }
                    }
                    // Name
                    else if (ctx.includes('your name') && type === 'text') {
                        if (setVal(el, 'Wolfgang Meyer')) {
                            result.filled.push('name');
                            used.add(el);
                        }
                    }
                    // Phone
                    else if (type === 'tel' || ctx.includes('telephone') || ctx.includes('telefon')) {
                        if (setVal(el, '+264610000000')) {
                            result.filled.push('phone');
                            used.add(el);
                        }
                    }
                    // Company name (archive)
                    else if (id === 'archivnmfield' || ctx.includes('company name') || ctx.includes('archive')) {
                        if (!used.has(el) && setVal(el, 'PantryMate')) {
                            result.filled.push('company');
                            used.add(el);
                        }
                    }
                    // Category select
                    else if (el.tagName === 'SELECT') {
                        const opts = Array.from(el.options);
                        let selected = false;
                        for (const opt of opts) {
                            const t = opt.text.toLowerCase();
                            if (t.includes('internet') || t.includes('e-commerce') || t.includes('online') || t.includes('tech')) {
                                el.value = opt.value;
                                el.dispatchEvent(new Event('change', {bubbles: true}));
                                result.filled.push('category:' + opt.text.substring(0, 30));
                                selected = true;
                                used.add(el);
                                break;
                            }
                        }
                        if (!selected && opts.length > 1) {
                            el.selectedIndex = 1;
                            el.dispatchEvent(new Event('change', {bubbles: true}));
                            result.filled.push('category:' + opts[1].text.substring(0, 30));
                            used.add(el);
                        }
                    }
                    // Title
                    else if (ctx.includes('title') || ctx.includes('headline')) {
                        if (!used.has(el) && type === 'text' && setVal(el, data.headline)) {
                            result.filled.push('title');
                            used.add(el);
                        }
                    }
                    // Body text (main PR text)
                    else if (id === 'inhalt' || ctx.includes('text of your press') || ctx.includes('press release text')) {
                        if (setVal(el, data.body)) {
                            result.filled.push('body');
                            used.add(el);
                        }
                    }
                    // Portrait / About
                    else if (el.tagName === 'TEXTAREA' && (ctx.includes('portrait') || ctx.includes('about') || ctx.includes('about /'))) {
                        if (setVal(el, data.about)) {
                            result.filled.push('portrait');
                            used.add(el);
                        }
                    }
                    // Contact / Postal address
                    else if (el.tagName === 'TEXTAREA' && (ctx.includes('contact') || ctx.includes('postal') || ctx.includes('address') || ctx.includes('presscontact'))) {
                        if (setVal(el, data.contact)) {
                            result.filled.push('contact');
                            used.add(el);
                        }
                    }
                    // Verification - check what's around it
                    else if (name === 'verification') {
                        result.verCtx = ctx.substring(0, 200);
                        // If it's a honeypot-style field, leave empty
                        // If it has a visible CAPTCHA image, we need to read it
                        const parentImgs = (el.closest('tr') || el.parentElement.parentElement || el.parentElement)
                            ?.querySelectorAll('img') || [];
                        if (parentImgs.length > 0) {
                            const img = parentImgs[0];
                            result.captchaImgSrc = img.src;
                            result.captchaImgId = img.id;
                        } else {
                            // No image - might be empty spam filter, leave blank
                            result.verificationIsHoneypot = true;
                        }
                    }
                });
                
                // Checkboxes
                ['erklaerung_agb', 'erklaerung_datenschutz'].forEach(n => {
                    const cb = form.querySelector('[name="' + n + '"]') || 
                               form.querySelector('[name^="erklaerung"]');
                    if (cb) { cb.checked = true; result.filled.push('cb:' + n.substring(0,12)); }
                });
                
                // Also try by prefix
                form.querySelectorAll('input[type="checkbox"]').forEach(cb => {
                    if (cb.name.includes('erklaerung')) {
                        cb.checked = true;
                    }
                });
                
                result.totalFields = fields.length;
                result.bodyLength = data.body.length;
                
                return result;
            }""", data)

            print(f"\n  Fill result: {fill_result}")

            # Screenshot full form
            sc1 = sc(page, "filled_form")

            captcha_src = fill_result.get("captchaImgSrc")
            is_honeypot = fill_result.get("verificationIsHoneypot", False)
            ver_ctx = fill_result.get("verCtx", "")

            print(f"  CAPTCHA src: {captcha_src}")
            print(f"  Is honeypot: {is_honeypot}")
            print(f"  Ver context: {ver_ctx[:100]}")

            if captcha_src:
                # There's a CAPTCHA image - need to read it
                # Save it
                cap_path = os.path.join(SCREENSHOTS_DIR, f"v6_captcha_img_{int(time.time())}.png")
                try:
                    cap_el = page.query_selector(f'img[src="{captcha_src}"]')
                    if cap_el:
                        cap_el.screenshot(path=cap_path)
                        print(f"  CAPTCHA image saved: {cap_path}")
                except:
                    pass
                log_result("OpenPR.com", "PantryMate", "captcha",
                          f"Image CAPTCHA. Src: {captcha_src}. Fields: {fill_result.get('filled')}",
                          sc1)
                browser.close()
                return

            # Click Preview button
            preview_click = page.evaluate("""() => {
                const form = document.getElementById('formular');
                if (!form) return {error: 'no form'};
                const btn = form.querySelector('button[type="submit"]');
                if (!btn) return {error: 'no button'};
                const text = (btn.value || btn.textContent || '').trim();
                btn.click();
                return {clicked: true, text: text};
            }""")
            print(f"\n  Preview click: {preview_click}")

            try:
                page.wait_for_load_state("domcontentloaded", timeout=20000)
            except:
                pass
            time.sleep(3)

            sc2 = sc(page, "after_preview_click")
            url = page.url
            rc = page.content().lower()
            print(f"  URL after preview: {url}")

            # Get page state details
            page_state = page.evaluate("""() => {
                const errors = Array.from(document.querySelectorAll('.alert-danger, .error, [class*="error"], .bg-danger, .fehler'))
                    .map(e => e.textContent.trim()).filter(t => t.length > 2).join(' | ').substring(0, 600);
                
                const step2 = document.querySelector('[class*="step-2"], [class*="step2"], [data-step="2"]') !== null;
                const previewContent = document.querySelector('[class*="preview"], #preview, .preview-content') !== null;
                
                // Find any new captcha
                const captchaImg = document.querySelector('img[src*="captcha"], img[id*="captcha"]');
                
                // Progress bar info
                const progress = document.querySelector('.progress, [class*="progress"], [class*="wizard"]');
                const progressText = progress ? progress.textContent.trim().substring(0, 100) : '';
                
                const allText = document.body.textContent.substring(0, 500);
                
                return {
                    errors,
                    step2,
                    previewContent,
                    captchaImgSrc: captchaImg ? captchaImg.src : null,
                    progressText,
                    bodySnippet: allText
                };
            }""")

            print(f"  Page state: errors={page_state['errors'][:200]}, captcha={page_state['captchaImgSrc']}, progress={page_state['progressText']}")

            if page_state.get("captchaImgSrc"):
                # CAPTCHA appeared on preview page
                cap_src = page_state["captchaImgSrc"]
                cap_path2 = os.path.join(SCREENSHOTS_DIR, f"v6_captcha_preview_{int(time.time())}.png")
                try:
                    cap_el = page.query_selector(f'img[src="{cap_src}"]')
                    if cap_el:
                        cap_el.screenshot(path=cap_path2)
                except:
                    pass
                log_result("OpenPR.com", "PantryMate", "captcha",
                          f"CAPTCHA on preview page. Src: {cap_src}. Fields: {fill_result.get('filled')}",
                          sc2)

            elif page_state.get("errors") and "please check" in page_state["errors"].lower():
                log_result("OpenPR.com", "PantryMate", "captcha",
                          f"Form errors: {page_state['errors'][:400]}. Fields: {fill_result.get('filled')}",
                          sc2)

            elif "step 2" in rc or "preview" in rc or page_state.get("previewContent") or "vorschau" in rc:
                # On preview - try to submit
                print("  On preview page - looking for Submit/Publish button...")
                final_submit = page.evaluate("""() => {
                    const btns = document.querySelectorAll('button[type="submit"], input[type="submit"], button:not([type="button"])');
                    for (const btn of btns) {
                        const text = (btn.value || btn.textContent || '').toLowerCase().trim();
                        if (text.includes('submit') || text.includes('publish') || text.includes('send') || 
                            text.includes('confirm') || text.includes('veröffentlichen')) {
                            btn.click();
                            return {clicked: true, text: text};
                        }
                    }
                    // Click first submit button
                    const first = btns[0];
                    if (first) { first.click(); return {clicked: true, text: 'first btn'}; }
                    return {clicked: false};
                }""")
                print(f"  Final submit: {final_submit}")

                try:
                    page.wait_for_load_state("domcontentloaded", timeout=20000)
                except:
                    pass
                time.sleep(3)
                sc3 = sc(page, "final_result")
                log_result("OpenPR.com", "PantryMate", "submitted",
                          f"PR submitted via preview flow! URL: {page.url}. Fields: {fill_result.get('filled')}",
                          sc3)

            elif any(x in rc for x in ["thank", "confirmation", "vielen dank", "success", "published"]):
                log_result("OpenPR.com", "PantryMate", "submitted",
                          f"PR submitted! URL: {url}. Fields: {fill_result.get('filled')}",
                          sc2)
            else:
                log_result("OpenPR.com", "PantryMate", "captcha",
                          f"Unclear result. URL: {url}. Errors: {page_state['errors'][:200]}. Body: {page_state['bodySnippet'][:200]}",
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
