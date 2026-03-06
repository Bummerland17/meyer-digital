const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 390, height: 844 }, // iPhone 14 size — perfect for TikTok
    recordVideo: {
      dir: '/root/.openclaw/workspace/assets/clips/',
      size: { width: 390, height: 844 }
    }
  });

  const page = await context.newPage();

  console.log('Loading pantrymate.net...');
  await page.goto('https://pantrymate.net', { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);

  // Scroll down slowly to show the app
  await page.evaluate(() => window.scrollTo({ top: 300, behavior: 'smooth' }));
  await page.waitForTimeout(2000);
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
  await page.waitForTimeout(2000);

  await context.close();
  await browser.close();
  console.log('Done! Check assets/clips/');
})();
