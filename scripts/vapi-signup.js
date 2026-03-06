const { chromium } = require('/root/.openclaw/workspace/node_modules/playwright');
const fs = require('fs');
const path = require('path');

const EMAIL = 'hello@pantrymate.net';
const PASSWORD = 'SmartBook2026!';
const NAME = 'Wolfgang Meyer';
const SCREENSHOT_DIR = '/root/.openclaw/workspace/assets/screenshots';

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function tryVapiSignup() {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();

  try {
    console.log('Navigating to Vapi signup...');
    await page.goto('https://dashboard.vapi.ai/sign-up', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await sleep(5000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'vapi-01-signup.png') });
    console.log('Page title:', await page.title());
    console.log('URL:', page.url());
    
    const bodyText = (await page.textContent('body').catch(() => '')).slice(0, 2000);
    console.log('Body text:', bodyText);

    // Check for email input
    const emailInput = await page.$('input[type="email"], input[name="email"], input[placeholder*="email" i]');
    if (!emailInput) {
      console.log('No email input found on first try, waiting more...');
      await sleep(3000);
      const emailInput2 = await page.$('input[type="email"], input[name="email"], input[placeholder*="email" i]');
      if (!emailInput2) {
        console.log('Still no email input. Inputs found:', await page.$$eval('input', els => els.map(e => ({type: e.type, name: e.name, placeholder: e.placeholder}))));
      }
    } else {
      console.log('Found email input, filling form...');
      await emailInput.fill(EMAIL);

      const nameInput = await page.$('input[name="name"], input[placeholder*="name" i], input[placeholder*="full" i]');
      if (nameInput) {
        await nameInput.fill(NAME);
        console.log('Filled name field');
      }

      const passInput = await page.$('input[type="password"]');
      if (passInput) {
        await passInput.fill(PASSWORD);
        console.log('Filled password field');
      }

      await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'vapi-02-filled.png') });

      const submitBtn = await page.$('button[type="submit"], button:has-text("Sign up"), button:has-text("Create account"), button:has-text("Continue")');
      if (submitBtn) {
        await submitBtn.click();
        console.log('Clicked submit');
        await sleep(8000);
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'vapi-03-after-submit.png') });
        console.log('After submit URL:', page.url());
      }
    }

  } catch (err) {
    console.error('Vapi signup error:', err.message);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'vapi-error.png') }).catch(() => {});
  } finally {
    await browser.close();
  }
}

tryVapiSignup().catch(console.error);
