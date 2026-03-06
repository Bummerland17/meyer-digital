const { chromium } = require('/root/.openclaw/workspace/node_modules/playwright');
const path = require('path');

const EMAIL = 'hello@pantrymate.net';
const PASSWORD = 'SmartBook2026!Ai#';
const NAME = 'Wolfgang Meyer';
const SCREENSHOT_DIR = '/root/.openclaw/workspace/assets/screenshots';

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function run() {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();

  try {
    console.log('Navigating to Bland.ai signup...');
    await page.goto('https://app.bland.ai/sign-up', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await sleep(4000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'bland-01-loaded.png') });
    console.log('Title:', await page.title());
    console.log('URL:', page.url());

    const inputs = await page.$$eval('input', els => els.map(e => ({
      type: e.type, name: e.name, placeholder: e.placeholder, id: e.id
    })));
    console.log('Inputs:', JSON.stringify(inputs, null, 2));

    const buttons = await page.$$eval('button', els => els.map(e => ({
      type: e.type, text: e.textContent.trim().slice(0, 60), disabled: e.disabled
    })));
    console.log('Buttons:', JSON.stringify(buttons, null, 2));

    const bodyText = (await page.textContent('body')).slice(0, 3000);
    console.log('Body:', bodyText);

  } catch (err) {
    console.error('Error:', err.message);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'bland-error.png') }).catch(() => {});
  } finally {
    await browser.close();
  }
}

run().catch(console.error);
