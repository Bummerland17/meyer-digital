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
    // Try main page first
    console.log('Loading main page...');
    await page.goto('https://www.saashub.com/', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2000);
    await page.screenshot({ path: '/root/.openclaw/workspace/snap_main.png', fullPage: false });
    console.log('Main page URL:', page.url());
    
    // Find login links
    const loginLinks = await page.$$eval('a', links =>
      links.map(l => ({ text: l.textContent.trim(), href: l.href }))
           .filter(l => /sign.?in|log.?in|account|login/i.test(l.text + l.href))
    );
    console.log('Login links:', JSON.stringify(loginLinks.slice(0, 10)));
    
    // Try the PantryMate page
    console.log('\nLoading PantryMate page...');
    await page.goto('https://www.saashub.com/pantrymate', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2000);
    await page.screenshot({ path: '/root/.openclaw/workspace/snap_pantrymate.png', fullPage: false });
    console.log('PantryMate URL:', page.url());
    
    const pm_links = await page.$$eval('a', links =>
      links.map(l => ({ text: l.textContent.trim(), href: l.href }))
           .filter(l => /edit|claim|manage|update|submit|login|sign/i.test(l.text + l.href))
           .slice(0, 15)
    );
    console.log('PantryMate page links:', JSON.stringify(pm_links));
    
  } catch(e) {
    console.error('Error:', e.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/snap_error.png' });
  }
  await browser.close();
})();
