const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();

  await page.goto('https://post.craigslist.org/c/phx', { waitUntil: 'load', timeout: 30000 });
  await page.waitForTimeout(1000);

  // Subarea - radio then continue button
  await page.locator('input[type="radio"]').first().check();
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {}),
    page.locator('button[name="go"]').first().click()
  ]);
  await page.waitForTimeout(1500);
  console.log('After subarea:', page.url());

  // Type - radio then continue button  
  let bt = await page.textContent('body').catch(() => '');
  if (bt.includes('what type of posting')) {
    await page.locator('input[value="so"]').check();
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {}),
      page.locator('button[name="go"]').first().click()
    ]);
    await page.waitForTimeout(1500);
    console.log('After type:', page.url());
  }

  // Category - clicking radio auto-navigates (no continue needed)
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {}),
    page.locator('input[name="id"][value="76"]').click()
  ]);
  await page.waitForTimeout(2000);
  console.log('After category click:', page.url());

  // If we're still on category page (not auto-navigated), click continue
  if (page.url().includes('?s=cat')) {
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {}),
      page.locator('button[name="go"]').first().click()
    ]);
    await page.waitForTimeout(2000);
    console.log('After category continue:', page.url());
  }

  // Should be at edit form now
  console.log('Edit form URL:', page.url());

  // Fill form
  const titleEl = page.locator('input[name="PostingTitle"]');
  await titleEl.click(); await titleEl.fill('Custom App Development for Local Businesses'); await page.keyboard.press('Tab');
  const bodyEl = page.locator('textarea[name="PostingBody"]');
  await bodyEl.click(); await bodyEl.fill('Test description. Please ignore.'); await page.keyboard.press('Tab');
  const postalEl = page.locator('input[name="postal"]');
  await postalEl.click(); await postalEl.fill('85001'); await page.keyboard.press('Tab');
  const emailEl = page.locator('input[name="FromEMail"]');
  await emailEl.click(); await emailEl.fill('hello@pantrymate.net'); await page.keyboard.press('Tab');
  await page.waitForTimeout(500);

  console.log('Fields filled. Values:');
  console.log('  title:', await titleEl.inputValue());
  console.log('  postal:', await postalEl.inputValue());
  console.log('  email:', await emailEl.inputValue());

  // Submit edit form
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {}),
    page.locator('button[type="submit"], button[name="go"]').first().click()
  ]);
  await page.waitForTimeout(2000);
  console.log('After form submit:', page.url());

  // Geoverify - just click continue
  if (page.url().includes('?s=geoverify') || page.url().includes('geoverify')) {
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {}),
      page.locator('button[name="go"], button:has-text("continue")').first().click()
    ]);
    await page.waitForTimeout(2000);
    console.log('After geoverify:', page.url());
  }

  // Image step - click done with images
  if (page.url().includes('editimage') || page.url().includes('image')) {
    const doneBtn = page.locator('button:has-text("done with images")').first();
    if (await doneBtn.count() > 0) {
      await Promise.all([
        page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {}),
        doneBtn.click()
      ]);
      await page.waitForTimeout(2000);
      console.log('After image done:', page.url());
    }
  }

  // Preview - get full section HTML to understand it
  await page.screenshot({ path: '/tmp/cl_preview16.png' });
  const previewHtml = await page.content();
  const sec = previewHtml.indexOf('<section');
  console.log('\nPreview/current page section HTML:');
  console.log(previewHtml.substring(sec, sec + 5000));

  console.log('\nButtons on this page:');
  const allBtns = await page.locator('button, input[type="submit"]').all();
  for (const b of allBtns) {
    const txt = await b.textContent().catch(() => '');
    const val = await b.getAttribute('value').catch(() => '');
    const name = await b.getAttribute('name').catch(() => '');
    console.log(`  "${txt?.trim()}" value="${val}" name="${name}"`);
  }

  // Try to click publish
  const publishBtn = page.locator('button:has-text("publish"), input[value="publish"]').first();
  if (await publishBtn.count() > 0) {
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {}),
      publishBtn.click()
    ]);
    await page.waitForTimeout(3000);
    console.log('\nAfter publish click:', page.url());
    await page.screenshot({ path: '/tmp/cl_after_publish16.png' });
    const finalHtml = await page.content();
    const fSec = finalHtml.indexOf('<section');
    console.log('Final section:');
    console.log(finalHtml.substring(fSec, fSec + 5000));
  }

  await browser.close();
})();
