# DNS Fix for unitfix.app → GitHub Pages

## Problem
`unitfix.app` is returning NXDOMAIN — no DNS records exist pointing anywhere.

## Solution
Add the following DNS records at your domain registrar (e.g. Namecheap, GoDaddy, Cloudflare, etc.):

### Required DNS Records

| Type  | Name | Value                  | TTL  |
|-------|------|------------------------|------|
| A     | @    | 185.199.108.153        | 3600 |
| A     | @    | 185.199.109.153        | 3600 |
| A     | @    | 185.199.110.153        | 3600 |
| A     | @    | 185.199.111.153        | 3600 |
| CNAME | www  | bummerland17.github.io | 3600 |

> **Note:** `@` means the root domain (`unitfix.app`).

### What these do
- The four **A records** point `unitfix.app` to GitHub's Pages servers.
- The **CNAME** points `www.unitfix.app` to the GitHub Pages endpoint.
- A `CNAME` file with `unitfix.app` is already deployed to the `gh-pages` branch, so GitHub knows to serve this repo at that domain.

## Steps Already Completed (by automation)

✅ GitHub repo made public (was private — Pages requires public repo on free plan)  
✅ Build + deploy GitHub Actions workflow created (`.github/workflows/deploy.yml`)  
✅ Workflow ran successfully — built the React/Vite app and pushed to `gh-pages` branch  
✅ GitHub Pages enabled via API, pointing to `gh-pages` branch  
✅ `CNAME` file with `unitfix.app` deployed to `gh-pages`  

## After Adding DNS Records

Once records propagate (typically **24–48 hours**, often much faster):

1. `https://unitfix.app` will load the app
2. GitHub will automatically provision a **free HTTPS certificate** (Let's Encrypt) — this can take up to 1 hour after DNS propagates

## Verify DNS Propagation

```bash
# Check A records
dig unitfix.app A

# Should return all four IPs:
# 185.199.108.153
# 185.199.109.153
# 185.199.110.153
# 185.199.111.153
```

Or use: https://dnschecker.org/#A/unitfix.app

## GitHub Pages Status

Check Pages status at:  
`https://github.com/Bummerland17/unitfix-simple-maintenance/settings/pages`

Expected timeline:
- **DNS propagation:** 1–48 hours
- **HTTPS cert:** ~1 hour after DNS is live
- **Total downtime after DNS update:** ~1–24 hours
