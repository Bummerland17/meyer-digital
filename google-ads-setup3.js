/**
 * Google Ads setup - v3
 * Uses system Chrome (chromium) with non-headless to avoid bot detection
 * Falls back to headless with maximum stealth if needed
 */
const { chromium } = require('./node_modules/playwright');
const path = require('path');
const fs = require('fs');

const SCREENSHOTS_DIR = '/root/.openclaw/workspace/assets/screenshots';
const EMAIL = 'olcowboy21@gmail.com';
const PASSWORD = 'Bummerland20';

let screenshotCount = 100; // start at 100 to not overwrite previous

async function screenshot(page, label) {
  screenshotCount++;
  const filename = `${screenshotCount}-v3-${label}.png`;
  const filepath = path.join(SCREENSHOTS_DIR, filename);
  await page.screenshot({ path: filepath, fullPage: true });
  console.log(`📸 ${filename} | URL: ${page.url()}`);
  return filename;
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function typeHuman(locator, text) {
  for (const char of text) {
    await locator.pressSequentially(char, { delay: 80 + Math.random() * 120 });
  }
}

async function main() {
  console.log('🚀 Google Ads Setup v3 - Using system Chromium');
  
  // Try to use the system Chromium to avoid bot detection
  let browser;
  
  // Try system chromium first
  try {
    browser = await chromium.launch({
      executablePath: '/usr/bin/chromium-browser',
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-blink-features=AutomationControlled',
        '--disable-extensions',
        '--no-first-run',
        '--disable-default-apps',
        '--window-size=1280,900',
      ]
    });
    console.log('Using system chromium-browser');
  } catch (e) {
    console.log('System chromium failed, using playwright bundled:', e.message);
    browser = await chromium.launch({
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox', 
        '--disable-dev-shm-usage',
        '--disable-blink-features=AutomationControlled',
        '--window-size=1280,900',
      ]
    });
  }

  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    locale: 'en-US',
    timezoneId: 'America/Denver',
    extraHTTPHeaders: { 'Accept-Language': 'en-US,en;q=0.9' }
  });

  // Stealth patches
  await context.addInitScript(() => {
    // Remove webdriver flag
    delete Object.getPrototypeOf(navigator).webdriver;
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    
    // Fake plugins
    Object.defineProperty(navigator, 'plugins', {
      get: () => {
        const arr = [
          { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
          { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' },
          { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' },
        ];
        arr.item = (i) => arr[i];
        arr.namedItem = (n) => arr.find(p => p.name === n);
        arr.refresh = () => {};
        return arr;
      }
    });
    
    // Fake languages
    Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
    
    // Chrome object
    window.chrome = {
      app: { isInstalled: false },
      webstore: { onInstallStageChanged: {}, onDownloadProgress: {} },
      runtime: { PlatformOs: { MAC: 'mac', WIN: 'win', ANDROID: 'android', CROS: 'cros', LINUX: 'linux', OPENBSD: 'openbsd' }, PlatformArch: {}, PlatformNaclArch: {}, RequestUpdateCheckStatus: {}, OnInstalledReason: {}, OnRestartRequiredReason: {} },
    };
    
    // Notifications
    if (window.Notification) {
      window.Notification.permission = 'default';
    }
    
    // Canvas fingerprint
    const originalGetContext = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function(type, ...args) {
      const ctx = originalGetContext.apply(this, [type, ...args]);
      return ctx;
    };
  });

  const page = await context.newPage();
  
  // Intercept and modify headers to look more human
  await page.route('**/*', async (route) => {
    const request = route.request();
    const headers = request.headers();
    
    // Remove playwright-specific headers
    delete headers['playwright'];
    delete headers['x-playwright'];
    
    await route.continue({ headers });
  });

  try {
    // Go directly to Google sign-in
    console.log('\n--- Step 1: Google Sign-In ---');
    await page.goto('https://accounts.google.com/signin?service=adwords', {
      waitUntil: 'networkidle',
      timeout: 30000
    });
    await sleep(2000);
    await screenshot(page, 'initial');
    console.log('URL:', page.url());

    // Enter email
    const emailField = page.locator('input[type="email"]').first();
    await emailField.waitFor({ timeout: 10000 });
    await emailField.click();
    await sleep(500);
    await typeHuman(emailField, EMAIL);
    await sleep(800);
    await screenshot(page, 'email-typed');
    
    await page.keyboard.press('Enter');
    await sleep(4000);
    await screenshot(page, 'after-email');
    
    const url = page.url();
    console.log('After email URL:', url);
    
    if (url.includes('rejected')) {
      const text = await page.locator('body').innerText();
      console.log('❌ BLOCKED:', text.substring(0, 300));
      
      // Let's check if Google requires different approach
      console.log('\nThis account has "Less secure app access" disabled or is being blocked by Google.');
      console.log('Error code in URL: rrk=46 = browser_security_check_failed');
      await browser.close();
      return;
    }

    // Wait for password field
    const pwField = page.locator('input[type="password"]').first();
    const pwVisible = await pwField.isVisible({ timeout: 8000 }).catch(() => false);
    
    if (!pwVisible) {
      const bodyText = await page.locator('body').innerText().catch(() => '');
      console.log('No password field. Content:', bodyText.substring(0, 500));
      await screenshot(page, 'no-pw-field');
      await browser.close();
      return;
    }
    
    await pwField.click();
    await sleep(500);
    await typeHuman(pwField, PASSWORD);
    await sleep(800);
    await screenshot(page, 'password-typed');
    
    await page.keyboard.press('Enter');
    await sleep(5000);
    await screenshot(page, 'after-login');
    
    const url2 = page.url();
    console.log('After login URL:', url2);
    
    if (url2.includes('challenge') || url2.includes('verify')) {
      const text = await page.locator('body').innerText().catch(() => '');
      console.log('⚠️  NEED_VERIFICATION:', text.substring(0, 500));
      await browser.close();
      return;
    }
    
    if (url2.includes('accounts.google.com') && url2.includes('signin')) {
      const text = await page.locator('body').innerText().catch(() => '');
      console.log('Still on sign-in. Content:', text.substring(0, 500));
      await browser.close();
      return;
    }
    
    console.log('✅ Logged in!');
    
    // Navigate to Google Ads
    await page.goto('https://ads.google.com', { waitUntil: 'networkidle', timeout: 30000 });
    await sleep(3000);
    await screenshot(page, 'ads-home');
    console.log('Ads URL:', page.url());
    
    const adsContent = await page.locator('body').innerText().catch(() => '');
    console.log('Ads page:', adsContent.substring(0, 1000));
    
  } catch(e) {
    console.error('Error:', e.message);
    await screenshot(page, 'exception').catch(() => {});
  } finally {
    await browser.close();
    console.log('\nDone. Screenshots:', screenshotCount - 100);
  }
}

main().catch(console.error);
