const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();

  try {
    await page.goto('https://www.saashub.com/users/sign_in', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    await page.screenshot({ path: '/root/.openclaw/workspace/snap_login.png', fullPage: true });
    
    const html = await page.content();
    fs.writeFileSync('/root/.openclaw/workspace/login_page.html', html);
    
    // Get all inputs
    const inputs = await page.$$eval('input, button, [type=submit]', els =>
      els.map(el => ({
        tag: el.tagName,
        type: el.getAttribute('type'),
        name: el.getAttribute('name'),
        id: el.getAttribute('id'),
        placeholder: el.getAttribute('placeholder'),
        class: el.getAttribute('class') ? el.getAttribute('class').substring(0,80) : ''
      }))
    );
    console.log('INPUTS:', JSON.stringify(inputs, null, 2));
    console.log('URL:', page.url());
    
  } catch(e) {
    console.error('Error:', e.message);
  }
  await browser.close();
})();
