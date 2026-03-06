const { chromium } = require('playwright');

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();

  await page.goto('https://post.craigslist.org/c/phx', { waitUntil: 'load', timeout: 30000 });
  await sleep(1500);

  // Subarea
  await page.locator('input[type="radio"]').first().check();
  await Promise.all([page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(()=>{}), page.locator('button[name="go"]').first().click()]);
  await sleep(1500);

  // Type
  let bt = await page.textContent('body').catch(() => '');
  if (bt.includes('what type of posting')) {
    await page.locator('input[value="so"]').check();
    await Promise.all([page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(()=>{}), page.locator('button[name="go"]').first().click()]);
    await sleep(1500);
  }

  // Category (auto-nav)
  await Promise.all([page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(()=>{}), page.locator('input[name="id"][value="76"]').click()]);
  await sleep(2000);
  console.log('At:', page.url().split('?s=')[1]);

  // Fill form
  const titleEl = page.locator('input[name="PostingTitle"]');
  await titleEl.click(); await titleEl.fill('Custom App Development for Local Businesses'); await page.keyboard.press('Tab');
  const bodyEl = page.locator('textarea[name="PostingBody"]');
  await bodyEl.click(); await bodyEl.fill(`Test body.

hello@pantrymate.net`);
  await page.keyboard.press('Tab');
  const postalEl = page.locator('input[name="postal"]');
  await postalEl.click(); await postalEl.fill('85001'); await page.keyboard.press('Tab');
  const emailEl = page.locator('input[name="FromEMail"]');
  await emailEl.click(); await emailEl.fill('hello@pantrymate.net'); await page.keyboard.press('Tab');
  await sleep(500);

  await Promise.all([page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(()=>{}), page.locator('button[type="submit"], button[name="go"]').first().click()]);
  await sleep(2000);
  console.log('After form submit:', page.url().split('?s=')[1]);

  // Show bodyemail page
  const html = await page.content();
  const sec = html.indexOf('<section');
  console.log('\n=== CURRENT PAGE SECTION ===');
  console.log(html.substring(sec, sec + 5000));

  console.log('\n=== BUTTONS ===');
  const btns = await page.locator('button, input[type="submit"]').all();
  for (const b of btns) {
    const txt = await b.textContent().catch(() => '');
    const val = await b.getAttribute('value').catch(() => '');
    const name = await b.getAttribute('name').catch(() => '');
    console.log(`  "${txt?.trim()}" val="${val}" name="${name}"`);
  }

  await page.screenshot({ path: '/tmp/cl_bodyemail.png' });

  await browser.close();
})();
