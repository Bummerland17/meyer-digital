const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();
  const log = [];
  const errors = [];

  const snap = async (name) => {
    await page.screenshot({ path: `/root/.openclaw/workspace/snap_${name}.png`, fullPage: false });
  };

  try {
    // ── 1. Login ──────────────────────────────────────────────────────────────
    log.push('Navigating to sign-in page...');
    await page.goto('https://www.saashub.com/users/sign_in', { waitUntil: 'networkidle', timeout: 30000 });
    await snap('01_login');

    await page.fill('input[name="user[email]"]', 'olcowboy21@gmail.com');
    await page.fill('input[name="user[password]"]', 'Bummerland20');
    await page.click('input[type="submit"], button[type="submit"]');
    await page.waitForLoadState('networkidle', { timeout: 20000 });
    await snap('02_after_login');
    log.push('Login submitted. URL: ' + page.url());

    if (page.url().includes('sign_in')) {
      errors.push('Still on sign-in page — login may have failed');
      await snap('02_login_error');
    }

    // ── 2. Navigate to PantryMate edit page ───────────────────────────────────
    log.push('Navigating to PantryMate listing...');
    await page.goto('https://www.saashub.com/pantrymate', { waitUntil: 'networkidle', timeout: 30000 });
    await snap('03_pantrymate_page');
    log.push('PantryMate page URL: ' + page.url());

    // Look for edit/claim links
    const editLinks = await page.$$eval('a', links =>
      links.map(l => ({ text: l.textContent.trim(), href: l.href }))
           .filter(l => /edit|claim|manage|update|submit/i.test(l.text + l.href))
    );
    log.push('Edit links found: ' + JSON.stringify(editLinks.slice(0, 10)));

    // Try to find and click the edit button
    let editClicked = false;
    for (const sel of ['a[href*="/edit"]', 'a:has-text("Edit")', 'a:has-text("Update")', 'a:has-text("Claim")']) {
      try {
        const el = await page.$(sel);
        if (el) {
          const href = await el.getAttribute('href');
          log.push(`Found edit element with selector "${sel}", href: ${href}`);
          await el.click();
          await page.waitForLoadState('networkidle', { timeout: 20000 });
          editClicked = true;
          log.push('Navigated to edit page: ' + page.url());
          await snap('04_edit_page');
          break;
        }
      } catch (e) { /* skip */ }
    }

    if (!editClicked) {
      // Try direct URL patterns
      const slug = 'pantrymate';
      const tryUrls = [
        `https://www.saashub.com/${slug}/edit`,
        `https://www.saashub.com/products/${slug}/edit`,
        `https://www.saashub.com/tools/${slug}/edit`,
      ];
      for (const url of tryUrls) {
        log.push(`Trying edit URL: ${url}`);
        await page.goto(url, { waitUntil: 'networkidle', timeout: 20000 });
        if (!page.url().includes('sign_in') && !page.url().includes('404') && !page.url().includes('error')) {
          log.push('Found edit page at: ' + page.url());
          await snap('04_edit_direct');
          editClicked = true;
          break;
        }
      }
    }

    await snap('05_current_state');
    log.push('Current URL: ' + page.url());

    // ── 3. Get all page content / form fields ─────────────────────────────────
    const pageContent = await page.content();
    fs.writeFileSync('/root/.openclaw/workspace/saashub_page.html', pageContent);
    log.push('Page HTML saved to saashub_page.html');

    // Check what forms/inputs exist
    const inputs = await page.$$eval('input, select, textarea', els =>
      els.map(el => ({
        tag: el.tagName,
        type: el.type,
        name: el.name,
        id: el.id,
        placeholder: el.placeholder,
        value: el.value ? el.value.substring(0, 50) : ''
      }))
    );
    log.push('Form inputs found: ' + JSON.stringify(inputs));

  } catch (e) {
    errors.push('Error: ' + e.message);
    log.push('Stack: ' + e.stack);
    await snap('error_state');
  }

  await browser.close();

  const report = { log, errors };
  fs.writeFileSync('/root/.openclaw/workspace/saashub_report.json', JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report, null, 2));
})();
