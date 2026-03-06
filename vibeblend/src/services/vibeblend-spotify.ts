/**
 * vibeblend-spotify.ts
 *
 * Core Spotify service for VibeBlend.
 * Handles: OAuth PKCE, token management, music DNA analysis,
 * region-matched recommendations, and playlist creation.
 *
 * Tech Stack: React + Vite + TypeScript + Supabase
 */

import { createClient } from '@supabase/supabase-js';

// ─────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────

export interface SpotifyTrack {
  id: string;
  name: string;
  uri: string;
  artists: Array<{ id: string; name: string }>;
  album: {
    name: string;
    images: Array<{ url: string; width: number; height: number }>;
  };
  popularity: number;
}

export interface AudioFeatures {
  id: string;
  tempo: number;          // BPM
  energy: number;         // 0.0 – 1.0
  danceability: number;   // 0.0 – 1.0
  valence: number;        // 0.0 – 1.0 (positivity)
  acousticness: number;   // 0.0 – 1.0
  instrumentalness: number;
  speechiness: number;
  loudness: number;       // dB, typically -60 to 0
  key: number;
  mode: number;           // 0 = minor, 1 = major
  time_signature: number;
  duration_ms: number;
}

export interface MusicDNA {
  tempo: number;
  energy: number;
  danceability: number;
  valence: number;
  acousticness: number;
  // Derived label
  profile: 'energetic' | 'chill' | 'danceable' | 'melancholic' | 'euphoric' | 'mixed';
}

export interface RegionConfig {
  id: string;
  label: string;
  flag: string;
  vibe: string; // e.g. "Groovy, rhythmic, infectious"
  genreSeeds: string[]; // Spotify genre seed IDs (max 5 used in API call)
}

export interface BlendResult {
  playlistId: string;
  playlistUrl: string;
  playlistName: string;
  tracks: SpotifyTrack[];
  dna: MusicDNA;
  region: RegionConfig;
}

export interface SpotifyTokens {
  accessToken: string;
  refreshToken: string;
  expiresAt: number; // Unix timestamp ms
}

// ─────────────────────────────────────────────
// Region Registry
// ─────────────────────────────────────────────

export const REGIONS: RegionConfig[] = [
  {
    id: 'afrobeats',
    label: 'Afrobeats',
    flag: '🇳🇬',
    vibe: 'Groovy, rhythmic, infectious',
    genreSeeds: ['afrobeat', 'afropop', 'african', 'dance', 'world-music'],
  },
  {
    id: 'west-african',
    label: 'West African',
    flag: '🌍',
    vibe: 'Soulful, percussive, warm',
    genreSeeds: ['afrobeat', 'afropop', 'afro-soul', 'african', 'world-music'],
  },
  {
    id: 'east-african',
    label: 'East African',
    flag: '🌍',
    vibe: 'Melodic, spiritual, rich',
    genreSeeds: ['african', 'afro-soul', 'world-music', 'afropop', 'dance'],
  },
  {
    id: 'south-african',
    label: 'South African',
    flag: '🇿🇦',
    vibe: 'Bold, euphoric, driving',
    genreSeeds: ['south-african', 'african', 'dance', 'afrobeat', 'afropop'],
  },
  {
    id: 'afropop',
    label: 'Afropop',
    flag: '🌐',
    vibe: 'Upbeat, fresh, global',
    genreSeeds: ['afropop', 'afrobeat', 'afro-soul', 'dance', 'african'],
  },
  {
    id: 'latin',
    label: 'Latin',
    flag: '🇲🇽',
    vibe: 'Passionate, rhythmic, vibrant',
    genreSeeds: ['latin', 'reggaeton', 'salsa', 'tropical', 'latin-pop'],
  },
  {
    id: 'k-pop',
    label: 'K-Pop',
    flag: '🇰🇷',
    vibe: 'Polished, energetic, catchy',
    genreSeeds: ['k-pop', 'k-pop-boy-group', 'k-pop-girl-group', 'korean', 'dance'],
  },
  {
    id: 'dancehall',
    label: 'Dancehall',
    flag: '🇯🇲',
    vibe: 'Bouncy, raw, Caribbean',
    genreSeeds: ['dancehall', 'reggae', 'reggae-fusion', 'caribbean', 'dance'],
  },
  {
    id: 'brazilian',
    label: 'Brazilian',
    flag: '🇧🇷',
    vibe: 'Lush, complex, joyful',
    genreSeeds: ['mpb', 'samba', 'pagode', 'forr', 'axe'],
  },
  {
    id: 'bollywood',
    label: 'Bollywood',
    flag: '🇮🇳',
    vibe: 'Cinematic, colorful, dramatic',
    genreSeeds: ['indian', 'bollywood', 'desi', 'filmi', 'world-music'],
  },
];

// ─────────────────────────────────────────────
// PKCE Helpers
// ─────────────────────────────────────────────

const SPOTIFY_CLIENT_ID = import.meta.env.VITE_SPOTIFY_CLIENT_ID as string;
const SPOTIFY_REDIRECT_URI = import.meta.env.VITE_SPOTIFY_REDIRECT_URI as string;
const SPOTIFY_SCOPES = [
  'user-top-read',
  'playlist-modify-public',
  'playlist-modify-private',
  'user-read-private',
  'user-read-email',
].join(' ');

/** Generate a cryptographically random code verifier */
function generateCodeVerifier(length = 128): string {
  const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
  const array = new Uint8Array(length);
  crypto.getRandomValues(array);
  return Array.from(array)
    .map((x) => charset[x % charset.length])
    .join('');
}

/** SHA-256 hash → Base64URL encode for PKCE challenge */
async function generateCodeChallenge(verifier: string): Promise<string> {
  const data = new TextEncoder().encode(verifier);
  const digest = await crypto.subtle.digest('SHA-256', data);
  return btoa(String.fromCharCode(...new Uint8Array(digest)))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

// ─────────────────────────────────────────────
// OAuth Flow
// ─────────────────────────────────────────────

/**
 * Start Spotify OAuth flow.
 * Stores code_verifier in sessionStorage, then redirects to Spotify.
 */
export async function initiateSpotifyAuth(): Promise<void> {
  const verifier = generateCodeVerifier();
  const challenge = await generateCodeChallenge(verifier);

  sessionStorage.setItem('spotify_code_verifier', verifier);

  const params = new URLSearchParams({
    client_id: SPOTIFY_CLIENT_ID,
    response_type: 'code',
    redirect_uri: SPOTIFY_REDIRECT_URI,
    code_challenge_method: 'S256',
    code_challenge: challenge,
    scope: SPOTIFY_SCOPES,
    show_dialog: 'false',
  });

  window.location.href = `https://accounts.spotify.com/authorize?${params.toString()}`;
}

/**
 * Handle the OAuth callback. Call this from your /callback route.
 * Exchanges auth code for tokens and stores them in Supabase.
 *
 * @returns SpotifyTokens
 */
export async function handleSpotifyCallback(
  code: string,
  supabaseUserId: string,
): Promise<SpotifyTokens> {
  const verifier = sessionStorage.getItem('spotify_code_verifier');
  if (!verifier) throw new Error('No code verifier found. OAuth flow corrupted.');

  const response = await fetch('https://accounts.spotify.com/api/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: SPOTIFY_CLIENT_ID,
      grant_type: 'authorization_code',
      code,
      redirect_uri: SPOTIFY_REDIRECT_URI,
      code_verifier: verifier,
    }),
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(`Token exchange failed: ${err.error_description || err.error}`);
  }

  const data = await response.json();
  sessionStorage.removeItem('spotify_code_verifier');

  const tokens: SpotifyTokens = {
    accessToken: data.access_token,
    refreshToken: data.refresh_token,
    expiresAt: Date.now() + data.expires_in * 1000,
  };

  await storeTokensInSupabase(supabaseUserId, tokens);
  return tokens;
}

/**
 * Refresh an expired access token.
 * Updates Supabase with new token data.
 */
export async function refreshSpotifyToken(
  refreshToken: string,
  supabaseUserId: string,
): Promise<SpotifyTokens> {
  const response = await fetch('https://accounts.spotify.com/api/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: SPOTIFY_CLIENT_ID,
      grant_type: 'refresh_token',
      refresh_token: refreshToken,
    }),
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(`Token refresh failed: ${err.error_description}`);
  }

  const data = await response.json();
  const tokens: SpotifyTokens = {
    accessToken: data.access_token,
    refreshToken: data.refresh_token ?? refreshToken, // Spotify may not always return a new one
    expiresAt: Date.now() + data.expires_in * 1000,
  };

  await storeTokensInSupabase(supabaseUserId, tokens);
  return tokens;
}

/** Persist tokens to Supabase profiles table */
async function storeTokensInSupabase(userId: string, tokens: SpotifyTokens): Promise<void> {
  const supabase = createClient(
    import.meta.env.VITE_SUPABASE_URL,
    import.meta.env.VITE_SUPABASE_ANON_KEY,
  );

  const { error } = await supabase
    .from('profiles')
    .update({
      spotify_access_token: tokens.accessToken,
      spotify_refresh_token: tokens.refreshToken,
      token_expires_at: tokens.expiresAt,
    })
    .eq('id', userId);

  if (error) throw new Error(`Failed to store tokens: ${error.message}`);
}

// ─────────────────────────────────────────────
// Spotify API Client
// ─────────────────────────────────────────────

/** Generic authenticated Spotify API fetch wrapper */
async function spotifyFetch<T>(
  endpoint: string,
  accessToken: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`https://api.spotify.com/v1${endpoint}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (response.status === 401) {
    throw new Error('SPOTIFY_TOKEN_EXPIRED'); // caller should refresh and retry
  }

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(
      `Spotify API error ${response.status}: ${err?.error?.message ?? response.statusText}`,
    );
  }

  // Handle 204 No Content
  if (response.status === 204) return {} as T;
  return response.json();
}

// ─────────────────────────────────────────────
// Music DNA Analysis
// ─────────────────────────────────────────────

/**
 * Fetch user's top tracks (up to 50).
 * time_range: short_term (4 weeks) | medium_term (6 months) | long_term (years)
 */
export async function getTopTracks(
  accessToken: string,
  timeRange: 'short_term' | 'medium_term' | 'long_term' = 'medium_term',
  limit = 50,
): Promise<SpotifyTrack[]> {
  const data = await spotifyFetch<{ items: SpotifyTrack[] }>(
    `/me/top/tracks?time_range=${timeRange}&limit=${limit}`,
    accessToken,
  );
  return data.items;
}

/**
 * Batch fetch audio features for up to 100 track IDs.
 * Spotify allows up to 100 IDs per call.
 */
export async function getAudioFeaturesBatch(
  accessToken: string,
  trackIds: string[],
): Promise<AudioFeatures[]> {
  if (trackIds.length === 0) return [];

  // Chunk into groups of 100
  const chunks: string[][] = [];
  for (let i = 0; i < trackIds.length; i += 100) {
    chunks.push(trackIds.slice(i, i + 100));
  }

  const results: AudioFeatures[] = [];
  for (const chunk of chunks) {
    const data = await spotifyFetch<{ audio_features: (AudioFeatures | null)[] }>(
      `/audio-features?ids=${chunk.join(',')}`,
      accessToken,
    );
    // Spotify may return null for tracks without analysis
    results.push(...data.audio_features.filter((f): f is AudioFeatures => f !== null));
  }

  return results;
}

/**
 * Compute Music DNA from audio features.
 * Returns averaged values + a derived human-readable profile label.
 */
export function computeMusicDNA(features: AudioFeatures[]): MusicDNA {
  if (features.length === 0) {
    throw new Error('Cannot compute DNA with zero audio features');
  }

  const avg = (key: keyof AudioFeatures): number => {
    const sum = features.reduce((acc, f) => acc + (f[key] as number), 0);
    return Math.round((sum / features.length) * 1000) / 1000;
  };

  const dna: MusicDNA = {
    tempo: Math.round(avg('tempo')),
    energy: avg('energy'),
    danceability: avg('danceability'),
    valence: avg('valence'),
    acousticness: avg('acousticness'),
    profile: 'mixed',
  };

  // Derive profile label
  if (dna.energy > 0.7 && dna.danceability > 0.65) {
    dna.profile = 'energetic';
  } else if (dna.energy < 0.4 && dna.acousticness > 0.5) {
    dna.profile = 'chill';
  } else if (dna.danceability > 0.7) {
    dna.profile = 'danceable';
  } else if (dna.valence < 0.35) {
    dna.profile = 'melancholic';
  } else if (dna.valence > 0.75 && dna.energy > 0.65) {
    dna.profile = 'euphoric';
  } else {
    dna.profile = 'mixed';
  }

  return dna;
}

/**
 * Full pipeline: fetch top tracks → audio features → compute DNA.
 * Returns both the DNA and the top tracks (needed for filtering later).
 */
export async function analyzeUserMusicDNA(
  accessToken: string,
): Promise<{ dna: MusicDNA; topTracks: SpotifyTrack[] }> {
  const topTracks = await getTopTracks(accessToken);
  const trackIds = topTracks.map((t) => t.id);
  const features = await getAudioFeaturesBatch(accessToken, trackIds);
  const dna = computeMusicDNA(features);
  return { dna, topTracks };
}

// ─────────────────────────────────────────────
// Recommendations (the core blend logic)
// ─────────────────────────────────────────────

/**
 * Get region-matched track recommendations using Spotify Recommendations API.
 *
 * Seeds the request with:
 *  - Regional genre seeds (from RegionConfig)
 *  - User's DNA as target audio features
 *
 * Filters out tracks the user already knows (topTracks).
 */
export async function getRegionMatchedRecommendations(
  accessToken: string,
  dna: MusicDNA,
  region: RegionConfig,
  knownTrackIds: Set<string>,
  limit = 30, // ask for more than we need so we can filter
): Promise<SpotifyTrack[]> {
  // Spotify allows max 5 seed values total (genres + artists + tracks combined)
  const genreSeeds = region.genreSeeds.slice(0, 5).join(',');

  const params = new URLSearchParams({
    seed_genres: genreSeeds,
    target_energy: dna.energy.toString(),
    target_danceability: dna.danceability.toString(),
    target_valence: dna.valence.toString(),
    target_acousticness: dna.acousticness.toString(),
    target_tempo: dna.tempo.toString(),
    // Allow some tolerance — we don't want to be too strict
    min_energy: Math.max(0, dna.energy - 0.25).toString(),
    max_energy: Math.min(1, dna.energy + 0.25).toString(),
    min_danceability: Math.max(0, dna.danceability - 0.25).toString(),
    max_danceability: Math.min(1, dna.danceability + 0.25).toString(),
    limit: limit.toString(),
  });

  const data = await spotifyFetch<{ tracks: SpotifyTrack[] }>(
    `/recommendations?${params.toString()}`,
    accessToken,
  );

  // Filter out tracks already in user's known library
  const filtered = data.tracks.filter((t) => !knownTrackIds.has(t.id));

  // Return top 25
  return filtered.slice(0, 25);
}

// ─────────────────────────────────────────────
// Playlist Creation
// ─────────────────────────────────────────────

/**
 * Get the current user's Spotify profile.
 */
export async function getSpotifyProfile(
  accessToken: string,
): Promise<{ id: string; display_name: string; images: Array<{ url: string }> }> {
  return spotifyFetch('/me', accessToken);
}

/**
 * Create a new playlist on the user's Spotify account.
 */
export async function createSpotifyPlaylist(
  accessToken: string,
  userId: string,
  name: string,
  description: string,
  isPublic = true,
): Promise<{ id: string; external_urls: { spotify: string } }> {
  return spotifyFetch(`/users/${userId}/playlists`, accessToken, {
    method: 'POST',
    body: JSON.stringify({
      name,
      description,
      public: isPublic,
    }),
  });
}

/**
 * Add tracks to an existing Spotify playlist.
 * Spotify allows max 100 URIs per call.
 */
export async function addTracksToPlaylist(
  accessToken: string,
  playlistId: string,
  trackUris: string[],
): Promise<void> {
  // Chunk into batches of 100
  for (let i = 0; i < trackUris.length; i += 100) {
    const chunk = trackUris.slice(i, i + 100);
    await spotifyFetch(`/playlists/${playlistId}/tracks`, accessToken, {
      method: 'POST',
      body: JSON.stringify({ uris: chunk }),
    });
  }
}

// ─────────────────────────────────────────────
// Master Blend Function
// ─────────────────────────────────────────────

/**
 * The full VibeBlend pipeline.
 *
 * 1. Analyze user's music DNA
 * 2. Get region-matched recommendations
 * 3. Create playlist on Spotify
 * 4. Add tracks
 * 5. Return BlendResult
 *
 * @param accessToken  - Valid Spotify access token
 * @param region       - Selected RegionConfig
 * @param customName   - Optional custom playlist name (Pro feature)
 */
export async function createBlend(
  accessToken: string,
  region: RegionConfig,
  customName?: string,
): Promise<BlendResult> {
  // Step 1: Analyze DNA
  const { dna, topTracks } = await analyzeUserMusicDNA(accessToken);
  const knownTrackIds = new Set(topTracks.map((t) => t.id));

  // Step 2: Get recommendations
  const recommendations = await getRegionMatchedRecommendations(
    accessToken,
    dna,
    region,
    knownTrackIds,
  );

  if (recommendations.length === 0) {
    throw new Error(
      'No matching tracks found for this region. Try a different region or check your Spotify connection.',
    );
  }

  // Step 3: Get user profile for playlist creation
  const profile = await getSpotifyProfile(accessToken);

  // Step 4: Create playlist
  const now = new Date();
  const monthYear = now.toLocaleString('en-US', { month: 'long', year: 'numeric' });
  const playlistName =
    customName ?? `VibeBlend: ${region.label} × ${monthYear}`;
  const description = `Blended by VibeBlend — ${region.label} sounds matched to your music DNA. Energy: ${dna.energy}, Danceability: ${dna.danceability}, Vibe: ${dna.profile}.`;

  const playlist = await createSpotifyPlaylist(
    accessToken,
    profile.id,
    playlistName,
    description,
  );

  // Step 5: Add tracks
  const trackUris = recommendations.map((t) => t.uri);
  await addTracksToPlaylist(accessToken, playlist.id, trackUris);

  return {
    playlistId: playlist.id,
    playlistUrl: playlist.external_urls.spotify,
    playlistName,
    tracks: recommendations,
    dna,
    region,
  };
}

// ─────────────────────────────────────────────
// Blend Limit Enforcement (Free Tier)
// ─────────────────────────────────────────────

export interface BlendQuota {
  canBlend: boolean;
  blendsUsed: number;
  blendsAllowed: number; // 1 for free, Infinity for pro
  resetDate: string;
}

/**
 * Check if user can create a new blend.
 * Reads from Supabase profile. Handles monthly reset.
 */
export async function checkBlendQuota(supabaseUserId: string): Promise<BlendQuota> {
  const supabase = createClient(
    import.meta.env.VITE_SUPABASE_URL,
    import.meta.env.VITE_SUPABASE_ANON_KEY,
  );

  const { data: profile, error } = await supabase
    .from('profiles')
    .select('plan, blend_count_this_month, blend_reset_date')
    .eq('id', supabaseUserId)
    .single();

  if (error || !profile) throw new Error('Could not fetch user profile');

  const today = new Date().toISOString().split('T')[0];
  const resetDate = profile.blend_reset_date as string;

  // Check if we need to reset the monthly count
  if (today > resetDate) {
    // Reset the counter (new month)
    await supabase
      .from('profiles')
      .update({
        blend_count_this_month: 0,
        blend_reset_date: new Date(new Date().getFullYear(), new Date().getMonth() + 1, 1)
          .toISOString()
          .split('T')[0],
      })
      .eq('id', supabaseUserId);

    profile.blend_count_this_month = 0;
  }

  const isPro = profile.plan === 'pro';
  const blendsAllowed = isPro ? Infinity : 1;
  const canBlend = profile.blend_count_this_month < blendsAllowed;

  return {
    canBlend,
    blendsUsed: profile.blend_count_this_month,
    blendsAllowed,
    resetDate: profile.blend_reset_date,
  };
}

/**
 * Increment blend count after a successful blend.
 */
export async function incrementBlendCount(supabaseUserId: string): Promise<void> {
  const supabase = createClient(
    import.meta.env.VITE_SUPABASE_URL,
    import.meta.env.VITE_SUPABASE_ANON_KEY,
  );

  const { error } = await supabase.rpc('increment_blend_count', { user_id: supabaseUserId });
  if (error) throw new Error(`Failed to increment blend count: ${error.message}`);
}

// ─────────────────────────────────────────────
// Save Blend to Supabase History
// ─────────────────────────────────────────────

export async function saveBlendToHistory(
  supabaseUserId: string,
  result: BlendResult,
): Promise<void> {
  const supabase = createClient(
    import.meta.env.VITE_SUPABASE_URL,
    import.meta.env.VITE_SUPABASE_ANON_KEY,
  );

  const { error } = await supabase.from('blends').insert({
    user_id: supabaseUserId,
    region: result.region.id,
    region_label: result.region.label,
    spotify_playlist_id: result.playlistId,
    spotify_playlist_url: result.playlistUrl,
    track_count: result.tracks.length,
    music_dna: result.dna,
  });

  if (error) throw new Error(`Failed to save blend: ${error.message}`);
}

// ─────────────────────────────────────────────
// Convenience: Full Blend Flow with Guards
// ─────────────────────────────────────────────

/**
 * Full guarded blend: checks quota → creates blend → saves to history → increments counter.
 * This is what your React component should call.
 *
 * @param accessToken  - Spotify access token (refresh if needed before calling)
 * @param supabaseUserId - Supabase user UUID
 * @param region - Selected region
 * @param customName - Optional custom playlist name (Pro)
 */
export async function guardedCreateBlend(
  accessToken: string,
  supabaseUserId: string,
  region: RegionConfig,
  customName?: string,
): Promise<BlendResult> {
  // 1. Check quota
  const quota = await checkBlendQuota(supabaseUserId);
  if (!quota.canBlend) {
    throw new Error(
      `BLEND_LIMIT_REACHED:You've used your free blend for this month. Upgrade to Pro for unlimited blends, or try again after ${quota.resetDate}.`,
    );
  }

  // 2. Create the blend
  const result = await createBlend(accessToken, region, customName);

  // 3. Save to history (non-blocking — don't fail the blend if history fails)
  await saveBlendToHistory(supabaseUserId, result).catch((e) =>
    console.warn('Non-fatal: failed to save blend history', e),
  );

  // 4. Increment counter
  await incrementBlendCount(supabaseUserId).catch((e) =>
    console.warn('Non-fatal: failed to increment blend count', e),
  );

  return result;
}
