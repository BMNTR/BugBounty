---
name: bbp-subdomain-takeover
description: Specialized skill for identifying and exploiting dangling DNS records to perform subdomain takeovers on cloud services. Use during authorized bug bounty or pentest work to enumerate DNS, detect unclaimed third-party resources (S3, Azure, GitHub Pages, Heroku, Fastly), verify exploitability with safe PoCs, and produce a takeover report.
version: "2.0"
---

# Subdomain Takeover Skill

Identifies dangling DNS records (CNAME/A/TXT/NS) pointing to deprovisioned or
unclaimed third-party services, verifies exploitability, and produces a safe,
policy-compliant proof of concept.

## When to Use

- Recon surfaced subdomains whose CNAME chains point to cloud providers
- `httpx`/browser shows vendor error pages ("NoSuchBucket", "There isn't a
  GitHub Pages site here", "No such app")
- Historical data (wayback, CT logs) shows subdomains that no longer resolve
  to live content but still exist in DNS
- Program scope explicitly allows takeover testing (CHECK THE POLICY FIRST)

## Prerequisites

- **Scope check**: confirm the subdomain AND the takeover class are in-scope.
  Some programs forbid actually claiming the resource; then you stop at
  "vulnerable fingerprint confirmed" and document instead.
- Subfinder/amass/assetfinder + dnsx + httpx + nuclei (all present via WSL)
- subzy for mass automated detection (`wsl subzy run --targets subs.txt`)
- dig/host/nslookup for manual CNAME chain verification

## Workflow

### Step 1: Enumerate and Resolve DNS Records

```bash
# Enumerate subdomains (passive first)
subfinder -d target.com -silent | tee recon/subs.txt
assetfinder --subs-only target.com >> recon/subs.txt
sort -u recon/subs.txt -o recon/subs.txt

# Resolve all records: A, CNAME, AAAA, TXT, NS
dnsx -l recon/subs.txt -a -cname -txt -ns -resp -o recon/dnsx.json

# Extract only CNAME-bearing hosts pointing to third parties
cat recon/dnsx.json | jq -r 'select(.cname != null) |
  "\(.host) -> \(.cname)"' | grep -Ev 'target\.com'
```

### Step 2: Detect Dangling / Unclaimed Resources

```bash
# HTTP-probe every CNAME host and capture response body signatures
httpx -l recon/subs.txt -status-code -content-length \
  -title -tech-detect -follow-hosts -no-color \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)" \
  -o recon/httpx.txt

# Automated signature detection with nuclei (takeover template set)
nuclei -l recon/subs.txt -t takeovers/ -severity medium,high,critical \
  -rate-limit 30 -bulk-size 25 -H "User-Agent: Mozilla/5.0" \
  -o recon/nuclei_takeover.txt

# Or subzy for one-shot mass detection with fingerprints built-in
subzy run --targets recon/subs.txt --hide_fails --https \
  > recon/subzy.txt
```

### Step 3: Verify Manually (Never Trust Automation Alone)

```bash
# Confirm the full CNAME chain resolves to NXDOMAIN on the VENDOR side
dig +short CNAME old-app.target.com
dig +short CNAME cname-chain-host.example-cdn.net   # walk each hop
dig +short old-app.target.com                       # A record should fail

# Fetch the error page and match against the fingerprint table
curl -s -A "Mozilla/5.0" https://old-app.target.com/ | head -50

# Distinguish TRUE dangling from soft-fail:
# - Vendor returns its OWN "not found" page  -> likely claimable
# - Target's own 404/catch-all SPA           -> NOT vulnerable (see SKILL.md
#   lesson: a 200 OK can be an SPA catch-all, not a real endpoint)
```

### Step 4: Classify Exploitability

Consult `references/fingerprints.md`:

| Fingerprint state | Meaning | Action |
|---|---|---|
| Vendor error + resource name free | Claimable | Proceed to PoC if policy allows |
| Vendor error + resource name TAKEN | Not exploitable by you (owned by someone else) | Skip; may be someone else's valid asset |
| No vendor error, site loads normally | DNS not dangling | Remove from queue |

### Step 5: Safe Proof of Concept (only if program policy permits)

1. Register/claim ONLY the exact resource named in the dangling record.
2. Publish a benign marker page:
   `<h1>Subdomain Takeover PoC</h1><p>Authorized test for [program name]. Contact: [email]</p>`
3. Screenshot the vulnerable subdomain serving your marker (timestamped).
4. **Reclaim/deprovision immediately after capturing evidence** where the
   provider allows it, to avoid leaving a live hijack behind.

### Step 6: Report

Use `assets/takeover-report.md`. Always include: DNS chain evidence
(`dig` output), vendor fingerprint screenshot, claimed-resource screenshot,
impact narrative (cookie theft via parent-domain cookies, phishing, OAuth
callback hijack, CSP bypass on subdomain).

## Key Concepts

| Concept | Detail |
|---------|--------|
| Dangling CNAME | Record points to service resource that was deleted/unregistered |
| Fingerprint | Unique vendor response body/header proving which service is unclaimed |
| Soft fail vs hard fail | CDN serves custom 404 (hard) vs target SPA catch-all (soft) |
| A-record takeover | Released cloud IP re-allocatable (rare; verify reverse DNS + provider) |
| NS delegation takeover | Subdomain delegated to expired nameserver account (highest impact) |
| Wildcard masking | `*.target.com` always resolves -> hides dangling records from scanners |

## Common False Positives

- SPA catch-all routes returning 200 for anything
- Vendor pages where the underlying resource is still actively owned
- Cloudflare-fronted hosts where origin is gone but CF serves cached content
- `.github.io` claims where org still owns the repo (check HTTP header
  `X-GitHub-Request-Id` presence = repo exists)

## Tools & Systems

| Tool | Purpose |
|------|---------|
| subfinder / amass / assetfinder | Passive subdomain enumeration |
| dnsx | Mass DNS resolution incl. CNAME chains |
| httpx | HTTP probing with tech detection |
| nuclei `-t takeovers/` | Signature-based takeover detection |
| subzy | Dedicated takeover scanner with large fingerprint set |
| can-i-take-over-xyz (GitHub) | Upstream fingerprint reference DB |

## Output Format

Save raw evidence under `programs/<slug>/evidence/`:
`dig_output.txt`, `fingerprint_screenshot.png`, `poc_marker.png`,
plus the filled report from `assets/takeover-report.md`.
