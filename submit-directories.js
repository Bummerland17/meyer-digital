const { chromium } = require('/root/.openclaw/workspace/node_modules/playwright');
const path = require('path');
const fs = require('fs');

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

let screenshotCounter = 0;
async function screenshot(page, label) {
  screenshotCounter++;
  const fname = `${String(screenshotCounter).padStart(3, '0')}-${label.replace(/[^a-z0-9]/gi, '-')}.png`;
  const fpath = path.join(SCREENSHOTS_DIR, fname);
  await page.screenshot({ path: fpath, fullPage: false });
  console.log(`📸 Screenshot: ${fpath}`);
  return fpath;
}

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function handleGoogleOAuth(context, triggerFn) {
  // Set up popup listener before triggering
  const popupPromise = context.waitForEvent('page', { timeout: 15000 }).catch(() => null);
  await triggerFn();
  
  let googlePage = await popupPromise;
  if (!googlePage) {
    console.log('No popup detected, checking current pages...');
    const pages = context.pages();
    googlePage = pages[pages.length - 1];
  }
  
  await googlePage.waitForLoadState('domcontentloaded', { timeout: 15000 }).catch(() => {});
  console.log('Google OAuth page URL:', googlePage.url());
  await screenshot(googlePage, 'google-oauth-start');
  
  // Fill email
  try {
    await googlePage.waitForSelector('input[type="email"]', { timeout: 10000 });
    await googlePage.fill('input[type="email"]', GOOGLE_EMAIL);
    await screenshot(googlePage, 'google-email-filled');
    await googlePage.click('#identifierNext, [id="identifierNext"], button[jsname="LgbsSe"]');
    await sleep(2000);
    await googlePage.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
    await screenshot(googlePage, 'google-after-email-next');
  } catch (e) {
    console.log('Error filling email:', e.message);
    await screenshot(googlePage, 'google-email-error');
    return false;
  }
  
  // Fill password
  try {
    await googlePage.waitForSelector('input[type="password"]', { timeout: 10000 });
    await googlePage.fill('input[type="password"]', GOOGLE_PASSWORD);
    await screenshot(googlePage, 'google-password-filled');
    await googlePage.click('#passwordNext, [id="passwordNext"], button[jsname="LgbsSe"]');
    await sleep(3000);
    await googlePage.waitForLoadState('domcontentloaded', { timeout: 15000 }).catch(() => {});
    await screenshot(googlePage, 'google-after-password');
  } catch (e) {
    console.log('Error filling password:', e.message);
    await screenshot(googlePage, 'google-password-error');
    return false;
  }
  
  // Check for 2FA
  const url = googlePage.url();
  console.log('After password URL:', url);
  if (url.includes('challenge') || url.includes('2fa') || url.includes('verify') || url.includes('signin/v2/challenge')) {
    console.log('NEED_2FA_CODE - 2FA challenge detected!');
    await screenshot(googlePage, 'google-2fa-needed');
    return '2FA_NEEDED';
  }
  
  // Check for account selection
  try {
    const accountBtn = await googlePage.$('[data-email]');
    if (accountBtn) {
      await accountBtn.click();
      await sleep(2000);
      await screenshot(googlePage, 'google-account-selected');
    }
  } catch (e) {}
  
  return googlePage;
}

// ============================================================
// SITE 1: uneed.be
// ============================================================
async function submitUneed(browser, product) {
  console.log(`\n=== UNEED.BE - Submitting ${product.name} ===`);
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    await page.goto('https://www.uneed.be', { timeout: 30000 });
    await sleep(2000);
    await screenshot(page, `uneed-${product.name}-home`);
    
    // Find submit button
    const submitBtn = await page.$('a[href*="submit"], button:has-text("Submit"), a:has-text("Submit")');
    if (!submitBtn) {
      console.log('No submit button found, trying to navigate directly');
      await page.goto('https://www.uneed.be/submit', { timeout: 30000 });
    } else {
      await submitBtn.click();
    }
    await sleep(2000);
    await screenshot(page, `uneed-${product.name}-submit-page`);
    
    // Look for Google sign in
    const googleBtn = await page.$('button:has-text("Google"), a:has-text("Google"), [data-provider="google"]');
    if (googleBtn) {
      console.log('Found Google button, clicking...');
      const result = await handleGoogleOAuth(context, () => googleBtn.click());
      if (result === '2FA_NEEDED') {
        console.log('NEED_2FA_CODE for uneed.be');
        return { site: 'uneed.be', product: product.name, status: 'NEED_2FA_CODE' };
      }
      await sleep(3000);
      await screenshot(page, `uneed-${product.name}-after-auth`);
    }
    
    // Fill form
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
    const currentUrl = page.url();
    console.log('Current URL after possible auth:', currentUrl);
    await screenshot(page, `uneed-${product.name}-form`);
    
    // Fill product name
    const nameInput = await page.$('input[name="name"], input[placeholder*="name"], input[placeholder*="Name"], input[id*="name"]');
    if (nameInput) await nameInput.fill(product.name);
    
    const urlInput = await page.$('input[name="url"], input[placeholder*="url"], input[placeholder*="URL"], input[type="url"]');
    if (urlInput) await urlInput.fill(product.url);
    
    const taglineInput = await page.$('input[name="tagline"], input[placeholder*="tagline"], textarea[placeholder*="tagline"]');
    if (taglineInput) await taglineInput.fill(product.tagline);
    
    const descInput = await page.$('textarea[name="description"], textarea[placeholder*="description"], textarea[placeholder*="Description"]');
    if (descInput) await descInput.fill(product.description);
    
    await screenshot(page, `uneed-${product.name}-form-filled`);
    
    // Submit
    const submitFormBtn = await page.$('button[type="submit"], button:has-text("Submit"), input[type="submit"]');
    if (submitFormBtn) {
      await submitFormBtn.click();
      await sleep(3000);
      await screenshot(page, `uneed-${product.name}-submitted`);
      return { site: 'uneed.be', product: product.name, status: 'SUBMITTED' };
    }
    
    return { site: 'uneed.be', product: product.name, status: 'FORM_NOT_FOUND' };
  } catch (e) {
    console.log('Error on uneed.be:', e.message);
    await screenshot(page, `uneed-${product.name}-error`);
    return { site: 'uneed.be', product: product.name, status: 'ERROR', error: e.message };
  } finally {
    await context.close();
  }
}

// ============================================================
// SITE 2: betalist.com
// ============================================================
async function submitBetalist(browser, product) {
  console.log(`\n=== BETALIST.COM - Submitting ${product.name} ===`);
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    await page.goto('https://betalist.com/startups/new', { timeout: 30000 });
    await sleep(2000);
    await screenshot(page, `betalist-${product.name}-start`);
    
    // Look for sign in / Google auth
    const googleBtn = await page.$('a[href*="google"], button:has-text("Google"), a:has-text("Continue with Google"), a:has-text("Sign in with Google")');
    if (googleBtn) {
      console.log('Found Google button on betalist');
      const result = await handleGoogleOAuth(context, () => googleBtn.click());
      if (result === '2FA_NEEDED') {
        return { site: 'betalist.com', product: product.name, status: 'NEED_2FA_CODE' };
      }
      await sleep(3000);
      await screenshot(page, `betalist-${product.name}-after-auth`);
    }
    
    // Navigate to submission form
    await page.goto('https://betalist.com/startups/new', { timeout: 30000 });
    await sleep(2000);
    await screenshot(page, `betalist-${product.name}-form`);
    
    // Fill form fields
    const nameInput = await page.$('input[name*="name"], input[id*="name"], input[placeholder*="name"]');
    if (nameInput) await nameInput.fill(product.name);
    
    const urlInput = await page.$('input[name*="url"], input[id*="url"], input[type="url"], input[placeholder*="url"]');
    if (urlInput) await urlInput.fill(product.url);
    
    const taglineInput = await page.$('input[name*="tagline"], textarea[name*="tagline"], input[placeholder*="tagline"]');
    if (taglineInput) await taglineInput.fill(product.tagline);
    
    const descInput = await page.$('textarea[name*="description"], textarea[id*="description"]');
    if (descInput) await descInput.fill(product.description);
    
    const emailInput = await page.$('input[name*="email"], input[type="email"]');
    if (emailInput) await emailInput.fill(product.email);
    
    await screenshot(page, `betalist-${product.name}-form-filled`);
    
    const submitBtn = await page.$('button[type="submit"], input[type="submit"], button:has-text("Submit")');
    if (submitBtn) {
      await submitBtn.click();
      await sleep(3000);
      await screenshot(page, `betalist-${product.name}-submitted`);
      return { site: 'betalist.com', product: product.name, status: 'SUBMITTED' };
    }
    
    return { site: 'betalist.com', product: product.name, status: 'FORM_NOT_FOUND' };
  } catch (e) {
    console.log('Error on betalist.com:', e.message);
    await screenshot(page, `betalist-${product.name}-error`);
    return { site: 'betalist.com', product: product.name, status: 'ERROR', error: e.message };
  } finally {
    await context.close();
  }
}

// ============================================================
// SITE 3: saashub.com
// ============================================================
async function submitSaashub(browser, product) {
  console.log(`\n=== SAASHUB.COM - Submitting ${product.name} ===`);
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    await page.goto('https://www.saashub.com', { timeout: 30000 });
    await sleep(2000);
    await screenshot(page, `saashub-${product.name}-home`);
    
    // Find sign in link
    const signInLink = await page.$('a[href*="sign_in"], a[href*="login"], a:has-text("Sign In"), a:has-text("Login")');
    if (signInLink) {
      await signInLink.click();
      await sleep(2000);
      await screenshot(page, `saashub-${product.name}-signin-page`);
    }
    
    // Look for Google OAuth
    const googleBtn = await page.$('a[href*="google"], button:has-text("Google"), a:has-text("Sign in with Google"), a:has-text("Continue with Google")');
    if (googleBtn) {
      console.log('Found Google button on saashub');
      const result = await handleGoogleOAuth(context, () => googleBtn.click());
      if (result === '2FA_NEEDED') {
        return { site: 'saashub.com', product: product.name, status: 'NEED_2FA_CODE' };
      }
      await sleep(3000);
      await screenshot(page, `saashub-${product.name}-after-auth`);
    }
    
    // Navigate to add product
    await page.goto('https://www.saashub.com/software/new', { timeout: 30000 });
    await sleep(2000);
    await screenshot(page, `saashub-${product.name}-add-product`);
    
    // Fill form
    const nameInput = await page.$('input[name*="name"], input[id*="name"], input[placeholder*="Name"]');
    if (nameInput) await nameInput.fill(product.name);
    
    const urlInput = await page.$('input[name*="url"], input[id*="url"], input[type="url"]');
    if (urlInput) await urlInput.fill(product.url);
    
    const descInput = await page.$('textarea[name*="description"], textarea[id*="description"], textarea[placeholder*="description"]');
    if (descInput) await descInput.fill(product.description);
    
    await screenshot(page, `saashub-${product.name}-form-filled`);
    
    const submitBtn = await page.$('button[type="submit"], input[type="submit"], button:has-text("Submit"), button:has-text("Add")');
    if (submitBtn) {
      await submitBtn.click();
      await sleep(3000);
      await screenshot(page, `saashub-${product.name}-submitted`);
      return { site: 'saashub.com', product: product.name, status: 'SUBMITTED' };
    }
    
    return { site: 'saashub.com', product: product.name, status: 'FORM_NOT_FOUND' };
  } catch (e) {
    console.log('Error on saashub.com:', e.message);
    await screenshot(page, `saashub-${product.name}-error`);
    return { site: 'saashub.com', product: product.name, status: 'ERROR', error: e.message };
  } finally {
    await context.close();
  }
}

// ============================================================
// SITE 4: toolify.ai
// ============================================================
async function submitToolify(browser, product) {
  console.log(`\n=== TOOLIFY.AI - Submitting ${product.name} ===`);
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    await page.goto('https://www.toolify.ai/submit-tool', { timeout: 30000 });
    await sleep(3000);
    await screenshot(page, `toolify-${product.name}-start`);
    
    // Check for Cloudflare challenge
    const cfChallenge = await page.$('#challenge-running, .cf-browser-verification, #cf-challenge-running');
    if (cfChallenge) {
      console.log('Cloudflare challenge detected, waiting...');
      await sleep(8000);
      await screenshot(page, `toolify-${product.name}-after-cf`);
    }
    
    // Look for sign in / Google auth
    const signInBtn = await page.$('button:has-text("Sign"), a:has-text("Sign"), button:has-text("Login"), a:has-text("Login")');
    if (signInBtn) {
      await signInBtn.click();
      await sleep(2000);
      await screenshot(page, `toolify-${product.name}-signin`);
    }
    
    const googleBtn = await page.$('button:has-text("Google"), a:has-text("Google"), [data-provider="google"]');
    if (googleBtn) {
      console.log('Found Google button on toolify');
      const result = await handleGoogleOAuth(context, () => googleBtn.click());
      if (result === '2FA_NEEDED') {
        return { site: 'toolify.ai', product: product.name, status: 'NEED_2FA_CODE' };
      }
      await sleep(3000);
    }
    
    // Navigate to submit
    await page.goto('https://www.toolify.ai/submit-tool', { timeout: 30000 });
    await sleep(2000);
    await screenshot(page, `toolify-${product.name}-form`);
    
    // Fill form
    const nameInput = await page.$('input[name*="name"], input[placeholder*="name"], input[placeholder*="tool"]');
    if (nameInput) await nameInput.fill(product.name);
    
    const urlInput = await page.$('input[name*="url"], input[type="url"], input[placeholder*="url"]');
    if (urlInput) await urlInput.fill(product.url);
    
    const taglineInput = await page.$('input[name*="tagline"], input[placeholder*="tagline"]');
    if (taglineInput) await taglineInput.fill(product.tagline);
    
    const descInput = await page.$('textarea[name*="description"], textarea[placeholder*="description"]');
    if (descInput) await descInput.fill(product.description);
    
    const emailInput = await page.$('input[name*="email"], input[type="email"]');
    if (emailInput) await emailInput.fill(product.email);
    
    await screenshot(page, `toolify-${product.name}-form-filled`);
    
    const submitBtn = await page.$('button[type="submit"], button:has-text("Submit"), input[type="submit"]');
    if (submitBtn) {
      await submitBtn.click();
      await sleep(3000);
      await screenshot(page, `toolify-${product.name}-submitted`);
      return { site: 'toolify.ai', product: product.name, status: 'SUBMITTED' };
    }
    
    return { site: 'toolify.ai', product: product.name, status: 'FORM_NOT_FOUND' };
  } catch (e) {
    console.log('Error on toolify.ai:', e.message);
    await screenshot(page, `toolify-${product.name}-error`);
    return { site: 'toolify.ai', product: product.name, status: 'ERROR', error: e.message };
  } finally {
    await context.close();
  }
}

// ============================================================
// MAIN
// ============================================================
async function main() {
  console.log('Starting directory submissions...\n');
  
  const browser = await chromium.launch({ 
    headless: true, 
    slowMo: 100,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });
  
  const results = [];
  
  try {
    // Submit PantryMate to all sites
    results.push(await submitUneed(browser, PANTRYMATE));
    results.push(await submitBetalist(browser, PANTRYMATE));
    results.push(await submitSaashub(browser, PANTRYMATE));
    results.push(await submitToolify(browser, PANTRYMATE));
    
    // Submit UnitFix to all sites
    results.push(await submitUneed(browser, UNITFIX));
    results.push(await submitBetalist(browser, UNITFIX));
    results.push(await submitSaashub(browser, UNITFIX));
    results.push(await submitToolify(browser, UNITFIX));
    
  } finally {
    await browser.close();
  }
  
  console.log('\n\n=== FINAL RESULTS ===');
  console.log(JSON.stringify(results, null, 2));
  
  return results;
}

main().catch(console.error);
