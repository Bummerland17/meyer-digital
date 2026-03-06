#!/usr/bin/env python3
"""
Website Factory Builder
=======================
Takes a config JSON, fills a template, creates a GitHub repo,
pushes the site, enables GitHub Pages, and returns the live URL.

Usage:
  python builder.py config.json
  python builder.py '{"business_name": "...", ...}'
"""

import json
import sys
import os
import re
import requests
import base64
import datetime
import time
from pathlib import Path

# ─── Configuration ────────────────────────────────────────────────────────────

TEMPLATES_DIR = Path(__file__).parent / "templates"
CLIENT_SITES_FILE = Path(__file__).parent / "client-sites.json"
GITHUB_ORG = "Bummerland17"

# GitHub token — set via env var or hardcode for local use
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") or "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"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

TEMPLATE_FILES = {
    "service-business":   "service-business.html",
    "saas-app":           "saas-app.html",
    "agency-consultant":  "agency-consultant.html",
    "real-estate-local":  "real-estate-local.html",
    "digital-product":    "digital-product.html",
}

# ─── Helpers ──────────────────────────────────────────────────────────────────

def load_config(source: str) -> dict:
    """Load config from a file path or a raw JSON string."""
    source = source.strip()
    if source.startswith("{"):
        return json.loads(source)
    with open(source) as f:
        return json.load(f)


def load_template(template_name: str) -> str:
    """Load the HTML template by name."""
    filename = TEMPLATE_FILES.get(template_name)
    if not filename:
        raise ValueError(f"Unknown template: '{template_name}'. "
                         f"Choose from: {list(TEMPLATE_FILES.keys())}")
    path = TEMPLATES_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Template file not found: {path}")
    return path.read_text(encoding="utf-8")


def derive_colors(primary_color: str) -> dict:
    """Derive primary-dark by darkening the primary color slightly."""
    # Parse hex → darken by 15% → return hex
    h = primary_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    factor = 0.80
    rd = max(0, int(r * factor))
    gd = max(0, int(g * factor))
    bd = max(0, int(b * factor))
    return {
        "PRIMARY_COLOR_DARK": f"#{rd:02x}{gd:02x}{bd:02x}",
        "ACCENT_COLOR": primary_color,  # default accent = primary
    }


def build_replacements(config: dict) -> dict:
    """
    Build the full replacement dict from a config.
    Every {{PLACEHOLDER}} in a template maps to a key here.
    Missing placeholders are left as-is for manual replacement.
    """
    c = config
    year = datetime.date.today().year

    # Services list → individual vars
    services = c.get("services", ["Service 1", "Service 2", "Service 3"])
    while len(services) < 3:
        services.append(f"Service {len(services)+1}")

    # Address
    address = c.get("address", "")

    # Derive colors
    primary = c.get("primary_color", "#2563eb")
    color_vars = derive_colors(primary)

    replacements = {
        # Identity
        "BUSINESS_NAME":        c.get("business_name", ""),
        "PRODUCT_NAME":         c.get("business_name", ""),
        "AGENCY_NAME":          c.get("business_name", ""),
        "AGENT_NAME":           c.get("business_name", ""),
        "TAGLINE":              c.get("tagline", ""),
        "META_DESCRIPTION":     c.get("tagline", ""),

        # Colors
        "PRIMARY_COLOR":        primary,
        **color_vars,

        # Contact
        "PHONE":                c.get("phone", ""),
        "EMAIL":                c.get("email", ""),
        "ADDRESS":              address,
        "LOCATION":             address,
        "CITY":                 address.split(",")[-1].strip() if "," in address else address,

        # CTA
        "CTA_TEXT":             c.get("cta_text", "Get Started"),
        "STRIPE_LINK":          c.get("stripe_link", "#"),
        "STRIPE_LINK_PLUS":     c.get("stripe_link", "#"),

        # Hero
        "HEADLINE":             c.get("headline", c.get("business_name", "")),
        "HERO_BADGE":           c.get("hero_badge", "Trusted Local Business"),
        "HERO_NOTE":            c.get("hero_note", "No commitment required"),
        "SOCIAL_PROOF":         c.get("social_proof", "Trusted by hundreds of clients"),

        # Services
        "SERVICES_HEADING":     c.get("services_heading", "Our Services"),
        "SERVICES_SUBHEADING":  c.get("services_subheading", "Everything you need, done right."),
        "SERVICE_1_ICON":       c.get("service_1_icon", "⭐"),
        "SERVICE_1_NAME":       services[0] if len(services) > 0 else "",
        "SERVICE_1_DESC":       c.get("service_1_desc", "Professional service delivered with care."),
        "SERVICE_2_ICON":       c.get("service_2_icon", "💡"),
        "SERVICE_2_NAME":       services[1] if len(services) > 1 else "",
        "SERVICE_2_DESC":       c.get("service_2_desc", "Expert solutions tailored to your needs."),
        "SERVICE_3_ICON":       c.get("service_3_icon", "🎯"),
        "SERVICE_3_NAME":       services[2] if len(services) > 2 else "",
        "SERVICE_3_DESC":       c.get("service_3_desc", "Results-driven approach for lasting impact."),

        # About
        "ABOUT_HEADING":        c.get("about_heading", f"About {c.get('business_name','')}"),
        "ABOUT_TEXT_1":         c.get("about_text_1", "We've been serving clients with dedication and expertise."),
        "ABOUT_TEXT_2":         c.get("about_text_2", "Our team brings years of experience to every project."),
        "STAT_1_NUMBER":        c.get("stat_1_number", "500+"),
        "STAT_1_LABEL":         c.get("stat_1_label", "Happy Clients"),
        "STAT_2_NUMBER":        c.get("stat_2_number", "10+"),
        "STAT_2_LABEL":         c.get("stat_2_label", "Years Experience"),
        "STAT_3_NUMBER":        c.get("stat_3_number", "100%"),
        "STAT_3_LABEL":         c.get("stat_3_label", "Satisfaction Rate"),

        # Testimonials
        "TESTIMONIALS_HEADING": c.get("testimonials_heading", "What Our Clients Say"),
        "TESTIMONIAL_1_TEXT":   c.get("testimonial_1_text", "Outstanding service. Highly recommend."),
        "TESTIMONIAL_1_NAME":   c.get("testimonial_1_name", "Happy Client"),
        "TESTIMONIAL_1_LOCATION": c.get("testimonial_1_location", "Local Customer"),
        "TESTIMONIAL_1_INITIAL": c.get("testimonial_1_name", "C")[0].upper(),
        "TESTIMONIAL_2_TEXT":   c.get("testimonial_2_text", "Professional, timely, and excellent results."),
        "TESTIMONIAL_2_NAME":   c.get("testimonial_2_name", "Satisfied Customer"),
        "TESTIMONIAL_2_LOCATION": c.get("testimonial_2_location", "Returning Client"),
        "TESTIMONIAL_2_INITIAL": c.get("testimonial_2_name", "S")[0].upper(),
        "TESTIMONIAL_3_TEXT":   c.get("testimonial_3_text", "Best decision I made. Worth every penny."),
        "TESTIMONIAL_3_NAME":   c.get("testimonial_3_name", "Loyal Client"),
        "TESTIMONIAL_3_LOCATION": c.get("testimonial_3_location", "Long-term Customer"),
        "TESTIMONIAL_3_INITIAL": c.get("testimonial_3_name", "L")[0].upper(),

        # Contact
        "CONTACT_HEADING":      c.get("contact_heading", "Get In Touch"),
        "CONTACT_SUBHEADING":   c.get("contact_subheading", "We'd love to hear from you."),
        "CONTACT_BODY":         c.get("contact_body", "Ready to get started? Send us a message."),

        # Footer
        "YEAR": str(year),

        # SaaS specific
        "FEATURES_HEADING":     c.get("features_heading", "Everything You Need"),
        "FEATURES_SUBHEADING":  c.get("features_subheading", "Built for results."),
        "FEATURE_1_ICON":       c.get("feature_1_icon", "⚡"),
        "FEATURE_1_NAME":       c.get("feature_1_name", services[0] if services else "Feature 1"),
        "FEATURE_1_DESC":       c.get("feature_1_desc", "Powerful capability built into the platform."),
        "FEATURE_2_ICON":       c.get("feature_2_icon", "🔒"),
        "FEATURE_2_NAME":       c.get("feature_2_name", services[1] if len(services)>1 else "Feature 2"),
        "FEATURE_2_DESC":       c.get("feature_2_desc", "Enterprise-grade security and reliability."),
        "FEATURE_3_ICON":       c.get("feature_3_icon", "📊"),
        "FEATURE_3_NAME":       c.get("feature_3_name", services[2] if len(services)>2 else "Feature 3"),
        "FEATURE_3_DESC":       c.get("feature_3_desc", "Analytics and insights at your fingertips."),
        "PRICING_HEADING":      c.get("pricing_heading", "Simple Pricing"),
        "PRICING_SUBHEADING":   c.get("pricing_subheading", "No hidden fees. Cancel anytime."),
        "FREE_FEATURE_1":       c.get("free_feature_1", "Up to 5 projects"),
        "FREE_FEATURE_2":       c.get("free_feature_2", "Basic analytics"),
        "FREE_FEATURE_3":       c.get("free_feature_3", "Email support"),
        "PRO_PRICE":            c.get("pro_price", "29"),
        "PRO_FEATURE_1":        c.get("pro_feature_1", "Unlimited projects"),
        "PRO_FEATURE_2":        c.get("pro_feature_2", "Advanced analytics"),
        "PRO_FEATURE_3":        c.get("pro_feature_3", "Priority support"),
        "PLUS_PRICE":           c.get("plus_price", "79"),
        "PLUS_FEATURE_1":       c.get("plus_feature_1", "Team collaboration"),
        "PLUS_FEATURE_2":       c.get("plus_feature_2", "Custom integrations"),
        "PLUS_FEATURE_3":       c.get("plus_feature_3", "Dedicated account manager"),
        "FAQ_HEADING":          c.get("faq_heading", "Frequently Asked Questions"),
        "FAQ_1_QUESTION":       c.get("faq_1_question", "How do I get started?"),
        "FAQ_1_ANSWER":         c.get("faq_1_answer", "Sign up for a free account and you're ready to go."),
        "FAQ_2_QUESTION":       c.get("faq_2_question", "Can I cancel anytime?"),
        "FAQ_2_ANSWER":         c.get("faq_2_answer", "Yes, cancel anytime with no fees."),
        "FAQ_3_QUESTION":       c.get("faq_3_question", "Do you offer refunds?"),
        "FAQ_3_ANSWER":         c.get("faq_3_answer", "We offer a 30-day money-back guarantee."),
        "FAQ_4_QUESTION":       c.get("faq_4_question", "Is my data secure?"),
        "FAQ_4_ANSWER":         c.get("faq_4_answer", "Yes, we use industry-standard encryption."),
        "CTA_BANNER_HEADLINE":  c.get("cta_banner_headline", f"Ready to get started with {c.get('business_name','')}?"),
        "CTA_BANNER_SUBTEXT":   c.get("cta_banner_subtext", "Join thousands of happy customers today."),
        "HERO_BADGE":           c.get("hero_badge", "New"),

        # Agency specific
        "SPECIALTY_LINE":       c.get("specialty_line", "Strategy · Design · Growth"),
        "FOUNDER_NAME":         c.get("founder_name", c.get("business_name", "")),
        "FOUNDER_TITLE":        c.get("founder_title", "Founder & CEO"),
        "WORK_HEADING":         c.get("work_heading", "Selected Work"),
        "CASE_1_TAG":           c.get("case_1_tag", "Branding"),
        "CASE_1_TITLE":         c.get("case_1_title", "Client Project"),
        "CASE_1_DESC":          c.get("case_1_desc", "How we helped a client reach their goals."),
        "CASE_1_RESULT":        c.get("case_1_result", "40% increase in conversions"),
        "CASE_2_TAG":           c.get("case_2_tag", "Digital Marketing"),
        "CASE_2_TITLE":         c.get("case_2_title", "Growth Project"),
        "CASE_2_DESC":          c.get("case_2_desc", "Strategic campaign that drove measurable results."),
        "CASE_2_RESULT":        c.get("case_2_result", "3x ROI in 6 months"),
        "CASE_3_TAG":           c.get("case_3_tag", "Web Design"),
        "CASE_3_TITLE":         c.get("case_3_title", "Redesign Project"),
        "CASE_3_DESC":          c.get("case_3_desc", "Complete rebrand and website overhaul."),
        "CASE_3_RESULT":        c.get("case_3_result", "2x organic traffic"),
        "PROCESS_HEADING":      c.get("process_heading", "How We Work"),
        "PROCESS_SUBHEADING":   c.get("process_subheading", "A clear process so you always know what's happening."),
        "STEP_1_NAME":          c.get("step_1_name", "Discovery"),
        "STEP_1_DESC":          c.get("step_1_desc", "We learn about your business, goals, and audience."),
        "STEP_2_NAME":          c.get("step_2_name", "Strategy"),
        "STEP_2_DESC":          c.get("step_2_desc", "We build a clear plan with measurable objectives."),
        "STEP_3_NAME":          c.get("step_3_name", "Execution"),
        "STEP_3_DESC":          c.get("step_3_desc", "We build and launch with speed and precision."),
        "STEP_4_NAME":          c.get("step_4_name", "Growth"),
        "STEP_4_DESC":          c.get("step_4_desc", "We optimize and iterate to keep results improving."),

        # Real estate specific
        "LISTINGS_HEADING":     c.get("listings_heading", "Featured Properties"),
        "LISTING_1_STATUS":     c.get("listing_1_status", "For Sale"),
        "LISTING_1_PRICE":      c.get("listing_1_price", "$000,000"),
        "LISTING_1_ADDRESS":    c.get("listing_1_address", "123 Main Street"),
        "LISTING_1_CITY":       c.get("listing_1_city", "Phoenix, AZ"),
        "LISTING_1_BEDS":       c.get("listing_1_beds", "3"),
        "LISTING_1_BATHS":      c.get("listing_1_baths", "2"),
        "LISTING_1_SQFT":       c.get("listing_1_sqft", "1,800"),
        "LISTING_2_STATUS":     c.get("listing_2_status", "For Sale"),
        "LISTING_2_PRICE":      c.get("listing_2_price", "$000,000"),
        "LISTING_2_ADDRESS":    c.get("listing_2_address", "456 Oak Avenue"),
        "LISTING_2_CITY":       c.get("listing_2_city", "Phoenix, AZ"),
        "LISTING_2_BEDS":       c.get("listing_2_beds", "4"),
        "LISTING_2_BATHS":      c.get("listing_2_baths", "3"),
        "LISTING_2_SQFT":       c.get("listing_2_sqft", "2,200"),
        "LISTING_3_STATUS":     c.get("listing_3_status", "New Listing"),
        "LISTING_3_PRICE":      c.get("listing_3_price", "$000,000"),
        "LISTING_3_ADDRESS":    c.get("listing_3_address", "789 Elm Drive"),
        "LISTING_3_CITY":       c.get("listing_3_city", "Phoenix, AZ"),
        "LISTING_3_BEDS":       c.get("listing_3_beds", "3"),
        "LISTING_3_BATHS":      c.get("listing_3_baths", "2"),
        "LISTING_3_SQFT":       c.get("listing_3_sqft", "1,650"),
        "AGENT_BIO_1":          c.get("agent_bio_1", "With deep knowledge of the local market, I help buyers and sellers navigate real estate with confidence."),
        "AGENT_BIO_2":          c.get("agent_bio_2", "My approach is straightforward: honest advice, clear communication, and results."),
        "CREDENTIAL_1":         c.get("credential_1", "Licensed Realtor"),
        "CREDENTIAL_2":         c.get("credential_2", "10+ Years Experience"),
        "CREDENTIAL_3":         c.get("credential_3", "Top Producer"),
        "BROKERAGE":            c.get("brokerage", ""),
        "NEIGHBORHOOD_HEADING": c.get("neighborhood_heading", f"Living in {c.get('city', address.split(',')[-1].strip() if ',' in address else 'the Area')}"),
        "NEIGHBORHOOD_SUBHEADING": c.get("neighborhood_subheading", "Every neighborhood has its own character."),
        "NEIGHBORHOOD_1_NAME":  c.get("neighborhood_1_name", "Downtown"),
        "NEIGHBORHOOD_1_INFO":  c.get("neighborhood_1_info", "Urban living · Walkable"),
        "NEIGHBORHOOD_2_NAME":  c.get("neighborhood_2_name", "Midtown"),
        "NEIGHBORHOOD_2_INFO":  c.get("neighborhood_2_info", "Family-friendly · Parks"),
        "NEIGHBORHOOD_3_NAME":  c.get("neighborhood_3_name", "East Side"),
        "NEIGHBORHOOD_3_INFO":  c.get("neighborhood_3_info", "Quiet streets · Good schools"),
        "NEIGHBORHOOD_4_NAME":  c.get("neighborhood_4_name", "West End"),
        "NEIGHBORHOOD_4_INFO":  c.get("neighborhood_4_info", "New development · Modern"),
        "CONTACT_HEADING":      c.get("contact_heading", "Ready to Buy or Sell?"),
        "CONTACT_SUBHEADING":   c.get("contact_subheading", "Schedule a free consultation today."),

        # Digital product specific
        "PRICE":                c.get("price", "47"),
        "OLD_PRICE":            c.get("old_price", "97"),
        "GUARANTEE_TEXT":       c.get("guarantee_text", "30-day money-back guarantee"),
        "PROOF_1":              c.get("proof_1", "500+ customers"),
        "PROOF_2":              c.get("proof_2", "4.9/5 rating"),
        "PROOF_3":              c.get("proof_3", "Instant access"),
        "BENEFITS_HEADING":     c.get("benefits_heading", "What You'll Achieve"),
        "BENEFITS_SUBHEADING":  c.get("benefits_subheading", "Real outcomes from real people."),
        "BENEFIT_1_ICON":       c.get("benefit_1_icon", "🚀"),
        "BENEFIT_1_TITLE":      c.get("benefit_1_title", services[0] if services else "Result 1"),
        "BENEFIT_1_DESC":       c.get("benefit_1_desc", "Clear, actionable steps to get results faster."),
        "BENEFIT_2_ICON":       c.get("benefit_2_icon", "💰"),
        "BENEFIT_2_TITLE":      c.get("benefit_2_title", services[1] if len(services)>1 else "Result 2"),
        "BENEFIT_2_DESC":       c.get("benefit_2_desc", "Proven framework used by hundreds of customers."),
        "BENEFIT_3_ICON":       c.get("benefit_3_icon", "⏱"),
        "BENEFIT_3_TITLE":      c.get("benefit_3_title", services[2] if len(services)>2 else "Result 3"),
        "BENEFIT_3_DESC":       c.get("benefit_3_desc", "Save time with templates and shortcuts."),
        "BENEFIT_4_ICON":       c.get("benefit_4_icon", "🎯"),
        "BENEFIT_4_TITLE":      c.get("benefit_4_title", "Confidence"),
        "BENEFIT_4_DESC":       c.get("benefit_4_desc", "No more guessing — a clear path forward."),
        "FOR_HEADING":          c.get("for_heading", "This Is For You If..."),
        "FOR_1_TITLE":          c.get("for_1_title", "You're just starting out"),
        "FOR_1_DESC":           c.get("for_1_desc", "Perfect for beginners who want a proven roadmap."),
        "FOR_2_TITLE":          c.get("for_2_title", "You want faster results"),
        "FOR_2_DESC":           c.get("for_2_desc", "Skip the trial and error with a clear system."),
        "FOR_3_TITLE":          c.get("for_3_title", "You're ready to invest"),
        "FOR_3_DESC":           c.get("for_3_desc", "You understand that quality tools pay for themselves."),
        "NOT_FOR_DESC":         c.get("not_for_desc", "You're looking for a magic bullet that requires no effort."),
        "INCLUDES_HEADING":     c.get("includes_heading", "Everything Included"),
        "INCLUDE_1_TITLE":      c.get("include_1_title", "Main Guide"),
        "INCLUDE_1_DESC":       c.get("include_1_desc", "The complete system, step by step"),
        "INCLUDE_2_TITLE":      c.get("include_2_title", "Templates"),
        "INCLUDE_2_DESC":       c.get("include_2_desc", "Ready-to-use files, just fill in the blanks"),
        "INCLUDE_3_TITLE":      c.get("include_3_title", "Checklists"),
        "INCLUDE_3_DESC":       c.get("include_3_desc", "Never miss a step with printable checklists"),
        "INCLUDE_4_TITLE":      c.get("include_4_title", "Bonus Resource"),
        "INCLUDE_4_DESC":       c.get("include_4_desc", "Extra material to accelerate your progress"),
        "INCLUDE_5_TITLE":      c.get("include_5_title", "Video Walkthrough"),
        "INCLUDE_5_DESC":       c.get("include_5_desc", "Screen-recorded tutorial for each section"),
        "INCLUDE_6_TITLE":      c.get("include_6_title", "Lifetime Updates"),
        "INCLUDE_6_DESC":       c.get("include_6_desc", "All future versions included at no extra cost"),
        "BUY_HEADING":          c.get("buy_heading", "Get Instant Access Today"),
        "BUY_INCLUDES_TEXT":    c.get("buy_includes_text", "One-time payment · Instant download · Lifetime access"),
        "BUY_CTA_TEXT":         c.get("buy_cta_text", c.get("cta_text", "Buy Now")),
        "BUY_FEATURE_1":        c.get("buy_feature_1", "Secure checkout via Stripe"),
        "BUY_FEATURE_2":        c.get("buy_feature_2", "PDF + all files delivered by email"),
        "CREATOR_NAME":         c.get("creator_name", c.get("business_name", "")),
    }

    return replacements


def fill_template(html: str, replacements: dict) -> str:
    """Replace all {{PLACEHOLDER}} tokens in the template."""
    for key, value in replacements.items():
        html = html.replace(f"{{{{{key}}}}}", str(value))
    return html


def github_api(method: str, endpoint: str, **kwargs) -> requests.Response:
    """Make a GitHub API call."""
    url = f"https://api.github.com{endpoint}"
    resp = getattr(requests, method)(url, headers=HEADERS, **kwargs)
    return resp


def create_github_repo(repo_slug: str) -> dict:
    """Create a new public GitHub repo under GITHUB_ORG. Returns repo info."""
    print(f"  Creating GitHub repo: {GITHUB_ORG}/{repo_slug} ...")

    # Check if repo already exists
    resp = github_api("get", f"/repos/{GITHUB_ORG}/{repo_slug}")
    if resp.status_code == 200:
        print(f"  Repo already exists, using it.")
        return resp.json()

    resp = github_api("post", f"/orgs/{GITHUB_ORG}/repos", json={
        "name": repo_slug,
        "private": False,
        "description": f"Website built by Meyer Digital Website Factory",
        "auto_init": True,
    })
    # Fall back to user repos if org fails
    if resp.status_code not in (200, 201):
        resp = github_api("post", "/user/repos", json={
            "name": repo_slug,
            "private": False,
            "description": "Website built by Meyer Digital Website Factory",
            "auto_init": True,
        })
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"Failed to create repo: {resp.status_code} {resp.text}")

    data = resp.json()
    print(f"  Repo created: {data.get('html_url')}")
    time.sleep(2)  # Let GitHub settle
    return data


def push_html_file(repo_slug: str, html_content: str, commit_message: str = "Initial site build") -> bool:
    """Push index.html to the repo via GitHub Contents API."""
    print(f"  Pushing index.html to {GITHUB_ORG}/{repo_slug} ...")

    # Check if index.html already exists (to get its SHA for update)
    resp = github_api("get", f"/repos/{GITHUB_ORG}/{repo_slug}/contents/index.html")
    sha = resp.json().get("sha") if resp.status_code == 200 else None

    content_b64 = base64.b64encode(html_content.encode("utf-8")).decode("utf-8")
    payload = {
        "message": commit_message,
        "content": content_b64,
    }
    if sha:
        payload["sha"] = sha

    resp = github_api("put", f"/repos/{GITHUB_ORG}/{repo_slug}/contents/index.html", json=payload)
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"Failed to push file: {resp.status_code} {resp.text}")

    print("  File pushed successfully.")
    return True


def enable_github_pages(repo_slug: str) -> str:
    """Enable GitHub Pages on the main branch. Returns the live URL."""
    print(f"  Enabling GitHub Pages for {GITHUB_ORG}/{repo_slug} ...")

    resp = github_api("post", f"/repos/{GITHUB_ORG}/{repo_slug}/pages", json={
        "source": {
            "branch": "main",
            "path": "/",
        }
    })

    if resp.status_code in (200, 201):
        data = resp.json()
        url = data.get("html_url", f"https://{GITHUB_ORG.lower()}.github.io/{repo_slug}")
        print(f"  Pages enabled: {url}")
        return url
    elif resp.status_code == 409:
        # Already enabled
        url = f"https://{GITHUB_ORG.lower()}.github.io/{repo_slug}"
        print(f"  Pages already enabled: {url}")
        return url
    else:
        print(f"  Warning: Could not enable Pages ({resp.status_code}). URL may not work immediately.")
        return f"https://{GITHUB_ORG.lower()}.github.io/{repo_slug}"


def save_to_tracker(config: dict, live_url: str):
    """Append this build to client-sites.json."""
    if CLIENT_SITES_FILE.exists():
        with open(CLIENT_SITES_FILE) as f:
            sites = json.load(f)
    else:
        sites = []

    entry = {
        "client_name":      config.get("business_name", ""),
        "url":              live_url,
        "template_used":    config.get("template", ""),
        "built_date":       datetime.date.today().isoformat(),
        "payment_status":   config.get("payment_status", "pending"),
        "payment_amount":   config.get("payment_amount", 599),
        "stripe_link":      config.get("stripe_link", ""),
        "github_repo":      f"https://github.com/{GITHUB_ORG}/{config.get('github_repo','')}",
        "notes":            config.get("notes", ""),
    }

    # Update if already tracked
    for i, site in enumerate(sites):
        if site.get("client_name") == entry["client_name"]:
            sites[i] = entry
            break
    else:
        sites.append(entry)

    with open(CLIENT_SITES_FILE, "w") as f:
        json.dump(sites, f, indent=2)
    print(f"  Saved to client-sites.json")


def build(config: dict) -> str:
    """
    Main build function.
    Returns the live URL.
    """
    business = config.get("business_name", "Unknown")
    template = config.get("template", "service-business")
    repo_slug = config.get("github_repo", re.sub(r"[^a-z0-9-]", "-", business.lower()).strip("-"))
    deploy = config.get("deploy", True)

    print(f"\n{'='*60}")
    print(f"  Building: {business}")
    print(f"  Template: {template}")
    print(f"  Repo:     {GITHUB_ORG}/{repo_slug}")
    print(f"{'='*60}")

    # 1. Load + fill template
    print("\n[1/5] Loading template...")
    html = load_template(template)

    print("[2/5] Filling placeholders...")
    replacements = build_replacements(config)
    html = fill_template(html, replacements)

    # Count unfilled placeholders
    remaining = re.findall(r"\{\{[A-Z_]+\}\}", html)
    if remaining:
        unique = sorted(set(remaining))
        print(f"  Note: {len(unique)} placeholder(s) still need manual filling: {unique[:10]}{'...' if len(unique)>10 else ''}")

    if not deploy:
        # Just return the HTML without deploying
        output_path = Path(f"/tmp/{repo_slug}.html")
        output_path.write_text(html, encoding="utf-8")
        print(f"\n  [deploy=false] Site saved to: {output_path}")
        return str(output_path)

    # 2. Create GitHub repo
    print("\n[3/5] Creating GitHub repo...")
    create_github_repo(repo_slug)

    # 3. Push file
    print("\n[4/5] Pushing index.html...")
    push_html_file(repo_slug, html, commit_message=f"Build {business} site via Website Factory")

    # 4. Enable Pages
    print("\n[5/5] Enabling GitHub Pages...")
    live_url = enable_github_pages(repo_slug)

    # 5. Track
    print("\n[✓] Saving to tracker...")
    save_to_tracker(config, live_url)

    print(f"\n{'='*60}")
    print(f"  ✅ DONE!")
    print(f"  Live URL: {live_url}")
    print(f"  (GitHub Pages can take 2–5 min to go live)")
    print(f"{'='*60}\n")

    return live_url


# ─── CLI Entry Point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    source = sys.argv[1]
    config = load_config(source)
    url = build(config)
    print(url)
