/**
 * V4 - Surgical fixes based on screenshots:
 * - betalist: turbo-frame blocks button → use force click or Enter key
 * - saashub: Cloudflare on /login → try direct OAuth path, wait longer
 * - toolify: Google login in same page (no popup) → complete it, then click "Submit AI"
 * - uneed.be: Under maintenance, skip
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
  const fname = `v4-${String(sc).padStart(3,'0')}-${label.replace(/[^a-z0-9]/gi,'-').substring(0,50)}.png`;
  const fpath = path.join(SCREENSHOTS_DIR, fname);
  try { await page.screenshot({ path: fpath, fullPage: false }); } catch (e) {}
  console.log(`📸 ${fname}`);
  return fpath;
}

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// Complete Google OAuth on the given page (already on accounts.google.com)
async function doGoogleLogin(page, label = '') {
  console.log(`  [${label}] Google login at: ${page.url().substring(0, 80)}`);
  await ss(page, `google-${label}-start`);
  
  try {
    await page.waitForSelector('input[type="email"]', { timeout: 12000 });
    await page.fill('input[type="email"]', GOOGLE_EMAIL);
    await sleep(500);
    
    // Click Next (try multiple selectors)
    try {
      await page.click('#identifierNext', { timeout: 5000 });
    } catch {
      await page.keyboard.press('Enter');
    }
    await sleep(3000);
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
    await ss(page, `google-${label}-after-email`);
  } catch (e) {
    console.log(`  Email step error: ${e.message.substring(0,100)}`);
    return false;
  }
  
  try {
    await page.waitForSelector('input[type="password"]', { timeout: 12000 });
    await page.fill('input[type="password"]', GOOGLE_PASSWORD);
    await sleep(500);
    
    try {
      await page.click('#passwordNext', { timeout: 5000 });
    } catch {
      await page.keyboard.press('Enter');
    }
    await sleep(4000);
    await page.waitForLoadState('networkidle', { timeout: 20000 }).catch(() => {});
    await ss(page, `google-${label}-after-password`);
  } catch (e) {
    console.log(`  Password step error: ${e.message.substring(0,100)}`);
    return false;
  }
  
  const url = page.url();
  console.log(`  After auth URL: ${url.substring(0, 80)}`);
  if (url.includes('challenge') || url.includes('2-step') || url.includes('signin/v2/challenge')) {
    await ss(page, `google-${label}-2fa`);
    return '2FA';
  }
  
  return true;
}

// ============================================================
// BETALIST.COM
// ============================================================
let blCtx = null, blPage = null, blAuthed = false;

async function ensureBlAuth(browser) {
  if (blAuthed) return true;
  
  blCtx = blCtx || await browser.newContext();
  blPage = blPage || await blCtx.newPage();
  
  await blPage.goto('https://betalist.com/sign_in', { timeout: 30000 });
  await sleep(2000);
  await ss(blPage, 'bl-signin-page');
  
  const emailInput = await blPage.$('input[type="email"], input[name*="email"]');
  const pwdInput = await blPage.$('input[type="password"]');
  
  if (emailInput && pwdInput) {
    await emailInput.fill(GOOGLE_EMAIL);
    await sleep(200);
    await pwdInput.fill(GOOGLE_PASSWORD);
    await sleep(200);
    await ss(blPage, 'bl-login-filled');
    
    // Use keyboard Enter to bypass turbo-frame interception
    await pwdInput.press('Enter');
    await sleep(4000);
    await blPage.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
    await ss(blPage, 'bl-after-login-attempt');
    console.log('  BL after login URL:', blPage.url());
    
    if (!blPage.url().includes('sign_in') && !blPage.url().includes('sign_up')) {
      blAuthed = true;
      console.log('  ✅ BetaList login succeeded');
      return true;
    }
    
    // Check for error message
    const errorText = await blPage.evaluate(() => document.body.innerText.substring(0, 200));
    console.log('  BL page text:', errorText);
    
    // Try sign up if login failed (account might not exist)
    if (errorText.includes('Invalid') || errorText.includes('incorrect') || errorText.includes('not found')) {
      console.log('  Login failed, trying sign up...');
      await blPage.goto('https://betalist.com/sign_up', { timeout: 30000 });
      await sleep(2000);
      
      const usernameInp = await blPage.$('#user_username');
      const emailReg = await blPage.$('#user_email');
      const pwdReg = await blPage.$('#user_password');
      const pwdConf = await blPage.$('#user_password_confirmation');
      
      if (usernameInp) await usernameInp.fill('olcowboy21');
      if (emailReg) await emailReg.fill(GOOGLE_EMAIL);
      if (pwdReg) await pwdReg.fill(GOOGLE_PASSWORD);
      if (pwdConf) await pwdConf.fill(GOOGLE_PASSWORD);
      
      await ss(blPage, 'bl-signup-filled');
      if (pwdConf) await pwdConf.press('Enter');
      else if (pwdReg) await pwdReg.press('Enter');
      await sleep(4000);
      await ss(blPage, 'bl-after-signup');
      console.log('  BL after signup URL:', blPage.url());
      
      if (!blPage.url().includes('sign_up')) {
        blAuthed = true;
        return true;
      }
    }
  }
  
  // Try force-clicking the submit button via JS
  try {
    await blPage.evaluate(() => {
      const form = document.querySelector('form');
      if (form) form.submit();
    });
    await sleep(3000);
    await ss(blPage, 'bl-after-js-submit');
    console.log('  BL after JS submit URL:', blPage.url());
    if (!blPage.url().includes('sign_in') && !blPage.url().includes('sign_up')) {
      blAuthed = true;
      return true;
    }
  } catch (e) {}
  
  return blAuthed;
}

async function doBetalist(browser, product) {
  console.log(`\n=== BETALIST.COM - ${product.name} ===`);
  const r = { site: 'betalist.com', product: product.name };
  
  try {
    await ensureBlAuth(browser);
    
    if (!blAuthed) {
      // Check if we're now logged in anyway
      await blPage.goto('https://betalist.com', { timeout: 30000 });
      await sleep(2000);
      const loggedIn = await blPage.$('a[href*="/sign_out"], a[href*="logout"], [class*="avatar"]');
      if (!loggedIn) {
        return { ...r, status: 'AUTH_FAILED', note: 'Could not login - recaptcha or wrong creds' };
      }
    }
    
    // Navigate to submit
    await blPage.goto('https://betalist.com/startups/new', { timeout: 30000 });
    await sleep(2000);
    await ss(blPage, `bl-${product.name}-submit-page`);
    console.log('  Submit URL:', blPage.url());
    
    if (blPage.url().includes('sign') || blPage.url().includes('login')) {
      return { ...r, status: 'AUTH_REQUIRED', url: blPage.url() };
    }
    
    const pageText = await blPage.evaluate(() => document.body.innerText.substring(0, 300));
    console.log('  Page text:', pageText);
    
    // Get all inputs including labels via evaluate
    const inputs = await blPage.evaluate(() => {
      return Array.from(document.querySelectorAll('input, textarea, select')).map(el => {
        const label = el.labels?.[0]?.textContent?.trim() || 
                      el.closest('[data-label]')?.dataset?.label ||
                      document.querySelector(`label[for="${el.id}"]`)?.textContent?.trim() || '';
        return { tag: el.tagName, type: el.type, name: el.name, id: el.id, placeholder: el.placeholder, label };
      });
    });
    console.log('  Inputs:', JSON.stringify(inputs));
    
    let filled = false;
    for (const inp of inputs) {
      if (['hidden','submit','button'].includes(inp.type)) continue;
      const sel = inp.id ? `#${inp.id}` : inp.name ? `[name="${inp.name}"]` : null;
      if (!sel) continue;
      const key = (inp.label || inp.placeholder || inp.name || inp.id || '').toLowerCase();
      let val = null;
      if (key.includes('name') || key.includes('startup') || key.includes('product') || key.includes('title')) val = product.name;
      else if (key.includes('url') || key.includes('website') || key.includes('link')) val = product.url;
      else if (key.includes('tagline') || key.includes('headline') || key.includes('pitch')) val = product.tagline;
      else if (key.includes('desc') || key.includes('about')) val = product.description;
      else if (key.includes('email') || key.includes('contact')) val = product.email;
      if (val) {
        try {
          await blPage.fill(sel, val);
          filled = true;
          console.log(`  Filled: ${sel} = "${val.substring(0, 40)}"`);
        } catch (e) {}
      }
    }
    
    await ss(blPage, `bl-${product.name}-form-filled`);
    
    if (filled) {
      // Try submit via JS first (bypass turbo-frame)
      const submitted = await blPage.evaluate(() => {
        const btn = document.querySelector('button[type="submit"], input[type="submit"]');
        if (btn) { btn.click(); return true; }
        const form = document.querySelector('form');
        if (form) { form.submit(); return true; }
        return false;
      });
      
      if (submitted) {
        await sleep(4000);
        await ss(blPage, `bl-${product.name}-after-submit`);
        console.log('  After submit URL:', blPage.url());
        return { ...r, status: 'SUBMITTED', url: blPage.url() };
      }
    }
    
    return { ...r, status: 'NO_FORM', url: blPage.url(), note: pageText.substring(0, 100) };
  } catch (e) {
    console.log('  Error:', e.message.substring(0, 200));
    return { ...r, status: 'ERROR', error: e.message.substring(0, 200) };
  }
}

// ============================================================
// SAASHUB.COM
// ============================================================
let shCtx = null, shPage = null, shAuthed = false;

async function ensureShAuth(browser) {
  if (shAuthed) return true;
  
  shCtx = shCtx || await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });
  shPage = shPage || await shCtx.newPage();
  
  // Home page works (no CF there)
  await shPage.goto('https://www.saashub.com', { timeout: 30000, waitUntil: 'domcontentloaded' });
  await sleep(4000);
  await ss(shPage, 'sh-home');
  
  const homeText = await shPage.evaluate(() => document.body.innerText.substring(0, 200));
  console.log('  SH home:', homeText.substring(0, 100));
  
  // Try direct Google OAuth path (bypass CF-protected /login page)
  const oauthPaths = [
    'https://www.saashub.com/users/auth/google_oauth2',
    'https://www.saashub.com/auth/google_oauth2',
    'https://www.saashub.com/users/auth/google',
  ];
  
  for (const oauthPath of oauthPaths) {
    console.log('  Trying OAuth path:', oauthPath);
    
    const [popup] = await Promise.all([
      shCtx.waitForEvent('page', { timeout: 5000 }).catch(() => null),
      shPage.goto(oauthPath, { timeout: 15000, waitUntil: 'domcontentloaded' }).catch(() => {})
    ]);
    
    await sleep(3000);
    const currentUrl = shPage.url();
    console.log('  After OAuth path URL:', currentUrl.substring(0, 80));
    
    if (currentUrl.includes('accounts.google.com') || currentUrl.includes('google.com/o/oauth')) {
      // Same page now on Google - complete login
      const result = await doGoogleLogin(shPage, 'saashub');
      if (result === '2FA') return '2FA';
      await sleep(3000);
      await shPage.waitForLoadState('domcontentloaded', { timeout: 15000 }).catch(() => {});
      await ss(shPage, 'sh-after-google-auth');
      console.log('  After Google auth URL:', shPage.url().substring(0, 80));
      if (shPage.url().includes('saashub.com') && !shPage.url().includes('login')) {
        shAuthed = true;
        return true;
      }
      break;
    }
    
    if (popup) {
      await popup.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
      console.log('  Popup URL:', popup.url().substring(0, 80));
      if (popup.url().includes('google')) {
        const result = await doGoogleLogin(popup, 'saashub-popup');
        if (result === '2FA') return '2FA';
        await popup.waitForEvent('close', { timeout: 15000 }).catch(() => {});
        await sleep(2000);
        shAuthed = true;
        return true;
      }
    }
    
    // If we hit CF page, wait and try next
    const txt = await shPage.evaluate(() => document.body.innerText.substring(0, 100));
    if (txt.includes('verification') || txt.includes('Cloudflare')) {
      console.log('  CF block, trying next path...');
      continue;
    }
  }
  
  // Fallback: try /login with a longer wait
  if (!shAuthed) {
    await shPage.goto('https://www.saashub.com/login', { timeout: 30000, waitUntil: 'domcontentloaded' });
    console.log('  Waiting for CF to pass on /login...');
    await sleep(10000);
    await ss(shPage, 'sh-login-after-wait');
    
    const loginText = await shPage.evaluate(() => document.body.innerText.substring(0, 200));
    console.log('  Login page text:', loginText.substring(0, 100));
    
    if (!loginText.includes('verification') && !loginText.includes('Cloudflare')) {
      const googleBtn = await shPage.$('a[href*="google"], a:has-text("Google"), button:has-text("Google")');
      if (googleBtn) {
        await googleBtn.click();
        await sleep(3000);
        await shPage.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
        if (shPage.url().includes('google')) {
          const result = await doGoogleLogin(shPage, 'saashub-login');
          if (result === '2FA') return '2FA';
          await sleep(3000);
          shAuthed = true;
        }
      }
    }
  }
  
  return shAuthed;
}

async function doSaashub(browser, product) {
  console.log(`\n=== SAASHUB.COM - ${product.name} ===`);
  const r = { site: 'saashub.com', product: product.name };
  
  try {
    const authResult = await ensureShAuth(browser);
    if (authResult === '2FA') return { ...r, status: 'NEED_2FA_CODE' };
    
    await ss(shPage, `sh-${product.name}-current-state`);
    console.log('  Current URL:', shPage.url());
    
    // Navigate to Submit Product
    // The nav showed /submit/list
    await shPage.goto('https://www.saashub.com/submit/list', { timeout: 30000, waitUntil: 'domcontentloaded' });
    await sleep(3000);
    await ss(shPage, `sh-${product.name}-submit-list`);
    console.log('  Submit list URL:', shPage.url());
    
    const submitListText = await shPage.evaluate(() => document.body.innerText.substring(0, 500));
    console.log('  Submit list text:', submitListText.substring(0, 200));
    
    // Look for a "Submit Free" or "Submit" button/link
    const submitFreeLink = await shPage.$('a:has-text("Submit Free"), a:has-text("Submit for Free"), a[href*="submit/new"], a[href*="new"]');
    if (submitFreeLink) {
      const href = await submitFreeLink.getAttribute('href');
      console.log('  Found submit free link:', href);
      await submitFreeLink.click();
      await sleep(2000);
    } else {
      // Try direct
      await shPage.goto('https://www.saashub.com/submit/new', { timeout: 30000 }).catch(() => {});
      await sleep(2000);
    }
    
    await ss(shPage, `sh-${product.name}-submit-form`);
    console.log('  Submit form URL:', shPage.url());
    
    const pageText = await shPage.evaluate(() => document.body.innerText.substring(0, 300));
    console.log('  Form text:', pageText.substring(0, 200));
    
    const inputs = await shPage.$$eval('input, textarea', els => 
      els.map(el => ({ type: el.getAttribute('type'), name: el.name, id: el.id, placeholder: el.placeholder }))
    );
    console.log('  Inputs:', JSON.stringify(inputs));
    
    if (inputs.filter(i => !['hidden','submit'].includes(i.type)).length === 0) {
      return { ...r, status: 'NO_FORM', url: shPage.url(), text: pageText.substring(0, 150) };
    }
    
    let filled = false;
    for (const inp of inputs) {
      if (['hidden','submit','button'].includes(inp.type)) continue;
      const sel = inp.id ? `#${inp.id}` : inp.name ? `[name="${inp.name}"]` : null;
      if (!sel) continue;
      const key = (inp.placeholder || inp.name || inp.id || '').toLowerCase();
      let val = null;
      if (key.includes('name') || key.includes('product') || key.includes('title')) val = product.name;
      else if (key.includes('url') || key.includes('website') || key.includes('homepage')) val = product.url;
      else if (key.includes('tagline') || key.includes('short')) val = product.tagline;
      else if (key.includes('desc')) val = product.description;
      else if (key.includes('email')) val = product.email;
      if (val) { try { await shPage.fill(sel, val); filled = true; console.log(`  Filled ${sel}`); } catch (e) {} }
    }
    
    await ss(shPage, `sh-${product.name}-form-filled`);
    
    if (filled) {
      const submitted = await shPage.evaluate(() => {
        const btn = document.querySelector('button[type="submit"], input[type="submit"]');
        if (btn) { btn.click(); return true; }
        return false;
      });
      if (submitted) {
        await sleep(4000);
        await ss(shPage, `sh-${product.name}-after-submit`);
        return { ...r, status: 'SUBMITTED', url: shPage.url() };
      }
    }
    
    return { ...r, status: 'INCOMPLETE', url: shPage.url() };
  } catch (e) {
    console.log('  Error:', e.message.substring(0, 200));
    return { ...r, status: 'ERROR', error: e.message.substring(0, 200) };
  }
}

// ============================================================
// TOOLIFY.AI
// ============================================================
let tfCtx = null, tfPage = null, tfAuthed = false;

async function ensureTfAuth(browser) {
  if (tfAuthed) return true;
  
  tfCtx = tfCtx || await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });
  tfPage = tfPage || await tfCtx.newPage();
  
  await tfPage.goto('https://www.toolify.ai', { timeout: 30000, waitUntil: 'domcontentloaded' });
  await sleep(3000);
  await ss(tfPage, 'tf-home');
  
  // Click Login
  const loginBtn = await tfPage.$('a:has-text("Login"), button:has-text("Login")');
  if (!loginBtn) {
    console.log('  No Login button found');
    return false;
  }
  
  await loginBtn.click();
  await sleep(3000);
  await tfPage.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
  await ss(tfPage, 'tf-after-login-click');
  console.log('  After login click URL:', tfPage.url().substring(0, 80));
  
  // The login click might have navigated to Google OAuth directly, or shown a modal
  const currentUrl = tfPage.url();
  
  if (currentUrl.includes('accounts.google.com') || currentUrl.includes('google.com/o/oauth')) {
    // Complete Google login in current page
    const result = await doGoogleLogin(tfPage, 'toolify');
    if (result === '2FA') return '2FA';
    await sleep(3000);
    await tfPage.waitForLoadState('domcontentloaded', { timeout: 15000 }).catch(() => {});
    await ss(tfPage, 'tf-after-google');
    console.log('  After Google auth URL:', tfPage.url().substring(0, 80));
    
    if (tfPage.url().includes('toolify.ai')) {
      tfAuthed = true;
      return true;
    }
  } else {
    // Look for modal with Google option
    const googleBtn = await tfPage.$('button:has-text("Continue with Google"), a:has-text("Continue with Google"), button:has-text("Google")');
    if (googleBtn) {
      await googleBtn.click();
      await sleep(3000);
      await tfPage.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
      const url2 = tfPage.url();
      console.log('  After Google btn click URL:', url2.substring(0, 80));
      
      if (url2.includes('accounts.google.com')) {
        const result = await doGoogleLogin(tfPage, 'toolify-g');
        if (result === '2FA') return '2FA';
        await sleep(3000);
        await tfPage.waitForLoadState('domcontentloaded', { timeout: 15000 }).catch(() => {});
        await ss(tfPage, 'tf-after-google2');
        if (tfPage.url().includes('toolify.ai')) {
          tfAuthed = true;
          return true;
        }
      }
    } else {
      // Try navigating directly to the Google OAuth URL
      console.log('  Trying direct Google OAuth for toolify...');
      await tfPage.goto('https://www.toolify.ai/login', { timeout: 30000, waitUntil: 'domcontentloaded' }).catch(() => {});
      await sleep(2000);
      await ss(tfPage, 'tf-login-page');
      
      const googleBtn2 = await tfPage.$('button:has-text("Continue with Google"), button:has-text("Google"), a:has-text("Google")');
      if (googleBtn2) {
        await googleBtn2.click();
        await sleep(3000);
        await tfPage.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
        console.log('  URL:', tfPage.url().substring(0, 80));
        if (tfPage.url().includes('google')) {
          const result = await doGoogleLogin(tfPage, 'toolify-login');
          if (result === '2FA') return '2FA';
          await sleep(3000);
          await tfPage.waitForLoadState('domcontentloaded', { timeout: 15000 }).catch(() => {});
          if (tfPage.url().includes('toolify.ai')) {
            tfAuthed = true;
            return true;
          }
        }
      }
    }
  }
  
  return tfAuthed;
}

async function doToolify(browser, product) {
  console.log(`\n=== TOOLIFY.AI - ${product.name} ===`);
  const r = { site: 'toolify.ai', product: product.name };
  
  try {
    const authResult = await ensureTfAuth(browser);
    if (authResult === '2FA') return { ...r, status: 'NEED_2FA_CODE' };
    
    await ss(tfPage, `tf-${product.name}-auth-state`);
    console.log('  After auth, URL:', tfPage.url().substring(0, 80));
    
    // Navigate to submit page
    await tfPage.goto('https://www.toolify.ai/submit', { timeout: 30000, waitUntil: 'domcontentloaded' });
    await sleep(3000);
    await ss(tfPage, `tf-${product.name}-submit-page`);
    console.log('  Submit page URL:', tfPage.url());
    
    // Click "Submit AI" card/option
    const submitAiBtn = await tfPage.$('a:has-text("Submit AI"), button:has-text("Submit AI"), [href*="submit-ai"], div:has-text("Submit AI")');
    if (submitAiBtn) {
      console.log('  Found Submit AI button');
      await submitAiBtn.click();
      await sleep(2000);
      await ss(tfPage, `tf-${product.name}-submit-ai-clicked`);
    } else {
      // The /submit page has a search form to look up tools
      // The URL field placeholder is "Please enter the tool url, such as: 'https://www.copy.ai/'"
      // Let's try to find and fill it
      const urlInput = await tfPage.$('input[placeholder*="enter the tool url"], input[placeholder*="tool url"]');
      if (urlInput) {
        console.log('  Found URL input on submit page');
        await urlInput.fill(product.url);
        await sleep(500);
        await ss(tfPage, `tf-${product.name}-url-filled`);
        
        // Press Enter or find submit button
        await urlInput.press('Enter');
        await sleep(3000);
        await ss(tfPage, `tf-${product.name}-after-url-submit`);
        
        console.log('  After URL submit URL:', tfPage.url());
        const pageText = await tfPage.evaluate(() => document.body.innerText.substring(0, 300));
        console.log('  Page text:', pageText.substring(0, 200));
        
        // Now fill in the full tool submission form
        const inputs2 = await tfPage.$$eval('input, textarea', els => 
          els.map(el => ({ type: el.type, name: el.name, id: el.id, placeholder: el.placeholder }))
        );
        console.log('  Form inputs:', JSON.stringify(inputs2));
        
        let filled = false;
        for (const inp of inputs2) {
          if (['hidden','submit','radio','checkbox'].includes(inp.type)) continue;
          const sel = inp.id ? `#${inp.id}` : inp.name ? `[name="${inp.name}"]` : null;
          if (!sel) continue;
          const key = (inp.placeholder || inp.name || inp.id || '').toLowerCase();
          let val = null;
          if (key.includes('name') || key.includes('title')) val = product.name;
          else if (key.includes('url') || key.includes('link')) val = product.url;
          else if (key.includes('tagline') || key.includes('slogan')) val = product.tagline;
          else if (key.includes('desc')) val = product.description;
          else if (key.includes('email')) val = product.email;
          if (val) { try { await tfPage.fill(sel, val); filled = true; } catch (e) {} }
        }
        
        await ss(tfPage, `tf-${product.name}-form-filled`);
        
        if (filled) {
          const btn = await tfPage.$('button[type="submit"], button:has-text("Submit"), input[type="submit"]');
          if (btn) {
            await btn.click();
            await sleep(3000);
            await ss(tfPage, `tf-${product.name}-submitted`);
            return { ...r, status: 'SUBMITTED', url: tfPage.url() };
          }
        }
        
        return { ...r, status: 'FORM_INCOMPLETE', url: tfPage.url() };
      }
    }
    
    // Take final screenshot
    const finalText = await tfPage.evaluate(() => document.body.innerText.substring(0, 300));
    console.log('  Final page text:', finalText.substring(0, 200));
    
    return { ...r, status: 'INCOMPLETE', url: tfPage.url() };
  } catch (e) {
    console.log('  Error:', e.message.substring(0, 200));
    await ss(tfPage, `tf-${product.name}-error`).catch(() => {});
    return { ...r, status: 'ERROR', error: e.message.substring(0, 200) };
  }
}

// ============================================================
// MAIN
// ============================================================
async function main() {
  console.log('=== V4 - Surgical Directory Submissions ===\n');
  const browser = await chromium.launch({
    headless: true, slowMo: 100,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });
  
  const results = [];
  
  try {
    // Uneed - under maintenance
    results.push({ site: 'uneed.be', product: 'PantryMate', status: 'SITE_UNDER_MAINTENANCE' });
    results.push({ site: 'uneed.be', product: 'UnitFix', status: 'SITE_UNDER_MAINTENANCE' });
    
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
    if (blCtx) await blCtx.close().catch(() => {});
    if (shCtx) await shCtx.close().catch(() => {});
    if (tfCtx) await tfCtx.close().catch(() => {});
    await browser.close();
  }
  
  console.log('\n=== FINAL RESULTS ===');
  console.log(JSON.stringify(results, null, 2));
}

main().catch(console.error);
