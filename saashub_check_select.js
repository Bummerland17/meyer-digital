const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');

chromium.use(StealthPlugin());

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ 
    viewport: { width: 1440, height: 900 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });
  const page = await context.newPage();

  await page.goto('https://www.saashub.com/suggest_alternative/pantrymate', { waitUntil: 'domcontentloaded', timeout: 20000 });
  await page.waitForTimeout(2000);
  
  const csrfToken = await page.$eval('input[name="authenticity_token"]', el => el.value).catch(() => null);
  
  // Get the full response body from the select endpoint
  const response = await page.evaluate(({ token }) => {
    const formData = new FormData();
    formData.append('authenticity_token', token);
    
    return fetch('/suggest_alternative/pantrymate/select?slug_alt=supercook', {
      method: 'POST',
      body: formData,
      headers: { 'Accept': 'text/html, application/xhtml+xml, */*' }
    }).then(r => r.text());
  }, { token: csrfToken });
  
  console.log('Select response for SuperCook:');
  console.log(response.substring(0, 1000));
  console.log('\n---\n');
  
  // Check the text more carefully
  const cleanText = response.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
  console.log('Clean text:', cleanText.substring(0, 500));
  
  await browser.close();
})();
