const { chromium } = require('playwright-extra');
const StealthPlugin = require('playwright-extra-plugin-stealth');
const fs = require('fs');

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
    console.log('Loading login page with stealth plugin...');
    await page.goto('https://www.saashub.com/login', { waitUntil: 'domcontentloaded', timeout: 30000 });
    
    // Wait longer for Cloudflare to resolve
    await page.waitForTimeout(8000);
    await page.screenshot({ path: '/root/.openclaw/workspace/snap_extra.png', fullPage: false });
    
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
    
    // If we got past CF, try to login
    const emailInput = await page.$('input[type="email"], input[name*="email"], input[placeholder*="email" i]');
    if (emailInput) {
      console.log('Found email input! Attempting login...');
      await emailInput.fill('olcowboy21@gmail.com');
      const passInput = await page.$('input[type="password"]');
      if (passInput) {
        await passInput.fill('Bummerland20');
        await page.screenshot({ path: '/root/.openclaw/workspace/snap_filled.png' });
        await page.keyboard.press('Enter');
        await page.waitForTimeout(5000);
        await page.screenshot({ path: '/root/.openclaw/workspace/snap_after_login.png' });
        console.log('After login URL:', page.url());
      }
    }
    
  } catch(e) {
    console.error('Error:', e.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/snap_extra_error.png' }).catch(() => {});
  }
  await browser.close();
})();
