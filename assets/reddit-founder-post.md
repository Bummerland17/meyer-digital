# Reddit Founder Story Post

## Post for: r/SideProject, r/Entrepreneur, r/indiehackers, r/startups
## (Post separately to each — space them 2-3 days apart)

---

### Title Options (pick one per sub):
- "I tracked my food waste for a month. $74. So I built something."
- "I was spending $60/month on DoorDash while having $80 of food in my fridge. Built a fix."
- "6 months of nights and weekends. Here's what I built and why."
- "The dinner decision problem was costing me $70/month. Here's what I did about it."

---

### Post Body:

Last January I started tracking every ingredient I threw away.

Wilted spinach. Half an onion. That can of chickpeas I kept meaning to use. A block of cheese I forgot about.

At the end of the month: $74 in wasted food. I'd also ordered DoorDash four times that month.

The problem wasn't that I didn't have food. I had food. I just couldn't figure out what to *make* with it at 6pm when I was tired and hungry. So I'd stare at the fridge for 3 minutes, open DoorDash, and spend $35 on something I didn't really want.

I searched for an app that would just tell me what to cook based on what I already owned. Everything I found either wanted me to plan meals in advance (I never do) or showed me recipes that required 4 ingredients I didn't have.

So I built PantryMate.

You type in what's in your fridge and pantry. It tells you what to make. In about 30 seconds. That's it. No meal planning. No "add to grocery list." Just: you have this stuff, here's dinner.

The "Cook Now" filter shows only recipes you can make right now with zero extra shopping. The "1 Away" filter shows recipes you're just one ingredient short on — useful for when you're making a quick grocery run.

It's live at **pantrymate.net** — free to use, Pro plan if you want the full experience.

6 months of evenings and weekends. Zero marketing budget. Just launched.

Happy to answer questions about the build, the stack, or the problem. And if you've solved the dinner decision problem a different way, genuinely curious what works for you.

---

*Stack: React/Vite, Supabase, Stripe. AI recipe matching via [your AI provider].*

---

### Reply Templates (for comments you'll get):

**"What's the tech stack?"**
> React + Vite frontend, Supabase for auth/db, Stripe for payments. AI layer handles the ingredient matching and recipe scoring. Deployed on [host]. Happy to go deeper on any part.

**"How is this different from SuperCook?"**
> SuperCook makes you manually pick every ingredient one by one. PantryMate is more like talking to a chef — you describe what you have, it figures out what to make. The UX is faster and the recommendations are smarter because it scores recipes by how well they match your specific pantry, not just "contains one of these ingredients."

**"Is it free?"**
> Yes, free tier available. Pro is $9.99/mo for unlimited AI suggestions and advanced filters. Pro Plus is $14.99/mo for everything including waste tracking and budget insights.
