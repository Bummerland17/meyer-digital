/**
 * Explore the actual submission flows on each site
 */
const { chromium } = require('/root/.openclaw/workspace/node_modules/playwright');
const path = require('path');

const SCREENSHOTS_DIR = '/root/.openclaw/workspace/assets/screenshots';
let sc = 0;
async function ss(page, label) {
  sc++;
  const fname = `ex-${String(sc).padStart(3,'0')}-${label.replace(/[^a-z0-9]/gi,'-').substring(0,60)}.png`;
  await page.screenshot({ path: path.join(SCREENSHOTS_DIR, fname), fullPage: true }).catch(() => {});
  console.log(`📸 ${fname}`);
}
async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function main() {
  const browser = await chromium.launch({
    headless: true, slowMo: 50,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });
  
  // ========== BETALIST ==========
  {
    console.log('\n=== BETALIST.COM EXPLORATION ===');
    const ctx = await browser.newContext();
    const page = await ctx.newPage();
    
    await page.goto('https://betalist.com', { timeout: 30000 });
    await sleep(2000);
    await ss(page, 'bl-home');
    
    // Find the "Submit Startup" link
    const submitLinks = await page.$$eval('a', els => 
      els.filter(el => el.textContent?.toLowerCase().includes('submit'))
         .map(el => ({ text: el.textContent?.trim(), href: el.href }))
    );
    console.log('Submit links on BL home:', JSON.stringify(submitLinks));
    
    // Check what the login form looks like more carefully
    await page.goto('https://betalist.com/sign_in', { timeout: 30000 });
    await sleep(2000);
    
    // Get all forms
    const forms = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('form')).map(f => ({
        action: f.action,
        method: f.method,
        id: f.id,
        class: f.className.substring(0, 100),
        inputs: Array.from(f.querySelectorAll('input, button, textarea')).map(i => ({
          tag: i.tagName, type: i.type, name: i.name, id: i.id, value: i.value?.substring(0,20)
        }))
      }));
    });
    console.log('BL Forms:', JSON.stringify(forms, null, 2));
    
    await ctx.close();
  }
  
  // ========== SAASHUB ==========
  {
    console.log('\n=== SAASHUB.COM EXPLORATION ===');
    const ctx = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    });
    const page = await ctx.newPage();
    
    await page.goto('https://www.saashub.com', { timeout: 30000, waitUntil: 'domcontentloaded' });
    await sleep(3000);
    await ss(page, 'sh-home');
    
    // Find Submit Product link
    const navLinks = await page.$$eval('a', els =>
      els.map(el => ({ text: el.textContent?.trim().substring(0, 30), href: el.href }))
         .filter(l => l.text && l.href?.includes('saashub'))
    );
    console.log('SH nav links:', JSON.stringify(navLinks));
    
    // Click Submit Product
    const submitBtn = await page.$('a:has-text("Submit Product"), a:has-text("Submit a Product")');
    if (submitBtn) {
      const href = await submitBtn.getAttribute('href');
      console.log('Submit Product href:', href);
      
      await submitBtn.click();
      await sleep(3000);
      await ss(page, 'sh-after-submit-click');
      console.log('After Submit Product click URL:', page.url());
      
      const text = await page.evaluate(() => document.body.innerText.substring(0, 500));
      console.log('Text:', text.substring(0, 300));
    }
    
    await ctx.close();
  }
  
  // ========== TOOLIFY ==========
  {
    console.log('\n=== TOOLIFY.AI EXPLORATION ===');
    const ctx = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    });
    const page = await ctx.newPage();
    
    await page.goto('https://www.toolify.ai/submit', { timeout: 30000, waitUntil: 'domcontentloaded' });
    await sleep(3000);
    await ss(page, 'tf-submit-overview');
    
    // Find all clickable links/buttons on submit page
    const links = await page.$$eval('a[href]', els =>
      els.map(el => ({ text: el.textContent?.trim().substring(0, 40), href: el.href }))
         .filter(l => l.text && l.href?.includes('toolify'))
    );
    console.log('TF submit page links:', JSON.stringify(links));
    
    // Find "Submit AI" specifically
    const submitAiLink = await page.$('a:has-text("Submit AI"), a[href*="submit-ai"], a[href*="submit/ai"]');
    if (submitAiLink) {
      const href = await submitAiLink.getAttribute('href');
      console.log('Submit AI link:', href);
      await submitAiLink.click();
      await sleep(2000);
      await ss(page, 'tf-after-submit-ai-link');
      console.log('After Submit AI link URL:', page.url());
    } else {
      // Try to find Submit AI as card/button
      const allButtons = await page.$$eval('button, [role="button"], div[class*="card"]', els =>
        els.map(el => ({ 
          tag: el.tagName,
          text: el.textContent?.trim().substring(0, 50),
          class: el.className.substring(0, 50)
        })).filter(b => b.text?.toLowerCase().includes('submit'))
      );
      console.log('Submit buttons:', JSON.stringify(allButtons));
    }
    
    // Check what happens after clicking one of the "Submit AI" options
    await page.goto('https://www.toolify.ai/submit', { timeout: 30000, waitUntil: 'domcontentloaded' });
    await sleep(2000);
    
    // Click on first item/card that says "Submit AI"  
    const submitAiCard = await page.$('text=Submit AI');
    if (submitAiCard) {
      await submitAiCard.click();
      await sleep(2000);
      await ss(page, 'tf-after-submit-ai-card-click');
      console.log('After Submit AI card click URL:', page.url());
      
      // Get page structure
      const inputs = await page.$$eval('input, textarea', els =>
        els.map(el => ({ type: el.type, name: el.name, id: el.id, placeholder: el.placeholder }))
      );
      console.log('Inputs after click:', JSON.stringify(inputs));
      
      const text = await page.evaluate(() => document.body.innerText.substring(0, 500));
      console.log('Page text:', text.substring(0, 300));
    }
    
    // Try to find the actual submit tool form
    const possibleUrls = [
      'https://www.toolify.ai/ai-submit',
      'https://www.toolify.ai/submit/ai',
      'https://www.toolify.ai/submit/tool',
      'https://www.toolify.ai/add-ai',
    ];
    
    for (const url of possibleUrls) {
      await page.goto(url, { timeout: 15000, waitUntil: 'domcontentloaded' }).catch(() => {});
      await sleep(1000);
      const text = await page.evaluate(() => document.body.innerText.substring(0, 100));
      if (!text.includes('404') && !text.includes('Page not found')) {
        console.log('Found valid URL:', url, text.substring(0, 50));
        await ss(page, `tf-valid-url-${url.replace(/https?:\/\//,'').replace(/\//g,'-')}`);
      }
    }
    
    await ctx.close();
  }
  
  await browser.close();
}

main().catch(console.error);
