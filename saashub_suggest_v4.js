const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');

chromium.use(StealthPlugin());

const results = { submitted: [], failed: [] };

async function suggestAlternative(context, competitor) {
  const page = await context.newPage();
  
  try {
    await page.goto('https://www.saashub.com/suggest_alternative/pantrymate', { waitUntil: 'domcontentloaded', timeout: 20000 });
    await page.waitForTimeout(2000);
    
    const csrfToken = await page.$eval('input[name="authenticity_token"]', el => el.value).catch(() => null);
    
    // POST to autocomplete endpoint
    const autocompleteHtml = await page.evaluate(({ token, query }) => {
      const formData = new FormData();
      formData.append('authenticity_token', token);
      formData.append('query', query);
      
      return fetch('/suggest_alternative/pantrymate/autocomplete', {
        method: 'POST',
        body: formData,
        headers: { 'Accept': 'text/html, application/xhtml+xml' }
      }).then(r => r.text());
    }, { token: csrfToken, query: competitor });
    
    console.log(`\n=== Autocomplete for ${competitor} ===`);
    console.log(autocompleteHtml.substring(0, 2000));
    
    fs.writeFileSync(`/root/.openclaw/workspace/autocomplete_${competitor.toLowerCase()}.html`, autocompleteHtml);
    
    // Parse product slugs from the response
    const slugMatches = [...autocompleteHtml.matchAll(/href="\/([a-z0-9-]+)"[^>]*>[\s\S]*?<\/a>/gi)];
    const serviceLinks = slugMatches.map(m => m[1]).filter(s => !s.includes('/') && s.length > 3);
    console.log('Found slugs:', serviceLinks.slice(0, 10));
    
    await page.close();
    return autocompleteHtml;
    
  } catch(e) {
    console.error(`Error for ${competitor}:`, e.message);
    await page.close();
    return null;
  }
}

async function submitSuggestion(context, serviceSlug) {
  const page = await context.newPage();
  
  try {
    // Navigate to suggest page to get fresh CSRF token
    await page.goto('https://www.saashub.com/suggest_alternative/pantrymate', { waitUntil: 'domcontentloaded', timeout: 20000 });
    await page.waitForTimeout(2000);
    
    const csrfToken = await page.$eval('input[name="authenticity_token"]', el => el.value).catch(() => null);
    
    // POST to the main suggest endpoint with the service slug
    const response = await page.evaluate(({ token, slug }) => {
      const formData = new FormData();
      formData.append('authenticity_token', token);
      formData.append('service_slug', slug);
      
      return fetch('/suggest_alternative/pantrymate', {
        method: 'POST',
        body: formData,
        headers: { 'Accept': 'text/html, application/xhtml+xml' },
        redirect: 'follow'
      }).then(r => ({ url: r.url, text: r.text() })).then(async r => ({ url: r.url, text: await r.text }));
    }, { token: csrfToken, slug: serviceSlug });
    
    console.log('Submit response URL:', response.url);
    console.log('Response text:', response.text ? response.text.substring(0, 500) : 'n/a');
    
    await page.close();
  } catch(e) {
    console.error(`Error submitting ${serviceSlug}:`, e.message);
    await page.close();
  }
}

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ 
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });
  
  const sc = await suggestAlternative(context, 'SuperCook');
  const ml = await suggestAlternative(context, 'Mealime');
  const ym = await suggestAlternative(context, 'Yummly');
  
  await browser.close();
})();
