const { chromium } = require('playwright');

const EMAIL = 'hello@pantrymate.net';

const CITIES = [
  { name: 'Phoenix AZ',        code: 'phx', zip: '85001', subarea: null },
  { name: 'Salt Lake City UT', code: 'slc', zip: '84101', subarea: null },
  { name: 'Denver CO',         code: 'den', zip: '80201', subarea: null },
  { name: 'Boise ID',          code: 'boi', zip: '83701', subarea: null },
  { name: 'Las Vegas NV',      code: 'lvg', zip: '89101', subarea: null },
];

const SERVICES = [
  {
    id: 'app-dev',
    title: 'Custom App Development for Local Businesses — $1,500 flat rate',
    body: `I build custom mobile and web apps for local businesses — restaurants, contractors, salons, gyms, dental offices.

Examples of what I build:
• Online ordering systems (skip the GrubHub 30% fee)
• Appointment booking apps
• Customer loyalty apps
• Contractor job tracking apps
• Simple business management tools

Flat rate pricing: $1,500-3,500 depending on complexity.
Fast turnaround: 2-4 weeks.
Based in Wyoming, work with businesses nationwide.

No monthly fees, no ongoing contracts. You own the code.

Text or email to discuss your project:
hello@pantrymate.net`,
  },
  {
    id: 'ai-agent',
    title: 'AI Phone Agent for Dental Offices — Books Appointments 24/7',
    body: `Is your practice losing bookings to missed after-hours calls?

I set up AI phone agents for dental and medical offices that:
• Answer every call 24/7 — no voicemail
• Book appointments automatically
• Send SMS confirmations to patients
• Integrate with your existing schedule

Setup takes 48 hours.
$497/month flat rate. No contracts.

Practices typically recover 4-8 missed bookings per week — at $200-400 per appointment, the ROI is immediate.

Email for a free 10-minute demo:
hello@pantrymate.net`,
  },
];

const results = [];

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function postListing(browser, city, service) {
  const page = await browser.newPage();
  const label = `[${city.name}] "${service.title.substring(0, 40)}..."`;
  
  try {
    console.log(`\n${label} — starting`);
    
    // Navigate to post URL
    await page.goto(`https://post.craigslist.org/c/${city.code}`, { waitUntil: 'load', timeout: 30000 });
    await sleep(1500);

    // Step 1: Subarea selection
    const subareaRadio = page.locator('input[type="radio"]').first();
    if (await subareaRadio.count() > 0) {
      await subareaRadio.check();
      await Promise.all([
        page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {}),
        page.locator('button[name="go"]').first().click()
      ]);
      await sleep(1500);
      console.log(`  ${label} subarea done → ${page.url().split('?s=')[1]}`);
    }

    // Step 2: Type selection (may or may not appear)
    let bt = await page.textContent('body').catch(() => '');
    if (bt.includes('what type of posting')) {
      await page.locator('input[value="so"]').check();
      await Promise.all([
        page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {}),
        page.locator('button[name="go"]').first().click()
      ]);
      await sleep(1500);
      console.log(`  ${label} type done → ${page.url().split('?s=')[1]}`);
    }

    // Step 3: Category selection (computer services = value 76, auto-navigates on click)
    const catRadio = page.locator('input[name="id"][value="76"]');
    if (await catRadio.count() > 0) {
      await Promise.all([
        page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {}),
        catRadio.click()
      ]);
      await sleep(2000);
      console.log(`  ${label} category done → ${page.url().split('?s=')[1]}`);
    }

    // If still on cat page, click continue
    if (page.url().includes('?s=cat')) {
      await Promise.all([
        page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {}),
        page.locator('button[name="go"]').first().click()
      ]);
      await sleep(2000);
    }

    // Step 4: Fill the edit form
    if (!page.url().includes('?s=edit')) {
      throw new Error(`Expected edit form, got: ${page.url()}`);
    }

    // Title
    const titleEl = page.locator('input[name="PostingTitle"]');
    await titleEl.click();
    // Truncate to 70 chars if needed
    const truncTitle = service.title.substring(0, 70);
    await titleEl.fill(truncTitle);
    await page.keyboard.press('Tab');

    // Body
    const bodyEl = page.locator('textarea[name="PostingBody"]');
    await bodyEl.click();
    await bodyEl.fill(service.body);
    await page.keyboard.press('Tab');

    // ZIP
    const postalEl = page.locator('input[name="postal"]');
    await postalEl.click();
    await postalEl.fill(city.zip);
    await page.keyboard.press('Tab');

    // Email
    const emailEl = page.locator('input[name="FromEMail"]');
    await emailEl.click();
    await emailEl.fill(EMAIL);
    await page.keyboard.press('Tab');
    await sleep(500);

    // Verify fields filled
    const titleVal = await titleEl.inputValue();
    const emailVal = await emailEl.inputValue();
    if (!titleVal || !emailVal) {
      throw new Error(`Fields not filled: title="${titleVal}" email="${emailVal}"`);
    }

    // Submit edit form
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {}),
      page.locator('button[type="submit"], button[name="go"]').first().click()
    ]);
    await sleep(2000);
    console.log(`  ${label} form submitted → ${page.url().split('?s=')[1]}`);

    // Step 5: Geoverify — just continue
    if (page.url().includes('geoverify')) {
      await Promise.all([
        page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {}),
        page.locator('button[name="go"], button:has-text("continue")').first().click()
      ]);
      await sleep(2000);
      console.log(`  ${label} geoverify → ${page.url().split('?s=')[1]}`);
    }

    // Step 6: Image step — done with images
    if (page.url().includes('editimage') || page.url().includes('image')) {
      const doneBtn = page.locator('button:has-text("done with images")').first();
      if (await doneBtn.count() > 0) {
        await Promise.all([
          page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {}),
          doneBtn.click()
        ]);
        await sleep(2000);
        console.log(`  ${label} images done → ${page.url().split('?s=')[1]}`);
      }
    }

    // Step 7: Preview — click publish
    if (page.url().includes('preview')) {
      const publishBtn = page.locator('button:has-text("publish")').first();
      if (await publishBtn.count() > 0) {
        await Promise.all([
          page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {}),
          publishBtn.click()
        ]);
        await sleep(3000);
        console.log(`  ${label} published → ${page.url().split('?s=')[1]}`);
      }
    }

    // Final state
    const finalUrl = page.url();
    const finalBt = await page.textContent('body').catch(() => '');
    await page.screenshot({ path: `/tmp/cl_final_${city.code}_${service.id}.png` });

    let status = 'unknown';
    if (finalUrl.includes('loginloop') && finalBt.includes('email shortly')) {
      status = '✅ confirmation_email_sent';
    } else if (finalUrl.includes('manage') || finalBt.includes('your post is live')) {
      status = '✅ published';
    } else if (finalBt.toLowerCase().includes('error') || finalBt.toLowerCase().includes('problem')) {
      status = `❌ error: ${finalUrl.split('?s=')[1]}`;
    } else {
      status = `⚠️ unknown: ${finalUrl.split('?s=')[1]}`;
    }

    console.log(`  ${label} → STATUS: ${status}`);
    results.push({ city: city.name, service: service.id, title: service.title, status });

  } catch (err) {
    console.log(`  ${label} → FAILED: ${err.message}`);
    await page.screenshot({ path: `/tmp/cl_error_${city.code}_${service.id}.png` }).catch(() => {});
    results.push({ city: city.name, service: service.id, title: service.title, status: `❌ error: ${err.message.substring(0,80)}` });
  } finally {
    await page.close();
  }
}

(async () => {
  console.log('=== Craigslist Auto-Poster ===');
  console.log(`Posting ${SERVICES.length} services in ${CITIES.length} cities = ${SERVICES.length * CITIES.length} total posts\n`);

  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });

  for (const city of CITIES) {
    for (const service of SERVICES) {
      await postListing(browser, city, service);
      // Small delay between posts to be respectful
      await sleep(3000);
    }
  }

  await browser.close();

  console.log('\n\n============================================================');
  console.log('FINAL RESULTS SUMMARY');
  console.log('============================================================');
  let successCount = 0;
  for (const r of results) {
    const ok = r.status.startsWith('✅');
    if (ok) successCount++;
    console.log(`${r.status}`);
    console.log(`  City: ${r.city}`);
    console.log(`  Title: ${r.title.substring(0, 60)}`);
    console.log('');
  }
  console.log(`Successful: ${successCount} / ${results.length}`);
  console.log('\nNOTE: Posts with "confirmation_email_sent" status require Wolfgang to:');
  console.log('  1. Check email at hello@pantrymate.net');
  console.log('  2. Click the confirmation link for each post (10 emails)');
  console.log('  3. Log in or create a Craigslist account');
  console.log('  4. Pay $5 per posting to publish ($50 total)');
  console.log('  Links expire in 30 minutes — check email now!');
})();
