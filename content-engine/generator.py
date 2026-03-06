#!/usr/bin/env python3
"""
Content Engine — generator.py
Wolfgang's automated TikTok/IG Reels pipeline.

Usage:
    from generator import generate_script, generate_voiceover, generate_video
"""

import os, re, json, time, requests
from pathlib import Path

# ── Load .env manually (no dotenv dep required) ───────────────────────────────
def _load_env():
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

_load_env()

GEMINI_KEY       = os.environ.get("GEMINI_API_KEY", "")
ELEVEN_KEY       = os.environ.get("ELEVENLABS_API_KEY", "")
CREATOMATE_KEY   = os.environ.get("CREATOMATE_API_KEY", "")

# ── Voice IDs ─────────────────────────────────────────────────────────────────
VOICES = {
    "wolfgang":  "CwhRBWXzGAHq8TQ4Fs17",   # Roger — warm, authoritative
    "female":    "EXAVITQu4vr4xnSDxMaL",   # Sarah
    "energetic": "pNInz6obpgDQGcFmaJgB",   # Adam (Alex's voice)
}

# ── Brand config ──────────────────────────────────────────────────────────────
BRAND = {
    "PantryMate": {
        "bg":          "#1a3a2a",
        "accent":      "#4ade80",
        "problem_bg":  "#7f1d1d",
        "solution_bg": "#14532d",
        "stat_color":  "#ffffff",
        "url":         "pantrymate.net",
        "handle":      "@pantrymate",
    },
    "SmartBook AI": {
        "bg":          "#0d1521",
        "accent":      "#3b82f6",
        "problem_bg":  "#1e1b4b",
        "solution_bg": "#0d1521",
        "stat_color":  "#ffffff",
        "url":         "smartbookai.com",
        "handle":      "@smartbookai",
    },
    "UnitFix": {
        "bg":          "#1a1a2e",
        "accent":      "#f59e0b",
        "problem_bg":  "#292524",
        "solution_bg": "#1a1a2e",
        "stat_color":  "#ffffff",
        "url":         "unitfix.com",
        "handle":      "@unitfix",
    },
}

# ── Template IDs ──────────────────────────────────────────────────────────────
TEMPLATES = {
    "bold-text-hook":        "bold-text-hook",
    "split-problem-solution":"split-problem-solution",
    "stat-bomb":             "stat-bomb",
}


# ─────────────────────────────────────────────────────────────────────────────
# 1. SCRIPT GENERATION — Gemini
# ─────────────────────────────────────────────────────────────────────────────

def generate_script(product: str, angle: str, duration: int = 30,
                    template: str = "bold-text-hook") -> dict:
    """
    Generate a TikTok/IG Reels script using Gemini 2.0 Flash.

    Returns a dict with:
        raw_script, hook, body, cta, caption, hashtags,
        thumbnail_text, template, product, angle
    """
    if not GEMINI_KEY:
        raise ValueError("GEMINI_API_KEY not set")

    brand = BRAND.get(product, {})
    url   = brand.get("url", "")
    handle = brand.get("handle", product.lower())

    template_hints = {
        "bold-text-hook": "Word-by-word text reveal. Hook is a single SHOCKING line. Body is 3 ultra-short punchy sentences. Fast cut energy.",
        "split-problem-solution": "Visually split screen: left=problem, right=solution. Hook names the problem directly. Body names the fix. Very direct.",
        "stat-bomb": "Opens with a massive stat/number that stops the scroll. Then explains what it means. Then reveals the solution. Very data-forward.",
    }
    t_hint = template_hints.get(template, "")

    prompt = f"""Write a {duration}-second TikTok/Instagram Reels script for {product}.

Angle: {angle}
Visual template: {template} — {t_hint}
Brand URL: {url}

FORMAT YOUR RESPONSE EXACTLY LIKE THIS (no other text):

HOOK (0-3s): [The single most scroll-stopping line possible — controversial, surprising, or painful. MAX 10 words.]

BODY (3-{duration-5}s): [Fast-paced content. Short sentences. Max 3 lines. Specific beats vague every time. No corporate language. Talk like a person.]

CTA ({duration-5}-{duration}s): [One single action. Mention the URL or handle. Make it feel low-friction.]

CAPTION: [IG/TikTok caption, 2-3 sentences max, conversational, ends with call to action. No emojis in the middle of sentences — only at end if natural.]

HASHTAGS: [Exactly 5 hashtags, mix of niche and broad, relevant to {product} and the angle. Format: #tag1 #tag2 #tag3 #tag4 #tag5]

THUMBNAIL_TEXT: [3-5 bold words for text overlay on thumbnail. ALL CAPS.]

SPOKEN_VOICEOVER: [Just the words to be spoken aloud — no stage directions, no section labels, just the clean script for TTS. Natural speech rhythm.]

RULES:
- Hook must be the single sharpest line you can write. No hedging.
- Body: max 15 words per sentence. Specific numbers beat vague claims.
- CTA: ONE action. "Comment below", "Link in bio", "Go to {url}" — pick one.
- Write like a real person talking to camera, not a marketer writing ad copy.
- The whole thing should feel like it belongs on FoodTok, FinTok, or ProductTok — not like an ad.
"""

    resp = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}",
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=30
    )
    resp.raise_for_status()

    raw = resp.json()["candidates"][0]["content"]["parts"][0]["text"]

    # Parse sections
    def extract(label, text):
        pattern = rf"{re.escape(label)}[^\n]*\n(.*?)(?=\n[A-Z_]{{3,}}[^a-z]|\Z)"
        m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return m.group(1).strip() if m else ""

    hook      = extract("HOOK", raw)
    body      = extract("BODY", raw)
    cta       = extract("CTA", raw)
    caption   = extract("CAPTION", raw)
    hashtags  = extract("HASHTAGS", raw)
    thumb     = extract("THUMBNAIL_TEXT", raw)
    voiceover = extract("SPOKEN_VOICEOVER", raw)

    # Clean bracket labels from lines like "HOOK (0-3s): text"
    for label in ["HOOK", "BODY", "CTA", "CAPTION", "HASHTAGS", "THUMBNAIL_TEXT", "SPOKEN_VOICEOVER"]:
        raw = re.sub(rf"^{label}[^\n]*:", "", raw, flags=re.MULTILINE).strip()

    return {
        "product":        product,
        "angle":          angle,
        "template":       template,
        "duration":       duration,
        "raw_script":     raw,
        "hook":           hook,
        "body":           body,
        "cta":            cta,
        "caption":        caption,
        "hashtags":       hashtags,
        "thumbnail_text": thumb,
        "voiceover_text": voiceover if voiceover else f"{hook}\n{body}\n{cta}",
    }


# ─────────────────────────────────────────────────────────────────────────────
# 2. VOICEOVER GENERATION — ElevenLabs
# ─────────────────────────────────────────────────────────────────────────────

def generate_voiceover(script_text: str,
                        voice_id: str = VOICES["wolfgang"],
                        output_path: str = "output.mp3") -> str | None:
    """
    Generate an MP3 voiceover from script text via ElevenLabs.
    Returns output_path on success, None on failure.
    """
    if not ELEVEN_KEY:
        print("⚠️  ELEVENLABS_API_KEY not set — skipping voiceover")
        return None

    # Strip stage directions and section labels
    spoken = re.sub(r'\[.*?\]', '', script_text)
    spoken = re.sub(r'(?m)^(HOOK|BODY|CTA|CAPTION|HASHTAGS|THUMBNAIL_TEXT|SPOKEN_VOICEOVER)[^\n]*\n?', '', spoken)
    spoken = re.sub(r'\s+', ' ', spoken).strip()

    if not spoken:
        print("⚠️  No spoken text extracted from script")
        return None

    url     = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": ELEVEN_KEY, "Content-Type": "application/json"}
    payload = {
        "text": spoken,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability":        0.45,
            "similarity_boost": 0.78,
            "style":            0.35,
            "use_speaker_boost": True
        }
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(resp.content)
        size_kb = len(resp.content) // 1024
        print(f"✅ Voiceover saved: {output_path} ({size_kb} KB)")
        return output_path
    else:
        print(f"❌ ElevenLabs error {resp.status_code}: {resp.text[:200]}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# 3. VIDEO GENERATION — Creatomate
# ─────────────────────────────────────────────────────────────────────────────

def generate_video(script: dict,
                   voiceover_url: str,
                   template_id: str = "bold-text-hook",
                   output_dir: str = "output") -> dict:
    """
    Queue a Creatomate render using one of Wolfgang's 3 templates.

    Args:
        script:        Output dict from generate_script()
        voiceover_url: Public URL to the MP3 (Creatomate must be able to fetch it)
                       OR a local path — in that case you must host it first.
        template_id:   "bold-text-hook" | "split-problem-solution" | "stat-bomb"
        output_dir:    Where to save the render metadata JSON

    Returns:
        dict with render_id, status, estimated_url, and full API response
    """
    if not CREATOMATE_KEY or CREATOMATE_KEY == "your_creatomate_key_here":
        print("⚠️  CREATOMATE_API_KEY not configured — returning render spec only")
        return _build_render_spec(script, voiceover_url, template_id, queued=False)

    spec   = _build_render_spec(script, voiceover_url, template_id, queued=True)
    payload = {
        "source": spec["source"],
        "output_format": "mp4",
        "webhook_url": None,  # Set this to receive completion notifications
    }

    resp = requests.post(
        "https://api.creatomate.com/v1/renders",
        headers={
            "Authorization": f"Bearer {CREATOMATE_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30
    )

    if resp.status_code in (200, 201):
        data = resp.json()
        # Creatomate returns a list of renders
        render = data[0] if isinstance(data, list) else data
        render_id = render.get("id", "unknown")
        print(f"✅ Creatomate render queued: {render_id}")
        print(f"   Status: {render.get('status', '?')} — check dashboard or poll /renders/{render_id}")

        result = {
            "render_id":     render_id,
            "status":        render.get("status", "queued"),
            "template":      template_id,
            "product":       script["product"],
            "angle":         script["angle"],
            "snapshot_url":  render.get("snapshot_url"),
            "url":           render.get("url"),
            "raw_response":  render,
        }

        # Save metadata
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        meta_path = out / f"render-{render_id}.json"
        meta_path.write_text(json.dumps(result, indent=2))

        return result
    else:
        print(f"❌ Creatomate error {resp.status_code}: {resp.text[:300]}")
        return {"error": resp.text, "status": "failed"}


def poll_render(render_id: str, max_wait: int = 120) -> dict:
    """Poll Creatomate until render is done (or timeout). Returns final render data."""
    if not CREATOMATE_KEY or CREATOMATE_KEY == "your_creatomate_key_here":
        return {"status": "no_key"}

    start = time.time()
    while time.time() - start < max_wait:
        resp = requests.get(
            f"https://api.creatomate.com/v1/renders/{render_id}",
            headers={"Authorization": f"Bearer {CREATOMATE_KEY}"},
            timeout=15
        )
        if resp.status_code == 200:
            data = resp.json()
            status = data.get("status")
            print(f"   Render {render_id}: {status}")
            if status in ("succeeded", "failed"):
                return data
        time.sleep(5)

    return {"status": "timeout", "render_id": render_id}


def _build_render_spec(script: dict, voiceover_url: str,
                        template_id: str, queued: bool) -> dict:
    """Build the Creatomate source JSON for a given template."""
    product = script["product"]
    b       = BRAND.get(product, BRAND["PantryMate"])

    hook = script.get("hook", "")
    body = script.get("body", "")
    cta  = script.get("cta", "")
    dur  = script.get("duration", 30)

    if template_id == "bold-text-hook":
        source = {
            "output_format": "mp4",
            "width": 1080,
            "height": 1920,
            "frame_rate": 30,
            "duration": dur,
            "elements": [
                _rect("background", "0%", "0%", "100%", "100%", b["bg"], z=0),
                _rect("accent_bar_top", "0%", "0%", "100%", "8px", b["accent"], z=2),
                _rect("accent_bar_bottom", "0%", f"calc(100% - 8px)", "100%", "8px", b["accent"], z=2),
                _text("hook_text", hook.upper(), "8%", "22%", "84%",
                      font="Montserrat", weight="900", size="72px",
                      color="#ffffff", transform="uppercase", lh=1.1,
                      animations=[_word_appear(0.0, b["accent"])], z=10),
                _text("body_text", body, "8%", "48%", "84%",
                      font="Inter", weight="600", size="42px",
                      color="#e8e8e8", lh=1.35,
                      animations=[_word_appear(3.0, "#e8e8e8")], z=10),
                _rect("cta_box", "8%", "80%", "84%", "120px",
                      b["accent"], z=9, radius="16px",
                      animations=[_scale_in(dur - 6)]),
                _text("cta_text", cta, "8%", "80%", "84%",
                      font="Montserrat", weight="800", size="36px",
                      color="#000000", align="center", valign="middle",
                      height="120px",
                      animations=[_fade_in(dur - 5.7)], z=11),
                _text("brand_tag", b["handle"], "8%", "91%", "84%",
                      font="Inter", weight="400", size="28px",
                      color=b["accent"], opacity=0.7, align="center", z=10),
                _audio("voiceover", voiceover_url, z=20),
            ]
        }

    elif template_id == "split-problem-solution":
        # Parse problem/solution from hook and body
        parts = body.split("\n\n") if "\n\n" in body else [body, ""]
        prob_text = hook
        sol_text  = parts[0] if parts else body
        source = {
            "output_format": "mp4",
            "width": 1080,
            "height": 1920,
            "frame_rate": 30,
            "duration": dur,
            "elements": [
                _rect("problem_panel", "0%", "0%", "50%", "100%", b["problem_bg"], z=1),
                _rect("solution_panel", "50%", "0%", "50%", "100%", b["solution_bg"], z=2),
                _rect("divider", "50%", "0%", "4px", "100%", "#ffffff", opacity=0.15, z=15),
                _text("prob_label", "THE PROBLEM", "4%", "8%", "44%",
                      font="Montserrat", weight="900", size="30px",
                      color="#ef4444", ls="3px",
                      animations=[_fade_in(0.3)], z=10),
                _text("prob_icon", "❌", "4%", "14%", "44%",
                      font="Inter", weight="400", size="80px",
                      color="#ffffff",
                      animations=[_scale_in(0.4)], z=10),
                _text("prob_headline", prob_text.upper(), "4%", "26%", "44%",
                      font="Montserrat", weight="800", size="48px",
                      color="#ffffff", lh=1.15, transform="uppercase",
                      animations=[_word_appear(0.5, "#ef4444")], z=10),
                _text("sol_label", "THE FIX", "52%", "8%", "44%",
                      font="Montserrat", weight="900", size="30px",
                      color=b["accent"], ls="3px",
                      animations=[_fade_in(3.5)], z=10),
                _text("sol_icon", "✅", "52%", "14%", "44%",
                      font="Inter", weight="400", size="80px",
                      color="#ffffff",
                      animations=[_scale_in(3.6)], z=10),
                _text("sol_headline", sol_text.upper(), "52%", "26%", "44%",
                      font="Montserrat", weight="800", size="48px",
                      color="#ffffff", lh=1.15, transform="uppercase",
                      animations=[_word_appear(3.8, b["accent"])], z=10),
                _text("sol_detail", cta, "52%", "62%", "44%",
                      font="Inter", weight="600", size="32px",
                      color=b["accent"], lh=1.3,
                      animations=[_fade_in(4.5)], z=10),
                _rect("cta_bar", "0%", "88%", "100%", "100px",
                      b["accent"], z=20,
                      animations=[_slide_in_bottom(dur - 5)]),
                _text("cta_text", f"→ {b['url']}", "0%", "88%", "100%",
                      font="Montserrat", weight="800", size="34px",
                      color="#000000", align="center", valign="middle",
                      height="100px",
                      animations=[_fade_in(dur - 4.7)], z=21),
                _audio("voiceover", voiceover_url, z=30),
            ]
        }

    elif template_id == "stat-bomb":
        # Extract stat from hook (look for number pattern)
        stat_match = re.search(r'[\$€£]?[\d,]+[%kmb]?', hook, re.IGNORECASE)
        stat_num   = stat_match.group(0) if stat_match else hook[:8]
        stat_label = hook.replace(stat_num, "").strip() or body[:50]
        source = {
            "output_format": "mp4",
            "width": 1080,
            "height": 1920,
            "frame_rate": 30,
            "duration": dur,
            "elements": [
                _rect("background", "0%", "0%", "100%", "100%", b["bg"], z=0),
                _rect("flash", "0%", "0%", "100%", "100%", "#ffffff", z=50,
                      animations=[_fade_out(0.0, 0.25)]),
                _text("pre_hook", "Did you know...", "8%", "12%", "84%",
                      font="Inter", weight="500", size="38px",
                      color="#aaaaaa", align="center",
                      animations=[_fade_in(0.25)], z=10),
                _text("stat_number", stat_num, "4%", "28%", "92%",
                      font="Montserrat", weight="900", size="180px",
                      color="#ffffff", align="center", lh=0.95,
                      animations=[_scale_impact(0.5)], z=10),
                _text("stat_label", stat_label.upper(), "8%", "58%", "84%",
                      font="Montserrat", weight="700", size="52px",
                      color=b["accent"], align="center", ls="1px",
                      transform="uppercase",
                      animations=[_word_appear(0.9, b["accent"])], z=10),
                _rect("divider", "8%", "72%", "84%", "3px", b["accent"], z=9,
                      animations=[_width_reveal(1.8)]),
                _text("solution", body, "8%", "74%", "84%",
                      font="Inter", weight="600", size="42px",
                      color="#ffffff", align="center", lh=1.35,
                      animations=[_word_appear(2.2, "#ffffff")], z=10),
                _rect("cta_pill", "15%", "88%", "70%", "90px",
                      b["accent"], z=20, radius="50px",
                      animations=[_scale_in(dur - 5)]),
                _text("cta_text", cta, "15%", "88%", "70%",
                      font="Montserrat", weight="800", size="30px",
                      color="#000000", align="center", valign="middle",
                      height="90px",
                      animations=[_fade_in(dur - 4.6)], z=21),
                _audio("voiceover", voiceover_url, z=30),
            ]
        }
    else:
        raise ValueError(f"Unknown template_id: {template_id}")

    return {"source": source, "queued": queued}


# ── Element builder helpers ───────────────────────────────────────────────────

def _rect(id_, x, y, w, h, fill, z=0, radius=None, opacity=None, animations=None):
    el = {"id": id_, "type": "rectangle",
          "x": x, "y": y, "width": w, "height": h,
          "fill_color": fill, "z_index": z}
    if radius:   el["border_radius"] = radius
    if opacity is not None: el["opacity"] = opacity
    if animations: el["animations"] = animations
    return el

def _text(id_, text, x, y, w, font="Inter", weight="600", size="40px",
          color="#ffffff", align="left", valign=None, height=None,
          lh=None, ls=None, opacity=None, transform=None,
          animations=None, z=10):
    el = {"id": id_, "type": "text", "text": text,
          "x": x, "y": y, "width": w,
          "font_family": font, "font_weight": weight,
          "font_size": size, "fill_color": color,
          "text_align": align, "z_index": z}
    if height:    el["height"] = height
    if valign:    el["vertical_align"] = valign
    if lh:        el["line_height"] = lh
    if ls:        el["letter_spacing"] = ls
    if opacity is not None: el["opacity"] = opacity
    if transform: el["text_transform"] = transform
    if animations: el["animations"] = animations
    return el

def _audio(id_, source, z=20):
    return {"id": id_, "type": "audio", "source": source, "z_index": z, "volume": 1.0}

def _word_appear(start, color_from="#ffffff"):
    return {"type": "text-appear", "split": "word",
            "easing": "cubic-bezier(0.22, 1, 0.36, 1)",
            "duration": 0.08, "start": start,
            "color_from": color_from, "color_to": "#ffffff"}

def _fade_in(start, dur=0.25):
    return {"type": "fade-in", "start": start, "duration": dur}

def _fade_out(start, dur=0.25):
    return {"type": "fade-out", "start": start, "duration": dur}

def _scale_in(start, dur=0.35):
    return {"type": "scale", "value_from": 0, "value_to": 1,
            "start": start, "duration": dur,
            "easing": "cubic-bezier(0.34, 1.56, 0.64, 1)"}

def _scale_impact(start):
    return {"type": "scale", "value_from": 2.5, "value_to": 1,
            "start": start, "duration": 0.4,
            "easing": "cubic-bezier(0.22, 1, 0.36, 1)"}

def _slide_in_bottom(start, dur=0.35):
    return {"type": "slide-in", "direction": "bottom",
            "start": start, "duration": dur,
            "easing": "cubic-bezier(0.34, 1.56, 0.64, 1)"}

def _width_reveal(start, dur=0.4):
    return {"type": "width", "value_from": "0%", "value_to": "84%",
            "start": start, "duration": dur,
            "easing": "cubic-bezier(0.22, 1, 0.36, 1)"}


# ─────────────────────────────────────────────────────────────────────────────
# 4. CONTENT CALENDAR
# ─────────────────────────────────────────────────────────────────────────────

CONTENT_ANGLES = {
    "PantryMate": [
        ("You have $60 of food in your fridge and you just ordered DoorDash",  "stat-bomb"),
        ("The average family wastes $1,500/year on food they already bought",   "stat-bomb"),
        ("I built an app that tells you what to cook in 30 seconds",            "bold-text-hook"),
        ("Day in the life using PantryMate for a week",                         "bold-text-hook"),
        ("Why meal planning apps fail (and what we did differently)",            "split-problem-solution"),
    ],
    "SmartBook AI": [
        ("Your dental practice loses $500 every night after 6pm",               "stat-bomb"),
        ("I built an AI that answers phones for dentists 24/7",                 "bold-text-hook"),
        ("What happens when you miss a patient call at 7pm",                    "split-problem-solution"),
        ("Cold calling dentists with an AI — here's what happened",             "bold-text-hook"),
        ("Behind the scenes: building a $497/mo AI product",                    "bold-text-hook"),
    ],
    "UnitFix": [
        ("Being a landlord is a second job nobody warned you about",            "stat-bomb"),
        ("How I manage 5 properties without losing my mind",                    "bold-text-hook"),
        ("The maintenance request that cost me $3,000 (and how to prevent it)", "split-problem-solution"),
        ("Landlord hack: automated maintenance tracking for $29/mo",            "bold-text-hook"),
    ],
}

def generate_content_calendar(
    week_plan: list[tuple[str, int]] | None = None
) -> list[dict]:
    """
    week_plan: list of (product, angle_index) for 7 days.
    If None, uses the default 7-post mix: PM×3, SB×2, UF×2.
    Returns list of dicts with day, product, angle, template.
    """
    if week_plan is None:
        week_plan = [
            ("PantryMate",    0),
            ("SmartBook AI",  0),
            ("UnitFix",       0),
            ("PantryMate",    1),
            ("SmartBook AI",  2),
            ("UnitFix",       2),
            ("PantryMate",    2),
        ]

    calendar = []
    for day_idx, (product, angle_idx) in enumerate(week_plan):
        angles = CONTENT_ANGLES[product]
        angle, template = angles[angle_idx % len(angles)]
        calendar.append({
            "day":       day_idx + 1,
            "date_offset": f"+{day_idx}d",
            "product":   product,
            "angle":     angle,
            "template":  template,
            "voice":     VOICES["wolfgang"],
        })
    return calendar


if __name__ == "__main__":
    # Quick test
    print("Content Engine — generator.py loaded ✅")
    print(f"Gemini key: {'✅' if GEMINI_KEY else '❌ missing'}")
    print(f"ElevenLabs: {'✅' if ELEVEN_KEY else '❌ missing'}")
    print(f"Creatomate: {'✅' if (CREATOMATE_KEY and CREATOMATE_KEY != 'your_creatomate_key_here') else '⚠️  not configured yet'}")
    cal = generate_content_calendar()
    print(f"\n7-day calendar preview:")
    for entry in cal:
        print(f"  Day {entry['day']}: [{entry['product']}] {entry['angle'][:50]}...")
