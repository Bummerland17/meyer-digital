const { chromium } = require('playwright');

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();

  await page.goto('https://post.craigslist.org/c/slc', { waitUntil: 'load', timeout: 30000 });
  await sleep(1500);
  console.log('Initial URL:', page.url());

  // Log initial content
  let html = await page.content();
  let sec = html.indexOf('<section');
  console.log('Initial section:');
  console.log(html.substring(sec, sec + 2000));

  // Subarea - select first radio and continue
  const radios = await page.locator('input[type="radio"]').all();
  console.log(`Radios on initial page: ${radios.length}`);
  for (const r of radios) {
    const val = await r.getAttribute('value').catch(() => '');
    const name = await r.getAttribute('name').catch(() => '');
    console.log(`  radio name="${name}" value="${val}"`);
  }

  if (radios.length > 0) {
    await radios[0].check();
  }
  
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {}),
    page.locator('button[name="go"]').first().click()
  ]);
  await sleep(1500);
  console.log('\nAfter subarea:', page.url());

  html = await page.content();
  sec = html.indexOf('<section');
  console.log('Section after subarea (first 3000):');
  console.log(html.substring(sec, sec + 3000));

  // Check for type page
  let bt = await page.textContent('body').catch(() => '');
  if (bt.includes('what type of posting')) {
    console.log('\n→ Found type selection page');
    await page.locator('input[value="so"]').check();
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {}),
      page.locator('button[name="go"]').first().click()
    ]);
    await sleep(1500);
    console.log('After type:', page.url());
    
    html = await page.content();
    sec = html.indexOf('<section');
    console.log('Section after type (first 2000):');
    console.log(html.substring(sec, sec + 2000));
  } else {
    console.log('\n→ No type selection page, checking current page...');
  }

  // Check what radios are available now
  const radios2 = await page.locator('input[name="id"]').all();
  console.log(`\nCategory radios: ${radios2.length}`);
  for (const r of radios2.slice(0, 5)) {
    const val = await r.getAttribute('value').catch(() => '');
    const label = await page.locator(`label:has(input[name="id"][value="${val}"])`).textContent().catch(() => '');
    console.log(`  value="${val}" label="${label.trim()}"`);
  }

  await page.screenshot({ path: '/tmp/cl_slc_debug.png' });
  await browser.close();
})();
