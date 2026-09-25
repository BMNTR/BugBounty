# Local Resource Map — Nuclei Templates

## What lives where (verified)

```
C:\BugBounty\wordlists\nuclei-templates\              <- template repo clone
  http\cves\      http\vulnerabilities\   http\misconfiguration\
  http\takeovers\ http\exposures\         http\technologies\
  dns\  ssl\  cloud\  code\  dast\  javascript\  network\  workflows\  profiles\
Second copy at C:\BugBounty\tools\nuclei-templates (bbcore may use either).
```

WSL: `/mnt/c/BugBounty/wordlists/nuclei-templates`

## Fast lookups

| Task | Invocation |
|---|---|
| Takeover scan | `-t wordlists/nuclei-templates/http/takeovers/` |
| Exposed panels/secrets | `-t .../http/exposures/` |
| Misconfigurations | `-t .../http/misconfiguration/` |
| CVE-specific (after version fingerprint) | `-t ".../http/cves/<year>/" -tags <product>` |
| Severity triage run | `-severity critical,high -rl 30 -bs 25` |

## Usage recipes

```bash
# WAF-aware scan per AGENTS.md guidance:
nuclei -l subs.txt \
  -t /mnt/c/BugBounty/wordlists/nuclei-templates/http/takeovers/ \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)" \
  -rate-limit 30 -bulk-size 25 -o recon/nuclei.txt

# Tag-based selection instead of paths:
nuclei -u https://target -tags cve,fuzz,network -severity high,critical
```

Custom templates you write go into your program dir, not this clone:
`programs/<slug>/scripts/my-template.yaml`.

## When nothing is local

```bash
nuclei -update-templates    # or:
cd C:\BugBounty\wordlists\nuclei-templates && git pull --ff-only
```
Upstream: github.com/projectdiscovery/nuclei-templates
