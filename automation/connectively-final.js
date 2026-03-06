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
  
  // Track network requests
  page.on('request', req => {
    if (req.url().includes('subscribe') || req.url().includes('email') || req.url().includes('signup')) {
      console.log('🌐 Request:', req.method(), req.url());
    }
  });
  
  page.on('response', async res => {
    if (res.url().includes('subscribe') || res.url().includes('email') || res.url().includes('signup') || res.url().includes('api')) {
      console.log('📥 Response:', res.status(), res.url());
      try {
        const text = await res.text();
        console.log('   Body:', text.slice(0, 300));
      } catch(e) {}
    }
  });

  try {
    console.log('🌐 Going to sources page...');
    await page.goto('https://www.helpareporter.com/sources', { waitUntil: 'networkidle', timeout: 30000 });
    await screenshot(page, 'sources-page');
    console.log('Title:', await page.title());
    
    // Check for modal/dialog
    const modalEl = await page.$('[role="dialog"]');
    if (modalEl) {
      console.log('✅ Modal detected on sources page');
      await screenshot(page, 'sources-modal');
      
      // Fill email in modal
      const emailInput = await page.$('[role="dialog"] input, input[name="email"]');
      if (emailInput) {
        await emailInput.fill('hello@pantrymate.net');
        await sleep(500);
        console.log('Email filled in modal');
        await screenshot(page, 'sources-modal-filled');
        
        // Click Sign Up in modal
        const signUpBtn = await page.$('[role="dialog"] button:has-text("Sign Up"), [role="dialog"] button:has-text("Sign up")');
        if (signUpBtn) {
          await signUpBtn.click();
          await sleep(5000);
          await screenshot(page, 'sources-modal-submitted');
          console.log('Submitted! URL:', page.url());
        }
      }
    }

    // Also try the main page approach
    console.log('\n📧 Trying homepage email form...');
    await page.goto('https://www.helpareporter.com', { waitUntil: 'networkidle', timeout: 30000 });
    
    // Find all email inputs and check which section they're in
    const emailInputs = await page.$$('input[type="text"][name="email"], input[type="email"]');
    console.log('Found', emailInputs.length, 'email inputs');
    
    for (let i = 0; i < emailInputs.length; i++) {
      const box = await emailInputs[i].boundingBox();
      const placeholder = await emailInputs[i].getAttribute('placeholder');
      console.log(`Input ${i}: box=${JSON.stringify(box)}, placeholder="${placeholder}"`);
    }
    
    // Use the second email input (the one in the main hero section, not nav)
    // Or try different inputs
    if (emailInputs.length > 0) {
      // Try first input - scroll to it first
      const targetInput = emailInputs[0];
      await targetInput.scrollIntoViewIfNeeded();
      await targetInput.click();
      await targetInput.fill('hello@pantrymate.net');
      await sleep(500);
      await screenshot(page, 'homepage-email-filled');
      
      // Look for the adjacent Sign Up button
      // The nav Sign Up button is bg-gray-700, the hero one might be different
      const btns = await page.$$('button');
      for (const btn of btns) {
        const text = await btn.textContent();
        const cls = await btn.getAttribute('class');
        const box = await btn.boundingBox();
        if (text?.toLowerCase().includes('sign')) {
          console.log(`Sign btn: "${text?.trim()}" y=${box?.y?.toFixed(0)}`);
        }
      }
      
      // Press Enter to submit
      await targetInput.press('Enter');
      await sleep(5000);
      
      // Check for success/toast/message
      const bodyText = await page.textContent('body');
      const successPatterns = ['success', 'subscribed', 'thank you', 'check your email', 'confirmation', 'added', 'welcome'];
      const found = successPatterns.filter(p => bodyText?.toLowerCase().includes(p));
      console.log('Success patterns found:', found);
      
      await screenshot(page, 'homepage-after-submit-final');
      
      // Check for toast notifications
      const toasts = await page.$$('[class*="toast"], [role="status"], [role="alert"], [class*="notification"]');
      for (const toast of toasts) {
        const text = await toast.textContent();
        console.log('Toast/notification:', text?.slice(0, 200));
      }
    }

    // Try to also check featured.com/alerts for a more complete signup
    console.log('\n🔗 Checking featured.com/alerts...');
    await page.goto('https://featured.com/alerts', { waitUntil: 'networkidle', timeout: 30000 });
    await screenshot(page, 'featured-alerts');
    console.log('Featured alerts URL:', page.url());
    console.log('Title:', await page.title());
    
    const featuredInputs = await page.$$eval('input', els => els.map(e => ({
      type: e.type, name: e.name, placeholder: e.placeholder
    })));
    console.log('Inputs on featured.com/alerts:', featuredInputs);

  } catch (err) {
    console.error('❌ Error:', err.message);
    console.error(err.stack);
    await screenshot(page, 'error-final');
  } finally {
    await browser.close();
  }
})();
