const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');

chromium.use(StealthPlugin());

const results = { submitted: [], failed: [] };

async function suggestAlternative(page, competitor) {
  try {
    console.log(`\nSuggesting: ${competitor}`);
    await page.goto('https://www.saashub.com/suggest_alternative/pantrymate', { waitUntil: 'domcontentloaded', timeout: 20000 });
    await page.waitForTimeout(2000);
    
    const queryInput = await page.$('input[name="query"]');
    if (!queryInput) {
      console.log('No query input found');
      results.failed.push(competitor);
      return;
    }
    
    // Type the competitor name
    await queryInput.fill('');
    await queryInput.type(competitor, { delay: 100 });
    await page.waitForTimeout(2000);
    
    await page.screenshot({ path: `/root/.openclaw/workspace/snap_suggest_${competitor.toLowerCase().replace(/\s/g,'_')}.png` });
    
    // Wait for autocomplete dropdown
    const html = await page.content();
    
    // Look for data items or list items that contain the competitor name
    const allText = await page.$eval('body', el => el.textContent);
    console.log('Page text excerpt:', allText.substring(0, 500));
    
    // Try to find li/div/a that matches
    const selectors = [
      `li:has-text("${competitor}")`,
      `[data-value]:has-text("${competitor}")`,
      `.suggestion:has-text("${competitor}")`,
      `[class*="result"]:has-text("${competitor}")`,
      `[class*="item"]:has-text("${competitor}")`,
    ];
    
    let clicked = false;
    for (const sel of selectors) {
      try {
        const el = await page.$(sel);
        if (el) {
          await el.click();
          await page.waitForTimeout(2000);
          console.log(`Clicked: ${sel}`);
          clicked = true;
          break;
        }
      } catch(e) { /* skip */ }
    }
    
    if (!clicked) {
      // Check the HTML structure for autocomplete
      const autocompleteHtml = await page.$$eval('[class*="autocomplete"], [class*="suggest"], [id*="autocomplete"], [id*="suggest"]', els =>
        els.map(el => ({ class: el.className, id: el.id, html: el.innerHTML.substring(0,300) }))
      );
      console.log('Autocomplete elements:', JSON.stringify(autocompleteHtml.slice(0,5)));
      
      // Check all visible links/elements after typing
      const visibleLinks = await page.$$eval('a[href*="/"], li', els =>
        els.map(el => ({ text: el.textContent.trim().substring(0,60), href: el.getAttribute('href') || '' }))
          .filter(l => l.text.length > 1 && l.text.length < 100)
          .slice(0, 20)
      );
      console.log('Visible items after typing:', JSON.stringify(visibleLinks));
      
      results.failed.push(`${competitor}: couldn't find clickable suggestion`);
    } else {
      const afterUrl = page.url();
      const bodyText = await page.$eval('body', el => el.textContent.replace(/\s+/g, ' ').substring(0,300));
      console.log(`After selecting ${competitor}:`, afterUrl);
      console.log('Body:', bodyText.substring(0, 200));
      
      if (bodyText.toLowerCase().includes('success') || bodyText.toLowerCase().includes('thank') || afterUrl !== 'https://www.saashub.com/suggest_alternative/pantrymate') {
        results.submitted.push(competitor);
        console.log(`✅ ${competitor} suggested`);
      } else {
        results.failed.push(`${competitor}: unclear if submitted`);
      }
    }
    
  } catch(e) {
    console.error(`Error suggesting ${competitor}:`, e.message);
    results.failed.push(`${competitor}: ${e.message}`);
  }
}

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ 
    viewport: { width: 1280, height: 900 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });
  const page = await context.newPage();
  
  // Check the HTML of the suggest page more carefully
  await page.goto('https://www.saashub.com/suggest_alternative/pantrymate', { waitUntil: 'domcontentloaded', timeout: 20000 });
  await page.waitForTimeout(3000);
  const html = await page.content();
  fs.writeFileSync('/root/.openclaw/workspace/suggest_page.html', html);
  console.log('Suggest page HTML saved');
  
  // Type and see what happens
  const queryInput = await page.$('input[name="query"]');
  if (queryInput) {
    await queryInput.type('Supercook', { delay: 100 });
    await page.waitForTimeout(3000);
    
    // Check all elements with autocomplete-related patterns
    const dynamicEls = await page.$$eval('*', els =>
      els.filter(el => el.children.length > 0 && el.textContent.toLowerCase().includes('supercook'))
        .map(el => ({ tag: el.tagName, class: el.className, id: el.id, html: el.innerHTML.substring(0,200) }))
        .slice(0, 10)
    );
    console.log('Dynamic elements after typing:', JSON.stringify(dynamicEls));
    
    await page.screenshot({ path: '/root/.openclaw/workspace/snap_suggest_typed.png', fullPage: true });
  }
  
  await browser.close();
  console.log('\nResults:', JSON.stringify(results, null, 2));
})();
