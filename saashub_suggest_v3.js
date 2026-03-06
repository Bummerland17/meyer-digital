const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');

chromium.use(StealthPlugin());

const results = { submitted: [], failed: [], skipped: [] };

async function getAuthToken(page, url) {
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 20000 });
  await page.waitForTimeout(2000);
  const token = await page.$eval('input[name="authenticity_token"]', el => el.value).catch(() => null);
  return token;
}

async function suggestViaPost(context, competitor) {
  const page = await context.newPage();
  
  try {
    // Get the suggest page and its authenticity token
    await page.goto('https://www.saashub.com/suggest_alternative/pantrymate', { waitUntil: 'domcontentloaded', timeout: 20000 });
    await page.waitForTimeout(2000);
    
    // Get CSRF token from page
    const csrfToken = await page.$eval('input[name="authenticity_token"]', el => el.value).catch(() => null);
    console.log(`CSRF token for ${competitor}:`, csrfToken ? csrfToken.substring(0, 20) + '...' : 'not found');
    
    // Type in search
    await page.waitForSelector('input[name="query"]', { timeout: 5000 });
    const input = await page.$('input[name="query"]');
    await input.type(competitor, { delay: 100 });
    
    // Wait for turbo frame to load
    await page.waitForTimeout(3000);
    
    // Look for the turbo-frame response
    const frameContent = await page.$eval('turbo-frame', el => el.innerHTML).catch(() => null);
    if (frameContent) {
      console.log(`Turbo frame for ${competitor}:`, frameContent.substring(0, 500));
    }
    
    // Find the service autocomplete frame
    const autocompleteFrame = await page.$('[id*="service_autocomplete"], turbo-frame#service_autocomplete').catch(() => null);
    
    // Check the full page content for any results
    const pageContent = await page.content();
    const supercookMatch = pageContent.match(new RegExp(`href="[^"]*${competitor.toLowerCase()}[^"]*"`, 'gi'));
    console.log(`Links matching ${competitor}:`, supercookMatch);
    
    // Also check for data attributes or hidden form fields
    const dataAttrs = await page.$$eval('[data-service-id], [data-id], [data-slug]', els =>
      els.map(el => ({
        'data-service-id': el.getAttribute('data-service-id'),
        'data-id': el.getAttribute('data-id'),
        'data-slug': el.getAttribute('data-slug'),
        text: el.textContent.trim().substring(0, 50)
      }))
    );
    console.log(`Data attrs:`, JSON.stringify(dataAttrs));
    
    // Try submitting the autocomplete form directly via fetch
    const autocompleteResponse = await page.evaluate(async (csrfToken, query) => {
      const formData = new FormData();
      formData.append('authenticity_token', csrfToken);
      formData.append('query', query);
      
      const resp = await fetch('/suggest_alternative/pantrymate/autocomplete', {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRF-Token': csrfToken,
          'Accept': 'text/html, application/xhtml+xml',
        }
      });
      return await resp.text();
    }, csrfToken, competitor);
    
    console.log(`Autocomplete response for ${competitor}:`, autocompleteResponse.substring(0, 1000));
    
    // Parse the response for service URLs/IDs
    const serviceLinks = autocompleteResponse.match(/href="\/([^"]+)"/gi);
    console.log('Service links in response:', serviceLinks);
    
    const slugMatch = autocompleteResponse.match(/href="\/([a-z0-9-]+)"[^>]*>[^<]*<\/a>/gi);
    console.log('Slug matches:', slugMatch ? slugMatch.slice(0, 5) : 'none');
    
    // Look for the actual service link to click
    const linkToClick = autocompleteResponse.match(/href="(\/[a-z0-9-]+)"[^>]*>\s*(?:<[^>]+>\s*)*([^\n<]{5,})/i);
    console.log('First service:', linkToClick);
    
    await page.close();
    
  } catch(e) {
    console.error(`Error for ${competitor}:`, e.message);
    results.failed.push(competitor);
    await page.close();
  }
}

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ 
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });
  
  await suggestViaPost(context, 'SuperCook');
  
  await browser.close();
})();
