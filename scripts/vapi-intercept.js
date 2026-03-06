const { chromium } = require('/root/.openclaw/workspace/node_modules/playwright');
const path = require('path');

const EMAIL = 'hello@pantrymate.net';
const SCREENSHOT_DIR = '/root/.openclaw/workspace/assets/screenshots';

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function run() {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();

  // Intercept network requests
  const apiCalls = [];
  page.on('request', req => {
    const url = req.url();
    if (!url.includes('linkedin') && !url.includes('google') && !url.includes('analytics')) {
      apiCalls.push({ method: req.method(), url: url, headers: req.headers() });
    }
  });
  page.on('response', async res => {
    const url = res.url();
    if (url.includes('vapi') && !url.includes('chunk') && !url.includes('.js') && !url.includes('.css')) {
      const status = res.status();
      let body = '';
      try { body = await res.text(); } catch(e) {}
      console.log(`RESPONSE ${status} ${url}: ${body.slice(0, 200)}`);
    }
  });

  try {
    await page.goto('https://dashboard.vapi.ai/register', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await sleep(3000);

    // Check for Clerk or other auth provider
    console.log('Checking auth provider...');
    const scripts = await page.$$eval('script[src]', els => els.map(e => e.src));
    const authScripts = scripts.filter(s => s.includes('clerk') || s.includes('auth0') || s.includes('supabase') || s.includes('firebase'));
    console.log('Auth scripts:', authScripts);

    // Check localStorage/cookies for clues
    const lsKeys = await page.evaluate(() => Object.keys(localStorage));
    console.log('LocalStorage keys:', lsKeys);

    // Check what host the forms post to
    const forms = await page.$$eval('form', els => els.map(f => ({action: f.action, method: f.method})));
    console.log('Forms:', forms);

    await sleep(2000);

    // Output unique API calls 
    const uniqueUrls = [...new Set(apiCalls.map(c => c.url))];
    console.log('\nNetwork calls (unique):');
    uniqueUrls.forEach(u => console.log(' ', u));

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
}

run().catch(console.error);
