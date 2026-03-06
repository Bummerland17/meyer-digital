#!/usr/bin/env python3
"""
Course Factory — Promotion Pipeline
Usage: python3 promote.py "Course Title Here"
"""

import sys
import json
import os
import re
import argparse
from pathlib import Path
from openai import OpenAI

FACTORY_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(FACTORY_DIR, "config.json")

with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", CONFIG.get("openai_api_key_fallback", ""))
client = OpenAI(api_key=OPENAI_API_KEY)
MODEL = CONFIG.get("model", "gpt-4o")


def slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def gpt(prompt: str, temperature: float = 0.8) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()


def find_course_dir(title: str) -> str:
    slug = slugify(title)
    course_dir = os.path.join(FACTORY_DIR, CONFIG["courses_dir"], slug)
    if os.path.exists(course_dir):
        return course_dir
    # Try fuzzy match
    courses_base = os.path.join(FACTORY_DIR, CONFIG["courses_dir"])
    if os.path.exists(courses_base):
        for d in os.listdir(courses_base):
            if slug[:20] in d or d[:20] in slug:
                return os.path.join(courses_base, d)
    return course_dir


def load_course_context(course_dir: str) -> dict:
    outline_path = os.path.join(course_dir, "outline.json")
    if os.path.exists(outline_path):
        with open(outline_path) as f:
            return json.load(f)
    return {}


def generate_twitter_posts(outline: dict, count: int = 10) -> list:
    print(f"  🐦 Generating {count} Twitter/X posts...")
    modules_preview = ", ".join([m['title'] for m in outline['modules'][:5]])
    prompt = f"""You are a viral Twitter/X copywriter for a serial entrepreneur.

Course: "{outline['title']}"
Subtitle: {outline['subtitle']}
Price: ${outline['price']}
Target: {outline['target_audience']}
Transformation: {outline['transformation']}
Module topics: {modules_preview}
Creator: Wolfgang — built 5 AI businesses simultaneously (PantryMate, SmartBook AI, UnitFix, Wolfpack AI, Wolfpack Real Estate)

Write {count} unique Twitter/X posts. Mix these formats:
- Thread starter (1/🧵)
- Bold statement + proof
- "Most people don't know..."
- Personal story snippet
- Question + answer
- List tweet (3-5 items)
- Controversial take
- Result/transformation story

Rules:
- Max 280 chars per tweet (threads can stack)
- Use line breaks for readability
- Include 1-3 hashtags max
- Some should have a CTA with [LINK]
- Voice: confident, direct, slightly provocative. No corporate fluff.

Return as JSON array: [{{"post": "...", "type": "...", "has_cta": true/false}}]
Return only valid JSON.
"""
    raw = gpt(prompt)
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def generate_linkedin_posts(outline: dict, count: int = 5) -> list:
    print(f"  💼 Generating {count} LinkedIn posts...")
    prompt = f"""You are a LinkedIn content strategist for a serial entrepreneur.

Course: "{outline['title']}"
Price: ${outline['price']}
Target: {outline['target_audience']}
Transformation: {outline['transformation']}
Creator: Wolfgang — built 5 AI revenue streams simultaneously while most people are still "learning to code"

Write {count} LinkedIn posts. Use these formats:
1. Personal story / journey post (500 words)
2. Lessons learned list (7 lessons)
3. Contrarian take / hot take
4. Step-by-step breakdown
5. Results/transformation post

LinkedIn style:
- Start with a hook line (no "I'm excited to announce")
- Use line breaks every 1-2 sentences
- End with a question to drive comments
- Include CTA for the course with [LINK]
- Professional but raw and honest

Return as JSON array: [{{"post": "...", "format": "...", "word_count": 0}}]
Return only valid JSON.
"""
    raw = gpt(prompt)
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def generate_email_broadcasts(outline: dict, count: int = 3) -> list:
    print(f"  📧 Generating {count} email broadcasts...")
    prompt = f"""You are an email marketing expert writing launch emails for a course.

Course: "{outline['title']}"
Price: ${outline['price']}
Target: {outline['target_audience']}
Transformation: {outline['transformation']}

Write {count} emails for a launch sequence:
1. LAUNCH EMAIL — Announce the course is live, story-driven, CTA to buy
2. SOCIAL PROOF EMAIL — Results, what's inside, overcome objections
3. LAST CHANCE EMAIL — Urgency, fear of missing out, final push

Each email:
- Subject line (A/B test: provide 2 options)
- Preview text (60 chars)
- Body (300-400 words)
- P.S. line
- Clear CTA button text

Voice: Personal, direct, like emailing a friend. From Wolfgang.

Return as JSON array:
[{{
  "email_number": 1,
  "type": "launch|social_proof|last_chance",
  "subject_a": "...",
  "subject_b": "...",
  "preview_text": "...",
  "body": "...",
  "cta_text": "...",
  "ps": "..."
}}]
Return only valid JSON.
"""
    raw = gpt(prompt)
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def generate_youtube_description(outline: dict) -> str:
    print(f"  🎬 Generating YouTube video description...")
    prompt = f"""Write a YouTube video description for a course promo video.

Course: "{outline['title']}"
Price: ${outline['price']}
Target: {outline['target_audience']}
Creator: Wolfgang

Description requirements:
- First 2 lines must hook viewers (these show without clicking "more")
- Overview of what the video covers
- 5 timestamps (00:00, 02:30, 05:00, 08:00, 11:00) with made-up but realistic sections
- What's in the course (bullet list)
- Strong CTA with [COURSE LINK]
- Creator bio (1 paragraph)
- 15 SEO tags at the bottom

Format clearly. 400-500 words total.
"""
    return gpt(prompt)


def generate_hacker_news_post(outline: dict) -> str:
    print(f"  🟠 Generating Hacker News Show HN post...")
    prompt = f"""Write a Hacker News "Show HN" post for this course.

Course: "{outline['title']}"
Price: ${outline['price']}
What it teaches: {outline['transformation']}

HN rules:
- Title: "Show HN: [title] – [one line description]" (max 80 chars)
- Body: 150-200 words
- Be technical and honest — HN hates marketing fluff
- Explain the unique approach (using AI agents to build multiple businesses)
- Acknowledge limitations/what it doesn't cover
- Invite genuine feedback

Write just the title and body. No markdown headers.
"""
    return gpt(prompt)


def run_promotion(course_title: str):
    print(f"\n🏭 COURSE FACTORY — PROMOTION PIPELINE")
    print(f"{'='*50}")
    print(f"Course: {course_title}")
    print(f"{'='*50}\n")

    course_dir = find_course_dir(course_title)
    outline = load_course_context(course_dir)

    if not outline:
        print(f"⚠️  Could not find course outline at {course_dir}")
        print("Run pipeline.py first to generate the course.")
        sys.exit(1)

    marketing_dir = os.path.join(course_dir, "marketing")
    os.makedirs(marketing_dir, exist_ok=True)

    # Twitter
    print("📱 GENERATING SOCIAL CONTENT")
    tweets = generate_twitter_posts(outline, 10)
    tweets_md = f"# Twitter/X Posts: {outline['title']}\n\n"
    for i, tweet in enumerate(tweets, 1):
        tweets_md += f"## Post {i} [{tweet.get('type', 'general')}]\n\n"
        tweets_md += f"{tweet['post']}\n\n"
        tweets_md += f"*CTA: {'Yes' if tweet.get('has_cta') else 'No'}*\n\n---\n\n"
    with open(os.path.join(marketing_dir, "twitter-posts.md"), "w") as f:
        f.write(tweets_md)
    print(f"  ✅ 10 Twitter posts saved")

    # LinkedIn
    linkedin = generate_linkedin_posts(outline, 5)
    linkedin_md = f"# LinkedIn Posts: {outline['title']}\n\n"
    for i, post in enumerate(linkedin, 1):
        linkedin_md += f"## Post {i} [{post.get('format', 'general')}]\n\n"
        linkedin_md += f"{post['post']}\n\n---\n\n"
    with open(os.path.join(marketing_dir, "linkedin-posts.md"), "w") as f:
        f.write(linkedin_md)
    print(f"  ✅ 5 LinkedIn posts saved")

    # Emails
    print("\n📧 GENERATING EMAIL SEQUENCE")
    emails = generate_email_broadcasts(outline, 3)
    emails_md = f"# Email Broadcasts: {outline['title']}\n\n"
    for email in emails:
        emails_md += f"## Email {email['email_number']}: {email['type'].replace('_', ' ').title()}\n\n"
        emails_md += f"**Subject A:** {email['subject_a']}\n"
        emails_md += f"**Subject B:** {email['subject_b']}\n"
        emails_md += f"**Preview:** {email['preview_text']}\n\n"
        emails_md += f"---\n\n{email['body']}\n\n"
        emails_md += f"**[{email['cta_text']}]**\n\n"
        emails_md += f"*P.S. {email['ps']}*\n\n---\n\n"
    with open(os.path.join(marketing_dir, "email-broadcasts.md"), "w") as f:
        f.write(emails_md)
    print(f"  ✅ 3 email broadcasts saved")

    # YouTube
    print("\n🎬 GENERATING VIDEO CONTENT")
    yt_desc = generate_youtube_description(outline)
    with open(os.path.join(marketing_dir, "youtube-description.md"), "w") as f:
        f.write(f"# YouTube Description: {outline['title']}\n\n")
        f.write(yt_desc)
    print(f"  ✅ YouTube description saved")

    # HN
    hn_post = generate_hacker_news_post(outline)
    with open(os.path.join(marketing_dir, "hackernews-post.md"), "w") as f:
        f.write(f"# Hacker News Post: {outline['title']}\n\n")
        f.write(hn_post)
    print(f"  ✅ Hacker News post saved")

    print(f"\n{'='*50}")
    print(f"✅ PROMOTION PIPELINE COMPLETE!")
    print(f"📁 Marketing files: {marketing_dir}")
    print(f"{'='*50}")

    return marketing_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Course Promotion Pipeline")
    parser.add_argument("title", nargs="+", help="Course title")
    args = parser.parse_args()
    run_promotion(" ".join(args.title))
