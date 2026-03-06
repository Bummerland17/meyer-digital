const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();

  // Step 1: navigate
  await page.goto('https://post.craigslist.org/c/phx', { waitUntil: 'domcontentloaded', timeout: 30000 });
  
  // Step 1b: subarea
  await page.locator('input[type="radio"]').first().check();
  await page.locator('button[name="go"]').click();
  await page.waitForLoadState('domcontentloaded');
  console.log('After subarea:', page.url());
  
  // Step 2: select "service offered"
  await page.locator('input[value="so"]').check();
  await page.locator('button[name="go"]').click();
  await page.waitForLoadState('domcontentloaded');
  console.log('After type:', page.url());

  // Step 3: select "computer services"
  const computerLink = page.getByText(/computer services/i).first();
  if (await computerLink.count() > 0) {
    await computerLink.click();
    await page.waitForLoadState('domcontentloaded');
    console.log('After category:', page.url());
  }
  await page.screenshot({ path: '/tmp/cl_step4.png' });

  let html = await page.content();
  console.log('\nStep 4 HTML (first 6000 chars):');
  console.log(html.substring(0, 6000));

  // Check inputs
  const inputs = await page.locator('input, textarea, select').all();
  console.log(`\nFound ${inputs.length} form elements:`);
  for (const inp of inputs) {
    const tag = await inp.evaluate(el => el.tagName);
    const name = await inp.getAttribute('name').catch(() => '');
    const id = await inp.getAttribute('id').catch(() => '');
    const type = await inp.getAttribute('type').catch(() => '');
    const placeholder = await inp.getAttribute('placeholder').catch(() => '');
    console.log(`  <${tag}> name="${name}" id="${id}" type="${type}" placeholder="${placeholder}"`);
  }

  await browser.close();
})();
