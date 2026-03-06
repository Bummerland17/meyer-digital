const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');

chromium.use(StealthPlugin());

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ 
    viewport: { width: 1280, height: 900 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });
  const page = await context.newPage();

  try {
    // Check the verify page HTML for verification process details
    const verifyHtml = fs.readFileSync('/root/.openclaw/workspace/verify_page.html', 'utf8');
    const mainContent = verifyHtml.match(/<main[\s\S]*?<\/main>/i);
    if (mainContent) {
      console.log('Verify page main content:');
      console.log(mainContent[0].replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim().substring(0, 2000));
    }
    
    // Also check the management navbar on the edit page for owner-specific links
    const editHtml = fs.readFileSync('/root/.openclaw/workspace/edit_page.html', 'utf8');
    const navMatch = editHtml.match(/management-navbar[\s\S]*?<\/section>/i);
    if (navMatch) {
      const navLinks = navMatch[0].match(/href="[^"]*"[^>]*>[^<]*/g);
      console.log('\nManagement navbar links:', navLinks);
    }
    
    // Look for any pricing-related URLs in edit page
    const pricingMatch = editHtml.match(/pric[^"<]*/gi);
    console.log('\nPricing mentions:', [...new Set(pricingMatch)].slice(0,20));
    
    // Check if there's a pricing page for PantryMate
    await page.goto('https://www.saashub.com/pantrymate-pricing', { waitUntil: 'domcontentloaded', timeout: 20000 });
    await page.waitForTimeout(3000);
    console.log('\nPricing page title:', await page.title());
    console.log('Pricing URL:', page.url());
    
    // Check pricing page for a known product to find pattern
    await page.goto('https://www.saashub.com/notion-pricing', { waitUntil: 'domcontentloaded', timeout: 20000 });
    await page.waitForTimeout(3000);
    console.log('\nNotion pricing title:', await page.title());
    
    // Look at how competitors are added on a product page
    await page.goto('https://www.saashub.com/pantrymate-alternatives', { waitUntil: 'domcontentloaded', timeout: 20000 });
    await page.waitForTimeout(3000);
    console.log('\nAlternatives page title:', await page.title());
    const altLinks = await page.$$eval('a', ls =>
      ls.map(l => ({ text: l.textContent.trim().substring(0,60), href: l.href }))
        .filter(l => /submit|add|suggest|edit|compet/i.test(l.text + l.href))
        .slice(0, 10)
    );
    console.log('Alternatives page action links:', JSON.stringify(altLinks));
    
  } catch(e) {
    console.error('Error:', e.message);
  }
  await browser.close();
})();
