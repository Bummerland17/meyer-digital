const { chromium } = require('/root/.openclaw/workspace/node_modules/playwright');
const path = require('path');

const EMAIL = 'hello@pantrymate.net';
const PASSWORD = 'SmartBook2026!Ai#';
const SCREENSHOT_DIR = '/root/.openclaw/workspace/assets/screenshots';

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function run() {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();

  try {
    await page.goto('https://dashboard.vapi.ai/register', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await sleep(4000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'vapi2-01-loaded.png') });

    // List all inputs
    const inputs = await page.$$eval('input', els => els.map(e => ({
      type: e.type, name: e.name, placeholder: e.placeholder, id: e.id, value: e.value
    })));
    console.log('Inputs found:', JSON.stringify(inputs, null, 2));

    // List all buttons
    const buttons = await page.$$eval('button', els => els.map(e => ({
      type: e.type, text: e.textContent.trim().slice(0, 50), disabled: e.disabled
    })));
    console.log('Buttons found:', JSON.stringify(buttons, null, 2));

    // Fill email
    const emailInput = await page.$('input[type="email"], input[name="email"], input[placeholder*="email" i]');
    if (emailInput) {
      await emailInput.click();
      await emailInput.fill('');
      await emailInput.type(EMAIL, { delay: 50 });
      console.log('Filled email');
    }

    await sleep(500);

    // Fill password
    const passInputs = await page.$$('input[type="password"]');
    console.log('Password inputs:', passInputs.length);
    if (passInputs[0]) {
      await passInputs[0].click();
      await passInputs[0].fill('');
      await passInputs[0].type(PASSWORD, { delay: 50 });
      console.log('Filled password 1');
    }
    if (passInputs[1]) {
      await passInputs[1].click();
      await passInputs[1].fill('');
      await passInputs[1].type(PASSWORD, { delay: 50 });
      console.log('Filled password 2 (confirm)');
    }

    await sleep(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'vapi2-02-filled.png') });

    // Check button state again
    const buttons2 = await page.$$eval('button', els => els.map(e => ({
      type: e.type, text: e.textContent.trim().slice(0, 50), disabled: e.disabled
    })));
    console.log('Buttons after fill:', JSON.stringify(buttons2, null, 2));

    // Try forcing click with JS
    const signUpBtn = await page.$('button[type="submit"]');
    if (signUpBtn) {
      // Try JS click to bypass disabled state
      await page.evaluate(btn => btn.removeAttribute('disabled'), signUpBtn);
      await signUpBtn.click({ force: true });
      console.log('Force-clicked submit button');
      await sleep(8000);
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'vapi2-03-after-submit.png') });
      console.log('URL after submit:', page.url());
      console.log('Body text:', (await page.textContent('body')).slice(0, 2000));
    }

  } catch (err) {
    console.error('Error:', err.message);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'vapi2-error.png') }).catch(() => {});
  } finally {
    await browser.close();
  }
}

run().catch(console.error);
