const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    recordVideo: { dir: '/root/.openclaw/workspace/assets/clips/', size: { width: 390, height: 844 } }
  });

  const page = await context.newPage();

  await page.goto('https://pantrymate.net/auth', { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(2000);

  await page.fill('input[type="email"]', 'unitfix.official@gmail.com');
  await page.waitForTimeout(500);
  await page.fill('input[type="password"]', 'Clawable_AI_TEST');
  await page.waitForTimeout(500);

  // Press Enter to submit
  await page.press('input[type="password"]', 'Enter');
  await page.waitForTimeout(5000);

  console.log('URL after login:', page.url());
  await page.screenshot({ path: '/root/.openclaw/workspace/assets/clips/after-login2.png' });

  // Log all buttons on page
  const buttons = await page.$$eval('button', bs => bs.map(b => b.innerText.trim()));
  console.log('Buttons:', buttons);

  await context.close();
  await browser.close();
})();
