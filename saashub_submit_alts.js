const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');

chromium.use(StealthPlugin());

const results = { submitted: [], failed: [] };

async function submitAlternative(context, slug_alt, name) {
  const page = await context.newPage();
  
  try {
    // Get fresh CSRF token from the suggest page
    await page.goto('https://www.saashub.com/suggest_alternative/pantrymate', { waitUntil: 'domcontentloaded', timeout: 20000 });
    await page.waitForTimeout(2000);
    
    const csrfToken = await page.$eval('input[name="authenticity_token"]', el => el.value).catch(() => null);
    console.log(`\nSubmitting ${name} (slug: ${slug_alt})...`);
    
    // POST to the select endpoint  
    const response = await page.evaluate(({ token, slug }) => {
      const formData = new FormData();
      formData.append('authenticity_token', token);
      
      return fetch(`/suggest_alternative/pantrymate/select?slug_alt=${slug}`, {
        method: 'POST',
        body: formData,
        headers: { 'Accept': 'text/html, application/xhtml+xml, */*' }
      }).then(r => ({ status: r.status, url: r.url }));
    }, { token: csrfToken, slug: slug_alt });
    
    console.log(`Response for ${name}:`, response);
    
    if (response.status === 200 || response.status === 302 || response.status === 201) {
      results.submitted.push(name);
      console.log(`✅ ${name} submitted as alternative`);
    } else {
      console.log(`⚠️ Unexpected status ${response.status} for ${name}`);
      results.failed.push(`${name}: status ${response.status}`);
    }
    
    // Also try navigating to the URL directly to confirm
    await page.goto(`https://www.saashub.com/suggest_alternative/pantrymate/select?slug_alt=${slug_alt}`, { waitUntil: 'domcontentloaded', timeout: 20000 });
    await page.waitForTimeout(2000);
    
    const url = page.url();
    const title = await page.title();
    const bodyText = await page.$eval('body', el => el.textContent.replace(/\s+/g, ' ').substring(0, 300));
    console.log(`Navigation result for ${name}:`, url, title);
    console.log('Body:', bodyText.substring(0, 200));
    
    await page.screenshot({ path: `/root/.openclaw/workspace/snap_alt_${slug_alt}.png` });
    
  } catch(e) {
    console.error(`Error for ${name}:`, e.message);
    results.failed.push(`${name}: ${e.message}`);
  }
  
  await page.close();
}

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ 
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });
  
  await submitAlternative(context, 'supercook', 'SuperCook');
  await submitAlternative(context, 'mealime', 'Mealime');
  await submitAlternative(context, 'yummly', 'Yummly');
  
  console.log('\n=== FINAL RESULTS ===');
  console.log(JSON.stringify(results, null, 2));
  fs.writeFileSync('/root/.openclaw/workspace/alt_results.json', JSON.stringify(results, null, 2));
  
  await browser.close();
})();
