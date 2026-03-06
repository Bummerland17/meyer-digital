/**
 * SmartBook AI - Vapi Outbound Call Launcher
 * Reads from /root/.openclaw/workspace/assets/call-queue.json
 * and dispatches calls via the Vapi API.
 *
 * Usage: node vapi-start-calls.js [--dry-run] [--limit=10]
 * 
 * SAFETY: Only runs during Mon-Fri 9am-5pm business hours for each lead's timezone.
 * Current safe UTC window: 16:00-00:00 UTC (Mountain 9am-5pm) or 17:00-01:00 UTC (Pacific 9am-5pm)
 */

const fs = require('fs');
const path = require('path');

// Load env
const envPath = '/root/.openclaw/workspace/.env';
const env = {};
fs.readFileSync(envPath, 'utf8').split('\n').forEach(line => {
  const [k, v] = line.split('=');
  if (k && v) env[k.trim()] = v.trim();
});

const API_KEY = env.VAPI_API_KEY;
const ASSISTANT_ID = env.VAPI_ASSISTANT_ID;
const PHONE_ID = env.VAPI_PHONE_ID;

if (!API_KEY || !ASSISTANT_ID || !PHONE_ID) {
  console.error('❌ Missing credentials. Run vapi-deploy.sh first.');
  console.error('  Need: VAPI_API_KEY, VAPI_ASSISTANT_ID, VAPI_PHONE_ID in .env');
  process.exit(1);
}

const args = process.argv.slice(2);
const DRY_RUN = args.includes('--dry-run');
const limitArg = args.find(a => a.startsWith('--limit='));
const LIMIT = limitArg ? parseInt(limitArg.split('=')[1]) : 999;

const QUEUE_PATH = '/root/.openclaw/workspace/assets/call-queue.json';
const queue = JSON.parse(fs.readFileSync(QUEUE_PATH, 'utf8'));

// Check business hours (9am-5pm) for a given timezone
function isBusinessHours(timezone) {
  const now = new Date();
  const localTime = new Date(now.toLocaleString('en-US', { timeZone: timezone }));
  const hour = localTime.getHours();
  const day = localTime.getDay(); // 0=Sun, 6=Sat
  return day >= 1 && day <= 5 && hour >= 9 && hour < 17;
}

async function makeCall(lead) {
  const body = {
    assistantId: ASSISTANT_ID,
    phoneNumberId: PHONE_ID,
    customer: {
      number: lead.phone,
      name: lead.business_name,
    },
    assistantOverrides: {
      variableValues: {
        business_name: lead.business_name,
        business_type: lead.type,
        city: lead.city,
      }
    }
  };

  if (DRY_RUN) {
    console.log(`[DRY RUN] Would call ${lead.business_name} at ${lead.phone}`);
    return { id: 'dry-run-' + Date.now(), status: 'queued' };
  }

  const response = await fetch('https://api.vapi.ai/call', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`API error ${response.status}: ${err}`);
  }

  return response.json();
}

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function main() {
  console.log('🚀 SmartBook AI - Vapi Call Launcher');
  console.log('=====================================');
  if (DRY_RUN) console.log('⚠️  DRY RUN MODE - no actual calls will be made');
  console.log(`📋 Queue: ${queue.length} leads`);
  console.log(`📞 Assistant: ${ASSISTANT_ID}`);
  console.log(`📱 Phone: ${PHONE_ID}`);
  console.log('');

  const eligible = queue.filter(lead => {
    if (lead.status !== 'queued') return false;
    if (!isBusinessHours(lead.local_timezone)) {
      console.log(`⏰ Skipping ${lead.business_name} — outside business hours (${lead.local_timezone})`);
      return false;
    }
    return true;
  }).slice(0, LIMIT);

  console.log(`✅ ${eligible.length} leads eligible for calling now`);
  console.log('');

  let success = 0, failed = 0;

  for (const lead of eligible) {
    try {
      console.log(`📞 Calling ${lead.business_name} (${lead.phone})...`);
      const result = await makeCall(lead);
      lead.status = 'called';
      lead.call_id = result.id;
      lead.called_at = new Date().toISOString();
      console.log(`   ✅ Call queued: ${result.id}`);
      success++;
    } catch (err) {
      console.log(`   ❌ Failed: ${err.message}`);
      lead.status = 'failed';
      lead.error = err.message;
      failed++;
    }

    // Rate limit: 1 call per 3 seconds
    await sleep(3000);
  }

  // Save updated queue
  fs.writeFileSync(QUEUE_PATH, JSON.stringify(queue, null, 2));

  console.log('');
  console.log('=================');
  console.log(`✅ Done: ${success} calls placed, ${failed} failed`);
  console.log(`📋 Queue updated: ${QUEUE_PATH}`);
  console.log(`📊 Monitor: https://dashboard.vapi.ai/calls`);
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
