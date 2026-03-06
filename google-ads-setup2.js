const { chromium } = require('./node_modules/playwright');
const path = require('path');
const fs = require('fs');

const SCREENSHOTS_DIR = '/root/.openclaw/workspace/assets/screenshots';
const EMAIL = 'olcowboy21@gmail.com';
const PASSWORD = 'Bummerland20';

let screenshotCount = 0;

async function screenshot(page, label) {
  screenshotCount++;
  const filename = `${String(screenshotCount).padStart(2, '0')}-${label}.png`;
  const filepath = path.join(SCREENSHOTS_DIR, filename);
  await page.screenshot({ path: filepath, fullPage: true });
  console.log(`📸 Screenshot: ${filename} | URL: ${page.url()}`);
  return filename;
}

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function typeSlowly(locator, text) {
  await locator.click();
  for (const char of text) {
    await locator.pressSequentially(char, { delay: 50 + Math.random() * 100 });
  }
}

async function main() {
  console.log('🚀 Starting Google Ads Campaign Setup for PantryMate (v2 - stealth)');
  
  const browser = await chromium.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-blink-features=AutomationControlled',
      '--disable-features=IsolateOrigins,site-per-process',
      '--window-size=1280,900',
    ]
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    locale: 'en-US',
    timezoneId: 'America/Denver',
    permissions: [],
    extraHTTPHeaders: {
      'Accept-Language': 'en-US,en;q=0.9',
    }
  });

  // Override webdriver detection
  await context.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
    window.chrome = { runtime: {} };
    delete window.__playwright;
    delete window.__pwInitScripts;
  });

  const page = await context.newPage();

  try {
    // Step 1: Go to Google accounts directly with proper flow
    console.log('\n--- Step 1: Navigate to Google Sign-In ---');
    await page.goto('https://accounts.google.com/signin/v2/identifier?service=adwords&hl=en&flowName=GlifWebSignIn&flowEntry=ServiceLogin', { 
      waitUntil: 'networkidle', 
      timeout: 30000 
    });
    await sleep(2000);
    await screenshot(page, 'signin-page-start');
    console.log(`URL: ${page.url()}`);

    // Enter email
    console.log('Entering email...');
    const emailInput = page.locator('#identifierId, input[type="email"]').first();
    await emailInput.waitFor({ timeout: 15000 });
    await emailInput.click();
    await sleep(500);
    await typeSlowly(emailInput, EMAIL);
    await sleep(1000);
    await screenshot(page, 'email-filled');
    
    // Click Next
    const nextBtn = page.locator('#identifierNext, button:has-text("Next")').first();
    await nextBtn.click();
    await sleep(3000);
    await screenshot(page, 'after-email-submit');
    console.log(`URL: ${page.url()}`);

    // Check if we hit the "can't sign you in" page  
    const url1 = page.url();
    if (url1.includes('rejected') || url1.includes('blocked')) {
      await screenshot(page, 'signin-rejected');
      console.log('⚠️  SIGN-IN REJECTED: Google is blocking automated login');
      console.log('URL:', url1);
      const bodyText = await page.locator('body').innerText().catch(() => 'N/A');
      console.log('Page:', bodyText.substring(0, 500));
      await browser.close();
      return;
    }

    // Check for 2FA / challenge
    if (url1.includes('challenge') || url1.includes('verify')) {
      await screenshot(page, 'verification-required');
      const bodyText = await page.locator('body').innerText().catch(() => 'N/A');
      console.log('⚠️  NEED_VERIFICATION:', bodyText.substring(0, 500));
      await browser.close();
      return;
    }

    // Enter password
    console.log('Entering password...');
    const pwInput = page.locator('input[type="password"]').first();
    const pwVisible = await pwInput.isVisible({ timeout: 10000 }).catch(() => false);
    
    if (!pwVisible) {
      console.log('Password field not found. Current URL:', page.url());
      const bodyText = await page.locator('body').innerText().catch(() => 'N/A');
      console.log('Page:', bodyText.substring(0, 1000));
      await screenshot(page, 'no-password-field');
      await browser.close();
      return;
    }

    await pwInput.click();
    await sleep(500);
    await typeSlowly(pwInput, PASSWORD);
    await sleep(1000);
    await screenshot(page, 'password-filled');

    const pwNextBtn = page.locator('#passwordNext, button:has-text("Next")').first();
    await pwNextBtn.click();
    await sleep(5000);
    await screenshot(page, 'after-password-submit');
    console.log(`URL: ${page.url()}`);

    const url2 = page.url();
    
    // Check for various post-login states
    if (url2.includes('challenge') || url2.includes('verify') || url2.includes('signin/v2/challenge')) {
      const bodyText = await page.locator('body').innerText().catch(() => 'N/A');
      console.log('⚠️  NEED_VERIFICATION after password:', bodyText.substring(0, 1000));
      await screenshot(page, 'post-login-verification');
      await browser.close();
      return;
    }

    if (url2.includes('rejected')) {
      const bodyText = await page.locator('body').innerText().catch(() => 'N/A');
      console.log('⚠️  SIGN-IN REJECTED after password:', bodyText.substring(0, 500));
      await browser.close();
      return;
    }

    console.log('✅ Login appears successful! URL:', url2);
    
    // Navigate to Google Ads
    console.log('\n--- Step 2: Navigate to Google Ads ---');
    await page.goto('https://ads.google.com', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await sleep(4000);
    await screenshot(page, 'ads-dashboard');
    console.log(`URL: ${page.url()}`);

    const adsUrl = page.url();
    
    // If still redirected to sign-in
    if (adsUrl.includes('accounts.google.com')) {
      const bodyText = await page.locator('body').innerText().catch(() => 'N/A');
      console.log('Still on auth page:', bodyText.substring(0, 1000));
      await screenshot(page, 'still-auth');
      await browser.close();
      return;
    }

    // Step 3: Look for campaign creation
    console.log('\n--- Step 3: Looking for campaign creation option ---');
    await sleep(2000);
    
    // Take a full screenshot to see the dashboard
    await screenshot(page, 'ads-dashboard-full');
    const dashText = await page.locator('body').innerText().catch(() => 'N/A');
    console.log('Dashboard content:', dashText.substring(0, 2000));

    // Look for new campaign button
    const newCampaignBtns = [
      'button:has-text("New campaign")',
      'a:has-text("New campaign")',
      'button:has-text("+ New campaign")',
      'button:has-text("Create campaign")',
      '[aria-label="New campaign"]',
    ];

    let campaignBtnClicked = false;
    for (const sel of newCampaignBtns) {
      try {
        const el = page.locator(sel).first();
        const vis = await el.isVisible({ timeout: 2000 });
        if (vis) {
          await el.click();
          campaignBtnClicked = true;
          console.log(`Clicked: ${sel}`);
          await sleep(3000);
          break;
        }
      } catch (e) {}
    }

    if (!campaignBtnClicked) {
      // Try navigating to campaign wizard
      console.log('Trying direct campaign URL...');
      await page.goto('https://ads.google.com/aw/campaigns?newCampaign=true', { waitUntil: 'domcontentloaded', timeout: 30000 });
      await sleep(3000);
    }

    await screenshot(page, 'campaign-creation-page');
    console.log(`URL: ${page.url()}`);
    const campText = await page.locator('body').innerText().catch(() => 'N/A');
    console.log('Campaign creation page:', campText.substring(0, 2000));

    // Step 4: Select goal - Website traffic
    console.log('\n--- Step 4: Select Campaign Goal ---');
    
    const goalSelectors = [
      'div:has-text("Website traffic"):not(:has(div))',
      'label:has-text("Website traffic")',
      '[data-automation-id*="traffic"]',
      'div[role="radio"]:has-text("Website traffic")',
    ];
    
    let goalClicked = false;
    for (const sel of goalSelectors) {
      try {
        const el = page.locator(sel).first();
        const vis = await el.isVisible({ timeout: 2000 });
        if (vis) {
          await el.click();
          goalClicked = true;
          console.log(`Clicked goal: ${sel}`);
          break;
        }
      } catch (e) {}
    }

    await sleep(1000);
    await screenshot(page, 'goal-selection');

    // Continue button
    const cont1 = page.locator('button:has-text("Continue"), button:has-text("Next"), [data-automation-id="continue"]').first();
    try {
      const vis = await cont1.isVisible({ timeout: 3000 });
      if (vis) {
        await cont1.click();
        await sleep(3000);
      }
    } catch (e) {}

    await screenshot(page, 'after-goal');
    console.log(`URL: ${page.url()}`);

    // Step 5: Select Search campaign type
    console.log('\n--- Step 5: Select Campaign Type (Search) ---');
    
    const searchSelectors = [
      'div[data-e2e-id*="search"]',
      'label:has-text("Search")',
      'div:has-text("Search ads"):not(:has(div:has-text("Search ads")))',
      'button:has-text("Search")',
    ];
    
    for (const sel of searchSelectors) {
      try {
        const el = page.locator(sel).first();
        const vis = await el.isVisible({ timeout: 2000 });
        if (vis) {
          await el.click();
          console.log(`Selected type: ${sel}`);
          break;
        }
      } catch (e) {}
    }

    await sleep(1000);
    await screenshot(page, 'campaign-type');

    const cont2 = page.locator('button:has-text("Continue"), button:has-text("Next")').first();
    try {
      const vis = await cont2.isVisible({ timeout: 3000 });
      if (vis) {
        await cont2.click();
        await sleep(3000);
      }
    } catch (e) {}

    await screenshot(page, 'after-type');
    console.log(`URL: ${page.url()}`);
    const typeText = await page.locator('body').innerText().catch(() => 'N/A');
    console.log('After type selection:', typeText.substring(0, 1000));

    console.log('\n--- Final status ---');
    console.log('URL:', page.url());
    await screenshot(page, 'end-state');

  } catch (error) {
    console.error('Error:', error.message);
    try {
      await screenshot(page, 'error-state');
      console.log('Error URL:', page.url());
      const bodyText = await page.locator('body').innerText().catch(() => 'N/A');
      console.log('Error page:', bodyText.substring(0, 1000));
    } catch (e2) {}
  } finally {
    await browser.close();
    console.log('\n✅ Done. Total screenshots:', screenshotCount);
    console.log('Screenshots at:', SCREENSHOTS_DIR);
  }
}

main().catch(console.error);
