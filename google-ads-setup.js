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

async function main() {
  console.log('🚀 Starting Google Ads Campaign Setup for PantryMate');
  
  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });

  const page = await context.newPage();

  try {
    // Step 1: Go to Google Ads
    console.log('\n--- Step 1: Navigate to ads.google.com ---');
    await page.goto('https://ads.google.com', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await sleep(2000);
    await screenshot(page, 'ads-homepage');
    console.log(`URL: ${page.url()}`);

    // Step 2: Sign in
    console.log('\n--- Step 2: Sign In ---');
    
    // Look for sign-in button
    const signInBtn = page.locator('a:has-text("Sign in"), button:has-text("Sign in"), a:has-text("Get started")').first();
    const btnVisible = await signInBtn.isVisible().catch(() => false);
    
    if (btnVisible) {
      await signInBtn.click();
      await sleep(2000);
    } else {
      // Maybe already redirected to sign-in page
      await page.goto('https://accounts.google.com/signin/v2/identifier?service=adwords', { waitUntil: 'domcontentloaded', timeout: 30000 });
      await sleep(2000);
    }
    
    await screenshot(page, 'signin-page');
    console.log(`URL: ${page.url()}`);

    // Enter email
    const emailInput = page.locator('input[type="email"], input[name="identifier"]').first();
    await emailInput.waitFor({ timeout: 15000 });
    await emailInput.fill(EMAIL);
    await screenshot(page, 'email-entered');
    
    // Click Next
    await page.keyboard.press('Enter');
    await sleep(3000);
    await screenshot(page, 'after-email-next');
    console.log(`URL: ${page.url()}`);

    // Check for verification prompt
    const pageContent = await page.content();
    if (pageContent.includes('phone') || pageContent.includes('verify') || pageContent.includes('2-Step') || pageContent.includes('verification')) {
      await screenshot(page, 'verification-prompt');
      console.log('⚠️  NEED_VERIFICATION: Phone verification or 2FA detected');
      console.log('Page text:', await page.locator('body').innerText().catch(() => 'N/A'));
      await browser.close();
      return;
    }

    // Enter password
    const passwordInput = page.locator('input[type="password"], input[name="password"], input[name="Passwd"]').first();
    const pwVisible = await passwordInput.isVisible({ timeout: 10000 }).catch(() => false);
    
    if (pwVisible) {
      await passwordInput.fill(PASSWORD);
      await screenshot(page, 'password-entered');
      await page.keyboard.press('Enter');
      await sleep(4000);
    }
    
    await screenshot(page, 'after-signin');
    console.log(`URL: ${page.url()}`);

    // Check for 2FA / verification
    const url = page.url();
    const content = await page.content();
    
    if (url.includes('challenge') || url.includes('verify') || url.includes('signin/v2/challenge') || 
        content.includes('2-Step Verification') || content.includes('phone number') || 
        content.includes('Verify it') || content.includes('verification code')) {
      await screenshot(page, 'need-verification');
      console.log('⚠️  NEED_VERIFICATION: 2FA/Challenge detected');
      console.log('URL:', url);
      const bodyText = await page.locator('body').innerText().catch(() => 'N/A');
      console.log('Page content:', bodyText.substring(0, 1000));
      await browser.close();
      return;
    }

    // Wait for redirect to ads dashboard
    console.log('\n--- Step 3: Navigate to Google Ads Dashboard ---');
    
    // May need to navigate to ads.google.com after sign in
    if (!url.includes('ads.google.com')) {
      await page.goto('https://ads.google.com', { waitUntil: 'domcontentloaded', timeout: 30000 });
      await sleep(3000);
    }
    
    await screenshot(page, 'ads-dashboard');
    console.log(`URL: ${page.url()}`);
    
    // Check again for verification
    const adsUrl = page.url();
    const adsContent = await page.content();
    if (adsUrl.includes('accounts.google.com') || adsContent.includes('verify') || adsContent.includes('Verify')) {
      if (adsUrl.includes('challenge') || adsContent.includes('2-Step')) {
        await screenshot(page, 'verification-required');
        console.log('⚠️  NEED_VERIFICATION: Verification required before accessing Google Ads');
        console.log('URL:', adsUrl);
        const bodyText = await page.locator('body').innerText().catch(() => 'N/A');
        console.log('Page content:', bodyText.substring(0, 1000));
        await browser.close();
        return;
      }
    }

    // Look for "New campaign" button or similar
    console.log('\n--- Step 4: Start New Campaign ---');
    
    // Wait a bit for the page to fully load
    await sleep(3000);
    await screenshot(page, 'pre-new-campaign');
    
    // Try different selectors for new campaign button
    const newCampaignSelectors = [
      'a:has-text("New campaign")',
      'button:has-text("New campaign")',
      'button:has-text("+ New campaign")',
      '[data-text="New campaign"]',
      'a[href*="newcampaign"]',
      'button:has-text("Create")',
      'a:has-text("Create campaign")',
    ];
    
    let clicked = false;
    for (const sel of newCampaignSelectors) {
      const el = page.locator(sel).first();
      const vis = await el.isVisible({ timeout: 2000 }).catch(() => false);
      if (vis) {
        await el.click();
        clicked = true;
        console.log(`Clicked: ${sel}`);
        break;
      }
    }
    
    if (!clicked) {
      // Try navigating directly to campaign creation
      console.log('No new campaign button found, trying direct navigation...');
      await page.goto('https://ads.google.com/aw/campaigns/new/web', { waitUntil: 'domcontentloaded', timeout: 30000 });
      await sleep(3000);
    }
    
    await sleep(3000);
    await screenshot(page, 'campaign-creation-start');
    console.log(`URL: ${page.url()}`);

    // Step 5: Select campaign goal
    console.log('\n--- Step 5: Select Campaign Goal ---');
    
    // Look for "Website traffic" or "Sales" goal
    const goalSelectors = [
      'div:has-text("Website traffic")',
      'label:has-text("Website traffic")',
      'span:has-text("Website traffic")',
      'div:has-text("Sales")',
    ];
    
    for (const sel of goalSelectors) {
      const el = page.locator(sel).first();
      const vis = await el.isVisible({ timeout: 2000 }).catch(() => false);
      if (vis) {
        await el.click();
        console.log(`Selected goal: ${sel}`);
        break;
      }
    }
    
    await sleep(2000);
    await screenshot(page, 'goal-selected');
    
    // Look for "Continue" button
    const continueBtn = page.locator('button:has-text("Continue"), button:has-text("Next")').first();
    const contVis = await continueBtn.isVisible({ timeout: 3000 }).catch(() => false);
    if (contVis) {
      await continueBtn.click();
      await sleep(3000);
    }
    
    await screenshot(page, 'after-goal-continue');
    console.log(`URL: ${page.url()}`);

    // Step 6: Select campaign type (Search)
    console.log('\n--- Step 6: Select Campaign Type ---');
    
    const searchTypeSelectors = [
      'div:has-text("Search")',
      'label:has-text("Search")',
      '[data-text="Search"]',
    ];
    
    for (const sel of searchTypeSelectors) {
      const el = page.locator(sel).first();
      const vis = await el.isVisible({ timeout: 2000 }).catch(() => false);
      if (vis) {
        await el.click();
        console.log(`Selected campaign type: ${sel}`);
        break;
      }
    }
    
    await sleep(2000);
    await screenshot(page, 'campaign-type-selected');
    
    // Continue
    const cont2 = page.locator('button:has-text("Continue"), button:has-text("Next")').first();
    const cont2Vis = await cont2.isVisible({ timeout: 3000 }).catch(() => false);
    if (cont2Vis) {
      await cont2.click();
      await sleep(3000);
    }
    
    await screenshot(page, 'after-type-continue');
    console.log(`URL: ${page.url()}`);

    // Step 7: Enter website URL
    console.log('\n--- Step 7: Enter Website URL ---');
    
    const urlInput = page.locator('input[type="url"], input[placeholder*="website"], input[placeholder*="URL"], input[name*="url"]').first();
    const urlVis = await urlInput.isVisible({ timeout: 5000 }).catch(() => false);
    if (urlVis) {
      await urlInput.fill('https://pantrymate.net');
      console.log('Entered website URL: https://pantrymate.net');
    }
    
    await sleep(1000);
    await screenshot(page, 'website-url-entered');
    
    const cont3 = page.locator('button:has-text("Continue"), button:has-text("Next")').first();
    const cont3Vis = await cont3.isVisible({ timeout: 3000 }).catch(() => false);
    if (cont3Vis) {
      await cont3.click();
      await sleep(3000);
    }
    
    await screenshot(page, 'after-url-continue');
    console.log(`URL: ${page.url()}`);

    // Save full page state  
    console.log('\n--- Full page text dump ---');
    const fullText = await page.locator('body').innerText().catch(() => 'N/A');
    console.log(fullText.substring(0, 2000));
    
    // Step 8: Campaign name
    console.log('\n--- Step 8: Campaign Name ---');
    
    const nameInput = page.locator('input[placeholder*="campaign name"], input[name*="name"], input[aria-label*="Campaign name"]').first();
    const nameVis = await nameInput.isVisible({ timeout: 5000 }).catch(() => false);
    if (nameVis) {
      await nameInput.clear();
      await nameInput.fill('PantryMate Lifetime Deal');
      console.log('Entered campaign name');
    }
    
    await sleep(1000);
    await screenshot(page, 'campaign-named');

    console.log('\n--- Reached end of automated steps ---');
    console.log('Final URL:', page.url());
    
    // Final screenshot
    await screenshot(page, 'final-state');
    
  } catch (error) {
    console.error('Error:', error.message);
    await screenshot(page, 'error-state').catch(() => {});
    console.log('Current URL:', page.url());
    const bodyText = await page.locator('body').innerText().catch(() => 'N/A');
    console.log('Page content:', bodyText.substring(0, 2000));
  } finally {
    await browser.close();
    console.log('\n✅ Browser closed. Screenshots saved to:', SCREENSHOTS_DIR);
    console.log('Total screenshots:', screenshotCount);
  }
}

main().catch(console.error);
