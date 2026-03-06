#!/usr/bin/env node
/**
 * StreetView Scout — Virtual Driving for Dollars
 * Usage: node streetview-scout.js addresses.txt
 * Or pipe: echo "123 Main St, Phoenix AZ" | node streetview-scout.js
 *
 * Pulls Street View images for each address and saves them to ./scout-output/
 * Use to visually screen distressed properties without leaving your desk.
 */

const https = require('https');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const API_KEY = 'AIzaSyAuBYyoyqOvNalVNrnff1giboFsG_tXGfI';
const OUTPUT_DIR = path.join(__dirname, 'scout-output');
const SIZE = '640x480';
const FOV = '90';   // field of view — higher = wider angle
const PITCH = '-10'; // slightly down to see yard/foundation

// Distress indicators to look for (manual review checklist printed with each image)
const CHECKLIST = [
  '□ Overgrown lawn / dead grass',
  '□ Peeling paint / broken gutters',
  '□ Boarded windows or plywood',
  '□ Tarp on roof',
  '□ No curtains / no furniture visible',
  '□ Newspapers / mail piling up',
  '□ For Rent sign on vacant property',
  '□ Dumpster / debris in yard',
];

function geocode(address) {
  // Uses Places "Find Place from Text" API (no separate enable needed)
  return new Promise((resolve, reject) => {
    const encoded = encodeURIComponent(address);
    const url = `https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=${encoded}&inputtype=textquery&fields=geometry,formatted_address,name&key=${API_KEY}`;
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        const json = JSON.parse(data);
        if (json.status === 'OK' && json.candidates && json.candidates.length > 0) {
          const loc = json.candidates[0].geometry.location;
          const formatted = json.candidates[0].formatted_address || json.candidates[0].name || address;
          resolve({ lat: loc.lat, lng: loc.lng, formatted });
        } else {
          reject(new Error(`Geocode failed for "${address}": ${json.status}`));
        }
      });
    }).on('error', reject);
  });
}

function checkStreetViewAvailability(lat, lng) {
  return new Promise((resolve) => {
    const url = `https://maps.googleapis.com/maps/api/streetview/metadata?location=${lat},${lng}&key=${API_KEY}`;
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        const json = JSON.parse(data);
        resolve(json.status === 'OK');
      });
    }).on('error', () => resolve(false));
  });
}

function downloadStreetView(lat, lng, outputPath, heading = '0') {
  return new Promise((resolve, reject) => {
    const url = `https://maps.googleapis.com/maps/api/streetview?size=${SIZE}&location=${lat},${lng}&fov=${FOV}&pitch=${PITCH}&heading=${heading}&key=${API_KEY}`;
    const file = fs.createWriteStream(outputPath);
    https.get(url, (res) => {
      res.pipe(file);
      file.on('finish', () => { file.close(); resolve(); });
    }).on('error', reject);
  });
}

function sanitizeFilename(str) {
  return str.replace(/[^a-z0-9]/gi, '_').substring(0, 60);
}

async function processAddress(address, index, total) {
  console.log(`\n[${index + 1}/${total}] ${address}`);
  
  try {
    // Geocode
    const { lat, lng, formatted } = await geocode(address);
    console.log(`  ✓ Geocoded: ${formatted}`);

    // Check availability
    const available = await checkStreetViewAvailability(lat, lng);
    if (!available) {
      console.log(`  ⚠ No Street View available — skip`);
      return { address, status: 'no_streetview', formatted };
    }

    // Download 2 angles: front + side
    const slug = sanitizeFilename(address);
    const frontPath = path.join(OUTPUT_DIR, `${String(index + 1).padStart(3, '0')}_${slug}_FRONT.jpg`);
    const sidePath = path.join(OUTPUT_DIR, `${String(index + 1).padStart(3, '0')}_${slug}_SIDE.jpg`);
    const notesPath = path.join(OUTPUT_DIR, `${String(index + 1).padStart(3, '0')}_${slug}_NOTES.txt`);

    await downloadStreetView(lat, lng, frontPath, '0');
    await downloadStreetView(lat, lng, sidePath, '90');

    // Write checklist notes file
    const notes = [
      `ADDRESS: ${formatted}`,
      `COORDS: ${lat}, ${lng}`,
      `SCREENED: ${new Date().toISOString()}`,
      `GOOGLE MAPS: https://www.google.com/maps?q=${lat},${lng}`,
      `STREET VIEW: https://www.google.com/maps/@${lat},${lng},3a,90y,0h,-10t/data=!3m4!1e1`,
      '',
      'DISTRESS CHECKLIST (mark what you see):',
      ...CHECKLIST,
      '',
      'PRIORITY: [ ] Hot  [ ] Warm  [ ] Skip',
      'NOTES: ',
    ].join('\n');

    fs.writeFileSync(notesPath, notes);
    console.log(`  ✓ Saved: front + side view + checklist`);
    return { address, status: 'ok', formatted, lat, lng, frontPath, sidePath };

  } catch (err) {
    console.log(`  ✗ Error: ${err.message}`);
    return { address, status: 'error', error: err.message };
  }
}

async function main() {
  // Create output dir
  if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  let addresses = [];

  // Read from file arg or stdin
  const inputFile = process.argv[2];
  if (inputFile && fs.existsSync(inputFile)) {
    addresses = fs.readFileSync(inputFile, 'utf8')
      .split('\n')
      .map(l => l.trim())
      .filter(l => l && !l.startsWith('#'));
  } else if (!process.stdin.isTTY) {
    const rl = readline.createInterface({ input: process.stdin });
    for await (const line of rl) {
      if (line.trim() && !line.startsWith('#')) addresses.push(line.trim());
    }
  } else {
    // Demo mode — Phoenix distressed zip code addresses
    console.log('No input file provided. Running demo with Phoenix sample addresses...\n');
    addresses = [
      '1423 W McDowell Rd, Phoenix, AZ 85007',
      '3201 W Van Buren St, Phoenix, AZ 85009',
      '2845 W Thomas Rd, Phoenix, AZ 85017',
      '4102 S 35th Ave, Phoenix, AZ 85041',
      '1867 E Broadway Rd, Phoenix, AZ 85040',
    ];
  }

  console.log(`\n🏠 StreetView Scout — Virtual Driving for Dollars`);
  console.log(`📍 Processing ${addresses.length} addresses`);
  console.log(`📁 Output: ${OUTPUT_DIR}`);
  console.log(`💰 Est. cost: $${((addresses.length * 2) / 1000 * 7).toFixed(2)} (Street View) + $${(addresses.length / 1000 * 5).toFixed(2)} (Geocoding)\n`);

  const results = [];
  for (let i = 0; i < addresses.length; i++) {
    const result = await processAddress(addresses[i], i, addresses.length);
    results.push(result);
    // Small delay to avoid rate limiting
    if (i < addresses.length - 1) await new Promise(r => setTimeout(r, 200));
  }

  // Summary
  const ok = results.filter(r => r.status === 'ok').length;
  const noSV = results.filter(r => r.status === 'no_streetview').length;
  const errors = results.filter(r => r.status === 'error').length;

  console.log(`\n${'='.repeat(50)}`);
  console.log(`DONE`);
  console.log(`✓ ${ok} properties screened`);
  console.log(`⚠ ${noSV} no Street View available`);
  console.log(`✗ ${errors} errors`);
  console.log(`\nOpen scout-output/ to review photos + checklists.`);
  console.log(`Each property has: FRONT.jpg + SIDE.jpg + NOTES.txt`);
  console.log(`Mark each as Hot / Warm / Skip then prioritize your calls.`);

  // Write summary JSON
  const summaryPath = path.join(OUTPUT_DIR, '_summary.json');
  fs.writeFileSync(summaryPath, JSON.stringify({ 
    runDate: new Date().toISOString(),
    total: addresses.length, ok, noSV, errors, results 
  }, null, 2));
}

main().catch(console.error);
