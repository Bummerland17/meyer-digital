const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();

  // Go to the Phoenix post page
  await page.goto('https://phoenix.craigslist.org/post', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.screenshot({ path: '/tmp/cl_debug_step1.png' });
  
  const html = await page.content();
  console.log('=== STEP 1 HTML (first 3000 chars) ===');
  console.log(html.substring(0, 3000));
  
  console.log('\n=== URL ===', page.url());
  
  // Check all input elements
  const inputs = await page.locator('input').all();
  console.log(`\nFound ${inputs.length} input elements`);
  for (const inp of inputs) {
    const name = await inp.getAttribute('name').catch(() => '');
    const id = await inp.getAttribute('id').catch(() => '');
    const type = await inp.getAttribute('type').catch(() => '');
    const value = await inp.getAttribute('value').catch(() => '');
    console.log(`  input name="${name}" id="${id}" type="${type}" value="${value}"`);
  }

  // Check all links
  const links = await page.locator('a, label').all();
  console.log(`\nFound ${links.length} links/labels`);
  for (const l of links.slice(0, 30)) {
    const txt = await l.textContent().catch(() => '');
    const href = await l.getAttribute('href').catch(() => '');
    console.log(`  "${txt.trim()}" href="${href}"`);
  }

  await browser.close();
})();
