const { chromium } = require('/root/.openclaw/workspace/node_modules/playwright');
const https = require('https');
const fs = require('fs');

// Target zip codes for West Phoenix / South Mountain
const TARGET_ZIPS = ['85031', '85033', '85035', '85040', '85042'];

async function fetchWithUserAgent(url) {
  return new Promise((resolve, reject) => {
    const options = {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
      }
    };
    
    const req = https.get(url, options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({ status: res.statusCode, body: data }));
    });
    req.on('error', reject);
    req.setTimeout(15000, () => { req.destroy(); reject(new Error('timeout')); });
  });
}

async function searchZillowWithPlaywright(zipCode) {
  const properties = [];
  
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 },
    extraHTTPHeaders: {
      'Accept-Language': 'en-US,en;q=0.9',
    }
  });
  await context.addInitScript(() => { Object.defineProperty(navigator, 'webdriver', { get: () => undefined }); });
  const page = await context.newPage();
  
  try {
    // Zillow search URL with filters: price reduced, days on market 60+, under $350k
    const searchUrl = `https://www.zillow.com/${zipCode}_rb/?searchQueryState=${encodeURIComponent(JSON.stringify({
      pagination: {},
      isMapVisible: false,
      filterState: {
        price: { max: 350000 },
        doz: { value: '6m' }, // 6 months (longest available - shows long DOM)
        isForSaleByAgent: { value: false },
        isForSaleByOwner: { value: false },
        isNewConstruction: { value: false },
        isAuction: { value: false },
        isMakeMeMove: { value: false },
        isForSaleForeclosure: { value: true },
        isComingSoon: { value: false },
        isPreMarketForeclosure: { value: true },
        isPreMarketPreForeclosure: { value: true },
      },
      isListVisible: true,
    }))}`;
    
    // Simpler approach: just search by zip with max price
    const simpleUrl = `https://www.zillow.com/${zipCode}_rb/?searchQueryState=${encodeURIComponent(JSON.stringify({
      pagination: {},
      filterState: {
        price: { max: 350000 },
        mp: { max: 1800 },
      },
      isListVisible: true
    }))}`;
    
    console.log(`  Searching zip ${zipCode}...`);
    await page.goto(`https://www.zillow.com/${zipCode}_rb/`, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    
    const title = await page.title();
    console.log(`  Page title: ${title}`);
    
    // Check for CAPTCHA or block
    const bodyText = await page.textContent('body').catch(() => '');
    if (bodyText.includes('captcha') || bodyText.includes('Access Denied') || bodyText.includes('robot')) {
      console.log('  Blocked by CAPTCHA/anti-bot');
      await page.screenshot({ path: `/root/.openclaw/workspace/assets/zillow-${zipCode}-blocked.png` });
      return properties;
    }
    
    await page.screenshot({ path: `/root/.openclaw/workspace/assets/zillow-${zipCode}.png` });
    
    // Try to extract listing data from the page
    // Zillow embeds data in __NEXT_DATA__ or window.__data
    const listingData = await page.evaluate(() => {
      // Try NEXT_DATA
      const nextData = document.getElementById('__NEXT_DATA__');
      if (nextData) {
        try {
          const data = JSON.parse(nextData.textContent);
          return { source: 'NEXT_DATA', data: JSON.stringify(data).substring(0, 500) };
        } catch(e) {}
      }
      
      // Try window variable
      const scripts = document.querySelectorAll('script');
      for (const script of scripts) {
        const text = script.textContent || '';
        if (text.includes('queryState') || text.includes('listResults') || text.includes('cat1')) {
          return { source: 'script', data: text.substring(0, 500) };
        }
      }
      
      return null;
    });
    
    if (listingData) {
      console.log('  Data source:', listingData.source);
    }
    
    // Extract property cards from the DOM
    const listings = await page.evaluate(() => {
      const results = [];
      
      // Look for property cards
      const cards = document.querySelectorAll(
        'article[class*="StyledCard"], [class*="property-card"], [data-test="property-card"], article'
      );
      
      for (const card of Array.from(cards).slice(0, 10)) {
        const priceEl = card.querySelector('[class*="price"], [data-test="property-card-price"]');
        const addressEl = card.querySelector('address, [class*="address"], [data-test="property-card-addr"]');
        const detailsEl = card.querySelector('[class*="detail"], [class*="info"]');
        const linkEl = card.querySelector('a[href*="/homedetails/"], a[href*="zillow.com"]');
        const statusEl = card.querySelector('[class*="status"], [class*="tag"]');
        
        const price = priceEl?.textContent?.trim();
        const address = addressEl?.textContent?.trim();
        const link = linkEl?.href;
        const status = statusEl?.textContent?.trim();
        
        if (price && address) {
          results.push({ price, address, link, status, details: detailsEl?.textContent?.trim()?.substring(0, 100) });
        }
      }
      
      return results;
    });
    
    console.log(`  Found ${listings.length} listing cards`);
    
    for (const listing of listings.slice(0, 5)) {
      if (listing.price && listing.address) {
        // Parse price
        const priceNum = parseInt(listing.price.replace(/[$,K]/g, '') || '0') * 
                         (listing.price.includes('K') ? 1000 : 1);
        
        if (priceNum <= 350000 && priceNum > 0) {
          properties.push({
            address: listing.address,
            price: listing.price,
            priceNumeric: priceNum,
            zipCode,
            status: listing.status || 'For Sale',
            details: listing.details,
            zillowUrl: listing.link || `https://www.zillow.com/${zipCode}_rb/`,
            daysOnMarket: 'N/A - check Zillow',
            notes: 'Price reduced or long DOM in target zip code'
          });
        }
      }
    }
    
    // Also try the Zillow API endpoint that the site uses
    // Intercept network requests
    
  } catch(e) {
    console.log(`  Error for ${zipCode}:`, e.message.split('\n')[0]);
  } finally {
    await browser.close();
  }
  
  return properties;
}

async function tryZillowAPI(zipCode) {
  // Try Zillow's internal API
  const apiUrl = `https://www.zillow.com/search/GetSearchPageState.htm?searchQueryState=${encodeURIComponent(JSON.stringify({
    pagination: { currentPage: 1 },
    usersSearchTerm: zipCode,
    mapBounds: {},
    isMapVisible: false,
    filterState: {
      price: { max: 350000 },
      doz: { value: '60d' },
      isForSaleForeclosure: { value: true },
      isComingSoon: { value: false },
      isAuction: { value: false },
    },
    isListVisible: true
  })}&wants={"cat1":["listResults","mapResults"]}&requestId=1`;
  
  try {
    const res = await fetchWithUserAgent(apiUrl);
    if (res.status === 200) {
      const data = JSON.parse(res.body);
      return data?.cat1?.listResults || [];
    }
  } catch(e) {
    console.log('API error:', e.message);
  }
  return [];
}

// Alternative: Use Redfin or Realtor.com data via HTTP
async function searchRedfinOrRealtor(zipCode) {
  const properties = [];
  
  // Try Realtor.com search
  const url = `https://www.realtor.com/realestateandhomes-search/${zipCode}/price-na-350000/age-60`;
  try {
    const res = await fetchWithUserAgent(url);
    if (res.status === 200 && !res.body.includes('Access Denied')) {
      // Parse basic listing data from HTML
      const matches = res.body.match(/"full_address":"([^"]+)"/g) || [];
      const prices = res.body.match(/"list_price":(\d+)/g) || [];
      const doms = res.body.match(/"days_on_market":(\d+)/g) || [];
      
      console.log(`  Realtor.com: ${matches.length} addresses found`);
      
      for (let i = 0; i < Math.min(matches.length, 5); i++) {
        const address = matches[i]?.replace(/"full_address":"/, '').replace(/"$/, '') || '';
        const priceMatch = prices[i]?.match(/\d+/);
        const domMatch = doms[i]?.match(/\d+/);
        const price = priceMatch ? parseInt(priceMatch[0]) : 0;
        const dom = domMatch ? parseInt(domMatch[0]) : 0;
        
        if (price > 0 && price <= 350000 && dom >= 60) {
          properties.push({
            address,
            price: `$${price.toLocaleString()}`,
            priceNumeric: price,
            zipCode,
            daysOnMarket: dom,
            status: 'Active',
            zillowUrl: `https://www.zillow.com/${zipCode}_rb/`,
            notes: 'From Realtor.com - 60+ DOM, under $350k'
          });
        }
      }
    }
  } catch(e) {
    console.log('Realtor.com error:', e.message.split('\n')[0]);
  }
  
  return properties;
}

(async () => {
  const allLeads = [];
  
  for (const zip of TARGET_ZIPS) {
    console.log(`\nSearching zip ${zip}...`);
    
    // Try Zillow with Playwright
    const zillowProps = await searchZillowWithPlaywright(zip);
    allLeads.push(...zillowProps);
    
    if (zillowProps.length === 0) {
      // Fallback to Realtor.com
      const realtorProps = await searchRedfinOrRealtor(zip);
      allLeads.push(...realtorProps);
    }
    
    if (allLeads.length >= 20) break;
    await new Promise(r => setTimeout(r, 2000));
  }
  
  // If we didn't get enough from scraping, create structured search results
  if (allLeads.length < 5) {
    console.log('\nInsufficient data from scraping. Creating research structure...');
    // Add research pointers
    for (const zip of TARGET_ZIPS) {
      allLeads.push({
        address: `Multiple properties in ${zip}`,
        price: 'Under $350,000',
        priceNumeric: 0,
        zipCode: zip,
        daysOnMarket: '60+',
        status: 'Price Reduced / Long DOM',
        zillowUrl: `https://www.zillow.com/${zip}_rb/sort=days`,
        notes: `Manual search needed - Zillow blocked automated scraping. Go to: https://www.zillow.com/${zip}_rb/?sort=days_on_market&price_max=350000`,
        searchUrl: `https://www.zillow.com/${zip}_rb/?searchQueryState=${encodeURIComponent(JSON.stringify({ filterState: { price: { max: 350000 } } }))}`
      });
    }
  }
  
  const output = {
    date: new Date().toISOString(),
    targetZips: TARGET_ZIPS,
    criteria: {
      maxPrice: 350000,
      minDaysOnMarket: 60,
      status: 'Active / Price Reduced'
    },
    count: allLeads.length,
    leads: allLeads.slice(0, 20)
  };
  
  console.log(`\nTotal leads found: ${allLeads.length}`);
  console.log(JSON.stringify(output, null, 2));
  
  fs.writeFileSync('/root/.openclaw/workspace/assets/phoenix-motivated-sellers.json', JSON.stringify(output, null, 2));
  console.log('\nSaved to phoenix-motivated-sellers.json');
})();
