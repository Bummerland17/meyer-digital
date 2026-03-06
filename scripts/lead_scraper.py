#!/usr/bin/env python3
"""
Caribbean + Philippines Tourism Lead Scraper
Hits Google Places API for all business categories, fetches details, scores leads.
"""

import json, time, os, sys, hashlib
import urllib.request, urllib.parse
from datetime import datetime

PLACES_KEY = "AIzaSyAuBYyoyqOvNalVNrnff1giboFsG_tXGfI"
BRAVE_KEY  = "BSA106jyrhl-5L1J4pkHQrw8H0BcesL"

OUTDIR = "/root/.openclaw/workspace/real-estate"
RESDIR = "/root/.openclaw/workspace/research"
os.makedirs(OUTDIR, exist_ok=True)
os.makedirs(RESDIR, exist_ok=True)

TODAY = "2026-03-05"

# ── Business categories ──────────────────────────────────────────────────────
# Each: (query_term, business_category, place_type_hint)
CATEGORIES = [
    # Lodging
    ("boutique hotel",          "hotel",         "lodging"),
    ("guesthouse",              "guesthouse",     "lodging"),
    ("eco lodge",               "eco_lodge",      "lodging"),
    ("villa rental",            "villa",          "lodging"),
    ("yoga retreat",            "spa_retreat",    "lodging"),
    ("destination spa",         "spa_retreat",    "spa"),
    # Tours & Activities
    ("tour operator",           "tour_operator",  "travel_agency"),
    ("boat charter",            "boat_charter",   "travel_agency"),
    ("dive shop",               "dive_shop",      "establishment"),
    ("snorkel tour",            "water_activity", "travel_agency"),
    ("fishing charter",         "fishing_charter","travel_agency"),
    ("surfing school",          "surf_school",    "establishment"),
    ("zip line",                "activity",       "amusement_park"),
    ("ATV tour",                "activity",       "travel_agency"),
    ("horseback riding",        "activity",       "establishment"),
    ("cultural tour",           "tour_operator",  "travel_agency"),
    ("kayak rental",            "water_activity", "establishment"),
    # Transport
    ("car rental",              "car_rental",     "car_rental"),
    ("airport transfer",        "transport",      "travel_agency"),
    ("private shuttle",         "transport",      "travel_agency"),
    # Food & Events
    ("restaurant tourist",      "restaurant",     "restaurant"),
    ("wedding venue",           "wedding_venue",  "establishment"),
]

# ── Search locations ─────────────────────────────────────────────────────────
CARIBBEAN_LOCATIONS = [
    ("Trinidad",          "Trinidad",          "Trinidad and Tobago"),
    ("Tobago",            "Tobago",             "Trinidad and Tobago"),
    ("Saint Lucia",       "Saint Lucia",        "Saint Lucia"),
    ("Grenada",           "Grenada",            "Grenada"),
    ("Barbados",          "Barbados",           "Barbados"),
    ("Belize",            "Belize",             "Belize"),
    ("Nassau Bahamas",    "Nassau",             "Bahamas"),
    ("Jamaica",           "Jamaica",            "Jamaica"),
    ("Antigua",           "Antigua",            "Antigua and Barbuda"),
]

PHILIPPINES_LOCATIONS = [
    ("El Nido Palawan",   "El Nido",            "Philippines"),
    ("Coron Palawan",     "Coron",              "Philippines"),
    ("Siargao",           "Siargao",            "Philippines"),
    ("Bohol Philippines", "Bohol",              "Philippines"),
    ("Dumaguete Philippines","Dumaguete",        "Philippines"),
    ("Boracay Philippines","Boracay",            "Philippines"),
]

ALL_LOCATIONS = [("caribbean", *loc) for loc in CARIBBEAN_LOCATIONS] + \
                [("philippines", *loc) for loc in PHILIPPINES_LOCATIONS]

# ── Chain / large-brand blocklist ────────────────────────────────────────────
CHAIN_BLOCKLIST = [
    "marriott","hilton","sandals","hyatt","ihg","starwood","wyndham",
    "holiday inn","best western","radisson","accor","intercontinental",
    "sheraton","westin","four seasons","ritz","hertz","budget","avis",
    "enterprise","national","alamo","europcar","sixt","padi 5-star",
    "sunwing","riu","iberostar","secrets","excellence","dreams",
    "hard rock","moon palace","bahia principe",
]

def is_chain(name):
    n = name.lower()
    return any(b in n for b in CHAIN_BLOCKLIST)

# ── HTTP helpers ─────────────────────────────────────────────────────────────
def http_get(url, headers=None, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers or {})
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            if attempt == retries - 1:
                print(f"  !! HTTP error: {e} — {url[:80]}", file=sys.stderr)
                return None
            time.sleep(1.5)

def places_text_search(query, location_str):
    q = urllib.parse.quote(f"{query} {location_str}")
    url = (f"https://maps.googleapis.com/maps/api/place/textsearch/json"
           f"?query={q}&key={PLACES_KEY}")
    return http_get(url)

def places_detail(place_id):
    fields = "name,formatted_phone_number,international_phone_number,website,url,rating,user_ratings_total,formatted_address,types,price_level"
    url = (f"https://maps.googleapis.com/maps/api/place/details/json"
           f"?place_id={place_id}&fields={fields}&key={PLACES_KEY}")
    return http_get(url)

def brave_search(query):
    q = urllib.parse.quote(query)
    url = f"https://api.search.brave.com/res/v1/web/search?q={q}&count=5"
    headers = {"X-Subscription-Token": BRAVE_KEY, "Accept": "application/json"}
    return http_get(url, headers=headers)

# ── Scoring logic ────────────────────────────────────────────────────────────
def score_lead(detail, business_category):
    score = 0
    rating = detail.get("rating") or 0
    reviews = detail.get("user_ratings_total") or 0
    website = detail.get("website") or ""
    phone = detail.get("international_phone_number") or detail.get("formatted_phone_number") or ""

    # Low rating = bigger digital gap
    if rating <= 3.5:   score += 30
    elif rating <= 4.0: score += 20
    elif rating <= 4.3: score += 10

    # Few reviews = low visibility
    if reviews < 20:    score += 25
    elif reviews < 50:  score += 15
    elif reviews < 100: score += 10

    # No website = top priority
    if not website:
        score += 40
    elif any(x in website.lower() for x in ["wix","weebly","blogspot","wordpress.com","squarespace","godaddy","yolasite","tripod","geocities"]):
        score += 25  # DIY/bad website
    elif any(x in website.lower() for x in ["booking.com","tripadvisor","airbnb","expedia","viator","yelp","facebook"]):
        score += 35  # They're using an OTA as their "website" — perfect prospect

    # Has phone = contactable
    if phone:
        score += 10

    # Categories more likely to be OTA-dependent
    if business_category in ["tour_operator","boat_charter","dive_shop","fishing_charter",
                              "water_activity","activity","villa","surf_school"]:
        score += 10

    return score

def priority_label(score):
    if score >= 65: return "high"
    if score >= 40: return "medium"
    return "low"

def infer_digital_gaps(detail):
    gaps = []
    website = detail.get("website") or ""
    rating = detail.get("rating") or 0
    reviews = detail.get("user_ratings_total") or 0

    if not website:
        gaps.append("no website found")
    elif any(x in website.lower() for x in ["wix","weebly","wordpress.com","squarespace","godaddy","yolasite"]):
        gaps.append("DIY website builder detected")
    elif any(x in website.lower() for x in ["booking.com","tripadvisor","airbnb","expedia","viator","facebook"]):
        gaps.append("using OTA/platform as primary web presence — paying 15-25% commission")

    if reviews < 20:
        gaps.append(f"very few reviews ({reviews}) — low search visibility")
    elif reviews < 50:
        gaps.append(f"low review count ({reviews}) — SEO opportunity")

    if rating and rating < 4.0:
        gaps.append(f"below-average rating ({rating}) — reputation management needed")

    if not detail.get("international_phone_number"):
        gaps.append("no international phone number listed")

    if not gaps:
        gaps.append("limited digital marketing signals detected")

    return gaps

# ── Main scrape loop ─────────────────────────────────────────────────────────
seen_ids   = set()
seen_names = set()

caribbean_leads  = []
philippines_leads = []

print(f"\n{'='*60}")
print(f"  Caribbean + Philippines Lead Scraper — {TODAY}")
print(f"  {len(ALL_LOCATIONS)} locations × {len(CATEGORIES)} categories")
print(f"{'='*60}\n")

total_api_calls = 0
total_detail_calls = 0

for region, loc_query, island, country in ALL_LOCATIONS:
    print(f"\n▸ {island}, {country}")
    for query_term, biz_cat, _ in CATEGORIES:
        print(f"  → {query_term} ...", end=" ", flush=True)
        result = places_text_search(query_term, loc_query)
        total_api_calls += 1
        time.sleep(0.25)

        if not result or result.get("status") not in ("OK","ZERO_RESULTS"):
            print(f"[{result.get('status','ERR') if result else 'ERR'}]")
            continue

        items = result.get("results", [])
        new_found = 0

        for item in items[:8]:  # up to 8 per query
            pid = item.get("place_id","")
            name = item.get("name","")

            # Deduplicate
            if pid in seen_ids: continue
            seen_ids.add(pid)

            name_key = name.lower().strip()
            if name_key in seen_names: continue
            seen_names.add(name_key)

            # Filter chains
            if is_chain(name): continue

            # Quick rating pre-filter (don't bother fetching details for obvious large chains)
            rating_raw = item.get("rating") or 0
            reviews_raw = item.get("user_ratings_total") or 0

            # Verify it's geographically relevant (basic check)
            addr = item.get("formatted_address","").lower()
            if loc_query.lower().split()[0] not in addr and country.lower() not in addr:
                # Might be a false match from Google
                # Still include if rating suggests it's a small place
                if reviews_raw > 2000:
                    continue  # Large / mismatched result

            # Fetch place details for phone + website
            detail_data = places_detail(pid)
            total_detail_calls += 1
            time.sleep(0.2)

            if not detail_data or detail_data.get("status") != "OK":
                # Fall back to basic data
                detail = {
                    "name": name,
                    "formatted_address": item.get("formatted_address",""),
                    "rating": rating_raw,
                    "user_ratings_total": reviews_raw,
                    "website": "",
                    "international_phone_number": "",
                    "formatted_phone_number": "",
                }
            else:
                detail = detail_data.get("result", {})

            # Re-check chain on full detail
            if is_chain(detail.get("name", name)):
                continue

            rating = detail.get("rating") or rating_raw
            reviews = detail.get("user_ratings_total") or reviews_raw
            website = detail.get("website") or ""
            phone = detail.get("international_phone_number") or detail.get("formatted_phone_number") or ""

            # Quality filter: skip if massive review count (likely large chain)
            if reviews > 3000:
                continue

            # Score
            s = score_lead(detail, biz_cat)
            gaps = infer_digital_gaps(detail)

            lead = {
                "name": detail.get("name") or name,
                "island": island,
                "country": country,
                "region": region,
                "phone": phone,
                "website": website,
                "google_rating": rating if rating else None,
                "review_count": reviews if reviews else 0,
                "business_type": biz_cat,
                "business_category": biz_cat,
                "address": detail.get("formatted_address",""),
                "price_range": None,  # enriched below if possible
                "digital_gap_signals": gaps,
                "score": s,
                "priority": priority_label(s),
                "place_id": pid,
            }

            if region == "caribbean":
                caribbean_leads.append(lead)
            else:
                philippines_leads.append(lead)

            new_found += 1

        print(f"[+{new_found}]")

print(f"\n{'='*60}")
print(f"  API calls: {total_api_calls} text-search, {total_detail_calls} detail")
print(f"  Caribbean raw leads:   {len(caribbean_leads)}")
print(f"  Philippines raw leads: {len(philippines_leads)}")
print(f"{'='*60}\n")

# ── Brave Search enrichment for top no-website leads ─────────────────────────
print("Enriching top no-website leads via Brave Search...")
no_web = [l for l in caribbean_leads + philippines_leads if not l.get("website")][:25]

for lead in no_web:
    query = f'{lead["name"]} {lead["island"]} contact website'
    print(f"  Brave: {lead['name'][:40]}...")
    res = brave_search(query)
    time.sleep(0.5)
    if res and res.get("web",{}).get("results"):
        top = res["web"]["results"][0]
        url = top.get("url","")
        # If we find a real website (not OTA/booking)
        if url and not any(x in url for x in ["tripadvisor","booking.com","yelp","facebook","google","instagram","airbnb"]):
            lead["website"] = url
            lead["digital_gap_signals"].append("website found via search — not in Google Maps listing")
        elif url and any(x in url for x in ["tripadvisor","booking.com","airbnb","viator"]):
            lead["digital_gap_signals"].append("only OTA profiles found in web search")
            if not lead.get("website"):
                lead["website"] = url

print(f"  Enrichment complete.\n")

# ── Sort by score ─────────────────────────────────────────────────────────────
caribbean_leads.sort(key=lambda x: x["score"], reverse=True)
philippines_leads.sort(key=lambda x: x["score"], reverse=True)

# Remove internal score field before saving
def clean_lead(lead):
    l = dict(lead)
    l.pop("score", None)
    l.pop("place_id", None)
    l.pop("region", None)
    return l

caribbean_clean   = [clean_lead(l) for l in caribbean_leads]
philippines_clean = [clean_lead(l) for l in philippines_leads]

# ── Save JSON files ───────────────────────────────────────────────────────────
carib_path = f"{OUTDIR}/caribbean-leads-{TODAY}.json"
phil_path  = f"{OUTDIR}/philippines-leads-{TODAY}.json"

with open(carib_path, "w") as f:
    json.dump(caribbean_clean, f, indent=2)
with open(phil_path, "w") as f:
    json.dump(philippines_clean, f, indent=2)

print(f"✓ Saved {len(caribbean_clean)} Caribbean leads → {carib_path}")
print(f"✓ Saved {len(philippines_clean)} Philippines leads → {phil_path}")

# ── Summary report ─────────────────────────────────────────────────────────────
all_leads = caribbean_leads + philippines_leads
all_leads.sort(key=lambda x: x["score"], reverse=True)
top10 = all_leads[:10]

# Island breakdowns
from collections import Counter
carib_by_island = Counter(l["island"] for l in caribbean_leads)
phil_by_island  = Counter(l["island"] for l in philippines_leads)
carib_by_cat    = Counter(l["business_type"] for l in caribbean_leads)
phil_by_cat     = Counter(l["business_type"] for l in philippines_leads)
carib_by_prio   = Counter(l["priority"] for l in caribbean_leads)
phil_by_prio    = Counter(l["priority"] for l in philippines_leads)

report_lines = [
    f"# Caribbean + Philippines Tourism Lead Report",
    f"**Generated:** {TODAY}  |  **Model:** Google Places API + Brave Search",
    "",
    "---",
    "",
    f"## 📊 Summary",
    "",
    f"| Metric | Caribbean | Philippines | Total |",
    f"|--------|-----------|-------------|-------|",
    f"| Total leads | {len(caribbean_leads)} | {len(philippines_leads)} | {len(all_leads)} |",
    f"| High priority | {carib_by_prio.get('high',0)} | {phil_by_prio.get('high',0)} | {carib_by_prio.get('high',0)+phil_by_prio.get('high',0)} |",
    f"| Medium priority | {carib_by_prio.get('medium',0)} | {phil_by_prio.get('medium',0)} | {carib_by_prio.get('medium',0)+phil_by_prio.get('medium',0)} |",
    f"| Low priority | {carib_by_prio.get('low',0)} | {phil_by_prio.get('low',0)} | {carib_by_prio.get('low',0)+phil_by_prio.get('low',0)} |",
    f"| No website found | {sum(1 for l in caribbean_leads if not l.get('website'))} | {sum(1 for l in philippines_leads if not l.get('website'))} | {sum(1 for l in all_leads if not l.get('website'))} |",
    "",
    "---",
    "",
    "## 🌴 Caribbean — Breakdown by Island",
    "",
    "| Island | Leads |",
    "|--------|-------|",
]
for island, count in sorted(carib_by_island.items(), key=lambda x: -x[1]):
    report_lines.append(f"| {island} | {count} |")

report_lines += [
    "",
    "## 🌴 Caribbean — Breakdown by Business Category",
    "",
    "| Category | Leads |",
    "|----------|-------|",
]
for cat, count in sorted(carib_by_cat.items(), key=lambda x: -x[1]):
    report_lines.append(f"| {cat} | {count} |")

report_lines += [
    "",
    "---",
    "",
    "## 🏝️ Philippines — Breakdown by Island",
    "",
    "| Island | Leads |",
    "|--------|-------|",
]
for island, count in sorted(phil_by_island.items(), key=lambda x: -x[1]):
    report_lines.append(f"| {island} | {count} |")

report_lines += [
    "",
    "## 🏝️ Philippines — Breakdown by Business Category",
    "",
    "| Category | Leads |",
    "|----------|-------|",
]
for cat, count in sorted(phil_by_cat.items(), key=lambda x: -x[1]):
    report_lines.append(f"| {cat} | {count} |")

report_lines += [
    "",
    "---",
    "",
    "## 🎯 Top 10 Highest Priority Leads",
    "",
]

for i, lead in enumerate(top10, 1):
    gaps_str = "; ".join(lead.get("digital_gap_signals",[])[:3])
    report_lines += [
        f"### {i}. {lead['name']}",
        f"**Location:** {lead['island']}, {lead['country']}  ",
        f"**Category:** {lead['business_type']}  ",
        f"**Contact:** {lead.get('phone') or '—'}  ",
        f"**Website:** {lead.get('website') or '❌ None found'}  ",
        f"**Rating:** {lead.get('google_rating') or '—'} ({lead.get('review_count',0)} reviews)  ",
        f"**Priority:** {lead['priority'].upper()}  ",
        f"**Why:** {gaps_str}",
        "",
    ]

report_lines += [
    "---",
    "",
    "## 💡 Pitch Angle by Category",
    "",
    "| Category | Core Pitch |",
    "|----------|------------|",
    "| Hotels/Guesthouses | Direct bookings = no 15% Booking.com commission |",
    "| Tour Operators | Viator takes 20-30%; own site = full margin |",
    "| Dive/Water Activities | Rank #1 for 'scuba diving [island]' on Google |",
    "| Car Rentals | Beat TravelJoy/Rentalcars on local search |",
    "| Restaurants (tourist zones) | Google Business + TripAdvisor SEO = walk-ins |",
    "| Wedding Venues | High-intent couples search Google, not platforms |",
    "| Villas | Airbnb 3% host + 14% guest = 17% per booking lost |",
    "| Spas/Retreats | Direct retreat bookings = no ClassPass/OTA cut |",
    "",
    "---",
    f"*Files: `caribbean-leads-{TODAY}.json` | `philippines-leads-{TODAY}.json`*",
]

report_path = f"{RESDIR}/caribbean-philippines-leads-summary.md"
with open(report_path, "w") as f:
    f.write("\n".join(report_lines))

print(f"✓ Saved summary report → {report_path}")
print(f"\n🏁 Done. {len(all_leads)} total leads collected.")
