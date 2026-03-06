/**
 * V6 - Final fixes:
 * 1. SaaSHub: Fix form filling (don't map linkedin_url to product URL, handle react-select)
 * 2. Toolify: Use placeholder-based selectors to fill unnamed inputs, scroll to submit
 * 3. BetaList: Try to sign up (not sign in) with the email
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
};

const UNITFIX = {
  name: 'UnitFix',
  url: 'https://unitfix.app',
  tagline: 'Maintenance tracking for small landlords — tenants submit via link, no account needed',
  description: 'Maintenance request tracker for landlords. Each unit gets a public URL, tenants submit without an account, landlord tracks everything in one dashboard. Free + $29/mo.',
  email: 'hello@pantrymate.net',
};

let sc = 0;
async function ss(page, label) {
  sc++;
  const fname = `v6-${String(sc).padStart(3,'0')}-${label.replace(/[^a-z0-9]/gi,'-').substring(0,60)}.png`;
  const fpath = path.join(SCREENSHOTS_DIR, fname);
  try { await page.screenshot({ path: fpath, fullPage: false }); } catch (e) {}
  console.log(`📸 ${fname}`);
  return fpath;
}
async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ============================================================
// BETALIST - Try to register first, then submit
// ============================================================
async function doBetalist(browser, product) {
  console.log(`\n=== BETALIST.COM - ${product.name} ===`);
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  const r = { site: 'betalist.com', product: product.name };
  
  try {
    // Visit the submit page (which might redirect to login/register if not authed)
    await page.goto('https://betalist.com/submit', { timeout: 30000 });
    await sleep(2000);
    await ss(page, `bl-${product.name}-submit-direct`);
    console.log('  /submit URL:', page.url());
    
    const text = await page.evaluate(() => document.body.innerText.substring(0, 400));
    console.log('  Text:', text.substring(0, 200));
    
    // If it's a 404, the URL changed in their platform
    // Try the raw submit page
    if (page.url().includes('sign') || text.includes('sign in') || text.includes('Sign in')) {
      // Register first
      await page.goto('https://betalist.com/sign_up', { timeout: 30000 });
      await sleep(2000);
      await ss(page, `bl-${product.name}-signup`);
      
      const signupText = await page.evaluate(() => document.body.innerText.substring(0, 400));
      console.log('  Signup text:', signupText.substring(0, 200));
      
      // Fill signup form
      const usernameInput = await page.$('input[name="user[username]"], #user_username');
      const emailInput = await page.$('input[name="user[email]"], #user_email');
      const pwdInput = await page.$('input[name="user[password]"], #user_password');
      const pwdConfirm = await page.$('input[name="user[password_confirmation]"], #user_password_confirmation');
      
      if (usernameInput) {
        await usernameInput.fill('pantrymatehq');
        console.log('  Filled username');
      }
      if (emailInput) {
        await emailInput.fill(GOOGLE_EMAIL);
        console.log('  Filled email');
      }
      if (pwdInput) {
        await pwdInput.fill(GOOGLE_PASSWORD);
        console.log('  Filled password');
      }
      if (pwdConfirm) {
        await pwdConfirm.fill(GOOGLE_PASSWORD);
        console.log('  Filled confirm password');
      }
      
      await ss(page, `bl-${product.name}-signup-filled`);
      
      // Submit
      if (pwdConfirm) {
        await pwdConfirm.press('Enter');
      } else if (pwdInput) {
        await pwdInput.press('Enter');
      }
      await sleep(4000);
      await ss(page, `bl-${product.name}-after-signup`);
      console.log('  After signup URL:', page.url());
      
      const afterText = await page.evaluate(() => document.body.innerText.substring(0, 300));
      console.log('  After signup text:', afterText.substring(0, 200));
      
      // Check if registered  
      if (page.url().includes('sign_up') && afterText.includes('taken')) {
        // Email already taken - try sign in
        console.log('  Email taken, trying different approach...');
        return { ...r, status: 'EMAIL_TAKEN_CANT_LOGIN', note: 'Email exists but wrong password or needs magic link verification' };
      }
    }
    
    // Now try to access the submit page
    await page.goto('https://betalist.com/submit', { timeout: 30000 });
    await sleep(2000);
    await ss(page, `bl-${product.name}-submit-page`);
    console.log('  Submit page URL:', page.url());
    
    const submitText = await page.evaluate(() => document.body.innerText.substring(0, 400));
    console.log('  Submit page text:', submitText.substring(0, 200));
    
    if (page.url().includes('sign_in') || page.url().includes('sign_up')) {
      return { ...r, status: 'AUTH_BLOCKED', url: page.url() };
    }
    
    const inputs = await page.$$eval('input:not([type=hidden]):not([type=submit]), textarea', els =>
      els.map(el => ({ type: el.type, name: el.name, id: el.id, placeholder: el.placeholder }))
    );
    console.log('  Inputs:', JSON.stringify(inputs));
    
    return { ...r, status: 'CHECKED', url: page.url(), note: submitText.substring(0, 100) };
  } catch (e) {
    console.log('  Error:', e.message.substring(0, 150));
    return { ...r, status: 'ERROR', error: e.message.substring(0, 150) };
  } finally {
    await ctx.close();
  }
}

// ============================================================
// SAASHUB - /services/submit with corrected form filling
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
    await ss(page, `sh-${product.name}-step1`);
    
    const text = await page.evaluate(() => document.body.innerText.substring(0, 200));
    if (text.includes('security verification') || text.includes('Cloudflare')) {
      console.log('  CF blocking - waiting...');
      await sleep(10000);
      const text2 = await page.evaluate(() => document.body.innerText.substring(0, 200));
      if (text2.includes('security verification')) {
        return { ...r, status: 'CLOUDFLARE_BLOCKED' };
      }
    }
    
    // Step 1: Enter URL
    const urlInput = await page.$('input[placeholder*="http"], input[type="url"]');
    if (!urlInput) {
      return { ...r, status: 'NO_URL_INPUT', url: page.url() };
    }
    
    await urlInput.fill(product.url);
    await sleep(300);
    await ss(page, `sh-${product.name}-url-filled`);
    
    const continueBtn = await page.$('input[type="submit"][value="Continue"], button:has-text("Continue")');
    if (continueBtn) await continueBtn.click();
    else await urlInput.press('Enter');
    
    await sleep(3000);
    await ss(page, `sh-${product.name}-step2`);
    console.log('  Step 2 URL:', page.url());
    
    if (page.url().includes('login') || page.url().includes('sign_in')) {
      return { ...r, status: 'LOGIN_REQUIRED', url: page.url() };
    }
    
    // Step 2: Fill the product form
    const step2Text = await page.evaluate(() => document.body.innerText.substring(0, 300));
    console.log('  Step 2 text:', step2Text.substring(0, 200));
    
    // Fill Product Name
    const nameInput = await page.$('#service_name');
    if (nameInput) {
      await nameInput.fill(product.name);
      console.log('  Filled name:', product.name);
    }
    
    // Fill Tagline
    const taglineInput = await page.$('#service_tagline');
    if (taglineInput) {
      await taglineInput.fill(product.tagline);
      console.log('  Filled tagline');
    }
    
    // Fill Contact Email
    const emailInput = await page.$('#service_contact_email');
    if (emailInput) {
      await emailInput.fill(product.email);
      console.log('  Filled contact email');
    }
    
    // Skip linkedin_url (we don't have one)
    // Skip categories (react-select, complex)
    // Skip competitors (react-select, complex)
    
    await ss(page, `sh-${product.name}-step2-filled`);
    
    // Try to submit
    const submitBtn = await page.$('input[type="submit"], button[type="submit"], button:has-text("Submit"), button:has-text("Save"), button:has-text("Add")');
    if (submitBtn) {
      const btnText = await submitBtn.evaluate(el => el.textContent?.trim() || el.value);
      console.log('  Found submit button:', btnText);
      
      await submitBtn.click();
      await sleep(4000);
      await ss(page, `sh-${product.name}-after-submit`);
      console.log('  After submit URL:', page.url());
      
      const afterText = await page.evaluate(() => document.body.innerText.substring(0, 300));
      console.log('  After submit text:', afterText.substring(0, 200));
      
      // Check for success indicators
      if (page.url().includes('services/new') || afterText.includes('submitted') || afterText.includes('success') || afterText.includes('thank')) {
        return { ...r, status: 'SUBMITTED', url: page.url() };
      }
      
      if (afterText.includes('Please enter a URL') || afterText.includes('can\'t be blank')) {
        return { ...r, status: 'VALIDATION_ERROR', url: page.url(), note: afterText.substring(0, 150) };
      }
      
      return { ...r, status: 'SUBMIT_ATTEMPTED', url: page.url(), note: afterText.substring(0, 150) };
    }
    
    return { ...r, status: 'NO_SUBMIT_BTN', url: page.url() };
  } catch (e) {
    console.log('  Error:', e.message.substring(0, 150));
    await ss(page, `sh-${product.name}-error`).catch(() => {});
    return { ...r, status: 'ERROR', error: e.message.substring(0, 150) };
  } finally {
    await ctx.close();
  }
}

// ============================================================
// TOOLIFY - Use placeholder-based selectors, scroll + submit
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
    await ss(page, `tf-${product.name}-submit-page`);
    
    // Find and fill the URL input field (with placeholder "Please enter the tool url...")
    const urlInput = await page.$('input[placeholder*="enter the tool url"], input[placeholder*="copy.ai"]');
    if (!urlInput) {
      return { ...r, status: 'NO_URL_INPUT' };
    }
    
    // Also find the Name input (placeholder "Copy AI")
    const nameInput = await page.$('input[placeholder="Copy AI"], input[placeholder*="Copy AI"]');
    
    console.log('  Found URL input:', !!urlInput, 'Name input:', !!nameInput);
    
    // Fill name first if found
    if (nameInput) {
      await nameInput.fill(product.name);
      console.log('  Filled name:', product.name);
    }
    
    // Fill URL
    await urlInput.fill(product.url);
    console.log('  Filled URL:', product.url);
    await sleep(500);
    await ss(page, `tf-${product.name}-inputs-filled`);
    
    // Look for submit button near the form
    // The form might have a submit button that we need to scroll to find
    const allButtons = await page.$$eval('button', els => 
      els.map(el => ({ text: el.textContent?.trim(), class: el.className.substring(0, 50), type: el.type }))
         .filter(b => b.text && b.text.length < 50)
    );
    console.log('  All buttons:', JSON.stringify(allButtons.slice(0, 10)));
    
    // Try to find a submit button for this form
    const submitBtn = await page.$('button:has-text("Submit now"), button:has-text("Submit Tool"), button:has-text("Add Tool"), button:has-text("Submit"), form button[type="submit"]');
    if (submitBtn) {
      const btnText = await submitBtn.evaluate(el => el.textContent?.trim());
      console.log('  Found submit button:', btnText);
      await submitBtn.scrollIntoViewIfNeeded();
      await submitBtn.click();
      await sleep(4000);
      await ss(page, `tf-${product.name}-after-submit`);
      console.log('  After submit URL:', page.url());
      return { ...r, status: 'SUBMITTED', url: page.url() };
    }
    
    // Try pressing Enter in the URL field
    await urlInput.press('Enter');
    await sleep(3000);
    await ss(page, `tf-${product.name}-after-enter`);
    console.log('  After Enter URL:', page.url());
    
    const afterText = await page.evaluate(() => document.body.innerText.substring(0, 400));
    console.log('  After Enter text:', afterText.substring(0, 200));
    
    if (page.url() !== 'https://www.toolify.ai/submit') {
      return { ...r, status: 'REDIRECTED', url: page.url() };
    }
    
    // Check if there's a modal or overlay that appeared
    const modal = await page.$('[class*="modal"], [class*="dialog"], [role="dialog"]');
    if (modal) {
      await ss(page, `tf-${product.name}-modal`);
      console.log('  Modal appeared!');
    }
    
    // Take full page screenshot to see everything
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, `v6-full-${product.name}-submit.png`), fullPage: true });
    console.log(`📸 v6-full-${product.name}-submit.png (full page)`);
    
    // Get page source to find form
    const formInfo = await page.evaluate(() => {
      const forms = Array.from(document.querySelectorAll('form')).map(f => ({
        action: f.action,
        id: f.id,
        class: f.className.substring(0, 60),
        inputs: Array.from(f.querySelectorAll('input, textarea, button')).map(el => ({
          tag: el.tagName, type: el.type, name: el.name, placeholder: el.placeholder, 
          id: el.id, value: el.value?.substring(0, 30)
        }))
      }));
      return forms;
    });
    console.log('  Forms on page:', JSON.stringify(formInfo, null, 2));
    
    return { ...r, status: 'URL_ENTERED_NO_REDIRECT', url: page.url() };
  } catch (e) {
    console.log('  Error:', e.message.substring(0, 150));
    await ss(page, `tf-${product.name}-error`).catch(() => {});
    return { ...r, status: 'ERROR', error: e.message.substring(0, 150) };
  } finally {
    await ctx.close();
  }
}

// ============================================================
// MAIN
// ============================================================
async function main() {
  console.log('=== V6 - Targeted Fix Run ===\n');
  
  const browser = await chromium.launch({
    headless: true, slowMo: 80,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });
  
  const results = [];
  
  try {
    results.push(await doBetalist(browser, PANTRYMATE));
    results.push(await doBetalist(browser, UNITFIX));
    results.push(await doSaashub(browser, PANTRYMATE));
    results.push(await doSaashub(browser, UNITFIX));
    results.push(await doToolify(browser, PANTRYMATE));
    results.push(await doToolify(browser, UNITFIX));
  } finally {
    await browser.close();
  }
  
  console.log('\n=== FINAL RESULTS ===');
  console.log(JSON.stringify(results, null, 2));
}

main().catch(console.error);
