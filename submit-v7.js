/**
 * V7 - Final submission fixes:
 * 1. Toolify: Fill form, click the BUTTON[type=button], handle payment dialog with "No" 
 * 2. SaaSHub: Fill categories via react-select, find free submit button
 * 3. BetaList: Use magic link signup - report as needs manual verification
 */

const { chromium } = require('/root/.openclaw/workspace/node_modules/playwright');
const path = require('path');

const SCREENSHOTS_DIR = '/root/.openclaw/workspace/assets/screenshots';
const GOOGLE_EMAIL = 'olcowboy21@gmail.com';
const GOOGLE_PASSWORD = 'Bummerland20';

const PANTRYMATE = {
  name: 'PantryMate',
  url: 'https://pantrymate.net',
  tagline: 'Scan your pantry, get dinner suggestions in 30 seconds',
  description: 'AI meal planning app — scan pantry or receipt, get meals you can cook tonight from what you have. Free tier + $14.99/mo Pro Plus or $49 lifetime deal.',
  email: 'hello@pantrymate.net',
  categories: ['AI', 'Food', 'Productivity'],
  competitors: ['Whisk', 'Mealime', 'Paprika'],
};

const UNITFIX = {
  name: 'UnitFix',
  url: 'https://unitfix.app',
  tagline: 'Maintenance tracking for small landlords — tenants submit via link, no account needed',
  description: 'Maintenance request tracker for landlords. Each unit gets a public URL, tenants submit without an account, landlord tracks everything in one dashboard. Free + $29/mo.',
  email: 'hello@pantrymate.net',
  categories: ['Productivity', 'Real Estate', 'Property Management'],
  competitors: ['Buildium', 'AppFolio', 'Rentec Direct'],
};

let sc = 0;
async function ss(page, label) {
  sc++;
  const fname = `v7-${String(sc).padStart(3,'0')}-${label.replace(/[^a-z0-9]/gi,'-').substring(0,60)}.png`;
  const fpath = path.join(SCREENSHOTS_DIR, fname);
  try { await page.screenshot({ path: fpath, fullPage: false }); } catch (e) {}
  console.log(`📸 ${fname}`);
  return fpath;
}
async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ============================================================
// TOOLIFY - Fill form, click button, handle payment dialog
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
    
    // Fill Name field
    const nameInput = await page.$('input[placeholder="Copy AI"]');
    if (nameInput) {
      await nameInput.fill(product.name);
      console.log('  Filled name:', product.name);
    }
    
    // Fill URL field
    const urlInput = await page.$('input[placeholder*="enter the tool url"]');
    if (urlInput) {
      await urlInput.fill(product.url);
      console.log('  Filled URL:', product.url);
    }
    
    await ss(page, `tf-${product.name}-filled`);
    
    // Find the form's submit button (Element UI button inside the form)
    // It's a BUTTON[type="button"] - the last button in the form
    const formBtn = await page.evaluate(() => {
      const form = document.querySelector('form.el-form');
      if (!form) return null;
      const buttons = form.querySelectorAll('button');
      return buttons.length;
    });
    console.log('  Buttons in form:', formBtn);
    
    // Click the submit button in the form
    const clicked = await page.evaluate(() => {
      const form = document.querySelector('form.el-form');
      if (!form) return 'no-form';
      const buttons = Array.from(form.querySelectorAll('button'));
      const lastBtn = buttons[buttons.length - 1];
      if (lastBtn) { lastBtn.click(); return 'clicked-' + lastBtn.textContent?.trim(); }
      return 'no-button';
    });
    console.log('  Form button click result:', clicked);
    
    await sleep(3000);
    await ss(page, `tf-${product.name}-after-btn-click`);
    
    // Check for payment dialog / "No" button
    const noBtn = await page.$('button:has-text("No"), button:has-text("Skip"), button:has-text("Free"), button:has-text("Maybe later")');
    if (noBtn) {
      const noBtnText = await noBtn.evaluate(el => el.textContent?.trim());
      console.log('  Found "No/Skip" button:', noBtnText);
      await ss(page, `tf-${product.name}-payment-dialog`);
      await noBtn.click();
      await sleep(3000);
      await ss(page, `tf-${product.name}-after-no`);
      console.log('  After "No" URL:', page.url());
    }
    
    // Check for success or further steps
    const pageText = await page.evaluate(() => document.body.innerText.substring(0, 400));
    console.log('  Page text:', pageText.substring(0, 200));
    
    await ss(page, `tf-${product.name}-final`);
    
    // Check if tool was submitted (might redirect to tool page or show success)
    const currentUrl = page.url();
    if (currentUrl !== 'https://www.toolify.ai/submit') {
      return { ...r, status: 'SUBMITTED', url: currentUrl };
    }
    
    // Still on /submit - check if there's a dialog
    const dialogText = await page.evaluate(() => {
      const dialog = document.querySelector('[class*="dialog"], [class*="modal"], [role="dialog"]');
      return dialog?.innerText?.substring(0, 200);
    });
    console.log('  Dialog text:', dialogText);
    
    if (dialogText) {
      await ss(page, `tf-${product.name}-dialog-content`);
      return { ...r, status: 'DIALOG_SHOWN', url: currentUrl, note: dialogText };
    }
    
    return { ...r, status: 'FORM_FILLED', url: currentUrl, note: pageText.substring(0, 100) };
  } catch (e) {
    console.log('  Error:', e.message.substring(0, 150));
    await ss(page, `tf-${product.name}-error`).catch(() => {});
    return { ...r, status: 'ERROR', error: e.message.substring(0, 150) };
  } finally {
    await ctx.close();
  }
}

// ============================================================
// SAASHUB - With categories via react-select
// ============================================================
async function doSaashub(browser, product) {
  console.log(`\n=== SAASHUB.COM - ${product.name} ===`);
  const ctx = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });
  const page = await ctx.newPage();
  const r = { site: 'saashub.com', product: product.name };
  
  try {
    // Go to submit page
    await page.goto('https://www.saashub.com/services/submit', { timeout: 30000, waitUntil: 'domcontentloaded' });
    await sleep(3000);
    
    const text0 = await page.evaluate(() => document.body.innerText.substring(0, 150));
    if (text0.includes('security verification') || text0.includes('Cloudflare')) {
      console.log('  CF blocking - waiting...');
      await sleep(10000);
      const text1 = await page.evaluate(() => document.body.innerText.substring(0, 150));
      if (text1.includes('security verification')) {
        return { ...r, status: 'CLOUDFLARE_BLOCKED' };
      }
    }
    
    // Step 1: Enter URL
    const urlInput = await page.$('input[placeholder*="http"], input[type="url"]');
    if (!urlInput) return { ...r, status: 'NO_URL_INPUT' };
    
    await urlInput.fill(product.url);
    const continueBtn = await page.$('input[type="submit"][value="Continue"], button:has-text("Continue")');
    if (continueBtn) await continueBtn.click();
    else await urlInput.press('Enter');
    
    await sleep(3000);
    await ss(page, `sh-${product.name}-step2`);
    console.log('  Step 2 URL:', page.url());
    
    if (page.url().includes('login') || page.url().includes('sign_in')) {
      return { ...r, status: 'LOGIN_REQUIRED', url: page.url() };
    }
    
    // Fill basic fields
    const nameInput = await page.$('#service_name');
    if (nameInput) await nameInput.fill(product.name);
    
    const taglineInput = await page.$('#service_tagline');
    if (taglineInput) await taglineInput.fill(product.tagline);
    
    const emailInput = await page.$('#service_contact_email');
    if (emailInput) await emailInput.fill(product.email);
    
    // Fill categories via react-select
    // Find the categories select input
    const catInput = await page.$('#react-select-2-input');
    if (catInput) {
      for (const cat of product.categories.slice(0, 2)) {
        console.log('  Adding category:', cat);
        await catInput.click();
        await catInput.fill(cat.toLowerCase());
        await sleep(1500);
        
        // Look for dropdown options
        const option = await page.$('.react-select__option, [class*="option"], [id*="option"]');
        if (option) {
          const optionText = await option.evaluate(el => el.textContent?.trim());
          console.log('  Found option:', optionText);
          await option.click();
          await sleep(500);
        } else {
          // Try pressing Enter or Tab
          await catInput.press('Enter');
          await sleep(500);
        }
        
        await ss(page, `sh-${product.name}-cat-${cat.replace(/\s/g, '-')}`);
      }
    }
    
    // Fill competitors
    const compInput = await page.$('#react-select-3-input');
    if (compInput) {
      for (const comp of product.competitors.slice(0, 1)) {
        console.log('  Adding competitor:', comp);
        await compInput.click();
        await compInput.fill(comp.toLowerCase());
        await sleep(1500);
        
        const option = await page.$('.react-select__option, [class*="option"]');
        if (option) {
          await option.click();
          await sleep(500);
        } else {
          await compInput.press('Enter');
          await sleep(500);
        }
      }
    }
    
    await ss(page, `sh-${product.name}-all-filled`);
    
    // Look for all buttons
    const buttons = await page.$$eval('button, input[type="submit"]', els =>
      els.map(el => ({ tag: el.tagName, text: el.textContent?.trim() || el.value, class: el.className.substring(0, 60) }))
         .filter(b => b.text && b.text.length < 80)
    );
    console.log('  All buttons:', JSON.stringify(buttons));
    
    // Look for free submit button (not $75 paid)
    // The free submission should be labeled "Submit", "Submit for Free", or similar
    const submitBtn = await page.$('input[type="submit"][value*="Submit"], button:has-text("Submit for Free"), button:has-text("Submit Product")');
    if (submitBtn) {
      const btnText = await submitBtn.evaluate(el => el.textContent?.trim() || el.value);
      console.log('  Found free submit button:', btnText);
      await submitBtn.click();
    } else {
      // Try submitting the form via JS, skipping required fields that we can't fill
      const submitted = await page.evaluate(() => {
        const forms = document.querySelectorAll('form');
        for (const form of forms) {
          const action = form.action;
          if (action && !action.includes('newsletter')) {
            // Find actual submit button
            const btn = form.querySelector('input[type="submit"], button[type="submit"]');
            if (btn) { btn.click(); return 'form-clicked:' + btn.textContent; }
          }
        }
        return 'no-form-submit';
      });
      console.log('  JS submit result:', submitted);
    }
    
    await sleep(4000);
    await ss(page, `sh-${product.name}-after-submit`);
    console.log('  After submit URL:', page.url());
    
    const afterText = await page.evaluate(() => document.body.innerText.substring(0, 500));
    console.log('  After text:', afterText.substring(0, 300));
    
    // Check success
    if (afterText.includes('Thank') || afterText.includes('success') || afterText.includes('submitted') || 
        (!afterText.includes('Please select at least one category') && !afterText.includes('can\'t be blank'))) {
      if (!afterText.includes('Submit a New Software Product')) {
        return { ...r, status: 'SUBMITTED', url: page.url() };
      }
    }
    
    if (afterText.includes('Please select at least one category')) {
      return { ...r, status: 'CATEGORY_REQUIRED', url: page.url(), note: 'Could not fill react-select categories' };
    }
    
    return { ...r, status: 'SUBMIT_ATTEMPTED', url: page.url(), note: afterText.substring(0, 150) };
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
  console.log('=== V7 - Toolify + SaaSHub Final Fix ===\n');
  
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
