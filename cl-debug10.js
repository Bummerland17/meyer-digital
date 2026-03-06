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

  // Category - computer services
  await page.locator('input[name="id"][value="76"]').check();
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {}),
    page.locator('button[name="go"]').first().click()
  ]);
  await page.waitForTimeout(2000);
  console.log('At edit form:', page.url());

  // Fill title
  await page.locator('input[name="PostingTitle"]').fill('Custom App Development for Local Businesses — $1,500 flat rate');
  // Fill body
  await page.locator('textarea[name="PostingBody"]').fill('Test post body for debugging purposes. Please ignore.');
  // Fill postal/zip
  await page.locator('input[name="postal"]').fill('85001');
  // Fill email
  await page.locator('input[name="FromEMail"]').fill('hello@pantrymate.net');
  // Uncheck phone
  const phoneCheck = page.locator('input[name="show_phone_ok"]');
  if (await phoneCheck.isChecked()) await phoneCheck.uncheck();

  await page.screenshot({ path: '/tmp/cl_form_filled.png' });
  console.log('Form filled, submitting...');

  // Submit
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {}),
    page.locator('button[name="go"], button[type="submit"]').first().click()
  ]);
  await page.waitForTimeout(3000);

  console.log('After form submit:', page.url());
  await page.screenshot({ path: '/tmp/cl_after_submit.png' });

  const bodyText2 = await page.textContent('body').catch(() => '');
  console.log('\nPage text (first 3000):', bodyText2.substring(0, 3000));

  // If there's a payment section
  const html = await page.content();
  const sStart = html.indexOf('<section');
  const sEnd = html.indexOf('</section>', sStart) + '</section>'.length;
  if (sStart > 0) {
    console.log('\nSection HTML:');
    console.log(html.substring(sStart, Math.min(sEnd, sStart + 5000)));
  }

  await browser.close();
})();
