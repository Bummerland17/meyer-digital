#!/usr/bin/env python3
"""
SmartBook AI Outreach Batch 3
Targets: Denver, Salt Lake City, Boise, Austin, Nashville
Types: dental, gym, spa, chiro, vet
"""

import json, time, re, smtplib, ssl, requests, random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# ── Config ──────────────────────────────────────────────────────────────────
GOOGLE_API_KEY = "AIzaSyAuBYyoyqOvNalVNrnff1giboFsG_tXGfI"
SMTP_HOST = "smtp.zoho.com"
SMTP_PORT = 465
SMTP_USER = "hello@pantrymate.net"
SMTP_PASS = "ZyYXtNB4sG8c"
FROM_NAME = "Wolfgang Meyer"
FROM_EMAIL = "hello@pantrymate.net"
MAX_EMAILS = 80
DELAY_MIN = 4.0
DELAY_MAX = 5.5
OUTPUT_FILE = "/root/.openclaw/workspace/assets/outreach-batch3.json"

SKIP_EMAIL_PATTERNS = ["noreply", "info@eos", "mediainquiries", "no-reply", "donotreply"]

CITIES = [
    {"name": "Denver",       "state": "CO", "lat": 39.7392, "lng": -104.9903, "types": ["dental","gym","spa","chiro","vet"]},
    {"name": "Salt Lake City","state": "UT", "lat": 40.7608, "lng": -111.8910, "types": ["dental","gym","spa","chiro","vet"]},
    {"name": "Boise",        "state": "ID", "lat": 43.6150, "lng": -116.2023, "types": ["dental","gym","spa","chiro","vet"]},
    {"name": "Austin",       "state": "TX", "lat": 30.2672, "lng": -97.7431,  "types": ["dental","gym","spa","chiro","vet"]},
    {"name": "Nashville",    "state": "TN", "lat": 36.1627, "lng": -86.7816,  "types": ["dental","gym","spa"]},
]

TYPE_KEYWORDS = {
    "dental":  ["dentist", "dental"],
    "gym":     ["gym", "fitness", "crossfit", "yoga", "pilates"],
    "spa":     ["spa", "massage", "salon", "beauty", "aesthetics"],
    "chiro":   ["chiropractor", "chiropractic"],
    "vet":     ["veterinarian", "veterinary", "animal hospital", "pet clinic"],
}

PLACES_TYPE_MAP = {
    "dental": "dentist",
    "gym":    "gym",
    "spa":    "spa",
    "chiro":  "physiotherapist",
    "vet":    "veterinary_care",
}

SUBJECT_LINES = [
    "After-hours calls are costing you bookings — quick question",
    "Your phone is losing you $2,000/week — here's how to fix it",
    "AI answering service for {biz_type} — 48hr setup, $497/mo",
]

BODY_DENTAL = """Hi {name} team,

Quick question — how many appointment requests do you miss when the office is closed?

Most dental practices lose 4-6 bookings per week to after-hours calls. I set up AI phone agents that answer 24/7, book appointments automatically, and send SMS confirmations.

48-hour setup. $497/month flat. No contracts.

Happy to send a 2-minute demo — just reply here.

— Wolfgang Meyer
hello@pantrymate.net"""

BODY_GYM = """Hi {name} team,

How many membership inquiries go to voicemail after hours?

I set up AI phone agents for gyms and fitness studios that answer every call 24/7, capture leads, and book trials automatically.

48-hour setup. $497/month. No contracts.

Reply for a quick demo.

— Wolfgang Meyer
hello@pantrymate.net"""

BODY_GENERAL = """Hi {name} team,

Missed calls = missed bookings. I set up AI phone agents that answer 24/7, book appointments automatically, and send SMS confirmations to clients.

48-hour setup. $497/month flat. No contracts.

Practices typically recover 4-8 missed bookings per week. Reply for a 2-minute demo.

— Wolfgang Meyer
hello@pantrymate.net"""

# ── Load existing leads to skip ──────────────────────────────────────────────
def load_existing():
    existing_names = set()
    existing_domains = set()
    for fname in ["gym-spa-leads.json", "new-leads-batch2.json", "dental-leads.json"]:
        try:
            with open(f"/root/.openclaw/workspace/assets/{fname}") as f:
                data = json.load(f)
            for r in data:
                if r.get("name"):
                    existing_names.add(r["name"].lower().strip())
                if r.get("website"):
                    try:
                        domain = urlparse(r["website"].lower()).netloc.lstrip("www.")
                        if domain:
                            existing_domains.add(domain)
                    except:
                        pass
        except Exception as e:
            print(f"  Warning loading {fname}: {e}")
    print(f"Existing: {len(existing_names)} names, {len(existing_domains)} domains to skip")
    return existing_names, existing_domains

# ── Google Places ────────────────────────────────────────────────────────────
def search_places(lat, lng, biz_type, radius=8000):
    places = []
    gtype = PLACES_TYPE_MAP.get(biz_type, "establishment")
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": gtype,
        "key": GOOGLE_API_KEY,
        "minrating": 4.0,
    }
    page_token = None
    for _ in range(3):  # up to 3 pages = 60 results
        if page_token:
            params = {"pagetoken": page_token, "key": GOOGLE_API_KEY}
            time.sleep(2)
        try:
            r = requests.get(url, params=params, timeout=10)
            data = r.json()
            if data.get("status") not in ("OK", "ZERO_RESULTS"):
                print(f"    Places API error: {data.get('status')} - {data.get('error_message','')}")
                break
            for place in data.get("results", []):
                rating = place.get("rating", 0)
                reviews = place.get("user_ratings_total", 0)
                if rating >= 4.0 and reviews >= 25:
                    places.append({
                        "place_id": place["place_id"],
                        "name": place.get("name", ""),
                        "rating": rating,
                        "reviews": reviews,
                        "vicinity": place.get("vicinity", ""),
                    })
            page_token = data.get("next_page_token")
            if not page_token:
                break
        except Exception as e:
            print(f"    Places search error: {e}")
            break
    return places

def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,website,formatted_phone_number,rating,user_ratings_total",
        "key": GOOGLE_API_KEY,
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if data.get("status") == "OK":
            return data.get("result", {})
    except Exception as e:
        print(f"    Details error: {e}")
    return {}

# ── Email scraping ───────────────────────────────────────────────────────────
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

BAD_EMAIL_DOMAINS = {
    "example.com","sentry.io","wix.com","wixpress.com","sentry-next.wixpress.com",
    "wordpress.com","squarespace.com","cloudflare.com","google.com","facebook.com",
    "instagram.com","twitter.com","schema.org","w3.org","adobe.com","jquery.com",
    "bootstrapcdn.com","omniasystems.net","gargle.com","yoast.com","mailchimp.com",
    "constantcontact.com","hubspot.com","salesforce.com","sendgrid.net","amazonaws.com",
    "domain.com","company.com","email.com","yourcompany.com","yourdomain.com",
    "test.com","placeholder.com","acme.com",
}

BAD_EMAIL_PATTERNS = [
    r"^user@", r"^test@", r"^john@company", r"^jane@", r"^name@",
    r"@sentry", r"@wixpress", r"sentry\.",
    # Image/asset extensions in domain part
    r"\.(png|jpg|gif|svg|css|js|avif|webp|ico)$",
    # Hashed/UUID looking local parts (tracking pixels)
    r"^[a-f0-9]{20,}@",
]

def is_valid_email(email):
    email = email.lower().strip()
    for pat in SKIP_EMAIL_PATTERNS:
        if pat in email:
            return False
    # Must have exactly one @
    parts = email.split("@")
    if len(parts) != 2:
        return False
    local, domain = parts
    # Local part must be reasonable
    if len(local) < 3 or len(local) > 64:
        return False
    # Domain must look real
    if "." not in domain or len(domain) < 4:
        return False
    if domain in BAD_EMAIL_DOMAINS:
        return False
    # Check domain TLD validity (no image extensions)
    tld = domain.rsplit(".", 1)[-1]
    if tld in ("png","jpg","gif","svg","css","js","avif","webp","ico","mp4","php"):
        return False
    # Check bad patterns
    for pat in BAD_EMAIL_PATTERNS:
        if re.search(pat, email):
            return False
    # Skip emails that look like tracking/hashed (long hex local part)
    if re.match(r"^[a-f0-9]{16,}@", local):
        return False
    return True

def score_email(email):
    """Prefer named emails over generic ones. Higher = better."""
    email = email.lower()
    name_part = email.split("@")[0]
    domain = email.split("@")[1]
    
    score = 10
    # Penalize generic local parts
    generic = ["info","contact","hello","admin","support","office","reception",
               "front","booking","appointments","mail","team","general","inquiries"]
    if name_part in generic:
        score = 5
    # Reward named emails (contain letters and maybe numbers, looks like a person)
    if re.match(r"^[a-z]+[a-z0-9.]*$", name_part) and len(name_part) > 4 and "." in name_part:
        score = 12  # looks like firstname.lastname
    # Penalize edu/org domains (universities etc.)
    if domain.endswith(".edu") or domain.endswith(".gov"):
        score = 1
    # Penalize gmail (personal, not biz)
    if "gmail.com" in domain or "yahoo.com" in domain or "hotmail.com" in domain:
        score = 3
    return score

def scrape_emails_from_url(url, timeout=8):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)"}
    try:
        r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        if r.status_code != 200:
            return []
        text = r.text
        emails = EMAIL_RE.findall(text)
        valid = [e.lower() for e in emails if is_valid_email(e)]
        return list(set(valid))
    except:
        return []

def find_email_for_website(base_url):
    if not base_url:
        return None
    base = base_url.rstrip("/")
    all_emails = []
    for path in ["", "/contact", "/about", "/contact-us", "/about-us"]:
        url = base + path
        emails = scrape_emails_from_url(url)
        all_emails.extend(emails)
        if emails:
            break  # found some, stop
    if not all_emails:
        return None
    # Deduplicate and score
    unique = list(set(all_emails))
    unique.sort(key=lambda e: -score_email(e))
    return unique[0]

# ── Email sending ────────────────────────────────────────────────────────────
def build_email(to_email, biz_name, biz_type, subject_idx):
    subject_template = SUBJECT_LINES[subject_idx % 3]
    
    # Map biz_type to human-readable label for subject
    type_labels = {
        "dental": "dental practice",
        "gym": "gym / fitness studio",
        "spa": "spa / salon",
        "chiro": "chiro practice",
        "vet": "vet practice",
    }
    biz_type_label = type_labels.get(biz_type, "local business")
    subject = subject_template.replace("{biz_type}", biz_type_label)
    
    if biz_type == "dental":
        body = BODY_DENTAL.format(name=biz_name)
    elif biz_type == "gym":
        body = BODY_GYM.format(name=biz_name)
    else:
        body = BODY_GENERAL.format(name=biz_name)
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = to_email
    msg.attach(MIMEText(body, "plain"))
    return msg

def send_email(smtp_conn, to_email, biz_name, biz_type, subject_idx):
    msg = build_email(to_email, biz_name, biz_type, subject_idx)
    smtp_conn.sendmail(FROM_EMAIL, [to_email], msg.as_string())

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    existing_names, existing_domains = load_existing()
    
    # Gather all candidates
    all_candidates = []  # {name, city, state, biz_type, rating, reviews, website, email}
    
    for city in CITIES:
        for biz_type in city["types"]:
            print(f"\n🔍 Searching {city['name']} — {biz_type}...")
            places = search_places(city["lat"], city["lng"], biz_type)
            print(f"   Found {len(places)} qualifying places")
            
            for place in places:
                name = place["name"]
                
                # Skip if already in existing lists
                if name.lower().strip() in existing_names:
                    print(f"   ⏭  Skip (existing): {name}")
                    continue
                
                # Get details (website)
                details = get_place_details(place["place_id"])
                website = details.get("website", "")
                if not website:
                    print(f"   ⏭  Skip (no website): {name}")
                    continue
                
                # Check domain not already emailed
                try:
                    domain = urlparse(website.lower()).netloc.lstrip("www.")
                except:
                    domain = ""
                if domain and domain in existing_domains:
                    print(f"   ⏭  Skip (existing domain): {name}")
                    continue
                
                # Scrape email
                print(f"   📧 Scraping email: {name} ({website})")
                email = find_email_for_website(website)
                if not email:
                    print(f"   ⏭  Skip (no email found): {name}")
                    continue
                
                print(f"   ✅ Found email: {email}")
                all_candidates.append({
                    "name": name,
                    "city": city["name"],
                    "state": city["state"],
                    "biz_type": biz_type,
                    "rating": place["rating"],
                    "reviews": place["reviews"],
                    "website": website,
                    "email": email,
                    "phone": details.get("formatted_phone_number", ""),
                })
                
                # Avoid hammering the scraper
                time.sleep(0.5)
    
    print(f"\n\n{'='*60}")
    print(f"Total candidates found: {len(all_candidates)}")
    print(f"Max to send: {MAX_EMAILS}")
    
    # Filter out low-quality emails (personal email providers)
    PERSONAL_DOMAINS = {"gmail.com","yahoo.com","hotmail.com","outlook.com","aol.com","icloud.com","live.com"}
    quality = []
    for c in all_candidates:
        email_domain = c["email"].split("@")[-1].lower()
        if email_domain in PERSONAL_DOMAINS:
            print(f"   ⏭  Skip personal email ({c['email']}): {c['name']}")
            continue
        quality.append(c)
    print(f"After quality filter: {len(quality)} candidates")
    all_candidates = quality

    # Deduplicate by email
    seen_emails = set()
    deduped = []
    for c in all_candidates:
        if c["email"] not in seen_emails:
            seen_emails.add(c["email"])
            deduped.append(c)
    print(f"After dedup: {len(deduped)} unique emails")
    
    to_send = deduped[:MAX_EMAILS]
    print(f"Will send: {len(to_send)} emails")
    
    # Send emails
    sent = []
    errors = []
    subject_idx = 0
    
    print(f"\n📨 Connecting to SMTP...")
    context = ssl.create_default_context()
    
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as smtp:
            smtp.login(SMTP_USER, SMTP_PASS)
            print("✅ SMTP connected\n")
            
            for i, biz in enumerate(to_send):
                try:
                    print(f"[{i+1}/{len(to_send)}] Sending to {biz['email']} ({biz['name']}, {biz['city']}, {biz['biz_type']})...")
                    send_email(smtp, biz["email"], biz["name"], biz["biz_type"], subject_idx)
                    
                    sent.append({
                        **biz,
                        "subject_idx": subject_idx,
                        "subject": SUBJECT_LINES[subject_idx % 3],
                        "sent_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "status": "sent",
                    })
                    subject_idx += 1
                    
                    delay = random.uniform(DELAY_MIN, DELAY_MAX)
                    print(f"   ✅ Sent. Waiting {delay:.1f}s...")
                    time.sleep(delay)
                    
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    errors.append({"biz": biz, "error": str(e)})
                    time.sleep(2)
    
    except Exception as e:
        print(f"❌ SMTP connection failed: {e}")
        errors.append({"error": f"SMTP connection: {e}"})
    
    # Save results
    with open(OUTPUT_FILE, "w") as f:
        json.dump(sent, f, indent=2)
    print(f"\n💾 Saved {len(sent)} sent leads to {OUTPUT_FILE}")
    
    # Report
    print(f"\n{'='*60}")
    print(f"📊 CAMPAIGN REPORT")
    print(f"{'='*60}")
    print(f"Total found/qualified:  {len(all_candidates)}")
    print(f"After dedup:            {len(deduped)}")
    print(f"Attempted:              {len(to_send)}")
    print(f"Successfully sent:      {len(sent)}")
    print(f"Errors:                 {len(errors)}")
    
    # By city
    print(f"\nBy City:")
    for city in CITIES:
        count = sum(1 for s in sent if s["city"] == city["name"])
        print(f"  {city['name']}: {count}")
    
    # By type
    print(f"\nBy Business Type:")
    for t in ["dental","gym","spa","chiro","vet"]:
        count = sum(1 for s in sent if s["biz_type"] == t)
        print(f"  {t}: {count}")
    
    if errors:
        print(f"\nErrors:")
        for e in errors:
            print(f"  {e}")

if __name__ == "__main__":
    main()
