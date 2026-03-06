const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const SCREENSHOTS_DIR = '/root/.openclaw/workspace/automation/screenshots';
fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function screenshot(page, name) {
  const p = path.join(SCREENSHOTS_DIR, name + '.png');
  await page.screenshot({ path: p, fullPage: true });
  console.log('📸', p);
}

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 }
  });

  const page = await context.newPage();
  
  // Capture ALL non-trivial network requests
  const networkLog = [];
  
  page.on('request', req => {
    const url = req.url();
    const method = req.method();
    if (!url.includes('google') && !url.includes('doubleclick') && !url.includes('.svg') && 
        !url.includes('.woff') && !url.includes('.webp') && !url.includes('.png') && 
        !url.includes('.jpg') && !url.includes('blob:') && !url.includes('analytics') &&
        !url.includes('intercom')) {
      const postData = req.postData();
      networkLog.push({ type: 'req', method, url, postData });
      if (method === 'POST' || (postData && postData.length > 0)) {
        console.log(`📤 ${method} ${url}`);
        if (postData) console.log('   POST data:', postData.slice(0, 300));
      }
    }
  });
  
  page.on('response', async res => {
    const url = res.url();
    if (!url.includes('google') && !url.includes('doubleclick') && !url.includes('.svg') && 
        !url.includes('.woff') && !url.includes('.webp') && !url.includes('.png') && 
        !url.includes('.jpg') && !url.includes('blob:') && !url.includes('analytics') &&
        !url.includes('intercom') && !url.includes('chunk') && !url.includes('static')) {
      try {
        const text = await res.text();
        networkLog.push({ type: 'res', status: res.status(), url, body: text.slice(0, 500) });
        console.log(`📥 ${res.status()} ${url}`);
        if (text && text.length > 0 && !text.startsWith('(') && !text.startsWith('RIFF')) {
          console.log('   Body:', text.slice(0, 300));
        }
      } catch(e) {}
    }
  });

  try {
    console.log('=== Intercepting HARO form submission ===\n');
    
    await page.goto('https://www.helpareporter.com/sources', { waitUntil: 'networkidle', timeout: 30000 });
    
    // Inspect the form structure more carefully
    const formDetails = await page.$$eval('form', forms => forms.map(f => ({
      action: f.action,
      method: f.method,
      id: f.id,
      class: f.className?.slice(0, 100),
      innerHTML: f.innerHTML?.slice(0, 500)
    })));
    console.log('Forms on page:', JSON.stringify(formDetails, null, 2));
    
    // Look for server action or API endpoint in the form
    const inputDetails = await page.$$eval('input, button[type="submit"]', els => els.map(e => ({
      type: e.type,
      name: e.name,
      value: e.value,
      formAction: e.formAction,
      id: e.id
    })));
    console.log('\nAll form inputs/submits:', JSON.stringify(inputDetails, null, 2));
    
    // Find the sign up button near the email input
    const signupSection = await page.$('section, div[class*="hero"], div[class*="signup"], form');
    
    // Fill email
    const emailInput = await page.$('input[name="email"]');
    if (emailInput) {
      await emailInput.fill('hello@pantrymate.net');
      console.log('\n✅ Email filled');
      
      // Find the Sign Up button
      // Try to find it within a form or near the input
      const parent = await emailInput.evaluateHandle(el => {
        // Walk up to find container
        let p = el.parentElement;
        for (let i = 0; i < 5; i++) {
          if (!p) break;
          const btn = p.querySelector('button[type="submit"], button:not([type="button"])');
          if (btn) return btn;
          p = p.parentElement;
        }
        return null;
      });
      
      if (parent) {
        const btnText = await parent.textContent().catch(() => '');
        console.log('Found adjacent button:', btnText);
        
        // Clear network log for submission
        networkLog.length = 0;
        console.log('\nClearing log, submitting form...');
        
        await parent.click();
        await sleep(5000);
        
        console.log('\n--- Network requests during submission ---');
        networkLog.forEach(item => {
          if (item.type === 'req' && (item.method === 'POST' || item.postData)) {
            console.log(`POST ${item.url}: ${item.postData}`);
          }
          if (item.type === 'res') {
            console.log(`${item.status} ${item.url}: ${item.body?.slice(0, 200)}`);
          }
        });
      }
      
      await screenshot(page, 'intercept-after-submit');
      
      // Try pressing Enter instead
      await emailInput.fill('hello@pantrymate.net');
      networkLog.length = 0;
      console.log('\nTrying Enter key submission...');
      await emailInput.press('Enter');
      await sleep(5000);
      
      console.log('\n--- Network requests during Enter submission ---');
      networkLog.forEach(item => {
        if (item.type === 'req') {
          console.log(`${item.method} ${item.url}`);
          if (item.postData) console.log('  POST:', item.postData);
        }
        if (item.type === 'res') {
          console.log(`  → ${item.status}: ${item.body?.slice(0, 200)}`);
        }
      });
      
      await screenshot(page, 'intercept-after-enter');
    }
    
    // Try the Next.js server action approach - look for __NEXT_DATA__ or form action handlers
    const nextData = await page.evaluate(() => {
      const el = document.getElementById('__NEXT_DATA__');
      if (el) return el.textContent;
      return null;
    });
    if (nextData) {
      console.log('\nNext.js data:', nextData.slice(0, 500));
    }
    
    // Check for form with action attribute containing server endpoint
    const formActions = await page.$$eval('[action]', els => els.map(e => ({
      tag: e.tagName,
      action: e.action,
      method: e.method
    })));
    console.log('\nElements with action:', formActions);

  } catch (err) {
    console.error('❌ Error:', err.message);
    await screenshot(page, 'intercept-error');
  } finally {
    await browser.close();
  }
})();
