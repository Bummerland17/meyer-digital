const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();

  // Check city codes via their homepages
  const cities = [
    { name: 'Phoenix AZ', home: 'https://phoenix.craigslist.org/' },
    { name: 'Salt Lake City UT', home: 'https://saltlake.craigslist.org/' },
    { name: 'Denver CO', home: 'https://denver.craigslist.org/' },
    { name: 'Boise ID', home: 'https://boise.craigslist.org/' },
    { name: 'Las Vegas NV', home: 'https://lasvegas.craigslist.org/' },
  ];

  for (const c of cities) {
    await page.goto(c.home, { waitUntil: 'domcontentloaded', timeout: 20000 });
    const link = page.locator('a[href*="post.craigslist.org"]').first();
    if (await link.count() > 0) {
      const href = await link.getAttribute('href');
      console.log(`${c.name}: ${href}`);
    }
  }

  // Now explore the posting flow for phoenix
  console.log('\n=== EXPLORING POST FLOW FOR PHOENIX ===');
  await page.goto('https://post.craigslist.org/c/phx', { waitUntil: 'domcontentloaded', timeout: 30000 });
  console.log('URL:', page.url());
  await page.screenshot({ path: '/tmp/cl_post_step1.png' });
  
  const html = await page.content();
  console.log('\nHTML (first 5000 chars):');
  console.log(html.substring(0, 5000));
  
  await browser.close();
})();
