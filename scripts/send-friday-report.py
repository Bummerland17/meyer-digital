import json, requests

token = json.load(open('/root/.openclaw/openclaw.json'))['channels']['telegram']['botToken']
chat_id = '8654703697'

msg = (
    "🔄 *Weekly Feedback Loop Report* — Friday March 6\n\n"
    "*Status:* 2 HIGH priority items flagged\n\n"
    "---\n\n"
    "🔴 *HIGH: Vapi calls — 100% hangup rate*\n"
    "151 calls made this week. Every single one hung up immediately.\n"
    "Alex's opener is not working at all.\n"
    "*Fix needed:* Scribe rewrites the opener.\n"
    "Suggested hook: _\"Hey, this is Alex. I help [business type] in [city] get more 5-star reviews without chasing people down. Quick 45-second question?\"_\n"
    "A/B test 3 variants next week.\n\n"
    "🔴 *Stripe refund flagged — $14*\n"
    "Note: This is from olcowboy21@gmail.com — your own test account. Not a real churn. Sub still active.\n\n"
    "---\n\n"
    "📊 *This week by the numbers:*\n"
    "📞 151 calls | 100% hangup | 57.6% showed interest before dropping\n"
    "💰 1 sub | $14/mo MRR | $1,486 gap to March target\n"
    "📧 Email queue empty — 39 sent total this cycle\n"
    "🚫 Zoho outgoing block still active — no emails sending\n"
    "❌ Reddit: both accounts still rate-limited\n\n"
    "🟡 *Medium (no rush):*\n"
    "• All email subject lines at 0% reply — Quill needs fresh angles\n"
    "• 'Unknown' biz type: 39 sends, 0 replies — drop it\n"
    "• Consider a limited-time MRR push (lifetime deal promo)\n\n"
    "📌 No new subscribers | No new GitHub issues | Zoho block = top unblock priority"
)

r = requests.post(
    f'https://api.telegram.org/bot{token}/sendMessage',
    json={'chat_id': chat_id, 'text': msg, 'parse_mode': 'Markdown'},
    timeout=10
)
print(r.status_code, r.text[:300])
