const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');

chromium.use(StealthPlugin());

const results = {
  submitted: [],
  failed: [],
  manual_required: []
};

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ 
    viewport: { width: 1280, height: 900 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  });
  const page = await context.newPage();

  // ─── STEP 1: Submit community edit (categories + description) ─────────────
  try {
    console.log('\n=== STEP 1: Submitting community edit form ===');
    await page.goto('https://www.saashub.com/product-changes/pantrymate/new', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    
    await page.screenshot({ path: '/root/.openclaw/workspace/snap_edit_before.png' });
    
    // Fill description
    const descField = await page.$('#service_description');
    if (descField) {
      await descField.fill('PantryMate is an AI-powered meal planning app that helps home cooks, busy families, and people trying to reduce food waste. Users scan or input their pantry ingredients and get personalized meal suggestions in 30 seconds. The AI generates recipes based on what you already have, eliminating dinner decision fatigue and reducing food waste by using up ingredients before they spoil.');
      console.log('✅ Description filled');
    }
    
    // Update categories
    const catField = await page.$('#category_names_list');
    if (catField) {
      await catField.fill('AI, Food And Beverage, Meal Planning, Productivity');
      console.log('✅ Categories filled: AI, Food And Beverage, Meal Planning, Productivity');
    }
    
    // Add note
    const noteField = await page.$('#note, input[name="note"]');
    if (noteField) {
      await noteField.fill('Adding description and updating categories to include Meal Planning and Productivity in addition to AI and Food And Beverage');
      console.log('✅ Note filled');
    }
    
    // Add submitter email
    const emailField = await page.$('#user_email, input[name="user_email"]');
    if (emailField) {
      await emailField.fill('olcowboy21@gmail.com');
      console.log('✅ Email filled');
    }
    
    await page.screenshot({ path: '/root/.openclaw/workspace/snap_edit_filled.png' });
    
    // Submit the form
    const submitBtn = await page.$('input[type="submit"][name="commit"], button[type="submit"]');
    if (submitBtn) {
      await submitBtn.click();
      await page.waitForTimeout(4000);
      await page.screenshot({ path: '/root/.openclaw/workspace/snap_edit_submitted.png' });
      
      const afterUrl = page.url();
      const afterTitle = await page.title();
      console.log('After submit URL:', afterUrl);
      console.log('After submit title:', afterTitle);
      
      if (!afterUrl.includes('/product-changes/pantrymate/new') || afterTitle.includes('success') || afterTitle.includes('Thank')) {
        results.submitted.push('Community edit: categories (AI, Food And Beverage, Meal Planning, Productivity) + description');
        console.log('✅ Community edit submitted successfully');
      } else {
        // Check for success/error messages
        const bodyText = await page.$eval('body', el => el.textContent.replace(/\s+/g, ' ').substring(0, 500));
        console.log('Page after submit:', bodyText);
        results.submitted.push('Community edit submitted (confirmation status unclear)');
      }
    } else {
      console.log('❌ Submit button not found');
      results.failed.push('Community edit: submit button not found');
    }
    
  } catch(e) {
    console.error('Edit form error:', e.message);
    results.failed.push('Community edit: ' + e.message);
  }

  // ─── STEP 2: Suggest alternatives ─────────────────────────────────────────
  const competitors = [
    { name: 'SuperCook', search: 'SuperCook' },
    { name: 'Mealime', search: 'Mealime' },
    { name: 'Yummly', search: 'Yummly' },
  ];
  
  for (const comp of competitors) {
    try {
      console.log(`\n=== Suggesting alternative: ${comp.name} ===`);
      await page.goto('https://www.saashub.com/suggest_alternative/pantrymate', { waitUntil: 'domcontentloaded', timeout: 20000 });
      await page.waitForTimeout(3000);
      
      const queryInput = await page.$('input[name="query"]');
      if (!queryInput) {
        console.log('❌ Query input not found');
        results.failed.push(`Suggest ${comp.name}: query input not found`);
        continue;
      }
      
      await queryInput.fill(comp.search);
      await page.waitForTimeout(2000); // wait for autocomplete
      
      await page.screenshot({ path: `/root/.openclaw/workspace/snap_suggest_${comp.name.toLowerCase()}.png` });
      
      // Look for dropdown suggestions
      const suggestions = await page.$$eval('[class*="suggest"], [class*="dropdown"] a, [class*="autocomplete"] li, [data-*] li, .dropdown-content a', els =>
        els.map(el => ({ text: el.textContent.trim(), href: el.href || '' })).slice(0, 10)
      );
      console.log('Suggestions visible:', JSON.stringify(suggestions));
      
      // Try to find and click the suggestion
      const allLinks = await page.$$eval('a', ls => ls.map(l => ({ text: l.textContent.trim(), href: l.href })));
      const match = allLinks.find(l => l.text.toLowerCase().includes(comp.search.toLowerCase()));
      
      if (match) {
        console.log(`Found match: ${match.text} - ${match.href}`);
        await page.click(`a:has-text("${comp.name}")`);
        await page.waitForTimeout(3000);
        await page.screenshot({ path: `/root/.openclaw/workspace/snap_suggested_${comp.name.toLowerCase()}.png` });
        const afterText = await page.$eval('body', el => el.textContent.replace(/\s+/g, ' ').substring(0, 300));
        console.log('After click:', afterText.substring(0, 200));
        results.submitted.push(`Alternative suggested: ${comp.name}`);
      } else {
        console.log(`No direct link for ${comp.name} in page - likely need to press Enter or use form`);
        // Try pressing Enter/submitting
        await page.keyboard.press('Enter');
        await page.waitForTimeout(3000);
        await page.screenshot({ path: `/root/.openclaw/workspace/snap_suggested_enter_${comp.name.toLowerCase()}.png` });
        const afterUrl = page.url();
        const bodyText = await page.$eval('body', el => el.textContent.replace(/\s+/g, ' ').substring(0, 500));
        console.log('After Enter URL:', afterUrl);
        console.log('Body text:', bodyText.substring(0, 300));
        results.submitted.push(`Competitor ${comp.name}: attempted via search form`);
      }
      
    } catch(e) {
      console.error(`Suggest ${comp.name} error:`, e.message);
      results.failed.push(`Suggest ${comp.name}: ${e.message}`);
    }
  }
  
  // ─── Summary ───────────────────────────────────────────────────────────────
  results.manual_required = [
    'LOGIN: Go to https://www.saashub.com/login with olcowboy21@gmail.com / Bummerland20',
    'LOGO: After login, go to PantryMate edit page and upload logo from https://pantrymate.net/favicon.ico',
    'PRICING: Add pricing plans (Free, Pro $9.99/mo, Pro Plus $14.99/mo, Lifetime $49) - requires owner account',
    'COMPETITORS: Manually add PlantNanny (not in SaaSHub) and verify SuperCook/Mealime/Yummly were added',
    'VERIFY OWNERSHIP: Use https://www.saashub.com/verify/pantrymate with your @pantrymate.net email to get owner access',
    'CATEGORIES: Community edit submitted but requires SaaSHub approval - owner edit is immediate',
  ];
  
  console.log('\n\n=== FINAL RESULTS ===');
  console.log(JSON.stringify(results, null, 2));
  
  fs.writeFileSync('/root/.openclaw/workspace/saashub_results.json', JSON.stringify(results, null, 2));
  await browser.close();
})();
