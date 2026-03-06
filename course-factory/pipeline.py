#!/usr/bin/env python3
"""
Course Factory Pipeline
Usage: python3 pipeline.py "Course Topic Here" [--price 97]
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


def gpt(prompt: str, temperature: float = 0.7) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()


def generate_outline(topic: str, price: int) -> dict:
    print(f"  📋 Generating course outline...")
    prompt = f"""You are an expert course creator building a premium online course.

Course Topic: "{topic}"
Price Point: ${price}

Create a comprehensive 10-module course outline. Return a JSON object with this structure:

{{
  "title": "<compelling course title>",
  "subtitle": "<one-line subtitle that sells the transformation>",
  "tagline": "<8-word max punchy tagline>",
  "target_audience": "<specific person this is for>",
  "transformation": "<what student gets/becomes after the course>",
  "price": {price},
  "modules": [
    {{
      "number": 1,
      "title": "<Module Title>",
      "description": "<2 sentences on what this module covers>",
      "lessons": [
        {{
          "number": 1,
          "title": "<Lesson Title>",
          "objective": "<what student learns in 1 sentence>"
        }}
      ]
    }}
  ]
}}

Rules:
- 10 modules total
- 3-5 lessons per module
- Lessons should be actionable and specific
- Module flow: Problem → Foundation → Core Skills → Advanced → Launch/Scale
- Return only valid JSON, no markdown fences

Topic: {topic}
"""
    raw = gpt(prompt, temperature=0.5)
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def generate_lesson_script(course_title: str, module_title: str, lesson: dict) -> str:
    print(f"    📝 Writing script: {lesson['title']}...")
    prompt = f"""You are a world-class educator writing a video lesson script.

Course: "{course_title}"
Module: "{module_title}"
Lesson: "{lesson['title']}"
Objective: {lesson['objective']}

Write a complete lesson script (700-900 words) that:
1. Opens with a hook (story, stat, or provocative question)
2. States what students will learn
3. Delivers the core teaching with 2-3 concrete examples
4. Includes a real-world exercise or action step
5. Closes with a bridge to the next lesson

Format with clear sections: [HOOK], [WHAT YOU'LL LEARN], [CORE CONTENT], [ACTION STEP], [BRIDGE]

Write in a conversational, energetic tone. The instructor is Wolfgang — a serial entrepreneur who built 5 revenue streams simultaneously using AI.
"""
    return gpt(prompt, temperature=0.8)


def generate_slides(course_title: str, lesson_title: str, script: str) -> list:
    prompt = f"""Based on this lesson script, create slide deck content.

Course: {course_title}
Lesson: {lesson_title}

Script excerpt:
{script[:1500]}

Create 6 slides. Return JSON array:
[
  {{
    "slide_number": 1,
    "type": "title|content|example|quote|action|summary",
    "title": "<slide title>",
    "bullets": ["<bullet 1>", "<bullet 2>", "<bullet 3>"],
    "speaker_note": "<what to say on this slide>"
  }}
]

Return only valid JSON.
"""
    raw = gpt(prompt, temperature=0.5)
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def generate_sales_page(outline: dict) -> str:
    print(f"  💰 Writing sales page copy...")
    modules_text = "\n".join([
        f"Module {m['number']}: {m['title']} — {m['description']}"
        for m in outline['modules']
    ])
    prompt = f"""You are a world-class direct response copywriter.

Write a complete sales page for this course:

Title: {outline['title']}
Subtitle: {outline['subtitle']}
Price: ${outline['price']}
Target: {outline['target_audience']}
Transformation: {outline['transformation']}

Modules:
{modules_text}

Write a full sales page with these sections:
1. **HEADLINE** — Bold transformation promise
2. **SUB-HEADLINE** — Who this is for + timeframe
3. **HOOK** — Story or pain point (150 words)
4. **THE PROBLEM** — What they're struggling with (100 words)
5. **INTRODUCE THE SOLUTION** — Course intro (100 words)
6. **WHAT'S INSIDE** — Module breakdown with benefits
7. **WHO THIS IS FOR** — 5 bullet ideal customer profile
8. **RESULTS/PROOF** — What students will achieve
9. **ABOUT THE INSTRUCTOR** — Wolfgang's credibility (built PantryMate, SmartBook AI, UnitFix, Wolfpack AI using AI agents)
10. **PRICE + OFFER** — What they get, value stack, price anchor
11. **GUARANTEE** — 30-day money-back
12. **FAQ** — 5 objection-busting Q&As
13. **FINAL CTA** — Strong closing push

Use conversational, high-energy copywriting. Dollar signs, bold claims backed by specifics.
"""
    return gpt(prompt, temperature=0.8)


def generate_gumroad_listing(outline: dict) -> str:
    print(f"  🛒 Writing Gumroad listing...")
    prompt = f"""Write a Gumroad product listing for this course:

Title: {outline['title']}
Subtitle: {outline['subtitle']}
Price: ${outline['price']}
Target: {outline['target_audience']}
Transformation: {outline['transformation']}

Modules: {json.dumps([{{'number': m['number'], 'title': m['title']}} for m in outline['modules']])}

Write:
1. Product name (same as title)
2. Short description (2 sentences, used in previews)
3. Full description (400-500 words) with:
   - What's included
   - Who it's for
   - What you'll be able to do
   - Module list
   - About the creator (Wolfgang, serial AI entrepreneur)
4. Tags (10 comma-separated tags for discovery)

Format clearly with section headers.
"""
    return gpt(prompt, temperature=0.7)


def run_pipeline(topic: str, price: int = None):
    if price is None:
        price = CONFIG["price_points"]["standard_course"]

    print(f"\n🏭 COURSE FACTORY PIPELINE")
    print(f"{'='*50}")
    print(f"Topic: {topic}")
    print(f"Price: ${price}")
    print(f"{'='*50}\n")

    # 1. Generate outline
    print("📐 STEP 1: Course Outline")
    outline = generate_outline(topic, price)
    slug = slugify(outline['title'])
    course_dir = os.path.join(FACTORY_DIR, CONFIG["courses_dir"], slug)
    os.makedirs(course_dir, exist_ok=True)

    with open(os.path.join(course_dir, "outline.json"), "w") as f:
        json.dump(outline, f, indent=2)

    # Save readable outline
    outline_md = f"# {outline['title']}\n\n"
    outline_md += f"**{outline['subtitle']}**\n\n"
    outline_md += f"*{outline['tagline']}*\n\n"
    outline_md += f"**Target:** {outline['target_audience']}\n\n"
    outline_md += f"**Transformation:** {outline['transformation']}\n\n"
    outline_md += f"**Price:** ${outline['price']}\n\n---\n\n"

    for module in outline['modules']:
        outline_md += f"## Module {module['number']}: {module['title']}\n\n"
        outline_md += f"{module['description']}\n\n"
        for lesson in module['lessons']:
            outline_md += f"- **Lesson {lesson['number']}:** {lesson['title']} — *{lesson['objective']}*\n"
        outline_md += "\n"

    with open(os.path.join(course_dir, "outline.md"), "w") as f:
        f.write(outline_md)

    print(f"  ✅ Outline saved: {course_dir}/outline.md")

    # 2. Generate Module 1 scripts (sample)
    print("\n📝 STEP 2: Module 1 Scripts (Sample)")
    module_1 = outline['modules'][0]
    scripts_dir = os.path.join(course_dir, "scripts", "module-01")
    os.makedirs(scripts_dir, exist_ok=True)

    for lesson in module_1['lessons']:
        script = generate_lesson_script(outline['title'], module_1['title'], lesson)
        lesson_slug = slugify(lesson['title'])
        script_path = os.path.join(scripts_dir, f"lesson-{lesson['number']:02d}-{lesson_slug}.md")
        with open(script_path, "w") as f:
            f.write(f"# {lesson['title']}\n\n")
            f.write(f"**Module:** {module_1['title']}\n")
            f.write(f"**Objective:** {lesson['objective']}\n\n---\n\n")
            f.write(script)

    print(f"  ✅ Module 1 scripts saved: {scripts_dir}/")

    # 3. Generate slides for Module 1, Lesson 1
    print("\n🖼️  STEP 3: Slide Deck (Module 1, Lesson 1)")
    first_lesson = module_1['lessons'][0]
    with open(os.path.join(scripts_dir, f"lesson-01-{slugify(first_lesson['title'])}.md")) as f:
        first_script = f.read()

    slides = generate_slides(outline['title'], first_lesson['title'], first_script)
    slides_dir = os.path.join(course_dir, "slides")
    os.makedirs(slides_dir, exist_ok=True)

    with open(os.path.join(slides_dir, "module-01-lesson-01-slides.json"), "w") as f:
        json.dump(slides, f, indent=2)

    # Also save as readable markdown
    slides_md = f"# Slides: {first_lesson['title']}\n\n"
    for slide in slides:
        slides_md += f"---\n\n## Slide {slide['slide_number']}: {slide['title']}\n\n"
        for b in slide.get('bullets', []):
            slides_md += f"- {b}\n"
        slides_md += f"\n*Speaker note: {slide.get('speaker_note', '')}*\n\n"

    with open(os.path.join(slides_dir, "module-01-lesson-01-slides.md"), "w") as f:
        f.write(slides_md)

    print(f"  ✅ Slides saved: {slides_dir}/")

    # 4. Sales page
    print("\n💰 STEP 4: Sales Page")
    sales_page = generate_sales_page(outline)
    with open(os.path.join(course_dir, "sales-page.md"), "w") as f:
        f.write(f"# SALES PAGE: {outline['title']}\n\n")
        f.write(sales_page)
    print(f"  ✅ Sales page saved: {course_dir}/sales-page.md")

    # 5. Gumroad listing
    print("\n🛒 STEP 5: Gumroad Listing")
    gumroad = generate_gumroad_listing(outline)
    with open(os.path.join(course_dir, "gumroad-listing.md"), "w") as f:
        f.write(f"# GUMROAD LISTING: {outline['title']}\n\n")
        f.write(gumroad)
    print(f"  ✅ Gumroad listing saved: {course_dir}/gumroad-listing.md")

    # Update registry
    registry_path = os.path.join(FACTORY_DIR, "..", "factory-factory", "registry.json")
    if os.path.exists(registry_path):
        with open(registry_path) as f:
            registry = json.load(f)
        registry["factories"]["course-factory"]["products"].append(outline["title"])
        with open(registry_path, "w") as f:
            json.dump(registry, f, indent=2)

    print(f"\n{'='*50}")
    print(f"✅ COURSE FACTORY COMPLETE!")
    print(f"📁 Output: {course_dir}")
    print(f"{'='*50}")
    print(f"\n📌 Next step: Run promote.py to generate marketing content")
    print(f"   python3 promote.py \"{outline['title']}\"")

    return outline, course_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Course Factory Pipeline")
    parser.add_argument("topic", nargs="+", help="Course topic")
    parser.add_argument("--price", type=int, default=None, help="Price in USD")
    args = parser.parse_args()

    topic = " ".join(args.topic)
    run_pipeline(topic, args.price)
