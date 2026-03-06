const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');

chromium.use(StealthPlugin());

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ 
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });
  const page = await context.newPage();

  // Check the PantryMate alternatives page
  await page.goto('https://www.saashub.com/pantrymate-alternatives', { waitUntil: 'domcontentloaded', timeout: 20000 });
  await page.waitForTimeout(3000);
  
  const altText = await page.$eval('body', el => el.textContent);
  const hasSuperCook = altText.toLowerCase().includes('supercook');
  const hasMealime = altText.toLowerCase().includes('mealime');
  const hasYummly = altText.toLowerCase().includes('yummly');
  
  console.log('SuperCook in alternatives:', hasSuperCook);
  console.log('Mealime in alternatives:', hasMealime);
  console.log('Yummly in alternatives:', hasYummly);
  
  // Get all product links
  const products = await page.$$eval('a[href*="saashub.com/"]', ls =>
    ls.map(l => ({ text: l.textContent.trim().substring(0,60), href: l.href }))
      .filter(l => !l.href.includes('/best-') && !l.href.includes('/submit') && !l.href.includes('/login'))
      .slice(0, 20)
  );
  console.log('Products on alternatives page:', JSON.stringify(products));
  
  await page.screenshot({ path: '/root/.openclaw/workspace/snap_alts_check.png', fullPage: false });
  
  // Also check the main pantrymate page to see if categories/description updated
  await page.goto('https://www.saashub.com/pantrymate', { waitUntil: 'domcontentloaded', timeout: 20000 });
  await page.waitForTimeout(3000);
  
  const pmText = await page.$eval('body', el => el.textContent.replace(/\s+/g, ' ').substring(0, 2000));
  const hasCategories = pmText.toLowerCase().includes('meal planning') || pmText.toLowerCase().includes('productivity');
  const hasDescription = pmText.toLowerCase().includes('food waste') || pmText.toLowerCase().includes('pantry ingredients');
  
  console.log('\nPantryMate page:');
  console.log('Has Meal Planning/Productivity categories:', hasCategories);
  console.log('Has description with food waste/pantry:', hasDescription);
  
  await browser.close();
})();
