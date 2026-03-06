const { chromium } = require('playwright');

const GOOGLE_EMAIL = 'olcowboy21@gmail.com';
const GOOGLE_PASSWORD = 'Bummerland20';

const PRODUCTS = {
  pantrymate: {
    name: 'PantryMate',
    url: 'https://pantrymate.net',
    tagline: 'Scan your pantry, get dinner suggestions in 30 seconds',
    description: 'PantryMate is an AI-powered meal planning app that scans your pantry or grocery receipt and tells you what meals you can cook tonight based on what you already have. No "go buy 8 more ingredients" recipes — just practical dinner decisions in 30 seconds. Free tier available, Pro Plus $14.99/mo or $49 lifetime.',
    category: 'AI, Food & Cooking, Productivity',
    tags: 'meal planning, pantry, cooking, food waste, AI, recipe suggestions',
    email: 'hello@pantrymate.net'
  },
  unitfix: {
    name: 'UnitFix',
    url: 'https://unitfix.app',
    tagline: 'Maintenance tracking for small landlords — tenants submit via link, no account needed',
    description: 'UnitFix is a maintenance request tracker for small landlords managing 1-20 units. Each unit gets a unique public URL. Tenants submit requests without creating an account. Landlord sees everything in one dashboard with status tracking, notes, and full history. Free for 1 unit, $29/mo for up to 5 units.',
    category: 'Productivity, Real Estate, Property Management',
    tags: 'landlord, property management, maintenance, real estate, tenants',
    email: 'hello@pantrymate.net'
  }
};

const SITES = [
  { name: 'saashub.com', url: 'https://www.saashub.com', submitPath: '/add-product', hasGoogleAuth: true },
  { name: 'betalist.com', url: 'https://betalist.com', submitPath: '/startups/new', hasGoogleAuth: true },
  { name: 'alternativeto.net', url: 'https://alternativeto.net', submitPath: '/add/', hasGoogleAuth: false },
  { name: 'toolify.ai', url: 'https://www.toolify.ai', submitPath: '/submit-tool', hasGoogleAuth: true },
  { name: 'uneed.be', url: 'https://www.uneed.be', submitPath: '/submit', hasGoogleAuth: true },
];

async function handleGoogleSignIn(page) {
  try {
    // Click Google sign in button
    const googleBtns = [
      'button:has-text("Google")',
      'a:has-text("Google")', 
      '[class*="google"]',
      'button:has-text("Sign in with Google")',
      'a:has-text("Sign in with Google")',
    ];
    
    for (const sel of googleBtns) {
      const btn = page.locator(sel).first();
      if (await btn.count() > 0 && await btn.isVisible()) {
        await btn.click();
        await page.waitForTimeout(2000);
        break;
      }
    }

    // Handle Google OAuth popup/redirect
    const emailField = page.locator('input[type="email"]').first();
    if (await emailField.count() > 0) {
      await emailField.fill(GOOGLE_EMAIL);
      await page.keyboard.press('Enter');
      await page.waitForTimeout(2000);
      
      const pwField = page.locator('input[type="password"]').first();
      if (await pwField.count() > 0) {
        await pwField.fill(GOOGLE_PASSWORD);
        await page.keyboard.press('Enter');
        await page.waitForTimeout(3000);
      }
    }
    return true;
  } catch(e) {
    return false;
  }
}

async function submitToSite(browser, site, product) {
  const page = await browser.newPage();
  const result = { site: site.name, product: product.name, status: '❌ failed', detail: '' };
  
  try {
    await page.goto(site.url + site.submitPath, { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(2000);

    // Try to log in / sign up
    const signInLinks = page.locator('a:has-text("Sign in"), a:has-text("Login"), a:has-text("Register"), button:has-text("Sign up")').first();
    if (await signInLinks.count() > 0) {
      await signInLinks.click();
      await page.waitForTimeout(1500);
      await handleGoogleSignIn(page);
      await page.waitForTimeout(2000);
      // Navigate back to submit
      await page.goto(site.url + site.submitPath, { waitUntil: 'domcontentloaded', timeout: 15000 });
      await page.waitForTimeout(2000);
    }

    // Try to fill the submission form
    const filled = await fillForm(page, product);
    if (filled) {
      result.status = '✅ submitted';
      result.detail = page.url();
    } else {
      result.status = '⚠️ form not found';
      result.detail = page.url();
    }
  } catch(e) {
    result.detail = e.message.slice(0, 100);
  } finally {
    await page.close();
  }
  return result;
}

async function fillForm(page, product) {
  const fields = {
    name: ['input[name*="name" i]', 'input[placeholder*="name" i]', 'input[id*="name" i]'],
    url: ['input[name*="url" i]', 'input[placeholder*="url" i]', 'input[type="url"]'],
    tagline: ['input[name*="tagline" i]', 'input[name*="short" i]', 'input[placeholder*="tagline" i]'],
    description: ['textarea[name*="desc" i]', 'textarea[placeholder*="desc" i]', 'textarea'],
    email: ['input[type="email"]', 'input[name*="email" i]'],
  };

  let filled = false;
  
  for (const [field, selectors] of Object.entries(fields)) {
    for (const sel of selectors) {
      try {
        const el = page.locator(sel).first();
        if (await el.count() > 0 && await el.isVisible()) {
          const val = field === 'name' ? product.name :
                     field === 'url' ? product.url :
                     field === 'tagline' ? product.tagline :
                     field === 'description' ? product.description :
                     field === 'email' ? product.email : '';
          await el.fill(val);
          filled = true;
          break;
        }
      } catch {}
    }
  }

  if (filled) {
    // Try submit
    for (const sel of ['button[type="submit"]', 'input[type="submit"]', 'button:has-text("Submit")', 'button:has-text("Add")']) {
      try {
        const btn = page.locator(sel).first();
        if (await btn.count() > 0 && await btn.isVisible()) {
          await btn.click();
          await page.waitForTimeout(3000);
          return true;
        }
      } catch {}
    }
  }
  return false;
}

(async () => {
  console.log('🚀 Directory Submitter — Starting\n');
  const browser = await chromium.launch({ headless: true });
  const results = [];

  for (const site of SITES) {
    for (const [key, product] of Object.entries(PRODUCTS)) {
      process.stdout.write(`${site.name} → ${product.name}... `);
      const r = await submitToSite(browser, site, product);
      console.log(r.status);
      results.push(r);
      await new Promise(res => setTimeout(res, 2000));
    }
  }

  await browser.close();

  const success = results.filter(r => r.status.includes('✅')).length;
  console.log(`\n✅ ${success}/${results.length} submissions completed`);
  
  require('fs').writeFileSync(
    '/root/.openclaw/workspace/assets/directory-results.json',
    JSON.stringify(results, null, 2)
  );
})();
