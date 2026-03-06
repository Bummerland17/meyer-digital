#!/usr/bin/env python3
import smtplib
import ssl
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_HOST = "smtp.zoho.com"
SMTP_PORT = 465
SMTP_USER = "hello@pantrymate.net"
SMTP_PASS = "ZyYXtNB4sG8c"
FROM_NAME = "Wolfgang Meyer"
FROM_EMAIL = "hello@pantrymate.net"
DELAY = 10

DENTAL_SUBJECT = "Your phones are losing you bookings after hours"
DENTAL_BODY = """{greeting}

Quick question: when someone calls after 6pm to book an appointment, what happens?

Most dental offices send it to voicemail. The patient hangs up and books somewhere else.

SmartBook AI answers that call instantly — speaks naturally, answers questions about your services, and books them directly into your calendar. Available 24/7, costs less than a part-time receptionist.

Worth a 10-minute look? Reply and I'll send you a quick demo.

Wolfgang Meyer
SmartBook AI
hello@pantrymate.net"""

GYM_SUBJECT = "How many membership enquiries go unanswered after hours?"
GYM_BODY = """{greeting}

Most gyms lose 30-40% of new membership enquiries because they come in after hours or during a busy class.

SmartBook AI answers every call — talks naturally about your classes, pricing, and availability, and books the trial session on the spot. No voicemail. No missed leads.

Costs less than one lost membership per month. Want to see how it works?

Wolfgang Meyer
SmartBook AI
hello@pantrymate.net"""

OTHER_SUBJECT = "Never miss a customer call again"
OTHER_BODY = """{greeting}

Every missed call is a lost customer — especially after hours or when you're busy.

SmartBook AI handles your inbound calls 24/7. It answers naturally, answers questions about your business, and either books appointments or collects contact details for you to follow up.

No hardware. No complex setup. Running in 48 hours.

Want to see a quick demo?

Wolfgang Meyer
SmartBook AI
hello@pantrymate.net"""

emails_to_send = [
    {
        "to": "reception@cherrymedispa.com",
        "business": "Cherry MediSpa",
        "template": "gym",
    },
    {
        "to": "carson@wasatchcrossfit.com",
        "business": "Wasatch CrossFit",
        "template": "gym",
    },
]

def get_email_content(template, business_name):
    greeting = f"Hi {business_name} team,"
    if template == "dental":
        subject = DENTAL_SUBJECT
        body = DENTAL_BODY.format(greeting=greeting)
    elif template == "gym":
        subject = GYM_SUBJECT
        body = GYM_BODY.format(greeting=greeting)
    else:
        subject = OTHER_SUBJECT
        body = OTHER_BODY.format(greeting=greeting)
    return subject, body

def send_email(to_email, business, template):
    subject, body = get_email_content(template, business)
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = to_email
    
    msg.attach(MIMEText(body, "plain"))
    
    context = ssl.create_default_context()
    
    try:
        print(f"\nSending to: {to_email} ({business})")
        print(f"Subject: {subject}")
        
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        
        print(f"✓ SENT successfully to {to_email}")
        return True
    except Exception as e:
        print(f"✗ FAILED to send to {to_email}: {e}")
        return False

results = []
for i, entry in enumerate(emails_to_send):
    if i > 0:
        print(f"\nWaiting {DELAY} seconds...")
        time.sleep(DELAY)
    
    success = send_email(entry["to"], entry["business"], entry["template"])
    results.append({**entry, "success": success})

print("\n=== SUMMARY ===")
for r in results:
    status = "✓ SENT" if r["success"] else "✗ FAILED"
    print(f"{status}: {r['business']} → {r['to']}")
