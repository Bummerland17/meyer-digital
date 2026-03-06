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
  
  // Track relevant API calls
  const apiCalls = [];
  page.on('response', async res => {
    const url = res.url();
    if (!url.includes('google') && !url.includes('doubleclick') && !url.includes('analytics')) {
      const status = res.status();
      let body = '';
      try {
        body = await res.text();
      } catch(e) {}
      if (body.length < 2000) {
        apiCalls.push({ url, status, body: body.slice(0, 500) });
      }
    }
  });

  try {
    console.log('=== HARO Email Subscription Signup ===\n');
    
    // Go to sources page
    await page.goto('https://www.helpareporter.com/sources', { waitUntil: 'networkidle', timeout: 30000 });
    await screenshot(page, 'sub-01-sources-page');
    
    // Find and fill the email input in the main form (not the nav)
    // There should be an input[name="email"] 
    const emailInput = await page.waitForSelector('input[name="email"]', { timeout: 10000 });
    console.log('✅ Found email input');
    
    const box = await emailInput.boundingBox();
    console.log('Input position:', box);
    
    await emailInput.click();
    await emailInput.fill('hello@pantrymate.net');
    await sleep(500);
    await screenshot(page, 'sub-02-email-typed');
    console.log('✅ Email filled: hello@pantrymate.net');
    
    // Look for Sign Up button near the email input
    // The button in hero section (not the modal one)
    const allButtons = await page.$$('button');
    let signUpBtn = null;
    
    for (const btn of allButtons) {
      const text = await btn.textContent();
      const btnBox = await btn.boundingBox();
      if (text?.trim().toLowerCase() === 'sign up' && btnBox) {
        // The first visible one should be in the hero section
        console.log(`Sign Up button at y=${btnBox.y?.toFixed(0)}`);
        if (!signUpBtn) {
          signUpBtn = btn;
        }
      }
    }
    
    if (signUpBtn) {
      console.log('Clicking Sign Up button...');
      await signUpBtn.click();
    } else {
      console.log('No Sign Up button found, pressing Enter...');
      await emailInput.press('Enter');
    }
    
    // Wait for response
    await sleep(5000);
    await screenshot(page, 'sub-03-after-submit');
    
    // Check for success messages in the DOM
    const bodyHtml = await page.content();
    const bodyText = await page.textContent('body');
    
    // Success patterns to look for
    const successPatterns = [
      'success', 'subscribed', 'thank you', 'thanks', 'check your email', 
      'verification', 'confirm', 'added', 'welcome', 'signed up',
      'you\'re in', 'you are in', 'great', 'email has been'
    ];
    
    console.log('\n--- Checking for success patterns ---');
    for (const pattern of successPatterns) {
      if (bodyText?.toLowerCase().includes(pattern)) {
        console.log(`✅ Found: "${pattern}"`);
        // Get surrounding context
        const idx = bodyText.toLowerCase().indexOf(pattern);
        console.log('   Context:', bodyText.slice(Math.max(0, idx-50), idx+100));
      }
    }
    
    // Check visible page sections
    console.log('\n--- Visible text sections ---');
    const sections = await page.$$eval('h1, h2, h3, p, [class*="toast"], [class*="alert"], [class*="success"], [role="status"], [role="alert"]', els => 
      els.map(e => e.textContent?.trim()).filter(t => t && t.length > 5 && t.length < 300)
    );
    sections.forEach(s => console.log('  >', s));
    
    // Check for Clerk sign-up option
    console.log('\n\n=== Checking Clerk-based full signup ===');
    await page.goto('https://www.helpareporter.com/sources', { waitUntil: 'networkidle', timeout: 30000 });
    
    // Click Sources dropdown > Sign up
    await page.click('button:has-text("Sources")');
    await sleep(800);
    
    // Click the "Sign up" item in dropdown
    await page.click('text=Sign up', { timeout: 5000 });
    await sleep(2000);
    
    console.log('URL after Sign up click:', page.url());
    await screenshot(page, 'sub-04-clerk-signup');
    
    // Get all form inputs
    const allInputs = await page.$$eval('input', els => els.map(e => ({
      type: e.type, name: e.name, placeholder: e.placeholder, id: e.id,
      class: e.className?.slice(0, 60)
    })));
    console.log('Inputs on signup page:', JSON.stringify(allInputs, null, 2));
    
    const pageText2 = await page.textContent('body');
    console.log('\nPage text (first 500):', pageText2?.slice(0, 500));
    
    // Check if it opened a Clerk auth modal or new page
    const clerkModal = await page.$('.cl-modal, .cl-signUp, [class*="clerk"]');
    if (clerkModal) {
      console.log('✅ Clerk modal found');
      const clerkText = await clerkModal.textContent();
      console.log('Clerk modal text:', clerkText?.slice(0, 300));
    }

    await screenshot(page, 'sub-05-final-state');
    
    console.log('\n=== API calls captured ===');
    apiCalls.forEach(call => {
      if (!call.url.includes('intercom') && !call.url.includes('cloudflare')) {
        console.log(`${call.status} ${call.url}`);
        if (call.body && call.body.length > 0 && !call.body.includes('function')) {
          console.log('  Body:', call.body.slice(0, 200));
        }
      }
    });

  } catch (err) {
    console.error('❌ Error:', err.message);
    await screenshot(page, 'sub-error');
  } finally {
    await browser.close();
  }
})();
