const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');

chromium.use(StealthPlugin());

const results = { submitted: [], failed: [] };

async function suggestAlt(context, slug_alt, name) {
  const page = await context.newPage();
  
  const responses = [];
  page.on('response', async resp => {
    const url = resp.url();
    if (url.includes('suggest') || url.includes('select') || url.includes('alternative')) {
      try {
        const body = await resp.text();
        if (body.length > 0) {
          responses.push({ url, status: resp.status(), body: body.substring(0, 200) });
        }
      } catch(e) {}
    }
  });
  
  try {
    console.log(`\n=== Suggesting ${name} (${slug_alt}) ===`);
    
    // Navigate directly to suggest page  
    await page.goto('https://www.saashub.com/suggest_alternative/pantrymate', { waitUntil: 'domcontentloaded', timeout: 20000 });
    await page.waitForTimeout(3000);
    
    await page.screenshot({ path: `/root/.openclaw/workspace/snap_sug_direct_${slug_alt}.png` });
    
    // Find the query input
    await page.waitForSelector('input[name="query"]', { timeout: 10000 });
    const queryInput = await page.$('input[name="query"]');
    
    if (!queryInput) {
      console.log('No input found');
      await page.close();
      return;
    }
    
    console.log('Found input, typing...');
    await queryInput.click();
    await queryInput.type(name, { delay: 150 });
    
    // Wait for the autocomplete turbo-frame to update
    // The form uses data-action="service-autocomplete#search" likely
    // Let's wait for network response
    await page.waitForTimeout(4000);
    
    await page.screenshot({ path: `/root/.openclaw/workspace/snap_sug_typed_${slug_alt}.png`, fullPage: true });
    
    // Log the full page HTML at this point
    const html = await page.content();
    const matchingLink = html.match(new RegExp(`href="[^"]*${slug_alt}[^"]*"`, 'i'));
    console.log(`Link with ${slug_alt} in HTML:`, matchingLink);
    
    // Check for turbo-frame
    const turboFrameId = await page.$eval('turbo-frame[id="service_autocomplete"]', el => ({
      id: el.id,
      html: el.innerHTML.substring(0, 500)
    })).catch(() => null);
    
    if (turboFrameId) {
      console.log('Turbo frame found:', JSON.stringify(turboFrameId));
    } else {
      console.log('No turbo frame service_autocomplete found');
      // Check all turbo-frames
      const frames = await page.$$eval('turbo-frame', els => els.map(el => ({ id: el.id, html: el.innerHTML.substring(0, 200) })));
      console.log('All turbo frames:', JSON.stringify(frames));
    }
    
    // Try to find and use the link in the DOM
    const matchEl = await page.$(`a[href*="slug_alt=${slug_alt}"]`);
    if (matchEl) {
      const href = await matchEl.getAttribute('href');
      const text = await matchEl.textContent();
      console.log(`Found: ${text} → ${href}`);
      await matchEl.click();
      await page.waitForTimeout(3000);
      
      const finalUrl = page.url();
      const finalText = await page.$eval('body', el => el.textContent.replace(/\s+/g, ' ').substring(0, 200));
      console.log('Final URL:', finalUrl);
      console.log('Final text:', finalText);
      
      await page.screenshot({ path: `/root/.openclaw/workspace/snap_sug_done_${slug_alt}.png` });
      results.submitted.push(name);
      console.log(`✅ ${name} suggested!`);
    } else {
      console.log(`No link found for slug_alt=${slug_alt}`);
      
      // Dump all links for debugging
      const allLinks = await page.$$eval('a', ls => ls.map(l => ({ text: l.textContent.trim().substring(0,40), href: l.getAttribute('href') })).filter(l => l.href && l.href.includes('pantrymate')));
      console.log('PantryMate links:', JSON.stringify(allLinks));
      
      results.failed.push(`${name}: link not found`);
    }
    
    console.log('Responses captured:', JSON.stringify(responses));
    
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
  
  console.log('\n=== RESULTS ===');
  console.log(JSON.stringify(results, null, 2));
  
  await browser.close();
})();
