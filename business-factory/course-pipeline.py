#!/usr/bin/env python3
"""
Business Factory — Course Pipeline
Generates a complete online course: outline, module scripts, sales copy,
Gumroad listing, and full marketing assets.

Usage:
  python3 course-pipeline.py "Course Topic" --audience "target audience" --price 97
  python3 course-pipeline.py "The AI Business Stack" --price 97
"""

import sys
import json
import os
import re
import argparse
from pathlib import Path

# ── OpenAI ────────────────────────────────────────────────────────────────────
try:
    from openai import OpenAI
except ImportError:
    print("openai package not found. Run: pip install openai")
    sys.exit(1)

OPENAI_API_KEY = os.environ.get(
    "OPENAI_API_KEY",
    "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"
)
client = OpenAI(api_key=OPENAI_API_KEY)
MODEL = "gpt-4o"

FACTORY_DIR = Path(__file__).parent
PRODUCTS_DIR = FACTORY_DIR / "products"


# ── Utilities ─────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def gpt(prompt: str, temperature: float = 0.7) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()


def parse_json_response(raw: str) -> any:
    """Strip markdown code fences and parse JSON."""
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def log(msg: str):
    print(msg)


# ── Step 1: Course Outline ────────────────────────────────────────────────────

def generate_outline(topic: str, audience: str, price: int) -> dict:
    log("  📋 Generating 10-module course outline...")
    prompt = f"""You are an expert course creator building a premium online course.

Topic: "{topic}"
Target Audience: {audience}
Price: ${price}

Create a 10-module course outline. Return a JSON object:

{{
  "title": "<compelling course title>",
  "subtitle": "<one-line subtitle that sells the transformation>",
  "tagline": "<8-word punchy tagline>",
  "target_audience": "<specific person this is for>",
  "transformation": "<what the student becomes/achieves after completing the course>",
  "price": {price},
  "modules": [
    {{
      "number": 1,
      "title": "<Module Title>",
      "description": "<2 sentences on what this module covers and why it matters>",
      "lessons": [
        {{
          "number": 1,
          "title": "<Lesson Title>",
          "objective": "<single sentence: what student learns or can do after this lesson>"
        }}
      ]
    }}
  ]
}}

Rules:
- Exactly 10 modules
- 3-5 lessons per module
- Module arc: Problem Framing → Foundations → Core Skills → Advanced Execution → Launch & Scale
- Lessons are specific and actionable, not vague
- The course is taught by Wolfgang — serial entrepreneur who built PantryMate, SmartBook AI, UnitFix, Wolfpack AI, and a wholesale real estate business simultaneously using AI agents
- Return ONLY valid JSON, no markdown fences
"""
    return parse_json_response(gpt(prompt, temperature=0.5))


# ── Step 2: Module 1 Scripts ──────────────────────────────────────────────────

def generate_lesson_script(course_title: str, module: dict, lesson: dict) -> str:
    log(f"    📝 Writing: {lesson['title']}...")
    prompt = f"""You are writing a video lesson script for an online course.

Course: "{course_title}"
Module {module['number']}: {module['title']}
Lesson {lesson['number']}: {lesson['title']}
Objective: {lesson['objective']}

Write a complete lesson script (750–950 words) structured as:

[HOOK]
Open with a story, stat, or question that creates immediate relevance.

[WHAT YOU'LL LEARN]
2-3 sentences setting expectations for this lesson.

[CORE CONTENT]
The main teaching. Use 2-3 concrete examples. Be specific — name tools, numbers, scenarios.
Break into clear sub-sections with bolded headers.

[ACTION STEP]
One specific exercise the student does right now. Not "think about it" — actually DO something.

[BRIDGE]
1 sentence connecting to the next lesson.

Tone: Wolfgang's voice — direct, experienced, slightly irreverent. No academic language. No filler.
Write the full script. No meta-commentary, just the script.
"""
    return gpt(prompt, temperature=0.8)


# ── Step 3: Sales Page ────────────────────────────────────────────────────────

def generate_sales_page(outline: dict) -> str:
    log("  💰 Writing sales page copy...")
    modules_text = "\n".join(
        f"Module {m['number']}: {m['title']} — {m['description']}"
        for m in outline["modules"]
    )
    prompt = f"""You are a direct response copywriter. Write a complete, long-form sales page.

Course: {outline['title']}
Subtitle: {outline['subtitle']}
Price: ${outline['price']}
Target: {outline['target_audience']}
Transformation: {outline['transformation']}

Modules:
{modules_text}

Write the full sales page with these sections:

## HEADLINE
Bold, transformation-focused. Not clever — clear.

## SUB-HEADLINE
Who this is for + the timeframe + the mechanism.

## HOOK (150 words)
A story or scenario the reader recognizes as their own situation. Pull them in.

## THE PROBLEM (100 words)
Name the specific frustrations. Be specific enough that readers say "that's exactly me."

## THE SOLUTION (100 words)
Introduce the course. What it is, how it works, why now.

## WHAT'S INSIDE
Each module with 2-3 benefit bullets (not just topic names — outcomes).

## WHO THIS IS FOR
5 bullet "you're the right fit if..." statements.

## WHAT YOU'LL BE ABLE TO DO AFTER
5 specific, concrete outcomes. Not vague promises.

## ABOUT WOLFGANG
3-sentence credibility section. He built PantryMate (AI meal planning app), SmartBook AI (bookkeeping), UnitFix (property maintenance), Wolfpack AI (agent platform), and wholesale real estate — simultaneously — using AI agents. Not a guru. A builder.

## THE OFFER
What's included (list), original value, your price today, anchoring.

## GUARANTEE
30-day no-questions-asked refund. Simple and direct.

## FAQ
5 Q&As that handle real objections (time, skill level, "is this for me", ROI, refund policy).

## FINAL CTA
Strong 3-sentence push. Buy button text: "Get Instant Access — $[price]"

Write in Wolfgang's voice: confident, no fluff, treats the reader as an intelligent adult.
"""
    return gpt(prompt, temperature=0.8)


# ── Step 4: Gumroad Listing ───────────────────────────────────────────────────

def generate_gumroad_listing(outline: dict) -> str:
    log("  🛒 Writing Gumroad listing...")
    modules_json = json.dumps([{"num": m["number"], "title": m["title"]} for m in outline["modules"]])
    prompt = f"""Write a Gumroad product listing.

Course: {outline['title']}
Subtitle: {outline['subtitle']}
Price: ${outline['price']}
Target: {outline['target_audience']}
Transformation: {outline['transformation']}
Modules: {modules_json}

Produce:

**PRODUCT NAME**
(same as course title)

**SHORT DESCRIPTION** (2 sentences — used in Gumroad previews and Google snippets)

**FULL DESCRIPTION** (450-500 words):
- Opening hook
- What's inside (module list with 1-line descriptions)
- Who this is for (3 bullets)
- What you'll be able to do (3 bullets)
- About Wolfgang (1 short paragraph)
- What you get on purchase (files, format, access)

**TAGS** (12 comma-separated discovery tags)

Write in plain text with clear section breaks. No markdown tables.
"""
    return gpt(prompt, temperature=0.7)


# ── Step 5: Marketing Assets ──────────────────────────────────────────────────

def generate_twitter_posts(outline: dict) -> list:
    log("  🐦 Generating 10 Twitter/X posts...")
    prompt = f"""Write 10 Twitter/X posts for this course launch.

Course: "{outline['title']}"
Price: ${outline['price']}
Target: {outline['target_audience']}
Transformation: {outline['transformation']}
Creator: Wolfgang — built 5 AI businesses simultaneously

Post formats to use (mix them):
- Thread opener (hook + 1/🧵)
- Bold statement with proof
- "Most people get this wrong..." take
- Personal story snippet (2-3 lines)
- List tweet (3-5 punchy items)
- Contrarian opinion
- Result/before-after story
- Question + answer
- Quote-style insight
- Direct CTA tweet

Rules:
- Max 280 chars per tweet
- Use line breaks
- 0-2 hashtags max per tweet
- CTA tweets include [LINK]
- Voice: confident, direct, no corporate language

Return JSON array:
[{{"post": "...", "type": "...", "has_cta": true}}]
Return ONLY valid JSON.
"""
    return parse_json_response(gpt(prompt, temperature=0.85))


def generate_linkedin_posts(outline: dict) -> list:
    log("  💼 Generating 5 LinkedIn posts...")
    prompt = f"""Write 5 LinkedIn posts for this course launch.

Course: "{outline['title']}"
Price: ${outline['price']}
Target: {outline['target_audience']}
Transformation: {outline['transformation']}
Creator: Wolfgang — built PantryMate, SmartBook AI, UnitFix, Wolfpack AI, wholesale RE at the same time

Post formats:
1. Personal story / journey (400-500 words, raw and honest)
2. Lessons learned list (7 hard-won lessons, 1 sentence each)
3. Contrarian take / hot take (200-300 words)
4. Step-by-step breakdown (how Wolfgang does it)
5. Transformation/results post with CTA

LinkedIn style:
- Hook line first (no "I'm excited to announce")
- Short paragraphs, line breaks every 1-2 sentences
- End with a genuine question
- CTA posts include [LINK]
- Professional but human

Return JSON array:
[{{"post": "...", "format": "...", "word_count": 0}}]
Return ONLY valid JSON.
"""
    return parse_json_response(gpt(prompt, temperature=0.82))


def generate_email_broadcasts(outline: dict) -> list:
    log("  📧 Generating 3-email launch sequence...")
    prompt = f"""Write a 3-email launch sequence for this course.

Course: "{outline['title']}"
Price: ${outline['price']}
Target: {outline['target_audience']}
Creator: Wolfgang

Email 1 — LAUNCH: Course is live. Story-driven, personal, warm. CTA to buy.
Email 2 — SOCIAL PROOF / INSIDE LOOK: What's in the course, what you'll be able to do, overcome top objections.
Email 3 — LAST CHANCE (sent 48h before cart closes or price increases): Urgency, recap of transformation, address final hesitation.

Each email:
- Subject A + Subject B (A/B test options)
- Preview text (55 chars max)
- Body (280-350 words, from Wolfgang, personal tone)
- CTA button text
- P.S. line (often outperforms the body CTA)

Return JSON array:
[{{
  "number": 1,
  "type": "launch",
  "subject_a": "...",
  "subject_b": "...",
  "preview_text": "...",
  "body": "...",
  "cta_text": "...",
  "ps": "..."
}}]
Return ONLY valid JSON.
"""
    return parse_json_response(gpt(prompt, temperature=0.78))


def generate_youtube_description(outline: dict) -> str:
    log("  🎬 Generating YouTube promo description...")
    prompt = f"""Write a YouTube video description for a course promo/overview video.

Course: "{outline['title']}"
Price: ${outline['price']}
Creator: Wolfgang

Requirements:
- First 2 lines MUST work as a standalone hook (visible before "Show more")
- What the video covers (3-4 bullet points)
- Timestamps (6 sections at 0:00, 1:30, 3:45, 6:20, 9:00, 11:30 — invent realistic labels)
- What's inside the full course
- CTA: [COURSE LINK]
- Wolfgang bio (2 sentences)
- 15 SEO-optimized tags on the last line prefixed with "Tags:"

Total: 380-450 words. Plain text.
"""
    return gpt(prompt, temperature=0.75)


def generate_hn_post(outline: dict) -> str:
    log("  🟠 Generating Hacker News Show HN post...")
    prompt = f"""Write a Hacker News "Show HN" submission for this course.

Course: "{outline['title']}"
Price: ${outline['price']}
What it teaches: {outline['transformation']}
Creator: Wolfgang — built multiple AI products simultaneously, documenting the exact system

HN norms:
- Title format: "Show HN: [Course Title] – [one descriptive clause]" (under 80 chars)
- Body: 150-200 words
- Technical and honest — HN despises marketing language
- Explain the actual system/approach (AI agents for parallel execution)
- Be upfront about what it covers AND what it doesn't
- Invite genuine feedback and questions
- First-person, builder's perspective

Write just the title on line 1, then a blank line, then the body. No headers.
"""
    return gpt(prompt, temperature=0.65)


# ── Main Pipeline ─────────────────────────────────────────────────────────────

def run_pipeline(topic: str, audience: str = None, price: int = 97) -> Path:
    if not audience:
        audience = "entrepreneurs, freelancers, and side-project builders who want to use AI to create multiple income streams"

    print(f"\n{'='*60}")
    print(f"🏭  BUSINESS FACTORY — COURSE PIPELINE")
    print(f"{'='*60}")
    print(f"Topic:    {topic}")
    print(f"Audience: {audience}")
    print(f"Price:    ${price}")
    print(f"{'='*60}\n")

    # ── 1. Outline ────────────────────────────────────────────────────────────
    print("📐 STEP 1: Course Outline")
    outline = generate_outline(topic, audience, price)
    slug = slugify(outline["title"])
    course_dir = PRODUCTS_DIR / slug
    course_dir.mkdir(parents=True, exist_ok=True)

    with open(course_dir / "outline.json", "w") as f:
        json.dump(outline, f, indent=2)

    # Human-readable outline
    md = f"# {outline['title']}\n\n"
    md += f"**{outline['subtitle']}**\n\n"
    md += f"*{outline['tagline']}*\n\n"
    md += f"**For:** {outline['target_audience']}\n\n"
    md += f"**Outcome:** {outline['transformation']}\n\n"
    md += f"**Price:** ${outline['price']}\n\n---\n\n"
    for m in outline["modules"]:
        md += f"## Module {m['number']}: {m['title']}\n\n{m['description']}\n\n"
        for l in m["lessons"]:
            md += f"- **Lesson {l['number']}:** {l['title']} — *{l['objective']}*\n"
        md += "\n"
    with open(course_dir / "outline.md", "w") as f:
        f.write(md)
    print(f"  ✅ Outline → {course_dir}/outline.md")

    # ── 2. Module 1 Scripts ───────────────────────────────────────────────────
    print("\n📝 STEP 2: Module 1 Scripts")
    mod1 = outline["modules"][0]
    scripts_dir = course_dir / "scripts" / "module-01"
    scripts_dir.mkdir(parents=True, exist_ok=True)

    for lesson in mod1["lessons"]:
        script = generate_lesson_script(outline["title"], mod1, lesson)
        fname = f"lesson-{lesson['number']:02d}-{slugify(lesson['title'])}.md"
        with open(scripts_dir / fname, "w") as f:
            f.write(f"# {lesson['title']}\n\n")
            f.write(f"**Module {mod1['number']}:** {mod1['title']}\n")
            f.write(f"**Objective:** {lesson['objective']}\n\n---\n\n")
            f.write(script)
    print(f"  ✅ Scripts → {scripts_dir}/")

    # ── 3. Sales Page ─────────────────────────────────────────────────────────
    print("\n💰 STEP 3: Sales Page")
    sales_page = generate_sales_page(outline)
    with open(course_dir / "sales-page.md", "w") as f:
        f.write(f"# Sales Page: {outline['title']}\n\n{sales_page}")
    print(f"  ✅ Sales page → {course_dir}/sales-page.md")

    # ── 4. Gumroad Listing ────────────────────────────────────────────────────
    print("\n🛒 STEP 4: Gumroad Listing")
    gumroad = generate_gumroad_listing(outline)
    with open(course_dir / "gumroad-listing.md", "w") as f:
        f.write(f"# Gumroad Listing: {outline['title']}\n\n{gumroad}")
    print(f"  ✅ Gumroad listing → {course_dir}/gumroad-listing.md")

    # ── 5. Marketing Assets ───────────────────────────────────────────────────
    print("\n📣 STEP 5: Marketing Assets")
    mkt_dir = course_dir / "marketing"
    mkt_dir.mkdir(exist_ok=True)

    # Twitter
    tweets = generate_twitter_posts(outline)
    tweets_md = f"# Twitter/X Posts — {outline['title']}\n\n"
    for i, t in enumerate(tweets, 1):
        tweets_md += f"## Post {i} `[{t.get('type','general')}]`\n\n{t['post']}\n\n"
        tweets_md += f"*CTA: {'✅' if t.get('has_cta') else '—'}*\n\n---\n\n"
    with open(mkt_dir / "twitter-posts.md", "w") as f:
        f.write(tweets_md)
    print(f"  ✅ 10 tweets → marketing/twitter-posts.md")

    # LinkedIn
    linkedin = generate_linkedin_posts(outline)
    linkedin_md = f"# LinkedIn Posts — {outline['title']}\n\n"
    for i, p in enumerate(linkedin, 1):
        linkedin_md += f"## Post {i} `[{p.get('format','general')}]`\n\n{p['post']}\n\n---\n\n"
    with open(mkt_dir / "linkedin-posts.md", "w") as f:
        f.write(linkedin_md)
    print(f"  ✅ 5 LinkedIn posts → marketing/linkedin-posts.md")

    # Emails
    emails = generate_email_broadcasts(outline)
    emails_md = f"# Email Launch Sequence — {outline['title']}\n\n"
    for e in emails:
        emails_md += f"## Email {e['number']}: {e['type'].replace('_',' ').title()}\n\n"
        emails_md += f"**Subject A:** {e['subject_a']}\n"
        emails_md += f"**Subject B:** {e['subject_b']}\n"
        emails_md += f"**Preview:** {e['preview_text']}\n\n"
        emails_md += f"---\n\n{e['body']}\n\n"
        emails_md += f"**[{e['cta_text']}]**\n\n*P.S. {e['ps']}*\n\n---\n\n"
    with open(mkt_dir / "email-broadcasts.md", "w") as f:
        f.write(emails_md)
    print(f"  ✅ 3 emails → marketing/email-broadcasts.md")

    # YouTube
    yt = generate_youtube_description(outline)
    with open(mkt_dir / "youtube-description.md", "w") as f:
        f.write(f"# YouTube Description — {outline['title']}\n\n{yt}")
    print(f"  ✅ YouTube description → marketing/youtube-description.md")

    # HN
    hn = generate_hn_post(outline)
    with open(mkt_dir / "hackernews-post.md", "w") as f:
        f.write(f"# Hacker News Post — {outline['title']}\n\n{hn}")
    print(f"  ✅ HN post → marketing/hackernews-post.md")

    # ── Done ──────────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"✅  COURSE PIPELINE COMPLETE")
    print(f"📁  {course_dir}")
    print(f"{'='*60}\n")

    return course_dir, outline


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Course Factory Pipeline")
    parser.add_argument("topic", nargs="+", help="Course topic")
    parser.add_argument("--audience", default=None, help="Target audience description")
    parser.add_argument("--price", type=int, default=97, help="Price in USD")
    args = parser.parse_args()

    run_pipeline(" ".join(args.topic), args.audience, args.price)
