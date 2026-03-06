const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');

chromium.use(StealthPlugin());

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ 
    viewport: { width: 1440, height: 900 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });
  const page = await context.newPage();

  // Check PantryMate main page
  await page.goto('https://www.saashub.com/pantrymate', { waitUntil: 'domcontentloaded', timeout: 20000 });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: '/root/.openclaw/workspace/snap_pm_final.png', fullPage: false });
  
  // Get categories
  const categories = await page.$$eval('a[href*="best-"]', ls =>
    ls.map(l => l.textContent.trim()).filter(t => t.length > 3 && t.length < 50).slice(0, 20)
  );
  console.log('Current categories/tags:', categories);
  
  // Also check alternatives page
  await page.goto('https://www.saashub.com/pantrymate-alternatives', { waitUntil: 'domcontentloaded', timeout: 20000 });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: '/root/.openclaw/workspace/snap_alts_final.png', fullPage: true });
  
  const altHtml = await page.content();
  fs.writeFileSync('/root/.openclaw/workspace/alts_page.html', altHtml);
  
  // Find all product names on alternatives page
  const products = await page.$$eval('figure + div, .card-content, [class*="product"]', els =>
    els.map(el => el.textContent.trim().substring(0, 80)).filter(t => t.length > 5).slice(0, 20)
  );
  console.log('Products section:', products);
  
  // Look for any pending/suggested alternatives
  const pendingText = altHtml.match(/pend[^<]*|suggest[^<]*/gi);
  console.log('Pending/suggested mentions:', [...new Set(pendingText)].slice(0, 5));
  
  await browser.close();
})();
