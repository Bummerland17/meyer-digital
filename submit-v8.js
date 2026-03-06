/**
 * V8 - Precise final fixes:
 * 1. Toolify: Select radio[value=1] (free tier) BEFORE clicking form button
 * 2. SaaSHub: Click the "Free" button explicitly (not $75)
 * 3. SaaSHub UnitFix: Handle "register to submit more than one product" limit
 */

const { chromium } = require('/root/.openclaw/workspace/node_modules/playwright');
const path = require('path');

const SCREENSHOTS_DIR = '/root/.openclaw/workspace/assets/screenshots';

const PANTRYMATE = {
  name: 'PantryMate',
  url: 'https://pantrymate.net',
  tagline: 'Scan your pantry, get dinner suggestions in 30 seconds',
  email: 'hello@pantrymate.net',
  categories: ['AI', 'Food'],
  competitors: ['Whisk'],
};

const UNITFIX = {
  name: 'UnitFix',
  url: 'https://unitfix.app',
  tagline: 'Maintenance tracking for small landlords — tenants submit via link, no account needed',
  email: 'hello@pantrymate.net',
  categories: ['Productivity', 'Real Estate'],
  competitors: ['Buildium'],
};

let sc = 0;
async function ss(page, label) {
  sc++;
  const fname = `v8-${String(sc).padStart(3,'0')}-${label.replace(/[^a-z0-9]/gi,'-').substring(0,60)}.png`;
  const fpath = path.join(SCREENSHOTS_DIR, fname);
  try { await page.screenshot({ path: fpath, fullPage: false }); } catch (e) {}
  console.log(`📸 ${fname}`);
  return fpath;
}
async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ============================================================
// TOOLIFY - Select radio[value=1] for free, then click
// ============================================================
async function doToolify(browser, product) {
  console.log(`\n=== TOOLIFY.AI - ${product.name} ===`);
  const ctx = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });
  const page = await ctx.newPage();
  const r = { site: 'toolify.ai', product: product.name };
  
  try {
    await page.goto('https://www.toolify.ai/submit', { timeout: 30000, waitUntil: 'domcontentloaded' });
    await sleep(3000);
    await ss(page, `tf-${product.name}-page`);
    
    // Fill Name and URL
    const nameInput = await page.$('input[placeholder="Copy AI"]');
    if (nameInput) await nameInput.fill(product.name);
    
    const urlInput = await page.$('input[placeholder*="enter the tool url"]');
    if (urlInput) await urlInput.fill(product.url);
    
    await sleep(500);
    
    // Check radio buttons in the form - select value=1 (free tier)
    const radioInfo = await page.evaluate(() => {
      const radios = Array.from(document.querySelectorAll('form.el-form input[type="radio"]'));
      return radios.map(r => ({ value: r.value, checked: r.checked, id: r.id, name: r.name }));
    });
    console.log('  Radio buttons:', JSON.stringify(radioInfo));
    
    // Select radio with value=1 (free)
    const selectedRadio = await page.evaluate(() => {
      const radios = Array.from(document.querySelectorAll('form.el-form input[type="radio"]'));
      const freeRadio = radios.find(r => r.value === '1');
      if (freeRadio) {
        freeRadio.click();
        // Also trigger change event
        freeRadio.dispatchEvent(new Event('change', { bubbles: true }));
        return 'selected-value-1';
      }
      // Just select the first one
      if (radios[0]) { radios[0].click(); return 'selected-first'; }
      return 'no-radio';
    });
    console.log('  Radio selection:', selectedRadio);
    await sleep(500);
    
    await ss(page, `tf-${product.name}-radio-selected`);
    
    // Get button text after radio selection to see if it changed
    const btnText = await page.evaluate(() => {
      const form = document.querySelector('form.el-form');
      if (!form) return null;
      const btn = form.querySelector('button');
      return btn?.textContent?.trim();
    });
    console.log('  Button text after radio selection:', btnText);
    
    // Click the form button
    const formBtnClicked = await page.evaluate(() => {
      const form = document.querySelector('form.el-form');
      if (!form) return 'no-form';
      const btn = form.querySelector('button');
      if (btn) { btn.click(); return 'clicked:' + btn.textContent?.trim(); }
      return 'no-btn';
    });
    console.log('  Form button clicked:', formBtnClicked);
    
    await sleep(3000);
    await ss(page, `tf-${product.name}-after-click`);
    console.log('  After click URL:', page.url());
    
    // Check what happened
    const afterText = await page.evaluate(() => document.body.innerText.substring(0, 400));
    console.log('  After text:', afterText.substring(0, 200));
    
    // Look for login requirement
    if (afterText.includes('Sign in') && afterText.includes('Continue with Google')) {
      console.log('  Got redirected to login page');
      return { ...r, status: 'LOGIN_REQUIRED', note: 'Toolify requires login to submit tools. Google OAuth blocked by "insecure browser" in headless mode.' };
    }
    
    // Look for success
    if (page.url() !== 'https://www.toolify.ai/submit') {
      return { ...r, status: 'REDIRECTED', url: page.url() };
    }
    
    // Check for any dialog with payment/free options
    const dialogInfo = await page.evaluate(() => {
      const dialogs = document.querySelectorAll('[class*="dialog"], [class*="modal"], [role="dialog"]');
      return Array.from(dialogs).map(d => ({
        text: d.innerText?.substring(0, 200),
        btns: Array.from(d.querySelectorAll('button')).map(b => b.textContent?.trim())
      }));
    });
    console.log('  Dialogs:', JSON.stringify(dialogInfo));
    
    if (dialogInfo.length > 0) {
      await ss(page, `tf-${product.name}-dialog`);
      // Try to click "No" or free option in dialog via JS
      const freeClicked = await page.evaluate(() => {
        const dialogs = document.querySelectorAll('[class*="dialog"], [class*="modal"], [role="dialog"]');
        for (const d of dialogs) {
          const btns = Array.from(d.querySelectorAll('button'));
          for (const btn of btns) {
            const text = btn.textContent?.trim().toLowerCase();
            if (text === 'no' || text === 'skip' || text === 'free' || text === 'cancel' || text === 'later') {
              btn.click();
              return 'clicked:' + text;
            }
          }
        }
        return 'no-free-btn';
      });
      console.log('  Free option clicked:', freeClicked);
      await sleep(2000);
      await ss(page, `tf-${product.name}-after-dialog`);
    }
    
    return { ...r, status: 'FORM_FILLED', note: `Form filled with name/URL. Requires login (Google OAuth blocked in headless). Button: ${formBtnClicked}` };
  } catch (e) {
    console.log('  Error:', e.message.substring(0, 150));
    await ss(page, `tf-${product.name}-error`).catch(() => {});
    return { ...r, status: 'ERROR', error: e.message.substring(0, 150) };
  } finally {
    await ctx.close();
  }
}

// ============================================================
// SAASHUB - Click "Free" button explicitly  
// ============================================================
async function doSaashub(browser, product, useNewContext = true) {
  console.log(`\n=== SAASHUB.COM - ${product.name} ===`);
  const ctx = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });
  const page = await ctx.newPage();
  const r = { site: 'saashub.com', product: product.name };
  
  try {
    await page.goto('https://www.saashub.com/services/submit', { timeout: 30000, waitUntil: 'domcontentloaded' });
    await sleep(3000);
    
    const t0 = await page.evaluate(() => document.body.innerText.substring(0, 100));
    if (t0.includes('security verification') || t0.includes('Cloudflare')) {
      await sleep(10000);
      const t1 = await page.evaluate(() => document.body.innerText.substring(0, 100));
      if (t1.includes('security verification')) return { ...r, status: 'CLOUDFLARE_BLOCKED' };
    }
    
    // Step 1: URL
    const urlInput = await page.$('input[placeholder*="http"], input[type="url"]');
    if (!urlInput) return { ...r, status: 'NO_URL_INPUT' };
    
    await urlInput.fill(product.url);
    const continueBtn = await page.$('input[type="submit"][value="Continue"]');
    if (continueBtn) await continueBtn.click();
    else await urlInput.press('Enter');
    
    await sleep(3000);
    await ss(page, `sh-${product.name}-step2`);
    console.log('  Step 2 URL:', page.url());
    
    const s2text = await page.evaluate(() => document.body.innerText.substring(0, 300));
    console.log('  Step 2 text:', s2text.substring(0, 200));
    
    if (page.url().includes('login') || page.url().includes('sign_in')) {
      return { ...r, status: 'LOGIN_REQUIRED', url: page.url() };
    }
    
    if (s2text.includes('register to submit more than one product')) {
      return { ...r, status: 'LIMIT_ONE_PER_IP', note: 'SaaSHub limits unregistered users to 1 product' };
    }
    
    // Step 2: Fill form
    const nameInput = await page.$('#service_name');
    if (nameInput) await nameInput.fill(product.name);
    
    const taglineInput = await page.$('#service_tagline');
    if (taglineInput) await taglineInput.fill(product.tagline);
    
    const emailInput = await page.$('#service_contact_email');
    if (emailInput) await emailInput.fill(product.email);
    
    // Fill categories
    for (const cat of product.categories.slice(0, 2)) {
      const catInput = await page.$('#react-select-2-input');
      if (catInput) {
        await catInput.click();
        await catInput.fill(cat.substring(0, 3));
        await sleep(1500);
        const option = await page.$('.react-select__option, [id*="react-select-2-option"]');
        if (option) {
          await option.click();
          await sleep(500);
          console.log('  Added category:', cat);
        } else {
          await catInput.press('Escape');
          await sleep(300);
        }
      }
    }
    
    // Fill competitors
    for (const comp of product.competitors.slice(0, 1)) {
      const compInput = await page.$('#react-select-3-input');
      if (compInput) {
        await compInput.click();
        await compInput.fill(comp.substring(0, 5));
        await sleep(1500);
        const option = await page.$('.react-select__option, [id*="react-select-3-option"]');
        if (option) {
          await option.click();
          await sleep(500);
          console.log('  Added competitor:', comp);
        } else {
          await compInput.press('Escape');
          await sleep(300);
        }
      }
    }
    
    await ss(page, `sh-${product.name}-form-filled`);
    
    // Scroll down to see all buttons
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await sleep(1000);
    await ss(page, `sh-${product.name}-scrolled-down`);
    
    // Find and click the "Free" button specifically
    const freeBtn = await page.$('button.bg-gray-100, button:has-text("Free")');
    if (freeBtn) {
      const freeBtnText = await freeBtn.evaluate(el => el.textContent?.trim());
      console.log('  Found Free button:', freeBtnText);
      
      // Click using JS to bypass any overlay
      await freeBtn.evaluate(el => el.click());
      await sleep(4000);
      await ss(page, `sh-${product.name}-after-free-click`);
      console.log('  After Free click URL:', page.url());
      
      const afterText = await page.evaluate(() => document.body.innerText.substring(0, 500));
      console.log('  After text:', afterText.substring(0, 300));
      
      if (afterText.includes('Thank') || afterText.includes('success') || afterText.includes('We will review') || 
          afterText.includes('submit') && afterText.includes('queue')) {
        return { ...r, status: 'SUBMITTED_FREE', url: page.url() };
      }
      
      if (page.url().includes('services/new') || page.url().includes('services/submit')) {
        if (!afterText.includes('Please select at least one category')) {
          return { ...r, status: 'SUBMITTED_FREE', url: page.url() };
        }
        return { ...r, status: 'CATEGORY_REQUIRED', url: page.url() };
      }
      
      if (!page.url().includes('saashub.com/services/new') && !page.url().includes('checkout')) {
        return { ...r, status: 'SUBMITTED_FREE', url: page.url() };
      }
      
      return { ...r, status: 'SUBMIT_ATTEMPTED', url: page.url(), note: afterText.substring(0, 150) };
    }
    
    // Log all buttons for debugging
    const allBtns = await page.$$eval('button', els => els.map(el => el.textContent?.trim()).filter(t => t));
    console.log('  All button texts:', JSON.stringify(allBtns));
    
    return { ...r, status: 'NO_FREE_BTN', url: page.url() };
  } catch (e) {
    console.log('  Error:', e.message.substring(0, 150));
    await ss(page, `sh-${product.name}-error`).catch(() => {});
    return { ...r, status: 'ERROR', error: e.message.substring(0, 150) };
  } finally {
    await ctx.close();
  }
}

// ============================================================
// MAIN
// ============================================================
async function main() {
  console.log('=== V8 - Toolify Radio + SaaSHub Free Button ===\n');
  
  const browser = await chromium.launch({
    headless: true, slowMo: 80,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });
  
  const results = [];
  
  try {
    results.push(await doToolify(browser, PANTRYMATE));
    results.push(await doToolify(browser, UNITFIX));
    results.push(await doSaashub(browser, PANTRYMATE));
    results.push(await doSaashub(browser, UNITFIX));
  } finally {
    await browser.close();
  }
  
  console.log('\n=== FINAL RESULTS ===');
  console.log(JSON.stringify(results, null, 2));
}

main().catch(console.error);
