#!/usr/bin/env python3
"""
Clean leads and send personalized cold emails via Zoho SMTP.
"""

import json
import smtplib
import time
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# SMTP config
SMTP_HOST = "smtp.zoho.com"
SMTP_PORT = 465
SMTP_USER = "hello@pantrymate.net"
SMTP_PASS = "ZyYXtNB4sG8c"
FROM_NAME = "Wolfgang Meyer"
FROM_EMAIL = "hello@pantrymate.net"
SUBJECT = "After-hours calls are costing you bookings — quick question"

# Load leads
with open('/root/.openclaw/workspace/assets/new-leads-batch2.json') as f:
    raw_leads = json.load(f)

# Clean: remove bad emails, deduplicate by email
BAD_EMAIL_PATTERNS = ['user@domain.com', '.webp', '.png', '.jpg']
seen_emails = set()
clean_leads = []

for lead in raw_leads:
    email = lead.get('email', '').strip().lower()
    
    # Skip bad emails
    if any(pat in email for pat in BAD_EMAIL_PATTERNS):
        print(f"  SKIP (bad email): {lead['name']} | {email}")
        continue
    
    # Skip duplicates
    if email in seen_emails:
        print(f"  SKIP (duplicate): {lead['name']} | {email}")
        continue
    
    seen_emails.add(email)
    clean_leads.append(lead)

print(f"\nClean leads: {len(clean_leads)}")

# Email templates by business type
def get_email_body(lead):
    name = lead['name']
    btype = lead['type']
    
    if btype == 'dental':
        body = f"""Hi {name} team,

Quick question — when a patient calls after 5pm to book an appointment, what happens? If it's going to voicemail, you're losing bookings every night.

Our AI phone answering service handles calls 24/7, books appointments automatically, and never misses a patient inquiry — even at 2am.

Most dental offices see 10–20% more bookings in the first month.

Happy to send a 2-minute demo — just reply here."""

    elif btype in ('spa', 'salon'):
        body = f"""Hi {name} team,

How many appointment slots go unfilled because clients called after hours and got voicemail?

Our AI phone service answers calls 24/7, books appointments instantly, and keeps your calendar full — without adding staff.

Clients expect to book when it's convenient for them, not just during business hours.

Happy to send a 2-minute demo — just reply here."""

    elif btype == 'gym':
        body = f"""Hi {name} team,

When a potential member calls about membership after hours, are you capturing that inquiry — or losing it to a competitor who picks up?

Our AI phone answering service handles membership inquiries and tour bookings 24/7, so you never miss a lead.

Takes minutes to set up, zero extra staff needed.

Happy to send a 2-minute demo — just reply here."""

    elif btype == 'chiropractor':
        body = f"""Hi {name} team,

Patients often decide to book a chiropractic appointment when the pain is bad — including evenings and weekends. If your phones go to voicemail, they'll book with whoever answers.

Our AI answers calls 24/7 and books appointments automatically, so you capture patients when they're ready.

Happy to send a 2-minute demo — just reply here."""

    elif btype == 'vet':
        body = f"""Hi {name} team,

Pet owners don't wait for business hours when their animal needs help. If after-hours calls go to voicemail, you're missing both emergencies and routine booking opportunities.

Our AI phone service handles calls 24/7 — triage urgent needs, book routine appointments, and capture every inquiry.

Happy to send a 2-minute demo — just reply here."""

    else:
        body = f"""Hi {name} team,

When clients call after hours and hit voicemail, you lose bookings. It's that simple.

Our AI phone answering service handles calls 24/7, books appointments automatically, and ensures you never miss a client inquiry — day or night.

Happy to send a 2-minute demo — just reply here."""

    return body

# Send emails
print(f"\nConnecting to Zoho SMTP...")
context = ssl.create_default_context()

sent = []
failed = []

with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
    server.login(SMTP_USER, SMTP_PASS)
    print("✅ Connected and logged in\n")
    
    for i, lead in enumerate(clean_leads, 1):
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = SUBJECT
            msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
            msg['To'] = lead['email']
            msg['Reply-To'] = FROM_EMAIL
            
            body = get_email_body(lead)
            msg.attach(MIMEText(body, 'plain'))
            
            server.sendmail(FROM_EMAIL, lead['email'], msg.as_string())
            
            sent.append(lead)
            print(f"[{i:2d}/{len(clean_leads)}] ✉️  SENT → {lead['name']} ({lead['city']}) | {lead['email']}")
            
        except Exception as e:
            failed.append({'lead': lead, 'error': str(e)})
            print(f"[{i:2d}/{len(clean_leads)}] ❌  FAILED → {lead['name']} | {e}")
        
        # Rate limit: 1 per 3 seconds
        if i < len(clean_leads):
            time.sleep(3)

print(f"\n{'='*60}")
print(f"✅ Sent: {len(sent)}")
print(f"❌ Failed: {len(failed)}")
print(f"\nSent to:")
for lead in sent:
    print(f"  - {lead['name']} ({lead['city']}, {lead.get('state','')}) | {lead['type']} | {lead['email']}")

if failed:
    print(f"\nFailed:")
    for item in failed:
        print(f"  - {item['lead']['name']} | {item['error']}")

# Update leads file with only clean leads
with open('/root/.openclaw/workspace/assets/new-leads-batch2.json', 'w') as f:
    json.dump(clean_leads, f, indent=2)
print(f"\nUpdated leads file with {len(clean_leads)} clean leads.")
