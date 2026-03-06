/**
 * V5 - Final targeted submission script
 * 
 * Key findings:
 * - betalist: /submit is the correct URL; login form[1] is email/pw (form[0] is Twitter)
 * - saashub: /services/submit has a URL-first form, no login needed for step 1
 * - toolify: /submit page has URL input field to submit new tools
 * - uneed.be: Under maintenance
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
  category: 'AI Tools, Food, Productivity',
  email: 'hello@pantrymate.net',
};

const UNITFIX = {
  name: 'UnitFix',
  url: 'https://unitfix.app',
  tagline: 'Maintenance tracking for small landlords — tenants submit via link, no account needed',
  description: 'Maintenance request tracker for landlords. Each unit gets a public URL, tenants submit without an account, landlord tracks everything in one dashboard. Free + $29/mo.',
  category: 'Productivity, Real Estate',
  email: 'hello@pantrymate.net',
};

let sc = 0;
async function ss(page, label) {
  sc++;
  const fname = `v5-${String(sc).padStart(3,'0')}-${label.replace(/[^a-z0-9]/gi,'-').substring(0,60)}.png`;
  const fpath = path.join(SCREENSHOTS_DIR, fname);
  try { await page.screenshot({ path: fpath, fullPage: false }); } catch (e) {}
  console.log(`📸 ${fname}`);
  return fpath;
}
async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function doGoogleLogin(page, label = '') {
  console.log(`  [Google/${label}] at: ${page.url().substring(0, 70)}`);
  try {
    await page.waitForSelector('input[type="email"]', { timeout: 12000 });
    await page.fill('input[type="email"]', GOOGLE_EMAIL);
    await sleep(300);
    try { await page.click('#identifierNext', { timeout: 3000 }); } catch { await page.keyboard.press('Enter'); }
    await sleep(3000);
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
    await ss(page, `google-${label}-after-email`);
  } catch (e) { console.log('  Email err:', e.message.substring(0, 80)); return false; }
  
  try {
    await page.waitForSelector('input[type="password"]', { timeout: 12000 });
    await page.fill('input[type="password"]', GOOGLE_PASSWORD);
    await sleep(300);
    try { await page.click('#passwordNext', { timeout: 3000 }); } catch { await page.keyboard.press('Enter'); }
    await sleep(4000);
    await page.waitForLoadState('networkidle', { timeout: 20000 }).catch(() => {});
    await ss(page, `google-${label}-after-password`);
  } catch (e) { console.log('  Password err:', e.message.substring(0, 80)); return false; }
  
  if (page.url().includes('challenge') || page.url().includes('2-step')) return '2FA';
  return true;
}

// ============================================================
// BETALIST
// ============================================================
let blCtx = null, blPage = null, blAuthed = false;

async function ensureBetalistAuth(browser) {
  if (blAuthed) return true;
  blCtx = blCtx || await browser.newContext();
  blPage = blPage || await blCtx.newPage();
  
  await blPage.goto('https://betalist.com/sign_in', { timeout: 30000 });
  await sleep(2000);
  await ss(blPage, 'bl-login-page');
  
  const forms = await blPage.evaluate(() => 
    Array.from(document.querySelectorAll('form')).map(f => ({
      action: f.action, 
      inputs: Array.from(f.querySelectorAll('input')).map(i => i.name)
    }))
  );
  console.log('BL forms:', JSON.stringify(forms));
  
  // Fill the email/password form (form[1] based on our exploration)
  await blPage.fill('#user_email', GOOGLE_EMAIL);
  await sleep(200);
  await blPage.fill('#user_password', GOOGLE_PASSWORD);
  await sleep(200);
  await ss(blPage, 'bl-login-filled');
  
  // Submit specifically the email/password form (form index 1)
  await blPage.evaluate(() => {
    // Get all forms and find the one with email/password
    const forms = document.querySelectorAll('form');
    for (const form of forms) {
      if (form.action.includes('sign_in') && form.querySelector('input[name="user[email]"]')) {
        // Dispatch submit event 
        const event = new Event('submit', { bubbles: true, cancelable: true });
        form.dispatchEvent(event);
        // Also try direct submit
        setTimeout(() => form.submit(), 100);
        return;
      }
    }
  });
  
  await sleep(4000);
  await blPage.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
  await ss(blPage, 'bl-after-login');
  console.log('  BL after login URL:', blPage.url());
  
  const currentText = await blPage.evaluate(() => document.body.innerText.substring(0, 200));
  if (blPage.url().includes('sign_in') || currentText.includes('Sign in to get started')) {
    console.log('  Login via form dispatch failed, trying fetch...');
    
    // Get the authenticity token
    const token = await blPage.evaluate(() => {
      const forms = document.querySelectorAll('form');
      for (const form of forms) {
        if (form.querySelector('input[name="user[email]"]')) {
          return form.querySelector('input[name="authenticity_token"]')?.value;
        }
      }
      return null;
    });
    
    if (token) {
      console.log('  Got token, trying direct form navigation...');
      // Navigate to sign_in with POST using fetch
      await blPage.evaluate(async ({ email, password, token }) => {
        const resp = await fetch('/sign_in', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: `authenticity_token=${encodeURIComponent(token)}&user[email]=${encodeURIComponent(email)}&user[password]=${encodeURIComponent(password)}&commit=Sign+in+with+email`,
          redirect: 'follow'
        });
        return resp.url;
      }, { email: GOOGLE_EMAIL, password: GOOGLE_PASSWORD, token });
      
      await sleep(2000);
      await blPage.reload({ timeout: 15000 }).catch(() => {});
      await sleep(2000);
      await ss(blPage, 'bl-after-fetch-login');
      console.log('  After fetch login URL:', blPage.url());
    }
  }
  
  // Check if we're logged in
  const isLoggedIn = !blPage.url().includes('sign_in') && !blPage.url().includes('sign_up');
  if (isLoggedIn) {
    blAuthed = true;
    console.log('  ✅ BL logged in!');
  } else {
    console.log('  ❌ BL login failed');
  }
  
  return blAuthed;
}

async function doBetalist(browser, product) {
  console.log(`\n=== BETALIST.COM - ${product.name} ===`);
  const r = { site: 'betalist.com', product: product.name };
  
  try {
    await ensureBetalistAuth(browser);
    
    // Navigate to betalist.com/submit
    await blPage.goto('https://betalist.com/submit', { timeout: 30000 });
    await sleep(2000);
    await ss(blPage, `bl-${product.name}-submit-page`);
    console.log('  Submit page URL:', blPage.url());
    
    if (blPage.url().includes('sign')) {
      return { ...r, status: 'AUTH_REQUIRED', url: blPage.url() };
    }
    
    const pageText = await blPage.evaluate(() => document.body.innerText.substring(0, 500));
    console.log('  Page text:', pageText.substring(0, 200));
    
    const inputs = await blPage.evaluate(() =>
      Array.from(document.querySelectorAll('input:not([type=hidden]):not([type=submit]), textarea')).map(el => ({
        tag: el.tagName, type: el.type, name: el.name, id: el.id, placeholder: el.placeholder,
        label: document.querySelector(`label[for="${el.id}"]`)?.textContent?.trim()
      }))
    );
    console.log('  Inputs:', JSON.stringify(inputs));
    
    if (inputs.length === 0) {
      return { ...r, status: 'NO_FORM', url: blPage.url(), note: pageText.substring(0, 150) };
    }
    
    let filled = false;
    for (const inp of inputs) {
      const sel = inp.id ? `#${inp.id}` : inp.name ? `[name="${inp.name}"]` : null;
      if (!sel) continue;
      const key = (inp.label || inp.placeholder || inp.name || inp.id || '').toLowerCase();
      let val = null;
      if (key.includes('name') || key.includes('startup') || key.includes('product') || key.includes('title')) val = product.name;
      else if (key.includes('url') || key.includes('website') || key.includes('link')) val = product.url;
      else if (key.includes('tagline') || key.includes('headline') || key.includes('pitch')) val = product.tagline;
      else if (key.includes('desc') || key.includes('about')) val = product.description;
      else if (key.includes('email') || key.includes('contact')) val = product.email;
      if (val) { try { await blPage.fill(sel, val); filled = true; console.log(`  Filled: ${sel}`); } catch(e) {} }
    }
    
    await ss(blPage, `bl-${product.name}-form-filled`);
    
    if (filled) {
      // Try to submit via JS
      const ok = await blPage.evaluate(() => {
        const btn = document.querySelector('button[type="submit"], input[type="submit"]');
        if (btn) { btn.click(); return 'clicked'; }
        const form = document.querySelector('form');
        if (form) { form.submit(); return 'form-submit'; }
        return null;
      });
      console.log('  Submit result:', ok);
      await sleep(4000);
      await ss(blPage, `bl-${product.name}-after-submit`);
      console.log('  After submit URL:', blPage.url());
      return { ...r, status: 'SUBMITTED', url: blPage.url() };
    }
    
    return { ...r, status: 'NO_FILL', url: blPage.url() };
  } catch (e) {
    console.log('  Error:', e.message.substring(0, 150));
    return { ...r, status: 'ERROR', error: e.message.substring(0, 150) };
  }
}

// ============================================================
// SAASHUB - /services/submit has URL-first form, no login needed for step 1
// ============================================================
async function doSaashub(browser, product) {
  console.log(`\n=== SAASHUB.COM - ${product.name} ===`);
  const ctx = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });
  const page = await ctx.newPage();
  const r = { site: 'saashub.com', product: product.name };
  
  try {
    await page.goto('https://www.saashub.com/services/submit', { timeout: 30000, waitUntil: 'domcontentloaded' });
    await sleep(3000);
    await ss(page, `sh-${product.name}-submit-page`);
    console.log('  URL:', page.url());
    
    const pageText = await page.evaluate(() => document.body.innerText.substring(0, 400));
    console.log('  Text:', pageText.substring(0, 200));
    
    // Check if CF is blocking
    if (pageText.includes('security verification') || pageText.includes('Cloudflare')) {
      console.log('  CF blocking /services/submit');
      await sleep(8000);
      const text2 = await page.evaluate(() => document.body.innerText.substring(0, 200));
      if (text2.includes('security verification')) {
        return { ...r, status: 'CLOUDFLARE_BLOCKED' };
      }
    }
    
    // Find URL input
    const urlInput = await page.$('input[placeholder*="http"], input[type="url"], input[name*="url"], input[id*="url"]');
    if (!urlInput) {
      const allInputs = await page.$$eval('input, textarea', els => els.map(el => ({ type: el.type, name: el.name, id: el.id, placeholder: el.placeholder })));
      console.log('  Inputs:', JSON.stringify(allInputs));
      return { ...r, status: 'NO_URL_INPUT', url: page.url(), text: pageText.substring(0, 150) };
    }
    
    console.log('  Found URL input, filling...');
    await urlInput.fill(product.url);
    await sleep(500);
    await ss(page, `sh-${product.name}-url-filled`);
    
    // Click Continue
    const continueBtn = await page.$('button:has-text("Continue"), input[type="submit"], button[type="submit"]');
    if (continueBtn) {
      await continueBtn.click();
      await sleep(3000);
      await ss(page, `sh-${product.name}-after-continue`);
      console.log('  After Continue URL:', page.url());
    }
    
    // Step 2: Check what's on the next page
    const step2Text = await page.evaluate(() => document.body.innerText.substring(0, 400));
    console.log('  Step 2 text:', step2Text.substring(0, 200));
    
    // Check if we need to log in now
    if (page.url().includes('login') || page.url().includes('sign_in') || page.url().includes('register')) {
      console.log('  Need to login for step 2');
      return { ...r, status: 'LOGIN_REQUIRED_STEP2', url: page.url() };
    }
    
    // Fill step 2 form fields
    const step2Inputs = await page.$$eval('input:not([type=hidden]):not([type=submit]), textarea, select', els =>
      els.map(el => ({ tag: el.tagName, type: el.type, name: el.name, id: el.id, placeholder: el.placeholder }))
    );
    console.log('  Step 2 inputs:', JSON.stringify(step2Inputs));
    
    let filled2 = false;
    for (const inp of step2Inputs) {
      const sel = inp.id ? `#${inp.id}` : inp.name ? `[name="${inp.name}"]` : null;
      if (!sel) continue;
      const key = (inp.placeholder || inp.name || inp.id || '').toLowerCase();
      let val = null;
      if (key.includes('name') || key.includes('product') || key.includes('title')) val = product.name;
      else if (key.includes('url') || key.includes('website')) val = product.url;
      else if (key.includes('tagline') || key.includes('short')) val = product.tagline;
      else if (key.includes('desc') || key.includes('about')) val = product.description;
      else if (key.includes('email')) val = product.email;
      if (val) { try { await page.fill(sel, val); filled2 = true; console.log(`  Step2 filled: ${sel}`); } catch(e) {} }
    }
    
    if (filled2) {
      await ss(page, `sh-${product.name}-step2-filled`);
      const submitBtn = await page.$('button[type="submit"], input[type="submit"], button:has-text("Submit"), button:has-text("Save")');
      if (submitBtn) {
        await submitBtn.click();
        await sleep(4000);
        await ss(page, `sh-${product.name}-submitted`);
        console.log('  Final URL:', page.url());
        return { ...r, status: 'SUBMITTED', url: page.url() };
      }
    }
    
    // Even if we only filled step 1, that's progress
    return { ...r, status: 'STEP1_COMPLETED', url: page.url(), note: step2Text.substring(0, 150) };
  } catch (e) {
    console.log('  Error:', e.message.substring(0, 150));
    await ss(page, `sh-${product.name}-error`).catch(() => {});
    return { ...r, status: 'ERROR', error: e.message.substring(0, 150) };
  } finally {
    await ctx.close();
  }
}

// ============================================================
// TOOLIFY - Use URL input on /submit page (login flow + submit)
// ============================================================
let tfCtx = null, tfPage = null, tfAuthed = false;

async function ensureToolifyAuth(browser) {
  if (tfAuthed) return true;
  
  tfCtx = tfCtx || await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });
  tfPage = tfPage || await tfCtx.newPage();
  
  // Visit login page directly
  await tfPage.goto('https://www.toolify.ai/login', { timeout: 30000, waitUntil: 'domcontentloaded' });
  await sleep(3000);
  await ss(tfPage, 'tf-login-page');
  console.log('  TF login page URL:', tfPage.url());
  
  const loginText = await tfPage.evaluate(() => document.body.innerText.substring(0, 300));
  console.log('  Login page text:', loginText.substring(0, 150));
  
  // Look for "Continue with Google" button
  const googleBtn = await tfPage.$('button:has-text("Continue with Google"), button:has-text("Google"), a:has-text("Google")');
  if (googleBtn) {
    console.log('  Found Google button on login page');
    
    // Click and see if it stays on page or goes to Google
    const [popup] = await Promise.all([
      tfCtx.waitForEvent('page', { timeout: 5000 }).catch(() => null),
      googleBtn.click()
    ]);
    await sleep(3000);
    
    if (popup) {
      await popup.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
      console.log('  Google popup URL:', popup.url().substring(0, 70));
      if (popup.url().includes('google')) {
        const result = await doGoogleLogin(popup, 'tf-popup');
        if (result === '2FA') return '2FA';
        await popup.waitForEvent('close', { timeout: 15000 }).catch(() => {});
        await sleep(2000);
      }
    } else {
      await tfPage.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
      if (tfPage.url().includes('google') || tfPage.url().includes('accounts')) {
        const result = await doGoogleLogin(tfPage, 'tf-same');
        if (result === '2FA') return '2FA';
        await sleep(3000);
        await tfPage.waitForLoadState('domcontentloaded', { timeout: 15000 }).catch(() => {});
      }
    }
    
    await ss(tfPage, 'tf-after-google-auth');
    console.log('  After Google auth URL:', tfPage.url().substring(0, 70));
    
    if (!tfPage.url().includes('accounts.google.com') && !tfPage.url().includes('login')) {
      tfAuthed = true;
      console.log('  ✅ Toolify logged in!');
      return true;
    }
  }
  
  // Try email/password login
  const emailInput = await tfPage.$('input[type="email"], input[name="email"], input[placeholder*="email" i]');
  const pwdInput = await tfPage.$('input[type="password"]');
  if (emailInput && pwdInput) {
    console.log('  Trying email/password login...');
    await emailInput.fill(GOOGLE_EMAIL);
    await pwdInput.fill(GOOGLE_PASSWORD);
    await ss(tfPage, 'tf-email-pw-filled');
    await pwdInput.press('Enter');
    await sleep(4000);
    await tfPage.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
    await ss(tfPage, 'tf-after-email-pw');
    console.log('  After email/pw URL:', tfPage.url().substring(0, 70));
    if (!tfPage.url().includes('login')) {
      tfAuthed = true;
      return true;
    }
  }
  
  return false;
}

async function doToolify(browser, product) {
  console.log(`\n=== TOOLIFY.AI - ${product.name} ===`);
  const r = { site: 'toolify.ai', product: product.name };
  
  try {
    const authResult = await ensureToolifyAuth(browser);
    if (authResult === '2FA') return { ...r, status: 'NEED_2FA_CODE' };
    
    await ss(tfPage, `tf-${product.name}-auth-state`);
    console.log('  Auth state URL:', tfPage.url().substring(0, 70));
    
    // Navigate to the submit page
    await tfPage.goto('https://www.toolify.ai/submit', { timeout: 30000, waitUntil: 'domcontentloaded' });
    await sleep(3000);
    await ss(tfPage, `tf-${product.name}-submit-page`);
    console.log('  Submit page URL:', tfPage.url());
    
    // Find the URL input field ("Please enter the tool url, such as...")
    const urlInputField = await tfPage.$('input[placeholder*="enter the tool url"], input[placeholder*="tool url"], input[placeholder*="copy.ai"]');
    if (urlInputField) {
      console.log('  Found URL input field on submit page');
      await urlInputField.fill(product.url);
      await sleep(500);
      await ss(tfPage, `tf-${product.name}-url-filled`);
      
      // Check for a submit button near this input or just press Enter
      const submitBtn = await tfPage.$('button:has-text("Submit"), button[type="submit"], button:has-text("Search"), button:has-text("Go")');
      if (submitBtn) {
        await submitBtn.click();
      } else {
        await urlInputField.press('Enter');
      }
      
      await sleep(4000);
      await tfPage.waitForLoadState('domcontentloaded', { timeout: 15000 }).catch(() => {});
      await ss(tfPage, `tf-${product.name}-after-url-submit`);
      console.log('  After URL submit URL:', tfPage.url());
      
      const resultText = await tfPage.evaluate(() => document.body.innerText.substring(0, 500));
      console.log('  Result text:', resultText.substring(0, 300));
      
      // If redirected to a tool detail/edit page
      if (tfPage.url() !== 'https://www.toolify.ai/submit') {
        return { ...r, status: 'URL_SUBMITTED', url: tfPage.url() };
      }
      
      // Fill any additional form that appeared
      const newInputs = await tfPage.$$eval('input:not([type=hidden]):not([type=radio]):not([name="toolifySearch"]), textarea', els =>
        els.map(el => ({ type: el.type, name: el.name, id: el.id, placeholder: el.placeholder }))
      );
      console.log('  New inputs:', JSON.stringify(newInputs));
      
      let filled = false;
      for (const inp of newInputs) {
        const sel = inp.id ? `#${inp.id}` : inp.name ? `[name="${inp.name}"]` : null;
        if (!sel) continue;
        const key = (inp.placeholder || inp.name || inp.id || '').toLowerCase();
        let val = null;
        if (key.includes('name') || key.includes('title') || key.includes('tool')) val = product.name;
        else if (key.includes('url') || key.includes('link') || key.includes('website')) val = product.url;
        else if (key.includes('tagline') || key.includes('slogan')) val = product.tagline;
        else if (key.includes('desc')) val = product.description;
        else if (key.includes('email')) val = product.email;
        if (val) { try { await tfPage.fill(sel, val); filled = true; } catch(e) {} }
      }
      
      await ss(tfPage, `tf-${product.name}-form-filled`);
      
      if (filled) {
        const finalBtn = await tfPage.$('button[type="submit"], button:has-text("Submit")');
        if (finalBtn) {
          await finalBtn.click();
          await sleep(3000);
          await ss(tfPage, `tf-${product.name}-submitted`);
          return { ...r, status: 'SUBMITTED', url: tfPage.url() };
        }
      }
      
      return { ...r, status: 'URL_ENTERED', url: tfPage.url(), note: resultText.substring(0, 150) };
    }
    
    const pageText = await tfPage.evaluate(() => document.body.innerText.substring(0, 300));
    console.log('  No URL input found. Page text:', pageText.substring(0, 200));
    return { ...r, status: 'NO_URL_INPUT', url: tfPage.url() };
  } catch (e) {
    console.log('  Error:', e.message.substring(0, 150));
    await ss(tfPage, `tf-${product.name}-error`).catch(() => {});
    return { ...r, status: 'ERROR', error: e.message.substring(0, 150) };
  }
}

// ============================================================
// MAIN
// ============================================================
async function main() {
  console.log('=== V5 - Final Submission Run ===\n');
  
  const browser = await chromium.launch({
    headless: true, slowMo: 80,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });
  
  const results = [
    { site: 'uneed.be', product: 'PantryMate', status: 'SITE_UNDER_MAINTENANCE', note: 'uneed.be shows "Please stand by while configuration is in progress."' },
    { site: 'uneed.be', product: 'UnitFix', status: 'SITE_UNDER_MAINTENANCE', note: 'uneed.be shows "Please stand by while configuration is in progress."' },
  ];
  
  try {
    results.push(await doBetalist(browser, PANTRYMATE));
    results.push(await doBetalist(browser, UNITFIX));
    results.push(await doSaashub(browser, PANTRYMATE));
    results.push(await doSaashub(browser, UNITFIX));
    results.push(await doToolify(browser, PANTRYMATE));
    results.push(await doToolify(browser, UNITFIX));
  } finally {
    if (blCtx) await blCtx.close().catch(() => {});
    if (tfCtx) await tfCtx.close().catch(() => {});
    await browser.close();
  }
  
  console.log('\n=== FINAL RESULTS ===');
  console.log(JSON.stringify(results, null, 2));
}

main().catch(console.error);
