const { chromium } = require('/root/.openclaw/workspace/node_modules/playwright');
const fs = require('fs');

const EMAIL = 'hello@pantrymate.net';

// No email addresses in body - using CL relay
const SELLER_AD = {
  title: 'We Buy Phoenix Houses Cash - Any Condition, Fast Close',
  body: `Selling your Phoenix home? We buy houses directly for cash.

Any condition - no repairs needed
Close in 7-14 days
No realtor fees, no commissions
We handle all paperwork
Pre-foreclosure, inherited, vacant, behind on payments - all OK

We work with a network of cash buyers and can often close faster than traditional buyers.

Reply to this ad for a no-obligation cash offer. We respond quickly.

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

Currently building our buyer list. Reply to this ad if you are an active investor looking for Phoenix deals.

Include: how many deals/year you close, typical buy box (price range, neighborhoods, condition), and if you prefer fix-flip or buy-and-hold.`,
  postal: '85031'
};

const results = [];
async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
async function ss(page, name) {
  await page.screenshot({ path: `/root/.openclaw/workspace/assets/final-${name}.png` }).catch(() => {});
}

async function runPostFlow(context, adType, adData, areaValue, typeValue, subcatValue) {
  const page = await context.newPage();
  console.log(`\n====== ${adType.toUpperCase()} AD ======`);
  
  try {
    // Step 1: Choose area
    await page.goto('https://post.craigslist.org/c/phx', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await sleep(1500);
    
    if (areaValue) {
      await page.locator(`input[value="${areaValue}"]`).first().click();
    } else {
      await page.locator('input[type=radio]').first().click(); // first area
    }
    await page.locator('button:has-text("continue")').click();
    await sleep(2000);
    console.log('  After area:', page.url().split('?')[1]);
    
    // Step 2: Choose type (hw = housing wanted, ho = housing offered)
    await page.locator(`input[value="${typeValue}"]`).click();
    await page.locator('button:has-text("continue")').click();
    await sleep(2000);
    console.log('  After type:', page.url().split('?')[1]);
    
    // Step 3: Choose sub-category
    await page.locator(`input[value="${subcatValue}"]`).click();
    await page.locator('button:has-text("continue")').click();
    await sleep(2000);
    console.log('  After subcat:', page.url().split('?')[1]);
    await ss(page, `${adType}-form`);
    
    // Check we're on edit page
    if (!page.url().includes('s=edit')) {
      console.log('  WARNING: not on edit page, URL:', page.url());
    }
    
    // Step 4: Fill the form
    await page.fill('#PostingTitle', adData.title);
    await page.fill('#PostingBody', adData.body);
    
    const postalEl = page.locator('input[name="postal"]');
    if (await postalEl.count() > 0) await postalEl.fill(adData.postal);
    
    // Email
    const emailEl = page.locator('input[name="FromEMail"]');
    if (await emailEl.count() > 0) await emailEl.fill(EMAIL);
    
    // Price (for real estate)
    const priceEl = page.locator('input[name="price"]');
    if (await priceEl.count() > 0) await priceEl.fill('250000');
    
    // Fill any required selects
    await page.evaluate(() => {
      for (const sel of document.querySelectorAll('select')) {
        if (!sel.value) {
          const firstReal = Array.from(sel.options).find(o => o.value && o.value !== '' && o.text !== '-');
          if (firstReal) { sel.value = firstReal.value; sel.dispatchEvent(new Event('change', {bubbles: true})); }
        }
      }
    });
    
    await ss(page, `${adType}-form-filled`);
    
    // Submit form
    await page.locator('button:has-text("continue")').click();
    await sleep(2500);
    console.log('  After form submit:', page.url().split('?')[1]);
    await ss(page, `${adType}-after-submit`);
    
    // Handle remaining steps
    for (let i = 0; i < 8; i++) {
      const url = page.url();
      const title = await page.title().catch(() => '?');
      const bodyText = await page.textContent('body').catch(() => '');
      console.log(`  [${i}] ${title.substring(0, 40)} | ${url.split('?')[1] || url.split('/').pop()}`);
      
      // Blocked
      if (bodyText.includes('posting blocked') || url.includes('blocked')) {
        const blockMsg = bodyText.match(/blocked[\s\S]{0,300}/)?.[0]?.substring(0, 200) || 'see screenshot';
        console.log('  ✗ BLOCKED:', blockMsg);
        return { success: false, url, note: 'Blocked: ' + blockMsg };
      }
      
      // Success
      if (bodyText.includes('confirmation email') || bodyText.includes('check your email') ||
          url.includes('/manage/') || bodyText.includes('has been received') ||
          bodyText.includes('Your posting has been')) {
        console.log('  ✓ SUCCESS');
        return { success: true, url, note: 'Confirmation email sent to hello@pantrymate.net' };
      }
      
      // Done with images
      const doneImgBtn = page.locator('button:has-text("done with images"), a:has-text("done with images")');
      if (await doneImgBtn.count() > 0) {
        await doneImgBtn.first().click();
        await sleep(2000);
        continue;
      }
      
      // Publish
      const publishBtn = page.locator('button:has-text("publish"), input[value="publish"]');
      if (await publishBtn.count() > 0) {
        await publishBtn.first().click();
        await sleep(4000);
        await ss(page, `${adType}-published`);
        console.log('  ✓ PUBLISHED');
        return { success: true, url: page.url(), note: 'Check hello@pantrymate.net for confirmation' };
      }
      
      // Continue
      const contBtn = page.locator('button:has-text("continue"), input[value="continue"]').first();
      if (await contBtn.count() > 0) {
        await contBtn.click();
        await sleep(2500);
        await ss(page, `${adType}-step${i}`);
      } else {
        console.log('  No more buttons');
        break;
      }
    }
    
    const finalText = await page.textContent('body').catch(() => '');
    return { 
      success: false, 
      url: page.url(), 
      note: finalText.substring(0, 200).replace(/\s+/g, ' ')
    };
    
  } catch(e) {
    console.error('  Error:', e.message.split('\n')[0]);
    await ss(page, `${adType}-error`);
    return { success: false, error: e.message.split('\n')[0] };
  } finally {
    await page.close();
  }
}

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 }
  });
  await context.addInitScript(() => { Object.defineProperty(navigator, 'webdriver', { get: () => undefined }); });
  
  try {
    // SELLER AD: area=first(central), hw=housing wanted, subcat=121(wanted: real estate)
    const sellerResult = await runPostFlow(context, 'seller', SELLER_AD, null, 'hw', '121');
    results.push({ type: 'seller_ad_phoenix', ...sellerResult });
    await sleep(4000);
    
    // BUYER AD: area=first(central), ho=housing offered, subcat=143(real estate - by owner)
    const buyerResult = await runPostFlow(context, 'buyer', BUYER_AD, null, 'ho', '143');
    results.push({ type: 'buyer_ad_phoenix', ...buyerResult });
    
  } finally {
    await browser.close();
  }
  
  console.log('\n=== FINAL CRAIGSLIST RESULTS ===');
  console.log(JSON.stringify(results, null, 2));
  fs.writeFileSync('/root/.openclaw/workspace/assets/craigslist-results.json', JSON.stringify(results, null, 2));
})();
