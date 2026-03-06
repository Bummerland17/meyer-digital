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
  const fname = `v2-${String(screenshotCounter).padStart(3, '0')}-${label.replace(/[^a-z0-9]/gi, '-')}.png`;
  const fpath = path.join(SCREENSHOTS_DIR, fname);
  try {
    await page.screenshot({ path: fpath, fullPage: false });
    console.log(`📸 ${fpath}`);
  } catch (e) {
    console.log(`Screenshot failed: ${e.message}`);
  }
  return fpath;
}

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function handleGoogleOAuth(page, context) {
  // We're on a Google sign-in page
  console.log('Handling Google OAuth, URL:', page.url());
  await screenshot(page, 'google-start');
  
  // Fill email
  try {
    await page.waitForSelector('input[type="email"]', { timeout: 10000 });
    await page.fill('input[type="email"]', GOOGLE_EMAIL);
    await sleep(500);
    await screenshot(page, 'google-email-filled');
    
    // Click Next
    await page.click('#identifierNext');
    await sleep(2500);
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
    await screenshot(page, 'google-after-email-next');
  } catch (e) {
    console.log('Email fill error:', e.message);
    await screenshot(page, 'google-email-error');
    return false;
  }
  
  // Fill password
  try {
    await page.waitForSelector('input[type="password"]', { timeout: 10000 });
    await page.fill('input[type="password"]', GOOGLE_PASSWORD);
    await sleep(500);
    await screenshot(page, 'google-password-filled');
    
    await page.click('#passwordNext');
    await sleep(4000);
    await page.waitForLoadState('domcontentloaded', { timeout: 15000 }).catch(() => {});
    await screenshot(page, 'google-after-password');
  } catch (e) {
    console.log('Password fill error:', e.message);
    await screenshot(page, 'google-password-error');
    return false;
  }
  
  const url = page.url();
  console.log('Post-auth URL:', url);
  
  if (url.includes('challenge') || url.includes('/2-step') || url.includes('/signin/v2/challenge')) {
    console.log('⚠️ 2FA CHALLENGE DETECTED');
    await screenshot(page, 'google-2fa');
    return '2FA';
  }
  
  return true;
}

// ============================================================
// SITE 1: uneed.be
// ============================================================
async function submitUneed(browser, product) {
  console.log(`\n=== UNEED.BE - ${product.name} ===`);
  const context = await browser.newContext({ ignoreHTTPSErrors: true });
  const page = await context.newPage();
  const results = { site: 'uneed.be', product: product.name };
  
  try {
    await page.goto('https://www.uneed.be', { timeout: 30000 });
    await sleep(2000);
    await screenshot(page, `uneed-${product.name}-home`);
    console.log('uneed home URL:', page.url());
    
    // Look for submit link
    const links = await page.$$eval('a', els => els.map(el => ({ text: el.textContent?.trim(), href: el.href })));
    const submitLink = links.find(l => l.text?.toLowerCase().includes('submit') || l.href?.includes('submit'));
    console.log('Submit link found:', submitLink);
    
    if (submitLink) {
      await page.goto(submitLink.href, { timeout: 30000 });
    } else {
      // Try clicking
      const btn = await page.$('a:has-text("Submit"), button:has-text("Submit"), a:has-text("Add"), a:has-text("Post")');
      if (btn) await btn.click();
    }
    
    await sleep(2000);
    await screenshot(page, `uneed-${product.name}-submit-page`);
    console.log('After navigate URL:', page.url());
    
    // Check if there's a login/Google button
    const googleBtn = await page.$('[class*="google" i], [id*="google" i], a[href*="google"], button:has-text("Google"), a:has-text("Google")');
    if (googleBtn) {
      console.log('Found Google button');
      // Check if it opens popup
      const [popup] = await Promise.all([
        context.waitForEvent('page', { timeout: 5000 }).catch(() => null),
        googleBtn.click()
      ]);
      
      if (popup) {
        console.log('Popup opened:', popup.url());
        await popup.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
        const result = await handleGoogleOAuth(popup, context);
        if (result === '2FA') return { ...results, status: 'NEED_2FA_CODE' };
        await popup.waitForEvent('close', { timeout: 10000 }).catch(() => {});
      } else {
        // Same page navigation
        await page.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
        if (page.url().includes('google') || page.url().includes('accounts')) {
          const result = await handleGoogleOAuth(page, context);
          if (result === '2FA') return { ...results, status: 'NEED_2FA_CODE' };
        }
      }
      
      await sleep(3000);
      await screenshot(page, `uneed-${product.name}-after-auth`);
    }
    
    // Get page content to understand structure
    const pageText = await page.evaluate(() => document.body.innerText.substring(0, 500));
    console.log('Page content:', pageText);
    
    // Get all input fields
    const inputs = await page.$$eval('input, textarea', els => 
      els.map(el => ({ 
        tag: el.tagName, 
        type: el.type, 
        name: el.name, 
        id: el.id, 
        placeholder: el.placeholder,
        label: el.labels?.[0]?.textContent 
      }))
    );
    console.log('Inputs found:', JSON.stringify(inputs));
    
    // Fill whatever we find
    let filledAny = false;
    for (const input of inputs) {
      const selector = input.id ? `#${input.id}` : input.name ? `[name="${input.name}"]` : null;
      if (!selector) continue;
      
      const lowerLabel = (input.label || input.placeholder || input.name || input.id || '').toLowerCase();
      let value = null;
      
      if (lowerLabel.includes('name') && !lowerLabel.includes('domain')) value = product.name;
      else if (lowerLabel.includes('url') || lowerLabel.includes('website') || lowerLabel.includes('link')) value = product.url;
      else if (lowerLabel.includes('tagline') || lowerLabel.includes('subtitle')) value = product.tagline;
      else if (lowerLabel.includes('description') || lowerLabel.includes('desc')) value = product.description;
      else if (lowerLabel.includes('email')) value = product.email;
      
      if (value) {
        try {
          await page.fill(selector, value);
          filledAny = true;
          console.log(`Filled ${selector} with "${value.substring(0, 50)}..."`);
        } catch (e) {}
      }
    }
    
    await screenshot(page, `uneed-${product.name}-form-filled`);
    
    if (filledAny) {
      const submitBtn = await page.$('button[type="submit"], input[type="submit"], button:has-text("Submit"), button:has-text("Add")');
      if (submitBtn) {
        await submitBtn.click();
        await sleep(3000);
        await screenshot(page, `uneed-${product.name}-after-submit`);
        return { ...results, status: 'SUBMITTED' };
      }
    }
    
    return { ...results, status: 'NO_FORM_OR_SUBMIT', url: page.url() };
  } catch (e) {
    console.log('Error:', e.message);
    await screenshot(page, `uneed-${product.name}-error`).catch(() => {});
    return { ...results, status: 'ERROR', error: e.message };
  } finally {
    await context.close();
  }
}

// ============================================================
// SITE 2: betalist.com
// ============================================================
async function submitBetalist(browser, product) {
  console.log(`\n=== BETALIST.COM - ${product.name} ===`);
  const context = await browser.newContext();
  const page = await context.newPage();
  const results = { site: 'betalist.com', product: product.name };
  
  try {
    // First go to home to see login options
    await page.goto('https://betalist.com', { timeout: 30000 });
    await sleep(2000);
    await screenshot(page, `betalist-${product.name}-home`);
    console.log('betalist home URL:', page.url());
    
    const pageText = await page.evaluate(() => document.body.innerText.substring(0, 800));
    console.log('Page text:', pageText);
    
    // Find login link
    const loginLink = await page.$('a[href*="login"], a[href*="sign_in"], a[href*="signin"], a:has-text("Login"), a:has-text("Sign in")');
    if (loginLink) {
      const href = await loginLink.getAttribute('href');
      console.log('Login link href:', href);
      await loginLink.click();
      await sleep(2000);
      await screenshot(page, `betalist-${product.name}-login-page`);
    }
    
    // Look for Google OAuth
    const googleBtn = await page.$('a[href*="google"], a[href*="omniauth"], button:has-text("Google"), a:has-text("Google")');
    if (googleBtn) {
      const href = await googleBtn.getAttribute('href');
      console.log('Google btn href:', href);
      
      const [popup] = await Promise.all([
        context.waitForEvent('page', { timeout: 5000 }).catch(() => null),
        googleBtn.click()
      ]);
      
      await sleep(3000);
      
      if (popup) {
        await popup.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
        console.log('Popup URL:', popup.url());
        if (popup.url().includes('google') || popup.url().includes('accounts')) {
          const result = await handleGoogleOAuth(popup, context);
          if (result === '2FA') return { ...results, status: 'NEED_2FA_CODE' };
        }
        await popup.waitForEvent('close', { timeout: 10000 }).catch(() => {});
      } else {
        await page.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
        if (page.url().includes('google') || page.url().includes('accounts')) {
          const result = await handleGoogleOAuth(page, context);
          if (result === '2FA') return { ...results, status: 'NEED_2FA_CODE' };
        }
      }
      
      await sleep(3000);
      await screenshot(page, `betalist-${product.name}-after-auth`);
    }
    
    // Now try to find the submission page
    const submitLink = await page.$('a[href*="submit"], a[href*="/new"], a:has-text("Submit"), a:has-text("Add startup")');
    if (submitLink) {
      await submitLink.click();
      await sleep(2000);
    } else {
      await page.goto('https://betalist.com/submit', { timeout: 30000 });
      await sleep(2000);
    }
    
    await screenshot(page, `betalist-${product.name}-submit-page`);
    console.log('Submit page URL:', page.url());
    
    const pageText2 = await page.evaluate(() => document.body.innerText.substring(0, 500));
    console.log('Submit page text:', pageText2);
    
    const inputs = await page.$$eval('input, textarea', els => 
      els.map(el => ({ 
        tag: el.tagName, 
        type: el.type, 
        name: el.name, 
        id: el.id, 
        placeholder: el.placeholder 
      }))
    );
    console.log('Inputs:', JSON.stringify(inputs));
    
    let filledAny = false;
    for (const input of inputs) {
      if (input.type === 'hidden' || input.type === 'submit') continue;
      const selector = input.id ? `#${input.id}` : input.name ? `[name="${input.name}"]` : null;
      if (!selector) continue;
      
      const lowerKey = (input.placeholder || input.name || input.id || '').toLowerCase();
      let value = null;
      
      if (lowerKey.includes('name') || lowerKey.includes('startup') || lowerKey.includes('product')) value = product.name;
      else if (lowerKey.includes('url') || lowerKey.includes('website') || lowerKey.includes('link')) value = product.url;
      else if (lowerKey.includes('tagline') || lowerKey.includes('headline') || lowerKey.includes('short')) value = product.tagline;
      else if (lowerKey.includes('description') || lowerKey.includes('about')) value = product.description;
      else if (lowerKey.includes('email') || lowerKey.includes('contact')) value = product.email;
      
      if (value) {
        try {
          await page.fill(selector, value);
          filledAny = true;
        } catch (e) {}
      }
    }
    
    await screenshot(page, `betalist-${product.name}-form-filled`);
    
    if (filledAny) {
      const submitBtn = await page.$('button[type="submit"], input[type="submit"], button:has-text("Submit"), button:has-text("Add")');
      if (submitBtn) {
        await submitBtn.click();
        await sleep(3000);
        await screenshot(page, `betalist-${product.name}-submitted`);
        return { ...results, status: 'SUBMITTED', url: page.url() };
      }
    }
    
    return { ...results, status: 'NO_FORM', url: page.url() };
  } catch (e) {
    console.log('Error:', e.message);
    await screenshot(page, `betalist-${product.name}-error`).catch(() => {});
    return { ...results, status: 'ERROR', error: e.message };
  } finally {
    await context.close();
  }
}

// ============================================================
// SITE 3: saashub.com (persistent auth across products)
// ============================================================
let saashubAuthContext = null;

async function ensureSaashubAuth(browser) {
  if (saashubAuthContext) return saashubAuthContext;
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    await page.goto('https://www.saashub.com', { timeout: 30000 });
    await sleep(2000);
    await screenshot(page, 'saashub-home');
    
    // Click Login
    const loginBtn = await page.$('a:has-text("Login"), a:has-text("Sign in"), a[href*="login"], a[href*="sign_in"]');
    if (loginBtn) {
      await loginBtn.click();
      await sleep(2000);
      await screenshot(page, 'saashub-login-page');
    }
    
    // Find Google OAuth
    const googleBtn = await page.$('a[href*="google"], a[href*="omniauth/google"], button:has-text("Google"), a:has-text("Google"), a:has-text("Continue with Google")');
    if (googleBtn) {
      const href = await googleBtn.getAttribute('href');
      console.log('SaaSHub Google href:', href);
      
      const [popup] = await Promise.all([
        context.waitForEvent('page', { timeout: 5000 }).catch(() => null),
        googleBtn.click()
      ]);
      
      if (popup) {
        await popup.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
        await screenshot(popup, 'saashub-google-popup');
        const result = await handleGoogleOAuth(popup, context);
        if (result === '2FA') return null;
        await popup.waitForEvent('close', { timeout: 15000 }).catch(() => {});
      } else {
        await page.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
        if (page.url().includes('google') || page.url().includes('accounts')) {
          await screenshot(page, 'saashub-google-same-page');
          const result = await handleGoogleOAuth(page, context);
          if (result === '2FA') return null;
          await page.waitForLoadState('domcontentloaded', { timeout: 15000 }).catch(() => {});
        }
      }
      
      await sleep(3000);
      await screenshot(page, 'saashub-after-auth');
      console.log('After SaaSHub auth, URL:', page.url());
    } else {
      console.log('No Google button found on SaaSHub');
      await screenshot(page, 'saashub-no-google');
    }
    
    saashubAuthContext = { context, page };
    return saashubAuthContext;
  } catch (e) {
    console.log('SaaSHub auth error:', e.message);
    return { context, page };
  }
}

async function submitSaashub(browser, product) {
  console.log(`\n=== SAASHUB.COM - ${product.name} ===`);
  const results = { site: 'saashub.com', product: product.name };
  
  const auth = await ensureSaashubAuth(browser);
  if (!auth) return { ...results, status: 'NEED_2FA_CODE' };
  
  const { context, page } = auth;
  
  try {
    // Navigate to submit product
    await page.goto('https://www.saashub.com/submit-product', { timeout: 30000 }).catch(() => {});
    await sleep(2000);
    await screenshot(page, `saashub-${product.name}-submit-page`);
    console.log('SaaSHub submit URL:', page.url());
    
    // Try alternative URLs if needed
    if (page.url().includes('404') || page.url().includes('not_found')) {
      await page.goto('https://www.saashub.com/products/new', { timeout: 30000 }).catch(() => {});
      await sleep(2000);
      await screenshot(page, `saashub-${product.name}-products-new`);
    }
    
    const pageText = await page.evaluate(() => document.body.innerText.substring(0, 500));
    console.log('Page text:', pageText);
    
    const inputs = await page.$$eval('input, textarea, select', els => 
      els.map(el => ({ 
        tag: el.tagName,
        type: el.getAttribute('type'), 
        name: el.name, 
        id: el.id, 
        placeholder: el.placeholder,
        labelText: el.labels?.[0]?.textContent?.trim()
      }))
    );
    console.log('Inputs:', JSON.stringify(inputs));
    
    let filledAny = false;
    for (const input of inputs) {
      if (input.type === 'hidden' || input.type === 'submit' || input.type === 'checkbox') continue;
      const selector = input.id ? `#${input.id}` : input.name ? `[name="${input.name}"]` : null;
      if (!selector) continue;
      
      const lowerKey = (input.labelText || input.placeholder || input.name || input.id || '').toLowerCase();
      let value = null;
      
      if (lowerKey.includes('name') || lowerKey.includes('product') || lowerKey.includes('title')) value = product.name;
      else if (lowerKey.includes('url') || lowerKey.includes('website') || lowerKey.includes('homepage')) value = product.url;
      else if (lowerKey.includes('tagline') || lowerKey.includes('short desc') || lowerKey.includes('one liner')) value = product.tagline;
      else if (lowerKey.includes('description') || lowerKey.includes('about')) value = product.description;
      else if (lowerKey.includes('email')) value = product.email;
      
      if (value) {
        try {
          await page.fill(selector, value);
          filledAny = true;
          console.log(`Filled ${selector}`);
        } catch (e) {}
      }
    }
    
    await screenshot(page, `saashub-${product.name}-form-filled`);
    
    if (filledAny) {
      const submitBtn = await page.$('button[type="submit"], input[type="submit"], button:has-text("Submit"), button:has-text("Save"), button:has-text("Add")');
      if (submitBtn) {
        await submitBtn.click();
        await sleep(3000);
        await screenshot(page, `saashub-${product.name}-submitted`);
        return { ...results, status: 'SUBMITTED', url: page.url() };
      }
    }
    
    return { ...results, status: 'NO_FORM', url: page.url() };
  } catch (e) {
    console.log('Error:', e.message);
    await screenshot(page, `saashub-${product.name}-error`).catch(() => {});
    return { ...results, status: 'ERROR', error: e.message };
  }
}

// ============================================================
// SITE 4: toolify.ai
// ============================================================
async function submitToolify(browser, product) {
  console.log(`\n=== TOOLIFY.AI - ${product.name} ===`);
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });
  const page = await context.newPage();
  const results = { site: 'toolify.ai', product: product.name };
  
  try {
    // First visit home to get cookies
    await page.goto('https://www.toolify.ai', { timeout: 30000 });
    await sleep(5000);
    await screenshot(page, `toolify-${product.name}-home`);
    console.log('Toolify home URL:', page.url());
    
    const homeText = await page.evaluate(() => document.body.innerText.substring(0, 300));
    console.log('Home text:', homeText);
    
    // Try to find login button
    const loginBtn = await page.$('button:has-text("Sign in"), a:has-text("Sign in"), button:has-text("Login"), a:has-text("Login"), a[href*="login"], a[href*="sign"]');
    if (loginBtn) {
      console.log('Found login button');
      const [popup] = await Promise.all([
        context.waitForEvent('page', { timeout: 5000 }).catch(() => null),
        loginBtn.click()
      ]);
      
      await sleep(3000);
      if (popup) {
        await popup.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
        await screenshot(popup, `toolify-${product.name}-login-popup`);
        
        const googleBtn = await popup.$('button:has-text("Google"), a:has-text("Google"), [class*="google"]');
        if (googleBtn) {
          const [googlePopup] = await Promise.all([
            context.waitForEvent('page', { timeout: 5000 }).catch(() => null),
            googleBtn.click()
          ]);
          if (googlePopup) {
            await handleGoogleOAuth(googlePopup, context);
          }
        }
      }
      
      await screenshot(page, `toolify-${product.name}-after-login`);
    }
    
    // Navigate to submit page
    await page.goto('https://www.toolify.ai/submit-tool', { timeout: 30000 });
    await sleep(5000);
    await screenshot(page, `toolify-${product.name}-submit-page`);
    console.log('Submit page URL:', page.url());
    
    const submitText = await page.evaluate(() => document.body.innerText.substring(0, 500));
    console.log('Submit page text:', submitText);
    
    // Check if Cloudflare is still blocking
    const cfBlocked = await page.$('#challenge-running, .cf-browser-verification, #cf-challenge-running, [id*="challenge"]');
    if (cfBlocked) {
      console.log('Still blocked by Cloudflare');
      await screenshot(page, `toolify-${product.name}-cf-blocked`);
      return { ...results, status: 'BLOCKED_CLOUDFLARE' };
    }
    
    // Look for sign in on submit page
    const signInRequired = await page.$('button:has-text("Sign in"), a:has-text("Sign in"), button:has-text("Login")');
    if (signInRequired) {
      const [popup] = await Promise.all([
        context.waitForEvent('page', { timeout: 5000 }).catch(() => null),
        signInRequired.click()
      ]);
      if (popup) {
        await popup.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
        await screenshot(popup, `toolify-${product.name}-auth-popup`);
      }
      await sleep(3000);
      await screenshot(page, `toolify-${product.name}-after-signin`);
    }
    
    // Fill form
    const inputs = await page.$$eval('input, textarea', els => 
      els.map(el => ({ type: el.type, name: el.name, id: el.id, placeholder: el.placeholder }))
    );
    console.log('Inputs:', JSON.stringify(inputs));
    
    let filledAny = false;
    for (const input of inputs) {
      if (input.type === 'hidden' || input.type === 'submit') continue;
      const selector = input.id ? `#${input.id}` : input.name ? `[name="${input.name}"]` : null;
      if (!selector) continue;
      
      const lowerKey = (input.placeholder || input.name || input.id || '').toLowerCase();
      let value = null;
      
      if (lowerKey.includes('name') || lowerKey.includes('tool')) value = product.name;
      else if (lowerKey.includes('url') || lowerKey.includes('website') || lowerKey.includes('link')) value = product.url;
      else if (lowerKey.includes('tagline') || lowerKey.includes('slogan')) value = product.tagline;
      else if (lowerKey.includes('description') || lowerKey.includes('about')) value = product.description;
      else if (lowerKey.includes('email')) value = product.email;
      
      if (value) {
        try {
          await page.fill(selector, value);
          filledAny = true;
        } catch (e) {}
      }
    }
    
    await screenshot(page, `toolify-${product.name}-form-filled`);
    
    if (filledAny) {
      const submitBtn = await page.$('button[type="submit"], button:has-text("Submit"), input[type="submit"]');
      if (submitBtn) {
        await submitBtn.click();
        await sleep(3000);
        await screenshot(page, `toolify-${product.name}-submitted`);
        return { ...results, status: 'SUBMITTED' };
      }
    }
    
    return { ...results, status: 'NO_FORM', url: page.url() };
  } catch (e) {
    console.log('Error:', e.message);
    await screenshot(page, `toolify-${product.name}-error`).catch(() => {});
    return { ...results, status: 'ERROR', error: e.message };
  } finally {
    await context.close();
  }
}

// ============================================================
// MAIN
// ============================================================
async function main() {
  console.log('Starting v2 directory submissions...\n');
  
  const browser = await chromium.launch({ 
    headless: true, 
    slowMo: 100,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--ignore-certificate-errors']
  });
  
  const results = [];
  
  try {
    // PantryMate submissions
    results.push(await submitUneed(browser, PANTRYMATE));
    results.push(await submitBetalist(browser, PANTRYMATE));
    results.push(await submitSaashub(browser, PANTRYMATE));
    results.push(await submitToolify(browser, PANTRYMATE));
    
    // UnitFix submissions (saashub reuses auth context)
    results.push(await submitUneed(browser, UNITFIX));
    results.push(await submitBetalist(browser, UNITFIX));
    results.push(await submitSaashub(browser, UNITFIX));
    results.push(await submitToolify(browser, UNITFIX));
    
  } finally {
    if (saashubAuthContext) await saashubAuthContext.context.close().catch(() => {});
    await browser.close();
  }
  
  console.log('\n\n=== FINAL RESULTS ===');
  console.log(JSON.stringify(results, null, 2));
}

main().catch(console.error);
