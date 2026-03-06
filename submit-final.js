/**
 * Final completion:
 * 1. Fix PantryMate verification email on SaaSHub (fill email before clicking)
 * 2. Verify UnitFix listing exists
 */

const { chromium } = require('/root/.openclaw/workspace/node_modules/playwright');
const path = require('path');

const SCREENSHOTS_DIR = '/root/.openclaw/workspace/assets/screenshots';
const GOOGLE_EMAIL = 'olcowboy21@gmail.com';
const GOOGLE_PASSWORD = 'Bummerland20';
const PRODUCT_EMAIL = 'hello@pantrymate.net';

let sc = 0;
async function ss(page, label) {
  sc++;
  const fname = `fin-${String(sc).padStart(3,'0')}-${label.replace(/[^a-z0-9]/gi,'-').substring(0,60)}.png`;
  const fpath = path.join(SCREENSHOTS_DIR, fname);
  try { await page.screenshot({ path: fpath, fullPage: false }); } catch (e) {}
  console.log(`📸 ${fname}`);
  return fpath;
}
async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function main() {
  const browser = await chromium.launch({
    headless: true, slowMo: 80,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });
  
  const ctx = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });
  const page = await ctx.newPage();
  
  try {
    // Login to SaaSHub
    await page.goto('https://www.saashub.com/login', { timeout: 30000, waitUntil: 'domcontentloaded' });
    await sleep(5000);
    await ss(page, 'sh-login');
    
    const loginText = await page.evaluate(() => document.body.innerText.substring(0, 200));
    console.log('Login page:', loginText.substring(0, 100));
    
    if (!loginText.includes('security verification') && !loginText.includes('Cloudflare')) {
      const emailInput = await page.$('input[type="email"]');
      const pwdInput = await page.$('input[type="password"]');
      if (emailInput && pwdInput) {
        await emailInput.fill(GOOGLE_EMAIL);
        await pwdInput.fill(GOOGLE_PASSWORD);
        const btn = await page.$('input[type="submit"], button[type="submit"]');
        if (btn) await btn.click();
        await sleep(3000);
        await ss(page, 'sh-after-login');
        console.log('After login URL:', page.url());
      }
    }
    
    // ---- Fix PantryMate verification ----
    console.log('\n--- Fix PantryMate verification email ---');
    await page.goto('https://www.saashub.com/verify/pantrymate', { timeout: 30000, waitUntil: 'domcontentloaded' });
    await sleep(3000);
    await ss(page, 'sh-pm-verify-page');
    
    const verifyText = await page.evaluate(() => document.body.innerText.substring(0, 400));
    console.log('Verify text:', verifyText.substring(0, 200));
    
    // Find email input on verify page
    const emailInputs = await page.$$eval('input', els => 
      els.map(el => ({ type: el.type, name: el.name, id: el.id, placeholder: el.placeholder }))
    );
    console.log('Inputs:', JSON.stringify(emailInputs));
    
    // Fill in the verification email
    const verifyEmailInput = await page.$('input[type="email"], input[type="text"], input[name*="email"], input[placeholder*="email" i]');
    if (verifyEmailInput) {
      await verifyEmailInput.fill(PRODUCT_EMAIL);
      console.log('Filled email:', PRODUCT_EMAIL);
      await sleep(300);
      
      const sendBtn = await page.$('button:has-text("Send"), input[type="submit"], button[type="submit"]');
      if (sendBtn) {
        const btnText = await sendBtn.evaluate(el => el.textContent?.trim() || el.value);
        console.log('Sending with button:', btnText);
        await sendBtn.click();
        await sleep(3000);
        await ss(page, 'sh-pm-verify-sent');
        console.log('After verify send URL:', page.url());
        
        const afterText = await page.evaluate(() => document.body.innerText.substring(0, 300));
        console.log('After send text:', afterText.substring(0, 200));
      }
    } else {
      console.log('No email input found');
      
      // Check forms in detail
      const forms = await page.evaluate(() =>
        Array.from(document.querySelectorAll('form')).map(f => ({
          action: f.action,
          html: f.innerHTML.substring(0, 300)
        }))
      );
      console.log('Forms:', JSON.stringify(forms));
    }
    
    // ---- Verify UnitFix listing ----
    console.log('\n--- Verify UnitFix listing ---');
    await page.goto('https://www.saashub.com/unitfix', { timeout: 30000, waitUntil: 'domcontentloaded' });
    await sleep(3000);
    await ss(page, 'sh-uf-listing');
    
    const ufText = await page.evaluate(() => document.body.innerText.substring(0, 400));
    console.log('UnitFix listing text:', ufText.substring(0, 200));
    
    // ---- Confirm PantryMate listing ----
    console.log('\n--- Confirm PantryMate listing ---');
    await page.goto('https://www.saashub.com/pantrymate', { timeout: 30000, waitUntil: 'domcontentloaded' });
    await sleep(3000);
    await ss(page, 'sh-pm-listing');
    
    const pmText = await page.evaluate(() => document.body.innerText.substring(0, 400));
    console.log('PantryMate listing text:', pmText.substring(0, 200));
    
  } finally {
    await ctx.close();
    await browser.close();
  }
}

main().catch(console.error);
