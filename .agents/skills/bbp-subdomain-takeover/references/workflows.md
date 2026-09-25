# Subdomain Takeover — Deep Workflows

Companion to SKILL.md. Advanced procedures, edge cases, and mass-scanning
pipelines tuned for the C:\BugBounty toolchain (WSL + bbcore).

## Workflow 1: Full pipeline (subfinder -> dnsx -> httpx -> nuclei)

```bash
# Run inside WSL from the program directory
TARGET=target.com
OUT=programs/$TARGET/recon

mkdir -p "$OUT"

# 1) Passive enumeration, merge all sources
subfinder -d $TARGET -silent -all > $OUT/subs.txt
assetfinder --subs-only $TARGET >> $OUT/subs.txt
amass enum -passive -d $TARGET >> $OUT/subs.txt 2>/dev/null

# 2) Historical + CT-log sources (catch decommissioned hosts)
curl -s "https://crt.sh/?q=%25.$TARGET&output=json" | \
  jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u >> $OUT/subs.txt
sort -u $OUT/subs.txt -o $OUT/subs.txt

# 3) DNS resolution with full record capture
dnsx -l $OUT/subs.txt -a -cname -txt -ns -resp -json -o $OUT/dnsx.json

# 4) Third-party CNAME extraction (exclude apex/own infra)
jq -r 'select(.cname != null) | .host + " -> " + (.cname | join(","))' \
  $OUT/dnsx.json | grep -Ev "(^|\\.)$TARGET" > $OUT/thirdparty_cnames.txt

# 5) HTTP probe only those hosts
awk '{print $1}' $OUT/thirdparty_cnames.txt > $OUT/cname_hosts.txt
httpx -l $OUT/cname_hosts.txt -status-code -content-length -title \
  -tech-detect -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)" \
  -o $OUT/httpx_cnames.txt

# 6) Takeover signature scan (WAF-aware rate limits)
nuclei -l $OUT/cname_hosts.txt -t takeovers/ \
  -rate-limit 30 -bulk-size 25 \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)" \
  -o $OUT/nuclei_takeover.txt
```

## Workflow 2: Wildcard masking bypass

Wildcards (`*.target.com -> some-cdn`) make every subdomain resolve, hiding
dangling records. Strategy:

```bash
# 1) Detect wildcard: query random labels
for i in 1 2 3; do dig +short $(openssl rand -hex 8).target.com; done
# If identical answers every time => wildcard active

# 2) Enumerate anyway (sources give names even without resolution)
#    then resolve ONLY via the third-party host:
#    for each candidate sub, fetch https://sub.target.com and compare
#    response against a known-random label response.
RANDOM_BODY=$(curl -s https://$(openssl rand -hex 8).target.com)
while read sub; do
  BODY=$(curl -s -m 10 "https://$sub")
  if [ "$BODY" != "$RANDOM_BODY" ]; then echo "[+] REAL: $sub"; fi
done < $OUT/subs.txt
```

## Workflow 3: CNAME chains

Dangling can hide mid-chain:

```bash
dig +short CNAME a.target.com   # -> b.target.com
dig +short CNAME b.target.com   # -> legacy.s3.amazonaws.com  <- dangling hop
```

`dnsx` resolves only one hop by default. Walk chains manually or use
`dnstwist`/custom loop until terminal A-record or NXDOMAIN.

## Workflow 4: Edge cases

### A-record takeover
```bash
dig +short A app.target.com        # e.g., 203.0.113.7
whois 203.0.113.7                  # provider? allocated?
# If it is an unallocated/released cloud range IP:
# - AWS EIP: released EIPs get re-allocated to other accounts
# - Verify reverse DNS and current binding BEFORE claiming impact
```
Rare and often out-of-scope; document evidence, check program policy.

### Azure `*.cloudapp.azure.com` re-registration
App Service deleted but CNAME kept -> recreate App Service with same name in
same region. Fingerprint: `404 Web Site not found.` body.

### Cloudflare SaaS / custom hostnames
Subdomain points to Cloudflare but domain not attached to any CF account ->
attacker adds target.com as partial zone / SaaS custom hostname. Fingerprint
is subtle (CF error 1001 `DNS resolution error`). High-value when parent uses
Cloudflare for SaaS vendors.

### GitHub Pages org/repo nuance
- `There isn't a GitHub Pages site here.` = user/org site free -> claimable
- Site loads but repo deleted later = still claimable if username matches
- Header check: presence of `X-GitHub-Request-Id` means Pages infra served
  something real; empty 404 without it leans claimable

## Safety & policy guardrails

1. Claiming a resource IS an active action: confirm the program allows
   takeover PoCs. If policy says "do not register domains", stop at Step 3.
2. Never point claimed resource at real users longer than needed for one
   timestamped screenshot; deprovision after.
3. Do not send email from hijacked MX/SPF during NS takeovers — capturing
   mail is interception; demonstrate SPF/DKIM misconfig textually instead.
4. Keep raw evidence: dig output, HTTP responses, screenshots under
   programs/<slug>/evidence/.

## Triage priority

1. NS delegation dangling (critical)
2. Stale TXT/MX verification records (high)
3. Main-site sibling subdomains on shared auth domain (cookie scope) (high)
4. OAuth redirect_uri hosts (critical if callback accepted)
5. Marketing/campaign subdomains (medium)
6. Internal-name leaks (dev-, staging-, uat-) (info->medium)
