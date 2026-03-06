const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();

  // Navigate
  await page.goto('https://post.craigslist.org/c/phx', { waitUntil: 'load', timeout: 30000 });
  await page.waitForTimeout(1000);

  // Subarea
  console.log('URL:', page.url());
  await page.locator('input[type="radio"]').first().check();
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {}),
    page.locator('button[name="go"]').first().click()
  ]);
  await page.waitForTimeout(1000);
  console.log('After subarea:', page.url());

  // Type selection
  let bodyText = await page.textContent('body').catch(() => '');
  if (bodyText.includes('what type of posting')) {
    console.log('On type selection page');
    await page.locator('input[value="so"]').check();
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {}),
      page.locator('button[name="go"]').first().click()
    ]);
    await page.waitForTimeout(1000);
    console.log('After type:', page.url());
  }

  // Category selection - inspect what's there
  bodyText = await page.textContent('body').catch(() => '');
  console.log('\nPage text includes "computer services":', bodyText.includes('computer services'));
  
  // Find the computer services link
  const links = await page.locator('a').all();
  console.log(`\nAll links on category page:`);
  for (const link of links) {
    const txt = await link.textContent().catch(() => '');
    const href = await link.getAttribute('href').catch(() => '');
    if (txt && txt.trim()) {
      console.log(`  "${txt.trim()}" -> ${href}`);
    }
  }

  // Also check list items
  console.log('\nAll list items / labels:');
  const items = await page.locator('li label, ul.selection-list li').all();
  for (const item of items) {
    const txt = await item.textContent().catch(() => '');
    const radio = await item.locator('input[type="radio"]').first();
    let val = '';
    if (await radio.count() > 0) val = await radio.getAttribute('value').catch(() => '');
    if (txt && txt.trim()) console.log(`  "${txt.trim()}" val="${val}"`);
  }

  await page.screenshot({ path: '/tmp/cl_cat_page.png' });

  await browser.close();
})();
