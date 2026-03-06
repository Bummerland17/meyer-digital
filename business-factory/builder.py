#!/usr/bin/env python3
"""
Business Factory — Builder
Given an opportunity dict, builds:
  1. Clean landing page HTML
  2. Stripe product + payment link
  3. GitHub Pages deployment (Bummerland17 org)
  4. Entry in active-businesses.json

Usage:
  python3 builder.py --opportunity <id-from-opportunities.json>
  python3 builder.py --manual     (interactive prompts)
  python3 builder.py --file business.json  (pass a pre-built spec)
"""

import json
import sys
import os
import re
import datetime
import urllib.request
import urllib.error
import urllib.parse
import subprocess
import argparse
import textwrap
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
STRIPE_KEY          = "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"
GITHUB_TOKEN        = "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"
GITHUB_ORG          = "Bummerland17"
BASE_URL            = f"https://{GITHUB_ORG.lower()}.github.io"
WORKSPACE           = Path(__file__).parent
ACTIVE_BUSINESSES   = WORKSPACE / "active-businesses.json"
OPPORTUNITIES_FILE  = WORKSPACE / "opportunities.json"
SITES_DIR           = WORKSPACE / "sites"


# ── Stripe helpers ────────────────────────────────────────────────────────────

def stripe_post(endpoint: str, params: dict) -> dict:
    """POST to Stripe API. Returns (success, response_dict)."""
    url = f"https://api.stripe.com/v1/{endpoint}"
    data = urllib.parse.urlencode(params).encode()
    req  = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {STRIPE_KEY}")
    req.add_header("Content-Type",  "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return {"ok": True, "data": json.loads(resp.read().decode())}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            err = json.loads(body)
        except Exception:
            err = {"raw": body}
        return {"ok": False, "error": err, "status": e.code}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def create_stripe_product(name: str, description: str, price_cents: int, price_type: str) -> dict:
    """
    Creates a Stripe product, price, and payment link.
    Returns dict with product_id, price_id, payment_link_url (or error info).
    """
    result = {"product_id": None, "price_id": None, "payment_link": None, "errors": []}

    # 1. Create product
    prod_resp = stripe_post("products", {
        "name":        name,
        "description": description,
        "metadata[source]": "business-factory",
    })
    if not prod_resp["ok"]:
        result["errors"].append(f"Product creation failed: {prod_resp.get('error')}")
        return result
    result["product_id"] = prod_resp["data"]["id"]

    # 2. Create price
    price_params = {
        "product":     result["product_id"],
        "unit_amount": price_cents,
        "currency":    "usd",
    }
    if price_type == "monthly":
        price_params["recurring[interval]"] = "month"

    price_resp = stripe_post("prices", price_params)
    if not price_resp["ok"]:
        result["errors"].append(f"Price creation failed: {price_resp.get('error')}")
        return result
    result["price_id"] = price_resp["data"]["id"]

    # 3. Create payment link
    link_resp = stripe_post("payment_links", {
        "line_items[0][price]":    result["price_id"],
        "line_items[0][quantity]": 1,
    })
    if not link_resp["ok"]:
        result["errors"].append(f"Payment link creation failed: {link_resp.get('error')}")
        # Product + price exist, just no link — document for manual fix
        return result
    result["payment_link"] = link_resp["data"]["url"]

    return result


# ── GitHub helpers ────────────────────────────────────────────────────────────

def github_api(method: str, endpoint: str, body: dict = None) -> dict:
    """Make a GitHub API call. Returns (ok, response)."""
    url  = f"https://api.github.com/{endpoint.lstrip('/')}"
    data = json.dumps(body).encode() if body else None
    req  = urllib.request.Request(url, data=data, method=method.upper())
    req.add_header("Authorization", f"token {GITHUB_TOKEN}")
    req.add_header("Accept",        "application/vnd.github.v3+json")
    req.add_header("Content-Type",  "application/json")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return {"ok": True, "data": json.loads(resp.read().decode())}
    except urllib.error.HTTPError as e:
        body_raw = e.read().decode()
        try:
            err = json.loads(body_raw)
        except Exception:
            err = {"raw": body_raw}
        return {"ok": False, "error": err, "status": e.code}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def ensure_repo(slug: str) -> dict:
    """Create or verify a repo in the Bummerland17 org."""
    # Check if exists
    check = github_api("GET", f"repos/{GITHUB_ORG}/{slug}")
    if check["ok"]:
        return {"ok": True, "created": False, "repo": check["data"]}

    # Create it
    create = github_api("POST", f"orgs/{GITHUB_ORG}/repos", {
        "name":        slug,
        "description": f"Business Factory: {slug}",
        "private":     False,
        "auto_init":   True,
    })
    if not create["ok"]:
        return create

    return {"ok": True, "created": True, "repo": create["data"]}


def deploy_to_github_pages(slug: str, html: str) -> dict:
    """
    Push index.html to the repo and enable GitHub Pages.
    Uses the GitHub Contents API (no git CLI needed).
    """
    import base64

    # 1. Ensure repo exists
    repo_result = ensure_repo(slug)
    if not repo_result["ok"]:
        return {"ok": False, "error": f"Repo creation failed: {repo_result.get('error')}"}

    # Small delay to let GitHub initialize the repo
    import time
    time.sleep(3)

    # 2. Get current SHA of index.html if it exists (needed for updates)
    existing = github_api("GET", f"repos/{GITHUB_ORG}/{slug}/contents/index.html")
    sha = existing["data"].get("sha") if existing["ok"] else None

    # 3. Push index.html
    content_b64 = base64.b64encode(html.encode()).decode()
    put_body = {
        "message": "Deploy landing page via Business Factory",
        "content": content_b64,
    }
    if sha:
        put_body["sha"] = sha

    push = github_api("PUT", f"repos/{GITHUB_ORG}/{slug}/contents/index.html", put_body)
    if not push["ok"]:
        return {"ok": False, "error": f"File push failed: {push.get('error')}"}

    # 4. Enable GitHub Pages (source: main branch, root dir)
    pages = github_api("POST", f"repos/{GITHUB_ORG}/{slug}/pages", {
        "source": {"branch": "main", "path": "/"},
    })
    # 422 = pages already enabled, that's fine
    if not pages["ok"] and pages.get("status") not in (422, 409):
        # Non-fatal — pages might need manual enable if permissions are restricted
        return {
            "ok":      True,
            "url":     f"{BASE_URL}/{slug}",
            "warning": f"Pages API returned {pages.get('status')}: {pages.get('error')} — may need manual enable",
        }

    return {"ok": True, "url": f"{BASE_URL}/{slug}"}


# ── Landing page generator ────────────────────────────────────────────────────

def build_landing_page(spec: dict) -> str:
    """
    Generate a clean, non-sloppy HTML landing page from a business spec dict.
    spec keys: name, tagline, problem, solution, price, price_type,
               payment_link, bullets (list of str), guarantee
    """
    name         = spec["name"]
    tagline      = spec["tagline"]
    problem      = spec["problem"]
    solution     = spec["solution"]
    price        = spec["price"]
    price_type   = spec.get("price_type", "one-time")
    payment_link = spec.get("payment_link", "#")
    bullets      = spec.get("bullets", [])
    guarantee    = spec.get("guarantee", "If it doesn't deliver, email for a full refund.")
    slug         = spec.get("slug", "")

    price_label = f"${price:.0f}" + ("/mo" if price_type == "monthly" else " one-time")

    bullets_html = "\n".join(
        f'          <li>{b}</li>' for b in bullets
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{name}</title>
  <meta name="description" content="{tagline}">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      background: #f9f9f7;
      color: #1a1a1a;
      line-height: 1.6;
    }}

    .hero {{
      background: #1a1a1a;
      color: #f9f9f7;
      padding: 72px 24px 64px;
      text-align: center;
    }}

    .hero h1 {{
      font-size: clamp(2rem, 5vw, 3.2rem);
      font-weight: 800;
      letter-spacing: -0.02em;
      line-height: 1.15;
      max-width: 720px;
      margin: 0 auto 20px;
    }}

    .hero p {{
      font-size: 1.2rem;
      opacity: 0.78;
      max-width: 560px;
      margin: 0 auto 36px;
    }}

    .cta-primary {{
      display: inline-block;
      background: #f0c040;
      color: #1a1a1a;
      font-size: 1.1rem;
      font-weight: 700;
      padding: 16px 36px;
      border-radius: 6px;
      text-decoration: none;
      transition: opacity 0.15s;
    }}
    .cta-primary:hover {{ opacity: 0.88; }}

    .price-tag {{
      display: block;
      margin-top: 12px;
      font-size: 0.95rem;
      opacity: 0.65;
    }}

    section {{
      max-width: 700px;
      margin: 0 auto;
      padding: 60px 24px;
    }}

    section h2 {{
      font-size: 1.6rem;
      font-weight: 700;
      margin-bottom: 16px;
      letter-spacing: -0.01em;
    }}

    section p {{
      font-size: 1.05rem;
      color: #333;
      margin-bottom: 16px;
    }}

    ul.benefits {{
      list-style: none;
      padding: 0;
      margin: 24px 0;
    }}

    ul.benefits li {{
      padding: 10px 0 10px 28px;
      position: relative;
      font-size: 1.05rem;
      border-bottom: 1px solid #e8e8e4;
    }}
    ul.benefits li:last-child {{ border-bottom: none; }}
    ul.benefits li::before {{
      content: "✓";
      position: absolute;
      left: 0;
      color: #2a8a4a;
      font-weight: 700;
    }}

    .guarantee {{
      background: #fff;
      border: 1px solid #e0e0dc;
      border-radius: 8px;
      padding: 24px 28px;
      font-size: 0.97rem;
      color: #444;
      margin-top: 32px;
    }}

    .guarantee strong {{ color: #1a1a1a; }}

    .buy-section {{
      text-align: center;
      background: #1a1a1a;
      color: #f9f9f7;
      padding: 64px 24px;
    }}

    .buy-section h2 {{
      font-size: 1.8rem;
      font-weight: 700;
      margin-bottom: 12px;
    }}

    .buy-section p {{
      opacity: 0.7;
      margin-bottom: 32px;
      font-size: 1.05rem;
    }}

    footer {{
      text-align: center;
      padding: 24px;
      font-size: 0.85rem;
      color: #999;
    }}

    @media (max-width: 500px) {{
      .hero h1 {{ font-size: 1.8rem; }}
    }}
  </style>
</head>
<body>

  <!-- HERO -->
  <div class="hero">
    <h1>{tagline}</h1>
    <p>{problem}</p>
    <a href="{payment_link}" class="cta-primary">Get it for {price_label}</a>
    <span class="price-tag">Instant download · No subscription · Pay once</span>
  </div>

  <!-- PROBLEM / SOLUTION -->
  <section>
    <h2>The problem</h2>
    <p>{problem}</p>

    <h2 style="margin-top: 40px;">What you get</h2>
    <p>{solution}</p>

    <ul class="benefits">
{bullets_html}
    </ul>

    <div class="guarantee">
      <strong>Guarantee:</strong> {guarantee}
    </div>
  </section>

  <!-- BUY -->
  <div class="buy-section">
    <h2>Get {name}</h2>
    <p>{price_label} · Instant delivery · Works immediately</p>
    <a href="{payment_link}" class="cta-primary">Buy now — {price_label}</a>
  </div>

  <footer>
    &copy; {datetime.datetime.utcnow().year} {GITHUB_ORG} &middot;
    Questions? Email hello@{slug}.com
  </footer>

</body>
</html>"""


# ── Active businesses ledger ──────────────────────────────────────────────────

def load_active_businesses() -> list:
    if ACTIVE_BUSINESSES.exists():
        with open(ACTIVE_BUSINESSES) as f:
            return json.load(f)
    return []


def save_active_businesses(businesses: list):
    with open(ACTIVE_BUSINESSES, "w") as f:
        json.dump(businesses, f, indent=2)


def add_business(spec: dict, stripe: dict, url: str):
    """Add a new business entry to active-businesses.json."""
    businesses = load_active_businesses()
    today      = datetime.date.today().isoformat()

    entry = {
        "id":                 spec["slug"],
        "name":               spec["name"],
        "description":        spec.get("tagline", ""),
        "url":                url,
        "stripe_payment_link": stripe.get("payment_link") or spec.get("payment_link", ""),
        "stripe_product_id":  stripe.get("product_id", ""),
        "stripe_price_id":    stripe.get("price_id", ""),
        "stripe_errors":      stripe.get("errors", []),
        "launched_date":      today,
        "first_sale_deadline": (datetime.date.today() + datetime.timedelta(days=7)).isoformat(),
        "kill_date":           (datetime.date.today() + datetime.timedelta(days=30)).isoformat(),
        "category":           spec.get("category", "digital-product"),
        "price":              spec["price"],
        "price_type":         spec.get("price_type", "one-time"),
        "status":             "active",
        "mrr":                0,
        "total_revenue":      0,
        "last_checked":       today,
        "day1_launch_plan":   spec.get("day1_launch_plan", ""),
        "expected_first_sale": spec.get("expected_first_sale", ""),
    }

    # Remove duplicates by id
    businesses = [b for b in businesses if b["id"] != entry["id"]]
    businesses.append(entry)
    save_active_businesses(businesses)
    return entry


# ── Build pipeline ────────────────────────────────────────────────────────────

def build_business(spec: dict, dry_run: bool = False) -> dict:
    """
    Full build pipeline for one business spec.
    Returns summary dict with all results.
    """
    slug = spec["slug"]
    print(f"\n{'─'*60}")
    print(f"Building: {spec['name']} ({slug})")
    print(f"{'─'*60}")

    # 1. Stripe
    print("\n[1/4] Creating Stripe product…")
    if dry_run:
        stripe_result = {"product_id": "dry_run", "price_id": "dry_run",
                         "payment_link": "#", "errors": []}
    else:
        stripe_result = create_stripe_product(
            name        = spec["name"],
            description = spec.get("tagline", spec["name"]),
            price_cents = int(spec["price"] * 100),
            price_type  = spec.get("price_type", "one-time"),
        )

    if stripe_result.get("payment_link"):
        print(f"  ✓ Payment link: {stripe_result['payment_link']}")
        spec["payment_link"] = stripe_result["payment_link"]
    else:
        print(f"  ✗ Stripe errors: {stripe_result.get('errors')}")
        if not spec.get("payment_link"):
            spec["payment_link"] = "#NEEDS_MANUAL_STRIPE"

    # 2. Build HTML
    print("\n[2/4] Building landing page…")
    html = build_landing_page(spec)
    site_dir = SITES_DIR / slug
    site_dir.mkdir(parents=True, exist_ok=True)
    (site_dir / "index.html").write_text(html)
    print(f"  ✓ HTML saved to {site_dir}/index.html")

    # 3. Deploy
    print("\n[3/4] Deploying to GitHub Pages…")
    if dry_run:
        deploy_result = {"ok": True, "url": f"{BASE_URL}/{slug}"}
    else:
        deploy_result = deploy_to_github_pages(slug, html)

    if deploy_result["ok"]:
        live_url = deploy_result["url"]
        print(f"  ✓ Live at: {live_url}")
        if deploy_result.get("warning"):
            print(f"  ⚠ {deploy_result['warning']}")
    else:
        live_url = f"{BASE_URL}/{slug}"
        print(f"  ✗ Deploy failed: {deploy_result.get('error')}")
        print(f"  → Fallback URL: {live_url}")

    # 4. Log
    print("\n[4/4] Logging to active-businesses.json…")
    entry = add_business(spec, stripe_result, live_url)
    print(f"  ✓ Logged")

    summary = {
        "slug":          slug,
        "name":          spec["name"],
        "url":           live_url,
        "payment_link":  spec.get("payment_link", ""),
        "stripe_ok":     bool(stripe_result.get("payment_link")),
        "deploy_ok":     deploy_result["ok"],
        "stripe_errors": stripe_result.get("errors", []),
        "deploy_warning": deploy_result.get("warning"),
        "day1_plan":     spec.get("day1_launch_plan", ""),
    }

    print(f"\n{'═'*60}")
    print(f"DONE: {spec['name']}")
    print(f"  URL:     {summary['url']}")
    print(f"  Stripe:  {'✓' if summary['stripe_ok'] else '✗ manual needed'}")
    print(f"  Deploy:  {'✓' if summary['deploy_ok'] else '✗ manual needed'}")
    print(f"{'═'*60}\n")

    return summary


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Business Factory Builder")
    parser.add_argument("--opportunity", help="ID from opportunities.json to build")
    parser.add_argument("--file", help="Path to a business spec JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Skip live API calls")
    args = parser.parse_args()

    if args.file:
        with open(args.file) as f:
            spec = json.load(f)
        build_business(spec, dry_run=args.dry_run)
    elif args.opportunity:
        with open(OPPORTUNITIES_FILE) as f:
            opps = json.load(f)["opportunities"]
        match = next((o for o in opps if o["id"] == args.opportunity), None)
        if not match:
            print(f"Opportunity '{args.opportunity}' not found.")
            sys.exit(1)
        # Convert opportunity to a rough spec — human should review before running
        spec = {
            "slug": match["id"],
            "name": match["idea"][:60].title(),
            "tagline": match["idea"],
            "problem": f"Many people struggle with: {match['idea']}",
            "solution": "A focused resource to solve this exactly.",
            "price": 9.00,
            "bullets": ["Immediate download", "No fluff", "Works out of the box"],
            "day1_launch_plan": f"Post to {match['scores']['launch_community']}",
        }
        print("Auto-generated spec from opportunity. Review before proceeding.")
        print(json.dumps(spec, indent=2))
        confirm = input("\nProceed with build? [y/N] ")
        if confirm.lower() == "y":
            build_business(spec, dry_run=args.dry_run)
    else:
        print("Usage: builder.py --file spec.json | --opportunity <id> | --dry-run")
        print("\nExample spec JSON:")
        example = {
            "slug": "my-product",
            "name": "My Product",
            "tagline": "The one-sentence hook",
            "problem": "Describe the pain point",
            "solution": "What they actually get",
            "price": 29.00,
            "price_type": "one-time",
            "category": "digital-product",
            "bullets": ["Thing 1", "Thing 2", "Thing 3"],
            "guarantee": "Full refund if it doesn't help.",
            "day1_launch_plan": "Post to r/entrepreneur + email list",
            "expected_first_sale": "Within 3 days",
        }
        print(json.dumps(example, indent=2))
