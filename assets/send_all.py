#!/usr/bin/env python3
import smtplib
import json
import time
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone

SMTP_HOST = 'smtp.zoho.com'
SMTP_PORT = 465
SMTP_USER = 'hello@pantrymate.net'
SMTP_PASS = 'ZyYXtNB4sG8c'
FROM_NAME = 'Wolfgang Meyer'

results = {
    "sent": [],
    "failed": [],
    "skipped": []
}

def send_email(to, subject, body, is_html=False):
    msg = MIMEMultipart()
    msg['From'] = f'{FROM_NAME} <{SMTP_USER}>'
    msg['To'] = to
    msg['Subject'] = subject
    mime_type = 'html' if is_html else 'plain'
    msg.attach(MIMEText(body, mime_type))
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
    return True

# ── Load queue ──────────────────────────────────────────────────────────────
queue_path = '/root/.openclaw/workspace/assets/email-queue.json'
with open(queue_path) as f:
    queue = json.load(f)

pending = [e for e in queue if e['status'] == 'pending']
print(f"Found {len(pending)} pending emails")

# ── Task 1: Send queue ───────────────────────────────────────────────────────
for i, email in enumerate(pending):
    to = email['to']
    subject = email['subject']
    body = email['body']

    # Skip obvious placeholder addresses
    if to.lower() == 'email@address.com':
        print(f"[{i+1}/{len(pending)}] SKIPPED (placeholder): {to}")
        email['status'] = 'skipped'
        email['skipped_at'] = datetime.now(timezone.utc).isoformat()
        results['skipped'].append({'id': email['id'], 'to': to, 'reason': 'placeholder address'})
        continue

    try:
        send_email(to, subject, body)
        ts = datetime.now(timezone.utc).isoformat()
        email['status'] = 'sent'
        email['sent_at'] = ts
        results['sent'].append({'id': email['id'], 'to': to, 'subject': subject, 'sent_at': ts})
        print(f"[{i+1}/{len(pending)}] SENT: {to} — {subject[:50]}")
    except Exception as e:
        email['status'] = 'failed'
        email['error'] = str(e)
        results['failed'].append({'id': email['id'], 'to': to, 'error': str(e)})
        print(f"[{i+1}/{len(pending)}] FAILED: {to} — {e}")

    delay = random.uniform(3, 5)
    print(f"  ↳ sleeping {delay:.1f}s...")
    time.sleep(delay)

# Save updated queue
with open(queue_path, 'w') as f:
    json.dump(queue, f, indent=2)

print("\n── Queue processing complete ──")

# ── Task 2: Josh Hirschmann / Local Restaurant & Bar ────────────────────────
josh_subject = "Following up — Google reviews for Local Restaurant & Bar"
josh_body = """Josh,

You're running two of the better spots in Jackson — Local and Trio — and both are sitting at 4.3 stars. That's solid, but it's not a moat. It's a target.

Hayden's Post is at 3.9 and they're actively working their reviews right now. When a 3.9-star place starts gaining momentum, the gap closes faster than most operators expect.

I help restaurants run a real review strategy — not just asking guests to "leave us a review," but building a system that generates consistent 5-star feedback, catches unhappy guests before they hit Google, and handles responses in a way that actually builds trust with new diners.

$400/month per restaurant. For both Local and Trio together, $800/month. Most clients see measurable rating movement within 60 days.

Got 15 minutes this week for a quick call? I'll show you exactly what I'd do for your two spots.

— Wolfgang Meyer
hello@pantrymate.net"""

try:
    send_email('info@localjh.com', josh_subject, josh_body)
    ts = datetime.now(timezone.utc).isoformat()
    results['sent'].append({'id': 'task2_josh_hirschmann', 'to': 'info@localjh.com', 'subject': josh_subject, 'sent_at': ts})
    print(f"SENT (Task 2): info@localjh.com")
except Exception as e:
    results['failed'].append({'id': 'task2_josh_hirschmann', 'to': 'info@localjh.com', 'error': str(e)})
    print(f"FAILED (Task 2): info@localjh.com — {e}")

time.sleep(random.uniform(3, 5))

# ── Task 3: Jackson SouthTown Hotel ─────────────────────────────────────────
hotel_subject = "Your Google rating is costing you bookings"
hotel_body = """Hi Jackson SouthTown team,

Quick math: research consistently shows that every star below 4.0 costs a hotel roughly 10% of potential bookings. You're at 3.4 stars. That's not a small leak — it's a significant chunk of revenue walking to the properties down the street.

At 1,783 reviews, this isn't bad luck or a rough season. That volume means the pattern is baked in. The good news: it's completely fixable with the right system in place.

I work with hotels on active reputation management — monitoring every review, crafting responses that protect and rebuild trust, and building a process that consistently generates more 5-star feedback from happy guests (who usually stay quiet unless someone asks).

$400/month. Results are visible within 30 days.

Worth a quick call this week? I can walk you through exactly what I'd do for SouthTown and what a realistic rating trajectory looks like.

— Wolfgang Meyer
hello@pantrymate.net"""

try:
    send_email('info@jacksonsouthtown.com', hotel_subject, hotel_body)
    ts = datetime.now(timezone.utc).isoformat()
    results['sent'].append({'id': 'task3_jackson_southtown', 'to': 'info@jacksonsouthtown.com', 'subject': hotel_subject, 'sent_at': ts})
    print(f"SENT (Task 3): info@jacksonsouthtown.com")
except Exception as e:
    results['failed'].append({'id': 'task3_jackson_southtown', 'to': 'info@jacksonsouthtown.com', 'error': str(e)})
    print(f"FAILED (Task 3): info@jacksonsouthtown.com — {e}")

time.sleep(random.uniform(3, 5))

# ── Task 4: PantryMate Activation Email ─────────────────────────────────────
pm_subject = "You're subscriber #1 — thank you"
pm_body = """Hey,

Just wanted to reach out personally — you're the first person to subscribe to PantryMate, and that actually means a lot. Seriously.

One question: what's your biggest frustration with meal planning right now? I'm building this thing in real-time and your answer will directly shape what I work on next.

Also — if you have any friends who can never figure out what's for dinner (you know the type), send them to pantrymate.net. If they sign up, I'll give you a free month as a thank you.

Thanks for being here from the start.

— Wolfgang
hello@pantrymate.net"""

try:
    send_email('olcowboy21@gmail.com', pm_subject, pm_body)
    ts = datetime.now(timezone.utc).isoformat()
    results['sent'].append({'id': 'task4_pantrymate_activation', 'to': 'olcowboy21@gmail.com', 'subject': pm_subject, 'sent_at': ts})
    print(f"SENT (Task 4): olcowboy21@gmail.com")
except Exception as e:
    results['failed'].append({'id': 'task4_pantrymate_activation', 'to': 'olcowboy21@gmail.com', 'error': str(e)})
    print(f"FAILED (Task 4): olcowboy21@gmail.com — {e}")

# ── Final summary ────────────────────────────────────────────────────────────
print(f"\n{'='*50}")
print(f"FINAL RESULTS")
print(f"{'='*50}")
print(f"  Sent:    {len(results['sent'])}")
print(f"  Failed:  {len(results['failed'])}")
print(f"  Skipped: {len(results['skipped'])}")
if results['failed']:
    print("\nFailed:")
    for f in results['failed']:
        print(f"  - {f['to']}: {f['error']}")
if results['skipped']:
    print("\nSkipped:")
    for s in results['skipped']:
        print(f"  - {s['to']}: {s['reason']}")

# Save results log
log_path = '/root/.openclaw/workspace/assets/send-results.json'
with open(log_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to: {log_path}")
