# Landlord Maintenance Tracker — 5 Templates
**For independent landlords and small portfolio owners. No software subscriptions required.**

---

## What's Included

Five plug-and-play templates for managing the operational side of rental property ownership:

1. **Maintenance Request Log** — Track every repair from submission to completion
2. **Contractor Directory** — All your vendors in one place with notes
3. **Annual Property Expense Tracker** — Categorized for tax time
4. **Tenant Communication Log** — Written record of every conversation
5. **Move-In / Move-Out Inspection Checklist** — Room-by-room with photo slots

Each template is available as a Notion database (duplicate-ready) or Google Sheets (copy-ready). Links and setup instructions below each template.

---

---

## TEMPLATE 1: Maintenance Request Log

**What it tracks:** Every maintenance request, who reported it, who fixed it, and how much it cost.

**Why you need it:** When a tenant claims you "never fixed that leak," you need a timestamped paper trail. When the water heater dies for the third time, you need to know the repair history before deciding to replace it.

---

### Fields

| Field | Type | Notes |
|-------|------|-------|
| Request ID | Auto-number | Auto-generated |
| Date Submitted | Date | When tenant reported it |
| Property | Text | Address or unit code |
| Unit | Text | Unit # |
| Tenant Name | Text | Who reported it |
| Issue Category | Select | Plumbing / HVAC / Electrical / Appliance / Structural / Other |
| Issue Description | Long text | Tenant's description verbatim |
| Priority | Select | Urgent (24hr) / Standard (7 days) / Non-urgent (30 days) |
| Assigned Contractor | Relation | Links to Template 2 |
| Contractor Contacted Date | Date | |
| Scheduled Date | Date | |
| Completed Date | Date | |
| Cost | Currency | Parts + labor |
| Paid Via | Select | Check / Zelle / Card / Cash |
| Invoice # | Text | For records |
| Status | Select | Open / In Progress / Completed / Deferred |
| Notes | Long text | Anything relevant |
| Photos | File | Before/after |

---

### How to Use It

**When a request comes in:**
1. Create a new row immediately — don't wait until you've handled it
2. Set Priority based on habitability impact:
   - *Urgent:* No heat, water leak, electrical hazard, lockout, pest infestation
   - *Standard:* Broken appliance, minor plumbing, cosmetic damage
   - *Non-urgent:* Touch-up paint, squeaky door, minor cosmetic
3. Contact your contractor and log the date

**At year end:**
- Filter by property for tax documentation
- Sort by Cost to identify your highest-expense units
- Review repeat issues by category — 3 plumbing calls in one unit usually means a bigger underlying problem

---

### Notion Setup

1. Go to notion.so → New Page → Table view
2. Add each field above as a property with the specified type
3. Create a linked database from Template 2 (Contractor Directory) for the "Assigned Contractor" relation field
4. Add views: All Requests / Open Only / Completed This Month / By Property

### Google Sheets Setup

Row 1: Headers (all field names above)  
Freeze row 1 and column A  
Use Data Validation for dropdown fields (Issue Category, Priority, Status)  
Add conditional formatting: Red = Urgent, Yellow = Standard, Green = Completed

---

---

## TEMPLATE 2: Contractor Directory

**What it tracks:** Every vendor you've ever used, their rates, what they're good at, and how reliable they are.

**Why you need it:** At 11pm when the furnace dies, you don't want to Google "HVAC repair [city]" and call a random plumber. You want to call the guy who showed up on time last winter and charged a fair rate.

---

### Fields

| Field | Type | Notes |
|-------|------|-------|
| Contractor Name | Text | Person's name |
| Company | Text | Business name (if applicable) |
| Trade | Select | Plumbing / HVAC / Electrical / Roofing / General / Locksmith / Pest / Landscaping / Other |
| Phone | Phone | Primary contact |
| Email | Email | For invoices |
| Service Area | Text | What neighborhoods/cities they cover |
| Licensed? | Checkbox | |
| Insured? | Checkbox | |
| License # | Text | Optional but good to have |
| Typical Hourly Rate | Currency | Or note if flat-rate |
| Emergency/After-Hours? | Checkbox | Will they come nights/weekends? |
| Emergency Rate | Currency | Expect 1.5-2x normal |
| Average Response Time | Text | "Same day" / "2-3 days" / "1 week" |
| Quality Rating | Select | ⭐⭐⭐⭐⭐ (1-5) |
| Reliability Rating | Select | ⭐⭐⭐⭐⭐ (1-5) |
| Times Used | Number | Track frequency |
| Last Used Date | Date | |
| Notes | Long text | Any quirks, preferences, payment requirements |
| Do Not Use | Checkbox | Flag problematic vendors |
| Reason (if flagged) | Text | |

---

### How to Use It

**When you hire someone new:**
- Add them before the work is done (while you have their info handy)
- Fill in license/insurance — ask if you don't have it
- After the job: rate quality and reliability honestly, add notes

**Building your contractor list from scratch:**
1. Ask other landlords in your area — best source
2. Check Nextdoor for recommendations from neighbors
3. Angie's List / Thumbtack for initial leads — verify before using
4. Your city's licensed contractor search (most have one)

**The contractor you want has:**
- License + insurance (non-negotiable for anything structural/electrical/plumbing)
- Responds within 4 hours to normal requests
- Gives you a written quote before starting
- Doesn't upsell you on work that isn't needed

---

---

## TEMPLATE 3: Annual Property Expense Tracker

**What it tracks:** Every dollar spent per property, pre-categorized for Schedule E (IRS rental income/expense form).

**Why you need it:** Every dollar of expenses reduces your taxable rental income. Most landlords with informal tracking systems miss 15-25% of legitimate deductions because they can't find the receipts.

---

### Categories (IRS Schedule E Aligned)

- Advertising
- Auto and Travel (property-related)
- Cleaning and Maintenance
- Commissions
- Insurance
- Legal and Professional Fees
- Management Fees
- Mortgage Interest
- Other Interest
- Repairs
- Supplies
- Taxes (Property)
- Utilities
- Depreciation (filled in by your accountant)
- Other

---

### Fields

| Field | Type |
|-------|------|
| Date | Date |
| Property | Text |
| Vendor | Text |
| Category | Select (from list above) |
| Description | Text |
| Amount | Currency |
| Payment Method | Select |
| Receipt Saved? | Checkbox |
| Receipt File | File/Link |
| Notes | Text |

---

### Year-End Use

1. Filter by property → export as CSV
2. Group by Category → gives your CPA the exact Schedule E numbers
3. Cross-reference with bank statements to catch anything missed

**Pro tip:** Reconcile monthly. Catching a missing receipt 2 weeks later is easy. Catching it 11 months later is a nightmare.

---

---

## TEMPLATE 4: Tenant Communication Log

**What it tracks:** Every significant conversation with every tenant, with timestamps.

**Why you need it:** Tenant disputes are won and lost on documentation. "I told you about the mold in October" is a claim. "Here's my log showing we received no communication about mold until February" is evidence.

---

### Fields

| Field | Type |
|-------|------|
| Date | Date |
| Time | Time |
| Property | Text |
| Unit | Text |
| Tenant Name | Text |
| Contact Method | Select: In-person / Phone / Text / Email / Portal / Letter |
| Initiated By | Select: Tenant / Landlord |
| Topic | Select: Maintenance / Rent / Lease / Noise Complaint / Notice / General / Legal |
| Summary | Long text |
| Action Required? | Checkbox |
| Action Taken | Text |
| Action Date | Date |
| Related Maintenance Request | Relation |
| Attachments | File |

---

### Best Practices

- Log within 24 hours of any conversation
- For phone calls: write a 2-3 sentence summary immediately after hanging up
- For text messages: screenshot and attach
- For email: copy/paste subject line and key points
- If you give a verbal notice, follow up with written confirmation

**What to log (even if it seems minor):**
- Any mention of a maintenance issue
- Any late payment discussion
- Any lease violation
- Noise complaints (yours or about theirs)
- Any threat, no matter how casual

---

---

## TEMPLATE 5: Move-In / Move-Out Inspection Checklist

**What it tracks:** Condition of every room, surface, and fixture at both move-in and move-out.

**Why you need it:** Security deposit disputes are the most common landlord-tenant legal issues. A signed, dated inspection form with photos makes the dispute trivial to resolve.

---

### Checklist Structure

Complete for each room/area. Rate condition: **Excellent / Good / Fair / Poor / N/A**

**Exterior**
- [ ] Front door (lock, paint, hardware)
- [ ] Back/side doors
- [ ] Windows (exterior)
- [ ] Siding/paint
- [ ] Yard / landscaping (if tenant responsibility)
- [ ] Driveway / parking
- [ ] Mailbox
- [ ] Outdoor lighting

**Entry / Hallways**
- [ ] Walls (paint, holes, scuffs)
- [ ] Floors
- [ ] Closet doors
- [ ] Lighting fixtures
- [ ] Smoke detector

**Living Room**
- [ ] Walls
- [ ] Floors / carpet
- [ ] Windows (interior)
- [ ] Blinds / curtains
- [ ] Outlets / switches
- [ ] Ceiling fan / light fixture
- [ ] Smoke/CO detector

**Kitchen**
- [ ] Walls
- [ ] Floor
- [ ] Cabinets (interior + exterior)
- [ ] Countertops
- [ ] Sink + faucet
- [ ] Garbage disposal
- [ ] Stove / oven (burners, interior, exterior)
- [ ] Refrigerator (interior, exterior, seals)
- [ ] Dishwasher (if applicable)
- [ ] Range hood / exhaust fan
- [ ] Outlets

**Bedroom(s)** — repeat per bedroom
- [ ] Walls
- [ ] Floor / carpet
- [ ] Closet (doors, rod, shelf)
- [ ] Windows
- [ ] Blinds
- [ ] Lighting
- [ ] Outlets

**Bathroom(s)** — repeat per bathroom
- [ ] Walls / tile
- [ ] Floor
- [ ] Toilet (flush, seat, condition)
- [ ] Sink + faucet (drain, hardware)
- [ ] Shower / tub (caulk, drain, door/curtain rod)
- [ ] Mirror
- [ ] Exhaust fan
- [ ] Cabinet
- [ ] Outlet (GFCI)

**Laundry (if in-unit)**
- [ ] Washer condition
- [ ] Dryer condition
- [ ] Hookups / drain
- [ ] Lint trap

**Utilities / Systems**
- [ ] HVAC filter (note date replaced)
- [ ] Thermostat
- [ ] Water heater (note age if visible)
- [ ] All smoke detectors tested
- [ ] CO detector tested
- [ ] All keys/fobs accounted for (list quantity)

---

### Signature Block

```
Property: _______________________  Unit: ______  Date: __________

Tenant(s): _______________________

Tenant Signature: _______________________  Date: __________

Landlord/Agent: _______________________  Date: __________

Notes: ________________________________________________________________
```

---

### Photo Protocol

Take photos in this order:
1. Every room — wide angle from doorway
2. Any pre-existing damage noted in checklist
3. All appliances (open fridge, oven)
4. All windows
5. Any area the tenant points out as having an issue

Store photos in a folder named: `[Address]-[Unit]-[YYYY-MM]-[MoveIn/MoveOut]`

At move-out, compare side-by-side with move-in photos.

**Normal wear and tear (NOT chargeable):**
- Small nail holes from pictures
- Light carpet wear in traffic areas
- Minor scuffs on walls at normal heights
- Faded paint after 3+ years

**Damage (chargeable):**
- Large holes in walls
- Burns, stains, pet damage to carpet
- Broken fixtures or appliances
- Missing items that were there at move-in

---

## Getting These Into Notion

1. Go to notion.so → New Page → Full Page
2. Create each template as a separate linked database
3. Add a master "Properties" database and relate each template to it
4. Share view-only links with tenants for their unit's maintenance history (optional)

**Template pack built for independent landlords managing 1-20 units.**  
*No subscription required. Duplicate the templates and they're yours.*

---

*Templates by Wolfgang Meyer*
