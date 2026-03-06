const { chromium } = require('/root/.openclaw/workspace/node_modules/playwright');
const fs = require('fs');

const EMAIL = 'hello@pantrymate.net';

// Email removed from body - use CL relay (replies go to hello@pantrymate.net)
const SELLER_AD = {
  title: 'We Buy Phoenix Houses Cash - Any Condition, Fast Close',
  body: `Selling your Phoenix home? We buy houses directly for cash.

Any condition - no repairs needed
Close in 7-14 days
No realtor fees, no commissions
We handle all paperwork
Pre-foreclosure, inherited, vacant, behind on payments - all OK

We work with a network of cash buyers and can often close faster than traditional buyers.

Reply to this ad for a no-obligation cash offer.

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

Currently building our buyer list. If you are an active investor looking for Phoenix deals, reply to this ad to get on the list.

Include: how many deals/year you close, typical buy box (price range, neighborhoods, condition), and if you prefer fix-flip or buy-and-hold.`,
  postal: '85031'
};

const results = [];
async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
async function ss(page, name) {
  await page.screenshot({ path: `/root/.openclaw/workspace/assets/v5-${name}.png` }).catch(() => {});
}

async function selectRadioByValue(page, value) {
  return await page.evaluate((v) => {
    const el = document.querySelector(`input[type="radio"][value="${v}"]`);
    if (el) { el.click(); return true; }
    return false;
  }, value);
}

async function selectRadioByLabelText(page, text) {
  return await page.evaluate((text) => {
    for (const inp of document.querySelectorAll('input[type="radio"]')) {
      const label = document.querySelector(`label[for="${inp.id}"]`) || inp.closest('label');
      if (label && label.textContent.toLowerCase().includes(text.toLowerCase())) {
        inp.click();
        return { found: true, text: label.textContent.trim().substring(0, 50) };
      }
    }
    return { found: false };
  }, text);
}

async function fillAllSelects(page) {
  return await page.evaluate(() => {
    const selects = document.querySelectorAll('select');
    const filled = [];
    for (const sel of selects) {
      if (sel.value) continue; // already has value
      const options = Array.from(sel.options);
      const firstReal = options.find(o => o.value && o.value !== '' && o.text.trim() && o.text !== '-');
      if (firstReal) {
        sel.value = firstReal.value;
        sel.dispatchEvent(new Event('change', { bubbles: true }));
        filled.push({ name: sel.name, text: firstReal.text });
      }
    }
    return filled;
  });
}

async function setContactEmail(page) {
  // Set email relay to show email OR just fill the email field
  const emailEl = page.locator('input[name="FromEMail"], #FromEMail');
  if (await emailEl.count() > 0) {
    await emailEl.fill(EMAIL);
    console.log('  ✓ Filled contact email');
  }
  
  // Check for email display option - try to select "show my email"
  const showEmailRadio = await page.evaluate(() => {
    for (const inp of document.querySelectorAll('input[type="radio"]')) {
      if (inp.name === 'contact_privacy' || inp.name === 'email_privacy') {
        const label = document.querySelector(`label[for="${inp.id}"]`) || inp.closest('label');
        if (label && (label.textContent.includes('show') || label.textContent.includes('display'))) {
          inp.click();
          return true;
        }
      }
    }
    return false;
  });
  
  if (showEmailRadio) console.log('  ✓ Set email to show');
}

async function clickContinue(page) {
  await sleep(300);
  const btn = page.locator('button:has-text("continue"), input[value="continue"]').first();
  if (await btn.count() > 0) {
    await btn.click();
    await sleep(2000);
    return true;
  }
  return false;
}

async function handlePostFlow(page, adData, adType) {
  // Fill form
  await page.fill('#PostingTitle', adData.title).catch(() => {});
  await page.fill('#PostingBody', adData.body).catch(() => {});
  
  const postalEl = page.locator('input[name="postal"]');
  if (await postalEl.count() > 0) await postalEl.fill(adData.postal);
  
  const priceEl = page.locator('input[name="price"]');
  if (await priceEl.count() > 0) await priceEl.fill('250000');
  
  await setContactEmail(page);
  await fillAllSelects(page);
  
  await ss(page, `${adType}-form-filled`);
  console.log('  Form filled, submitting...');
  await clickContinue(page);
  
  // Handle post-form steps
  for (let i = 0; i < 10; i++) {
    const url = page.url();
    const title = await page.title().catch(() => '?');
    console.log(`  [${i}] ${title.substring(0, 50)} | ${url.split('?')[1] || url}`);
    await ss(page, `${adType}-flow${i}`);
    
    const bodyText = await page.textContent('body').catch(() => '');
    
    // Blocked?
    if (bodyText.includes('posting blocked') || bodyText.includes('being blocked')) {
      console.log('  ✗ POST BLOCKED: ' + bodyText.substring(bodyText.indexOf('blocked'), bodyText.indexOf('blocked') + 200));
      return { success: false, url, note: 'Post blocked by Craigslist' };
    }
    
    // Success?
    if (bodyText.includes('confirmation email') || bodyText.includes('check your email') ||
        url.includes('/manage/') || bodyText.includes('has been received')) {
      return { success: true, url, note: 'Check hello@pantrymate.net for confirmation' };
    }
    
    // Edit again (after block)
    const editBtn = page.locator('a:has-text("Edit Again"), button:has-text("Edit Again")');
    if (await editBtn.count() > 0) {
      await editBtn.first().click();
      await sleep(2000);
      continue;
    }
    
    // Images
    const doneImgBtn = page.locator('button:has-text("done with images"), a:has-text("done with images")');
    if (bodyText.toLowerCase().includes('add image') && await doneImgBtn.count() > 0) {
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
      const finalUrl = page.url();
      return { success: true, url: finalUrl, note: 'Check hello@pantrymate.net for confirmation' };
    }
    
    if (!await clickContinue(page)) break;
  }
  
  return { success: false, url: page.url(), note: 'Incomplete flow' };
}

async function postAd(context, adType, adData, area, categoryType, subCatValue) {
  const page = await context.newPage();
  console.log(`\n====== ${adType.toUpperCase()} AD ======`);
  
  try {
    await page.goto('https://post.craigslist.org/c/phx', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await sleep(1500);
    
    // Area
    await selectRadioByLabelText(page, area);
    await clickContinue(page);
    
    // Category type
    const typeSel = await selectRadioByValue(page, categoryType);
    if (!typeSel) await selectRadioByLabelText(page, categoryType === 'hws' ? 'housing wanted' : 'housing offered');
    await clickContinue(page);
    await ss(page, `${adType}-subcat`);
    
    // Sub-category
    const subSel = await selectRadioByValue(page, subCatValue);
    if (!subSel) {
      // Try by label
      const subText = adType === 'seller' ? 'real estate' : 'real estate - by owner';
      await selectRadioByLabelText(page, subText);
    }
    await clickContinue(page);
    await ss(page, `${adType}-form`);
    
    console.log('  Form URL:', page.url());
    
    return await handlePostFlow(page, adData, adType);
    
  } catch(e) {
    console.error('  Fatal error:', e.message.split('\n')[0]);
    await ss(page, `${adType}-error`);
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
    // Seller ad: housing wanted > real estate wanted (value 121 from earlier)
    const sellerResult = await postAd(context, 'seller', SELLER_AD, 'west valley', 'hws', '121');
    results.push({ type: 'seller_ad_phoenix_west_valley', ...sellerResult });
    
    await sleep(3000);
    
    // Buyer ad: housing offered > real estate - by owner (value 143 from earlier)
    const buyerResult = await postAd(context, 'buyer', BUYER_AD, 'central/south phx', 'hos', '143');
    results.push({ type: 'buyer_ad_phoenix_central', ...buyerResult });
    
  } finally {
    await browser.close();
  }
  
  console.log('\n=== FINAL RESULTS ===');
  console.log(JSON.stringify(results, null, 2));
  fs.writeFileSync('/root/.openclaw/workspace/assets/craigslist-results.json', JSON.stringify(results, null, 2));
})();
