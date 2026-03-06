#!/usr/bin/env python3
"""
LeadDrop Delivery System
Sends lead CSV files to new subscribers via email.
Usage:
  python3 leaddrop-delivery.py --subscription-id sub_xxx
  python3 leaddrop-delivery.py --check-new   (check for new subs in last 24h)
  python3 leaddrop-delivery.py --customer-email user@example.com --product "Caribbean Tourism Leads"
"""

import stripe
import smtplib
import os
import sys
import json
import argparse
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────────
STRIPE_KEY = "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"
SMTP_HOST  = "smtp.zoho.com"
SMTP_PORT  = 465
SMTP_USER  = "hello@pantrymate.net"
SMTP_PASS  = "ZyYXtNB4sG8c"
FROM_NAME  = "LeadDrop"
FROM_EMAIL = "hello@pantrymate.net"

LEADS_DIR  = Path("/root/.openclaw/workspace/real-estate")
LOG_FILE   = Path("/root/.openclaw/workspace/leaddrop-delivery-log.json")

# Map product names → lead files
PRODUCT_FILE_MAP = {
    "Caribbean Tourism Leads":   "caribbean-leads-2026-03-05.json",
    "Philippines Tourism Leads": "philippines-leads-2026-03-05.json",
    "US Dental & MedSpa Leads":  "australia-dental-leads-2026-03-05.json",  # closest match
    "US Dental":                 "australia-dental-leads-2026-03-05.json",
    "UK Aesthetics Clinic Leads":"uk-aesthetics-leads-2026-03-05.json",
    "UK Aesthetics Leads":       "uk-aesthetics-leads-2026-03-05.json",
    "Phoenix RE Wholesale Leads":"phoenix-leads-2026-03-05.json",
    "All Markets Bundle":        None,  # send all files
}

# Lead counts per product
LEAD_COUNTS = {
    "Caribbean Tourism Leads":    967,
    "Philippines Tourism Leads":  619,
    "US Dental & MedSpa Leads":   110,
    "UK Aesthetics Clinic Leads": 200,  # being built
    "Phoenix RE Wholesale Leads": 736,
    "All Markets Bundle":         2632, # total
}

stripe.api_key = STRIPE_KEY


def load_log():
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            return json.load(f)
    return {"delivered": []}


def save_log(log):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def json_to_csv(json_path: Path) -> str:
    """Convert JSON lead file to CSV string."""
    import csv
    import io
    with open(json_path) as f:
        data = json.load(f)

    # Handle both list and dict with a leads key
    if isinstance(data, dict):
        leads = data.get("leads", data.get("results", data.get("businesses", [])))
    else:
        leads = data

    if not leads:
        return "No leads found"

    output = io.StringIO()
    if isinstance(leads[0], dict):
        fieldnames = list(leads[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leads)
    else:
        output.write(str(leads))

    return output.getvalue()


def get_all_lead_files():
    """Return all lead CSV files for the All Markets Bundle."""
    files = []
    for product, fname in PRODUCT_FILE_MAP.items():
        if fname and product != "All Markets Bundle":
            path = LEADS_DIR / fname
            if path.exists():
                files.append((product, path))
    return files


def send_leads_email(customer_email: str, customer_name: str, product_name: str):
    """Send lead CSV to customer via Zoho SMTP."""
    print(f"  Preparing email to {customer_email} for '{product_name}'...")

    lead_count = LEAD_COUNTS.get(product_name, "hundreds of")

    msg = MIMEMultipart()
    msg["From"]    = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"]      = customer_email
    msg["Subject"] = f"Your {product_name} leads are ready — LeadDrop"

    body = f"""Hi{' ' + customer_name if customer_name else ''},

Welcome to LeadDrop! 🎯

Your subscription to {product_name} is now active.

Attached are your {lead_count} leads for {product_name}.

What's included:
- Business name & type
- Location (city, country)
- Phone number
- Rating & review count
- Digital gap signals (website/social presence)
- Contact info where available

New leads are added and refreshed monthly. You'll receive an update email each time.

—–

Have questions? Just reply to this email — we respond within 24 hours.

To cancel your subscription, log in at https://billing.stripe.com or reply to this email.

Best,
The LeadDrop Team
hello@pantrymate.net
https://bummerland17.github.io/leaddrop/
"""

    msg.attach(MIMEText(body, "plain"))

    # Attach CSV file(s)
    if product_name == "All Markets Bundle":
        all_files = get_all_lead_files()
        for name, path in all_files:
            csv_data = json_to_csv(path)
            part = MIMEBase("application", "octet-stream")
            part.set_payload(csv_data.encode())
            encoders.encode_base64(part)
            fname = name.lower().replace(" ", "-") + "-leads.csv"
            part.add_header("Content-Disposition", f'attachment; filename="{fname}"')
            msg.attach(part)
    else:
        fname = PRODUCT_FILE_MAP.get(product_name)
        if fname:
            lead_path = LEADS_DIR / fname
            if lead_path.exists():
                csv_data = json_to_csv(lead_path)
                part = MIMEBase("application", "octet-stream")
                part.set_payload(csv_data.encode())
                encoders.encode_base64(part)
                csv_fname = product_name.lower().replace(" ", "-").replace("&", "and") + "-leads.csv"
                part.add_header("Content-Disposition", f'attachment; filename="{csv_fname}"')
                msg.attach(part)
            else:
                print(f"  ⚠️  Lead file not found: {lead_path}")
        else:
            print(f"  ⚠️  No file mapping for product: {product_name}")

    # Send via Zoho SSL
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(FROM_EMAIL, customer_email, msg.as_string())
        print(f"  ✅ Email sent to {customer_email}")
        return True
    except Exception as e:
        print(f"  ❌ SMTP error: {e}")
        return False


def deliver_subscription(sub_id: str, log: dict):
    """Deliver leads for a given Stripe subscription ID."""
    if sub_id in log["delivered"]:
        print(f"  ⏭️  Already delivered for {sub_id}, skipping.")
        return

    print(f"\nProcessing subscription: {sub_id}")
    try:
        sub = stripe.Subscription.retrieve(sub_id, expand=["customer", "items.data.price.product"])
    except Exception as e:
        print(f"  ❌ Stripe error: {e}")
        return

    customer = sub.customer
    email = customer.email if hasattr(customer, "email") else None
    name  = customer.name  if hasattr(customer, "name")  else ""

    if not email:
        print(f"  ❌ No customer email found for {sub_id}")
        return

    for item in sub["items"]["data"]:
        product_name = item["price"]["product"]["name"]
        print(f"  Product: {product_name}")
        success = send_leads_email(email, name or "", product_name)
        if success:
            log["delivered"].append(sub_id)
            save_log(log)


def check_new_subscriptions(hours: int = 24):
    """Check for new subscriptions in the last N hours and deliver."""
    log = load_log()
    cutoff = int(time.time()) - (hours * 3600)
    print(f"Checking for new subscriptions since {datetime.fromtimestamp(cutoff)} ...")

    subscriptions = stripe.Subscription.list(
        created={"gte": cutoff},
        status="active",
        expand=["data.customer", "data.items.data.price.product"],
        limit=100
    )

    if not subscriptions.data:
        print("No new subscriptions found.")
        return

    for sub in subscriptions.data:
        if sub.id not in log["delivered"]:
            deliver_subscription(sub.id, log)
        else:
            print(f"  ⏭️  Already delivered: {sub.id}")


def main():
    parser = argparse.ArgumentParser(description="LeadDrop Delivery System")
    parser.add_argument("--subscription-id",   help="Deliver for specific Stripe subscription ID")
    parser.add_argument("--check-new",         action="store_true", help="Check for new subs in last 24h")
    parser.add_argument("--hours",             type=int, default=24, help="Hours back to check (default: 24)")
    parser.add_argument("--customer-email",    help="Manual delivery: customer email")
    parser.add_argument("--product",           help="Manual delivery: product name")
    args = parser.parse_args()

    log = load_log()

    if args.subscription_id:
        deliver_subscription(args.subscription_id, log)

    elif args.check_new:
        check_new_subscriptions(args.hours)

    elif args.customer_email and args.product:
        print(f"\nManual delivery: {args.product} → {args.customer_email}")
        success = send_leads_email(args.customer_email, "", args.product)
        if success:
            print("✅ Done.")
        else:
            print("❌ Failed.")
            sys.exit(1)

    else:
        parser.print_help()
        print("\nExamples:")
        print("  python3 leaddrop-delivery.py --check-new")
        print("  python3 leaddrop-delivery.py --subscription-id sub_abc123")
        print('  python3 leaddrop-delivery.py --customer-email user@example.com --product "Caribbean Tourism Leads"')


if __name__ == "__main__":
    main()
