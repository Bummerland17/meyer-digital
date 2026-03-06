const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');

chromium.use(StealthPlugin());

const results = { submitted: [], failed: [] };

async function suggestAlt(context, slug_alt, name) {
  const page = await context.newPage();
  
  // Intercept and capture responses
  const responses = [];
  page.on('response', async resp => {
    const url = resp.url();
    if (url.includes('pantrymate') || url.includes('suggest')) {
      try {
        const body = await resp.text();
        responses.push({ url, status: resp.status(), body: body.substring(0, 300) });
      } catch(e) {}
    }
  });
  
  try {
    console.log(`\n=== Suggesting ${name} ===`);
    
    // Navigate to the PantryMate page first (where the suggest modal is loaded)
    await page.goto('https://www.saashub.com/pantrymate', { waitUntil: 'domcontentloaded', timeout: 20000 });
    await page.waitForTimeout(3000);
    
    // Click "Suggest an alternative" link
    await page.click('a[href="/suggest_alternative/pantrymate"]');
    await page.waitForTimeout(3000);
    
    await page.screenshot({ path: `/root/.openclaw/workspace/snap_modal_${slug_alt}.png` });
    
    // Check if modal/turbo-frame appeared
    const modalVisible = await page.$('.modal.is-active, [data-controller="modal"]');
    console.log('Modal visible:', !!modalVisible);
    
    // Find the query input in the modal
    const queryInput = await page.$('input[name="query"]');
    if (!queryInput) {
      console.log('No query input found in modal');
      results.failed.push(name);
      await page.close();
      return;
    }
    
    // Type the name
    await queryInput.fill('');
    await queryInput.type(name, { delay: 100 });
    await page.waitForTimeout(3000); // Wait for turbo-frame response
    
    await page.screenshot({ path: `/root/.openclaw/workspace/snap_typed_${slug_alt}.png` });
    
    // Check turbo-frame for results
    const turboFrame = await page.$('turbo-frame#service_autocomplete');
    if (turboFrame) {
      const frameHtml = await turboFrame.innerHTML();
      console.log('Turbo frame content:', frameHtml.substring(0, 500));
      
      // Click on the specific link in the turbo frame
      const link = await page.$(`turbo-frame#service_autocomplete a[href*="slug_alt=${slug_alt}"]`);
      if (link) {
        console.log(`Found link for ${name}, clicking...`);
        await link.click();
        await page.waitForTimeout(3000);
        
        const afterUrl = page.url();
        const bodyText = await page.$eval('body', el => el.textContent.replace(/\s+/g, ' ').substring(0, 300));
        console.log('After click URL:', afterUrl);
        console.log('Body:', bodyText.substring(0, 200));
        
        await page.screenshot({ path: `/root/.openclaw/workspace/snap_after_click_${slug_alt}.png` });
        
        results.submitted.push(name);
        console.log(`✅ ${name} suggested!`);
      } else {
        // Try clicking any link with the slug
        const anyLink = await page.$(`a[href*="${slug_alt}"]`);
        if (anyLink) {
          const href = await anyLink.getAttribute('href');
          console.log(`Found link with href: ${href}`);
          await anyLink.click();
          await page.waitForTimeout(3000);
          results.submitted.push(name);
        } else {
          console.log(`No link found for ${slug_alt} in turbo frame`);
          console.log('All links in page:', (await page.$$eval('a', ls => ls.map(l => l.href).filter(h => h.includes(slug_alt)))));
          results.failed.push(`${name}: link not found in results`);
        }
      }
    } else {
      console.log('No turbo frame found - checking regular DOM');
      const allLinks = await page.$$eval('a', ls => ls.map(l => ({ href: l.href, text: l.textContent.trim().substring(0, 60) })).filter(l => l.text.toLowerCase().includes(name.toLowerCase().substring(0, 5))));
      console.log('Matching links:', JSON.stringify(allLinks));
      results.failed.push(`${name}: no turbo frame`);
    }
    
    console.log('Captured responses:', JSON.stringify(responses.slice(-3)));
    
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
  fs.writeFileSync('/root/.openclaw/workspace/alt_results2.json', JSON.stringify(results, null, 2));
  
  await browser.close();
})();
