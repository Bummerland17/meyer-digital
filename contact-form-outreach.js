const { chromium } = require('playwright');
const fs = require('fs');

const PITCH = {
  name: 'Wolfgang Meyer',
  email: 'hello@pantrymate.net',
  phone: '',
  subject: 'AI Appointment Booking — Question for Your Practice',
  message: `Hi there,

I help dental practices set up AI phone agents that answer calls and book appointments 24/7 — including after hours when patients call and get voicemail.

Most practices lose 3-5 bookings per week to missed calls. At $200-500 per appointment, that's real money walking out the door every day.

Setup takes 48 hours. Flat rate of $497/month, no contracts. I'd love to show you a 2-minute demo.

Would anyone on your team be open to a quick look?

— Wolfgang Meyer
hello@pantrymate.net`
};

const DENTAL_SITES = [
  { name: 'Downtown Smiles Phoenix', url: 'http://downtownsmilesphx.com' },
  { name: 'Downtown Phoenix Dental', url: 'https://www.downtownphoenixdental.com' },
  { name: 'Healing Dentistry', url: 'http://healingdentistry.com' },
  { name: 'Brighter Way Dental', url: 'https://www.brighterwaydentalcenter.org' },
  { name: 'McDowell Road Family Dentistry', url: 'http://www.1010mrd.com' },
  { name: 'City Creek Dental', url: 'http://citycreekdental.com' },
  { name: 'SunDrop Dental', url: 'https://www.sundropslc.com' },
  { name: 'Lakeside Dental', url: 'http://mylakesidedental.com' },
  { name: 'Dental Elements Denver', url: 'https://dentalelements.com' },
  { name: 'Idaho Street Dental', url: 'http://idahostreetdental.com' },
  { name: 'Capitol Dental Boise', url: 'https://capitoldental.com' },
  { name: 'Metropolitan Dental Denver', url: 'https://www.metrodentalcare.com' },
  { name: 'Wynkoop Dentistry', url: 'https://denverwynkoopdentist.com' },
];

const CONTACT_PATHS = ['/contact', '/contact-us', '/contact-us/', '/about/contact', '/appointments', '/book', '/new-patient'];

const FORM_SELECTORS = {
  name: ['input[name*="name" i]:not([name*="last" i]):not([name*="first" i])', 'input[placeholder*="name" i]', 'input[id*="name" i]'],
  firstName: ['input[name*="first" i]', 'input[id*="first" i]', 'input[placeholder*="first" i]'],
  lastName: ['input[name*="last" i]', 'input[id*="last" i]', 'input[placeholder*="last" i]'],
  email: ['input[type="email"]', 'input[name*="email" i]', 'input[placeholder*="email" i]'],
  phone: ['input[type="tel"]', 'input[name*="phone" i]', 'input[placeholder*="phone" i]'],
  subject: ['input[name*="subject" i]', 'input[placeholder*="subject" i]', 'input[id*="subject" i]'],
  message: ['textarea[name*="message" i]', 'textarea[placeholder*="message" i]', 'textarea[id*="message" i]', 'textarea'],
};

async function tryFill(page, selectors, value) {
  for (const sel of selectors) {
    try {
      const el = page.locator(sel).first();
      if (await el.count() > 0 && await el.isVisible()) {
        await el.fill(value);
        return true;
      }
    } catch {}
  }
  return false;
}

async function findAndFillForm(page, siteName) {
  // Try to find message textarea (key indicator of a contact form)
  for (const sel of FORM_SELECTORS.message) {
    try {
      const el = page.locator(sel).first();
      if (await el.count() > 0 && await el.isVisible()) {
        // Found a form — fill it
        await tryFill(page, FORM_SELECTORS.name, PITCH.name);
        await tryFill(page, FORM_SELECTORS.firstName, 'Wolfgang');
        await tryFill(page, FORM_SELECTORS.lastName, 'Meyer');
        await tryFill(page, FORM_SELECTORS.email, PITCH.email);
        await tryFill(page, FORM_SELECTORS.phone, '');
        await tryFill(page, FORM_SELECTORS.subject, PITCH.subject);
        await el.fill(PITCH.message);
        
        // Find submit button
        const submitSelectors = [
          'button[type="submit"]',
          'input[type="submit"]',
          'button:has-text("Send")',
          'button:has-text("Submit")',
          'button:has-text("Contact")',
        ];
        
        for (const btnSel of submitSelectors) {
          try {
            const btn = page.locator(btnSel).first();
            if (await btn.count() > 0 && await btn.isVisible()) {
              await btn.click();
              await page.waitForTimeout(2000);
              return 'submitted';
            }
          } catch {}
        }
        return 'form_found_no_submit';
      }
    } catch {}
  }
  return 'no_form';
}

async function processsite(browser, site) {
  const page = await browser.newPage();
  try {
    // Try contact page paths
    for (const path of ['', ...CONTACT_PATHS]) {
      try {
        const url = site.url + path;
        await page.goto(url, { timeout: 10000, waitUntil: 'domcontentloaded' });
        await page.waitForTimeout(1500);
        
        const result = await findAndFillForm(page, site.name);
        if (result === 'submitted') {
          return { site: site.name, status: '✅ Form submitted', url };
        } else if (result === 'form_found_no_submit') {
          return { site: site.name, status: '⚠️ Form found, no submit button', url };
        }
      } catch {}
    }
    return { site: site.name, status: '❌ No contact form found' };
  } finally {
    await page.close();
  }
}

(async () => {
  console.log('🦷 SmartBook AI — Contact Form Outreach\n');
  
  const browser = await chromium.launch({ headless: true });
  const results = [];
  
  for (const site of DENTAL_SITES) {
    process.stdout.write(`Processing ${site.name}... `);
    const result = await processsite(browser, site);
    console.log(result.status);
    results.push(result);
    await new Promise(r => setTimeout(r, 2000));
  }
  
  await browser.close();
  
  const submitted = results.filter(r => r.status.includes('✅')).length;
  console.log(`\n📊 Done: ${submitted}/${results.length} contact forms submitted`);
  
  fs.writeFileSync('/root/.openclaw/workspace/assets/contact-form-results.json', 
    JSON.stringify(results, null, 2));
})();
