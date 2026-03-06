/**
 * V3 - Targeted per-site submissions based on actual page structure
 * 
 * Findings from V2:
 * - uneed.be: Under maintenance ("Please stand by while configuration is in progress.")
 * - betalist.com: No Google OAuth - has Sign in with X, email/password, magic link
 * - saashub.com: Cloudflare blocks the login page
 * - toolify.ai: Has Google OAuth popup with "Continue with Google"
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
  const fname = `v3-${String(sc).padStart(3,'0')}-${label.replace(/[^a-z0-9]/gi,'-')}.png`;
  const fpath = path.join(SCREENSHOTS_DIR, fname);
  try { await page.screenshot({ path: fpath }); } catch (e) {}
  console.log(`📸 ${fname}`);
  return fpath;
}

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function doGoogleLogin(page) {
  console.log('  Google login page:', page.url());
  await ss(page, 'google-login-start');

  // Wait for email input
  try {
    await page.waitForSelector('input[type="email"]', { timeout: 12000 });
  } catch (e) {
    console.log('  No email input found on Google page');
    return false;
  }

  await page.fill('input[type="email"]', GOOGLE_EMAIL);
  await sleep(300);
  await page.click('#identifierNext');
  await sleep(3000);
  await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
  await ss(page, 'google-after-email');

  try {
    await page.waitForSelector('input[type="password"]', { timeout: 12000 });
  } catch (e) {
    console.log('  No password input; checking URL:', page.url());
    await ss(page, 'google-no-password');
    if (page.url().includes('challenge') || page.url().includes('2-step')) return '2FA';
    return false;
  }

  await page.fill('input[type="password"]', GOOGLE_PASSWORD);
  await sleep(300);
  await page.click('#passwordNext');
  await sleep(4000);
  await page.waitForLoadState('networkidle', { timeout: 20000 }).catch(() => {});
  await ss(page, 'google-after-password');

  console.log('  After password URL:', page.url());
  if (page.url().includes('challenge') || page.url().includes('2-step') || page.url().includes('signin/v2/challenge')) {
    console.log('  ⚠️ 2FA REQUIRED');
    return '2FA';
  }
  return true;
}

// ============================================================
// TOOLIFY.AI - Has Google OAuth popup
// ============================================================
async function doToolify(browser, product) {
  console.log(`\n=== TOOLIFY.AI - ${product.name} ===`);
  const ctx = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });
  const page = await ctx.newPage();
  const r = { site: 'toolify.ai', product: product.name };

  try {
    // Visit home first
    await page.goto('https://www.toolify.ai', { timeout: 30000, waitUntil: 'domcontentloaded' });
    await sleep(4000);
    await ss(page, `toolify-${product.name}-home`);
    
    // Click Login button
    const loginBtn = await page.$('a:has-text("Login"), button:has-text("Login"), a[href*="login"]');
    if (!loginBtn) {
      console.log('  No login button found');
      await ss(page, `toolify-${product.name}-no-login`);
    } else {
      console.log('  Found login button, clicking...');
      
      // Look for popup
      const [popup] = await Promise.all([
        ctx.waitForEvent('page', { timeout: 8000 }).catch(() => null),
        loginBtn.click()
      ]);
      await sleep(2000);
      
      if (popup) {
        await popup.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
        console.log('  Login popup URL:', popup.url());
        await ss(popup, `toolify-${product.name}-login-popup`);
        
        // Look for "Continue with Google" in the popup
        const googleBtn = await popup.$('button:has-text("Continue with Google"), a:has-text("Continue with Google"), button:has-text("Google"), [class*="google" i]');
        if (googleBtn) {
          console.log('  Found Google button in popup');
          const [googlePopup] = await Promise.all([
            ctx.waitForEvent('page', { timeout: 8000 }).catch(() => null),
            googleBtn.click()
          ]);
          if (googlePopup) {
            await googlePopup.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
            const result = await doGoogleLogin(googlePopup);
            if (result === '2FA') return { ...r, status: 'NEED_2FA_CODE' };
            // Wait for popup to close
            await googlePopup.waitForEvent('close', { timeout: 15000 }).catch(() => {});
          } else {
            // Maybe navigated in same popup
            await popup.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
            if (popup.url().includes('google') || popup.url().includes('accounts.google')) {
              const result = await doGoogleLogin(popup);
              if (result === '2FA') return { ...r, status: 'NEED_2FA_CODE' };
            }
          }
        } else {
          // Try email/password in the popup
          await ss(popup, `toolify-${product.name}-popup-content`);
          const emailInput = await popup.$('input[type="email"], input[name="email"]');
          const pwdInput = await popup.$('input[type="password"]');
          if (emailInput && pwdInput) {
            await emailInput.fill(GOOGLE_EMAIL);
            await pwdInput.fill(GOOGLE_PASSWORD);
            await ss(popup, `toolify-${product.name}-popup-filled`);
            const submitBtn = await popup.$('button[type="submit"], button:has-text("Sign in"), button:has-text("Login")');
            if (submitBtn) await submitBtn.click();
          }
        }
        
        // Wait for popup to close
        await popup.waitForEvent('close', { timeout: 10000 }).catch(() => {});
      } else {
        // Same page navigation for login
        await page.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
        await ss(page, `toolify-${product.name}-login-same-page`);
        
        const googleBtn = await page.$('button:has-text("Continue with Google"), button:has-text("Google"), a:has-text("Google")');
        if (googleBtn) {
          const [gPopup] = await Promise.all([
            ctx.waitForEvent('page', { timeout: 8000 }).catch(() => null),
            googleBtn.click()
          ]);
          if (gPopup) {
            await gPopup.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
            const result = await doGoogleLogin(gPopup);
            if (result === '2FA') return { ...r, status: 'NEED_2FA_CODE' };
            await gPopup.waitForEvent('close', { timeout: 15000 }).catch(() => {});
          }
        }
      }
    }
    
    await sleep(3000);
    await ss(page, `toolify-${product.name}-after-auth`);
    console.log('  After auth URL:', page.url());
    
    // Now try to find the submit form
    // Navigate to submit page
    await page.goto('https://www.toolify.ai/submit', { timeout: 30000, waitUntil: 'domcontentloaded' }).catch(() => {});
    await sleep(3000);
    await ss(page, `toolify-${product.name}-submit1`);
    console.log('  /submit URL:', page.url());
    
    let submitPageText = await page.evaluate(() => document.body.innerText.substring(0, 300));
    console.log('  Submit page text:', submitPageText);
    
    if (submitPageText.includes('404') || submitPageText.includes('not found')) {
      // Try other submit URLs
      for (const submitUrl of ['https://www.toolify.ai/ai-tool/submit', 'https://www.toolify.ai/tools/new']) {
        await page.goto(submitUrl, { timeout: 30000, waitUntil: 'domcontentloaded' }).catch(() => {});
        await sleep(2000);
        submitPageText = await page.evaluate(() => document.body.innerText.substring(0, 200));
        if (!submitPageText.includes('404') && !submitPageText.includes('not found')) break;
      }
    }
    
    // Look for submit in nav
    await page.goto('https://www.toolify.ai', { timeout: 30000, waitUntil: 'domcontentloaded' }).catch(() => {});
    await sleep(2000);
    const submitNavLink = await page.$('a:has-text("Submit"), nav a[href*="submit"]');
    if (submitNavLink) {
      const submitHref = await submitNavLink.getAttribute('href');
      console.log('  Submit nav href:', submitHref);
      await submitNavLink.click();
      await sleep(2000);
    }
    
    await ss(page, `toolify-${product.name}-submit-page`);
    console.log('  Submit page URL:', page.url());
    
    // Get all links to understand site structure
    const allLinks = await page.$$eval('a[href]', els => 
      els.map(el => ({ text: el.textContent?.trim(), href: el.href }))
         .filter(l => l.text && l.href)
         .slice(0, 30)
    );
    console.log('  Links:', JSON.stringify(allLinks));
    
    // Look for form inputs
    const inputs = await page.$$eval('input, textarea', els => 
      els.map(el => ({ type: el.getAttribute('type'), name: el.name, id: el.id, placeholder: el.placeholder }))
    );
    console.log('  Inputs:', JSON.stringify(inputs));
    
    if (inputs.length === 0) {
      return { ...r, status: 'NO_FORM_FOUND', url: page.url(), note: 'Submit form not accessible or 404' };
    }
    
    // Fill form
    let filled = false;
    for (const inp of inputs) {
      if (['hidden','submit','button'].includes(inp.type)) continue;
      const sel = inp.id ? `#${inp.id}` : inp.name ? `[name="${inp.name}"]` : null;
      if (!sel) continue;
      const key = (inp.placeholder || inp.name || inp.id || '').toLowerCase();
      let val = null;
      if (key.includes('name') || key.includes('title') || key.includes('tool')) val = product.name;
      else if (key.includes('url') || key.includes('link') || key.includes('website')) val = product.url;
      else if (key.includes('tagline') || key.includes('slogan')) val = product.tagline;
      else if (key.includes('desc')) val = product.description;
      else if (key.includes('email')) val = product.email;
      if (val) { try { await page.fill(sel, val); filled = true; } catch (e) {} }
    }
    
    await ss(page, `toolify-${product.name}-form-filled`);
    
    if (filled) {
      const btn = await page.$('button[type="submit"], button:has-text("Submit"), input[type="submit"]');
      if (btn) {
        await btn.click();
        await sleep(3000);
        await ss(page, `toolify-${product.name}-after-submit`);
        return { ...r, status: 'SUBMITTED', url: page.url() };
      }
    }
    
    return { ...r, status: 'INCOMPLETE', url: page.url() };
  } catch (e) {
    console.log('  Error:', e.message);
    await ss(page, `toolify-${product.name}-error`).catch(() => {});
    return { ...r, status: 'ERROR', error: e.message };
  } finally {
    await ctx.close();
  }
}

// ============================================================
// BETALIST.COM - Email/password signup then submit
// ============================================================
let betalistCtx = null;
let betalistPage = null;
let betalistAuthed = false;

async function ensureBetalistAuth(browser) {
  if (betalistAuthed) return true;
  
  const ctx = betalistCtx || await browser.newContext();
  betalistCtx = ctx;
  const page = betalistPage || await ctx.newPage();
  betalistPage = page;
  
  console.log('  Setting up betalist auth...');
  
  // Go to sign_in page
  await page.goto('https://betalist.com/sign_in', { timeout: 30000 });
  await sleep(2000);
  await ss(page, 'betalist-signin-page');
  
  const pageText = await page.evaluate(() => document.body.innerText.substring(0, 300));
  console.log('  signin page text:', pageText);
  
  // Look for email+password form
  const emailInput = await page.$('input[type="email"], input[name*="email"]');
  const pwdInput = await page.$('input[type="password"]');
  
  if (emailInput && pwdInput) {
    console.log('  Filling email/password login form');
    await emailInput.fill(GOOGLE_EMAIL);
    await pwdInput.fill(GOOGLE_PASSWORD);
    await ss(page, 'betalist-login-filled');
    
    const submitBtn = await page.$('button[type="submit"], input[type="submit"], button:has-text("Sign in"), button:has-text("Login")');
    if (submitBtn) {
      await submitBtn.click();
      await sleep(3000);
      await ss(page, 'betalist-after-login');
      console.log('  After login URL:', page.url());
      
      if (!page.url().includes('sign_in') && !page.url().includes('login')) {
        betalistAuthed = true;
        return true;
      }
    }
  }
  
  // If login failed (no account), try to register
  console.log('  Login may have failed, trying sign up...');
  await page.goto('https://betalist.com/sign_up', { timeout: 30000 });
  await sleep(2000);
  await ss(page, 'betalist-signup-page');
  
  const usernameInput = await page.$('input[name="user[username]"], input[id="user_username"]');
  const emailReg = await page.$('input[name="user[email]"], input[id="user_email"]');
  const pwdReg = await page.$('input[name="user[password]"], input[id="user_password"]');
  const pwdConfirm = await page.$('input[name="user[password_confirmation]"], input[id="user_password_confirmation"]');
  
  if (usernameInput) await usernameInput.fill('pantrymatehello');
  if (emailReg) await emailReg.fill(GOOGLE_EMAIL);
  if (pwdReg) await pwdReg.fill(GOOGLE_PASSWORD);
  if (pwdConfirm) await pwdConfirm.fill(GOOGLE_PASSWORD);
  
  await ss(page, 'betalist-signup-filled');
  
  const regBtn = await page.$('input[type="submit"], button[type="submit"]');
  if (regBtn) {
    await regBtn.click();
    await sleep(3000);
    await ss(page, 'betalist-after-signup');
    console.log('  After signup URL:', page.url());
    
    if (!page.url().includes('sign_up')) {
      betalistAuthed = true;
      return true;
    }
  }
  
  // Check if already logged in by checking for user menu
  const userMenu = await page.$('[class*="avatar"], [class*="user"], a[href*="/users/"]');
  if (userMenu) {
    betalistAuthed = true;
    return true;
  }
  
  return false;
}

async function doBetalist(browser, product) {
  console.log(`\n=== BETALIST.COM - ${product.name} ===`);
  const r = { site: 'betalist.com', product: product.name };
  
  try {
    await ensureBetalistAuth(browser);
    
    const page = betalistPage;
    
    // Navigate to submit
    await page.goto('https://betalist.com/startups/new', { timeout: 30000 });
    await sleep(2000);
    await ss(page, `betalist-${product.name}-submit-page`);
    console.log('  Submit page URL:', page.url());
    
    const pageText = await page.evaluate(() => document.body.innerText.substring(0, 500));
    console.log('  Page text:', pageText);
    
    if (page.url().includes('sign') || page.url().includes('login')) {
      return { ...r, status: 'AUTH_REQUIRED', note: 'Registration may need email confirmation' };
    }
    
    const inputs = await page.$$eval('input, textarea, select', els => 
      els.map(el => ({ 
        tag: el.tagName, type: el.getAttribute('type'), 
        name: el.name, id: el.id, placeholder: el.placeholder,
        label: document.querySelector(`label[for="${el.id}"]`)?.textContent?.trim()
      }))
    );
    console.log('  Inputs:', JSON.stringify(inputs));
    
    if (inputs.filter(i => !['hidden','submit'].includes(i.type)).length === 0) {
      return { ...r, status: 'NO_FORM', url: page.url() };
    }
    
    let filled = false;
    for (const inp of inputs) {
      if (['hidden','submit','button'].includes(inp.type)) continue;
      const sel = inp.id ? `#${inp.id}` : inp.name ? `[name="${inp.name}"]` : null;
      if (!sel) continue;
      const key = (inp.label || inp.placeholder || inp.name || inp.id || '').toLowerCase();
      let val = null;
      if (key.includes('name') || key.includes('startup') || key.includes('product')) val = product.name;
      else if (key.includes('url') || key.includes('website') || key.includes('link')) val = product.url;
      else if (key.includes('tagline') || key.includes('headline')) val = product.tagline;
      else if (key.includes('desc') || key.includes('about')) val = product.description;
      else if (key.includes('email') || key.includes('contact')) val = product.email;
      if (val) { try { await page.fill(sel, val); filled = true; } catch (e) {} }
    }
    
    await ss(page, `betalist-${product.name}-form-filled`);
    
    if (filled) {
      const btn = await page.$('button[type="submit"], input[type="submit"], button:has-text("Submit")');
      if (btn) {
        await btn.click();
        await sleep(3000);
        await ss(page, `betalist-${product.name}-after-submit`);
        console.log('  After submit URL:', page.url());
        return { ...r, status: 'SUBMITTED', url: page.url() };
      }
    }
    
    return { ...r, status: 'NO_SUBMIT_BUTTON', url: page.url() };
  } catch (e) {
    console.log('  Error:', e.message);
    return { ...r, status: 'ERROR', error: e.message };
  }
}

// ============================================================
// SAASHUB.COM - Handle Cloudflare then find correct submit URL
// ============================================================
let saashubCtx = null;
let saashubPage = null;
let saashubAuthed = false;

async function ensureSaashubAuth(browser) {
  if (saashubAuthed) return true;
  
  const ctx = saashubCtx || await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });
  saashubCtx = ctx;
  const page = saashubPage || await ctx.newPage();
  saashubPage = page;
  
  // Go to home, wait for CF to resolve
  console.log('  Loading saashub...');
  await page.goto('https://www.saashub.com', { timeout: 60000, waitUntil: 'domcontentloaded' });
  await sleep(5000);
  await ss(page, 'saashub-initial-load');
  console.log('  URL after load:', page.url());
  
  let pageText = await page.evaluate(() => document.body.innerText.substring(0, 200));
  console.log('  Page text:', pageText);
  
  // If CF challenge, wait more
  if (pageText.includes('verify') || pageText.includes('Cloudflare') || pageText.includes('challenge')) {
    console.log('  Waiting for CF challenge to pass...');
    await sleep(8000);
    pageText = await page.evaluate(() => document.body.innerText.substring(0, 200));
    console.log('  After wait text:', pageText);
  }
  
  await ss(page, 'saashub-home');
  
  // Click Login
  const loginBtn = await page.$('a:has-text("Login"), a:has-text("Sign in"), a[href*="login"], a[href*="sign_in"]');
  if (loginBtn) {
    const href = await loginBtn.getAttribute('href');
    console.log('  Login href:', href);
    await loginBtn.click();
    await sleep(3000);
    await ss(page, 'saashub-login-page');
    console.log('  Login page URL:', page.url());
    
    const loginPageText = await page.evaluate(() => document.body.innerText.substring(0, 300));
    console.log('  Login page text:', loginPageText);
    
    // Look for Google OAuth
    const googleLink = await page.$('a[href*="google"], a[href*="omniauth"], button:has-text("Google"), a:has-text("Google")');
    if (googleLink) {
      const href2 = await googleLink.getAttribute('href');
      console.log('  Google link:', href2);
      
      const [popup] = await Promise.all([
        ctx.waitForEvent('page', { timeout: 5000 }).catch(() => null),
        googleLink.click()
      ]);
      await sleep(3000);
      
      if (popup) {
        await popup.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
        console.log('  Google popup URL:', popup.url());
        const result = await doGoogleLogin(popup);
        if (result === '2FA') return '2FA';
        await popup.waitForEvent('close', { timeout: 15000 }).catch(() => {});
      } else {
        await page.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
        if (page.url().includes('google') || page.url().includes('accounts')) {
          const result = await doGoogleLogin(page);
          if (result === '2FA') return '2FA';
          await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
        }
      }
      
      await sleep(3000);
      await ss(page, 'saashub-after-auth');
      console.log('  After auth URL:', page.url());
      saashubAuthed = true;
    } else {
      // Try email/password
      const emailInput = await page.$('input[type="email"], input[name*="email"]');
      const pwdInput = await page.$('input[type="password"]');
      if (emailInput && pwdInput) {
        await emailInput.fill(GOOGLE_EMAIL);
        await pwdInput.fill(GOOGLE_PASSWORD);
        const btn = await page.$('button[type="submit"], input[type="submit"]');
        if (btn) {
          await btn.click();
          await sleep(3000);
          await ss(page, 'saashub-after-login-attempt');
          saashubAuthed = true;
        }
      }
    }
  } else {
    console.log('  No login button found on saashub');
    await ss(page, 'saashub-no-login-btn');
    // Get all links
    const links = await page.$$eval('a[href]', els => els.map(el => ({ text: el.textContent?.trim(), href: el.href })).slice(0, 30));
    console.log('  Links:', JSON.stringify(links));
  }
  
  return saashubAuthed;
}

async function doSaashub(browser, product) {
  console.log(`\n=== SAASHUB.COM - ${product.name} ===`);
  const r = { site: 'saashub.com', product: product.name };
  
  try {
    const authResult = await ensureSaashubAuth(browser);
    if (authResult === '2FA') return { ...r, status: 'NEED_2FA_CODE' };
    
    const page = saashubPage;
    
    // Find submit URL - click "Submit a Product" from nav
    await page.goto('https://www.saashub.com', { timeout: 30000, waitUntil: 'domcontentloaded' });
    await sleep(3000);
    
    const submitLink = await page.$('a:has-text("Submit"), a[href*="submit"], a:has-text("Add a Product"), a:has-text("Feature My Product")');
    if (submitLink) {
      const submitHref = await submitLink.getAttribute('href');
      console.log('  Submit link href:', submitHref);
      await submitLink.click();
      await sleep(2000);
    } else {
      // Try known URLs
      const urls = [
        'https://www.saashub.com/promote',
        'https://www.saashub.com/products/new',
        'https://www.saashub.com/add',
      ];
      for (const url of urls) {
        await page.goto(url, { timeout: 20000 }).catch(() => {});
        await sleep(2000);
        const t = await page.evaluate(() => document.body.innerText.substring(0, 100));
        if (!t.includes('404')) { console.log('  Found working URL:', url); break; }
      }
    }
    
    await ss(page, `saashub-${product.name}-submit-page`);
    console.log('  Submit page URL:', page.url());
    
    const pageText = await page.evaluate(() => document.body.innerText.substring(0, 500));
    console.log('  Page text:', pageText);
    
    const inputs = await page.$$eval('input, textarea', els => 
      els.map(el => ({ type: el.getAttribute('type'), name: el.name, id: el.id, placeholder: el.placeholder }))
    );
    console.log('  Inputs:', JSON.stringify(inputs));
    
    if (inputs.filter(i => !['hidden','submit'].includes(i.type)).length === 0) {
      return { ...r, status: 'NO_FORM', url: page.url(), note: pageText.substring(0, 200) };
    }
    
    let filled = false;
    for (const inp of inputs) {
      if (['hidden','submit','button'].includes(inp.type)) continue;
      const sel = inp.id ? `#${inp.id}` : inp.name ? `[name="${inp.name}"]` : null;
      if (!sel) continue;
      const key = (inp.placeholder || inp.name || inp.id || '').toLowerCase();
      let val = null;
      if (key.includes('name') || key.includes('product') || key.includes('title')) val = product.name;
      else if (key.includes('url') || key.includes('website')) val = product.url;
      else if (key.includes('tagline') || key.includes('short')) val = product.tagline;
      else if (key.includes('desc')) val = product.description;
      else if (key.includes('email')) val = product.email;
      if (val) { try { await page.fill(sel, val); filled = true; } catch (e) {} }
    }
    
    await ss(page, `saashub-${product.name}-form-filled`);
    
    if (filled) {
      const btn = await page.$('button[type="submit"], input[type="submit"], button:has-text("Submit"), button:has-text("Save")');
      if (btn) {
        await btn.click();
        await sleep(3000);
        await ss(page, `saashub-${product.name}-after-submit`);
        return { ...r, status: 'SUBMITTED', url: page.url() };
      }
    }
    
    return { ...r, status: 'NO_SUBMIT_BUTTON', url: page.url() };
  } catch (e) {
    console.log('  Error:', e.message);
    return { ...r, status: 'ERROR', error: e.message };
  }
}

// ============================================================
// UNEED.BE - Site under maintenance
// ============================================================
async function doUneed(browser, product) {
  console.log(`\n=== UNEED.BE - ${product.name} ===`);
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true });
  const page = await ctx.newPage();
  const r = { site: 'uneed.be', product: product.name };
  
  try {
    await page.goto('https://www.uneed.be', { timeout: 30000 });
    await sleep(5000); // wait longer for possible config
    await ss(page, `uneed-${product.name}-home`);
    
    const text = await page.evaluate(() => document.body.innerText);
    console.log('  Page text:', text.substring(0, 200));
    
    if (text.includes('configuration') || text.includes('stand by') || text.includes('maintenance')) {
      // Try without www
      await page.goto('https://uneed.be', { timeout: 30000 });
      await sleep(3000);
      await ss(page, `uneed-${product.name}-no-www`);
      const text2 = await page.evaluate(() => document.body.innerText);
      console.log('  No-www text:', text2.substring(0, 200));
      
      if (text2.includes('configuration') || text2.includes('stand by')) {
        return { ...r, status: 'SITE_UNDER_MAINTENANCE', note: text2.substring(0, 100) };
      }
    }
    
    // Try to find submit
    const submitBtn = await page.$('a:has-text("Submit"), button:has-text("Submit"), a:has-text("Add"), a[href*="submit"]');
    if (!submitBtn) {
      const links = await page.$$eval('a[href]', els => els.map(el => ({ text: el.textContent?.trim(), href: el.href })).slice(0, 20));
      console.log('  Links:', JSON.stringify(links));
      return { ...r, status: 'NO_SUBMIT_LINK', url: page.url() };
    }
    
    await submitBtn.click();
    await sleep(2000);
    await ss(page, `uneed-${product.name}-submit-page`);
    
    // Google auth
    const googleBtn = await page.$('[class*="google" i], button:has-text("Google"), a:has-text("Google"), a[href*="google"]');
    if (googleBtn) {
      const [popup] = await Promise.all([
        ctx.waitForEvent('page', { timeout: 5000 }).catch(() => null),
        googleBtn.click()
      ]);
      if (popup) {
        await popup.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
        const result = await doGoogleLogin(popup);
        if (result === '2FA') return { ...r, status: 'NEED_2FA_CODE' };
        await popup.waitForEvent('close', { timeout: 15000 }).catch(() => {});
      }
      await sleep(2000);
    }
    
    await ss(page, `uneed-${product.name}-form`);
    
    const inputs = await page.$$eval('input, textarea', els => 
      els.map(el => ({ type: el.getAttribute('type'), name: el.name, id: el.id, placeholder: el.placeholder }))
    );
    
    let filled = false;
    for (const inp of inputs) {
      if (['hidden','submit'].includes(inp.type)) continue;
      const sel = inp.id ? `#${inp.id}` : inp.name ? `[name="${inp.name}"]` : null;
      if (!sel) continue;
      const key = (inp.placeholder || inp.name || inp.id || '').toLowerCase();
      let val = null;
      if (key.includes('name') || key.includes('product')) val = product.name;
      else if (key.includes('url') || key.includes('website') || key.includes('link')) val = product.url;
      else if (key.includes('tagline')) val = product.tagline;
      else if (key.includes('desc')) val = product.description;
      else if (key.includes('email')) val = product.email;
      if (val) { try { await page.fill(sel, val); filled = true; } catch (e) {} }
    }
    
    if (filled) {
      const btn = await page.$('button[type="submit"], input[type="submit"]');
      if (btn) {
        await btn.click();
        await sleep(3000);
        await ss(page, `uneed-${product.name}-submitted`);
        return { ...r, status: 'SUBMITTED' };
      }
    }
    
    return { ...r, status: 'INCOMPLETE', url: page.url() };
  } catch (e) {
    console.log('  Error:', e.message);
    await ss(page, `uneed-${product.name}-error`).catch(() => {});
    return { ...r, status: 'ERROR', error: e.message };
  } finally {
    await ctx.close();
  }
}

// ============================================================
// MAIN
// ============================================================
async function main() {
  console.log('=== V3 Directory Submissions ===\n');
  
  const browser = await chromium.launch({
    headless: true,
    slowMo: 100,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });
  
  const results = [];
  
  try {
    // Uneed (likely under maintenance)
    results.push(await doUneed(browser, PANTRYMATE));
    results.push(await doUneed(browser, UNITFIX));
    
    // Betalist
    results.push(await doBetalist(browser, PANTRYMATE));
    results.push(await doBetalist(browser, UNITFIX));
    
    // SaaSHub
    results.push(await doSaashub(browser, PANTRYMATE));
    results.push(await doSaashub(browser, UNITFIX));
    
    // Toolify
    results.push(await doToolify(browser, PANTRYMATE));
    results.push(await doToolify(browser, UNITFIX));
    
  } finally {
    if (saashubCtx) await saashubCtx.close().catch(() => {});
    await browser.close();
  }
  
  console.log('\n\n=== FINAL RESULTS ===');
  console.log(JSON.stringify(results, null, 2));
}

main().catch(console.error);
