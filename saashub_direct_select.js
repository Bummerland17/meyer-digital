const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');

chromium.use(StealthPlugin());

const results = { submitted: [], failed: [], responses: [] };

async function suggestAlt(context, slug_alt, name) {
  const page = await context.newPage();
  
  try {
    console.log(`\n=== Suggesting ${name} ===`);
    
    // Get CSRF token and cookies from the suggest page
    await page.goto('https://www.saashub.com/suggest_alternative/pantrymate', { waitUntil: 'domcontentloaded', timeout: 20000 });
    await page.waitForTimeout(2000);
    
    const csrfToken = await page.$eval('input[name="authenticity_token"]', el => el.value).catch(() => null);
    console.log('CSRF token:', csrfToken ? csrfToken.substring(0, 20) + '...' : 'null');
    
    // Use page.evaluate to make the request within the browser context (with cookies)
    const result = await page.evaluate(async ({ token, query, slug }) => {
      // First, hit the autocomplete endpoint
      const autoFormData = new FormData();
      autoFormData.append('authenticity_token', token);
      autoFormData.append('query', query);
      
      const autoResp = await fetch('/suggest_alternative/pantrymate/autocomplete', {
        method: 'POST',
        body: autoFormData,
        credentials: 'include',
      });
      const autoHtml = await autoResp.text();
      
      // Parse the select URL from the autocomplete response
      const selectMatch = autoHtml.match(new RegExp(`href="([^"]*slug_alt=${slug}[^"]*)"`, 'i'));
      if (!selectMatch) {
        return { error: `No link found for ${slug} in autocomplete response`, autoHtml: autoHtml.substring(0, 500) };
      }
      
      const selectUrl = selectMatch[1];
      
      // Now POST to the select URL
      const selectFormData = new FormData();
      selectFormData.append('authenticity_token', token);
      
      const selectResp = await fetch(selectUrl, {
        method: 'POST',
        body: selectFormData,
        credentials: 'include',
      });
      
      const selectBody = await selectResp.text();
      
      return {
        autoUrl: '/suggest_alternative/pantrymate/autocomplete',
        selectUrl,
        selectStatus: selectResp.status,
        selectBody: selectBody.substring(0, 300),
        autoHtml: autoHtml.substring(0, 200)
      };
    }, { token: csrfToken, query: name, slug: slug_alt });
    
    console.log('Result:', JSON.stringify(result, null, 2));
    
    if (result.error) {
      console.log(`❌ ${name}: ${result.error}`);
      results.failed.push(`${name}: ${result.error}`);
    } else if (result.selectStatus === 200 || result.selectStatus === 302) {
      console.log(`✅ ${name} suggested! Status: ${result.selectStatus}`);
      results.submitted.push(name);
      
      // Clean text check
      const cleanBody = result.selectBody.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
      console.log('Response text:', cleanBody.substring(0, 200));
    } else {
      results.failed.push(`${name}: status ${result.selectStatus}`);
    }
    
  } catch(e) {
    console.error(`Error for ${name}:`, e.message);
    results.failed.push(`${name}: ${e.message}`);
  }
  
  await page.close();
}

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ 
    viewport: { width: 1440, height: 900 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });
  
  await suggestAlt(context, 'supercook', 'SuperCook');
  await suggestAlt(context, 'mealime', 'Mealime');
  await suggestAlt(context, 'yummly', 'Yummly');
  
  console.log('\n=== FINAL RESULTS ===');
  console.log(JSON.stringify(results, null, 2));
  
  await browser.close();
})();
