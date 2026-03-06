#!/usr/bin/env python3
"""
Find 30 small businesses via Google Places API, scrape emails, save leads.
"""

import requests
import json
import time
import re
import sys
from urllib.parse import urljoin, urlparse

API_KEY = "AIzaSyAuBYyoyqOvNalVNrnff1giboFsG_tXGfI"

CITIES = [
    {"name": "Phoenix", "state": "AZ", "query_location": "33.4484,-112.0740", "radius": 15000},
    {"name": "Denver", "state": "CO", "query_location": "39.7392,-104.9903", "radius": 15000},
    {"name": "Salt Lake City", "state": "UT", "query_location": "40.7608,-111.8910", "radius": 15000},
    {"name": "Boise", "state": "ID", "query_location": "43.6150,-116.2023", "radius": 15000},
    {"name": "Austin", "state": "TX", "query_location": "30.2672,-97.7431", "radius": 15000},
]

BUSINESS_TYPES = [
    {"keyword": "gym fitness center", "type_label": "gym"},
    {"keyword": "spa massage", "type_label": "spa"},
    {"keyword": "dental office dentist", "type_label": "dental"},
    {"keyword": "chiropractor", "type_label": "chiropractor"},
    {"keyword": "hair salon", "type_label": "salon"},
    {"keyword": "veterinary clinic vet", "type_label": "vet"},
]

def search_places(keyword, location, radius):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": keyword,
        "location": location,
        "radius": radius,
        "key": API_KEY,
    }
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    return data.get("results", [])

def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,rating,user_ratings_total,website,formatted_phone_number,formatted_address",
        "key": API_KEY,
    }
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    return data.get("result", {})

def extract_emails_from_text(text):
    pattern = r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b'
    emails = re.findall(pattern, text)
    # Filter out common placeholder/noreply emails
    bad_patterns = ['noreply', 'no-reply', 'example', 'placeholder', 'test@', 'info@example', 
                    'donotreply', 'do-not-reply', '@sentry', '@github', '@w3.org',
                    '.png', '.jpg', '.gif', '.svg', 'wix.com', 'squarespace.com',
                    'wordpress.com', 'godaddy.com', 'schema.org', 'googleapis.com']
    valid = []
    seen = set()
    for e in emails:
        el = e.lower()
        if any(bp in el for bp in bad_patterns):
            continue
        if el in seen:
            continue
        seen.add(el)
        valid.append(e)
    return valid

def scrape_emails_from_url(url, timeout=8):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        if resp.status_code == 200:
            return extract_emails_from_text(resp.text)
    except Exception as e:
        pass
    return []

def find_email_for_website(website):
    if not website:
        return None
    
    # Normalize URL
    if not website.startswith('http'):
        website = 'https://' + website
    
    base = website.rstrip('/')
    pages_to_try = [
        base,
        base + '/contact',
        base + '/contact-us',
        base + '/about',
        base + '/about-us',
        base + '/reach-us',
        base + '/get-in-touch',
    ]
    
    for page in pages_to_try:
        emails = scrape_emails_from_url(page)
        if emails:
            # Prefer non-generic emails if possible
            non_info = [e for e in emails if not e.lower().startswith('info@') and not e.lower().startswith('contact@')]
            if non_info:
                return non_info[0]
            return emails[0]
        time.sleep(0.3)
    
    return None

def main():
    leads = []
    seen_places = set()
    
    print(f"Searching for businesses across {len(CITIES)} cities and {len(BUSINESS_TYPES)} types...")
    
    for city in CITIES:
        for btype in BUSINESS_TYPES:
            if len(leads) >= 60:  # Search more to get 30 with emails
                break
            
            query = f"{btype['keyword']} in {city['name']} {city['state']}"
            print(f"\nSearching: {query}")
            
            try:
                results = search_places(query, city['query_location'], city['radius'])
                print(f"  Found {len(results)} raw results")
            except Exception as e:
                print(f"  Error searching: {e}")
                continue
            
            for place in results:
                if len(leads) >= 60:
                    break
                
                place_id = place.get('place_id')
                if place_id in seen_places:
                    continue
                seen_places.add(place_id)
                
                # Basic filter from search results
                rating = place.get('rating', 0)
                reviews = place.get('user_ratings_total', 0)
                
                if rating < 4.0 or reviews < 20:
                    continue
                
                # Get full details
                try:
                    details = get_place_details(place_id)
                    time.sleep(0.2)
                except Exception as e:
                    continue
                
                website = details.get('website', '')
                if not website:
                    continue
                
                name = details.get('name', place.get('name', ''))
                phone = details.get('formatted_phone_number', '')
                rating = details.get('rating', rating)
                reviews = details.get('user_ratings_total', reviews)
                
                print(f"  Checking: {name} | rating={rating} | reviews={reviews} | {website}")
                
                # Scrape email
                email = find_email_for_website(website)
                
                if not email:
                    print(f"    No email found")
                    continue
                
                print(f"    Email found: {email}")
                
                leads.append({
                    "name": name,
                    "email": email,
                    "website": website,
                    "phone": phone,
                    "rating": rating,
                    "reviews": reviews,
                    "city": city['name'],
                    "state": city['state'],
                    "type": btype['type_label'],
                    "place_id": place_id,
                })
                
                if len(leads) >= 30:
                    print(f"\n✅ Reached 30 leads with emails!")
                    break
            
            time.sleep(0.5)
        
        if len(leads) >= 30:
            break
    
    print(f"\n\nTotal leads with emails: {len(leads)}")
    
    # Save to file
    output_path = '/root/.openclaw/workspace/assets/new-leads-batch2.json'
    with open(output_path, 'w') as f:
        json.dump(leads, f, indent=2)
    
    print(f"Saved to {output_path}")
    
    for i, lead in enumerate(leads, 1):
        print(f"{i:2d}. {lead['name']} ({lead['city']}, {lead['state']}) | {lead['type']} | {lead['email']}")
    
    return leads

if __name__ == '__main__':
    main()
