const { chromium } = require('playwright');

async function waitAndLog(page, label) {
  await page.waitForTimeout(2000);
  console.log(`\n=== ${label} ===`);
  console.log('URL:', page.url());
  const text = await page.textContent('body').catch(() => '');
  console.log('Body text (first 1500):', text.substring(0, 1500));
  await page.screenshot({ path: `/tmp/cl_${label.replace(/\s/g,'_')}.png` });
}

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();

  // Navigate
  await page.goto('https://post.craigslist.org/c/phx', { waitUntil: 'load', timeout: 30000 });
  await waitAndLog(page, 'INITIAL');

  // Handle whatever step we're on dynamically
  for (let step = 0; step < 8; step++) {
    const url = page.url();
    const bodyText = await page.textContent('body').catch(() => '');
    
    // SUBAREA selection
    if (url.includes('?s=subarea') && bodyText.includes('choose the location')) {
      console.log(`\nStep ${step}: Handling subarea selection`);
      await page.locator('input[type="radio"]').first().check();
      await page.locator('button[name="go"]').first().click();
      await page.waitForTimeout(2000);
      continue;
    }

    // TYPE selection
    if (bodyText.includes('what type of posting')) {
      console.log(`\nStep ${step}: Handling type selection`);
      const radio = page.locator('input[value="so"]');
      if (await radio.count() > 0) {
        await radio.check();
        await page.locator('button[name="go"]').first().click();
        await page.waitForTimeout(2000);
        continue;
      }
    }

    // CATEGORY selection
    if (bodyText.includes('computer services')) {
      console.log(`\nStep ${step}: Handling category selection`);
      const catLink = page.getByText(/computer services/i).first();
      await catLink.click();
      await page.waitForTimeout(2000);
      continue;
    }

    // FORM (title/body fields)
    if (bodyText.includes('posting title') || bodyText.includes('Posting Title') || 
        await page.locator('input[name="PostingTitle"]').count() > 0) {
      console.log(`\nStep ${step}: Found posting form`);
      await waitAndLog(page, 'FORM_PAGE');
      
      // Show all form elements
      const elements = await page.locator('input, textarea, select').all();
      console.log(`\nForm elements (${elements.length}):`);
      for (const el of elements) {
        const tag = await el.evaluate(e => e.tagName);
        const name = await el.getAttribute('name').catch(() => '');
        const id = await el.getAttribute('id').catch(() => '');
        const type = await el.getAttribute('type').catch(() => '');
        console.log(`  <${tag.toLowerCase()}> name="${name}" id="${id}" type="${type}"`);
      }
      break;
    }

    // PAYMENT page
    if (bodyText.toLowerCase().includes('payment') || bodyText.toLowerCase().includes('credit card') || 
        bodyText.toLowerCase().includes('billing')) {
      console.log(`\nStep ${step}: PAYMENT PAGE DETECTED`);
      await waitAndLog(page, 'PAYMENT_PAGE');
      break;
    }

    // EMAIL CONFIRMATION
    if (bodyText.toLowerCase().includes('check your email') || bodyText.toLowerCase().includes('confirm your')) {
      console.log(`\nStep ${step}: EMAIL CONFIRMATION PAGE`);
      await waitAndLog(page, 'EMAIL_CONFIRM');
      break;
    }

    // Nothing matched - show the page
    console.log(`\nStep ${step}: Unknown page`);
    await waitAndLog(page, `UNKNOWN_step${step}`);
    
    // Try clicking continue if available
    const cont = page.locator('button[name="go"], button:has-text("continue")').first();
    if (await cont.count() > 0) {
      await cont.click();
      await page.waitForTimeout(2000);
    } else {
      console.log('No continue button found, stopping.');
      break;
    }
  }

  await browser.close();
})();
