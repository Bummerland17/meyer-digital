const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');

chromium.use(StealthPlugin());

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ 
    viewport: { width: 1280, height: 900 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });
  const page = await context.newPage();

  try {
    // Try the product changes page
    console.log('Loading product changes page...');
    await page.goto('https://www.saashub.com/product-changes/pantrymate/new', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(5000);
    
    const title = await page.title();
    console.log('Title:', title);
    console.log('URL:', page.url());
    
    if (!title.includes('Just a moment')) {
      await page.screenshot({ path: '/root/.openclaw/workspace/snap_edit.png', fullPage: true });
      const html = await page.content();
      fs.writeFileSync('/root/.openclaw/workspace/edit_page.html', html);
      console.log('Edit page saved');
      
      const inputs = await page.$$eval('input, select, textarea', els =>
        els.map(el => ({
          tag: el.tagName,
          type: el.getAttribute('type'),
          name: el.getAttribute('name'),
          id: el.getAttribute('id'),
          placeholder: el.getAttribute('placeholder'),
        }))
      );
      console.log('Inputs:', JSON.stringify(inputs));
    }
    
    // Also check verify page
    await page.goto('https://www.saashub.com/verify/pantrymate', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(5000);
    console.log('\nVerify page title:', await page.title());
    console.log('Verify URL:', page.url());
    await page.screenshot({ path: '/root/.openclaw/workspace/snap_verify.png', fullPage: false });
    
  } catch(e) {
    console.error('Error:', e.message);
  }
  await browser.close();
})();
