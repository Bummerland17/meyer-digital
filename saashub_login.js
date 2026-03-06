const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ 
    viewport: { width: 1280, height: 900 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();

  try {
    console.log('Loading login page...');
    await page.goto('https://www.saashub.com/login', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    await page.screenshot({ path: '/root/.openclaw/workspace/snap_login.png', fullPage: true });
    console.log('Login URL:', page.url());
    
    // Get inputs
    const inputs = await page.$$eval('input, button', els =>
      els.map(el => ({
        tag: el.tagName,
        type: el.getAttribute('type'),
        name: el.getAttribute('name'),
        id: el.getAttribute('id'),
        placeholder: el.getAttribute('placeholder'),
      }))
    );
    console.log('Inputs:', JSON.stringify(inputs, null, 2));
    
    const html = await page.content();
    fs.writeFileSync('/root/.openclaw/workspace/login_page2.html', html);
    
  } catch(e) {
    console.error('Error:', e.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/snap_login_error.png' });
  }
  await browser.close();
})();
