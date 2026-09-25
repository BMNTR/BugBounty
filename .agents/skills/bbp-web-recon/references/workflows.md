# Web Recon Workflows (WAF-Aware Pipeline)

Reference for the full recon pipeline. Default entry point is the unified orchestrator
(`.\orchestrate.ps1 recon <domain>`); use these stage-level commands when running a
single stage manually, debugging the pipeline, or when the orchestrator is unavailable.
Every command below assumes WSL2 (Ubuntu) unless marked PowerShell.

Hard rules before anything runs:

- Verify every target against the program scope config (`bb.toml`) first.
- Passive-only until explicitly told to go active.
- All raw output goes to `C:\BugBounty\programs\<slug>\recon\` (WSL path: `/mnt/c/BugBounty/programs/<slug>/recon/`).
- Use a real browser User-Agent on every active tool; default tool UAs (`go-http-client` and similar library defaults) get flagged by Cloudflare/Imperva.

Set once per session:

```bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
SLUG="example-target"
OUT="/mnt/c/BugBounty/programs/$SLUG/recon"
mkdir -p "$OUT"
```

---

## Stage 1: Passive Recon (zero target interaction)

Do this first. Nothing here touches the target directly.

```bash
# Certificate transparency subdomains
curl -s "https://crt.sh/?q=%25.<domain>&output=json" | jq -r '.[].name_value' | sed 's/\*//g' | sort -u > "$OUT/crtsh-subs.txt"

# Historical URLs from Wayback/Common Crawl/OTX
echo "<domain>" | gau --subs --threads 5 > "$OUT/gau.txt" 2>/dev/null
waybackurls <domain> > "$OUT/waybackurls.txt"

# Extract parameters and JS paths worth revisiting later
cat "$OUT"/gau.txt "$OUT"/waybackurls.txt 2>/dev/null | grep -E "\?[a-zA-Z_]+=" | sort -u > "$OUT/params-history.txt"
cat "$OUT"/gau.txt "$OUT"/waybackurls.txt 2>/dev/null | grep -E "\.js($|\?)" | sort -u > "$OUT/js-history.txt"
```

Decision point: if `params-history.txt` is large, that endpoint corpus is often higher
value than any fresh crawl. Old endpoints still resolve surprisingly often.

Also run passive intelligence outside the terminal: Google dorks, GitHub dorks,
Shodan/Censys (see SKILL.md of bbp-program-triage and root AGENTS.md passive section).

## Stage 2: Subdomain Enumeration

```bash
# subfinder - passive, fast, API-key-fed (set keys in ~/.config/subfinder/provider-config.yaml)
subfinder -d <domain> -all -recursive -silent -o "$OUT/subfinder.txt"

# amass passive mode only (active mode is loud; do not use without authorization review)
amass enum -passive -d <domain> -o "$OUT/amass-passive.txt"

# Merge + dedupe + strip wildcard noise
sort -u "$OUT"/crtsh-subs.txt "$OUT"/subfinder.txt "$OUT"/amass-passive.txt 2>/dev/null | grep -F "<domain>" > "$OUT/allsubs.txt"
wc -l "$OUT/allsubs.txt"
```

Realistic expectations: 100-500 subs for a mid-size org, thousands for large ones.
If you get fewer than 10, check that provider API keys are configured in subfinder.

## Stage 3: DNS Resolution (dnsx)

```bash
dnsx -l "$OUT/allsubs.txt" -a -aaaa -cname -resp -silent -t 50 -rl 100 -o "$OUT/dnsx-resolved.txt"

# Pull just the resolvable hostnames for HTTP probing
grep -oP '^[a-zA-Z0-9._-]+' "$OUT/dnsx-resolved.txt" | sort -u > "$OUT/resolved.txt"

# CNAMEs pointing to cloud services are takeover candidates - keep them separate
grep -iE "cname.*(s3|amazonaws|azurewebsites|cloudapp|blob.core.windows|googleusercontent|cloudfront|heroku|github.io|fastly|zendesk|readme.io|tumblr|wordpress|shopify)" "$OUT/dnsx-resolved.txt" > "$OUT/takeover-candidates.txt"
```

Decision point: non-empty `takeover-candidates.txt` -> load `bbp-subdomain-takeover`
before continuing. That is usually faster to validate than web vulns.

## Stage 4: HTTP Probing (httpx)

```bash
httpx -l "$OUT/resolved.txt" \
  -title -tech-detect -status-code -content-length -ip -cdn \
  -follow-host-redirects -no-color -threads 25 -rate-limit 50 \
  -H "User-Agent: $UA" \
  -o "$OUT/httpx-probed.txt"

# Alive hosts only, one per line, for downstream tools
httpx -l "$OUT/resolved.txt" -silent -H "User-Agent: $UA" -o "$OUT/alive.txt"
```

Triage the probe results by response signals:

- `-tech-detect` shows WordPress, Jenkins, Grafana, Spring -> route to matching skill.
- Titles like "Index of /", "Dashboard", "Login" -> manual look now.
- Status 401/403 on interesting paths -> note for later auth-bypass testing, not a finding yet.

## Stage 5: WAF Detection + Nuclei (severity-prioritized)

```bash
# Detect WAF before scanning so rate limits are set correctly
wafw00f -a https://<main-domain> 2>/dev/null || curl -sI "https://<main-domain>" | grep -iE "server:|cf-ray|x-powered"
```

Template selection by severity tier - never run everything at once:

```bash
# Tier 1: critical + high only, first pass
nuclei -l "$OUT/alive.txt" -severity critical,high \
  -rl 30 -bs 25 -c 25 -timeout 8 -retries 1 -silent \
  -H "User-Agent: $UA" \
  -jsonl -o "$OUT/nuclei-high.jsonl"

# Tier 2: medium + low + info, second pass, slower
nuclei -l "$OUT/alive.txt" -severity medium,low,info \
  -exclude-tags fuzz,dos,intrusive \
  -rl 15 -bs 10 -c 10 -timeout 8 -silent \
  -H "User-Agent: $UA" \
  -jsonl -o "$OUT/nuclei-low.jsonl"

# Targeted exposures pass for cloud/exposed-config findings
nuclei -l "$OUT/alive.txt" -t exposures/ -t takeovers/ \
  -rl 20 -bs 15 -silent -H "User-Agent: $UA" \
  -jsonl -o "$OUT/nuclei-exposures.jsonl"
```

Flag meanings that matter:

- `-rl 30` : max requests per second (lower behind WAF).
- `-bs 25` : max payloads per template sent per host per batch (bulk size) - this is what triggers WAF blocks most often.
- `-c 25` : concurrency of templates across hosts.
- `-interactsh-url` optional for OAST callbacks; run `interactsh-client` yourself too and keep your own log (see AGENTS.md lesson 3).

Validation rule: every nuclei hit is a lead, not a report. Re-send the exact request with
curl and confirm the matcher condition manually before it enters `evidence/`.

## Stage 6: Content Discovery (ffuf)

Run against the highest-value alive hosts only (login pages, API roots, main apps).

```bash
ffuf -u https://<host>/FUZZ \
  -w /mnt/c/BugBounty/wordlists/SecLists/Discovery/Web-Content/raft-medium-directories.txt \
  -mc all -fc 404,410 -ac -t 20 -p "0.1-0.5" -timeout 8 \
  -H "User-Agent: $UA" \
  -of json -o "$OUT/ffuf-<host>.json"

# Extensions pass for backups and configs
ffuf -u https://<host>/FUZZ \
  -w /mnt/c/BugBounty/wordlists/SecLists/Discovery/Web-Content/raft-medium-files-lowercase.txt \
  -e .bak,.old,.env,.txt,.zip,.sql,.git/HEAD,.json,.yml \
  -mc all -fc 404,410 -ac -t 20 -p "0.1-0.5" \
  -H "User-Agent: $UA" \
  -of json -o "$OUT/ffuf-files-<host>.json"
```

Key flags:

- `-p "0.1-0.5"` : randomized jitter between requests (flat delays are detectable).
- `-ac` : auto-calibration filters false positives (soft-404 pages).
- `-fc 404,410` plus `-ac` together keeps output clean.
- Keep `-t 20` or lower on WAF-fronted hosts; raise only on confirmed no-WAF hosts.

Decision point: found `/swagger.json`, `/api-docs`, `/actuator`, `/admin`, `.env`,
`.git/HEAD` -> stop ffuf, pivot immediately (bbp-api-audit, bbp-spring-actuator-audit,
bbp-file-upload-lfi). One real endpoint beats ten thousand directory entries.

## Stage 7: Active Crawling (katana)

```bash
katana -list "$OUT/alive.txt" -d 3 \
  -js-crawl -kf all -aff \
  -c 10 -delay 2s -timeout 10 \
  -H "User-Agent: $UA" \
  -o "$OUT/katana-crawl.txt"

# Extract fresh parameterized URLs for manual testing
grep -E "\?[a-zA-Z_]+=" "$OUT/katana-crawl.txt" | sort -u > "$OUT/katana-params.txt"
```

- `-d 3` depth is enough for most apps; going deeper explodes request volume.
- `-kf all` keeps responses even when TLS/keep-alive fails (misconfigurations live there).
- If blocked mid-crawl (403/429 spike), stop, wait, resume with `-delay 5s -c 5`.

## Stage 8: Screenshots (gowitness)

```bash
gowitness file -f "$OUT/alive.txt" --write-screenshot --disable-logging \
  --screenshot-path /mnt/c/BugBounty/programs/$SLUG/evidence/screenshots/
```

Screenshots are for triage speed: scan them visually for login portals, admin panels,
default app pages, stack traces. Attach only the ones backing an actual finding.

---

## WAF-Aware Rate Limiting Cheat Sheet

| Situation | nuclei | ffuf | katana |
|-----------|--------|------|--------|
| No WAF detected | `-rl 60 -bs 50` | `-t 40` | `-c 15` |
| Cloudflare/Imperva/Akamai | `-rl 20 -bs 10` | `-t 10 -p "0.3-0.8"` | `-c 5 -delay 3s` |
| Already received 403/429 | `-rl 10 -bs 5`, add `-delay` between batches | pause 30+ min, then `-t 5 -p "1-2"` | skip, manual only |

Error recovery (from AGENTS.md): 403/429 -> try `-H "X-Forwarded-For: 127.0.0.1"` as one
test, drop rate further, or switch host. Never retry-loop into a block.

## Proxy Rotation Basics

```powershell
.\orchestrate.ps1 proxy direct          # default, fastest, fine for passive+light active
.\orchestrate.ps1 proxy tor             # slow but source IP changes per circuit
.\orchestrate.ps1 proxy rotate proxies.txt   # list of http://host:port entries
```

Rules: rotation is for staying under rate limits, not for evading bans after abuse.
Tor exit nodes are widely flagged; many WAFs will just challenge every Tor request,
making results useless. Prefer direct + low rates for accuracy.

## Output Organization

Everything lands under `programs/<slug>/recon/` using stable filenames:

```text
programs/<slug>/recon/
  crtsh-subs.txt  subfinder.txt  amass-passive.txt  allsubs.txt
  dnsx-resolved.txt  resolved.txt  takeover-candidates.txt
  httpx-probed.txt  alive.txt
  nuclei-high.jsonl  nuclei-low.jsonl  nuclei-exposures.jsonl
  ffuf-<host>.json  katana-crawl.txt  katana-params.txt
```

Update `programs/<slug>/state.json` after each stage (see bbp-program-orchestrator
workflows). Findings promoted out of recon go to `evidence/<finding-slug>/`.
