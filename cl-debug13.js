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
  console.log('Step: edit form', page.url());

  // Fill with Tab press technique
  const titleEl = page.locator('input[name="PostingTitle"]');
  await titleEl.click();
  await titleEl.fill('Custom App Development for Local Businesses');
  await page.keyboard.press('Tab');

  const bodyEl = page.locator('textarea[name="PostingBody"]');
  await bodyEl.click();
  await bodyEl.fill('Test description for debugging. Please ignore this posting.');
  await page.keyboard.press('Tab');

  const postalEl = page.locator('input[name="postal"]');
  await postalEl.click();
  await postalEl.fill('85001');
  await page.keyboard.press('Tab');

  const emailEl = page.locator('input[name="FromEMail"]');
  await emailEl.click();
  await emailEl.fill('hello@pantrymate.net');
  await page.keyboard.press('Tab');

  // Submit
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {}),
    page.locator('button[type="submit"]').first().click()
  ]);
  await page.waitForTimeout(3000);
  console.log('After edit submit:', page.url());

  // Walk through all remaining steps
  for (let i = 0; i < 10; i++) {
    const url = page.url();
    const bt = await page.textContent('body').catch(() => '');
    await page.screenshot({ path: `/tmp/cl_step_${i}_${url.split('?s=')[1] || 'unknown'}.png` });
    console.log(`\n--- Step ${i}: ${url} ---`);
    console.log('Body snippet:', bt.replace(/\s+/g, ' ').substring(0, 500));

    if (url.includes('?s=geoverify') || bt.includes('choose exact location') || bt.includes('find')) {
      console.log('  → Geoverify step: clicking continue');
      const cont = page.locator('button:has-text("continue"), button[name="go"]').first();
      if (await cont.count() > 0) {
        await Promise.all([
          page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {}),
          cont.click()
        ]);
        await page.waitForTimeout(2000);
        continue;
      }
    }

    if (url.includes('?s=preview') || bt.includes('review your post') || bt.includes('publish')) {
      console.log('  → Preview/publish step');
      const pub = page.locator('button:has-text("publish"), input[value="publish"], button[name="go"]').first();
      if (await pub.count() > 0) {
        console.log('  → Clicking publish');
        await Promise.all([
          page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {}),
          pub.click()
        ]);
        await page.waitForTimeout(3000);
        continue;
      }
    }

    if (bt.toLowerCase().includes('payment') || bt.toLowerCase().includes('credit card') || 
        bt.toLowerCase().includes('billing') || url.includes('pay')) {
      console.log('  → PAYMENT PAGE DETECTED - cannot proceed without payment');
      break;
    }

    if (bt.toLowerCase().includes('check your email') || bt.toLowerCase().includes('confirm') || 
        bt.toLowerCase().includes('email has been sent') || url.includes('manage')) {
      console.log('  → SUCCESS: Confirmation/email sent page');
      break;
    }

    // Show buttons
    const buttons = await page.locator('button, input[type="submit"]').all();
    console.log('  Buttons on page:');
    for (const b of buttons) {
      const txt = await b.textContent().catch(() => '');
      const val = await b.getAttribute('value').catch(() => '');
      const name = await b.getAttribute('name').catch(() => '');
      console.log(`    button: "${txt?.trim()}" value="${val}" name="${name}"`);
    }

    // Try clicking the first continue/go button
    const goBtn = page.locator('button[name="go"], button:has-text("continue"), button[type="submit"]').first();
    if (await goBtn.count() > 0) {
      console.log('  → Clicking go/continue button');
      await Promise.all([
        page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {}),
        goBtn.click()
      ]);
      await page.waitForTimeout(2000);
    } else {
      console.log('  → No continue button, stopping');
      break;
    }
  }

  await browser.close();
})();
