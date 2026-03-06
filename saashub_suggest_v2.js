const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');

chromium.use(StealthPlugin());

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ 
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });
  const page = await context.newPage();
  
  // Intercept network requests to see the autocomplete response
  const requestLog = [];
  page.on('response', async response => {
    const url = response.url();
    if (url.includes('autocomplete') || url.includes('suggest')) {
      try {
        const body = await response.text();
        requestLog.push({ url, body: body.substring(0, 500) });
        console.log('Response from:', url);
        console.log('Body:', body.substring(0, 500));
      } catch(e) {}
    }
  });

  await page.goto('https://www.saashub.com/suggest_alternative/pantrymate', { waitUntil: 'domcontentloaded', timeout: 20000 });
  await page.waitForTimeout(2000);
  
  const queryInput = await page.$('input[name="query"]');
  if (!queryInput) {
    console.log('No input found');
    await browser.close();
    return;
  }
  
  // Type and wait for network response
  await queryInput.click();
  await queryInput.type('SuperCook', { delay: 150 });
  await page.waitForTimeout(3000);
  
  await page.screenshot({ path: '/root/.openclaw/workspace/snap_suggest_v2.png', fullPage: true });
  
  // Check for any elements that appeared
  const allElements = await page.$$eval('*', els =>
    els.map(el => ({
      tag: el.tagName,
      class: el.className,
      id: el.id,
      text: el.textContent.trim().substring(0, 80),
      visible: el.offsetParent !== null || el.getBoundingClientRect().width > 0
    })).filter(el => el.text.toLowerCase().includes('supercook') || el.text.toLowerCase().includes('super cook'))
  );
  console.log('Elements with supercook:', JSON.stringify(allElements));
  
  // Try looking at shadow DOM or frames
  const frames = page.frames();
  console.log('Frames count:', frames.length);
  
  // Check the page source for the autocomplete trigger mechanism
  const html = await page.content();
  const autocompleteSection = html.match(/autocomplete[\s\S]{0,500}/i);
  if (autocompleteSection) {
    console.log('Autocomplete code:', autocompleteSection[0].substring(0, 500));
  }
  
  // Look for Stimulus/Turbo controllers
  const controllers = await page.$$eval('[data-controller]', els =>
    els.map(el => ({ controller: el.getAttribute('data-controller'), tag: el.tagName, class: el.className }))
  );
  console.log('Controllers:', JSON.stringify(controllers));
  
  console.log('Network requests:', JSON.stringify(requestLog));
  
  await browser.close();
})();
