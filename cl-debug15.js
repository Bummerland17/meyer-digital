const { chromium } = require('playwright');

async function clickContinue(page, timeout = 15000) {
  const btn = page.locator('button[name="go"], button[type="submit"], button:has-text("continue"), button:has-text("publish"), button:has-text("done with images")').first();
  if (await btn.count() > 0) {
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout }).catch(() => {}),
      btn.click()
    ]);
    await page.waitForTimeout(2000);
    return true;
  }
  return false;
}

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();

  await page.goto('https://post.craigslist.org/c/phx', { waitUntil: 'load', timeout: 30000 });
  await page.waitForTimeout(1000);

  // Run up through category selection, form fill, geoverify, image, preview
  // Subarea
  await page.locator('input[type="radio"]').first().check();
  await clickContinue(page);

  let bt = await page.textContent('body').catch(() => '');
  if (bt.includes('what type of posting')) {
    await page.locator('input[value="so"]').check();
    await clickContinue(page);
  }

  await page.locator('input[name="id"][value="76"]').check();
  await clickContinue(page);
  await page.waitForTimeout(1000);

  // Fill form
  const titleEl = page.locator('input[name="PostingTitle"]');
  await titleEl.click(); await titleEl.fill('Test Post'); await page.keyboard.press('Tab');
  const bodyEl = page.locator('textarea[name="PostingBody"]');
  await bodyEl.click(); await bodyEl.fill('Test body text.'); await page.keyboard.press('Tab');
  const postalEl = page.locator('input[name="postal"]');
  await postalEl.click(); await postalEl.fill('85001'); await page.keyboard.press('Tab');
  const emailEl = page.locator('input[name="FromEMail"]');
  await emailEl.click(); await emailEl.fill('hello@pantrymate.net'); await page.keyboard.press('Tab');
  await page.waitForTimeout(500);
  await clickContinue(page);
  console.log('After form:', page.url());

  // Geoverify
  await clickContinue(page);
  console.log('After geoverify:', page.url());

  // Image
  await page.screenshot({ path: '/tmp/cl_image_step.png' });
  const imgBt = await page.textContent('body').catch(() => '');
  console.log('Image page snippet:', imgBt.replace(/\s+/g,' ').substring(0, 200));
  const doneBtns = await page.locator('button').all();
  for (const b of doneBtns) {
    const txt = await b.textContent().catch(() => '');
    const name = await b.getAttribute('name').catch(() => '');
    console.log(`  btn: "${txt?.trim()}" name="${name}"`);
  }
  
  // Click "done with images"
  const doneBtn = page.locator('button:has-text("done with images"), button[name="go"]').first();
  if (await doneBtn.count() > 0) {
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {}),
      doneBtn.click()
    ]);
    await page.waitForTimeout(2000);
  }
  console.log('After image:', page.url());

  // Preview
  await page.screenshot({ path: '/tmp/cl_preview2.png' });
  const prevBt = await page.textContent('body').catch(() => '');
  console.log('Preview page snippet:', prevBt.replace(/\s+/g,' ').substring(0, 400));

  const prevHtml = await page.content();
  const prevSec = prevHtml.indexOf('<section');
  console.log('\nPreview section HTML:');
  console.log(prevHtml.substring(prevSec, prevSec + 3000));

  // Look for publish button specifically
  const allBtns = await page.locator('button, input[type="submit"], input[type="button"]').all();
  console.log('\nAll buttons on preview page:');
  for (const b of allBtns) {
    const txt = await b.textContent().catch(() => '');
    const val = await b.getAttribute('value').catch(() => '');
    const name = await b.getAttribute('name').catch(() => '');
    const type = await b.getAttribute('type').catch(() => '');
    console.log(`  <${type}> "${txt?.trim()}" value="${val}" name="${name}"`);
  }

  // Click publish
  await clickContinue(page);
  console.log('\nAfter publish:', page.url());
  await page.screenshot({ path: '/tmp/cl_final.png' });
  
  const finalHtml = await page.content();
  const finalSec = finalHtml.indexOf('<section');
  console.log('Final section HTML:');
  console.log(finalHtml.substring(finalSec, finalSec + 5000));

  await browser.close();
})();
