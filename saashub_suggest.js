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
    // Check suggest alternative page
    console.log('Loading suggest alternative page...');
    await page.goto('https://www.saashub.com/suggest_alternative/pantrymate', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(4000);
    
    console.log('Title:', await page.title());
    console.log('URL:', page.url());
    
    await page.screenshot({ path: '/root/.openclaw/workspace/snap_suggest.png', fullPage: true });
    
    const inputs = await page.$$eval('input, select, textarea', els =>
      els.map(el => ({
        tag: el.tagName,
        type: el.getAttribute('type'),
        name: el.getAttribute('name'),
        id: el.getAttribute('id'),
        placeholder: el.getAttribute('placeholder'),
        value: el.value ? el.value.substring(0,50) : ''
      }))
    );
    console.log('Inputs:', JSON.stringify(inputs, null, 2));
    
    // Also check if there's a pricing submission page
    const pricingUrls = [
      'https://www.saashub.com/pantrymate/plans/new',
      'https://www.saashub.com/products/pantrymate/pricing',
      'https://www.saashub.com/pantrymate/edit/pricing',
      'https://www.saashub.com/pantrymate/manage',
      'https://www.saashub.com/pantrymate/manage/pricing',
    ];
    
    for (const url of pricingUrls) {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });
      await page.waitForTimeout(2000);
      const t = await page.title();
      const u = page.url();
      if (!t.includes('Just a moment') && !t.includes('404') && u !== 'https://www.saashub.com/' && !u.includes('alternatives')) {
        console.log(`\nFound accessible pricing URL: ${u}`);
        console.log('Title:', t);
        const html = await page.content();
        fs.writeFileSync('/root/.openclaw/workspace/pricing_page.html', html);
      } else {
        console.log(`URL ${url} → ${u} (${t.substring(0,50)})`);
      }
    }
    
  } catch(e) {
    console.error('Error:', e.message);
  }
  await browser.close();
})();
