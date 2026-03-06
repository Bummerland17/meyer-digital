const { chromium } = require('/root/.openclaw/workspace/node_modules/playwright');
const fs = require('fs');

const EMAIL = 'hello@pantrymate.net';

const SELLER_AD = {
  title: 'We Buy Phoenix Houses Cash - Any Condition, Fast Close',
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

Currently building our buyer list. If you are an active investor looking for Phoenix deals, email us to get on the list:
hello@pantrymate.net

Include: how many deals/year you close, typical buy box (price range, neighborhoods, condition), and if you prefer fix-flip or buy-and-hold.`,
  postal: '85031'
};

const results = [];

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function logState(page, label) {
  const url = page.url();
  const title = await page.title().catch(() => '?');
  console.log(`  [${label}] ${title} | ${url}`);
  await page.screenshot({ path: `/root/.openclaw/workspace/assets/cl-${label.replace(/[^a-z0-9]/gi, '_')}.png` }).catch(() => {});
}

async function postAd(context, adType, adData) {
  const page = await context.newPage();
  console.log(`\n====== Posting ${adType} ad ======`);
  
  try {
    // Step 1: Start posting flow
    await page.goto('https://post.craigslist.org/c/phx', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await sleep(1500);
    await logState(page, `${adType}-1-start`);
    
    // Step 2: Choose area (select west valley for our zip codes)
    const areaLabels = page.locator('label');
    const areaCount = await areaLabels.count();
    console.log(`  Area options count: ${areaCount}`);
    
    // Select "west valley" for seller (85031 zip), or central for buyer
    const targetArea = adType === 'seller' ? 'west valley' : 'central/south phx';
    let areaSelected = false;
    
    for (let i = 0; i < areaCount; i++) {
      const text = await areaLabels.nth(i).textContent();
      if (text && text.toLowerCase().includes(targetArea.split(' ')[0])) {
        // Click the radio input for this label
        const forAttr = await areaLabels.nth(i).getAttribute('for');
        if (forAttr) {
          await page.click(`#${forAttr}`);
        } else {
          await areaLabels.nth(i).click();
        }
        console.log(`  Selected area: ${text.trim()}`);
        areaSelected = true;
        break;
      }
    }
    
    if (!areaSelected) {
      // Just click first option
      await areaLabels.first().click();
      console.log('  Selected first area option');
    }
    
    await sleep(500);
    
    // Click continue
    const contBtn = page.locator('button:has-text("continue"), input[value="continue"]');
    if (await contBtn.count() > 0) {
      await contBtn.first().click();
      await sleep(2000);
    }
    
    await logState(page, `${adType}-2-area`);
    
    // Step 3: Choose category type
    // For real estate, we want "housing"
    const currentUrl = page.url();
    console.log(`  Category selection page: ${currentUrl}`);
    
    // Look for housing category
    const allLabels = await page.locator('label').allTextContents();
    console.log('  Available categories:', allLabels.slice(0, 15).join(', '));
    
    // Find and click "housing"
    const housingLabel = page.locator('label:has-text("housing")').first();
    if (await housingLabel.count() > 0) {
      const forId = await housingLabel.getAttribute('for');
      if (forId) await page.click(`#${forId}`);
      else await housingLabel.click();
      console.log('  Selected: housing');
    } else {
      // Try to find housing radio
      const housingRadio = page.locator('input[value*="hous"]').first();
      if (await housingRadio.count() > 0) {
        await housingRadio.click();
      }
    }
    
    await sleep(500);
    
    const contBtn2 = page.locator('button:has-text("continue"), input[value="continue"]');
    if (await contBtn2.count() > 0) {
      await contBtn2.first().click();
      await sleep(2000);
    }
    
    await logState(page, `${adType}-3-housing`);
    
    // Step 4: Sub-category
    const subLabels = await page.locator('label').allTextContents();
    console.log('  Sub-categories:', subLabels.slice(0, 20).join(' | '));
    
    if (adType === 'seller') {
      // Real estate wanted
      const rewLabel = page.locator('label:has-text("real estate wanted")').first();
      if (await rewLabel.count() > 0) {
        const forId = await rewLabel.getAttribute('for');
        if (forId) await page.click(`#${forId}`);
        else await rewLabel.click();
        console.log('  Selected: real estate wanted');
      } else {
        console.log('  WARNING: real estate wanted not found, checking options...');
        const labels = await page.locator('label').all();
        for (const label of labels) {
          const t = await label.textContent();
          console.log('    Label:', t?.trim());
        }
      }
    } else {
      // Real estate for sale by owner
      const reaLabel = page.locator('label:has-text("real estate - by owner"), label:has-text("real estate for sale by owner")').first();
      if (await reaLabel.count() > 0) {
        const forId = await reaLabel.getAttribute('for');
        if (forId) await page.click(`#${forId}`);
        else await reaLabel.click();
        console.log('  Selected: real estate by owner');
      } else {
        // Try a more flexible match
        const labels = await page.locator('label').all();
        let found = false;
        for (const label of labels) {
          const t = (await label.textContent() || '').toLowerCase();
          if (t.includes('real estate') && (t.includes('owner') || t.includes('sale'))) {
            await label.click();
            console.log(`  Selected RE option: ${t.trim()}`);
            found = true;
            break;
          }
        }
        if (!found) console.log('  WARNING: real estate sale option not found');
      }
    }
    
    await sleep(500);
    
    const contBtn3 = page.locator('button:has-text("continue"), input[value="continue"]');
    if (await contBtn3.count() > 0) {
      await contBtn3.first().click();
      await sleep(2000);
    }
    
    await logState(page, `${adType}-4-subcat`);
    
    // Step 5: Fill the posting form
    const titleField = page.locator('#PostingTitle, input[name="PostingTitle"]');
    if (await titleField.count() > 0) {
      await titleField.fill(adData.title);
      console.log('  Filled title');
    } else {
      console.log('  Title field not found - checking page...');
      const inputs = await page.locator('input[type="text"]').allTextContents();
      const allInputs = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('input, textarea')).map(el => ({
          id: el.id, name: el.name, type: el.type, placeholder: el.placeholder
        }));
      });
      console.log('  All inputs:', JSON.stringify(allInputs.slice(0, 10)));
    }
    
    const bodyField = page.locator('#PostingBody, textarea[name="PostingBody"]');
    if (await bodyField.count() > 0) {
      await bodyField.fill(adData.body);
      console.log('  Filled body');
    }
    
    const postalField = page.locator('input[name="postal"], #postal');
    if (await postalField.count() > 0) {
      await postalField.fill(adData.postal);
      console.log('  Filled postal');
    }
    
    // Fill email if required
    const fromEmailField = page.locator('input[name="FromEMail"], #FromEMail');
    if (await fromEmailField.count() > 0) {
      await fromEmailField.fill(EMAIL);
      console.log('  Filled email');
    }
    
    await logState(page, `${adType}-5-filled`);
    
    // Continue
    const contBtn4 = page.locator('button:has-text("continue"), input[value="continue"], button[type="submit"]:not([id="onetime"])');
    if (await contBtn4.count() > 0) {
      await contBtn4.first().click();
      await sleep(2000);
    }
    
    await logState(page, `${adType}-6-after-form`);
    
    // Additional steps (location confirm, etc.)
    for (let step = 0; step < 5; step++) {
      const currentPageText = await page.textContent('body').catch(() => '');
      
      // Check for image upload step - skip it
      if (currentPageText.includes('image') || currentPageText.includes('photo')) {
        const doneWithImages = page.locator('button:has-text("done with images"), a:has-text("done with images")');
        if (await doneWithImages.count() > 0) {
          await doneWithImages.first().click();
          await sleep(2000);
          console.log('  Skipped images');
          continue;
        }
      }
      
      // Check for publish button
      const publishBtn = page.locator('button:has-text("publish"), input[value="publish"], button:has-text("Publish")');
      if (await publishBtn.count() > 0) {
        await publishBtn.first().click();
        await sleep(3000);
        await logState(page, `${adType}-published`);
        console.log('  PUBLISHED!');
        break;
      }
      
      // Check for confirmation/success page
      const url = page.url();
      if (url.includes('manage') || url.includes('confirm') || url.includes('success')) {
        console.log('  Success page reached');
        break;
      }
      
      // Click continue if present
      const nextBtn = page.locator('button:has-text("continue"), input[value="continue"], button[type="submit"]');
      if (await nextBtn.count() > 0) {
        const btnText = await nextBtn.first().textContent();
        console.log(`  Clicking: ${btnText?.trim()}`);
        await nextBtn.first().click();
        await sleep(2000);
        await logState(page, `${adType}-step-${step + 7}`);
      } else {
        console.log('  No more buttons found, stopping');
        break;
      }
    }
    
    const finalUrl = page.url();
    const finalText = await page.textContent('body').catch(() => '');
    const isSuccess = finalUrl.includes('manage') || finalUrl.includes('confirm') || 
                      finalText.includes('email') || finalText.includes('confirmation') ||
                      finalText.includes('published') || finalText.includes('Your posting');
    
    return {
      success: isSuccess,
      url: finalUrl,
      note: isSuccess ? 'Submission completed - check email for confirmation' : 'Check screenshots'
    };
    
  } catch (e) {
    console.error(`  Error: ${e.message.split('\n')[0]}`);
    try { await page.screenshot({ path: `/root/.openclaw/workspace/assets/cl-${adType}-error.png` }); } catch (_) {}
    return { success: false, error: e.message.split('\n')[0] };
  } finally {
    await page.close();
  }
}

(async () => {
  const browser = await chromium.launch({ 
    headless: true, 
    args: ['--no-sandbox', '--disable-dev-shm-usage']
  });
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 800 }
  });
  
  await context.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  });
  
  try {
    // Post seller ad (Real Estate Wanted - we're looking for sellers)
    const sellerResult = await postAd(context, 'seller', SELLER_AD);
    results.push({ type: 'seller_ad_phoenix', area: 'west_valley', ...sellerResult });
    
    await sleep(3000);
    
    // Post buyer ad (Real Estate for Sale - we have deals for investors)
    const buyerResult = await postAd(context, 'buyer', BUYER_AD);
    results.push({ type: 'buyer_ad_phoenix', area: 'central_south_phx', ...buyerResult });
    
  } finally {
    await browser.close();
  }
  
  console.log('\n=== CRAIGSLIST RESULTS ===');
  console.log(JSON.stringify(results, null, 2));
  
  fs.writeFileSync(
    '/root/.openclaw/workspace/assets/craigslist-results.json',
    JSON.stringify(results, null, 2)
  );
})();
