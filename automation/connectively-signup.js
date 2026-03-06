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
    console.log('🌐 Navigating to connectively.us...');
    await page.goto('https://www.connectively.us', { waitUntil: 'networkidle', timeout: 30000 });
    await screenshot(page, 'connectively-home');
    console.log('Title:', await page.title());
    console.log('URL:', page.url());

    // Look for sign up / source links
    const pageContent = await page.content();
    const links = await page.$$eval('a', els => els.map(e => ({ text: e.textContent?.trim(), href: e.href })));
    console.log('\n🔗 All links on page:');
    links.forEach(l => {
      if (l.text && l.href) console.log(' -', l.text, '->', l.href);
    });

    // Look for "source" or "sign up" buttons/links
    const sourceLink = links.find(l => 
      l.text && (l.text.toLowerCase().includes('source') || l.text.toLowerCase().includes('sign up') || l.text.toLowerCase().includes('register') || l.text.toLowerCase().includes('get started'))
    );
    console.log('\n🎯 Found source/signup link:', sourceLink);

    // Try to find and click the source signup
    let foundSignupPage = false;

    // Try clicking "Sign up as a source" or similar
    const signupSelectors = [
      'text=Sign up as a source',
      'text=Sign Up as a Source',
      'text=Source sign up',
      'text=Become a source',
      'text=Get Started',
      'text=Sign Up',
      'text=Register',
      'a[href*="source"]',
      'a[href*="signup"]',
      'a[href*="register"]',
      'button:has-text("source")',
      'button:has-text("Sign up")',
    ];

    for (const sel of signupSelectors) {
      try {
        const el = await page.$(sel);
        if (el) {
          console.log('✅ Found element:', sel);
          const text = await el.textContent();
          const href = await el.getAttribute('href');
          console.log('   Text:', text, 'Href:', href);
        }
      } catch(e) {}
    }

    // Try direct signup URL patterns
    const signupUrls = [
      'https://www.connectively.us/sign-up',
      'https://www.connectively.us/signup',
      'https://www.connectively.us/register',
      'https://www.connectively.us/auth/sign-up',
      'https://www.connectively.us/source/signup',
      'https://www.connectively.us/sources/signup',
      'https://app.connectively.us/sign-up',
      'https://app.connectively.us/signup',
    ];

    // First check for any "source" related buttons on homepage
    try {
      await page.click('text=Sign up as a source', { timeout: 3000 });
      await sleep(2000);
      await screenshot(page, 'connectively-after-source-click');
      foundSignupPage = true;
      console.log('✅ Clicked "Sign up as a source"');
    } catch(e) {
      console.log('ℹ️ "Sign up as a source" button not found, trying other approaches...');
    }

    if (!foundSignupPage) {
      // Try navigating to common signup URLs
      for (const url of signupUrls) {
        try {
          const response = await page.goto(url, { waitUntil: 'networkidle', timeout: 10000 });
          if (response && response.status() < 400) {
            console.log('✅ Found signup page at:', url);
            await screenshot(page, 'connectively-signup-page');
            foundSignupPage = true;
            break;
          }
        } catch(e) {
          console.log('❌ Failed:', url);
        }
      }
    }

    console.log('\n📄 Current URL:', page.url());
    console.log('📄 Page title:', await page.title());
    
    // Get all form fields
    const inputs = await page.$$eval('input', els => els.map(e => ({
      type: e.type, name: e.name, id: e.id, placeholder: e.placeholder
    })));
    console.log('\n📝 Form inputs found:', JSON.stringify(inputs, null, 2));

    // Get all buttons
    const buttons = await page.$$eval('button, input[type=submit], a[href*="sign"]', els => els.map(e => ({
      tag: e.tagName, text: e.textContent?.trim(), type: e.type, href: e.href
    })));
    console.log('\n🔘 Buttons/submit elements:', JSON.stringify(buttons, null, 2));

    await screenshot(page, 'connectively-final-state');

  } catch (err) {
    console.error('❌ Error:', err.message);
    await screenshot(page, 'connectively-error');
  } finally {
    await browser.close();
  }
})();
