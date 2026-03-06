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
    // Try to access the PantryMate page directly - may work without auth
    console.log('Loading PantryMate page...');
    await page.goto('https://www.saashub.com/pantrymate', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(5000);
    
    const title = await page.title();
    console.log('Title:', title);
    console.log('URL:', page.url());
    
    if (!title.includes('Just a moment')) {
      await page.screenshot({ path: '/root/.openclaw/workspace/snap_pm_full.png', fullPage: true });
      const html = await page.content();
      fs.writeFileSync('/root/.openclaw/workspace/pm_page.html', html);
      
      // Get all links
      const links = await page.$$eval('a', ls => ls.map(l => ({ text: l.textContent.trim().substring(0,60), href: l.href })));
      console.log('All links:', JSON.stringify(links.filter(l => l.href.includes('saashub')).slice(0,30)));
    }
    
    // Also try the submit page to understand the structure
    await page.goto('https://www.saashub.com/submit', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(5000);
    console.log('Submit page title:', await page.title());
    console.log('Submit URL:', page.url());
    
  } catch(e) {
    console.error('Error:', e.message);
  }
  await browser.close();
})();
