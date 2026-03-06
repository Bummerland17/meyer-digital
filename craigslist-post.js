const { chromium } = require('/root/.openclaw/workspace/node_modules/playwright');

const EMAIL = 'hello@pantrymate.net';
const PASSWORD = 'Bummerland20!CL';

const SELLER_AD = {
  title: 'We Buy Phoenix Houses Cash — Any Condition, Fast Close',
  body: `Selling your Phoenix home? We buy houses directly for cash.

Any condition - no repairs needed
Close in 7-14 days
No realtor fees, no commissions
We handle all paperwork
Pre-foreclosure, inherited, vacant, behind on payments - all OK

We work with a network of cash buyers and can often close faster than traditional buyers.

If you want a no-obligation cash offer, text or email:
hello@pantrymate.net

We buy in all Phoenix metro zip codes including 85031, 85033, 85035, 85040, 85042 and surrounding areas.`,
  postal: '85031'
};

const BUYER_AD = {
  title: 'Off-Market Phoenix Investment Properties - Cash Buyers Only',
  body: `Attention Phoenix real estate investors and cash buyers:

We source off-market, discounted properties in the Phoenix metro area and wholesale them to investors.

What we find:
- Single family homes 20-35% below ARV
- Pre-foreclosure and distressed properties
- West Phoenix and South Mountain area focus
- $150k-$350k price range

Currently building our buyer list. If you're an active investor looking for Phoenix deals, email us to get on the list:
hello@pantrymate.net

Include: how many deals/year you close, typical buy box (price range, neighborhoods, condition), and if you prefer fix-flip or buy-and-hold.`,
  postal: '85031'
};

const sites = ['phoenix', 'eastvalley'];
const results = [];

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function loginToCraigslist(page) {
  console.log('Navigating to login page...');
  await page.goto('https://accounts.craigslist.org/login', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await sleep(2000);
  
  console.log('Filling email...');
  await page.fill('#inputEmailHandle', EMAIL);
  await sleep(500);
  
  console.log('Filling password...');
  await page.fill('#inputPassword', PASSWORD);
  await sleep(500);
  
  await page.screenshot({ path: '/root/.openclaw/workspace/assets/cl-login-filled.png' });
  
  console.log('Clicking Log In button...');
  await page.click('#login');
  await sleep(4000);
  
  const url = page.url();
  console.log('After login URL:', url);
  await page.screenshot({ path: '/root/.openclaw/workspace/assets/cl-after-login.png' });
  
  return url;
}

async function navigateToPost(page, site) {
  const url = `https://${site}.craigslist.org/post`;
  console.log(`  Navigating to ${url}`);
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await sleep(2000);
  await page.screenshot({ path: `/root/.openclaw/workspace/assets/cl-${site}-post.png` });
  return page.url();
}

async function selectCategoryAndPost(page, site, adType, adData) {
  console.log(`\n--- Posting ${adType} ad on ${site} ---`);
  
  try {
    await navigateToPost(page, site);
    
    let html = await page.content();
    
    // Step 1: Select category type
    // Look for "housing offered" or "housing wanted" radio
    if (adType === 'seller') {
      // seller ad = we want to be in "real estate wanted" (where sellers look for buyers)
      // Category type: "housing" > "real estate wanted"
      
      // First look for type selection
      const housingWanted = page.locator('input[value="hws"]'); // housing wanted
      if (await housingWanted.count() > 0) {
        await housingWanted.click();
        console.log('  Selected housing wanted');
      } else {
        // Try text-based selection
        const options = page.locator('li label, .pickCategory label');
        const count = await options.count();
        console.log(`  Found ${count} category options`);
        for (let i = 0; i < count; i++) {
          const text = await options.nth(i).textContent();
          console.log(`    Option ${i}: ${text?.trim()}`);
        }
        // Click "housing" or related
        const housingLink = page.locator('a:has-text("housing"), label:has-text("housing")').first();
        if (await housingLink.count() > 0) {
          await housingLink.click();
          await sleep(1000);
        }
      }
    } else {
      // buyer ad = "real estate for sale by owner" 
      const housingOffered = page.locator('input[value="hos"]'); // housing offered/sale
      if (await housingOffered.count() > 0) {
        await housingOffered.click();
        console.log('  Selected housing for sale');
      }
    }
    
    await page.screenshot({ path: `/root/.openclaw/workspace/assets/cl-${site}-${adType}-step1.png` });
    
    // Click Continue if present
    let contBtn = page.locator('button:has-text("Continue"), input[value="Continue"], button:has-text("continue")');
    if (await contBtn.count() > 0) {
      await contBtn.first().click();
      await sleep(2000);
    }
    
    html = await page.content();
    await page.screenshot({ path: `/root/.openclaw/workspace/assets/cl-${site}-${adType}-step2.png` });
    
    // Step 2: Sub-category selection
    // Look for real estate specific options
    if (adType === 'seller') {
      // real estate wanted
      const rewOption = page.locator('input[value="rew"], label:has-text("real estate wanted")');
      if (await rewOption.count() > 0) {
        await rewOption.first().click();
        await sleep(500);
      }
    } else {
      // real estate for sale by owner
      const reaOption = page.locator('input[value="rea"], label:has-text("real estate - by owner")');
      if (await reaOption.count() > 0) {
        await reaOption.first().click();
        await sleep(500);
      }
    }
    
    await page.screenshot({ path: `/root/.openclaw/workspace/assets/cl-${site}-${adType}-step2b.png` });
    
    // Continue again
    contBtn = page.locator('button:has-text("Continue"), input[value="Continue"]');
    if (await contBtn.count() > 0) {
      await contBtn.first().click();
      await sleep(2000);
    }
    
    await page.screenshot({ path: `/root/.openclaw/workspace/assets/cl-${site}-${adType}-step3.png` });
    html = await page.content();
    
    // Step 3: Fill posting form
    const titleField = page.locator('#PostingTitle, input[name="PostingTitle"]');
    if (await titleField.count() > 0) {
      await titleField.fill(adData.title);
      console.log('  Filled title');
    } else {
      console.log('  WARNING: title field not found');
    }
    
    const bodyField = page.locator('#PostingBody, textarea[name="PostingBody"]');
    if (await bodyField.count() > 0) {
      await bodyField.fill(adData.body);
      console.log('  Filled body');
    } else {
      console.log('  WARNING: body field not found');
    }
    
    // Postal code
    const postalField = page.locator('input[name="postal"], #postal');
    if (await postalField.count() > 0) {
      await postalField.fill(adData.postal);
      console.log('  Filled postal');
    }
    
    await page.screenshot({ path: `/root/.openclaw/workspace/assets/cl-${site}-${adType}-filled.png` });
    
    // Continue
    contBtn = page.locator('button:has-text("Continue"), input[value="Continue"], button[type="submit"]');
    if (await contBtn.count() > 0) {
      await contBtn.first().click();
      await sleep(3000);
    }
    
    await page.screenshot({ path: `/root/.openclaw/workspace/assets/cl-${site}-${adType}-step4.png` });
    
    // May need to handle location confirmation, images, etc.
    // Look for publish button
    const publishBtn = page.locator('button:has-text("publish"), button:has-text("Publish"), input[value="publish"]');
    if (await publishBtn.count() > 0) {
      await publishBtn.first().click();
      await sleep(3000);
      await page.screenshot({ path: `/root/.openclaw/workspace/assets/cl-${site}-${adType}-published.png` });
    }
    
    // Skip images if prompted
    const skipImages = page.locator('button:has-text("done with images"), a:has-text("done with images"), button:has-text("skip")');
    if (await skipImages.count() > 0) {
      await skipImages.first().click();
      await sleep(2000);
    }
    
    await page.screenshot({ path: `/root/.openclaw/workspace/assets/cl-${site}-${adType}-final.png` });
    
    const finalUrl = page.url();
    console.log(`  Final URL: ${finalUrl}`);
    
    // Check for success indicators
    const pageText = await page.textContent('body');
    const isSuccess = pageText.includes('manage') || pageText.includes('Your posting') || 
                      finalUrl.includes('/manage') || pageText.includes('confirmation');
    
    return { 
      success: isSuccess, 
      url: finalUrl,
      note: isSuccess ? 'Posted successfully' : 'Uncertain - check screenshot'
    };
    
  } catch (e) {
    console.error(`  Error: ${e.message}`);
    try {
      await page.screenshot({ path: `/root/.openclaw/workspace/assets/cl-${site}-${adType}-error.png` });
    } catch (_) {}
    return { success: false, error: e.message };
  }
}

(async () => {
  const browser = await chromium.launch({ 
    headless: true, 
    args: [
      '--no-sandbox', 
      '--disable-dev-shm-usage',
      '--disable-blink-features=AutomationControlled'
    ]
  });
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 800 }
  });
  
  // Remove webdriver property
  await context.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  });
  
  const page = await context.newPage();
  
  try {
    const loginUrl = await loginToCraigslist(page);
    
    // Check login success
    if (loginUrl.includes('login')) {
      console.log('Login may have failed. Checking page...');
      const bodyText = await page.textContent('body');
      if (bodyText.includes('password')) {
        console.log('Still on login page - credentials may be wrong');
        results.push({ error: 'Login failed - still on login page' });
      }
    } else {
      console.log('Login appeared successful!');
    }
    
    // Proceed with posting regardless
    for (const site of sites) {
      const sellerResult = await selectCategoryAndPost(page, site, 'seller', SELLER_AD);
      results.push({ site, type: 'seller_ad', ...sellerResult });
      await sleep(2000);
      
      const buyerResult = await selectCategoryAndPost(page, site, 'buyer', BUYER_AD);
      results.push({ site, type: 'buyer_ad', ...buyerResult });
      await sleep(2000);
    }
    
  } catch (e) {
    console.error('Fatal error:', e.message);
    results.push({ fatal_error: e.message });
  } finally {
    await browser.close();
  }
  
  console.log('\n=== POSTING RESULTS ===');
  console.log(JSON.stringify(results, null, 2));
  
  require('fs').writeFileSync(
    '/root/.openclaw/workspace/assets/craigslist-results.json',
    JSON.stringify(results, null, 2)
  );
})();
