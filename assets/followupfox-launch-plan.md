# 🦊 FollowUpFox — Launch Plan

**Product:** FollowUpFox — daily follow-up reminders for freelancers & solo operators  
**Pricing:** Free (10 contacts) / $7/mo unlimited  
**URL:** https://bummerland17.github.io/followupfox/ → eventually followupfox.com

---

## 🚀 Product Hunt Launch

### Title
**FollowUpFox — Never lose a client because you forgot to follow up**

### Tagline
The dead-simple CRM for solo operators. One daily email. Nothing else.

### Description
```
Most freelancers lose clients between conversations — not because they're bad at their work, 
but because they forgot to follow up.

FollowUpFox solves this with radical simplicity:

🦊 Add a contact in 10 seconds (name, note, date)
📬 Get a daily 9am email with exactly who to contact today
💤 Snooze with one click — 3 days, 1 week, or pick a date

No pipelines. No deal stages. No CRM complexity you'll abandon in a week.

Just: who do I need to talk to today?

Built for freelancers, consultants, and solo operators who want more clients — not more software.
```

### Topics
- Productivity
- CRM
- Email
- Freelancing
- SaaS

### Launch Day Checklist
- [ ] Post at 12:01am PT on a Tuesday or Wednesday (best traffic days)
- [ ] Prepare 3-5 GIF demos of the app for comments
- [ ] Have 10-15 early users ready to upvote + comment on launch day
- [ ] Reply to every single comment within 30 minutes
- [ ] Share in Indie Hackers, r/SideProject, and Slack communities day-of
- [ ] Post in Maker Log / WIP.co 1 week before for awareness

### Hunter
Find a top hunter to submit it (search PH for hunters in "productivity" space).

---

## 📢 Reddit Strategy

### r/freelance — Post 1 (problem-first, no pitch)

**Title:** Anyone else losing deals because they forget to follow up? Here's how I finally fixed it

```
This is embarrassing to admit: I lost at least 3 clients last quarter because I just... 
forgot to follow up.

I had the calls, sent the proposals, and then just moved on to other stuff. A week later 
I'd remember, but by then they'd already hired someone else.

I tried HubSpot. Too complex. I tried Notion templates. Didn't stick. I tried calendar 
reminders. They piled up and I ignored them.

What finally worked for me: a spreadsheet with ONE column — "follow up by date" — and 
a daily alarm. Dead simple.

Now I built that as a micro tool. You add a contact + note + date, it emails you every 
morning at 9am with who to contact. That's it. Nothing else.

Anyone else struggle with this? What's your system?

[link to FollowUpFox — mention it's free to start]
```

**Engagement tip:** Answer every reply. Don't lead with the tool, lead with the pain.

---

### r/freelance — Post 2 (show and tell, after 2+ weeks)

**Title:** I built FollowUpFox after losing 3 clients to bad follow-ups [Show HN style]

```
Quick story: lost a $8k project because I forgot to follow up after a great discovery call.

Built FollowUpFox in response — it's a tiny web app that:
- Lets you add contacts with a follow-up date
- Emails you every morning at 9am with exactly who to reach out to
- One-click snooze for 3 days / 1 week / custom date

No pipeline. No stages. No complexity.

Happy to answer questions about building it (React + Supabase + Resend). Also curious 
if this is actually useful to other freelancers.

[link]
```

---

### r/smallbusiness — Post

**Title:** The cheapest CRM I've found for solo operators ($0 to start)

```
If you're a solo consultant or freelancer and "CRM" makes you want to close the tab, 
same.

I needed something that answered one question: "Who do I need to follow up with today?"

Built FollowUpFox for this. Free for 10 contacts, $7/mo for unlimited.

Daily 9am email digest. Add contacts in 10 seconds. Snooze if it's not the right time.

No setup, no learning curve. If you can use a Google Form, you can use this.

Would love feedback from other small business owners — what do you actually need in 
a follow-up tool?
```

---

### r/entrepreneur — Post

**Title:** Launched a micro-SaaS last week — here's exactly what happened (revenue, signups, learnings)

```
[Post after first week of launch with real numbers]

Product: FollowUpFox (daily follow-up reminders)
MRR: $__ 
Free users: __
Paid conversions: __%

What worked:
- Reddit posts in r/freelance got [X] signups
- Product Hunt got [X] upvotes and [X] signups
- Email subject line "🦊 3 follow-ups due today" has [X]% open rate

What didn't:
- [honest reflection]

Happy to answer questions on the build (React + Supabase + Resend).
```

---

## 🛍️ AppSumo Pitch

### Subject Line
**FollowUpFox — Lifetime deal for the only follow-up tool freelancers actually use**

### Body
```
Hi AppSumo team,

I'm the founder of FollowUpFox — a dead-simple follow-up reminder tool for freelancers 
and solo consultants.

**The problem:** Solo operators lose clients not because of bad proposals, but because 
they forget to follow up. Existing CRMs (HubSpot, Pipedrive) are too complex and get 
abandoned within weeks.

**Our solution:** Add a contact in 10 seconds → get a daily 9am email with exactly who 
to contact today → snooze with one click. That's the entire product.

**Why AppSumo users would love it:**
- Freelancers and consultants make up a huge portion of your audience
- Dead simple = actually gets used
- Clear, immediate ROI (one closed deal > lifetime subscription)

**Proposed deal:**
- Lifetime deal: $49 (normally $7/mo = $84/yr)
- Unlimited contacts
- All future features
- 60-day money-back guarantee

**Current traction:**
- [X] beta users
- [X]% daily active rate
- NPS: [score]

Would love to discuss a partnership.

[Your name]
hi@followupfox.com
```

---

## 💰 Pricing Strategy

### Current
| Plan | Price | Limits |
|---|---|---|
| Free | $0/mo | 10 contacts |
| Pro | $7/mo | Unlimited contacts |

### Rationale
- **$7/mo** is below the "do I need to think about this?" threshold
- Free tier (10 contacts) is genuinely useful — hooks consultants with active pipelines
- Conversion trigger: power users naturally hit 10 contacts within 2-3 weeks

### Future Pricing Options
| Path | When to Consider |
|---|---|
| Add a $19/mo team plan | When 2+ users from same company sign up |
| Annual plan ($49/yr = 2 months free) | Once MRR hits $500 |
| AppSumo LTD ($49 one-time) | For early traction spike, then sunset |
| Agency plan ($49/mo, 5 seats) | If freelance agencies start signing up |

### Freemium Conversion Levers
1. **Contact limit hit** → Show upgrade banner with count (e.g., "9/10 contacts used")
2. **Email digest** → Include upsell CTA in footer of free digest emails
3. **Snooze past 14 days** → Pro feature gate
4. **Export to CSV** → Pro feature gate

---

## 📅 90-Day Launch Timeline

### Week 1-2: Soft launch
- [ ] Deploy to production (Vercel + Supabase)
- [ ] Onboard 20 beta testers manually
- [ ] Set up PostHog or Plausible for analytics
- [ ] Stripe integration for payments

### Week 3-4: Content launch
- [ ] r/freelance post #1
- [ ] r/smallbusiness post
- [ ] Indie Hackers milestone post
- [ ] Direct outreach to 50 freelancers in network

### Week 5-8: Product Hunt
- [ ] Build up followers/makers on PH
- [ ] Find hunter
- [ ] Launch on PH (Tuesday or Wednesday)
- [ ] Reddit post #2 (results + show HN)

### Month 3: Monetization
- [ ] Review free→paid conversion rate
- [ ] A/B test pricing page
- [ ] AppSumo pitch if organic growth is slow
- [ ] Add annual billing option

---

## 📊 Success Metrics

| Metric | 30-day goal | 90-day goal |
|---|---|---|
| Free signups | 100 | 500 |
| Paid conversions | 5 ($35 MRR) | 30 ($210 MRR) |
| Daily digest open rate | >40% | >50% |
| 7-day retention | >30% | >40% |
| NPS | >40 | >60 |

---

## 🔧 Technical Launch Checklist

- [ ] Set `VITE_SUPABASE_URL` + `VITE_SUPABASE_ANON_KEY` in production env
- [ ] Deploy Supabase Edge Function `daily-digest`
- [ ] Set `RESEND_API_KEY` secret in Supabase
- [ ] Verify sending domain in Resend
- [ ] Configure cron: `0 9 * * *` UTC
- [ ] Set up custom domain (`followupfox.com`)
- [ ] Enable Supabase email templates (magic link)
- [ ] Add Stripe for payments
- [ ] Set up error monitoring (Sentry)
- [ ] Add analytics (Plausible or PostHog)
