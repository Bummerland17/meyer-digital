# PantryMate Email Drip — Supabase Edge Function Spec

## Overview

A 5-email onboarding drip sequence triggered when a new user signs up.

- **Email 1:** Immediately on signup
- **Email 2:** Day +3
- **Email 3:** Day +7
- **Email 4:** Day +14
- **Email 5:** Day +21

Email provider: Resend (`re_ZhcjQky6_LeqhmR9tf86UEiBRXtcwCGAR`)
From address: `Wolfgang Meyer <hello@pantrymate.net>`

---

## Architecture

### 1. Database table — `email_drip_queue`

```sql
create table email_drip_queue (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  email text not null,
  first_name text,
  email_number int not null,         -- 1..5
  scheduled_for timestamptz not null,
  sent_at timestamptz,
  created_at timestamptz default now()
);

create index on email_drip_queue (scheduled_for) where sent_at is null;
```

### 2. Trigger function — fires on new user signup

Create a Postgres function + trigger on `auth.users`:

```sql
create or replace function handle_new_user_drip()
returns trigger language plpgsql security definer as $$
declare
  first_name text;
begin
  -- Extract first name from metadata or email
  first_name := coalesce(
    new.raw_user_meta_data->>'full_name',
    split_part(new.email, '@', 1)
  );

  insert into email_drip_queue (user_id, email, first_name, email_number, scheduled_for)
  values
    (new.id, new.email, first_name, 1, now()),
    (new.id, new.email, first_name, 2, now() + interval '3 days'),
    (new.id, new.email, first_name, 3, now() + interval '7 days'),
    (new.id, new.email, first_name, 4, now() + interval '14 days'),
    (new.id, new.email, first_name, 5, now() + interval '21 days');

  return new;
end;
$$;

create trigger on_auth_user_created_drip
  after insert on auth.users
  for each row execute procedure handle_new_user_drip();
```

### 3. Edge Function — `send-drip-emails`

Deployed at: `supabase/functions/send-drip-emails/index.ts`

This function is called by a Supabase cron job every 15 minutes.
It picks up any unsent emails where `scheduled_for <= now()` and sends them via Resend.

```typescript
// supabase/functions/send-drip-emails/index.ts
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY')!
const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!

const EMAIL_SUBJECTS: Record<number, string> = {
  1: "Your pantry is set up. Here's what you can cook tonight.",
  2: "The filter that saves most people money (most users miss it)",
  3: "Your first week with PantryMate",
  4: "What $134/month in food waste taught me",
  5: "Last email (I promise) — one question",
}

function buildEmailBody(emailNumber: number, firstName: string): string {
  const name = firstName || 'there'
  switch (emailNumber) {
    case 1:
      return `Hey ${name},\n\nYou just set up PantryMate. Here's the thing most people miss:\n\nThe "Cook Now" filter only shows recipes where you already have EVERYTHING. No substitutions, no "oh wait I need to grab X". Just: you have this stuff → here's dinner.\n\nTry it tonight. Add 5-10 ingredients from your fridge/pantry, hit Cook Now, and pick something.\n\nThat's the whole product. 30 seconds to dinner.\n\n→ https://pantrymate.net\n\n— Wolfgang (the guy who built this because he was wasting $74/month on food)\n\nP.S. The "1 Away" filter shows what you're just one ingredient short of. It's weirdly satisfying.`
    case 2:
      return `Hey ${name},\n\nQuick tip from someone who's watched how people use PantryMate:\n\nMost users start with "Cook Now" which is great. But the "1 Away" filter is where the magic happens.\n\nIt shows you every recipe you could make if you just grabbed ONE more ingredient. So instead of buying a full meal kit or ordering DoorDash, you spend $2 on one item and unlock 12 new meal options.\n\nA lot of people have told me this filter alone paid for the app.\n\nGive it a try: https://pantrymate.net\n\n— Wolfgang`
    case 3:
      return `Hey ${name},\n\nIt's been a week. By now you've probably noticed whether PantryMate fits into your routine or not.\n\nIf it has — if you've avoided at least one DoorDash order or used up something that would've gone to waste — consider going Pro.\n\nPro gives you:\n✓ Unlimited daily scans (free tier caps at 3/day)\n✓ Smart AI filters (dietary preferences, time available)\n✓ Weekly shopping list generation\n✓ Budget tracker\n\n$9.99/month. Cancel any time.\n\nOr — and this is the deal I'm running for early users — grab lifetime Pro Plus for $49. One payment, everything forever, no subscription anxiety.\n\n→ Upgrade to Pro: https://pantrymate.net/upgrade\n→ Lifetime Deal ($49): https://buy.stripe.com/bJe14mfVyfAocYvg04bsc00\n\n— Wolfgang`
    case 4:
      return `Hey ${name},\n\nBefore I built PantryMate, I tracked everything I threw away for a month.\n\n$74 in wasted groceries. Plus $60 in DoorDash orders placed on nights I had a full fridge.\n\n$134/month because I couldn't answer "what's for dinner?"\n\nThe app started as a spreadsheet, then a script, then a proper product. I've been using it every day for 6 months. My food waste is down around 80%. More importantly, I'm not standing at the fridge anymore feeling paralyzed at 6pm.\n\nIf you're getting value from it, I'd genuinely love a review or even just a reply to this email telling me what you think.\n\nAnd if you haven't upgraded yet — here's the lifetime deal one more time: $49, everything forever: https://buy.stripe.com/bJe14mfVyfAocYvg04bsc00\n\n— Wolfgang`
    case 5:
      return `Hey ${name},\n\nLast email in this sequence, I promise.\n\nOne question: What would make PantryMate worth paying for, if it isn't already?\n\nHit reply and tell me. I read every response and actually build the things people ask for.\n\nIf you're already getting value — the lifetime deal is still available at $49: https://buy.stripe.com/bJe14mfVyfAocYvg04bsc00\n\nThanks for trying it.\n\n— Wolfgang`
    default:
      return ''
  }
}

Deno.serve(async () => {
  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

  // Fetch all unsent emails due now
  const { data: pending, error } = await supabase
    .from('email_drip_queue')
    .select('*')
    .is('sent_at', null)
    .lte('scheduled_for', new Date().toISOString())
    .limit(50)

  if (error) {
    return new Response(JSON.stringify({ error: error.message }), { status: 500 })
  }

  const results = []

  for (const row of pending ?? []) {
    const subject = EMAIL_SUBJECTS[row.email_number]
    const body = buildEmailBody(row.email_number, row.first_name)

    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: 'Wolfgang Meyer <hello@pantrymate.net>',
        to: [row.email],
        subject,
        text: body,
      }),
    })

    if (res.ok) {
      await supabase
        .from('email_drip_queue')
        .update({ sent_at: new Date().toISOString() })
        .eq('id', row.id)
      results.push({ id: row.id, email: row.email, emailNumber: row.email_number, status: 'sent' })
    } else {
      const err = await res.text()
      results.push({ id: row.id, email: row.email, emailNumber: row.email_number, status: 'failed', error: err })
    }
  }

  return new Response(JSON.stringify({ processed: results.length, results }), {
    headers: { 'Content-Type': 'application/json' },
  })
})
```

### 4. Cron job — run every 15 minutes

In Supabase dashboard → Database → Cron Jobs:

```sql
select cron.schedule(
  'send-drip-emails',
  '*/15 * * * *',
  $$
  select net.http_post(
    url := 'https://lelzkoiyqwrqzqprg.supabase.co/functions/v1/send-drip-emails',
    headers := '{"Authorization": "Bearer <SERVICE_ROLE_KEY>", "Content-Type": "application/json"}'::jsonb,
    body := '{}'::jsonb
  )
  $$
);
```

### 5. Environment variables to set in Supabase Edge Functions

| Variable | Value |
|---|---|
| `RESEND_API_KEY` | `re_ZhcjQky6_LeqhmR9tf86UEiBRXtcwCGAR` |
| `SUPABASE_URL` | `https://lelzkoiyqwrqzqprg.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | *(get from Supabase dashboard → Settings → API)* |

---

## Deployment steps

1. Run the SQL above in Supabase SQL editor (create table + trigger)
2. Deploy edge function: `supabase functions deploy send-drip-emails`
3. Set environment variables in Supabase dashboard
4. Set up cron job in Supabase dashboard
5. Test by creating a new user and checking `email_drip_queue` table

## Email files (reference)

See `/root/.openclaw/workspace/assets/email-drip-pantrymate/` for all 5 email body templates.
