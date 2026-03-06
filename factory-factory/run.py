#!/usr/bin/env python3
"""
Factory Factory — Meta-orchestration layer
Usage: python3 run.py "your business idea here"
"""

import sys
import json
import os
import subprocess
from openai import OpenAI

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registry.json")

with open(REGISTRY_PATH) as f:
    REGISTRY = json.load(f)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "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")
client = OpenAI(api_key=OPENAI_API_KEY)


def analyze_idea(idea: str) -> dict:
    """Use GPT-4 to analyze and score a business idea."""
    prompt = f"""You are a business analyst for a serial entrepreneur who builds AI-powered products.

Analyze this business idea and return a JSON object with the following structure:

{{
  "idea_type": "<one of: course, app, saas, service, ebook, community, newsletter, agency, tool, brand>",
  "factory": "<one of: course-factory, app-factory, business-factory, marketing-factory>",
  "scores": {{
    "demand": <1-10, how much market demand exists>,
    "buildability": <1-10, how fast/easy to build with AI>,
    "revenue_speed": <1-10, how quickly it can generate revenue>
  }},
  "total_score": <average of the three scores, rounded to 1 decimal>,
  "decision": "<one of: BUILD_NOW, RESEARCH_MORE, SKIP>",
  "parameters": {{
    "title": "<clean product title>",
    "topic": "<core topic/focus>",
    "target_audience": "<who this is for>",
    "price_point": <suggested price in USD>,
    "key_differentiator": "<why this wins>"
  }},
  "reasoning": "<2-3 sentences on why you scored it this way>",
  "risks": ["<risk 1>", "<risk 2>"],
  "pivots": ["<alternative angle if needed>"]
}}

Business idea: "{idea}"

Return only valid JSON. No markdown, no explanation.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    raw = response.choices[0].message.content.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def invoke_factory(factory_name: str, params: dict) -> str:
    """Invoke a factory with the given parameters."""
    factory_info = REGISTRY["factories"].get(factory_name)
    if not factory_info:
        return f"❌ Factory '{factory_name}' not found in registry."

    factory_path = os.path.join(WORKSPACE, factory_name)
    entry = factory_info.get("entry", "run.py")
    entry_path = os.path.join(factory_path, entry)

    if not os.path.exists(entry_path):
        return f"⚠️  Factory entry point not found: {entry_path}\nFactory is registered but not yet built."

    topic = params.get("topic", params.get("title", ""))
    result = subprocess.run(
        ["python3", entry_path, topic],
        capture_output=True, text=True, cwd=factory_path
    )
    return result.stdout or result.stderr


def print_analysis(idea: str, analysis: dict):
    """Pretty print the analysis results."""
    scores = analysis.get("scores", {})
    total = analysis.get("total_score", 0)
    decision = analysis.get("decision", "UNKNOWN")
    params = analysis.get("parameters", {})

    decision_icons = {
        "BUILD_NOW": "🚀",
        "RESEARCH_MORE": "🔍",
        "SKIP": "❌"
    }
    icon = decision_icons.get(decision, "❓")

    print("\n" + "="*60)
    print("🏭  FACTORY FACTORY — IDEA ANALYSIS")
    print("="*60)
    print(f"\n💡 Idea: {idea}")
    print(f"🏷️  Type: {analysis.get('idea_type', 'unknown').upper()}")
    print(f"🏭  Factory: {analysis.get('factory', 'unknown')}")
    print(f"\n📊 SCORES:")
    print(f"   Demand:         {scores.get('demand', 0)}/10")
    print(f"   Buildability:   {scores.get('buildability', 0)}/10")
    print(f"   Revenue Speed:  {scores.get('revenue_speed', 0)}/10")
    print(f"   ─────────────────────")
    print(f"   TOTAL SCORE:    {total}/10")
    print(f"\n{icon} DECISION: {decision}")
    print(f"\n📝 Reasoning: {analysis.get('reasoning', '')}")

    if params:
        print(f"\n🎯 PARAMETERS:")
        print(f"   Title:          {params.get('title', '')}")
        print(f"   Target:         {params.get('target_audience', '')}")
        print(f"   Price:          ${params.get('price_point', 0)}")
        print(f"   Differentiator: {params.get('key_differentiator', '')}")

    risks = analysis.get("risks", [])
    if risks:
        print(f"\n⚠️  Risks:")
        for r in risks:
            print(f"   • {r}")

    pivots = analysis.get("pivots", [])
    if pivots and decision == "SKIP":
        print(f"\n🔄 Suggested Pivots:")
        for p in pivots:
            print(f"   → {p}")

    print("\n" + "="*60)


def save_analysis(idea: str, analysis: dict):
    """Save analysis to the factory-factory log."""
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ideas_log.json")
    log = []
    if os.path.exists(log_path):
        with open(log_path) as f:
            log = json.load(f)

    log.append({
        "idea": idea,
        "analysis": analysis,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat()
    })

    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 run.py \"your business idea here\"")
        print("Example: python3 run.py \"AI productivity course for freelancers\"")
        sys.exit(1)

    idea = " ".join(sys.argv[1:])

    print(f"\n⏳ Analyzing: \"{idea}\"...")
    analysis = analyze_idea(idea)
    print_analysis(idea, analysis)
    save_analysis(idea, analysis)

    total = analysis.get("total_score", 0)
    decision = analysis.get("decision", "SKIP")
    factory = analysis.get("factory", "")

    if total >= 7 and decision == "BUILD_NOW":
        print(f"\n🚀 Score ≥ 7 — Invoking {factory} automatically...\n")
        result = invoke_factory(factory, analysis.get("parameters", {}))
        print(result)
    elif 5 <= total < 7 or decision == "RESEARCH_MORE":
        params = analysis.get("parameters", {})
        brief_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            f"research_brief_{params.get('title', 'idea').lower().replace(' ', '_')}.md"
        )
        with open(brief_path, "w") as f:
            f.write(f"# Research Brief: {params.get('title', idea)}\n\n")
            f.write(f"**Idea:** {idea}\n\n")
            f.write(f"**Score:** {total}/10\n\n")
            f.write(f"**Reasoning:** {analysis.get('reasoning', '')}\n\n")
            f.write(f"## Suggested Factory\n{factory}\n\n")
            f.write(f"## Questions to Answer Before Building\n")
            for r in analysis.get("risks", []):
                f.write(f"- [ ] {r}\n")
            f.write(f"\n## Parameters\n```json\n{json.dumps(params, indent=2)}\n```\n")
        print(f"\n🔍 Score 5-6 — Research brief saved to:\n   {brief_path}")
    else:
        print(f"\n❌ Score < 5 — Skipping. Consider the pivot suggestions above.")

    print()


if __name__ == "__main__":
    main()
