#!/usr/bin/env python3
"""
find-motivated-sellers.py
Scrapes Craigslist Phoenix for motivated seller listings, scores them,
saves top 20 to assets/motivated-sellers-live.json, and queues Vapi calls
for listings with phone numbers and score >= 6.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import os
from datetime import datetime, timezone, timedelta

VAPI_API_KEY = "0aaae7fe-be63-472a-a46d-5d9224e0fa89"
VAPI_PHONE_NUMBER_ID = "3f6ef946-452f-4b16-85cf-9e2d5b041df5"

SELLER_FIRST_MESSAGE = "Hey, I saw your property listing online. This is Rex calling for Wolfgang Meyer Investments — we're cash buyers in Phoenix. Is the property still available?"
SELLER_SYSTEM = """You are Rex for Wolfgang Meyer Investments. You are calling someone who posted a property for sale. If asked if you are an AI, disclose honestly. Goal: find out if they are motivated, get the address, understand their situation, and set up a time for Wolfgang to call back. Key questions: Is property still available? What's the address? Why are you selling? How quickly do you need to close? Would you consider a cash offer below asking if we can close in 7-10 days? If interested: 'Great — I'll have Wolfgang call you back personally within 24 hours to discuss numbers. What's the best time?' Do NOT make any offers or commitments. Just qualify and set callback."""

SEARCH_URLS = [
    "https://phoenix.craigslist.org/search/rea?query=for+sale+by+owner&sort=date",
    "https://phoenix.craigslist.org/search/rea?query=motivated+seller&sort=date",
    "https://phoenix.craigslist.org/search/rea?query=cash+only&sort=date",
    "https://phoenix.craigslist.org/search/rea?query=as+is&sort=date",
    "https://phoenix.craigslist.org/search/rea?query=fixer+upper&sort=date",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def extract_phone(text):
    pattern = r'(\(?\d{3}\)?[\s\-\.]\d{3}[\s\-\.]\d{4})'
    matches = re.findall(pattern, text)
    return matches[0] if matches else None

def extract_email(text):
    pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
    matches = re.findall(pattern, text)
    return matches[0] if matches else None

def parse_price(price_str):
    try:
        return int(re.sub(r'[^\d]', '', price_str))
    except:
        return None

def score_listing(title, body, price, post_date):
    text = (title + " " + (body or "")).lower()
    score = 0

    if "motivated" in text or "must sell" in text:
        score += 3
    if "cash only" in text or "as-is" in text or "as is" in text:
        score += 3
    if "fixer" in text or "needs work" in text:
        score += 2
    if price and price < 200000:
        score += 2
    if post_date:
        try:
            now = datetime.now(timezone.utc)
            diff = now - post_date
            if diff < timedelta(hours=24):
                score += 1
        except:
            pass
    if "retail" in text or "move in ready" in text or "move-in ready" in text:
        score -= 2

    return max(0, score)

def fetch_listing_detail(url):
    """Fetch listing page to get phone/email/body"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # Get body text
        body_el = soup.select_one("#postingbody")
        body = body_el.get_text(" ", strip=True) if body_el else ""

        phone = extract_phone(body)
        email = extract_email(body)
        return body, phone, email
    except Exception as e:
        return "", None, None

def search_craigslist():
    seen_urls = set()
    listings = []

    for url in SEARCH_URLS:
        print(f"Searching: {url}")
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")

            # Try JSON-LD or listing items
            items = soup.select("li.cl-search-result, li.result-row")
            if not items:
                # Try newer CL layout
                items = soup.select("[data-pid]")

            for item in items:
                try:
                    # Title
                    title_el = item.select_one("a.cl-app-anchor, a.result-title, .title")
                    if not title_el:
                        title_el = item.select_one("a[href*='/rea/']")
                    if not title_el:
                        continue

                    title = title_el.get_text(strip=True)
                    link = title_el.get("href", "")
                    if not link.startswith("http"):
                        link = "https://phoenix.craigslist.org" + link

                    if link in seen_urls:
                        continue
                    seen_urls.add(link)

                    # Price
                    price_el = item.select_one(".priceinfo, .result-price, .price")
                    price_str = price_el.get_text(strip=True) if price_el else ""
                    price = parse_price(price_str)

                    # Location
                    loc_el = item.select_one(".supertitle, .result-hood, .location, .meta")
                    location = loc_el.get_text(strip=True) if loc_el else "Phoenix, AZ"

                    # Post date
                    date_el = item.select_one("time")
                    post_date = None
                    post_date_str = ""
                    if date_el:
                        post_date_str = date_el.get("datetime", "")
                        try:
                            post_date = datetime.fromisoformat(post_date_str.replace("Z", "+00:00"))
                        except:
                            pass

                    listings.append({
                        "title": title,
                        "price": price,
                        "price_str": price_str,
                        "location": location,
                        "post_date": post_date_str,
                        "url": link,
                        "source_query": url.split("query=")[1].split("&")[0].replace("+", " "),
                        "_post_date_obj": post_date,
                    })

                except Exception as e:
                    continue

        except Exception as e:
            print(f"  Error fetching {url}: {e}")
        
        time.sleep(2)  # polite crawling

    return listings

def fire_seller_call(phone, listing):
    """Fire a Vapi call to a motivated seller"""
    # Normalize phone to E.164
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        e164 = f"+1{digits}"
    elif len(digits) == 11 and digits.startswith('1'):
        e164 = f"+{digits}"
    else:
        print(f"  Skipping invalid phone: {phone}")
        return None

    payload = {
        "phoneNumberId": VAPI_PHONE_NUMBER_ID,
        "customer": {"number": e164},
        "assistant": {
            "name": "Rex",
            "voice": {"provider": "11labs", "voiceId": "CwhRBWXzGAHq8TQ4Fs17"},
            "firstMessage": SELLER_FIRST_MESSAGE,
            "model": {
                "provider": "openai",
                "model": "gpt-4o",
                "messages": [{"role": "system", "content": SELLER_SYSTEM}]
            },
            "endCallFunctionEnabled": True,
            "silenceTimeoutSeconds": 20,
            "maxDurationSeconds": 180
        }
    }

    try:
        resp = requests.post(
            "https://api.vapi.ai/call",
            headers={
                "Authorization": f"Bearer {VAPI_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30
        )
        if resp.ok:
            call_id = resp.json().get("id")
            print(f"  ✅ Seller call fired → {e164} | call_id={call_id}")
            return call_id
        else:
            print(f"  ❌ Seller call failed {resp.status_code}: {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"  ❌ Exception firing seller call: {e}")
        return None

def main():
    print("=" * 60)
    print("MOTIVATED SELLER FINDER - Phoenix Craigslist")
    print("=" * 60)

    # Step 1: Scrape
    raw_listings = search_craigslist()
    print(f"\nFound {len(raw_listings)} raw listings. Fetching details...")

    # Step 2: Fetch details + score
    scored = []
    for i, listing in enumerate(raw_listings[:50]):  # limit to 50 for speed
        print(f"  [{i+1}/{min(len(raw_listings),50)}] {listing['title'][:60]}...")
        body, phone, email = fetch_listing_detail(listing["url"])
        score = score_listing(listing["title"], body, listing["price"], listing.get("_post_date_obj"))
        
        listing.pop("_post_date_obj", None)
        listing.update({
            "phone": phone,
            "email": email,
            "score": score,
            "body_preview": body[:300] if body else ""
        })
        scored.append(listing)
        time.sleep(1)

    # Step 3: Sort + top 20
    scored.sort(key=lambda x: x["score"], reverse=True)
    top20 = scored[:20]

    print(f"\nTop 20 listings:")
    for l in top20:
        print(f"  Score {l['score']:2d} | {l['title'][:50]} | ${l['price'] or 'N/A'} | Phone: {l['phone'] or 'none'}")

    # Save to file
    out_path = "/root/.openclaw/workspace/assets/motivated-sellers-live.json"
    with open(out_path, "w") as f:
        json.dump(top20, f, indent=2)
    print(f"\nSaved to {out_path}")

    # Step 4: Fire calls for score >= 6 with phone
    qualified = [l for l in top20 if l.get("phone") and l.get("score", 0) >= 6]
    print(f"\n{len(qualified)} listings qualify for calls (score >= 6 + phone)")
    
    seller_calls = []
    for listing in qualified:
        call_id = fire_seller_call(listing["phone"], listing)
        if call_id:
            seller_calls.append({
                "call_id": call_id,
                "title": listing["title"],
                "phone": listing["phone"],
                "score": listing["score"],
                "url": listing["url"],
                "fired_at": datetime.now(timezone.utc).isoformat()
            })
        time.sleep(30)

    # Save seller call log
    seller_log_path = "/root/.openclaw/workspace/assets/seller-calls-log.json"
    with open(seller_log_path, "w") as f:
        json.dump(seller_calls, f, indent=2)
    print(f"\nSeller calls log saved to {seller_log_path}")

    # Output summary for pipeline
    summary = {
        "total_found": len(raw_listings),
        "scored": len(scored),
        "top20": top20,
        "seller_calls_fired": len(seller_calls),
        "seller_calls": seller_calls
    }
    print(f"\nSUMMARY: {len(raw_listings)} found, {len(top20)} top listings, {len(seller_calls)} calls fired")
    return summary

if __name__ == "__main__":
    main()
