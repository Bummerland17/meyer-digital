const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const SCREENSHOTS_DIR = '/root/.openclaw/workspace/automation/screenshots';
fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function screenshot(page, name) {
  const p = path.join(SCREENSHOTS_DIR, name + '.png');
  await page.screenshot({ path: p, fullPage: true });
  console.log('📸', p);
}

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 }
  });

  const page = await context.newPage();
  
  try {
    console.log('Going to sources page...');
    await page.goto('https://www.helpareporter.com/sources', { waitUntil: 'networkidle', timeout: 30000 });
    
    // Fill email
    const emailInput = await page.waitForSelector('input[name="email"]', { timeout: 10000 });
    await emailInput.fill('hello@pantrymate.net');
    await sleep(300);
    
    // Set up response interceptor BEFORE clicking
    const postResponsePromise = page.waitForResponse(
      res => res.url().includes('helpareporter.com') && res.request().method() === 'POST',
      { timeout: 10000 }
    );
    
    // Click the button
    const signUpBtn = await page.$('button.bg-gray-700, button[type="submit"]');
    if (signUpBtn) {
      await signUpBtn.click();
    } else {
      // Try finding button by text near the input
      await page.evaluate(() => {
        const inputs = document.querySelectorAll('input[name="email"]');
        for (const input of inputs) {
          // Walk up and find submit button
          let p = input.parentElement;
          for (let i = 0; i < 5; i++) {
            if (!p) break;
            const btn = p.querySelector('button[type="submit"], input[type="submit"]');
            if (btn) {
              btn.click();
              return 'clicked submit';
            }
            p = p.parentElement;
          }
        }
        // Find any button that looks like Sign Up
        const buttons = document.querySelectorAll('button');
        for (const btn of buttons) {
          if (btn.textContent?.trim().toLowerCase() === 'sign up') {
            btn.click();
            return 'clicked sign up';
          }
        }
        return 'no button found';
      });
    }
    
    // Wait for POST response
    let postResponse;
    try {
      postResponse = await postResponsePromise;
      const responseBody = await postResponse.text();
      console.log('\n✅ POST Response received!');
      console.log('Status:', postResponse.status());
      console.log('Headers:', JSON.stringify(Object.fromEntries([...postResponse.headers()]), null, 2));
      console.log('Body (first 2000 chars):');
      console.log(responseBody.slice(0, 2000));
      
      // Save full body to file for analysis
      fs.writeFileSync('/root/.openclaw/workspace/automation/post-response.txt', responseBody);
      console.log('Full body saved to post-response.txt');
      
    } catch(e) {
      console.log('No POST response captured:', e.message);
    }
    
    // Wait for any DOM changes (toast, success message)
    await sleep(3000);
    await screenshot(page, 'after-submit-wait3s');
    
    // Check DOM for any notifications
    const notifications = await page.evaluate(() => {
      const selectors = [
        '[role="status"]', '[role="alert"]', '[role="log"]',
        '[class*="toast"]', '[class*="snack"]', '[class*="notif"]',
        '[class*="success"]', '[class*="error"]', '[class*="alert"]',
        '[data-sonner-toast]', '[data-radix-toast]'
      ];
      const results = [];
      for (const sel of selectors) {
        document.querySelectorAll(sel).forEach(el => {
          const text = el.textContent?.trim();
          if (text) results.push({ selector: sel, text });
        });
      }
      return results;
    });
    console.log('\nNotifications found:', notifications);
    
    // Get ALL body text after submit
    const fullText = await page.textContent('body');
    console.log('\nFull page text sample:', fullText?.slice(0, 500));
    
    // Also check for the specific "Adding email to subscriber list..." message
    if (fullText?.includes('Adding email')) {
      console.log('✅ Found "Adding email to subscriber list" message!');
    }
    if (fullText?.includes('success') || fullText?.includes('subscribed') || fullText?.includes('check your email')) {
      console.log('✅ Found success indicator in page text');
    }
    
    // Wait even longer for toasts
    await sleep(5000);
    await screenshot(page, 'after-submit-wait8s');
    
    const notifications2 = await page.evaluate(() => {
      const all = document.body.querySelectorAll('*');
      const results = [];
      for (const el of all) {
        if (el.children.length === 0) { // leaf nodes
          const text = el.textContent?.trim();
          if (text && text.length > 5 && text.length < 100 && 
              (text.toLowerCase().includes('success') || text.toLowerCase().includes('subscribed') || 
               text.toLowerCase().includes('check') || text.toLowerCase().includes('confirm') ||
               text.toLowerCase().includes('thank') || text.toLowerCase().includes('added') ||
               text.toLowerCase().includes('welcome'))) {
            results.push(text);
          }
        }
      }
      return results;
    });
    console.log('\nSuccess texts found:', notifications2);

  } catch (err) {
    console.error('❌ Error:', err.message);
    await screenshot(page, 'capture-error');
  } finally {
    await browser.close();
  }
})();
