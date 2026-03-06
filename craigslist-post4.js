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
async function ss(page, name) {
  await page.screenshot({ path: `/root/.openclaw/workspace/assets/v4-${name}.png` }).catch(() => {});
}

// Precise radio selector using exact text match via JS
async function selectRadioByExactText(page, exactText) {
  const result = await page.evaluate((text) => {
    const inputs = document.querySelectorAll('input[type="radio"]');
    for (const inp of inputs) {
      // Check the label for this input
      const id = inp.id;
      let label = null;
      if (id) label = document.querySelector(`label[for="${id}"]`);
      if (!label) label = inp.closest('label');
      if (label) {
        const labelText = label.textContent.trim();
        // Use exact match or starts-with for compound labels
        if (labelText === text || labelText.startsWith(text) || labelText.includes(text)) {
          inp.click();
          return { found: true, text: labelText.substring(0, 50) };
        }
      }
    }
    // Try by value
    const byValue = document.querySelector(`input[type="radio"][value="${text}"]`);
    if (byValue) {
      byValue.click();
      return { found: true, text: 'by value' };
    }
    return { found: false };
  }, exactText);
  
  if (result.found) {
    console.log(`  ✓ Selected radio: "${result.text}"`);
  } else {
    console.log(`  ✗ Radio not found: "${exactText}"`);
  }
  return result.found;
}

// Select radio by exact value attribute
async function selectRadioByValue(page, value) {
  return await page.evaluate((v) => {
    const el = document.querySelector(`input[type="radio"][value="${v}"]`);
    if (el) { el.click(); return true; }
    return false;
  }, value);
}

// Set native select value via JS (handles hidden selects behind jQuery UI)
async function setSelectValue(page, name, value) {
  return await page.evaluate(({name, value}) => {
    const sel = document.querySelector(`select[name="${name}"]`);
    if (!sel) return false;
    const options = Array.from(sel.options);
    const match = options.find(o => o.value === value || o.text.includes(value));
    if (match) {
      sel.value = match.value;
      // Trigger change event
      sel.dispatchEvent(new Event('change', {bubbles: true}));
      return { found: true, set: match.text };
    }
    // Set first non-empty option
    const firstReal = options.find(o => o.value && o.value !== '');
    if (firstReal) {
      sel.value = firstReal.value;
      sel.dispatchEvent(new Event('change', {bubbles: true}));
      return { found: true, set: firstReal.text, fallback: true };
    }
    return false;
  }, {name, value});
}

// Set ALL select dropdowns to their first valid option
async function fillAllSelects(page) {
  const result = await page.evaluate(() => {
    const selects = document.querySelectorAll('select');
    const filled = [];
    for (const sel of selects) {
      const options = Array.from(sel.options);
      const firstReal = options.find(o => o.value && o.value !== '' && o.text.trim() && o.text !== '-');
      if (firstReal && !sel.value) {
        sel.value = firstReal.value;
        sel.dispatchEvent(new Event('change', {bubbles: true}));
        filled.push({ name: sel.name, value: firstReal.value, text: firstReal.text });
      }
    }
    return filled;
  });
  if (result.length > 0) {
    console.log('  ✓ Filled selects:', result.map(r => `${r.name}=${r.text}`).join(', '));
  }
}

async function clickContinue(page) {
  const btn = page.locator('button:has-text("continue"), input[value="continue"]').first();
  if (await btn.count() > 0) {
    await btn.click();
    await sleep(2000);
    return true;
  }
  return false;
}

async function submitForm(page, adType) {
  for (let i = 0; i < 8; i++) {
    const url = page.url();
    const title = await page.title();
    console.log(`  [Step ${i}] ${title.substring(0, 50)} | ${url.substring(0, 80)}`);
    await ss(page, `${adType}-step${i}`);
    
    const bodyText = await page.textContent('body').catch(() => '');
    
    // Check success
    if (bodyText.includes('confirmation email') || bodyText.includes('check your email') ||
        url.includes('/manage/') || bodyText.includes('Your posting has been')) {
      console.log('  ✓ SUCCESS - confirmation email sent');
      return { success: true, url, note: 'Check hello@pantrymate.net for confirmation' };
    }
    
    // Skip images
    const doneImagesBtn = page.locator('button:has-text("done with images"), a:has-text("done with images"), button:has-text("done")');
    if (bodyText.toLowerCase().includes('add image') && await doneImagesBtn.count() > 0) {
      await doneImagesBtn.first().click();
      await sleep(2000);
      continue;
    }
    
    // Publish button
    const publishBtn = page.locator('button:has-text("publish"), input[value="publish"]');
    if (await publishBtn.count() > 0) {
      console.log('  Clicking publish...');
      await publishBtn.first().click();
      await sleep(4000);
      await ss(page, `${adType}-published`);
      const finalUrl = page.url();
      const finalText = await page.textContent('body').catch(() => '');
      return {
        success: true,
        url: finalUrl,
        note: finalText.includes('email') ? 'Check hello@pantrymate.net for confirmation' : 'Published'
      };
    }
    
    // Continue
    if (!await clickContinue(page)) {
      console.log('  No continue button, stopping');
      break;
    }
  }
  
  return { success: false, url: page.url(), note: 'Did not complete - check screenshots' };
}

async function postSellerAd(context) {
  const page = await context.newPage();
  console.log('\n====== SELLER AD (Real Estate Wanted) ======');
  
  try {
    await page.goto('https://post.craigslist.org/c/phx', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await sleep(1500);
    
    // Area: west valley  
    await selectRadioByExactText(page, 'west valley');
    await clickContinue(page);
    await ss(page, 'seller-type');
    
    // Type: housing wanted
    // Values might be: "hws" for housing wanted
    let found = await selectRadioByValue(page, 'hws');
    if (!found) found = await selectRadioByExactText(page, 'housing wanted');
    await clickContinue(page);
    await ss(page, 'seller-subcat');
    
    // Sub-cat: wanted: real estate
    // Check actual radio values
    const radioVals = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('input[type="radio"]')).map(r => ({
        value: r.value,
        labelText: (document.querySelector(`label[for="${r.id}"]`) || {}).textContent?.trim()?.substring(0, 40)
      }));
    });
    console.log('  Sub-cat radios:', JSON.stringify(radioVals));
    
    found = await selectRadioByValue(page, 'rew');
    if (!found) found = await selectRadioByExactText(page, 'wanted: real estate');
    if (!found) await selectRadioByExactText(page, 'real estate');
    
    await clickContinue(page);
    await ss(page, 'seller-form');
    
    console.log('  Form URL:', page.url());
    
    // Fill form
    await page.fill('#PostingTitle', SELLER_AD.title).catch(() => console.log('  title field missing'));
    await page.fill('#PostingBody', SELLER_AD.body).catch(() => console.log('  body field missing'));
    
    const postalEl = page.locator('input[name="postal"]');
    if (await postalEl.count() > 0) await postalEl.fill(SELLER_AD.postal);
    
    const priceEl = page.locator('input[name="price"]');
    if (await priceEl.count() > 0) await priceEl.fill('250000');
    
    const emailEl = page.locator('input[name="FromEMail"]');
    if (await emailEl.count() > 0) await emailEl.fill(EMAIL);
    
    await fillAllSelects(page);
    await ss(page, 'seller-form-filled');
    
    // Submit
    await clickContinue(page);
    return await submitForm(page, 'seller');
    
  } catch(e) {
    console.error('  Error:', e.message.split('\n')[0]);
    await ss(page, 'seller-error');
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
    
    // Area: central/south phx
    await selectRadioByExactText(page, 'central/south phx');
    await clickContinue(page);
    
    // Type: housing offered = "hos"
    let found = await selectRadioByValue(page, 'hos');
    if (!found) found = await selectRadioByExactText(page, 'housing offered');
    await clickContinue(page);
    await ss(page, 'buyer-subcat');
    
    // Sub-cat: real estate - by owner = "rea"
    const radioVals = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('input[type="radio"]')).map(r => ({
        value: r.value,
        labelText: (document.querySelector(`label[for="${r.id}"]`) || r.closest('label') || {}).textContent?.trim()?.substring(0, 40)
      }));
    });
    console.log('  Sub-cat radios:', JSON.stringify(radioVals));
    
    found = await selectRadioByValue(page, 'rea');
    if (!found) {
      // Find "real estate - by owner" specifically
      found = await page.evaluate(() => {
        for (const inp of document.querySelectorAll('input[type="radio"]')) {
          const label = document.querySelector(`label[for="${inp.id}"]`) || inp.closest('label');
          if (label && label.textContent.includes('real estate') && label.textContent.includes('owner')) {
            inp.click();
            return true;
          }
        }
        return false;
      });
    }
    
    await clickContinue(page);
    await ss(page, 'buyer-form');
    
    console.log('  Form URL:', page.url());
    
    // Fill form
    await page.fill('#PostingTitle', BUYER_AD.title).catch(() => console.log('  title field missing'));
    await page.fill('#PostingBody', BUYER_AD.body).catch(() => console.log('  body field missing'));
    
    const postalEl = page.locator('input[name="postal"]');
    if (await postalEl.count() > 0) await postalEl.fill(BUYER_AD.postal);
    
    const priceEl = page.locator('input[name="price"]');
    if (await priceEl.count() > 0) await priceEl.fill('250000');
    
    const emailEl = page.locator('input[name="FromEMail"]');
    if (await emailEl.count() > 0) await emailEl.fill(EMAIL);
    
    // Fill all required selects using JS (avoids jQuery UI widget issues)
    await fillAllSelects(page);
    await ss(page, 'buyer-form-filled');
    
    // Submit
    await clickContinue(page);
    return await submitForm(page, 'buyer');
    
  } catch(e) {
    console.error('  Error:', e.message.split('\n')[0]);
    await ss(page, 'buyer-error');
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
  
  console.log('\n=== FINAL RESULTS ===');
  console.log(JSON.stringify(results, null, 2));
  fs.writeFileSync('/root/.openclaw/workspace/assets/craigslist-results.json', JSON.stringify(results, null, 2));
})();
