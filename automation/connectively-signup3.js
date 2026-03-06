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

  // Listen for any navigation or popups
  page.on('dialog', async dialog => {
    console.log('Dialog:', dialog.type(), dialog.message());
    await dialog.accept();
  });

  try {
    console.log('🌐 Navigating to helpareporter.com...');
    await page.goto('https://www.helpareporter.com', { waitUntil: 'networkidle', timeout: 30000 });
    
    // Step 1: Click Sources dropdown then Sign up
    console.log('\n🔽 Step 1: Click Sources dropdown...');
    await page.click('button:has-text("Sources")');
    await sleep(1000);
    await screenshot(page, 'step1-sources-dropdown-open');
    
    // Find and click "Sign up" in the dropdown (the first one listed under Sources)
    // It appears as a block button with specific class
    const signupButtons = await page.$$('button:has-text("Sign up")');
    console.log('Found', signupButtons.length, 'Sign up buttons');
    
    // The first Sign up button (small one under Sources dropdown)
    if (signupButtons.length > 0) {
      console.log('Clicking first Sign up button in dropdown...');
      await signupButtons[0].click();
      await sleep(2000);
      await screenshot(page, 'step2-after-signup-click');
      console.log('URL after click:', page.url());
    }

    // Check if a modal appeared
    const modalContent = await page.$('[role="dialog"], .modal, [class*="modal"], [class*="dialog"]');
    if (modalContent) {
      console.log('Modal found!');
      const modalText = await modalContent.textContent();
      console.log('Modal text:', modalText?.slice(0, 500));
    }

    // Look for the email input form
    const inputs = await page.$$eval('input', els => els.map(e => ({
      type: e.type, name: e.name, id: e.id, placeholder: e.placeholder, visible: e.offsetParent !== null
    })));
    console.log('\nInputs:', JSON.stringify(inputs, null, 2));

    // The main email signup approach: fill email in the top form
    // Navigate fresh
    await page.goto('https://www.helpareporter.com', { waitUntil: 'networkidle', timeout: 30000 });
    
    console.log('\n📧 Step 2: Fill main email form...');
    const emailInput = await page.$('input[placeholder*="email" i], input[type="email"]');
    if (emailInput) {
      await emailInput.click();
      await emailInput.fill('hello@pantrymate.net');
      await sleep(500);
      await screenshot(page, 'step3-email-filled');
      console.log('Email filled, looking for Sign Up button...');
      
      // Find and click the Sign Up button next to the email input
      // The button with bg-gray-700 class is in the nav, the one with bg-black is in the hero
      const signUpBtn = await page.$('button.bg-gray-700');
      if (signUpBtn) {
        console.log('Found Sign Up button with bg-gray-700');
        await signUpBtn.click();
      } else {
        // Try pressing Enter
        await emailInput.press('Enter');
      }
      
      await sleep(3000);
      await screenshot(page, 'step4-after-submit');
      console.log('URL after submit:', page.url());
      
      // Check for any response
      const pageText = await page.textContent('body');
      console.log('\nPage text after submit (first 1000 chars):');
      console.log(pageText?.slice(0, 1000));
    } else {
      console.log('No email input found!');
    }

    // Also try the full-page Sign Up button (the one in the CTA section)
    await page.goto('https://www.helpareporter.com', { waitUntil: 'networkidle', timeout: 30000 });
    console.log('\n📋 Inspecting all Sign Up buttons...');
    
    const allButtons = await page.$$('button');
    for (let i = 0; i < allButtons.length; i++) {
      const text = await allButtons[i].textContent();
      const cls = await allButtons[i].getAttribute('class');
      if (text?.toLowerCase().includes('sign')) {
        const box = await allButtons[i].boundingBox();
        console.log(`Button ${i}: "${text?.trim()}" class="${cls?.slice(0, 80)}" box=${JSON.stringify(box)}`);
      }
    }

  } catch (err) {
    console.error('❌ Error:', err.message);
    console.error(err.stack);
    await screenshot(page, 'haro-error');
  } finally {
    await browser.close();
  }
})();
