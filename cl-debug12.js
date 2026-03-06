const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();

  await page.goto('https://post.craigslist.org/c/phx', { waitUntil: 'load', timeout: 30000 });
  await page.waitForTimeout(1000);

  // Subarea
  await page.locator('input[type="radio"]').first().check();
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {}),
    page.locator('button[name="go"]').first().click()
  ]);
  await page.waitForTimeout(1000);

  // Type
  let bodyText = await page.textContent('body').catch(() => '');
  if (bodyText.includes('what type of posting')) {
    await page.locator('input[value="so"]').check();
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {}),
      page.locator('button[name="go"]').first().click()
    ]);
    await page.waitForTimeout(1000);
  }

  // Category
  await page.locator('input[name="id"][value="76"]').check();
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {}),
    page.locator('button[name="go"]').first().click()
  ]);
  await page.waitForTimeout(2000);

  // Fill form
  await page.locator('input[name="PostingTitle"]').click();
  await page.locator('input[name="PostingTitle"]').fill('Test Post - Debug Only');
  await page.locator('textarea[name="PostingBody"]').click();
  await page.locator('textarea[name="PostingBody"]').fill('Test description for debugging. Please ignore this posting.');
  await page.locator('input[name="postal"]').click();
  await page.locator('input[name="postal"]').fill('85001');
  await page.locator('input[name="FromEMail"]').click();
  await page.locator('input[name="FromEMail"]').fill('hello@pantrymate.net');

  // Submit form
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {}),
    page.locator('button[type="submit"]').first().click()
  ]);
  await page.waitForTimeout(3000);
  console.log('After form submit:', page.url());

  // GEOVERIFY step - get the HTML
  const html = await page.content();
  const sStart = html.indexOf('<section');
  const sEnd = html.indexOf('</section>', sStart) + '</section>'.length;
  console.log('\nGEOVERIFY section HTML:');
  console.log(html.substring(sStart, Math.min(sEnd, sStart + 4000)));

  // Form elements on geoverify
  const elements = await page.locator('input, textarea, select, button').all();
  console.log(`\nForm elements (${elements.length}):`);
  for (const el of elements) {
    const tag = await el.evaluate(e => e.tagName);
    const name = await el.getAttribute('name').catch(() => '');
    const id = await el.getAttribute('id').catch(() => '');
    const type = await el.getAttribute('type').catch(() => '');
    const value = await el.getAttribute('value').catch(() => '');
    const text = await el.textContent().catch(() => '');
    console.log(`  <${tag.toLowerCase()}> name="${name}" id="${id}" type="${type}" value="${value?.substring(0,30)}" text="${text?.trim().substring(0,30)}"`);
  }

  // Try to fill city field and continue
  console.log('\nFilling geoverify location fields...');
  const cityField = page.locator('input[placeholder*="city"], input[name="city"]').first();
  if (await cityField.count() > 0) {
    await cityField.click();
    await cityField.fill('Phoenix');
  }
  const zipField = page.locator('input[placeholder*="ZIP"], input[name="zip"], input[placeholder*="postal"]').first();
  if (await zipField.count() > 0) {
    await zipField.click();
    await zipField.fill('85001');
  }

  await page.screenshot({ path: '/tmp/cl_geoverify.png' });

  // Click continue
  const contBtn = page.locator('button:has-text("continue"), button[name="go"]').first();
  if (await contBtn.count() > 0) {
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {}),
      contBtn.click()
    ]);
    await page.waitForTimeout(3000);
    console.log('\nAfter geoverify:', page.url());
    
    const bodyText3 = await page.textContent('body').catch(() => '');
    console.log('Page text (first 2000):', bodyText3.substring(0, 2000));
    await page.screenshot({ path: '/tmp/cl_after_geoverify.png' });
  }

  await browser.close();
})();
