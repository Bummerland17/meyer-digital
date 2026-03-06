const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();

  // Go to phoenix homepage
  await page.goto('https://phoenix.craigslist.org/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.screenshot({ path: '/tmp/cl_home.png' });
  
  // Find the post link
  const links = await page.locator('a').all();
  for (const l of links) {
    const txt = await l.textContent().catch(() => '');
    const href = await l.getAttribute('href').catch(() => '');
    if (txt.toLowerCase().includes('post') || (href && href.includes('post'))) {
      console.log(`POST LINK: "${txt.trim()}" href="${href}"`);
    }
  }

  // Try clicking the post link
  const postLink = page.locator('a:has-text("post to classifieds"), a[href*="post"]').first();
  console.log('\nTrying to find post link...');
  if (await postLink.count() > 0) {
    const href = await postLink.getAttribute('href');
    console.log('Found post link href:', href);
    await postLink.click();
    await page.waitForLoadState('domcontentloaded');
    console.log('After click URL:', page.url());
    await page.screenshot({ path: '/tmp/cl_after_post_click.png' });
    
    const html = await page.content();
    console.log('\n=== Post page HTML (first 4000 chars) ===');
    console.log(html.substring(0, 4000));
  }

  await browser.close();
})();
