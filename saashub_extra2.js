const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');

chromium.use(StealthPlugin());

(async () => {
  const browser = await chromium.launch({ 
    headless: true, 
    args: ['--no-sandbox']
  });
  
  const context = await browser.newContext({ 
    viewport: { width: 1280, height: 900 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    locale: 'en-US',
  });

  const page = await context.newPage();

  try {
    console.log('Loading login page with puppeteer stealth plugin...');
    await page.goto('https://www.saashub.com/login', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(8000);
    await page.screenshot({ path: '/root/.openclaw/workspace/snap_extra2.png', fullPage: false });
    
    console.log('Title:', await page.title());
    console.log('URL:', page.url());
    
    const inputs = await page.$$eval('input', els =>
      els.map(el => ({
        type: el.getAttribute('type'),
        name: el.getAttribute('name'),
        id: el.getAttribute('id'),
        placeholder: el.getAttribute('placeholder'),
      }))
    );
    console.log('Inputs:', JSON.stringify(inputs));
    
  } catch(e) {
    console.error('Error:', e.message);
  }
  await browser.close();
})();
