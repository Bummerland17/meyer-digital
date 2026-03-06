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
    // Check the verify page
    console.log('Loading verify page...');
    await page.goto('https://www.saashub.com/verify/pantrymate', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(4000);
    
    const title = await page.title();
    console.log('Title:', title);
    console.log('URL:', page.url());
    
    await page.screenshot({ path: '/root/.openclaw/workspace/snap_verify.png', fullPage: true });
    const html = await page.content();
    fs.writeFileSync('/root/.openclaw/workspace/verify_page.html', html);
    
    const inputs = await page.$$eval('input, select, textarea, a[href*="sign_in"], a[href*="login"]', els =>
      els.map(el => ({
        tag: el.tagName,
        type: el.getAttribute('type'),
        name: el.getAttribute('name'),
        href: el.getAttribute('href'),
        text: el.textContent ? el.textContent.trim().substring(0,50) : '',
        id: el.getAttribute('id'),
        placeholder: el.getAttribute('placeholder'),
      }))
    );
    console.log('Elements:', JSON.stringify(inputs, null, 2));
    
    // Try to look at alternative products that are well-filled
    // e.g., a competitor's page
    await page.goto('https://www.saashub.com/supercook', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    console.log('\nSuperCook URL:', page.url());
    
    const scLinks = await page.$$eval('a', ls =>
      ls.map(l => ({ text: l.textContent.trim().substring(0,60), href: l.href }))
        .filter(l => /pricing|edit|claim|verify|plan|cost/i.test(l.text + l.href))
        .slice(0, 15)
    );
    console.log('SuperCook relevant links:', JSON.stringify(scLinks));
    
  } catch(e) {
    console.error('Error:', e.message);
  }
  await browser.close();
})();
