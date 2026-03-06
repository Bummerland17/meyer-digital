const { chromium } = require('/root/.openclaw/workspace/node_modules/playwright');
const fs = require('fs');

// Search BiggerPockets forums for Phoenix cash buyers
async function findBuyersOnBiggerPockets() {
  const buyers = [];
  
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 }
  });
  const page = await context.newPage();
  
  try {
    // Search BiggerPockets for Phoenix cash buyers in forums
    const searchUrls = [
      'https://www.biggerpockets.com/search#slug=phoenix+cash+buyer&type=forum_post',
      'https://www.biggerpockets.com/forums/search?q=phoenix+cash+buyer',
      'https://www.biggerpockets.com/forums?q=phoenix+investor',
    ];
    
    for (const url of searchUrls) {
      try {
        console.log('Trying:', url);
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 20000 });
        await page.waitForTimeout(3000);
        
        const pageTitle = await page.title();
        console.log('  Title:', pageTitle);
        await page.screenshot({ path: `/root/.openclaw/workspace/assets/bp-${searchUrls.indexOf(url)}.png` });
        
        // Extract forum post data
        const posts = await page.evaluate(() => {
          const results = [];
          
          // Look for forum post items
          const postEls = document.querySelectorAll(
            'article, .forum-post, .search-result, [class*="post"], [class*="thread"], [class*="result"]'
          );
          
          for (const el of Array.from(postEls).slice(0, 20)) {
            const text = el.textContent || '';
            // Only include Phoenix-related posts about investing/buying
            if ((text.toLowerCase().includes('phoenix') || text.toLowerCase().includes('az')) &&
                (text.toLowerCase().includes('buy') || text.toLowerCase().includes('invest') || 
                 text.toLowerCase().includes('cash') || text.toLowerCase().includes('deal'))) {
              
              // Try to get user info
              const authorEl = el.querySelector('[class*="author"], [class*="user"], [class*="name"], a[href*="/users/"], a[href*="/profile/"]');
              const titleEl = el.querySelector('h2, h3, h4, .title, [class*="title"]');
              const linkEl = el.querySelector('a[href*="/forums/"]');
              
              results.push({
                author: authorEl?.textContent?.trim()?.substring(0, 50),
                authorHref: authorEl?.href,
                title: titleEl?.textContent?.trim()?.substring(0, 100),
                postLink: linkEl?.href,
                snippet: text.substring(0, 200).trim()
              });
            }
          }
          
          return results;
        });
        
        console.log(`  Found ${posts.length} relevant posts`);
        
        if (posts.length > 0) {
          for (const post of posts.slice(0, 10)) {
            if (post.author || post.title) {
              buyers.push({
                source: 'BiggerPockets Forum',
                name: post.author || 'Unknown',
                username: post.authorHref?.split('/users/')[1]?.split('?')[0] || 
                          post.authorHref?.split('/profile/')[1]?.split('?')[0] || '',
                contact: post.authorHref || '',
                postTitle: post.title || '',
                postUrl: post.postLink || url,
                snippet: post.snippet?.substring(0, 150),
                notes: 'Found via BiggerPockets forum search for Phoenix investors'
              });
            }
          }
        }
        
        if (buyers.length >= 10) break;
        
      } catch(e) {
        console.log('  Error on', url, ':', e.message.split('\n')[0]);
      }
    }
    
    // Try direct forum pages
    if (buyers.length < 5) {
      const forumPages = [
        'https://www.biggerpockets.com/forums/51', // Real Estate Investing subforum
        'https://www.biggerpockets.com/forums/52',
        'https://www.biggerpockets.com/forums/48-Wholesale-Real-Estate',
      ];
      
      for (const url of forumPages) {
        try {
          console.log('Trying forum:', url);
          await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 20000 });
          await page.waitForTimeout(2000);
          
          const posts = await page.evaluate(() => {
            const results = [];
            const links = document.querySelectorAll('a[href*="/forums/"]');
            for (const link of Array.from(links).slice(0, 30)) {
              const text = (link.textContent || '').toLowerCase();
              if (text.includes('phoenix') || text.includes('arizona') || text.includes('az ')) {
                results.push({
                  title: link.textContent.trim().substring(0, 100),
                  url: link.href
                });
              }
            }
            return results;
          });
          
          console.log(`  Phoenix-related threads: ${posts.length}`);
          
          for (const post of posts.slice(0, 5)) {
            if (post.title) {
              try {
                await page.goto(post.url, { waitUntil: 'domcontentloaded', timeout: 15000 });
                await page.waitForTimeout(1500);
                
                // Extract users from thread
                const users = await page.evaluate(() => {
                  const userLinks = document.querySelectorAll('a[href*="/users/"], a[href*="/profile/"]');
                  return Array.from(new Set(
                    Array.from(userLinks).map(a => ({
                      name: a.textContent.trim().substring(0, 40),
                      href: a.href
                    })).filter(u => u.name && u.name.length > 1)
                      .map(JSON.stringify)
                  )).map(JSON.parse).slice(0, 5);
                });
                
                for (const user of users) {
                  if (!buyers.some(b => b.contact === user.href)) {
                    buyers.push({
                      source: 'BiggerPockets',
                      name: user.name,
                      username: user.href.split('/users/')[1]?.split('/')[0] || user.href.split('/profile/')[1]?.split('/')[0] || '',
                      contact: user.href,
                      postTitle: post.title,
                      postUrl: post.url,
                      notes: 'Active in Phoenix real estate forum thread'
                    });
                  }
                }
                
                if (buyers.length >= 10) break;
              } catch(e2) {
                console.log('  Thread error:', e2.message.split('\n')[0]);
              }
            }
          }
          
          if (buyers.length >= 10) break;
        } catch(e) {
          console.log('  Forum error:', e.message.split('\n')[0]);
        }
      }
    }
    
  } finally {
    await browser.close();
  }
  
  return buyers;
}

(async () => {
  console.log('Searching BiggerPockets for Phoenix cash buyers...');
  const buyers = await findBuyersOnBiggerPockets();
  
  console.log(`\nFound ${buyers.length} potential buyers`);
  console.log(JSON.stringify(buyers, null, 2));
  
  fs.writeFileSync(
    '/root/.openclaw/workspace/assets/phoenix-buyers.json',
    JSON.stringify({ 
      source: 'BiggerPockets forum search',
      date: new Date().toISOString(),
      count: buyers.length,
      buyers 
    }, null, 2)
  );
  
  console.log('Saved to phoenix-buyers.json');
})();
