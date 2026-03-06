---
name: meta-ads-publisher
description: Create and publish ads to Meta Ads Manager via API. Use after /creative_director has prepared ad creatives, copy, and landing pages. Creates campaigns, ad sets, and ads as PAUSED for review. Includes mandatory holistic review before confirming creation.
---

# Meta Ads Publisher

Publish campaign assets to Meta Ads Manager via Marketing API.

## Prerequisites

- Meta Marketing API token (system user with ads_management permission)
- Ad Account ID
- Facebook Page ID
- Payment method on ad account (required by API)
- Approved creatives from /creative_director

## Credentials

Set these in your `.env` file:

```
META_AD_ACCOUNT_ID=act_your_account_id
META_PAGE_ID=your_facebook_page_id
META_ACCESS_TOKEN=your_access_token
```

See TOOLS.md for how to obtain these credentials.

## Workflow

### 1. Gather Assets

Before publishing, confirm you have:
- [ ] Campaign name and objective
- [ ] Ad set targeting (geo, age, interests)
- [ ] Daily/lifetime budget
- [ ] Image files (uploaded or local paths)
- [ ] Ad copy for each creative
- [ ] Landing page URLs
- [ ] CTA type (LEARN_MORE, SIGN_UP, etc.)

### 2. Pre-Publish Holistic Review âš ï¸� MANDATORY

**Before creating ANY ads, review the full picture:**

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�
â”‚  HOLISTIC REVIEW CHECKLIST                              â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  â–¡ Ad copy matches creative visuals                     â”‚
â”‚  â–¡ Landing page URL is correct for each ad              â”‚
â”‚  â–¡ CTA matches the funnel stage (TOFU/MOFU/BOFU)        â”‚
â”‚  â–¡ Targeting makes sense for the offer                  â”‚
â”‚  â–¡ Budget is appropriate for test/scale phase           â”‚
â”‚  â–¡ All ads in set are thematically consistent           â”‚
â”‚  â–¡ No typos or broken links                             â”‚
â”‚  â–¡ DSA compliance fields filled (EU targeting)          â”‚
â”‚  â–¡ Image dimensions correct (1:1, 4:5, etc.)            â”‚
â”‚  â–¡ Video placeholders have complete copy                â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Present summary to user:**
```markdown
## ðŸ“‹ Pre-Publish Review

**Campaign:** [name]
**Objective:** [TRAFFIC/LEADS/etc]
**Budget:** â‚¬[X]/day

**Ad Set:** [name]
**Targeting:** [countries], ages [X-Y]

**Ads to create:**
| # | Name | Type | Landing Page | CTA |
|---|------|------|--------------|-----|
| 1 | ... | Image | /path | LEARN_MORE |
| 2 | ... | Video | /path | SIGN_UP |

**Copy preview:**
> [First 100 chars of each ad's copy...]

âœ… All checks passed. Ready to publish?
```

**Wait for user confirmation before proceeding.**

### 3. Create Campaign

```bash
curl -X POST "https://graph.facebook.com/v21.0/act_{AD_ACCOUNT}/campaigns" \
  -d "name=Campaign Name" \
  -d "objective=OUTCOME_TRAFFIC" \
  -d "status=PAUSED" \
  -d "special_ad_categories=[]" \
  -d "is_adset_budget_sharing_enabled=false" \
  -d "access_token=$TOKEN"
```

**Objectives:**
- `OUTCOME_AWARENESS` â€” Brand awareness
- `OUTCOME_TRAFFIC` â€” Website traffic
- `OUTCOME_ENGAGEMENT` â€” Post engagement
- `OUTCOME_LEADS` â€” Lead generation
- `OUTCOME_SALES` â€” Conversions

### 4. Create Ad Set

```bash
curl -X POST "https://graph.facebook.com/v21.0/act_{AD_ACCOUNT}/adsets" \
  -d "name=Ad Set Name" \
  -d "campaign_id={CAMPAIGN_ID}" \
  -d "status=PAUSED" \
  -d "billing_event=IMPRESSIONS" \
  -d "optimization_goal=LINK_CLICKS" \
  -d "bid_strategy=LOWEST_COST_WITHOUT_CAP" \
  -d "daily_budget=2000" \
  -d 'targeting={"geo_locations":{"countries":["DE","AT","CH"]},"age_min":25,"age_max":55,"targeting_automation":{"advantage_audience":0}}' \
  -d "dsa_beneficiary=Company Name" \
  -d "dsa_payor=Company Name" \
  -d "access_token=$TOKEN"
```

**Required for EU targeting:**
- `dsa_beneficiary` â€” Who benefits from the ads
- `dsa_payor` â€” Who pays for the ads
- `targeting_automation.advantage_audience` â€” 0 to disable, 1 to enable

### 5. Upload Images

```bash
curl -X POST "https://graph.facebook.com/v21.0/act_{AD_ACCOUNT}/adimages" \
  -F "filename=@/path/to/image.png" \
  -F "access_token=$TOKEN"
```

Returns `image_hash` for use in ad creative.

### 6. Create Ads

**Single Image Ad:**
```bash
curl -X POST "https://graph.facebook.com/v21.0/act_{AD_ACCOUNT}/ads" \
  -d "name=Ad Name" \
  -d "adset_id={ADSET_ID}" \
  -d "status=PAUSED" \
  -d 'creative={"object_story_spec":{"page_id":"{PAGE_ID}","link_data":{"image_hash":"{HASH}","link":"https://...","message":"Ad copy here","call_to_action":{"type":"LEARN_MORE"}}}}' \
  -d "access_token=$TOKEN"
```

**Carousel Ad:**
```bash
curl -X POST "https://graph.facebook.com/v21.0/act_{AD_ACCOUNT}/ads" \
  -d "name=Carousel Ad" \
  -d "adset_id={ADSET_ID}" \
  -d "status=PAUSED" \
  -d 'creative={"object_story_spec":{"page_id":"{PAGE_ID}","link_data":{"message":"Main copy","link":"https://...","child_attachments":[{"link":"...","image_hash":"...","name":"Slide title","description":"Slide desc"}],"multi_share_optimized":true}}}' \
  -d "access_token=$TOKEN"
```

**Video Ad (placeholder â€” copy only, no video):**
Create as link ad with copy. Video uploaded later:
```bash
curl -X POST "https://graph.facebook.com/v21.0/act_{AD_ACCOUNT}/ads" \
  -d "name=VIDEO PLACEHOLDER - Name" \
  -d "adset_id={ADSET_ID}" \
  -d "status=PAUSED" \
  -d 'creative={"object_story_spec":{"page_id":"{PAGE_ID}","link_data":{"link":"https://...","message":"Video script as ad copy","name":"Headline","description":"Subhead","call_to_action":{"type":"LEARN_MORE"}}}}' \
  -d "access_token=$TOKEN"
```

### 7. Post-Publish Confirmation

After creating all ads, provide summary:

```markdown
## âœ… Ads Published to Meta

**Campaign:** [name] (ID: xxx) â€” PAUSED
**Ad Set:** [name] (ID: xxx) â€” PAUSED

**Ads Created:**
| # | Name | Type | ID | Status |
|---|------|------|-----|--------|
| 1 | ... | Image | xxx | PAUSED |
| 2 | ... | Carousel | xxx | PAUSED |
| 3 | ... | Video Placeholder | xxx | PAUSED |

**Review in Ads Manager:**
https://www.facebook.com/adsmanager/manage/ads?act={AD_ACCOUNT}

**Next steps:**
1. Review ads in Ads Manager
2. Upload videos for placeholder ads
3. When ready, set status to ACTIVE
```

## CTA Types

| Type | Use Case |
|------|----------|
| LEARN_MORE | General info, tutorials |
| SIGN_UP | Email capture, courses |
| DOWNLOAD | Lead magnets, PDFs |
| GET_OFFER | Promotions, discounts |
| BOOK_NOW | Consultations, calls |
| CONTACT_US | B2B inquiries |
| SHOP_NOW | E-commerce |
| WATCH_MORE | Video content |

## Common Errors

| Error | Solution |
|-------|----------|
| No Payment Method | Add credit card to ad account |
| App in Development Mode | Switch app to Live mode |
| DSA fields required | Add dsa_beneficiary and dsa_payor |
| Advantage Audience required | Add targeting_automation.advantage_audience |
| Invalid image dimensions | Use 1:1, 4:5, or 9:16 aspect ratios |

## Integration with Creative Team

```
/campaign_planner â†’ Strategy approved
        â†“
/creative_director â†’ Assets created
        â†“
/meta_ads_publisher â†’ Published to Meta (PAUSED)
        â†“
User reviews in Ads Manager â†’ ACTIVE
```

## Safety Rules

1. **Always create as PAUSED** â€” Never auto-activate ads
2. **Always do holistic review** â€” Check copy â†” creative match
3. **Always confirm with user** â€” Before creating, after creating
4. **Always provide Ads Manager link** â€” For manual review
5. **Never modify active ads** â€” Only paused/draft
