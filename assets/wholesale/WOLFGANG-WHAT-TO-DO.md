# Your Wholesale Checklist
## What You Do vs. What Rex Does

*Simple. No jargon. Print this out if it helps.*

---

## REX DOES (automated — runs while you sleep):

- ✅ Finds motivated sellers on Craigslist, Facebook Marketplace, and public records
- ✅ Makes first contact with sellers — qualifies them, gets address, condition, price expectations
- ✅ Calls cash buyers to learn their buy box (what they buy, where, at what price)
- ✅ Sends deal packages to buyers when you have a property under contract
- ✅ Follows up with anyone who didn't answer the first time
- ✅ Logs everything so you have a record

**Rex never:** makes offers, commits to prices, signs contracts, or pretends to be human.
**Rex always:** discloses he's an AI, offers opt-out, routes decisions to you.

---

## YOU DO (5 steps per deal, ~2-3 hours total):

---

### STEP 1: Check Rex's Warm Leads (10 min/day)

Every morning, check your Telegram for leads Rex flagged overnight.

A **warm lead** means:
- Seller answered the phone ✅
- Confirmed they own the property ✅
- Open to a cash offer ✅
- Gave Rex their callback info ✅

Cold leads (wrong number, no interest, DNC) are already handled.

**You only call the warm ones.**

---

### STEP 2: Call the Warm Seller Back (15-20 min)

Use the script at: `assets/wholesale/scripts/wolfgang-callback-script.md`

Your goal: **Verify the property and agree on a rough number.**

You need to know:
- Full address (confirm it)
- Are they the owner of record? (ask)
- Rough condition (cosmetic vs. major repairs)
- Price they'd accept
- How quickly they need to close

Then: offer to see it (or get photos). Don't commit to a price until you've run the numbers.

---

### STEP 3: Run the Numbers (10 min)

**Send the address to your AI (me) on Telegram.** I'll pull recent comps in the area and give you an ARV estimate within 2 minutes.

Then apply the formula:

```
ARV × 0.70 = Maximum All-In Price (MAO)
MAO - Estimated Repairs = Max Offer to Seller
Max Offer to Seller + $5,000–$10,000 = Your Assignment Price
```

**Example:**
- ARV (what it'll sell for fixed up): $280,000
- 70% of ARV: $196,000
- Repairs needed: ~$35,000
- Max offer to seller: **$161,000** (offer $155k to leave room)
- Sell contract to buyer at: **$165,000**
- **Your assignment fee: $10,000** 🎉

---

### STEP 4: Get It Under Contract (30 min)

**Use the template at:** `assets/wholesale/contracts/purchase-agreement-template.md`

Fill in:
- Property address
- Seller's name
- Purchase price (your agreed number)
- Your name: **"Wolfgang Meyer or assigns"** ← CRITICAL. Don't skip "or assigns."
- Sign and date it

**Send to seller via:**
- DocuSign (free tier — docusign.com)
- HelloSign (free tier)
- Or print, sign, scan, email

**Earnest Money (EMD):** $500–$1,000 is standard. Some sellers accept $100 if they're motivated. Wire it to the title company within 3 days of signing.

**Title company:** Email one from `assets/wholesale/title-companies.json`. Tell them you have a property under contract you'd like to open escrow on.

---

### STEP 5: Send to Buyers + Collect Your Fee (1 hour)

Once you have a signed contract:

1. Fill out the deal package: `assets/wholesale/deal-package-template.md`
2. Rex sends it to all buyers on the list automatically (or you forward it manually)
3. First buyer with proof of funds (bank statement or LOC) wins
4. Sign the assignment agreement: `assets/wholesale/contracts/assignment-agreement-template.md`
5. Send both contracts (original purchase + assignment) to the title company
6. Show up to closing (or sign remotely)
7. **Collect your assignment fee at closing. Done.**

---

## TITLE COMPANY PROCESS

(Once you have a signed purchase contract and an assignment signed with a buyer)

1. Email your title company contact from `assets/wholesale/title-companies.json`
2. Subject: "New escrow — assignment transaction"
3. Body: "Hi [NAME], I have a property under contract I'm assigning to a buyer. Property is [ADDRESS]. Here are the two contracts attached. Please open escrow and advise on next steps."
4. They handle the rest: title search, closing docs, coordination
5. At close: they pay you the assignment fee directly on the settlement statement

**You don't need to be at the property. You don't need a license. You need a contract.**

---

## TIMELINE PER DEAL

| Day | What Happens |
|-----|-------------|
| Day 1 | Rex qualifies seller, you get notified |
| Day 1-2 | You call back, run numbers, make offer |
| Day 2-3 | Contract signed, escrow opened |
| Day 3-4 | Deal package sent to buyers |
| Day 4-7 | Buyer found, assignment agreement signed |
| Day 7-14 | Title company closes |
| **Day 14** | **You get paid 🎉** |

---

## FREQUENTLY ASKED QUESTIONS

**"Do I need a real estate license?"**
No — not in Arizona, as long as you have the property under a valid purchase contract before marketing it. You are selling your *equitable interest in the contract*, not the property. The "or assigns" language makes this legal.

**"What if I can't find a buyer?"**
Cancel within your inspection period (10 days in your template) and get your EMD back. You're protected.

**"What if the seller asks if you're going to flip it?"**
Be honest: "I'm an investor. I may close on it myself or bring in a co-investor. Either way, your deal doesn't change."

**"What if the title company won't do assignments?"**
Find a different one. Your list in `title-companies.json` has investor-friendly options. Always confirm they handle assignments *before* opening escrow.

**"How much do I need to start?"**
- EMD: $500–$1,000 per deal (refundable if you cancel in time)
- That's it. You don't need to actually buy the property.

---

## YOUR FILES (quick reference)

| File | What It's For |
|------|--------------|
| `scripts/rex-seller-script.md` | Rex's seller qualification script |
| `scripts/rex-buyer-script.md` | Rex's buyer buy box capture script |
| `scripts/wolfgang-callback-script.md` | YOUR personal seller callback script |
| `contracts/purchase-agreement-template.md` | Contract to sign with seller |
| `contracts/assignment-agreement-template.md` | Contract to sign with buyer |
| `deal-package-template.md` | Email template to send buyers |
| `title-companies.json` | 5 investor-friendly title companies in Phoenix |
| `buyer-database.json` | Your 21 cash buyers, ready to contact |
| `deal-tracker.json` | Track your pipeline |

---

> **Remember:** Every deal starts with a phone call. Rex makes the first call. You make the second. The contract makes it real. The title company makes you money.
>
> *You've got this.*
