const { chromium } = require('playwright');

// Walk through all steps for ONE post to understand the flow
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();

  // Step 1: go to post page (session created)
  console.log('Step 1: Navigate to post URL');
  await page.goto('https://post.craigslist.org/c/phx', { waitUntil: 'domcontentloaded', timeout: 30000 });
  console.log('URL after navigate:', page.url());
  
  // Step 1b: Choose subarea — just pick first option
  const subAreaRadio = page.locator('input[type="radio"]').first();
  if (await subAreaRadio.count() > 0) {
    await subAreaRadio.check();
    console.log('Selected first subarea');
  }
  const continueBtn = page.locator('button[name="go"], button:has-text("continue")').first();
  if (await continueBtn.count() > 0) {
    await continueBtn.click();
    await page.waitForLoadState('domcontentloaded');
  }
  console.log('URL after subarea:', page.url());
  await page.screenshot({ path: '/tmp/cl_step2.png' });

  // Show current page
  let html = await page.content();
  console.log('\nStep 2 HTML snippet:');
  console.log(html.substring(html.indexOf('<section'), html.indexOf('<section') + 3000));

  // Step 2: Choose posting type
  // Find "service offered" option
  const soRadio = page.locator('input[value="so"], input[value="S"]');
  if (await soRadio.count() > 0) {
    await soRadio.first().check();
    console.log('Selected service offered');
  } else {
    // Try labels
    const labels = await page.locator('label').all();
    for (const l of labels) {
      const txt = await l.textContent().catch(() => '');
      console.log('  Label:', txt.trim());
    }
    // Try clicking service offered label
    const soLabel = page.getByText(/service offered/i).first();
    if (await soLabel.count() > 0) {
      await soLabel.click();
      console.log('Clicked service offered label');
    }
  }
  
  const cont2 = page.locator('button[name="go"], button:has-text("continue")').first();
  if (await cont2.count() > 0) {
    await cont2.click();
    await page.waitForLoadState('domcontentloaded');
  }
  console.log('URL after type selection:', page.url());
  await page.screenshot({ path: '/tmp/cl_step3.png' });

  html = await page.content();
  console.log('\nStep 3 HTML snippet (category selection):');
  // Find all links/labels that might be categories
  const items = await page.locator('a, label, li').all();
  console.log(`Found ${items.length} items`);
  for (const item of items.slice(0, 50)) {
    const txt = await item.textContent().catch(() => '');
    if (txt && txt.trim().length > 0 && txt.trim().length < 100) {
      console.log('  ITEM:', txt.trim());
    }
  }

  await browser.close();
})();
