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

  // Category - select computer services (value=76)
  await page.locator('input[name="id"][value="76"]').check();
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {}),
    page.locator('button[name="go"]').first().click()
  ]);
  await page.waitForTimeout(2000);
  
  console.log('After category:', page.url());
  await page.screenshot({ path: '/tmp/cl_after_cat.png' });

  const html = await page.content();
  // Find section
  const sStart = html.indexOf('<section');
  const sEnd = html.indexOf('</section>', sStart) + '</section>'.length;
  console.log('\nPage section HTML:');
  console.log(html.substring(sStart, Math.min(sEnd, sStart + 8000)));

  // Also log form elements
  const elements = await page.locator('input, textarea, select').all();
  console.log(`\n\nForm elements (${elements.length}):`);
  for (const el of elements) {
    const tag = await el.evaluate(e => e.tagName);
    const name = await el.getAttribute('name').catch(() => '');
    const id = await el.getAttribute('id').catch(() => '');
    const type = await el.getAttribute('type').catch(() => '');
    const value = await el.getAttribute('value').catch(() => '');
    console.log(`  <${tag.toLowerCase()}> name="${name}" id="${id}" type="${type}" value="${value?.substring(0,30)}"`);
  }

  await browser.close();
})();
