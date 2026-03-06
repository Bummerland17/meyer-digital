const { chromium } = require('playwright');

const EMAIL = 'hello@pantrymate.net';

const CITIES = [
  { name: 'Phoenix AZ',        code: 'phx', zip: '85001' },
  { name: 'Salt Lake City UT', code: 'slc', zip: '84101' },
  { name: 'Denver CO',         code: 'den', zip: '80201' },
  { name: 'Boise ID',          code: 'boi', zip: '83701' },
  { name: 'Las Vegas NV',      code: 'lvg', zip: '89101' },
];

const SERVICES = [
  {
    id: 'app-dev',
    title: 'Custom App Development for Local Businesses — $1,500 flat rate',
    // Title max 70 chars — truncate
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

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function postListing(browser, city, service) {
  const page = await browser.newPage();
  const label = `[${city.name}/${service.id}]`;

  try {
    console.log(`\n${label} Starting...`);
    await page.goto(`https://post.craigslist.org/c/${city.code}`, { waitUntil: 'load', timeout: 30000 });
    await sleep(1500);

    // Navigate through steps until we reach the edit form
    // Steps can be: subarea → type → cat → edit (or subarea → cat, or type → cat, etc.)
    for (let step = 0; step < 6; step++) {
      const url = page.url();
      const stage = url.split('?s=')[1] || '';
      const bt = await page.textContent('body').catch(() => '');
      console.log(`  ${label} step=${step} stage=${stage}`);

      if (stage === 'edit' || stage.startsWith('edit')) {
        console.log(`  ${label} → reached edit form`);
        break;
      }

      // SUBAREA: choose location
      if (bt.includes('choose the location that fits best') || stage === 'subarea') {
        console.log(`  ${label} → subarea page: selecting first area`);
        await page.locator('input[type="radio"]').first().check();
        await Promise.all([
          page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {}),
          page.locator('button[name="go"]').first().click()
        ]);
        await sleep(1500);
        continue;
      }

      // TYPE: what type of posting
      if (bt.includes('what type of posting') || stage === 'type') {
        console.log(`  ${label} → type page: selecting service offered`);
        await page.locator('input[value="so"]').check();
        await Promise.all([
          page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {}),
          page.locator('button[name="go"]').first().click()
        ]);
        await sleep(1500);
        continue;
      }

      // CATEGORY: pick computer services
      if (stage === 'cat' || bt.includes('please choose a category')) {
        console.log(`  ${label} → category page: selecting computer services`);
        const catRadio = page.locator('input[name="id"][value="76"]');
        if (await catRadio.count() > 0) {
          // Radio click auto-navigates
          await Promise.all([
            page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {}),
            catRadio.click()
          ]);
          await sleep(2000);
          // If still on cat page, click continue
          if (page.url().includes('?s=cat')) {
            await Promise.all([
              page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {}),
              page.locator('button[name="go"]').first().click()
            ]);
            await sleep(2000);
          }
          continue;
        } else {
          throw new Error('Computer services radio (value=76) not found on category page');
        }
      }

      // Unknown step — try clicking continue
      console.log(`  ${label} → unknown step, trying continue`);
      const cont = page.locator('button[name="go"], button:has-text("continue")').first();
      if (await cont.count() > 0) {
        await Promise.all([
          page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {}),
          cont.click()
        ]);
        await sleep(1500);
        continue;
      }
      throw new Error(`Stuck on step ${step}: stage=${stage}`);
    }

    // Verify we're on edit form
    if (!page.url().includes('?s=edit')) {
      throw new Error(`Expected edit form, got: ${page.url()}`);
    }

    // FILL THE FORM
    console.log(`  ${label} → filling form`);

    // Title (max 70 chars)
    const truncTitle = service.title.substring(0, 70);
    const titleEl = page.locator('input[name="PostingTitle"]');
    await titleEl.click();
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

    // Set Privacy to "P" (show real email) to avoid body-email conflict
    // This is necessary because body contains email address
    const privacyP = page.locator('input[name="Privacy"][value="P"]');
    if (await privacyP.count() > 0) {
      await privacyP.check();
      console.log(`  ${label} → set privacy to show real email`);
    }

    await sleep(500);

    // Verify
    const titleVal = await titleEl.inputValue();
    const emailVal = await emailEl.inputValue();
    console.log(`  ${label} → title="${titleVal.substring(0,40)}" email="${emailVal}"`);
    if (!titleVal || !emailVal) {
      throw new Error(`Form fields not filled properly`);
    }

    // Submit edit form
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {}),
      page.locator('button[type="submit"], button[name="go"]').first().click()
    ]);
    await sleep(2000);
    console.log(`  ${label} → after form submit: ${page.url().split('?s=')[1]}`);

    // Handle remaining steps
    for (let step = 0; step < 8; step++) {
      const url = page.url();
      const stage = url.split('?s=')[1] || '';
      const bt2 = await page.textContent('body').catch(() => '');
      console.log(`  ${label} post-form step=${step} stage=${stage}`);

      // Success: email sent
      if (stage === 'loginloop' && bt2.includes('email shortly')) {
        console.log(`  ${label} → ✅ CONFIRMED: Email sent to ${EMAIL}`);
        break;
      }

      // Success: already published
      if (bt2.includes('your post is live') || bt2.includes('posting is live')) {
        console.log(`  ${label} → ✅ LIVE`);
        break;
      }

      // Bodyemail conflict (shouldn't happen with Privacy=P, but handle it)
      if (stage === 'bodyemail') {
        throw new Error('Body email conflict - posting blocked');
      }

      // Geoverify
      if (stage === 'geoverify') {
        const cont = page.locator('button[name="go"], button:has-text("continue")').first();
        if (await cont.count() > 0) {
          await Promise.all([
            page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {}),
            cont.click()
          ]);
          await sleep(2000);
          continue;
        }
      }

      // Image step
      if (stage === 'editimage' || bt2.includes('Add Images')) {
        const doneBtn = page.locator('button:has-text("done with images")').first();
        if (await doneBtn.count() > 0) {
          await Promise.all([
            page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {}),
            doneBtn.click()
          ]);
          await sleep(2000);
          continue;
        }
      }

      // Preview
      if (stage === 'preview') {
        const publishBtn = page.locator('button:has-text("publish")').first();
        if (await publishBtn.count() > 0) {
          await Promise.all([
            page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {}),
            publishBtn.click()
          ]);
          await sleep(3000);
          continue;
        }
      }

      // Generic continue
      const genCont = page.locator('button[name="go"], button:has-text("continue"), button[type="submit"]').first();
      if (await genCont.count() > 0) {
        await Promise.all([
          page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {}),
          genCont.click()
        ]);
        await sleep(2000);
        continue;
      }

      console.log(`  ${label} → no continue button, ending at stage=${stage}`);
      break;
    }

    // Final status
    const finalUrl = page.url();
    const finalBt = await page.textContent('body').catch(() => '');
    await page.screenshot({ path: `/tmp/cl_final_${city.code}_${service.id}.png` });

    let status;
    if (finalUrl.includes('loginloop') && finalBt.includes('email shortly')) {
      status = '✅ confirmation_email_sent';
    } else if (finalBt.includes('your post is live')) {
      status = '✅ published_live';
    } else {
      status = `⚠️ ended_at: ${finalUrl.split('?s=')[1]}`;
    }

    console.log(`  ${label} → FINAL STATUS: ${status}`);
    results.push({ city: city.name, service: service.id, title: service.title, status });

  } catch (err) {
    const errMsg = err.message.substring(0, 100);
    console.log(`  ${label} → ❌ FAILED: ${errMsg}`);
    await page.screenshot({ path: `/tmp/cl_error_${city.code}_${service.id}.png` }).catch(() => {});
    results.push({ city: city.name, service: service.id, title: service.title, status: `❌ ${errMsg}` });
  } finally {
    await page.close();
  }
}

(async () => {
  console.log('=== Craigslist Auto-Poster v2 ===');
  console.log(`${SERVICES.length} services × ${CITIES.length} cities = ${SERVICES.length * CITIES.length} posts\n`);

  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });

  for (const city of CITIES) {
    for (const service of SERVICES) {
      await postListing(browser, city, service);
      await sleep(3000);
    }
  }

  await browser.close();

  console.log('\n\n=================================================');
  console.log('FINAL RESULTS');
  console.log('=================================================');
  let ok = 0;
  for (const r of results) {
    if (r.status.startsWith('✅')) ok++;
    console.log(`${r.status} | ${r.city} | ${r.title.substring(0, 50)}`);
  }
  console.log(`\nSuccessful: ${ok} / ${results.length}`);

  if (ok > 0) {
    console.log('\n⚠️  IMPORTANT: Check hello@pantrymate.net NOW!');
    console.log('   Each confirmed post has an email with a link to:');
    console.log('   1. Log in / create Craigslist account');
    console.log('   2. Pay $5 per post to publish');
    console.log('   Links expire in 30 minutes!');
  }
})();
