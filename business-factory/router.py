#!/usr/bin/env python3
"""
Business Factory — Router
Master orchestrator. Give it any idea; it scores, routes, and executes.

Usage:
  python3 router.py "any business idea"
  python3 router.py "AI productivity course for freelancers"
  python3 router.py "Notion template bundle for founders"
"""

import sys
import json
import os
import subprocess
import argparse
import datetime
import re
from pathlib import Path

# ── OpenAI ────────────────────────────────────────────────────────────────────
try:
    from openai import OpenAI
except ImportError:
    print("openai package required: pip install openai")
    sys.exit(1)

OPENAI_API_KEY = os.environ.get(
    "OPENAI_API_KEY",
    "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"
)
client = OpenAI(api_key=OPENAI_API_KEY)

FACTORY_DIR = Path(__file__).parent
LOG_FILE     = FACTORY_DIR / "factory-log.json"

PIPELINE_MAP = {
    "course":         FACTORY_DIR / "course-pipeline.py",
    "app":            FACTORY_DIR / "builder.py",        # existing
    "service":        FACTORY_DIR / "builder.py",        # uses builder with service spec
    "digital_product": FACTORY_DIR / "builder.py",       # existing digital product flow
}

SCORE_THRESHOLD_AUTO   = 7.0   # ≥ 7: build automatically
SCORE_THRESHOLD_REVIEW = 5.0   # 5–6: research brief, ask for approval


# ── Analysis ──────────────────────────────────────────────────────────────────

def analyze_idea(idea: str) -> dict:
    """Send idea to GPT-4o for scoring and routing."""
    prompt = f"""You are a business analyst for Wolfgang, a serial entrepreneur who builds AI-powered products.

Analyze this business idea and return a JSON object. Be honest and critical — Wolfgang wants signal, not hype.

{{
  "factory_type": "<one of: course, app, digital_product, service>",
  "scores": {{
    "demand": <1-10, how much real market demand exists right now>,
    "buildability": <1-10, how fast and easy to build with AI — 10 = 1 day, 1 = months>,
    "revenue_speed": <1-10, how quickly first dollar arrives after launch>
  }},
  "avg_score": <average of the three, rounded to 1 decimal>,
  "decision": "<BUILD_NOW if avg>=7, RESEARCH_MORE if 5-6, SKIP if <5>",
  "parameters": {{
    "title": "<clean, sellable product title>",
    "topic": "<core subject matter>",
    "target_audience": "<specific person this is for, 1 sentence>",
    "price_point": <suggested USD price>,
    "key_differentiator": "<why this beats alternatives in 1 sentence>"
  }},
  "reasoning": "<2-3 honest sentences on the scoring>",
  "risks": ["<risk 1>", "<risk 2>", "<risk 3>"],
  "pivots": ["<better angle 1 if score is low>", "<better angle 2>"]
}}

Context: Wolfgang builds things like AI apps (PantryMate, SmartBook AI), digital product bundles
(AI Sales Script Bundle, App Launch Playbook), and courses. He favors fast-to-market, AI-leveraged products
with clear audiences. He avoids high-complexity apps, service businesses that require his time, and
anything without a clear launch channel.

Business idea: "{idea}"

Return ONLY valid JSON. No markdown, no extra text.
"""
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    raw = resp.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


# ── Display ───────────────────────────────────────────────────────────────────

DECISION_ICONS = {
    "BUILD_NOW":      "🚀",
    "RESEARCH_MORE":  "🔍",
    "SKIP":           "❌",
}

FACTORY_LABELS = {
    "course":          "Course Pipeline  (course-pipeline.py)",
    "app":             "App Builder      (builder.py)",
    "digital_product": "Digital Product  (builder.py)",
    "service":         "Service Builder  (builder.py)",
}


def print_analysis(idea: str, analysis: dict):
    s = analysis.get("scores", {})
    avg = analysis.get("avg_score", 0)
    decision = analysis.get("decision", "SKIP")
    icon = DECISION_ICONS.get(decision, "❓")
    params = analysis.get("parameters", {})
    factory = analysis.get("factory_type", "unknown")

    print("\n" + "═"*62)
    print("🏭   BUSINESS FACTORY — IDEA ROUTER")
    print("═"*62)
    print(f"\n💡  Idea:     {idea}")
    print(f"🏷️   Type:     {factory.upper()}")
    print(f"🔧  Factory:  {FACTORY_LABELS.get(factory, factory)}")
    print(f"\n📊  SCORES")
    print(f"    Demand         {s.get('demand', 0):>2}/10")
    print(f"    Buildability   {s.get('buildability', 0):>2}/10")
    print(f"    Revenue Speed  {s.get('revenue_speed', 0):>2}/10")
    print(f"    {'─'*22}")
    print(f"    Average        {avg:>4}/10")
    print(f"\n{icon}  DECISION: {decision}")
    print(f"\n📝  {analysis.get('reasoning', '')}")

    if params:
        print(f"\n🎯  PARAMETERS")
        print(f"    Title:      {params.get('title', '')}")
        print(f"    For:        {params.get('target_audience', '')}")
        print(f"    Price:      ${params.get('price_point', 0)}")
        print(f"    Edge:       {params.get('key_differentiator', '')}")

    risks = analysis.get("risks", [])
    if risks:
        print(f"\n⚠️   Risks:")
        for r in risks:
            print(f"    • {r}")

    if decision == "SKIP":
        pivots = analysis.get("pivots", [])
        if pivots:
            print(f"\n🔄  Pivot Suggestions:")
            for p in pivots:
                print(f"    → {p}")

    print("\n" + "═"*62)


# ── Logging ───────────────────────────────────────────────────────────────────

def log_to_file(idea: str, analysis: dict, action_taken: str):
    log = []
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            log = json.load(f)

    log.append({
        "timestamp":    datetime.datetime.utcnow().isoformat(),
        "idea":         idea,
        "factory_type": analysis.get("factory_type"),
        "avg_score":    analysis.get("avg_score"),
        "decision":     analysis.get("decision"),
        "action_taken": action_taken,
        "parameters":   analysis.get("parameters", {}),
    })

    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


# ── Pipeline Invocation ───────────────────────────────────────────────────────

def invoke_course_pipeline(params: dict) -> bool:
    script = PIPELINE_MAP["course"]
    if not script.exists():
        print(f"⚠️  course-pipeline.py not found at {script}")
        return False

    topic    = params.get("topic") or params.get("title", "")
    audience = params.get("target_audience", "")
    price    = int(params.get("price_point", 97))

    cmd = ["python3", str(script), topic, "--audience", audience, "--price", str(price)]
    print(f"\n▶  Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=str(FACTORY_DIR))
    return result.returncode == 0


def invoke_builder(params: dict, factory_type: str) -> bool:
    """Invoke builder.py for digital products, apps, or services.
    For now: print the spec and instruct the human — builder.py needs a JSON spec file."""
    spec = {
        "slug":                  re.sub(r"[^a-z0-9]+", "-", params.get("title", "product").lower()).strip("-"),
        "name":                  params.get("title", ""),
        "tagline":               params.get("key_differentiator", ""),
        "problem":               f"Target: {params.get('target_audience', '')}",
        "solution":              params.get("key_differentiator", ""),
        "price":                 float(params.get("price_point", 29)),
        "price_type":            "one-time",
        "category":              factory_type,
        "bullets":               ["See full spec — generated by router"],
        "guarantee":             "30-day money-back guarantee",
        "day1_launch_plan":      "Post to relevant subreddit + email list",
        "expected_first_sale":   "7 days",
        "fast_roi_estimate_days": 7,
    }
    spec_path = FACTORY_DIR / f"seeds/router-{spec['slug']}.json"
    spec_path.parent.mkdir(exist_ok=True)
    with open(spec_path, "w") as f:
        json.dump(spec, f, indent=2)

    print(f"\n📄  Builder spec saved → {spec_path}")
    print(f"▶  To build: python3 builder.py --file {spec_path}")
    return True


def invoke_pipeline(factory_type: str, params: dict) -> bool:
    if factory_type == "course":
        return invoke_course_pipeline(params)
    elif factory_type in ("app", "digital_product", "service"):
        return invoke_builder(params, factory_type)
    else:
        print(f"⚠️  No pipeline registered for factory type: {factory_type}")
        return False


# ── Research Brief ────────────────────────────────────────────────────────────

def write_research_brief(idea: str, analysis: dict):
    params   = analysis.get("parameters", {})
    title    = params.get("title", idea)
    slug     = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    out_path = FACTORY_DIR / f"research-brief-{slug}.md"

    with open(out_path, "w") as f:
        f.write(f"# Research Brief: {title}\n\n")
        f.write(f"**Idea:** {idea}\n\n")
        f.write(f"**Score:** {analysis.get('avg_score', 0)}/10 (needs ≥7 for auto-build)\n\n")
        f.write(f"**Factory:** {analysis.get('factory_type', 'unknown')}\n\n")
        f.write(f"**Reasoning:** {analysis.get('reasoning', '')}\n\n")
        f.write(f"## Before Building — Validate These\n\n")
        for r in analysis.get("risks", []):
            f.write(f"- [ ] {r}\n")
        f.write(f"\n## Parameters\n\n```json\n{json.dumps(params, indent=2)}\n```\n\n")
        f.write(f"## If You Approve\n\n")
        ft = analysis.get("factory_type", "course")
        if ft == "course":
            f.write(f"```\npython3 course-pipeline.py \"{params.get('topic', '')}\" --price {params.get('price_point', 97)}\n```\n")
        else:
            f.write(f"```\npython3 builder.py --file seeds/[your-spec].json\n```\n")

    return out_path


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Business Factory Router")
    parser.add_argument("idea", nargs="+", help="Business idea to analyze")
    parser.add_argument("--dry-run", action="store_true", help="Analyze only, do not execute")
    args = parser.parse_args()

    idea = " ".join(args.idea)

    print(f"\n⏳  Analyzing: \"{idea}\"...")
    analysis = analyze_idea(idea)
    print_analysis(idea, analysis)

    avg      = analysis.get("avg_score", 0)
    decision = analysis.get("decision", "SKIP")
    factory  = analysis.get("factory_type", "")
    params   = analysis.get("parameters", {})

    if args.dry_run:
        log_to_file(idea, analysis, "dry_run")
        print("\n🔎  Dry run — no pipeline invoked.\n")
        return

    if avg >= SCORE_THRESHOLD_AUTO and decision == "BUILD_NOW":
        print(f"\n🚀  Score {avg}/10 ≥ {SCORE_THRESHOLD_AUTO} — Invoking {factory} pipeline automatically...\n")
        success = invoke_pipeline(factory, params)
        action  = f"auto_built:{factory}" if success else f"pipeline_failed:{factory}"
        log_to_file(idea, analysis, action)

    elif avg >= SCORE_THRESHOLD_REVIEW or decision == "RESEARCH_MORE":
        brief_path = write_research_brief(idea, analysis)
        print(f"\n🔍  Score {avg}/10 — Research brief saved:")
        print(f"    {brief_path}")
        print(f"\n    Review it and run the pipeline manually when ready.")
        log_to_file(idea, analysis, "research_brief_written")

    else:
        print(f"\n❌  Score {avg}/10 — Skipping. See pivot suggestions above.\n")
        log_to_file(idea, analysis, "skipped")

    print()


if __name__ == "__main__":
    main()
