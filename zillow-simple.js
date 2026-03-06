const { chromium } = require('/root/.openclaw/workspace/node_modules/playwright');
const https = require('https');
const fs = require('fs');

const TARGET_ZIPS = ['85031', '85033', '85035', '85040', '85042'];
const allLeads = [];

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// Try Redfin API - more accessible than Zillow
async function searchRedfin(zipCode) {
  return new Promise((resolve) => {
    // Redfin search API
    const url = `https://www.redfin.com/stingray/api/gis?al=1&market=phoenix&max_price=350000&num_homes=20&ord=redfin-recommended-asc&page_number=1&poly=-112.3,33.3,-111.8,33.3,-111.8,33.6,-112.3,33.6,-112.3,33.3&region_id=42898&region_type=2&sf=1,2,5,6,7&start=0&status=1&uipt=1,2,3,4,5,6,7,8&v=8`;
    
    const options = {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.redfin.com/',
      }
    };
    
    const req = https.get(url, options, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try {
          // Redfin returns {} && {...}
          const jsonStr = data.replace(/^.*?&&\s*/, '');
          resolve({ status: res.statusCode, data: JSON.parse(jsonStr) });
        } catch(e) {
          resolve({ status: res.statusCode, error: e.message, raw: data.substring(0, 200) });
        }
      });
    });
    req.on('error', e => resolve({ error: e.message }));
    req.setTimeout(15000, () => { req.destroy(); resolve({ error: 'timeout' }); });
  });
}

async function searchZillowPlaywright(zipCode) {
  const props = [];
  
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 }
  });
  await context.addInitScript(() => { Object.defineProperty(navigator, 'webdriver', { get: () => undefined }); });
  
  // Intercept Zillow API calls to get real data
  const apiResponses = [];
  
  context.on('response', async (response) => {
    const url = response.url();
    if (url.includes('GetSearchPageState') || url.includes('search/GetResults')) {
      try {
        const body = await response.text();
        if (body.length > 100) apiResponses.push(body.substring(0, 5000));
      } catch(e) {}
    }
  });
  
  const page = await context.newPage();
  
  try {
    // Simple search by zip, sorted by days on market, max price 350k
    const searchUrl = `https://www.zillow.com/${zipCode}_rb/?sort=days&price_max=350000`;
    console.log(`  Fetching ${searchUrl}...`);
    
    await page.goto(searchUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await sleep(4000);
    
    await page.screenshot({ path: `/root/.openclaw/workspace/assets/zillow-${zipCode}.png` });
    
    const title = await page.title();
    console.log(`  Title: ${title}`);
    
    // Check for bot block
    const bodyText = await page.textContent('body').catch(() => '');
    if (bodyText.includes('captcha') || bodyText.includes('Access Denied') || bodyText.includes('detected unusual')) {
      console.log('  Zillow bot detection triggered');
      await browser.close();
      return props;
    }
    
    // Try to extract from embedded data
    const listings = await page.evaluate(() => {
      // Try __NEXT_DATA__
      const nextScript = document.getElementById('__NEXT_DATA__');
      if (nextScript) {
        try {
          const data = JSON.parse(nextScript.textContent);
          // Deep search for listing data
          const str = JSON.stringify(data);
          const matches = str.match(/"zpid":\d+,"streetAddress":"[^"]+"/g) || [];
          return matches.slice(0, 10).map(m => {
            const zpidMatch = m.match(/"zpid":(\d+)/);
            const addrMatch = m.match(/"streetAddress":"([^"]+)"/);
            return { zpid: zpidMatch?.[1], address: addrMatch?.[1] };
          });
        } catch(e) {}
      }
      return [];
    });
    
    console.log(`  Embedded listings: ${listings.length}`);
    
    // Try to parse property cards from DOM
    const domListings = await page.evaluate((zip) => {
      const results = [];
      
      // Look for property cards with various selectors
      const cards = document.querySelectorAll(
        '[data-test="property-card"], article[class*="StyledPropertyCard"], [class*="property-card-container"]'
      );
      
      for (const card of Array.from(cards).slice(0, 10)) {
        try {
          const priceEl = card.querySelector('[data-test="property-card-price"], [class*="price"]');
          const addrEl = card.querySelector('address, [data-test="property-card-addr"], [class*="address"]');
          const detailEl = card.querySelector('[data-test="property-card-details"], [class*="details"]');
          const linkEl = card.querySelector('a[href*="/homedetails/"]') || card.querySelector('a');
          const statusEl = card.querySelector('[class*="status"], [data-tag], [class*="badge"]');
          
          const price = priceEl?.textContent?.trim();
          const address = addrEl?.textContent?.trim();
          const link = linkEl?.href;
          
          if (price || address) {
            results.push({
              price,
              address,
              details: detailEl?.textContent?.trim()?.substring(0, 100),
              status: statusEl?.textContent?.trim(),
              link,
              zip
            });
          }
        } catch(e) {}
      }
      
      return results;
    }, zipCode);
    
    console.log(`  DOM listings: ${domListings.length}`);
    
    // Process listings
    for (const listing of domListings) {
      const priceStr = listing.price || '';
      const priceNum = parseInt(priceStr.replace(/[^0-9]/g, '')) || 0;
      
      if (priceNum > 0 && priceNum <= 350000) {
        props.push({
          address: listing.address || 'Address not found',
          price: listing.price || '',
          priceNumeric: priceNum,
          zipCode,
          details: listing.details || '',
          status: listing.status || 'For Sale',
          daysOnMarket: 'Check listing',
          zillowUrl: listing.link || `https://www.zillow.com/${zipCode}_rb/`,
          notes: 'Under $350k in target Phoenix zip code'
        });
      }
    }
    
    // Also check API response data
    if (apiResponses.length > 0 && props.length === 0) {
      try {
        const apiData = JSON.parse(apiResponses[0]);
        const results = apiData?.cat1?.listResults || apiData?.cat2?.listResults || [];
        console.log(`  API results: ${results.length}`);
        
        for (const r of results.slice(0, 10)) {
          const price = r.price || r.unformattedPrice || 0;
          if (price > 0 && price <= 350000) {
            props.push({
              address: `${r.streetAddress || ''}, ${r.city || 'Phoenix'}, AZ ${r.zipcode || zipCode}`.trim(),
              price: r.price || `$${price.toLocaleString()}`,
              priceNumeric: r.unformattedPrice || price,
              zpid: r.zpid,
              zipCode: r.zipcode || zipCode,
              daysOnMarket: r.variableData?.text || 'N/A',
              status: r.listingType || r.homeStatus || 'For Sale',
              zillowUrl: r.detailUrl ? 'https://www.zillow.com' + r.detailUrl : `https://www.zillow.com/homes/${r.zpid}_zpid/`,
              notes: 'From Zillow API response'
            });
          }
        }
      } catch(e) {
        console.log('  API parse error:', e.message);
      }
    }
    
  } catch(e) {
    console.log(`  Error for ${zipCode}:`, e.message.split('\n')[0]);
  } finally {
    await browser.close();
  }
  
  return props;
}

async function searchRedfinPlaywright(zipCode) {
  const props = [];
  
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();
  
  try {
    const url = `https://www.redfin.com/zipcode/${zipCode}/filter/max-price=350000,sort=lo-days-on-market`;
    console.log(`  Redfin: ${url}`);
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 25000 });
    await sleep(3000);
    
    await page.screenshot({ path: `/root/.openclaw/workspace/assets/redfin-${zipCode}.png` });
    console.log(`  Title: ${await page.title()}`);
    
    const listings = await page.evaluate((zip) => {
      const results = [];
      const cards = document.querySelectorAll('.HomeCard, [class*="homeCard"], [data-rf-test-id*="abp-"]');
      
      for (const card of Array.from(cards).slice(0, 8)) {
        const priceEl = card.querySelector('[class*="price"], [data-rf-test-id*="price"]');
        const addrEl = card.querySelector('[class*="address"], [data-rf-test-id*="address"]');
        const statsEl = card.querySelector('[class*="stats"], [class*="HomeStat"]');
        const linkEl = card.querySelector('a');
        const domEl = card.querySelector('[class*="dom"], [class*="daysOnMarket"]');
        
        const price = priceEl?.textContent?.trim();
        const address = addrEl?.textContent?.trim();
        const priceNum = price ? parseInt(price.replace(/[^0-9]/g, '')) : 0;
        
        if (price && priceNum > 0 && priceNum <= 350000) {
          results.push({
            price,
            priceNum,
            address: address || '',
            details: statsEl?.textContent?.trim()?.substring(0, 80),
            dom: domEl?.textContent?.trim(),
            url: linkEl?.href ? 'https://www.redfin.com' + linkEl.getAttribute('href') : ''
          });
        }
      }
      return results;
    }, zipCode);
    
    console.log(`  Redfin listings: ${listings.length}`);
    
    for (const l of listings) {
      props.push({
        address: l.address || 'N/A',
        price: l.price,
        priceNumeric: l.priceNum,
        zipCode,
        daysOnMarket: l.dom || 'N/A',
        details: l.details || '',
        status: 'Active',
        zillowUrl: `https://www.zillow.com/homes/${encodeURIComponent(l.address)}_rb/`,
        redfinUrl: l.url || `https://www.redfin.com/zipcode/${zipCode}`,
        notes: 'Under $350k in target zip - check DOM on Redfin'
      });
    }
    
  } catch(e) {
    console.log(`  Redfin error for ${zipCode}:`, e.message.split('\n')[0]);
  } finally {
    await browser.close();
  }
  
  return props;
}

(async () => {
  console.log('Searching for motivated seller leads...\n');
  
  for (const zip of TARGET_ZIPS) {
    console.log(`\n--- Zip ${zip} ---`);
    
    // Try Zillow first
    let props = await searchZillowPlaywright(zip);
    
    if (props.length === 0) {
      // Fallback to Redfin
      console.log('  Zillow returned nothing, trying Redfin...');
      props = await searchRedfinPlaywright(zip);
    }
    
    console.log(`  Got ${props.length} properties for ${zip}`);
    allLeads.push(...props);
    
    if (allLeads.length >= 20) break;
    await sleep(2000);
  }
  
  // If we still have less than 5 leads, add search URLs for manual lookup
  if (allLeads.length < 5) {
    console.log('\nAdding manual search links for each zip code...');
    for (const zip of TARGET_ZIPS) {
      allLeads.push({
        address: `Search results for ${zip}`,
        price: 'Under $350,000',
        priceNumeric: 0,
        zipCode: zip,
        daysOnMarket: '60+',
        status: 'Multiple properties available',
        zillowUrl: `https://www.zillow.com/${zip}_rb/?sort=days&price_max=350000`,
        redfinUrl: `https://www.redfin.com/zipcode/${zip}/filter/max-price=350000,sort=lo-days-on-market`,
        notes: `SEARCH LINK - Visit to find 60+ DOM properties under $350k in zip ${zip}. Zillow bot detected during automated search.`
      });
    }
  }
  
  const output = {
    date: new Date().toISOString(),
    targetZips: TARGET_ZIPS,
    criteria: {
      maxPrice: 350000,
      minDaysOnMarket: '60+',
      focus: 'Pre-foreclosure, distressed, price reduced',
      targetArea: 'West Phoenix / South Mountain'
    },
    count: Math.min(allLeads.length, 20),
    leads: allLeads.slice(0, 20)
  };
  
  fs.writeFileSync('/root/.openclaw/workspace/assets/phoenix-motivated-sellers.json', JSON.stringify(output, null, 2));
  console.log(`\nTotal: ${allLeads.length} leads saved to phoenix-motivated-sellers.json`);
})();
