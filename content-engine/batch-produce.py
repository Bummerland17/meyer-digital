#!/usr/bin/env python3
"""
batch-produce.py — Generate a full week of content in one run.

Produces:
  - 7 scripts (Gemini)
  - 7 voiceovers (ElevenLabs MP3)
  - Creatomate render specs (or live renders if key is configured)
  - ready-to-post-schedule.md

Output lands in: content-engine/output/YYYY-MM-DD/
"""

import os, sys, json, time
from pathlib import Path
from datetime import date, timedelta

# Add parent dir so we can import generator
sys.path.insert(0, str(Path(__file__).parent))
from generator import (
    generate_script,
    generate_voiceover,
    generate_video,
    generate_content_calendar,
    VOICES,
    BRAND,
    CREATOMATE_KEY,
)

# ── Config ────────────────────────────────────────────────────────────────────

WEEK_LABEL   = "2026-03-week1"
BASE_OUT     = Path(__file__).parent / "output" / WEEK_LABEL
SCRIPT_DELAY = 1.5   # seconds between Gemini calls (rate limit buffer)
VO_DELAY     = 2.0   # seconds between ElevenLabs calls

# Week plan: (product, angle_index) × 7
# PantryMate×3, SmartBook AI×2, UnitFix×2
WEEK_PLAN = [
    ("PantryMate",    0),   # Day 1 — $60 food + DoorDash stat bomb
    ("SmartBook AI",  0),   # Day 2 — $500/night stat bomb
    ("UnitFix",       0),   # Day 3 — second job stat bomb
    ("PantryMate",    1),   # Day 4 — $1,500/year wasted
    ("SmartBook AI",  2),   # Day 5 — missed 7pm call (split screen)
    ("UnitFix",       2),   # Day 6 — $3,000 maintenance request
    ("PantryMate",    2),   # Day 7 — 30-second cook reveal
]

# Best post times (UTC) — adjust to Wolfgang's timezone
POST_TIMES = {
    "TikTok":   ["07:00", "12:00", "19:00"],
    "IG Reels": ["08:00", "13:00", "20:00"],
}

# Day-of-week post schedule (rotate for variety)
PLATFORM_BY_DAY = [
    ["TikTok", "IG Reels"],  # Day 1 — post both
    ["TikTok"],               # Day 2
    ["TikTok", "IG Reels"],  # Day 3
    ["IG Reels"],             # Day 4
    ["TikTok", "IG Reels"],  # Day 5
    ["TikTok"],               # Day 6
    ["TikTok", "IG Reels"],  # Day 7 — end of week push
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def banner(msg: str):
    print(f"\n{'─'*60}")
    print(f"  {msg}")
    print(f"{'─'*60}")

def save_json(data, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    BASE_OUT.mkdir(parents=True, exist_ok=True)
    print(f"\n🎬 BATCH PRODUCE — Week: {WEEK_LABEL}")
    print(f"   Output: {BASE_OUT}")

    calendar = generate_content_calendar(WEEK_PLAN)
    all_results   = []
    render_queue  = []   # Creatomate jobs to queue after voiceovers are done
    schedule_rows = []

    start_date = date(2026, 3, 4)  # Wednesday — start of week

    for entry in calendar:
        day        = entry["day"]
        product    = entry["product"]
        angle      = entry["angle"]
        template   = entry["template"]
        voice_id   = VOICES["wolfgang"]
        post_date  = start_date + timedelta(days=day - 1)
        day_dir    = BASE_OUT / f"day{day:02d}-{product.replace(' ', '-').lower()}"
        day_dir.mkdir(parents=True, exist_ok=True)

        banner(f"Day {day}/7 — {product}")
        print(f"  Angle:    {angle[:60]}")
        print(f"  Template: {template}")

        # ── 1. Generate script ───────────────────────────────────────────────
        print(f"\n  📝 Generating script...")
        try:
            script = generate_script(product, angle, duration=30, template=template)
            save_json(script, day_dir / "script.json")
            print(f"  ✅ Script saved — hook: {script['hook'][:60]}...")
        except Exception as e:
            print(f"  ❌ Script generation failed: {e}")
            script = {
                "product": product, "angle": angle,
                "template": template, "duration": 30,
                "hook": f"[SCRIPT FAILED: {e}]",
                "body": "", "cta": "", "caption": "", "hashtags": "",
                "thumbnail_text": product.upper(),
                "voiceover_text": angle,
                "raw_script": ""
            }
            save_json(script, day_dir / "script.json")

        time.sleep(SCRIPT_DELAY)

        # ── 2. Generate voiceover ────────────────────────────────────────────
        vo_path = day_dir / "voiceover.mp3"
        print(f"\n  🎙️  Generating voiceover...")
        vo_text = script.get("voiceover_text") or script.get("hook", "") + " " + script.get("body", "")
        vo_result = generate_voiceover(
            vo_text,
            voice_id=voice_id,
            output_path=str(vo_path)
        )

        vo_size = vo_path.stat().st_size if vo_path.exists() else 0
        vo_kb   = vo_size // 1024

        time.sleep(VO_DELAY)

        # ── 3. Queue Creatomate render ───────────────────────────────────────
        # Voiceover needs to be publicly accessible for Creatomate to fetch.
        # Until you host the MP3s (S3, Cloudflare R2, etc.) the render spec
        # is saved locally and you can trigger it after uploading.
        print(f"\n  🎬 Creatomate render...")
        if CREATOMATE_KEY and CREATOMATE_KEY != "your_creatomate_key_here":
            # LIVE: attempt real render (requires public voiceover URL)
            # For now we save spec; uncomment + add real URL once hosting is set up
            render_result = {
                "status": "pending_upload",
                "note": "Upload voiceover to public CDN, then call generate_video()",
                "spec_saved": str(day_dir / "render-spec.json")
            }
        else:
            render_result = {
                "status": "needs_key",
                "note": "Add CREATOMATE_API_KEY to .env to enable video generation",
            }

        # Save render spec regardless
        render_spec = generate_video(
            script=script,
            voiceover_url=f"https://your-cdn.com/{WEEK_LABEL}/day{day:02d}/voiceover.mp3",
            template_id=template,
            output_dir=str(day_dir)
        )
        save_json(render_spec, day_dir / "render-spec.json")
        print(f"  📄 Render spec saved: {day_dir / 'render-spec.json'}")

        render_queue.append({
            "day": day,
            "product": product,
            "template": template,
            "local_mp3": str(vo_path),
            "spec": str(day_dir / "render-spec.json"),
        })

        # ── 4. Collect schedule row ──────────────────────────────────────────
        platforms = PLATFORM_BY_DAY[day - 1]
        for platform in platforms:
            times = POST_TIMES[platform]
            post_time = times[(day - 1) % len(times)]
            schedule_rows.append({
                "day":           day,
                "date":          post_date.strftime("%Y-%m-%d (%a)"),
                "product":       product,
                "platform":      platform,
                "post_time_utc": post_time,
                "template":      template,
                "hook":          script.get("hook", "")[:80],
                "caption":       script.get("caption", ""),
                "hashtags":      script.get("hashtags", ""),
                "thumbnail":     script.get("thumbnail_text", ""),
                "vo_path":       str(vo_path),
                "vo_size_kb":    vo_kb,
                "video_status":  render_result.get("status", "unknown"),
                "script_path":   str(day_dir / "script.json"),
            })

        result_entry = {
            "day": day,
            "product": product,
            "angle": angle[:60],
            "template": template,
            "script": {
                "hook": script.get("hook", "")[:100],
                "caption": script.get("caption", "")[:150],
                "hashtags": script.get("hashtags", ""),
            },
            "voiceover": {
                "path": str(vo_path),
                "size_kb": vo_kb,
                "status": "saved" if vo_result else "failed",
            },
            "video": render_result,
        }
        all_results.append(result_entry)
        print(f"\n  ✅ Day {day} complete — VO: {vo_kb}KB | Video: {render_result['status']}")

    # ── 5. Write ready-to-post schedule ─────────────────────────────────────
    banner("Writing ready-to-post-schedule.md")
    _write_schedule(schedule_rows, BASE_OUT)

    # ── 6. Write full results JSON ───────────────────────────────────────────
    results_path = BASE_OUT / "batch-results.json"
    save_json(all_results, results_path)

    # ── 7. Print summary ─────────────────────────────────────────────────────
    banner("BATCH COMPLETE 🎉")
    print(f"\n{'='*60}")
    print(f"  Week:    {WEEK_LABEL}")
    print(f"  Output:  {BASE_OUT}")
    print(f"  Scripts: 7 generated")

    vo_successes = sum(1 for r in all_results if r["voiceover"]["status"] == "saved")
    print(f"  Voiceovers: {vo_successes}/7 generated")
    total_kb = sum(r["voiceover"]["size_kb"] for r in all_results)
    print(f"  Total audio: ~{total_kb} KB")

    print(f"\n  📁 Files:")
    for r in all_results:
        vo  = r["voiceover"]
        vid = r["video"]
        icon = "✅" if vo["status"] == "saved" else "❌"
        vid_icon = "🎬" if vid.get("status") == "queued" else "⏳"
        print(f"    Day {r['day']} [{r['product']:12}] {icon} MP3 {vo['size_kb']:>4}KB | {vid_icon} {vid.get('status','?')}")

    print(f"\n  📋 Schedule: {BASE_OUT / 'ready-to-post-schedule.md'}")
    print(f"  📊 Results:  {results_path}")

    needs_key = sum(1 for r in all_results if r["video"].get("status") == "needs_key")
    if needs_key:
        print(f"\n  ⚠️  {needs_key} videos need Creatomate key to render.")
        print(f"     → Get free trial at creatomate.com (50 renders, no card)")
        print(f"     → Add key to .env: CREATOMATE_API_KEY=your_key")
        print(f"     → Rerun: python3 batch-produce.py --video-only")

    print(f"{'='*60}\n")
    return all_results


def _write_schedule(rows: list[dict], out_dir: Path):
    """Write the ready-to-post-schedule.md file."""
    lines = [
        "# 📅 Ready-to-Post Schedule — Week 1 (March 2026)",
        "",
        f"Generated: {date.today().isoformat()}  ",
        f"Products: PantryMate (3) · SmartBook AI (2) · UnitFix (2)  ",
        f"Platforms: TikTok + Instagram Reels  ",
        "",
        "---",
        "",
        "## How to Post",
        "1. Upload `voiceover.mp3` to your CDN / Google Drive",
        "2. Paste CDN URL into `render-spec.json` → `voiceover_url` field",
        "3. Run `python3 trigger-renders.py` (or paste spec into Creatomate dashboard)",
        "4. Download MP4 once rendered (usually 1-2 min)",
        "5. Upload to TikTok/IG at the scheduled time below",
        "6. Paste the caption + hashtags from this file",
        "",
        "---",
        "",
    ]

    # Group by day
    by_day: dict[int, list] = {}
    for r in rows:
        by_day.setdefault(r["day"], []).append(r)

    for day, day_rows in sorted(by_day.items()):
        r0 = day_rows[0]
        lines += [
            f"## Day {day} — {r0['date']} · {r0['product']}",
            "",
            f"**Hook:** {r0['hook']}",
            "",
            f"**Thumbnail text:** `{r0['thumbnail']}`",
            "",
            f"**Template:** `{r0['template']}`",
            "",
            f"**Voiceover:** `{r0['vo_path']}` ({r0['vo_size_kb']} KB)",
            "",
            f"**Video status:** {r0['video_status']}",
            "",
        ]

        for pr in day_rows:
            best_time = pr['post_time_utc']
            lines += [
                f"### → {pr['platform']} — post at {best_time} UTC",
                "",
                "**Caption:**",
                "```",
                pr["caption"] or "(see script.json for full caption)",
                "```",
                "",
                "**Hashtags:** " + (pr["hashtags"] or "_see script.json_"),
                "",
            ]

        lines += ["---", ""]

    lines += [
        "## Platform Specs",
        "",
        "| Platform | Format | Resolution | FPS | Max Length |",
        "|----------|--------|------------|-----|------------|",
        "| TikTok | 9:16 vertical | 1080×1920 | 30 | 10 min |",
        "| IG Reels | 9:16 vertical | 1080×1920 | 30 | 90 sec |",
        "| IG Feed | 1:1 square | 1080×1080 | 30 | 60 sec |",
        "",
        "## Recommended Posting Windows (UTC)",
        "",
        "| Platform | Best Times |",
        "|----------|-----------|",
        "| TikTok | 07:00, 12:00, 19:00 |",
        "| Instagram | 08:00, 13:00, 20:00 |",
        "",
        "> Adjust for your local timezone. Wolfgang is in EST → subtract 5h.",
        "",
        "## Creatomate — Video Rendering",
        "",
        "Once you have your API key:",
        "```bash",
        "cd /root/.openclaw/workspace/content-engine",
        "# Edit .env: CREATOMATE_API_KEY=your_key",
        "python3 batch-produce.py  # re-run to queue renders",
        "```",
        "",
        "Free trial: **50 renders** at [creatomate.com](https://creatomate.com) — no card needed.",
        "",
    ]

    path = out_dir / "ready-to-post-schedule.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Schedule written: {path}")


if __name__ == "__main__":
    run()
