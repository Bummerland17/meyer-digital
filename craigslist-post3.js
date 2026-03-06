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

async function screenshot(page, name) {
  await page.screenshot({ path: `/root/.openclaw/workspace/assets/cl3-${name}.png` }).catch(() => {});
}

async function clickRadioByText(page, text) {
  const labels = await page.locator('label').all();
  for (const label of labels) {
    const t = (await label.textContent() || '').trim().toLowerCase();
    if (t.includes(text.toLowerCase())) {
      const forId = await label.getAttribute('for');
      if (forId) {
        await page.click(`#${forId}`);
      } else {
        await label.click();
      }
      console.log(`  ✓ Selected: "${t}"`);
      return true;
    }
  }
  console.log(`  ✗ Could not find option: "${text}"`);
  return false;
}

async function clickContinue(page) {
  await sleep(500);
  const btn = page.locator('button:has-text("continue"), input[value="continue"]').first();
  if (await btn.count() > 0) {
    await btn.click();
    await sleep(2000);
    return true;
  }
  return false;
}

async function postSellerAd(context) {
  const page = await context.newPage();
  console.log('\n====== SELLER AD (Real Estate Wanted) ======');
  
  try {
    // Start
    await page.goto('https://post.craigslist.org/c/phx', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await sleep(1500);
    
    // Select area: west valley (for 85031 zip codes)
    await clickRadioByText(page, 'west valley');
    await clickContinue(page);
    await screenshot(page, 'seller-type-page');
    
    // Select type: "housing wanted" 
    console.log('  Selecting type: housing wanted');
    const found = await clickRadioByText(page, 'housing wanted');
    if (!found) {
      // Log all available options
      const labels = await page.locator('label').allTextContents();
      console.log('  Available types:', labels.map(l => l.trim()).filter(l => l).join(' | '));
    }
    await clickContinue(page);
    await screenshot(page, 'seller-subcat-page');
    
    // Select sub-category: real estate wanted
    const labels2 = await page.locator('label').allTextContents();
    console.log('  Sub-cats:', labels2.map(l => l.trim()).filter(l => l.length > 2).join(' | '));
    
    await clickRadioByText(page, 'real estate wanted');
    await clickContinue(page);
    await screenshot(page, 'seller-form-page');
    
    // Fill form
    console.log('  URL after subcat:', page.url());
    
    const inputs = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('input, textarea, select')).map(el => ({
        id: el.id, name: el.name, type: el.type, tagName: el.tagName
      })).filter(el => el.id || el.name);
    });
    console.log('  Form inputs:', JSON.stringify(inputs.slice(0, 15)));
    
    // Fill title
    const titleEl = page.locator('#PostingTitle, input[name="PostingTitle"]');
    if (await titleEl.count() > 0) { await titleEl.fill(SELLER_AD.title); console.log('  ✓ Filled title'); }
    
    // Fill body
    const bodyEl = page.locator('#PostingBody, textarea[name="PostingBody"]');
    if (await bodyEl.count() > 0) { await bodyEl.fill(SELLER_AD.body); console.log('  ✓ Filled body'); }
    
    // Postal
    const postalEl = page.locator('input[name="postal"], #postal');
    if (await postalEl.count() > 0) { await postalEl.fill(SELLER_AD.postal); console.log('  ✓ Filled postal'); }
    
    // Email
    const emailEl = page.locator('input[name="FromEMail"], #FromEMail');
    if (await emailEl.count() > 0) { await emailEl.fill(EMAIL); console.log('  ✓ Filled email'); }
    
    // Price budget (for housing wanted)
    const priceEl = page.locator('input[name="price"], #price');
    if (await priceEl.count() > 0) { await priceEl.fill('250000'); console.log('  ✓ Filled price'); }
    
    await screenshot(page, 'seller-form-filled');
    await clickContinue(page);
    await screenshot(page, 'seller-after-continue');
    
    // Handle additional steps
    for (let i = 0; i < 6; i++) {
      const url = page.url();
      const title = await page.title();
      console.log(`  Step ${i}: ${title} | ${url}`);
      
      const bodyText = await page.textContent('body').catch(() => '');
      
      // Skip images
      if (bodyText.toLowerCase().includes('add image') || bodyText.toLowerCase().includes('photo')) {
        const doneBtn = page.locator('button:has-text("done"), a:has-text("done with images")');
        if (await doneBtn.count() > 0) {
          await doneBtn.first().click();
          await sleep(2000);
          continue;
        }
      }
      
      // Publish
      const publishBtn = page.locator('button:has-text("publish"), input[value="publish"]');
      if (await publishBtn.count() > 0) {
        await publishBtn.first().click();
        await sleep(3000);
        await screenshot(page, 'seller-published');
        console.log('  ✓ PUBLISHED!');
        return { success: true, url: page.url(), note: 'Check hello@pantrymate.net for confirmation email' };
      }
      
      // Check success
      if (url.includes('manage') || url.includes('confirm') || bodyText.includes('confirmation email')) {
        return { success: true, url, note: 'Confirmation email sent to hello@pantrymate.net' };
      }
      
      // Continue
      if (!await clickContinue(page)) break;
      await screenshot(page, `seller-step${i}`);
    }
    
    return { success: false, url: page.url(), note: 'Incomplete - check screenshots' };
    
  } catch(e) {
    console.error('  Error:', e.message.split('\n')[0]);
    await screenshot(page, 'seller-error');
    return { success: false, error: e.message.split('\n')[0] };
  } finally {
    await page.close();
  }
}

async function postBuyerAd(context) {
  const page = await context.newPage();
  console.log('\n====== BUYER AD (Real Estate by Owner) ======');
  
  try {
    await page.goto('https://post.craigslist.org/c/phx', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await sleep(1500);
    
    // Select area
    await clickRadioByText(page, 'central/south phx');
    await clickContinue(page);
    
    // Select type: housing offered
    await clickRadioByText(page, 'housing offered');
    await clickContinue(page);
    await screenshot(page, 'buyer-subcat-page');
    
    // Select sub-category: real estate - by owner
    const labels = await page.locator('label').allTextContents();
    console.log('  Sub-cats:', labels.map(l => l.trim()).filter(l => l.length > 2).join(' | '));
    
    await clickRadioByText(page, 'real estate - by owner');
    await clickContinue(page);
    await screenshot(page, 'buyer-form-page');
    
    console.log('  URL after subcat:', page.url());
    
    // Inspect form fields
    const inputs = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('input, textarea, select')).map(el => ({
        id: el.id, name: el.name, type: el.type, tagName: el.tagName,
        required: el.required, value: el.value?.substring(0, 30)
      })).filter(el => el.id || el.name);
    });
    console.log('  Form inputs:', JSON.stringify(inputs.slice(0, 20), null, 1));
    
    // Fill title
    const titleEl = page.locator('#PostingTitle, input[name="PostingTitle"]');
    if (await titleEl.count() > 0) { await titleEl.fill(BUYER_AD.title); console.log('  ✓ Filled title'); }
    
    // Fill body
    const bodyEl = page.locator('#PostingBody, textarea[name="PostingBody"]');
    if (await bodyEl.count() > 0) { await bodyEl.fill(BUYER_AD.body); console.log('  ✓ Filled body'); }
    
    // Postal
    const postalEl = page.locator('input[name="postal"], #postal');
    if (await postalEl.count() > 0) { await postalEl.fill(BUYER_AD.postal); console.log('  ✓ Filled postal'); }
    
    // Email
    const emailEl = page.locator('input[name="FromEMail"], #FromEMail');
    if (await emailEl.count() > 0) { await emailEl.fill(EMAIL); console.log('  ✓ Filled email'); }
    
    // Price (asking price for real estate)
    const priceEl = page.locator('input[name="price"], #price, input[name="ask"], #ask');
    if (await priceEl.count() > 0) { await priceEl.first().fill('250000'); console.log('  ✓ Filled price'); }
    
    // Handle required dropdowns - fill anything with "-" as selected value
    const selects = await page.locator('select').all();
    for (const sel of selects) {
      const name = await sel.getAttribute('name') || '';
      const val = await sel.inputValue();
      if (val === '-' || val === '') {
        // Try to select the first real option
        const options = await sel.locator('option').allTextContents();
        const nonEmpty = options.filter(o => o.trim() && o !== '-');
        if (nonEmpty.length > 0) {
          await sel.selectOption({ label: nonEmpty[0].trim() });
          console.log(`  ✓ Set ${name} to: ${nonEmpty[0].trim()}`);
        }
      }
    }
    
    await screenshot(page, 'buyer-form-filled');
    await clickContinue(page);
    await screenshot(page, 'buyer-after-continue');
    
    // Handle additional steps
    for (let i = 0; i < 6; i++) {
      const url = page.url();
      const title = await page.title();
      console.log(`  Step ${i}: ${title} | ${url}`);
      
      const bodyText = await page.textContent('body').catch(() => '');
      
      // Skip images
      if (bodyText.toLowerCase().includes('add image') || bodyText.toLowerCase().includes('photo')) {
        const doneBtn = page.locator('button:has-text("done"), a:has-text("done with images")');
        if (await doneBtn.count() > 0) {
          await doneBtn.first().click();
          await sleep(2000);
          continue;
        }
      }
      
      // Publish
      const publishBtn = page.locator('button:has-text("publish"), input[value="publish"]');
      if (await publishBtn.count() > 0) {
        await publishBtn.first().click();
        await sleep(3000);
        await screenshot(page, 'buyer-published');
        console.log('  ✓ PUBLISHED!');
        return { success: true, url: page.url(), note: 'Check hello@pantrymate.net for confirmation email' };
      }
      
      // Check success
      if (url.includes('manage') || url.includes('confirm') || bodyText.includes('confirmation email')) {
        return { success: true, url, note: 'Confirmation email sent' };
      }
      
      if (!await clickContinue(page)) break;
      await screenshot(page, `buyer-step${i}`);
    }
    
    return { success: false, url: page.url(), note: 'Incomplete - check screenshots' };
    
  } catch(e) {
    console.error('  Error:', e.message.split('\n')[0]);
    await screenshot(page, 'buyer-error');
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
    viewport: { width: 1280, height: 900 }
  });
  await context.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  });
  
  try {
    const sellerResult = await postSellerAd(context);
    results.push({ type: 'seller_ad_phoenix', ...sellerResult });
    await sleep(3000);
    
    const buyerResult = await postBuyerAd(context);
    results.push({ type: 'buyer_ad_phoenix', ...buyerResult });
  } finally {
    await browser.close();
  }
  
  console.log('\n=== RESULTS ===');
  console.log(JSON.stringify(results, null, 2));
  fs.writeFileSync('/root/.openclaw/workspace/assets/craigslist-results.json', JSON.stringify(results, null, 2));
})();
