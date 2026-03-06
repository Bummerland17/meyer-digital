const { chromium } = require('playwright');

async function fillField(page, selector, value) {
  const el = page.locator(selector).first();
  await el.click({ clickCount: 3 });
  await el.type(value, { delay: 20 });
  // Also try setting via evaluate
  await page.evaluate((sel, val) => {
    const el = document.querySelector(sel);
    if (el) {
      const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set 
        || Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
      if (nativeInputValueSetter) nativeInputValueSetter.call(el, val);
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    }
  }, selector, value);
}

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

  // Category - computer services
  await page.locator('input[name="id"][value="76"]').check();
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {}),
    page.locator('button[name="go"]').first().click()
  ]);
  await page.waitForTimeout(2000);
  console.log('At edit form:', page.url());

  // Fill fields using type() for React compatibility
  console.log('Filling title...');
  const titleEl = page.locator('input[name="PostingTitle"]');
  await titleEl.click();
  await titleEl.fill('Custom App Development for Local Businesses');
  await page.keyboard.press('Tab');

  console.log('Filling body...');
  const bodyEl = page.locator('textarea[name="PostingBody"]');
  await bodyEl.click();
  await bodyEl.fill('Test description for debugging. Please ignore this posting.');
  await page.keyboard.press('Tab');

  console.log('Filling postal...');
  const postalEl = page.locator('input[name="postal"]');
  await postalEl.click();
  await postalEl.fill('85001');
  await page.keyboard.press('Tab');

  console.log('Filling email...');
  const emailEl = page.locator('input[name="FromEMail"]');
  await emailEl.click();
  await emailEl.fill('hello@pantrymate.net');
  await page.keyboard.press('Tab');

  // Check what values are now in the fields
  const titleVal = await titleEl.inputValue();
  const bodyVal = await bodyEl.inputValue();
  const postalVal = await postalEl.inputValue();
  const emailVal = await emailEl.inputValue();
  console.log('Title value:', titleVal);
  console.log('Body value:', bodyVal.substring(0, 50));
  console.log('Postal value:', postalVal);
  console.log('Email value:', emailVal);

  await page.screenshot({ path: '/tmp/cl_filled11.png' });

  // Submit
  console.log('\nSubmitting...');
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {}),
    page.locator('button[type="submit"]').first().click()
  ]);
  await page.waitForTimeout(3000);

  console.log('\nAfter submit URL:', page.url());
  const postBodyText = await page.textContent('body').catch(() => '');
  console.log('Page text (first 2000):', postBodyText.substring(0, 2000));
  await page.screenshot({ path: '/tmp/cl_after_submit11.png' });

  await browser.close();
})();
