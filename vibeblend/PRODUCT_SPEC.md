# VibeBlend — Product Specification

**Version:** 1.0  
**Status:** Pre-development  
**Last Updated:** 2026-03-04

---

## 1. Overview

### What Is VibeBlend?

VibeBlend is a mobile-first web app that creates personalized Spotify playlists blending a user's existing music DNA with sounds from a specific culture or region. It solves a real problem: when you travel to a new country, move cities, or just get curious about another music culture, you don't know where to start — and generic "Afrobeats playlists" don't match your personal taste.

**Core insight:** The best discovery happens when new music *sounds like* music you already love. VibeBlend uses audio features (energy, tempo, danceability, valence, acousticness) to find regional music that matches your exact sonic fingerprint.

### One-Liner

> "Your music taste, anywhere in the world."

---

## 2. Core User Flow (5 Steps)

### Step 1 — Connect Spotify
- User taps "Connect with Spotify"
- Standard OAuth 2.0 PKCE flow
- Scopes: `user-top-read`, `playlist-modify-public`, `playlist-modify-private`, `user-read-private`
- On success: display name + avatar shown, user marked as authenticated in Supabase

### Step 2 — Analyze Your Music DNA
- App fetches top 50 tracks (`GET /me/top/tracks?time_range=medium_term&limit=50`)
- Batch fetches audio features for all 50 tracks (`GET /audio-features?ids=...`)
- Computes averages across 5 dimensions:
  - **Tempo** (BPM average)
  - **Energy** (0–1, how intense/fast)
  - **Danceability** (0–1, how rhythmically regular)
  - **Valence** (0–1, how positive/happy)
  - **Acousticness** (0–1, how acoustic vs electronic)
- Displays a visual "Music DNA Card" — radar chart or 5-bar breakdown
- Examples of user DNA profiles:
  - High energy + high danceability + high valence = party lover
  - Low energy + high acousticness + low tempo = chill acoustic listener
  - High energy + low valence = dark electronic / metal fan

### Step 3 — Pick Your Vibe
- Full-screen region selector grid with beautiful cover art
- Each region shown as a card: flag/illustration, name, and 3-word vibe descriptor
- Regions in v1:
  - 🇳🇬 Afrobeats — "Groovy, rhythmic, infectious"
  - 🌍 West African — "Soulful, percussive, warm"
  - 🌍 East African — "Melodic, spiritual, rich"
  - 🇿🇦 South African — "Bold, euphoric, driving"
  - 🌐 Afropop — "Upbeat, fresh, global"
  - 🇲🇽 Latin — "Passionate, rhythmic, vibrant"
  - 🇰🇷 K-Pop — "Polished, energetic, catchy"
  - 🇯🇲 Dancehall — "Bouncy, raw, Caribbean"
  - 🇧🇷 Brazilian — "Lush, complex, joyful"
  - 🇮🇳 Bollywood — "Cinematic, colorful, dramatic"
- User can also type a custom genre/region (Pro feature in v2)

### Step 4 — Blend Creation (Loading State)
- Animated blend visualization (two waveforms merging)
- Behind the scenes:
  1. Map selected region → genre seeds array
  2. Call `GET /recommendations` with:
     - `seed_genres` = region's genres (up to 5)
     - `target_energy`, `target_danceability`, `target_valence`, `target_acousticness` = user's DNA averages
     - `target_tempo` = user's average BPM
     - `limit=25`
  3. Filter out tracks already in user's top 50 (avoid showing them songs they already know)
  4. Create playlist via `POST /users/{id}/playlists`
  5. Add tracks via `POST /playlists/{id}/tracks`
- Takes approximately 3–6 seconds

### Step 5 — Your Blend is Ready
- Display playlist card with:
  - Custom name: "My [Region] Blend — [Month Year]" (editable)
  - Track list with album art thumbnails
  - Play button (opens Spotify)
  - Share button (native share sheet)
  - "Blend Again" button (goes back to Step 3)
- Blend saved to Supabase `blends` table
- If free tier: show upgrade prompt for unlimited blends

---

## 3. Monetization

### Free Tier
- **1 blend per calendar month**
- Access to all regions
- Playlists saved to Spotify (permanent)
- Blend history: last 3 blends visible

### Pro — $4.99/month (or $39.99/year)
- **Unlimited blends**
- Blend history: all time
- Custom blend names
- Adjustable DNA sliders (override audio feature targets — e.g., "I want more energy than my usual DNA")
- Priority recommendations (higher quality seed matching)
- Export playlist as shareable link with visual card (OG image)
- Early access to new regions

### Revenue Projections (Conservative)
| Month | Free Users | Pro Users (2% conv) | MRR |
|---|---|---|---|
| 3 | 500 | 10 | $50 |
| 6 | 2,000 | 40 | $200 |
| 12 | 8,000 | 160 | $800 |
| 18 | 20,000 | 400 | $2,000 |

Breakeven is low — infrastructure costs (Supabase free tier + Vercel) are ~$0–$50/mo until significant scale.

### Payment
- Stripe (web) + RevenueCat (mobile) for App Store / Play Store subscriptions
- Supabase stores `plan` field per user

---

## 4. Target Markets

### Primary: Digital Nomads
- Profile: Remote workers who move cities/countries every 1–3 months
- Pain: Spotify's algorithm is hyper-local. Moving to Lagos or Medellín doesn't update your recommendations for weeks.
- How VibeBlend helps: Instant local flavor that still sounds like *you*
- Channel: Nomad communities (Nomad List, Remote Year, Twitter/X nomad scene)

### Secondary: Travelers
- Profile: People on 1–4 week trips wanting an authentic musical experience
- Pain: "Show me the music" is as real as "show me the food"
- How VibeBlend helps: Create a "trip playlist" before you land
- Channel: Travel blogs, Instagram travel creators, Reddit (r/solotravel, r/travel)

### Tertiary: Expats & Third-Culture Kids
- Profile: People living away from their home culture, or between cultures
- Pain: Homesickness + wanting to stay connected to their roots *and* fit into their new home
- How VibeBlend helps: Blend their current taste with home sounds OR home taste with new city sounds
- Channel: Expat Facebook groups, WhatsApp communities, subreddits (r/expats)

### Quaternary: Music Explorers
- Profile: Spotify power users who love discovery but find algorithm too safe
- Pain: Spotify's Discover Weekly rarely crosses cultural boundaries
- How VibeBlend helps: Deliberate, intentional cross-cultural discovery
- Channel: Music Twitter/X, r/ifyoulikeblank, music Discord servers

### Cultural Diversity Angle (B2B Future)
- Travel agencies building custom playlist experiences for destinations
- Airlines (curated regional playlists for flights)
- Hotels/Airbnb (local music vibe for stays)

---

## 5. Competitive Landscape

### Direct Competitors

| Product | What It Does | Why VibeBlend Wins |
|---|---|---|
| **Spotify Blend** | Merges two *users'* playlists | Social feature, not cultural discovery. No regional targeting. |
| **Spotify DJ** | AI DJ with commentary | Great for passive listening, zero cultural intent, no customization |
| **Spotify Mixes** | Auto-generated genre mixes | Algorithm-driven, no user control, no regional angle |
| **Apple Music Radio** | Curated editorial + radio | Human-curated, not personalized, no cultural blending |
| **Soundiiz** | Cross-platform playlist sync | Utility tool, zero discovery aspect |
| **Every Noise at Once** | Genre explorer | Data viz / nerd tool, no playlist creation, no personalization |

### Why None of Them Solve This

None of these products answer: *"What music from THIS place sounds like MY music?"*

Spotify's own regional playlists (e.g., "Top 50 Nigeria") are just popularity charts — they don't match your taste profile. VibeBlend's core differentiator is **audio-DNA-matched cultural discovery**.

### Indirect Competition
- YouTube Music's auto-playlists
- Tidal editorial playlists
- Human curators on Spotify

None of these are personalized + regional simultaneously.

---

## 6. Unique Positioning

**Tagline:** "Your music taste, anywhere in the world."

**Elevator pitch:** "VibeBlend connects to your Spotify, analyzes how your music sounds — the energy, tempo, rhythm — then finds music from anywhere in the world that matches that exact feeling. You get the culture, but it still sounds like you."

**What makes it defensible:**
1. First-mover in audio-DNA-matched cultural discovery
2. Spotify's Recommendations API is powerful but underused for cultural exploration
3. Word-of-mouth natural: travelers share playlists, people tag the app
4. Emotional resonance: music + travel = deeply personal

---

## 7. Technical Constraints & Notes

### Spotify API Rate Limits
- Most endpoints: 30 requests/second
- Recommendations: No official limit but use sparingly; cache results
- Audio Features: Batch up to 100 track IDs per call

### Token Refresh Strategy
- Store `token_expires_at` (Unix timestamp) in Supabase
- Before every API call: check if token is expired
- If expired: call `POST /token` with `refresh_token` grant
- Update stored tokens in Supabase

### Spotify API Gotcha: Genre Seeds
- `seed_genres` must come from Spotify's approved genre list
- Call `GET /recommendations/available-genre-seeds` to get the full list
- Key ones available for African music: `afrobeat`, `afropop`, `afro-soul`, `african`, `south-african`
- `world-music` and `dance` work as supplementary seeds

### Playlist Naming Convention
```
VibeBlend: [Region] × [Month Year]
// e.g., "VibeBlend: Afrobeats × March 2026"
```

### Data Privacy
- Spotify tokens stored in Supabase (encrypted)
- We store: Spotify user ID, display name, token pair
- We do NOT store: listening history, track names, or playlist contents beyond a reference ID
- GDPR: Delete account deletes all rows from both tables

---

## 8. v1 Scope (MVP)

**In:**
- Spotify OAuth (PKCE)
- Music DNA analysis (5 audio features)
- 10 regions (as listed above)
- Blend generation + Spotify playlist creation
- Free tier enforcement (1 blend/month)
- Blend history page
- Mobile-first responsive design

**Out (v2+):**
- Custom genre input
- DNA slider overrides
- Social sharing with visual card
- B2B / travel partner API
- Offline playlist download
- Multi-language UI
- AI-generated playlist descriptions

---

## 9. Success Metrics (3-Month Post-Launch)

| Metric | Target |
|---|---|
| Registered users | 1,000 |
| Blends created | 2,500 |
| D7 retention | >20% |
| Pro conversions | >1.5% |
| App Store rating | >4.2 ⭐ |
| Avg session time | >3 minutes |

---

## 10. Launch Plan

### Week 1: Soft Launch
- ProductHunt (schedule for Tuesday)
- Post in r/solotravel, r/travel, r/spotify
- Post in Nomad List Slack community
- Twitter/X launch thread with demo video

### Week 2: Press Outreach
- Tech: TechCrunch, The Verge ("Spotify but for cultural exploration")
- Music: Pitchfork, NME, Okayafrica (for African angle)
- Travel: Lonely Planet, Conde Nast Traveler digital

### Month 2: Creator Partnerships
- Travel creators on TikTok / Instagram Reels
- Music discovery accounts (playlist curators)
- Digital nomad YouTubers
