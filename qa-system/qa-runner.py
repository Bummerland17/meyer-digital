#!/usr/bin/env python3
"""
qa-runner.py — PantryMate Quality Control Runner
Automated rule-based QA checks for emails, pages, scripts, and compliance.

Usage:
    python qa-runner.py --file path/to/content.txt --type email
    python qa-runner.py --file path/to/page.html --type page
    python qa-runner.py --file path/to/script.txt --type script
    python qa-runner.py --file path/to/content.txt --type compliance
    python qa-runner.py --file path/to/content.txt --type all

Exit codes:
    0 = PASS
    1 = FAIL
    2 = ERROR (file not found, invalid type, etc.)
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ─── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
REPORTS_DIR = SCRIPT_DIR / "reports"
CHECKLISTS = {
    "email": SCRIPT_DIR / "email-qa-checklist.json",
    "page": SCRIPT_DIR / "page-qa-checklist.json",
    "script": SCRIPT_DIR / "script-qa-checklist.json",
    "compliance": SCRIPT_DIR / "compliance-checklist.json",
}

# ─── Helpers ───────────────────────────────────────────────────────────────────

def load_file(path: str) -> str:
    """Load content from a file path."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(2)


def load_checklist(content_type: str) -> dict:
    """Load the appropriate checklist JSON."""
    checklist_path = CHECKLISTS.get(content_type)
    if not checklist_path:
        print(f"ERROR: Unknown content type '{content_type}'. Valid types: email, page, script, compliance", file=sys.stderr)
        sys.exit(2)
    try:
        with open(checklist_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Checklist not found: {checklist_path}", file=sys.stderr)
        sys.exit(2)


def save_report(report: dict, content_type: str) -> Path:
    """Save QA report to the reports directory."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    filename = f"{timestamp}-{content_type}.json"
    report_path = REPORTS_DIR / filename
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return report_path


def word_count(text: str) -> int:
    """Count words in text (strips HTML tags first)."""
    clean = re.sub(r"<[^>]+>", " ", text)
    words = clean.split()
    return len(words)


def flag_patterns(content: str, patterns: list, label: str) -> list:
    """Return list of matches found for a set of patterns."""
    flags = []
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            flags.append(f"[{label}] Found: {matches[:3]}")  # limit to first 3
    return flags


# ─── Email QA ──────────────────────────────────────────────────────────────────

def run_email_qa(content: str, checklist: dict) -> dict:
    """Score an email against Hawk's checklist."""
    scores = {}
    flags = []
    notes = []

    # Split subject and body (look for "Subject:" marker)
    subject_match = re.search(r"^Subject:\s*(.+)$", content, re.MULTILINE | re.IGNORECASE)
    subject = subject_match.group(1).strip() if subject_match else ""
    body_start = subject_match.end() if subject_match else 0
    body = content[body_start:].strip()
    body_words = word_count(body)

    # 1. Personalization
    has_business_name = bool(re.search(r"\b[A-Z][a-z]+(?:'s)?\s+(?:Restaurant|Bakery|Café|Cafe|Diner|Bistro|Kitchen|Grill|Bar|Pub|Pizzeria|Catering|Deli|Lounge|Eatery|Hotel|Inn|Hostel|Shop|Store|Market|Gym|Studio|Salon|Spa|Boutique|Agency|Clinic|Office)\b", body) or re.search(r"\{\{business_name\}\}", body, re.IGNORECASE))
    has_unresolved_template = bool(re.search(r"\{\{|\}\}|\[NAME\]|\[BUSINESS\]|\[OWNER\]|\[CITY\]", body))
    if has_unresolved_template:
        scores["personalization"] = 0
        flags.append("Unresolved template variables found in body")
    elif has_business_name:
        scores["personalization"] = 8
    elif re.search(r"\b(your restaurant|your bakery|your café|your business|your shop)\b", body, re.IGNORECASE):
        scores["personalization"] = 6
    else:
        scores["personalization"] = 3
        flags.append("No business name or type detected — may be too generic")

    # 2. Honesty
    honesty_score = 10
    honesty_flags = []
    guaranteed_patterns = [
        r"you will (?:make|earn|get|see)",
        r"guaranteed (?:to|income|revenue|results|profit)",
        r"100%\s+guaranteed",
        r"double your revenue guaranteed",
        r"we guarantee you",
        r"you'll definitely",
    ]
    for p in guaranteed_patterns:
        if re.search(p, body, re.IGNORECASE):
            honesty_score -= 4
            honesty_flags.append(f"Income guarantee phrase detected: '{p}'")

    fake_proof_patterns = [
        r"10,000\+?\s+(?:happy\s+)?(?:clients|customers|businesses)",
        r"as seen on\b",
        r"#1\s+(?:platform|solution|service)",
        r"best in the industry",
    ]
    for p in fake_proof_patterns:
        if re.search(p, body, re.IGNORECASE):
            honesty_score -= 2
            honesty_flags.append(f"Unverifiable claim: '{p}'")

    scores["honesty"] = max(0, honesty_score)
    flags.extend(honesty_flags)

    # 3. Brevity
    if body_words <= 90:
        scores["brevity"] = 10
    elif body_words <= 119:
        scores["brevity"] = 8
    elif body_words == 120:
        scores["brevity"] = 7
    elif body_words <= 150:
        scores["brevity"] = 5
        flags.append(f"Email body is {body_words} words — over the 120-word limit")
    elif body_words <= 200:
        scores["brevity"] = 3
        flags.append(f"Email body is {body_words} words — significantly over limit")
    else:
        scores["brevity"] = 1
        flags.append(f"Email body is {body_words} words — far too long for cold outreach")

    # 4. Subject Line Relevance
    subject_score = 8
    if not subject:
        subject_score = 0
        flags.append("No subject line found (looked for 'Subject: ...' line)")
    else:
        if re.search(r"^(Re:|Fwd:)\s", subject, re.IGNORECASE):
            subject_score -= 4
            flags.append("Deceptive Re:/Fwd: prefix on cold email subject")
        if re.search(r"[A-Z]{3,}", subject):
            subject_score -= 1
            flags.append("ALL CAPS detected in subject line")
        if re.search(r"[!?]{2,}", subject):
            subject_score -= 1
            flags.append("Excessive punctuation in subject line (!! or ??)")
        if len(subject) > 60:
            subject_score -= 1
            flags.append(f"Subject line is {len(subject)} chars — may be clipped in email clients")
    scores["subject_line_relevance"] = max(0, subject_score)

    # 5. CTA Clarity
    cta_patterns = [r"\breply\b", r"\bclick\b", r"\bbook\b", r"\bschedule\b", r"\bvisit\b", r"\bcall\b", r"\bsign up\b", r"\bget started\b"]
    question_marks = len(re.findall(r"\?", body))
    cta_found = any(re.search(p, body, re.IGNORECASE) for p in cta_patterns)

    if cta_found and question_marks <= 1:
        scores["cta_clarity"] = 9
    elif cta_found and question_marks == 2:
        scores["cta_clarity"] = 6
        flags.append("Multiple questions may dilute CTA clarity")
    elif cta_found and question_marks > 2:
        scores["cta_clarity"] = 4
        flags.append(f"Too many questions ({question_marks}) — unclear single CTA")
    else:
        scores["cta_clarity"] = 2
        flags.append("No clear CTA detected (reply/book/click/schedule/visit)")

    # 6. Spam Risk
    spam_score = 10
    spam_triggers = [
        r"FREE!!!",
        r"\bGUARANTEED\b",
        r"\bACT NOW\b",
        r"\bLIMITED TIME OFFER\b",
        r"\bCLICK HERE\b",
        r"\bMAKE MONEY\b",
        r"\bEARN \$",
        r"\bNO RISK\b",
        r"\b100% FREE\b",
        r"\bWINNER\b",
        r"\bYOU HAVE BEEN SELECTED\b",
        r"\bURGENT\b",
        r"\bFINAL NOTICE\b",
        r"\bLAST CHANCE\b",
    ]
    for trigger in spam_triggers:
        if re.search(trigger, body, re.IGNORECASE):
            spam_score -= 2
            flags.append(f"Spam trigger word detected: '{trigger}'")

    # ALL CAPS words (3+ consecutive)
    caps_words = re.findall(r"\b[A-Z]{3,}\b", body)
    caps_words = [w for w in caps_words if w not in ["CTA", "FAQ", "USA", "UK", "API", "AI"]]
    if len(caps_words) > 2:
        spam_score -= 2
        flags.append(f"Multiple ALL CAPS words: {caps_words[:5]}")

    scores["spam_risk"] = max(0, spam_score)

    # 7. Professional Tone
    tone_score = 10
    apologetic_patterns = [
        r"I know you'?re busy",
        r"I'?m sorry to bother",
        r"I won'?t take (?:much of )?your time",
        r"I hope I'?m not interrupting",
    ]
    pushy_patterns = [
        r"you NEED this",
        r"don'?t miss out",
        r"your competitors are already",
        r"you'?re leaving (?:money|revenue) on the table",
        r"please[,.]? please",
    ]
    formal_patterns = [
        r"Dear Sir/Madam",
        r"To Whom It May Concern",
        r"I am writing to",
        r"Please find attached",
    ]

    for p in apologetic_patterns:
        if re.search(p, body, re.IGNORECASE):
            tone_score -= 2
            flags.append(f"Over-apologetic opener: '{p}'")
    for p in pushy_patterns:
        if re.search(p, body, re.IGNORECASE):
            tone_score -= 2
            flags.append(f"Pushy/aggressive language: '{p}'")
    for p in formal_patterns:
        if re.search(p, body, re.IGNORECASE):
            tone_score -= 1
            flags.append(f"Overly formal phrasing: '{p}'")

    scores["professional_tone"] = max(0, tone_score)

    # ─── Scoring Logic ─────────────────────────────────────────────────────────
    total = sum(scores.values())
    honesty = scores["honesty"]
    any_below_5 = any(v < 5 for v in scores.values())

    if honesty < 7:
        verdict = "REJECT"
        action = "Escalate to Wolfgang immediately. Honesty score below threshold."
    elif any_below_5:
        verdict = "FLAG"
        action = "Return to Godfather for revision. One or more criteria scored below 5."
    elif total >= 60:
        verdict = "PASS"
        action = "Proceed to Shield compliance check."
    else:
        verdict = "FLAG"
        action = f"Total score {total}/70 is below 60. Return for revision."

    return {
        "checklist": "email-qa",
        "verdict": verdict,
        "total_score": total,
        "max_score": 70,
        "scores": scores,
        "word_count": body_words,
        "subject": subject,
        "flags": flags,
        "reviewer_notes": f"Hawk's automated review. Total: {total}/70. Honesty: {honesty}/10.",
        "action": action,
    }


# ─── Page QA ───────────────────────────────────────────────────────────────────

def run_page_qa(content: str, checklist: dict) -> dict:
    """Run Lens's checklist against HTML page content."""
    results = {}
    failures = []
    warnings = []

    # 1. Links functional
    placeholder_hrefs = re.findall(r'href=["\'](\s*#\s*|javascript:void|)["\']', content, re.IGNORECASE)
    placeholder_hrefs += re.findall(r'href=["\'][^"\']*(?:placeholder|todo|fixme|tbd)[^"\']*["\']', content, re.IGNORECASE)
    if placeholder_hrefs:
        results["links_functional"] = "FAIL"
        failures.append(f"Placeholder/broken hrefs found: {placeholder_hrefs[:5]}")
    else:
        results["links_functional"] = "PASS"

    # 2. No placeholder text
    placeholder_patterns = [
        r"lorem ipsum",
        r"\[Business Name\]",
        r"\[Owner Name\]",
        r"\[City\]",
        r"\[Phone\]",
        r"\[Email\]",
        r"INSERT HERE",
        r"INSERT TEXT",
        r"\bPLACEHOLDER\b",
        r"YOUR NAME HERE",
        r"COMPANY NAME",
        r"ADD YOUR",
        r"ENTER YOUR",
        r"\bTODO:",
        r"\bFIXME:",
        r"Sample Text",
        r"Dummy Text",
    ]
    found_placeholders = []
    for p in placeholder_patterns:
        if re.search(p, content, re.IGNORECASE):
            found_placeholders.append(p)
    # Also catch unresolved template vars
    template_vars = re.findall(r"\{\{[^}]+\}\}", content)
    if template_vars:
        found_placeholders.extend(template_vars[:5])

    if found_placeholders:
        results["no_placeholder_text"] = "FAIL"
        failures.append(f"Placeholder text detected: {found_placeholders}")
    else:
        results["no_placeholder_text"] = "PASS"

    # 3. Mobile responsive
    has_viewport = bool(re.search(r'<meta[^>]+name=["\']viewport["\']', content, re.IGNORECASE))
    has_media_queries = bool(re.search(r"@media\s*\(", content, re.IGNORECASE))
    has_responsive_framework = bool(re.search(r"bootstrap|tailwind|foundation", content, re.IGNORECASE))
    has_relative_units = bool(re.search(r"(?:width|max-width)\s*:\s*[0-9.]+(?:%|vw|rem|em)", content, re.IGNORECASE))

    if not has_viewport:
        results["mobile_responsive"] = "FAIL"
        failures.append("Missing viewport meta tag — page will not display correctly on mobile")
    elif not (has_media_queries or has_responsive_framework or has_relative_units):
        results["mobile_responsive"] = "FAIL"
        failures.append("Viewport meta tag present but no responsive CSS detected (no @media, no relative units, no framework)")
    else:
        results["mobile_responsive"] = "PASS"

    # 4. Stripe links real
    # Find all links near payment-related buttons
    payment_buttons = re.findall(r'(?:Buy|Purchase|Get Started|Checkout|Order|Pay|Subscribe)[^<]*?href=["\']([^"\']+)["\']|href=["\']([^"\']+)["\'][^>]*>(?:[^<]*?)(?:Buy|Purchase|Get Started|Checkout|Order|Pay|Subscribe)', content, re.IGNORECASE)
    all_hrefs = re.findall(r'href=["\']([^"\']+)["\']', content, re.IGNORECASE)
    stripe_links = [h for h in all_hrefs if "stripe" in h.lower()]
    fake_stripe = [h for h in stripe_links if not re.match(r'^https://buy\.stripe\.com/[a-zA-Z0-9]+$', h)]

    if fake_stripe:
        results["stripe_links_real"] = "FAIL"
        failures.append(f"Invalid Stripe links found (test mode or placeholder): {fake_stripe[:3]}")
    elif not stripe_links:
        # Check if there are payment buttons with non-stripe hrefs
        payment_context = re.search(r"(?:Buy Now|Purchase|Get Started|Checkout|Subscribe)", content, re.IGNORECASE)
        if payment_context:
            results["stripe_links_real"] = "FAIL"
            failures.append("Payment CTA found but no buy.stripe.com link detected — may be missing or using placeholder")
        else:
            results["stripe_links_real"] = "PASS"
    else:
        results["stripe_links_real"] = "PASS"

    # 5. Correct contact email
    emails_found = re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", content)
    wrong_emails = [e for e in emails_found if e.lower() != "hello@pantrymate.net"]
    if wrong_emails:
        results["correct_contact_email"] = "FAIL"
        failures.append(f"Wrong email address(es) found: {wrong_emails[:5]} — should be hello@pantrymate.net")
    else:
        results["correct_contact_email"] = "PASS"

    # 6. Testimonials labeled
    testimonial_sections = re.findall(r'(?:class|id)=["\'][^"\']*(?:testimonial|review|quote)[^"\']*["\']', content, re.IGNORECASE)
    blockquotes = re.findall(r"<blockquote[^>]*>(.+?)</blockquote>", content, re.IGNORECASE | re.DOTALL)
    has_testimonials = bool(testimonial_sections or blockquotes)

    if has_testimonials:
        disclaimer_patterns = [
            r"illustrative example",
            r"sample scenario",
            r"results may vary",
            r"not (?:a )?(?:real|typical) customer",
            r"example only",
            r"fictional scenario",
            r"these results are not typical",
        ]
        has_disclaimer = any(re.search(p, content, re.IGNORECASE) for p in disclaimer_patterns)
        if not has_disclaimer:
            results["testimonials_labeled"] = "FAIL"
            failures.append("Testimonials found but no 'illustrative example' or 'results may vary' disclaimer detected")
        else:
            results["testimonials_labeled"] = "PASS"
    else:
        results["testimonials_labeled"] = "PASS"

    # 7. No heavy dependencies (warning only)
    external_scripts = re.findall(r'<script[^>]+src=["\']https?://([^"\']+)["\']', content, re.IGNORECASE)
    external_styles = re.findall(r'<link[^>]+href=["\']https?://([^"\']+)["\']', content, re.IGNORECASE)
    allowed_external = ["fonts.googleapis.com", "fonts.gstatic.com", "www.googletagmanager.com",
                        "cdn.jsdelivr.net", "buy.stripe.com"]

    non_allowed_scripts = [s for s in external_scripts if not any(a in s for a in allowed_external)]
    non_allowed_styles = [s for s in external_styles if not any(a in s for a in allowed_external)]

    total_external = len(non_allowed_scripts) + len(non_allowed_styles)
    if total_external > 5:
        results["no_heavy_dependencies"] = "FAIL"
        failures.append(f"Heavy external dependencies: {total_external} non-approved external resources loaded")
    elif total_external > 2:
        results["no_heavy_dependencies"] = "WARNING"
        warnings.append(f"Multiple external dependencies found: {non_allowed_scripts[:3] + non_allowed_styles[:3]}")
    else:
        results["no_heavy_dependencies"] = "PASS"

    # ─── Verdict ───────────────────────────────────────────────────────────────
    blocking_fails = [k for k, v in results.items() if v == "FAIL" and k != "no_heavy_dependencies"]
    has_warnings = "WARNING" in results.values()

    if failures and any(v == "FAIL" for v in results.values()):
        verdict = "FAIL"
        action = "Return to Pixel with specific failures listed above. Fix and re-review."
    elif has_warnings and not failures:
        verdict = "PASS_WITH_WARNINGS"
        action = "Proceed to Shield compliance check. Address warnings at Pixel's discretion."
    else:
        verdict = "PASS"
        action = "Proceed to Shield compliance check."

    return {
        "checklist": "page-qa",
        "verdict": verdict,
        "criteria_results": results,
        "failures": failures,
        "warnings": warnings,
        "reviewer_notes": f"Lens's automated review. {len(failures)} failures, {len(warnings)} warnings.",
        "action": action,
    }


# ─── Script QA ─────────────────────────────────────────────────────────────────

def run_script_qa(content: str, checklist: dict) -> dict:
    """Run Echo's checklist against a call script."""
    results = {}
    failures = []

    # Extract sections (look for SECTION_NAME: or [SECTION_NAME])
    def get_section(name: str) -> str:
        pattern = rf"(?:\[{name}\]|{name}:)\s*(.*?)(?=\n\s*(?:\[|\w+:)|\Z)"
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ""

    opening = get_section("OPENING")
    pitch = get_section("PITCH")
    data_capture = get_section("DATA_CAPTURE")
    close = get_section("CLOSE")
    graceful_exit = get_section("GRACEFUL_EXIT")
    objection_handlers_raw = get_section("OBJECTION_HANDLERS")

    # 1. AI disclosure timing
    disclosure_keywords = ["AI", "artificial intelligence", "virtual assistant", "not a human", "automated"]
    opening_words = opening.split() if opening else []
    first_150_of_opening = " ".join(opening_words[:150]) if opening_words else content[:600]

    found_disclosure = any(kw.lower() in first_150_of_opening.lower() for kw in disclosure_keywords)
    word_position = None
    if found_disclosure:
        for i, word in enumerate(opening_words[:150]):
            if any(kw.lower() in word.lower() for kw in disclosure_keywords):
                word_position = i + 1
                break

    if not opening:
        results["ai_disclosure_timing"] = "FAIL"
        failures.append("No OPENING section found in script")
    elif not found_disclosure:
        results["ai_disclosure_timing"] = "FAIL"
        failures.append("AI disclosure not found in OPENING section — must appear within first 37 words (~15 seconds)")
    elif word_position and word_position > 37:
        results["ai_disclosure_timing"] = "FAIL"
        failures.append(f"AI disclosure found at word {word_position} — must be within first 37 words")
    else:
        results["ai_disclosure_timing"] = "PASS"

    # 2. Natural opening
    robotic_patterns = [
        r"I am calling to inform",
        r"please be advised",
        r"we are pleased to (?:offer|inform|announce)",
        r"valued (?:customer|business owner|client)",
        r"per our (?:records|database)",
    ]
    false_continuity = [
        r"as (?:we )?discussed",
        r"following up on our (?:previous |last )?(?:conversation|call|email)",
        r"as I mentioned (?:before|last time)",
    ]

    opening_failures = []
    for p in robotic_patterns:
        if re.search(p, opening, re.IGNORECASE):
            opening_failures.append(f"Robotic phrasing: '{p}'")
    for p in false_continuity:
        if re.search(p, opening, re.IGNORECASE):
            opening_failures.append(f"False continuity on cold call: '{p}'")
    if opening and word_count(opening) > 60:
        opening_failures.append(f"Opening is too long ({word_count(opening)} words) — should be under 60")

    if opening_failures:
        results["natural_opening"] = "FAIL"
        failures.extend(opening_failures)
    else:
        results["natural_opening"] = "PASS"

    # 3. Realistic objection handlers
    if not objection_handlers_raw:
        results["realistic_objection_handlers"] = "FAIL"
        failures.append("No OBJECTION_HANDLERS section found")
    else:
        # Count distinct objections (look for numbered items or 'If:' markers)
        objection_count = len(re.findall(r"(?:^\s*\d+[\.\)]\s|\bIf\s+(?:they|prospect)\b|\"(?:not interested|too busy|already have))", objection_handlers_raw, re.IGNORECASE | re.MULTILINE))
        if objection_count < 3:
            # Try alternate count: look for distinct response blocks
            objection_count = len(re.split(r"\n{2,}", objection_handlers_raw.strip()))

        pressure_patterns = [
            r"you (?:really )?need to",
            r"you should (?:really )?(?:consider|think)",
            r"don'?t miss (?:out|this)",
            r"only \d+ spots? left",
            r"you'?re leaving (?:money|revenue) on the table",
        ]
        pressure_found = [p for p in pressure_patterns if re.search(p, objection_handlers_raw, re.IGNORECASE)]

        if objection_count < 3:
            results["realistic_objection_handlers"] = "FAIL"
            failures.append(f"Only {objection_count} objection handler(s) found — minimum 3 required")
        elif pressure_found:
            results["realistic_objection_handlers"] = "FAIL"
            failures.append(f"Pressure tactics in objection handlers: {pressure_found}")
        else:
            results["realistic_objection_handlers"] = "PASS"

    # 4. Call duration (word count of main flow)
    main_sections = " ".join(filter(None, [opening, pitch, data_capture, close]))
    main_wc = word_count(main_sections)
    if main_wc > 450:
        results["call_duration"] = "FAIL"
        failures.append(f"Main flow is {main_wc} words — exceeds 450 word limit (~3 minutes at 150 WPM)")
    elif main_wc == 0:
        results["call_duration"] = "FAIL"
        failures.append("Could not parse script sections — unable to measure word count")
    else:
        results["call_duration"] = "PASS"

    # 5. Data capture clarity
    if not data_capture:
        # Check if script seems to intend data capture
        if re.search(r"(?:collect|capture|get their|ask for)\s+(?:info|information|email|phone|name)", content, re.IGNORECASE):
            results["data_capture_clarity"] = "FAIL"
            failures.append("Script mentions data collection but has no DATA_CAPTURE section")
        else:
            results["data_capture_clarity"] = "PASS"
    else:
        has_fields = bool(re.search(r"(?:name|email|phone|business name|address)", data_capture, re.IGNORECASE))
        has_confirmation = bool(re.search(r"(?:just to confirm|let me repeat|does that sound right|got it right|correct\?)", data_capture, re.IGNORECASE))
        has_fallback = bool(re.search(r"(?:no problem|that'?s okay|I understand|no worries)", data_capture, re.IGNORECASE))

        dc_failures = []
        if not has_fields:
            dc_failures.append("DATA_CAPTURE section doesn't specify which fields to collect")
        if not has_confirmation:
            dc_failures.append("No confirmation step in DATA_CAPTURE (how does AI verify accuracy?)")
        if not has_fallback:
            dc_failures.append("No fallback if prospect declines to share info")

        if dc_failures:
            results["data_capture_clarity"] = "FAIL"
            failures.extend(dc_failures)
        else:
            results["data_capture_clarity"] = "PASS"

    # 6. Graceful exit
    if not graceful_exit:
        results["graceful_exit"] = "FAIL"
        failures.append("No GRACEFUL_EXIT section found")
    else:
        pushy_exit_patterns = [
            r"\bbut\b(?!\s+(?:if|when))",
            r"\bhowever\b",
            r"just one more (?:thing|question|second)",
            r"before (?:I|we) (?:go|hang up)",
            r"think about what you'?re missing",
            r"you'?ll regret",
        ]
        guilt_pressure = [p for p in pushy_exit_patterns if re.search(p, graceful_exit, re.IGNORECASE)]

        if guilt_pressure:
            results["graceful_exit"] = "FAIL"
            failures.append(f"Graceful exit contains pressure language: {guilt_pressure}")
        else:
            results["graceful_exit"] = "PASS"

    # 7. No false claims
    forbidden_claims = [
        r"we guarantee (?:you|results|outcomes)",
        r"100%\s+of our (?:clients|customers)",
        r"you will (?:make|earn|see|get)",
        r"proven to (?:double|triple|increase) (?:revenue|sales|income)",
        r"no one else (?:does|offers)",
        r"the only (?:solution|platform|service)",
        r"every (?:restaurant|business|client|customer) (?:that|who|we)",
        r"you'?ll definitely",
    ]
    false_claims_found = []
    for p in forbidden_claims:
        if re.search(p, content, re.IGNORECASE):
            false_claims_found.append(p)

    if false_claims_found:
        results["no_false_claims"] = "FAIL"
        failures.append(f"False/unverifiable claims detected: {false_claims_found}")
    else:
        results["no_false_claims"] = "PASS"

    # ─── Verdict ───────────────────────────────────────────────────────────────
    has_failures = any(v == "FAIL" for v in results.values())
    verdict = "FAIL" if has_failures else "PASS"
    action = "Return to Scribe with failures above." if has_failures else "Proceed to Shield compliance check."

    return {
        "checklist": "script-qa",
        "verdict": verdict,
        "criteria_results": results,
        "word_count": {
            "main_flow_total": main_wc,
            "by_section": {
                "OPENING": word_count(opening),
                "PITCH": word_count(pitch),
                "DATA_CAPTURE": word_count(data_capture),
                "CLOSE": word_count(close),
                "GRACEFUL_EXIT": word_count(graceful_exit),
            }
        },
        "failures": failures,
        "reviewer_notes": f"Echo's automated review. {len(failures)} failures found.",
        "action": action,
    }


# ─── Compliance QA ─────────────────────────────────────────────────────────────

def run_compliance_qa(content: str, checklist: dict, content_type_hint: str = "unknown") -> dict:
    """Run Shield's compliance checklist."""
    results = {}
    violations = []

    # Detect content type hints
    is_email = bool(re.search(r"^Subject:", content, re.MULTILINE | re.IGNORECASE))
    is_script = bool(re.search(r"(?:\[OPENING\]|OPENING:|AI disclosure)", content, re.IGNORECASE))
    is_page = bool(re.search(r"<html|<!DOCTYPE|<head>|<body>", content, re.IGNORECASE))

    # 1. TCPA AI disclosure (scripts only)
    if is_script:
        disclosure_keywords = ["AI", "artificial intelligence", "virtual assistant", "not a human", "automated"]
        first_section = content[:600]
        found = any(kw.lower() in first_section.lower() for kw in disclosure_keywords)
        if not found:
            results["tcpa_ai_disclosure"] = "FAIL"
            violations.append("[CRITICAL] TCPA: No AI disclosure in opening section. Legal requirement.")
        else:
            results["tcpa_ai_disclosure"] = "PASS"
    else:
        results["tcpa_ai_disclosure"] = "N/A"

    # 2. DNC opt-out mechanism
    if is_email:
        has_unsub = bool(re.search(r"unsubscribe", content, re.IGNORECASE))
        if not has_unsub:
            results["dnc_opt_out_mechanism"] = "FAIL"
            violations.append("[CRITICAL] CAN-SPAM: No unsubscribe mechanism found in email.")
        else:
            # Check it's not broken
            unsub_href = re.search(r'href=["\']([^"\']*)["\'][^>]*>[^<]*unsubscrib', content, re.IGNORECASE)
            if unsub_href and unsub_href.group(1) in ("#", "", "javascript:void(0)"):
                results["dnc_opt_out_mechanism"] = "FAIL"
                violations.append("[CRITICAL] Unsubscribe link is broken/placeholder.")
            else:
                results["dnc_opt_out_mechanism"] = "PASS"
    elif is_script:
        has_optout = bool(re.search(r"(?:remove|opt.?out|do not call|stop calling)", content, re.IGNORECASE))
        if not has_optout:
            results["dnc_opt_out_mechanism"] = "FAIL"
            violations.append("[CRITICAL] DNC: No opt-out handling found in call script.")
        else:
            results["dnc_opt_out_mechanism"] = "PASS"
    else:
        results["dnc_opt_out_mechanism"] = "PASS"

    # 3. No income guarantees
    guaranteed_patterns = [
        r"you will (?:make|earn|get|see)",
        r"guaranteed (?:to|income|revenue|results|profit)",
        r"100%\s+guaranteed",
        r"we guarantee you",
        r"you'?ll definitely (?:make|earn|see|profit)",
        r"(?:make|earn)\s+\$[\d,]+\s+guaranteed",
    ]
    income_violations = []
    for p in guaranteed_patterns:
        if re.search(p, content, re.IGNORECASE):
            income_violations.append(p)

    if income_violations:
        results["no_income_guarantees"] = "FAIL"
        violations.append(f"[CRITICAL] FTC: Income guarantee language detected: {income_violations}")
    else:
        results["no_income_guarantees"] = "PASS"

    # 4. No fake urgency
    urgency_patterns = [
        r"only \d+ spots? (?:left|remaining|available)",
        r"only \d+ (?:openings?|slots?)",
        r"offer expires",
        r"ends tonight",
        r"last \d+ (?:openings?|spots?)",
        r"this week only",
        r"special pricing ends",
    ]
    urgency_found = []
    for p in urgency_patterns:
        if re.search(p, content, re.IGNORECASE):
            urgency_found.append(p)

    if urgency_found:
        results["no_fake_urgency"] = "FAIL"
        violations.append(f"[HIGH] FTC: Manufactured urgency language (verify or remove): {urgency_found}")
    else:
        results["no_fake_urgency"] = "PASS"

    # 5. No brand impersonation
    impersonation_patterns = [
        r"(?:^|\s)From:.*(?:Google|Amazon|Facebook|Meta|Yelp|DoorDash|Uber Eats|GrubHub)",
        r"(?:^|\s)Subject:.*(?:Your Google|Your Amazon|Your Facebook|Your Yelp)",
        r"(?:I am|I'm|This is) calling (?:from|on behalf of) (?:Google|Amazon|Facebook|Yelp)",
        r"This is (?:Google|Amazon|Facebook|Yelp|DoorDash)",
    ]
    impersonation_found = []
    for p in impersonation_patterns:
        if re.search(p, content, re.IGNORECASE):
            impersonation_found.append(p)

    if impersonation_found:
        results["no_brand_impersonation"] = "FAIL"
        violations.append(f"[CRITICAL] Trademark: Brand impersonation detected: {impersonation_found}")
    else:
        results["no_brand_impersonation"] = "PASS"

    # 6. CAN-SPAM unsubscribe (email only)
    if is_email:
        has_unsub = bool(re.search(r"unsubscribe", content, re.IGNORECASE))
        has_address = bool(re.search(r"\d+\s+\w+\s+(?:Street|St|Avenue|Ave|Blvd|Boulevard|Road|Rd|Lane|Ln|Drive|Dr|Court|Ct|Way|Place|Pl)", content, re.IGNORECASE))

        email_violations = []
        if not has_unsub:
            email_violations.append("No unsubscribe mechanism (CAN-SPAM requirement)")
        if not has_address:
            email_violations.append("No physical sender address (CAN-SPAM requirement)")

        if email_violations:
            results["can_spam_unsubscribe"] = "FAIL"
            violations.append(f"[CRITICAL] CAN-SPAM: {'; '.join(email_violations)}")
        else:
            results["can_spam_unsubscribe"] = "PASS"
    else:
        results["can_spam_unsubscribe"] = "N/A"

    # 7. No misleading subject (email only)
    if is_email:
        subject_match = re.search(r"^Subject:\s*(.+)$", content, re.MULTILINE | re.IGNORECASE)
        if subject_match:
            subject = subject_match.group(1)
            misleading_patterns = [
                r"^Re:\s",
                r"^Fwd:\s",
                r"Action Required",
                r"Your Account",
                r"Invoice",
                r"Confirmation",
                r"Receipt",
            ]
            misleading_found = [p for p in misleading_patterns if re.search(p, subject, re.IGNORECASE)]
            if misleading_found:
                results["no_misleading_subject"] = "FAIL"
                violations.append(f"[CRITICAL] CAN-SPAM: Misleading subject line patterns: {misleading_found}")
            else:
                results["no_misleading_subject"] = "PASS"
        else:
            results["no_misleading_subject"] = "N/A"
    else:
        results["no_misleading_subject"] = "N/A"

    # ─── Verdict ───────────────────────────────────────────────────────────────
    has_failures = any(v == "FAIL" for v in results.values())
    verdict = "FAIL" if has_failures else "PASS"
    action = ("ESCALATE TO WOLFGANG IMMEDIATELY. Do not proceed without human approval."
              if has_failures else "Compliance check passed. Content cleared for delivery.")

    return {
        "checklist": "compliance-qa",
        "verdict": verdict,
        "criteria_results": results,
        "violations": violations,
        "reviewer_notes": f"Shield's automated compliance review. {len(violations)} violation(s) found.",
        "action": action,
    }


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="PantryMate QA Runner — automated quality control checks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--file", "-f", required=True, help="Path to the content file to review")
    parser.add_argument(
        "--type", "-t", required=True,
        choices=["email", "page", "script", "compliance", "all"],
        help="Type of content being reviewed"
    )
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress stdout, only save report")
    args = parser.parse_args()

    content = load_file(args.file)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    types_to_run = ["email", "page", "script", "compliance"] if args.type == "all" else [args.type]

    all_reports = []
    overall_pass = True

    for content_type in types_to_run:
        checklist = load_checklist(content_type)

        if content_type == "email":
            result = run_email_qa(content, checklist)
        elif content_type == "page":
            result = run_page_qa(content, checklist)
        elif content_type == "script":
            result = run_script_qa(content, checklist)
        elif content_type == "compliance":
            result = run_compliance_qa(content, checklist)
        else:
            continue

        report = {
            "qa_runner_version": "1.0.0",
            "timestamp": timestamp,
            "file": str(args.file),
            "content_type": content_type,
            "result": result,
        }

        report_path = save_report(report, content_type)

        if not args.quiet:
            print(f"\n{'='*60}")
            print(f"QA REPORT — {content_type.upper()}")
            print(f"{'='*60}")
            print(f"File:      {args.file}")
            print(f"Timestamp: {timestamp}")
            print(f"Verdict:   {result['verdict']}")

            if "total_score" in result:
                print(f"Score:     {result['total_score']}/{result.get('max_score', 70)}")
                print("\nScores:")
                for k, v in result.get("scores", {}).items():
                    bar = "█" * v + "░" * (10 - v)
                    print(f"  {k:<28} {bar} {v}/10")

            if "criteria_results" in result:
                print("\nCriteria:")
                for k, v in result["criteria_results"].items():
                    icon = "✓" if v == "PASS" else ("⚠" if v == "WARNING" else ("—" if v == "N/A" else "✗"))
                    print(f"  {icon} {k}: {v}")

            if result.get("failures") or result.get("violations") or result.get("flags"):
                issues = result.get("failures") or result.get("violations") or result.get("flags", [])
                print(f"\nIssues ({len(issues)}):")
                for issue in issues:
                    print(f"  • {issue}")

            if result.get("warnings"):
                print(f"\nWarnings ({len(result['warnings'])}):")
                for w in result["warnings"]:
                    print(f"  ⚠ {w}")

            print(f"\nAction:    {result['action']}")
            print(f"Report:    {report_path}")

        if result["verdict"] not in ("PASS", "PASS_WITH_WARNINGS", "N/A"):
            overall_pass = False

        all_reports.append(report)

    if args.type == "all":
        combined_path = save_report({"reports": all_reports, "timestamp": timestamp}, "combined")
        if not args.quiet:
            print(f"\n{'='*60}")
            print(f"COMBINED REPORT: {combined_path}")
            print(f"Overall: {'PASS' if overall_pass else 'FAIL'}")

    sys.exit(0 if overall_pass else 1)


if __name__ == "__main__":
    main()
