const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();

  await page.goto('https://post.craigslist.org/c/phx', { waitUntil: 'load', timeout: 30000 });
  await page.waitForTimeout(1000);

  // Fast path through all steps
  await page.locator('input[type="radio"]').first().check();
  await Promise.all([page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(()=>{}), page.locator('button[name="go"]').first().click()]);
  await page.waitForTimeout(1000);

  let bt = await page.textContent('body').catch(() => '');
  if (bt.includes('what type of posting')) {
    await page.locator('input[value="so"]').check();
    await Promise.all([page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(()=>{}), page.locator('button[name="go"]').first().click()]);
    await page.waitForTimeout(1000);
  }

  await page.locator('input[name="id"][value="76"]').check();
  await Promise.all([page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(()=>{}), page.locator('button[name="go"]').first().click()]);
  await page.waitForTimeout(2000);

  const titleEl = page.locator('input[name="PostingTitle"]');
  await titleEl.click(); await titleEl.fill('Test Post'); await page.keyboard.press('Tab');
  const bodyEl = page.locator('textarea[name="PostingBody"]');
  await bodyEl.click(); await bodyEl.fill('Test body.'); await page.keyboard.press('Tab');
  const postalEl = page.locator('input[name="postal"]');
  await postalEl.click(); await postalEl.fill('85001'); await page.keyboard.press('Tab');
  const emailEl = page.locator('input[name="FromEMail"]');
  await emailEl.click(); await emailEl.fill('hello@pantrymate.net'); await page.keyboard.press('Tab');

  await Promise.all([page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(()=>{}), page.locator('button[type="submit"]').first().click()]);
  await page.waitForTimeout(2000);
  // Geoverify - continue
  await Promise.all([page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(()=>{}), page.locator('button[name="go"]').first().click()]);
  await page.waitForTimeout(2000);
  // Image step - done with images
  await Promise.all([page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(()=>{}), page.locator('button[name="go"]:has-text("done")').click()]);
  await page.waitForTimeout(2000);
  // Preview - publish
  console.log('At preview:', page.url());
  await page.screenshot({ path: '/tmp/cl_preview.png' });
  const previewHtml = await page.content();
  const sec = previewHtml.indexOf('<section');
  console.log('Preview section:');
  console.log(previewHtml.substring(sec, sec + 4000));

  await Promise.all([page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(()=>{}), page.locator('button[name="go"], button[type="submit"]').first().click()]);
  await page.waitForTimeout(3000);
  console.log('\nAfter publish:', page.url());
  await page.screenshot({ path: '/tmp/cl_loginloop.png' });
  
  const finalHtml = await page.content();
  const sec2 = finalHtml.indexOf('<section');
  console.log('Final section:');
  console.log(finalHtml.substring(sec2, sec2 + 5000));

  await browser.close();
})();
