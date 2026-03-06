#!/usr/bin/env python3
"""
Smart Email Scheduler — only sends during business hours in target timezone.
Run from heartbeat. Reads queue from email-queue.json, sends when timing is right.
"""

import json, smtplib, ssl, time, os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_USER = 'hello@pantrymate.net'
SMTP_PASS = 'ZyYXtNB4sG8c'
QUEUE_FILE = os.path.join(os.path.dirname(__file__), 'assets/email-queue.json')

# UTC offset for each timezone (standard time, pre-DST)
# DST starts 2nd Sunday March = March 8, 2026
TZ_OFFSETS = {
    'MT': -7,   # Mountain (Phoenix always -7, SLC/Denver/Boise -7 until Mar 8)
    'PT': -8,   # Pacific
    'CT': -6,   # Central
    'ET': -5,   # Eastern
}

BUSINESS_HOURS_START = 8   # 8am local
BUSINESS_HOURS_END = 17    # 5pm local
BUSINESS_DAYS = [0,1,2,3,4]  # Mon-Fri

def is_good_time_to_send(timezone='MT'):
    offset = TZ_OFFSETS.get(timezone, -7)
    utc_now = datetime.utcnow()
    local_hour = (utc_now.hour + offset) % 24
    local_day = utc_now.weekday()  # simple approximation
    
    if local_day not in BUSINESS_DAYS:
        return False, f"Weekend in {timezone}"
    if local_hour < BUSINESS_HOURS_START or local_hour >= BUSINESS_HOURS_END:
        return False, f"Outside business hours ({local_hour}:00 {timezone})"
    return True, f"Good time ({local_hour}:00 {timezone})"

def send_email(to, subject, body, from_name='Wolfgang Meyer'):
    msg = MIMEMultipart('alternative')
    msg['From'] = f'{from_name} <{SMTP_USER}>'
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.zoho.com', 465, context=ctx) as s:
        s.login(SMTP_USER, SMTP_PASS)
        s.sendmail(SMTP_USER, to, msg.as_string())

def run():
    if not os.path.exists(QUEUE_FILE):
        print("No email queue found.")
        return
    
    with open(QUEUE_FILE) as f:
        queue = json.load(f)
    
    pending = [e for e in queue if e.get('status') == 'pending']
    print(f"Email queue: {len(pending)} pending, {len(queue)-len(pending)} done")
    
    sent_count = 0
    for email in queue:
        if email.get('status') != 'pending':
            continue
        
        tz = email.get('timezone', 'MT')
        ok, reason = is_good_time_to_send(tz)
        
        if not ok:
            print(f"⏰ Holding: {email['to']} — {reason}")
            continue
        
        try:
            send_email(email['to'], email['subject'], email['body'])
            email['status'] = 'sent'
            email['sent_at'] = datetime.utcnow().isoformat()
            print(f"✅ Sent → {email['to']} ({reason})")
            sent_count += 1
            time.sleep(10)  # 10s gap — stays within Zoho daily limits
            if sent_count >= 150:  # Hard daily cap — Zoho limit safety
                print("Daily cap of 150 reached. Stopping.")
                break
        except Exception as e:
            email['status'] = 'failed'
            email['error'] = str(e)
            print(f"❌ Failed → {email['to']}: {e}")
    
    with open(QUEUE_FILE, 'w') as f:
        json.dump(queue, f, indent=2)
    
    print(f"\nDone: {sent_count} sent this run")
    return sent_count

if __name__ == '__main__':
    run()
