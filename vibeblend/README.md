# 🎵 VibeBlend

> **Your music taste, anywhere in the world.**

VibeBlend is a smart playlist curator that analyzes your Spotify music DNA and blends it with sounds from any region or culture you're curious about. Whether you've just landed in Nairobi, are curious about K-Pop, or want a Latinx summer — VibeBlend finds the music from that world that *fits you specifically*.

---

## 🧠 How It Works

1. **Connect Spotify** — OAuth login, we pull your top tracks
2. **Analyze your Music DNA** — We compute your average tempo, energy, danceability, valence, and acousticness across your top 50 tracks
3. **Pick your vibe** — Choose a region or culture (Afrobeats, West African, Latin, K-Pop, etc.)
4. **Get matched** — Spotify Recommendations API seeds with your DNA + regional genre seeds to find songs from that culture that sound *like your music*
5. **Blend & Save** — A 25-track playlist is created and saved directly to your Spotify

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite + TypeScript |
| Styling | Tailwind CSS + shadcn/ui |
| Auth + DB | Supabase |
| Music API | Spotify Web API |
| Mobile | Capacitor (iOS + Android) |

---

## 📁 Project Structure

```
vibeblend/
├── src/
│   ├── components/
│   │   ├── ui/                   # shadcn/ui components
│   │   ├── RegionSelector.tsx    # Region/vibe picker grid
│   │   ├── MusicDNACard.tsx      # Visual breakdown of user's audio DNA
│   │   ├── PlaylistCard.tsx      # Generated playlist display
│   │   └── SpotifyConnect.tsx    # OAuth connect button
│   ├── pages/
│   │   ├── Home.tsx              # Landing / onboarding
│   │   ├── Blend.tsx             # Main blend flow
│   │   ├── Dashboard.tsx         # Past blends history
│   │   └── Settings.tsx
│   ├── services/
│   │   └── vibeblend-spotify.ts  # All Spotify API logic (see below)
│   ├── hooks/
│   │   ├── useSpotifyAuth.ts
│   │   ├── useMusicDNA.ts
│   │   └── useBlend.ts
│   ├── lib/
│   │   ├── supabase.ts
│   │   └── regions.ts            # Region → genre seed mapping
│   └── App.tsx
├── capacitor.config.ts
├── vite.config.ts
├── tailwind.config.ts
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- A Spotify Developer App (free at [developer.spotify.com](https://developer.spotify.com))
- A Supabase project (free tier is fine)

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/vibeblend
cd vibeblend
npm install
```

### 2. Environment Variables

Create a `.env.local` file:

```env
VITE_SPOTIFY_CLIENT_ID=your_spotify_client_id
VITE_SPOTIFY_REDIRECT_URI=http://localhost:5173/callback
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 3. Spotify App Setup

In your Spotify Developer Dashboard:
- Add `http://localhost:5173/callback` as a Redirect URI
- Enable the following scopes:
  - `user-top-read`
  - `playlist-modify-public`
  - `playlist-modify-private`
  - `user-read-private`
  - `user-read-email`

### 4. Supabase Schema

Run this in your Supabase SQL editor:

```sql
-- Users table (extends Supabase auth.users)
create table public.profiles (
  id uuid references auth.users on delete cascade primary key,
  spotify_id text,
  display_name text,
  avatar_url text,
  spotify_access_token text,
  spotify_refresh_token text,
  token_expires_at bigint,
  plan text default 'free', -- 'free' | 'pro'
  blend_count_this_month int default 0,
  blend_reset_date date default current_date,
  created_at timestamptz default now()
);

-- Blends history
create table public.blends (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references public.profiles(id) on delete cascade,
  region text not null,
  region_label text,
  spotify_playlist_id text,
  spotify_playlist_url text,
  track_count int,
  music_dna jsonb,  -- stored snapshot of user's DNA at blend time
  created_at timestamptz default now()
);

-- RLS
alter table public.profiles enable row level security;
alter table public.blends enable row level security;

create policy "Users can view own profile" on public.profiles
  for select using (auth.uid() = id);

create policy "Users can update own profile" on public.profiles
  for update using (auth.uid() = id);

create policy "Users can view own blends" on public.blends
  for select using (auth.uid() = user_id);

create policy "Users can insert own blends" on public.blends
  for insert with check (auth.uid() = user_id);
```

### 5. Run Dev Server

```bash
npm run dev
```

### 6. Mobile (Capacitor)

```bash
npm run build
npx cap add ios
npx cap add android
npx cap sync
npx cap open ios   # opens Xcode
npx cap open android  # opens Android Studio
```

---

## 🎛 Spotify API Calls Used

| Call | Purpose |
|---|---|
| `GET /me/top/tracks?limit=50&time_range=medium_term` | Get user's top tracks |
| `GET /audio-features?ids={comma_separated_ids}` | Batch fetch audio features |
| `GET /recommendations?seed_genres=...&target_energy=...` | Get region-matched recommendations |
| `POST /users/{user_id}/playlists` | Create new playlist |
| `POST /playlists/{playlist_id}/tracks` | Add tracks to playlist |

---

## 🌍 Supported Regions (v1)

| Region | Genre Seeds |
|---|---|
| Afrobeats | afrobeat, afropop, african |
| West African | afrobeat, afropop, afro-soul, world-music |
| East African | african, world-music, afro-soul |
| Afropop | afropop, afrobeat, dance |
| South African | south-african, african, dance |
| Latin | latin, reggaeton, salsa |
| K-Pop | k-pop, k-pop-boy-group, k-pop-girl-group |
| Dancehall | dancehall, reggae, caribbean |
| Bollywood | indian, bollywood, desi |
| Brazilian | mpb, samba, forró |

---

## 📦 Key Dependencies

```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.x",
    "@supabase/supabase-js": "^2.x",
    "@capacitor/core": "^6.x",
    "@capacitor/ios": "^6.x",
    "@capacitor/android": "^6.x",
    "axios": "^1.x",
    "zustand": "^4.x"
  },
  "devDependencies": {
    "vite": "^5.x",
    "typescript": "^5.x",
    "tailwindcss": "^3.x",
    "@types/react": "^18.x"
  }
}
```

---

## 🔐 Auth Flow

VibeBlend uses **Spotify OAuth 2.0 PKCE** (no client secret needed on frontend):

1. User clicks "Connect Spotify"
2. Redirect to Spotify OAuth with PKCE challenge
3. Spotify redirects back with `code`
4. Exchange `code` for `access_token` + `refresh_token`
5. Store tokens in Supabase profile (encrypted at rest via Supabase)
6. Use `access_token` for all API calls; auto-refresh when expired

---

## 🧪 Testing

```bash
npm run test          # unit tests
npm run test:e2e      # Playwright e2e
```

---

## 📄 License

MIT
