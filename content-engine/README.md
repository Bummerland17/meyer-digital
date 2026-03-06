# 🎬 Content Engine — Wolfgang's Automated Video Pipeline

One-command content factory for **PantryMate**, **SmartBook AI**, and **UnitFix**.
Generates scripts → voiceovers → Creatomate renders → ready-to-post schedule.
Quality bar: viral FoodTok / FinTok / ProductTok. Not a cheap slideshow.

---

## Quick Start

```bash
cd /root/.openclaw/workspace/content-engine

# Generate a full week of content
python3 batch-produce.py
```

That single command:
1. Calls Gemini 2.0 Flash for 7 scripts (one per day)
2. Calls ElevenLabs for 7 voiceover MP3s
3. Builds Creatomate render specs (queues live renders if key is set)
4. Writes `output/2026-03-week1/ready-to-post-schedule.md`

---

## Stack

| Layer | Tool | Cost |
|-------|------|------|
| Script generation | Gemini 2.0 Flash | ~$0.001/script |
| Voiceover | ElevenLabs Turbo v2.5 | ~$0.003/30s clip |
| Video rendering | Creatomate | Free trial: 50 renders |
| Storage | Local / your CDN | — |

---

## Generate a Single Script

```python
from generator import generate_script

script = generate_script(
    product  = "PantryMate",
    angle    = "You have $60 of food in your fridge and just ordered DoorDash",
    duration = 30,
    template = "stat-bomb"       # or "bold-text-hook" or "split-problem-solution"
)

print(script["hook"])
print(script["caption"])
print(script["hashtags"])
```

**Output dict keys:**
- `hook` — first 3 seconds, scroll-stopping line
- `body` — core content
- `cta` — final action
- `caption` — IG/TikTok caption, ready to paste
- `hashtags` — 5 relevant hashtags
- `thumbnail_text` — 3-5 word overlay text
- `voiceover_text` — clean text for TTS (no stage directions)
- `raw_script` — full Gemini output

---

## Generate a Voiceover

```python
from generator import generate_voiceover, VOICES

path = generate_voiceover(
    script_text = script["voiceover_text"],
    voice_id    = VOICES["wolfgang"],   # warm, authoritative
    output_path = "output/day01/voiceover.mp3"
)
# → "output/day01/voiceover.mp3" (or None if ElevenLabs fails)
```

**Voice options:**
| Key | Voice ID | Style |
|-----|----------|-------|
| `wolfgang` | `CwhRBWXzGAHq8TQ4Fs17` | Warm, authoritative — Wolfgang narration |
| `female` | `EXAVITQu4vr4xnSDxMaL` | Sarah — clean female VO |
| `energetic` | `pNInz6obpgDQGcFmaJgB` | Adam — energetic, Alex's voice |

---

## Generate a Video (Creatomate)

```python
from generator import generate_video

result = generate_video(
    script        = script,
    voiceover_url = "https://your-cdn.com/voiceover.mp3",  # must be public
    template_id   = "bold-text-hook",
    output_dir    = "output/day01/"
)

print(result["render_id"])    # e.g. "abc123"
print(result["status"])       # "queued" | "succeeded" | "needs_key"
print(result["url"])          # MP4 download URL once done
```

**Setup (one-time):**
1. Go to [creatomate.com](https://creatomate.com) → Free trial (50 renders, no card)
2. Copy your API key
3. Add to `.env`: `CREATOMATE_API_KEY=your_key_here`

---

## Video Templates

### `bold-text-hook`
Dark background. Word-by-word white text animation synced to voiceover.
Accent color flash on each word. CTA pill at the end.
**Best for:** PantryMate tutorials, SmartBook demos, founder POV content.

### `split-problem-solution`
Screen splits: **red problem side** (left) → **green fix side** (right) slides in.
"THE PROBLEM ❌" vs "THE FIX ✅" labels. Full-width CTA at bottom.
**Best for:** Any before/after angle. Food waste. Missed calls. Maintenance chaos.

### `stat-bomb`
White flash → giant stat slams in → screen shake → label animates in →
solution reveals → pill CTA bounces in.
**Best for:** `$1,500 wasted`, `$500/night lost`, `47 hrs/month` angles.

---

## Brand Colors

| Product | Background | Accent |
|---------|-----------|--------|
| PantryMate | `#1a3a2a` | `#4ade80` |
| SmartBook AI | `#0d1521` | `#3b82f6` |
| UnitFix | `#1a1a2e` | `#f59e0b` |

---

## Platform Specs

| Platform | Ratio | Resolution | FPS | Max Length |
|----------|-------|------------|-----|------------|
| TikTok | 9:16 | 1080×1920 | 30 | 10 min |
| IG Reels | 9:16 | 1080×1920 | 30 | 90 sec |
| IG Feed | 1:1 | 1080×1080 | 30 | 60 sec |
| YouTube Shorts | 9:16 | 1080×1920 | 30 | 60 sec |

All Creatomate renders output at 1080×1920 / H.264 / AAC — compatible with all platforms.

---

## Posting Schedule (Recommended)

| Platform | Best Times (UTC) | Best Days |
|----------|-----------------|-----------|
| TikTok | 07:00, 12:00, 19:00 | Tue, Thu, Fri |
| Instagram | 08:00, 13:00, 20:00 | Mon, Wed, Sat |

**Wolfgang's tip:** Post the same video to TikTok first, then cross-post to IG Reels 24h later. TikTok's algorithm distributes faster; IG Reels catches anyone who missed it.

---

## Batch Production Workflow

```
Day 0: Generate scripts + voiceovers (batch-produce.py)
       → output/2026-03-week1/day01-pantrymate/script.json
       → output/2026-03-week1/day01-pantrymate/voiceover.mp3
       → output/2026-03-week1/day01-pantrymate/render-spec.json

Day 0: Upload MP3s to CDN (S3 / Cloudflare R2 / Google Drive public link)

Day 0: Update render-spec.json voiceover_url → trigger Creatomate renders

Day 0: Download MP4s → store in day*/video.mp4

Day 1-7: Post daily per ready-to-post-schedule.md
```

---

## Content Angles Library

### PantryMate
- "You have $60 of food in your fridge and you just ordered DoorDash"
- "The average family wastes $1,500/year on food they already bought"
- "I built an app that tells you what to cook in 30 seconds"
- "Day in the life using PantryMate for a week"
- "Why meal planning apps fail (and what we did differently)"

### SmartBook AI
- "Your dental practice loses $500 every night after 6pm"
- "I built an AI that answers phones for dentists 24/7"
- "What happens when you miss a patient call at 7pm"
- "Cold calling dentists with an AI — here's what happened"
- "Behind the scenes: building a $497/mo AI product"

### UnitFix
- "Being a landlord is a second job nobody warned you about"
- "How I manage 5 properties without losing my mind"
- "The maintenance request that cost me $3,000 (and how to prevent it)"
- "Landlord hack: automated maintenance tracking for $29/mo"

---

## File Structure

```
content-engine/
├── generator.py           ← Core functions (scripts, voiceovers, videos)
├── batch-produce.py       ← One-command weekly batch runner
├── README.md              ← This file
├── templates/
│   ├── bold-text-hook.json          ← Template 1 spec
│   ├── split-problem-solution.json  ← Template 2 spec
│   └── stat-bomb.json               ← Template 3 spec
└── output/
    └── 2026-03-week1/
        ├── ready-to-post-schedule.md
        ├── batch-results.json
        ├── day01-pantrymate/
        │   ├── script.json
        │   ├── voiceover.mp3
        │   └── render-spec.json
        ├── day02-smartbook-ai/
        ...
```

---

## Environment Variables (`.env`)

```bash
GEMINI_API_KEY=AIzaSy...         # Script generation
ELEVENLABS_API_KEY=sk_...        # Voiceover
CREATOMATE_API_KEY=your_key      # Video rendering (get free trial)
```

---

## Hosting Voiceovers for Creatomate

Creatomate needs a **public URL** for the MP3. Fastest options:

1. **Cloudflare R2** — free 10GB/mo, instant public URLs
2. **AWS S3** — `aws s3 cp voiceover.mp3 s3://your-bucket/ --acl public-read`
3. **Google Drive** — share as "Anyone with link" → use direct download URL trick
4. **Uploadthing** — dead-simple, free tier, Wolfgang already has hosting

---

*Built for Wolfgang's content empire. Add new products by extending `BRAND` and `CONTENT_ANGLES` in generator.py.*
