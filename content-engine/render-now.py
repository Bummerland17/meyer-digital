#!/usr/bin/env python3
"""
render-now.py — Submit 3 Creatomate renders and download MP4s.
Run: python3 render-now.py
"""

import os, sys, json, time, base64, requests
from pathlib import Path

CREATOMATE_KEY = "14e727214e174891a6f26bf4b7a6b16b090c8193553de7e9395326d052f07e011e75f981676b823cd5bc11ea195544f1"
API_BASE       = "https://api.creatomate.com/v1"
OUT_BASE       = Path(__file__).parent / "output" / "2026-03-week1"

HEADERS = {
    "Authorization": f"Bearer {CREATOMATE_KEY}",
    "Content-Type":  "application/json",
}

# Public CDN URLs for voiceovers (uploaded to catbox.moe)
VOICEOVER_URLS = {
    "pantrymate":   "https://files.catbox.moe/svqptm.mp3",
    "smartbook-ai": "https://files.catbox.moe/ocpl2b.mp3",
    "unitfix":      "https://files.catbox.moe/xliayq.mp3",
}

def load_audio_b64(mp3_path: str) -> str:
    """Load MP3 file and return as base64 data URI. (fallback — not used when CDN URLs available)"""
    data = Path(mp3_path).read_bytes()
    b64  = base64.b64encode(data).decode("ascii")
    return f"data:audio/mpeg;base64,{b64}"

def build_pantrymate(audio_b64: str) -> dict:
    return {
        "output_format": "mp4",
        "width": 1080,
        "height": 1920,
        "duration": 30,
        "frame_rate": 30,
        "elements": [
            # ── Background ──────────────────────────────────────────────────
            {
                "type": "shape", "shape": "rect",
                "fill_color": "#1a3a2a",
                "x": "50%", "y": "50%",
                "width": "100%", "height": "100%"
            },
            # ── Top accent bar ───────────────────────────────────────────────
            {
                "type": "shape", "shape": "rect",
                "fill_color": "#4ade80",
                "x": "50%", "y": "0.4%",
                "width": "100%", "height": "0.8%"
            },
            # ── Bottom accent bar ────────────────────────────────────────────
            {
                "type": "shape", "shape": "rect",
                "fill_color": "#4ade80",
                "x": "50%", "y": "99.6%",
                "width": "100%", "height": "0.8%"
            },
            # ── Brand label (top) ────────────────────────────────────────────
            {
                "type": "text", "text": "PANTRYMATE",
                "font_family": "Montserrat", "font_weight": "900",
                "font_size": "3.5 vmin",
                "fill_color": "#4ade80",
                "x": "50%", "y": "6%",
                "width": "85%", "text_align": "center",
                "time": 0, "duration": 30,
                
            },
            # ── HOOK — slams in chars one by one ─────────────────────────────
            {
                "type": "text",
                "text": "You have $60 of food\nin your fridge.",
                "font_family": "Montserrat", "font_weight": "800",
                "font_size": "8 vmin",
                "fill_color": "#ffffff",
                "x": "50%", "y": "35%",
                "width": "85%",
                "text_wrap": True, "text_align": "center",
                "line_height": "120%",
                "time": 0, "duration": 8,
                "animations": [
                    {"type": "scale", "easing": "back-out",
                     "fade": True, "scope": "split-chars"}
                ]
            },
            # ── Divider line ─────────────────────────────────────────────────
            {
                "type": "shape", "shape": "rect",
                "fill_color": "#4ade80",
                "x": "50%", "y": "52%",
                "width": "60%", "height": "0.3%",
                "time": 4, "duration": 26,
                "animations": [
                    {"type": "wipe", "direction": "right",
                     "easing": "quadratic-in-out", "duration": "0.4 s"}
                ]
            },
            # ── BODY ─────────────────────────────────────────────────────────
            {
                "type": "text",
                "text": "You just opened DoorDash anyway.\n\nThe average family wastes $1,500/year on food they already own.",
                "font_family": "Montserrat", "font_weight": "500",
                "font_size": "4.8 vmin",
                "fill_color": "#e8f5e9",
                "x": "50%", "y": "62%",
                "width": "85%",
                "text_wrap": True, "text_align": "center",
                "line_height": "140%",
                "time": 5, "duration": 18,
                "animations": [
                    {"type": "fade", "easing": "linear",
                     "fade": True, "duration": "0.6 s"}
                ]
            },
            # ── Stat callout ─────────────────────────────────────────────────
            {
                "type": "text", "text": "$1,500",
                "font_family": "Montserrat", "font_weight": "900",
                "font_size": "14 vmin",
                "fill_color": "#4ade80",
                "x": "50%", "y": "40%",
                "width": "90%", "text_align": "center",
                "time": 8, "duration": 10,
                "animations": [
                    {"type": "scale", "easing": "elastic-out",
                     "fade": True, "scope": "element",
                     "x_anchor": "50%", "y_anchor": "50%"}
                ]
            },
            {
                "type": "text", "text": "WASTED EVERY YEAR",
                "font_family": "Montserrat", "font_weight": "700",
                "font_size": "4 vmin",
                "fill_color": "#ffffff",
                
                "x": "50%", "y": "55%",
                "width": "85%", "text_align": "center",
                "time": 9, "duration": 9,
                "animations": [
                    {"type": "fade", "fade": True, "duration": "0.4 s"}
                ]
            },
            # ── CTA ──────────────────────────────────────────────────────────
            {
                "type": "shape", "shape": "rect",
                "fill_color": "#4ade80",
                "x": "50%", "y": "83%",
                "width": "80%", "height": "10%",
                "border_radius": "100",
                "time": 24, "duration": 6,
                "animations": [
                    {"type": "scale", "easing": "back-out",
                     "fade": True, "duration": "0.5 s",
                     "scope": "element",
                     "x_anchor": "50%", "y_anchor": "50%"}
                ]
            },
            {
                "type": "text", "text": "PantryMate fixes this. Free download.",
                "font_family": "Montserrat", "font_weight": "800",
                "font_size": "4.2 vmin",
                "fill_color": "#0a1f14",
                "x": "50%", "y": "83%",
                "width": "75%", "text_wrap": True,
                "text_align": "center",
                "line_height": "120%",
                "time": 24.3, "duration": 5.7,
                "animations": [
                    {"type": "fade", "fade": True, "duration": "0.3 s"}
                ]
            },
            {
                "type": "text", "text": "pantrymate.net",
                "font_family": "Montserrat", "font_weight": "500",
                "font_size": "3 vmin",
                "fill_color": "#4ade80",
                "x": "50%", "y": "93%",
                "width": "85%", "text_align": "center",
                "time": 25, "duration": 5
            },
            # ── Voiceover ─────────────────────────────────────────────────────
            {
                "type": "audio",
                "source": audio_b64,
                "time": 0, "duration": 30,
                "volume": "100%"
            },
        ]
    }


def build_smartbook(audio_b64: str) -> dict:
    return {
        "output_format": "mp4",
        "width": 1080,
        "height": 1920,
        "duration": 30,
        "frame_rate": 30,
        "elements": [
            # ── Background ───────────────────────────────────────────────────
            {
                "type": "shape", "shape": "rect",
                "fill_color": "#0d1521",
                "x": "50%", "y": "50%",
                "width": "100%", "height": "100%"
            },
            # ── Accent bars ──────────────────────────────────────────────────
            {
                "type": "shape", "shape": "rect",
                "fill_color": "#3b82f6",
                "x": "50%", "y": "0.4%",
                "width": "100%", "height": "0.8%"
            },
            {
                "type": "shape", "shape": "rect",
                "fill_color": "#3b82f6",
                "x": "50%", "y": "99.6%",
                "width": "100%", "height": "0.8%"
            },
            # ── Brand label ──────────────────────────────────────────────────
            {
                "type": "text", "text": "SMARTBOOK AI",
                "font_family": "Montserrat", "font_weight": "900",
                "font_size": "3.5 vmin",
                "fill_color": "#3b82f6",
                "x": "50%", "y": "6%",
                "width": "85%", "text_align": "center",
                "time": 0, "duration": 30,
                
            },
            # ── HOOK ─────────────────────────────────────────────────────────
            {
                "type": "text",
                "text": "Your dental practice\nloses $500 every night\nafter 6pm.",
                "font_family": "Montserrat", "font_weight": "800",
                "font_size": "7.5 vmin",
                "fill_color": "#ffffff",
                "x": "50%", "y": "32%",
                "width": "85%",
                "text_wrap": True, "text_align": "center",
                "line_height": "120%",
                "time": 0, "duration": 8,
                "animations": [
                    {"type": "scale", "easing": "back-out",
                     "fade": True, "scope": "split-chars"}
                ]
            },
            # ── Stat callout ─────────────────────────────────────────────────
            {
                "type": "text", "text": "$500",
                "font_family": "Montserrat", "font_weight": "900",
                "font_size": "20 vmin",
                "fill_color": "#3b82f6",
                "x": "50%", "y": "38%",
                "width": "90%", "text_align": "center",
                "time": 8, "duration": 9,
                "animations": [
                    {"type": "scale", "easing": "elastic-out",
                     "fade": True, "scope": "element",
                     "x_anchor": "50%", "y_anchor": "50%"}
                ]
            },
            {
                "type": "text", "text": "LOST EVERY SINGLE NIGHT",
                "font_family": "Montserrat", "font_weight": "700",
                "font_size": "3.8 vmin",
                "fill_color": "#ffffff",
                
                "x": "50%", "y": "55%",
                "width": "85%", "text_align": "center",
                "time": 9, "duration": 8,
                "animations": [{"type": "fade", "fade": True, "duration": "0.4 s"}]
            },
            # ── Divider ───────────────────────────────────────────────────────
            {
                "type": "shape", "shape": "rect",
                "fill_color": "#3b82f6",
                "x": "50%", "y": "54%",
                "width": "55%", "height": "0.3%",
                "time": 6, "duration": 24,
                "animations": [
                    {"type": "wipe", "direction": "right",
                     "easing": "quadratic-in-out", "duration": "0.4 s"}
                ]
            },
            # ── BODY ─────────────────────────────────────────────────────────
            {
                "type": "text",
                "text": "Every missed call after hours\nis a patient who booked somewhere else.\n\nSmartBook AI answers 24/7.",
                "font_family": "Montserrat", "font_weight": "500",
                "font_size": "4.5 vmin",
                "fill_color": "#bfdbfe",
                "x": "50%", "y": "63%",
                "width": "85%",
                "text_wrap": True, "text_align": "center",
                "line_height": "140%",
                "time": 17, "duration": 8,
                "animations": [{"type": "fade", "fade": True, "duration": "0.6 s"}]
            },
            # ── CTA box ──────────────────────────────────────────────────────
            {
                "type": "shape", "shape": "rect",
                "fill_color": "#3b82f6",
                "x": "50%", "y": "83%",
                "width": "80%", "height": "10%",
                "border_radius": "100",
                "time": 24, "duration": 6,
                "animations": [
                    {"type": "scale", "easing": "back-out",
                     "fade": True, "duration": "0.5 s",
                     "scope": "element",
                     "x_anchor": "50%", "y_anchor": "50%"}
                ]
            },
            {
                "type": "text", "text": "SmartBook AI — from $497/mo",
                "font_family": "Montserrat", "font_weight": "800",
                "font_size": "4.5 vmin",
                "fill_color": "#ffffff",
                "x": "50%", "y": "83%",
                "width": "75%", "text_wrap": True,
                "text_align": "center",
                "line_height": "120%",
                "time": 24.3, "duration": 5.7,
                "animations": [{"type": "fade", "fade": True, "duration": "0.3 s"}]
            },
            {
                "type": "text", "text": "smartbookai.com",
                "font_family": "Montserrat", "font_weight": "500",
                "font_size": "3 vmin",
                "fill_color": "#3b82f6",
                "x": "50%", "y": "93%",
                "width": "85%", "text_align": "center",
                "time": 25, "duration": 5
            },
            # ── Voiceover ────────────────────────────────────────────────────
            {
                "type": "audio",
                "source": audio_b64,
                "time": 0, "duration": 30,
                "volume": "100%"
            },
        ]
    }


def build_unitfix(audio_b64: str) -> dict:
    return {
        "output_format": "mp4",
        "width": 1080,
        "height": 1920,
        "duration": 30,
        "frame_rate": 30,
        "elements": [
            # ── Background ───────────────────────────────────────────────────
            {
                "type": "shape", "shape": "rect",
                "fill_color": "#1a1a2e",
                "x": "50%", "y": "50%",
                "width": "100%", "height": "100%"
            },
            # ── Accent bars ──────────────────────────────────────────────────
            {
                "type": "shape", "shape": "rect",
                "fill_color": "#f59e0b",
                "x": "50%", "y": "0.4%",
                "width": "100%", "height": "0.8%"
            },
            {
                "type": "shape", "shape": "rect",
                "fill_color": "#f59e0b",
                "x": "50%", "y": "99.6%",
                "width": "100%", "height": "0.8%"
            },
            # ── Brand label ──────────────────────────────────────────────────
            {
                "type": "text", "text": "UNITFIX",
                "font_family": "Montserrat", "font_weight": "900",
                "font_size": "3.5 vmin",
                "fill_color": "#f59e0b",
                "x": "50%", "y": "6%",
                "width": "85%", "text_align": "center",
                "time": 0, "duration": 30,
                
            },
            # ── HOOK ─────────────────────────────────────────────────────────
            {
                "type": "text",
                "text": "Being a landlord is a second job nobody warned you about.",
                "font_family": "Montserrat", "font_weight": "800",
                "font_size": "7.5 vmin",
                "fill_color": "#ffffff",
                "x": "50%", "y": "30%",
                "width": "85%",
                "text_wrap": True, "text_align": "center",
                "line_height": "125%",
                "time": 0, "duration": 9,
                "animations": [
                    {"type": "scale", "easing": "back-out",
                     "fade": True, "scope": "split-chars"}
                ]
            },
            # ── Pain points list ─────────────────────────────────────────────
            {
                "type": "text",
                "text": "📋 Maintenance requests\n🔧 Tracking repairs\n📞 Chasing contractors\n🔁 All over again.",
                "font_family": "Montserrat", "font_weight": "600",
                "font_size": "5 vmin",
                "fill_color": "#fde68a",
                "x": "50%", "y": "45%",
                "width": "82%",
                "text_wrap": True, "text_align": "left",
                "line_height": "160%",
                "time": 9, "duration": 10,
                "animations": [
                    {"type": "slide", "direction": "up",
                     "easing": "quadratic-out",
                     "fade": True, "scope": "split-lines",
                     "duration": "0.35 s"}
                ]
            },
            # ── Divider ───────────────────────────────────────────────────────
            {
                "type": "shape", "shape": "rect",
                "fill_color": "#f59e0b",
                "x": "50%", "y": "67%",
                "width": "55%", "height": "0.3%",
                "time": 18, "duration": 12,
                "animations": [
                    {"type": "wipe", "direction": "right",
                     "easing": "quadratic-in-out", "duration": "0.4 s"}
                ]
            },
            # ── BODY ─────────────────────────────────────────────────────────
            {
                "type": "text",
                "text": "UnitFix automates all of it.\nTenants self-serve. You get alerts.",
                "font_family": "Montserrat", "font_weight": "500",
                "font_size": "4.8 vmin",
                "fill_color": "#e5e7eb",
                "x": "50%", "y": "72%",
                "width": "85%",
                "text_wrap": True, "text_align": "center",
                "line_height": "140%",
                "time": 19, "duration": 8,
                "animations": [{"type": "fade", "fade": True, "duration": "0.5 s"}]
            },
            # ── CTA box ──────────────────────────────────────────────────────
            {
                "type": "shape", "shape": "rect",
                "fill_color": "#f59e0b",
                "x": "50%", "y": "85%",
                "width": "78%", "height": "9%",
                "border_radius": "100",
                "time": 24.5, "duration": 5.5,
                "animations": [
                    {"type": "scale", "easing": "back-out",
                     "fade": True, "duration": "0.5 s",
                     "scope": "element",
                     "x_anchor": "50%", "y_anchor": "50%"}
                ]
            },
            {
                "type": "text", "text": "UnitFix — $29/mo. Try free.",
                "font_family": "Montserrat", "font_weight": "800",
                "font_size": "4.8 vmin",
                "fill_color": "#1a1a2e",
                "x": "50%", "y": "85%",
                "width": "72%", "text_wrap": True,
                "text_align": "center",
                "time": 24.8, "duration": 5.2,
                "animations": [{"type": "fade", "fade": True, "duration": "0.3 s"}]
            },
            {
                "type": "text", "text": "unitfix.com",
                "font_family": "Montserrat", "font_weight": "500",
                "font_size": "3 vmin",
                "fill_color": "#f59e0b",
                "x": "50%", "y": "94%",
                "width": "85%", "text_align": "center",
                "time": 25.2, "duration": 4.8
            },
            # ── Voiceover ────────────────────────────────────────────────────
            {
                "type": "audio",
                "source": audio_b64,
                "time": 0, "duration": 30,
                "volume": "100%"
            },
        ]
    }


# ── Submit + poll + download ─────────────────────────────────────────────────

def submit_render(composition: dict, label: str) -> str | None:
    """Submit a render, return render_id."""
    print(f"\n🚀 Submitting: {label}...")
    payload = {"source": composition}          # object, not JSON string
    resp = requests.post(f"{API_BASE}/renders", headers=HEADERS, json=payload, timeout=60)
    if resp.status_code in (200, 201, 202):
        data = resp.json()
        # Creatomate returns a list
        render = data[0] if isinstance(data, list) else data
        rid    = render.get("id")
        status = render.get("status")
        print(f"   ✅ Queued — id: {rid}  status: {status}")
        return rid
    else:
        print(f"   ❌ Error {resp.status_code}: {resp.text[:400]}")
        return None

def poll_until_done(render_id: str, label: str, timeout: int = 300) -> dict | None:
    """Poll every 5s until status is succeeded or failed."""
    print(f"\n⏳ Polling {label} ({render_id})...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = requests.get(f"{API_BASE}/renders/{render_id}", headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            data   = resp.json()
            status = data.get("status")
            pct    = data.get("progress", 0)
            print(f"   {label}: {status} {int(pct*100) if pct else '?'}%")
            if status == "succeeded":
                return data
            if status == "failed":
                print(f"   ❌ Failed: {data.get('error_message', 'unknown')}")
                return None
        time.sleep(5)
    print(f"   ⏰ Timeout after {timeout}s")
    return None

def download_mp4(url: str, dest: Path) -> int:
    """Download MP4, return file size in bytes."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(url, stream=True, timeout=120)
    resp.raise_for_status()
    size = 0
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=65536):
            f.write(chunk)
            size += len(chunk)
    return size


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    print("\n🎬 CREATOMATE RENDER RUN — 3 Videos")
    print("=" * 60)

    print(f"   ✅ API key loaded")

    # Use public CDN URLs for voiceovers (Creatomate requires HTTPS URLs, not base64)
    print("\n🎙️  Using public CDN voiceover URLs...")
    vo_pm  = VOICEOVER_URLS["pantrymate"]
    vo_sb  = VOICEOVER_URLS["smartbook-ai"]
    vo_uf  = VOICEOVER_URLS["unitfix"]
    print(f"   PantryMate   VO: {vo_pm}")
    print(f"   SmartBook AI VO: {vo_sb}")
    print(f"   UnitFix      VO: {vo_uf}")

    # Build compositions
    jobs = [
        ("PantryMate",    build_pantrymate(vo_pm), OUT_BASE / "day01-pantrymate"   / "video.mp4"),
        ("SmartBook AI",  build_smartbook(vo_sb),  OUT_BASE / "day02-smartbook-ai" / "video.mp4"),
        ("UnitFix",       build_unitfix(vo_uf),    OUT_BASE / "day03-unitfix"       / "video.mp4"),
    ]

    # Submit all 3 simultaneously
    render_ids = {}
    for label, comp, dest in jobs:
        rid = submit_render(comp, label)
        if rid:
            render_ids[label] = (rid, dest)

    if not render_ids:
        print("\n❌ No renders submitted. Check API key and payload.")
        sys.exit(1)

    # Poll all until done
    results = {}
    pending = dict(render_ids)
    print(f"\n⏳ Polling {len(pending)} renders (up to 5 min each)...")

    deadline = time.time() + 360
    while pending and time.time() < deadline:
        for label in list(pending.keys()):
            rid, dest = pending[label]
            resp = requests.get(f"{API_BASE}/renders/{rid}", headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                data   = resp.json()
                status = data.get("status")
                pct    = int((data.get("progress") or 0) * 100)
                print(f"   [{label}] {status} {pct}%")
                if status == "succeeded":
                    results[label] = (data, dest)
                    del pending[label]
                elif status == "failed":
                    print(f"   ❌ {label} failed: {data.get('error_message','?')}")
                    del pending[label]
        if pending:
            time.sleep(8)

    # Download completed videos
    print(f"\n⬇️  Downloading {len(results)} completed video(s)...")
    summary = []
    for label, (data, dest) in results.items():
        url  = data.get("url")
        snap = data.get("snapshot_url", "")
        if not url:
            print(f"   ❌ {label}: no download URL in response")
            continue
        print(f"   Downloading {label}...")
        try:
            size = download_mp4(url, dest)
            size_mb = size / (1024 * 1024)
            print(f"   ✅ {label}: {dest} ({size_mb:.1f} MB)")
            summary.append({
                "product":      label,
                "render_id":    data.get("id"),
                "status":       "downloaded",
                "path":         str(dest),
                "size_mb":      round(size_mb, 2),
                "url":          url,
                "snapshot_url": snap,
            })
        except Exception as e:
            print(f"   ❌ {label} download failed: {e}")
            summary.append({"product": label, "status": "download_failed", "error": str(e)})

    # Save summary
    summary_path = OUT_BASE / "render-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))

    # Final report
    print(f"\n{'='*60}")
    print(f"  RENDER COMPLETE")
    print(f"{'='*60}")
    for s in summary:
        icon = "✅" if s.get("status") == "downloaded" else "❌"
        if s.get("status") == "downloaded":
            print(f"  {icon} [{s['product']}]")
            print(f"       Path:  {s['path']}")
            print(f"       Size:  {s['size_mb']} MB")
            print(f"       URL:   {s.get('url','')[:80]}")
        else:
            print(f"  {icon} [{s['product']}] {s.get('error', s.get('status'))}")
    print(f"\n  Summary JSON: {summary_path}")
    print(f"{'='*60}\n")
    return summary


if __name__ == "__main__":
    main()
