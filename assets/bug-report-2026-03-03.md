# PantryMate Bug Report — 2026-03-03
Repo: https://github.com/Bummerland17/honest-eats

---

## 🔴 CRITICAL

### C1 — Admin Emails Hard-Coded in Public Migration
**File:** `supabase/migrations/20260302234309_...sql`
Nine real personal email addresses permanently baked into public git repo.
- **Risk 1:** PII exposure — violates GDPR/CCPA
- **Risk 2:** Anyone registering with one of these emails gets automatic admin access
**Fix:** Remove emails from migration. Store in private env var. Use manual admin assignment. Purge from git history with `git filter-repo`.

---

## 🟠 HIGH

### H1 — Wrong Value Stored as `stripe_subscription_id`
**File:** `supabase/functions/check-subscription/index.ts` ~line 170
Stores `customers.data[0]?.id` (Customer ID `cus_...`) instead of `subscriptions.data[0].id` (Subscription ID `sub_...`).
**Fix:** Capture `sub.id` during subscription loop and store that instead.

### H2 — Pro+ Users Incorrectly Rate-Limited (Paying Customers Get Wrong Tier)
**File:** `supabase/functions/_shared/rate-limit.ts` lines ~43–57
All premium users get 50 AI calls/day. Pro+ unlimited branch is dead code. Paying Pro+ customers are being denied the service they paid for.
**Fix:** Cross-reference Stripe product ID against known Pro+ product IDs to correctly set `tier = "pro_plus"` with `limit = 0`.

### H3 — `drip-scheduler` and `send-drip-email` Have No Caller Authentication
**Files:** `supabase/functions/drip-scheduler/index.ts`, `supabase/functions/send-drip-email/index.ts`
Anyone with the public anon key can trigger batch email sends or send arbitrary drip emails.
**Fix:** Verify caller has service role key in Authorization header before processing.

### H4 — Subscription Cache Has No TTL (Cancelled Subscriptions Stay Active)
**File:** `src/hooks/useSubscription.ts` lines ~58–72
Cancelled subscriptions persist in localStorage forever — users retain Pro/Pro+ access after cancellation.
**Fix:** Add `cachedAt: Date.now()` to cache and reject entries older than 5 minutes.

---

## 🟡 MEDIUM

### M1 — Privacy Policy Checkbox Bypassed for OAuth Sign-Ups
**File:** `src/pages/AuthPage.tsx` lines ~65–70
Google/Apple OAuth buttons have no privacy gate. New OAuth users never acknowledge privacy policy — GDPR/legal risk.
**Fix:** Detect new OAuth users via `user.created_at` and show post-OAuth privacy consent step.

### M2 — Rate Limiter Fails Open on DB Errors
**File:** `supabase/functions/_shared/rate-limit.ts` lines ~67–71
DB errors silently bypass all rate limiting. Motivated attacker could trigger DB degradation for unlimited AI calls.
**Fix:** Return 503 during sustained DB errors instead of silently allowing all requests.

### M3 — Whop Webhook: Timing-Unsafe Signature Comparison
**File:** `supabase/functions/whop-webhook/index.ts` line ~39
String equality is not constant-time — timing attack could leak HMAC signature.
**Fix:** Use XOR-based constant-time byte comparison.

### M4 — `manage-admins` Fetches All Users to Find One (DoS Risk)
**File:** `supabase/functions/manage-admins/index.ts` lines ~84–92
`auth.admin.listUsers()` loads ALL users into memory to find one by email. Will timeout at scale.
**Fix:** Use filtered query or paginated lookup instead of full list scan.

### M5 — `.env` File Committed to Repository
`.env` with Supabase URL and anon key tracked in git. Establishes dangerous habit — one accidental service role key commit would be catastrophic.
**Fix:** `git rm --cached .env`, verify `.gitignore`, use `.env.example` with placeholders.

---

## 🔵 LOW

### L1 — `PerfOverlay` Dev Tool Shipped in Production
**File:** `src/App.tsx` ~line 15
Internal performance metrics exposed to all users.
**Fix:** `{import.meta.env.DEV && <PerfOverlay />}`

### L2 — `AuthContext` Dual State Init Race Condition
**File:** `src/contexts/AuthContext.tsx` lines ~27–40
Both `onAuthStateChange` and `getSession()` call `setLoading(false)` independently — brief inconsistent state window possible.
**Fix:** Use `onAuthStateChange` with `INITIAL_SESSION` as sole source of truth; remove separate `getSession()` call.

### L3 — No Stripe Webhook for Real-Time Subscription Events
No handler for `customer.subscription.deleted`, `customer.subscription.updated`, `invoice.payment_failed`. Cancellations only reflected when user next visits app.
**Fix:** Add `/stripe-webhook` edge function to immediately sync subscription changes.

---

## Summary

| ID | Severity | Issue |
|----|----------|-------|
| C1 | 🔴 Critical | Admin emails in public git |
| H1 | 🟠 High | Wrong stripe_subscription_id stored |
| H2 | 🟠 High | Pro+ users rate-limited incorrectly |
| H3 | 🟠 High | Unauthenticated drip email endpoints |
| H4 | 🟠 High | Subscription cache no TTL |
| M1 | 🟡 Medium | OAuth bypasses privacy policy |
| M2 | 🟡 Medium | Rate limiter fails open |
| M3 | 🟡 Medium | Timing-unsafe webhook signature |
| M4 | 🟡 Medium | listUsers() DoS risk |
| M5 | 🟡 Medium | .env committed to repo |
| L1 | 🔵 Low | PerfOverlay in production |
| L2 | 🔵 Low | Auth race condition |
| L3 | 🔵 Low | No Stripe webhook |

**Recommended fix order:** C1 immediately → H2 (paying users affected) → H4 → H1 → H3 → rest
