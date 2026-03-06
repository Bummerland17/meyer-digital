#!/usr/bin/env python3
"""Investigate page structure of difficult directories."""
import time
import os
from playwright.sync_api import sync_playwright

SCREENSHOTS_DIR = "/root/.openclaw/workspace/automation/screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def investigate(context, url, name):
    print(f"\n{'='*60}")
    print(f"Investigating: {name} — {url}")
    print(f"{'='*60}")
    page = context.new_page()
    try:
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        time.sleep(4)
        
        # Save screenshot
        path = os.path.join(SCREENSHOTS_DIR, f"investigate_{name}.png")
        page.screenshot(path=path)
        
        # Get all input fields
        inputs = page.query_selector_all("input, textarea, select")
        print(f"  Form elements found: {len(inputs)}")
        for el in inputs:
            try:
                tag = el.evaluate("el => el.tagName")
                name_attr = el.get_attribute("name") or ""
                type_attr = el.get_attribute("type") or ""
                placeholder = el.get_attribute("placeholder") or ""
                id_attr = el.get_attribute("id") or ""
                visible = el.is_visible()
                print(f"    <{tag.lower()} type={type_attr!r} name={name_attr!r} id={id_attr!r} placeholder={placeholder[:40]!r} visible={visible}>")
            except Exception as e:
                print(f"    Error reading element: {e}")
        
        # Get buttons
        buttons = page.query_selector_all("button, input[type='submit']")
        print(f"  Buttons found: {len(buttons)}")
        for btn in buttons:
            try:
                text = btn.inner_text()[:50] if btn.inner_text() else btn.get_attribute("value") or ""
                visible = btn.is_visible()
                print(f"    Button: {text!r} visible={visible}")
            except Exception:
                pass
        
        # Check title and URL
        print(f"  Final URL: {page.url}")
        print(f"  Page title: {page.title()}")
        
        # Check for specific content
        content = page.content().lower()
        indicators = ["login", "sign in", "sign up", "create account", "captcha", "recaptcha", "hcaptcha", "submit", "form"]
        found = [i for i in indicators if i in content]
        print(f"  Content indicators: {found}")
        
    except Exception as e:
        print(f"  Error: {e}")
    finally:
        page.close()


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
    
    targets = [
        ("https://www.uneed.be/submit-a-tool", "uneed"),
        ("https://www.launchingnext.com/submit", "launchingnext"),
        ("https://aitoolsdirectory.com/submit", "aitoolsdir_submit"),
        ("https://www.aicyclopedia.com/submit", "aicyclopedia"),
    ]
    
    for url, name in targets:
        investigate(context, url, name)
    
    browser.close()
