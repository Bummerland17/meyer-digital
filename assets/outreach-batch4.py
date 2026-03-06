#!/usr/bin/env python3
"""
SmartBook AI Outreach - Batch 4
Cities: Nashville TN, Charlotte NC, Austin TX, Tampa FL
Types: dental, chiropractors, physical therapy, med spas, urgent care, optometry, dermatology
"""

import json
import re
import time
import smtplib
import ssl
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
GMAPS_API_KEY = "AIzaSyAuBYyoyqOvNalVNrnff1giboFsG_tXGfI"
SMTP_HOST = "smtp.zoho.com"
SMTP_PORT = 465
SMTP_USER = "hello@pantrymate.net"
SMTP_PASS = "ZyYXtNB4sG8c"
FROM_NAME = "Wolfgang Meyer"
FROM_ADDR = "hello@pantrymate.net"
MAX_EMAILS = 60
EMAIL_DELAY = 5  # seconds between sends

ASSETS = Path("/root/.openclaw/workspace/assets")

CITIES = [
    {"name": "Nashville", "state": "TN", "lat": 36.1627, "lng": -86.7816},
    {"name": "Charlotte", "state": "NC", "lat": 35.2271, "lng": -80.8431},
    {"name": "Austin",    "state": "TX", "lat": 30.2672, "lng": -97.7431},
    {"name": "Tampa",     "state": "FL", "lat": 27.9506, "lng": -82.4572},
]

BIZ_TYPES = [
    {"query": "dental office",           "label": "dental",           "type_label": "dental"},
    {"query": "chiropractor",            "label": "chiropractor",     "type_label": "chiropractic"},
    {"query": "physical therapy clinic", "label": "physical therapy", "type_label": "physical therapy"},
    {"query": "med spa",                 "label": "med spa",          "type_label": "med spa"},
    {"query": "urgent care clinic",      "label": "urgent care",      "type_label": "urgent care"},
    {"query": "optometry office",        "label": "optometry",        "type_label": "optometry"},
    {"query": "dermatology clinic",      "label": "dermatology",      "type_label": "dermatology"},
]

SUBJECTS = [
    "Missed calls are costing you patients — quick question",
    "Your after-hours calls could be booking automatically",
    "3-minute read: how {city} practices are recovering 6 missed bookings/week",
]

EMAIL_BODY = """Hi {biz_name},

Quick question — what happens when a patient calls your office after hours?

Most {type_label} practices lose 4-8 appointments per week to voicemail. We set up AI phone agents that answer every call 24/7, book appointments automatically, and send SMS confirmations.

48-hour setup. $497/month. No contracts.

Reply for a 2-minute demo — or visit bummerland17.github.io/smartbook-ai to learn more.

— Wolfgang Meyer
hello@pantrymate.net"""

# Placeholder / obviously-fake email patterns to ALWAYS skip
PLACEHOLDER_EMAILS = {
    "user@domain.com", "email@address.com", "contact@mysite.com",
    "first.last@company.com", "your@email.com", "name@example.com",
    "info@example.com", "test@test.com", "admin@example.com",
    "example@example.com", "youremail@example.com",
}

# ── Load previously contacted businesses ────────────────────────────────────
def load_contacted():
    contacted_names = set()
    contacted_websites = set()
    contacted_emails = set()

    files = [
        "dental-leads.json",
        "gym-spa-leads.json",
        "new-leads-batch2.json",
        "outreach-batch3.json",
    ]
    for fname in files:
        fpath = ASSETS / fname
        if not fpath.exists():
            continue
        try:
            data = json.loads(fpath.read_text())
            items = data if isinstance(data, list) else data.get("leads", data.get("results", []))
            for item in items:
                if item.get("name"):
                    contacted_names.add(item["name"].lower().strip())
                if item.get("website"):
                    contacted_websites.add(item["website"].lower().strip().rstrip("/"))
                if item.get("email"):
                    contacted_emails.add(item["email"].lower().strip())
        except Exception as e:
            print(f"  Warning loading {fname}: {e}")
    print(f"Skip list: {len(contacted_names)} names | {len(contacted_websites)} websites | {len(contacted_emails)} emails")
    return contacted_names, contacted_websites, contacted_emails

# ── Google Places Text Search ────────────────────────────────────────────────
def search_places(city, biz_type):
    results = []
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{biz_type['query']} in {city['name']} {city['state']}",
        "key": GMAPS_API_KEY,
    }
    seen_ids = set()
    page_token = None

    for page in range(2):  # 2 pages = up to 40 results
        if page_token:
            params = {"pagetoken": page_token, "key": GMAPS_API_KEY}
            time.sleep(2)
        try:
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            status = data.get("status")
            if status == "ZERO_RESULTS":
                break
            if status not in ("OK",):
                print(f"    API status: {status} - {data.get('error_message','')}")
                break
            for place in data.get("results", []):
                pid = place.get("place_id")
                if pid in seen_ids:
                    continue
                seen_ids.add(pid)
                rating = place.get("rating", 0)
                n_reviews = place.get("user_ratings_total", 0)
                if rating < 4.0 or n_reviews < 20:
                    continue
                results.append({
                    "place_id": pid,
                    "name": place.get("name", ""),
                    "rating": rating,
                    "reviews": n_reviews,
                    "address": place.get("formatted_address", ""),
                })
            page_token = data.get("next_page_token")
            if not page_token:
                break
        except Exception as e:
            print(f"    Search error: {e}")
            break

    return results

# ── Google Places Details ─────────────────────────────────────────────────────
def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "website,formatted_phone_number",
        "key": GMAPS_API_KEY,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        result = resp.json().get("result", {})
        return {
            "website": result.get("website", ""),
            "phone": result.get("formatted_phone_number", ""),
        }
    except Exception as e:
        print(f"    Details error: {e}")
        return {}

# ── Email scraping ──────────────────────────────────────────────────────────
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

# Patterns in email addresses that are always junk
SKIP_EMAIL_RE = re.compile(
    r"(noreply|no-reply|donotreply|unsubscribe|bounce|mailer-daemon|"
    r"postmaster|abuse|spam|"
    r"@sentry\.|@wixpress\.|@wix\.|@wordpress\.|@squarespace\.|@sharetribe\.|"
    r"@cloudflare\.|@google\.|@adobe\.|@typekit\.|@fontawesome\.|"
    r"\.png@|\.jpg@|\.gif@|\.svg@|\.js@|\.css@|"
    r"example\.com|placeholder|yourname|youremail|name@|"
    r"@mailchimp\.|@constantcontact\.|@hubspot\.|@salesforce\."
    r")",
    re.IGNORECASE,
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def is_valid_email(e):
    e = e.lower().strip()
    if e in PLACEHOLDER_EMAILS:
        return False
    if SKIP_EMAIL_RE.search(e):
        return False
    # Must have at least 2-char local part
    local, domain = e.rsplit("@", 1) if "@" in e else (e, "")
    if len(local) < 2 or len(domain) < 4 or "." not in domain:
        return False
    return True

def scrape_email(website):
    if not website:
        return None

    base = website.rstrip("/")
    urls_to_try = [base, base + "/contact", base + "/contact-us", base + "/about"]

    found = []
    for url in urls_to_try:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=8, allow_redirects=True)
            if resp.status_code != 200:
                continue
            emails = EMAIL_RE.findall(resp.text)
            for e in emails:
                e = e.lower().strip().rstrip(".")
                if not is_valid_email(e):
                    continue
                if e not in found:
                    found.append(e)
            if found:
                break
        except Exception:
            pass

    if not found:
        return None

    # Prefer practice-specific domains over generic ones
    for e in found:
        dom = e.split("@")[1]
        if not re.search(r"@(gmail|yahoo|hotmail|outlook|icloud|aol)\.", e):
            return e
    return found[0]

# ── SMTP send ─────────────────────────────────────────────────────────────────
_smtp_blocked = False  # track if SMTP is globally blocked

def send_email(to_addr, subject, body):
    global _smtp_blocked
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{FROM_NAME} <{FROM_ADDR}>"
    msg["To"] = to_addr
    msg.attach(MIMEText(body, "plain"))

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx, timeout=15) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(FROM_ADDR, to_addr, msg.as_string())

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    global _smtp_blocked
    contacted_names, contacted_websites, contacted_emails = load_contacted()

    # ── Phase 1: Collect all leads ──────────────────────────────────────────
    print("\n═══════════════════════════════════════════════")
    print("  PHASE 1: LEAD COLLECTION")
    print("═══════════════════════════════════════════════")

    all_leads = []  # raw lead records

    stats = {
        "by_city": {},
        "by_type": {},
        "leads_found": 0,
        "emails_sent": 0,
        "skipped_already_contacted": 0,
        "skipped_no_website": 0,
        "skipped_no_email": 0,
        "errors": 0,
    }

    for city in CITIES:
        stats["by_city"][city["name"]] = {"leads": 0, "sent": 0}
        for biz in BIZ_TYPES:
            print(f"\n🔍 {biz['label']} in {city['name']} {city['state']}")
            places = search_places(city, biz)
            print(f"   → {len(places)} qualifying (≥4.0 rating, ≥20 reviews)")

            for place in places:
                name = place["name"]

                # Skip if already contacted by name
                if name.lower().strip() in contacted_names:
                    stats["skipped_already_contacted"] += 1
                    continue

                # Get website
                details = get_place_details(place["place_id"])
                website = details.get("website", "")
                phone = details.get("phone", "")

                if not website:
                    stats["skipped_no_website"] += 1
                    continue

                # Skip already-contacted website
                norm_site = website.lower().strip().rstrip("/")
                if norm_site in contacted_websites:
                    stats["skipped_already_contacted"] += 1
                    continue

                # Scrape email
                email = scrape_email(website)
                if not email:
                    stats["skipped_no_email"] += 1
                    continue

                if email in contacted_emails:
                    stats["skipped_already_contacted"] += 1
                    continue

                # Good lead
                print(f"   ✉  {name} → {email}")
                stats["leads_found"] += 1
                stats["by_city"][city["name"]]["leads"] += 1
                if biz["label"] not in stats["by_type"]:
                    stats["by_type"][biz["label"]] = {"leads": 0, "sent": 0}
                stats["by_type"][biz["label"]]["leads"] += 1

                all_leads.append({
                    "name": name,
                    "city": city["name"],
                    "state": city["state"],
                    "biz_type": biz["label"],
                    "rating": place["rating"],
                    "reviews": place["reviews"],
                    "website": website,
                    "email": email,
                    "phone": phone,
                    "status": "pending",
                })

                # Track to avoid sending duplicates
                contacted_emails.add(email)
                contacted_websites.add(norm_site)
                contacted_names.add(name.lower().strip())

    print(f"\n✅ Lead collection complete: {len(all_leads)} actionable leads")

    # ── Phase 2: Send emails ────────────────────────────────────────────────
    print("\n═══════════════════════════════════════════════")
    print("  PHASE 2: SENDING EMAILS")
    print("═══════════════════════════════════════════════")

    results = []
    emails_sent = 0
    subject_idx = 0
    smtp_error_streak = 0

    for lead in all_leads:
        if emails_sent >= MAX_EMAILS:
            print(f"\n🛑 Reached max {MAX_EMAILS} emails.")
            lead["status"] = "queued_over_limit"
            results.append(lead)
            continue

        if _smtp_blocked:
            lead["status"] = "queued_smtp_blocked"
            results.append(lead)
            continue

        # Build subject
        subj_template = SUBJECTS[subject_idx % len(SUBJECTS)]
        subject = subj_template.format(city=lead["city"])
        body = EMAIL_BODY.format(biz_name=lead["name"], type_label=lead["biz_type"])

        sent_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        print(f"   📧 [{emails_sent+1}/{MAX_EMAILS}] {lead['name']} → {lead['email']}")

        try:
            send_email(lead["email"], subject, body)
            lead["subject"] = subject
            lead["subject_idx"] = subject_idx % len(SUBJECTS)
            lead["sent_at"] = sent_at
            lead["status"] = "sent"
            emails_sent += 1
            subject_idx += 1
            stats["emails_sent"] += 1
            stats["by_city"][lead["city"]]["sent"] += 1
            stats["by_type"][lead["biz_type"]]["sent"] += 1
            smtp_error_streak = 0
            print(f"      ✅ Sent!")
            if emails_sent < MAX_EMAILS:
                time.sleep(EMAIL_DELAY)
        except smtplib.SMTPException as e:
            err_str = str(e)
            lead["subject"] = subject
            lead["sent_at"] = sent_at
            lead["status"] = f"error: {err_str[:100]}"
            stats["errors"] += 1
            smtp_error_streak += 1
            print(f"      ❌ {err_str[:80]}")
            # After 3 consecutive SMTP errors, mark as blocked and stop trying
            if smtp_error_streak >= 3 and "5.4.6" in err_str:
                print("\n🚫 SMTP account blocked (Zoho 550 5.4.6). Queuing remaining leads.")
                _smtp_blocked = True
        except Exception as e:
            lead["subject"] = subject
            lead["sent_at"] = sent_at
            lead["status"] = f"error: {str(e)[:100]}"
            stats["errors"] += 1
            print(f"      ❌ {e}")

        results.append(lead)

    # ── Save results ────────────────────────────────────────────────────────
    output = {
        "batch": 4,
        "run_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "smtp_status": "blocked" if _smtp_blocked else "ok",
        "stats": stats,
        "leads": results,
    }
    out_path = ASSETS / "outreach-batch4.json"
    out_path.write_text(json.dumps(output, indent=2))
    print(f"\n💾 Saved {len(results)} records → {out_path}")

    # ── Summary ─────────────────────────────────────────────────────────────
    print("\n" + "═"*55)
    print("BATCH 4 SUMMARY")
    print("═"*55)
    print(f"Leads found (scraped email):  {stats['leads_found']}")
    print(f"Emails sent:                  {stats['emails_sent']}")
    print(f"Skipped (prior contact):      {stats['skipped_already_contacted']}")
    print(f"Skipped (no website):         {stats['skipped_no_website']}")
    print(f"Skipped (no email scraped):   {stats['skipped_no_email']}")
    print(f"Send errors:                  {stats['errors']}")
    print(f"SMTP status:                  {'BLOCKED' if _smtp_blocked else 'OK'}")
    print()
    print("By city:")
    for city_name, s in stats["by_city"].items():
        print(f"  {city_name:12s}  leads={s['leads']}  sent={s['sent']}")
    print()
    print("By type:")
    for btype, s in stats.get("by_type", {}).items():
        print(f"  {btype:20s}  leads={s['leads']}  sent={s['sent']}")

if __name__ == "__main__":
    main()
