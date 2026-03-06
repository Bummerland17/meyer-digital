const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const SCREENSHOTS_DIR = '/root/.openclaw/workspace/automation/screenshots';
fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function screenshot(page, name) {
  const p = path.join(SCREENSHOTS_DIR, name + '.png');
  await page.screenshot({ path: p, fullPage: true });
  console.log('📸 Screenshot:', p);
  return p;
}

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 }
  });

  const page = await context.newPage();

  try {
    console.log('🌐 Navigating to helpareporter.com...');
    await page.goto('https://www.helpareporter.com', { waitUntil: 'networkidle', timeout: 30000 });
    await screenshot(page, 'haro-home');
    console.log('URL:', page.url());

    // Click the Sources dropdown button
    console.log('\n🔽 Clicking Sources dropdown...');
    try {
      await page.click('button:has-text("Sources")', { timeout: 5000 });
      await sleep(1000);
      await screenshot(page, 'haro-sources-dropdown');
      
      // Get dropdown content
      const dropdownLinks = await page.$$eval('a, button', els => els.map(e => ({
        tag: e.tagName,
        text: e.textContent?.trim(),
        href: e.href || null
      })));
      console.log('Dropdown items:', dropdownLinks.filter(l => l.text));
    } catch(e) {
      console.log('Sources dropdown click failed:', e.message);
    }

    // Also check the email signup field
    console.log('\n📧 Checking email signup field...');
    const emailInput = await page.$('input[type="email"], input[placeholder*="email" i]');
    if (emailInput) {
      console.log('Found email input!');
      const placeholder = await emailInput.getAttribute('placeholder');
      console.log('Placeholder:', placeholder);
    }

    // Get ALL links and buttons
    const allLinks = await page.$$eval('a[href], button', els => els.map(e => ({
      tag: e.tagName,
      text: e.textContent?.trim(),
      href: e.getAttribute('href') || null
    })));
    console.log('\nAll links/buttons:');
    allLinks.forEach(l => {
      if (l.text) console.log(` ${l.tag}: "${l.text}" -> ${l.href}`);
    });

    // Try clicking Sources dropdown and get sub-menu
    await page.goto('https://www.helpareporter.com', { waitUntil: 'networkidle', timeout: 30000 });
    
    // Try hovering over Sources
    try {
      await page.hover('button:has-text("Sources")', { timeout: 5000 });
      await sleep(500);
      await screenshot(page, 'haro-sources-hover');
    } catch(e) {}

    // Check for any popup/modal after click
    try {
      await page.click('button:has-text("Sources")', { timeout: 5000 });
      await sleep(1500);
      
      // Get visible dropdown items
      const visibleLinks = await page.$$eval('a:visible, button:visible', els => els.map(e => ({
        text: e.textContent?.trim(),
        href: e.getAttribute('href') || null,
        class: e.className
      })));
      console.log('\nVisible after Sources click:', visibleLinks.filter(l => l.text));
      await screenshot(page, 'haro-after-sources-click');
    } catch(e) {
      console.log('Error:', e.message);
    }

    // Try the page HTML for any signup-related content
    const html = await page.content();
    const signupMatches = html.match(/sign.?up|register|source.{0,50}(?:sign|join|start)/gi);
    console.log('\nSignup-related HTML matches:', signupMatches?.slice(0, 20));

  } catch (err) {
    console.error('❌ Error:', err.message);
    await screenshot(page, 'haro-error');
  } finally {
    await browser.close();
  }
})();
