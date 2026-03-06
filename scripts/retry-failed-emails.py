#!/usr/bin/env python3
"""Retry failed outreach emails — runs once after Zoho cooldown"""
import smtplib, json, time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

SMTP_HOST = 'smtp.zoho.com'
SMTP_PORT = 465
SMTP_USER = 'hello@pantrymate.net'
SMTP_PASS = 'ZyYXtNB4sG8c'
BOT_TOKEN = json.load(open('/root/.openclaw/openclaw.json'))['channels']['telegram']['botToken']

def send_email(to, subject, body):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as s:
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)
    return True

# Priority emails first
priority_emails = [
    {
        "to": "info@localjh.com",
        "subject": "Your competitors are working their reviews — Local Restaurant & Bar",
        "body": """<p>Josh,</p>
<p>Noticed Local Restaurant & Bar sitting at 4.3 stars — solid, but Hayden's Post and a few others in Jackson are actively working their review strategy right now. The gap closes faster than most owners expect.</p>
<p>I help restaurants in tourist markets like Jackson do one specific thing: turn the review volume they're already getting into a consistent rating climb. No fake reviews, no gimmicks — just a system that works with what's already happening.</p>
<p>$400/month, results visible in 30 days. If you manage Trio as well, I can cover both for $700/month.</p>
<p>Worth a 15-minute call this week? Reply here or text me.</p>
<p>Wolfgang<br>hello@pantrymate.net</p>"""
    },
    {
        "to": "info@jacksonsouthtown.com", 
        "subject": "3.4 stars is costing you bookings — here's the number",
        "body": """<p>Hi,</p>
<p>Hotels below 4.0 stars lose roughly 10-15% of potential bookings to competitors — travelers filter by rating before they ever read a review. At 1,783 reviews, Jackson SouthTown's rating isn't a fluke. It's a pattern that needs a system to fix it.</p>
<p>I work with hospitality businesses specifically on this: building a review response and recovery strategy that moves the needle within 60 days.</p>
<p>$400/month. No contracts. If the rating doesn't improve in the first 30 days, you don't pay for month two.</p>
<p>Quick call this week?</p>
<p>Wolfgang<br>hello@pantrymate.net</p>"""
    },
    {
        "to": "olcowboy21@gmail.com",
        "subject": "You're subscriber #1 — quick question",
        "body": """<p>Hey,</p>
<p>You're the first person who ever paid for PantryMate — that means something to me.</p>
<p>Quick question: what's your biggest frustration with meal planning right now? Not looking for a review, just genuinely want to know what would make this more useful for you.</p>
<p>Also — if you know anyone else who stares at their fridge every night wondering what to cook, send them to pantrymate.net. If they sign up, I'll add a free month to your account.</p>
<p>Wolfgang</p>"""
    }
]

sent = 0
failed = []
for email in priority_emails:
    try:
        send_email(email['to'], email['subject'], email['body'])
        print(f"✅ Sent: {email['to']}")
        sent += 1
        time.sleep(8)
    except Exception as e:
        print(f"❌ Failed {email['to']}: {e}")
        failed.append(email['to'])

import requests
msg = f"📧 Priority email retry complete\n✅ {sent}/3 sent\n{'❌ Still failed: ' + ', '.join(failed) if failed else '✅ All delivered'}"
requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    json={"chat_id": "8654703697", "text": msg})
print(msg)
