# TriageTalon Pro — Deep Workflows

Companion to SKILL.md. Output interpretation, triage sequencing, pivots.

## Step 1: Run passive triage (zero aggressive interaction)

```powershell
# From workspace root; ensure program folder exists first:
New-Item -ItemType Directory -Force -Path "programs\<slug>\recon"
python C:\BugBounty\TriageTalon\recon_local_pro.py <domain> <slug>
# or: .\orchestrate.ps1 triagetalon <domain> <slug>
```

Passive phase = no payloads, no brute force -> safe pre-nuclei step per
AGENTS.md scan-loop policy.

## Step 2: Interpret the grade

| Grade | Meaning | Next action |
|---|---|---|
| A/B | Clean surface | proceed to bbp-web-recon active pipeline |
| C | Minor exposures | review sensitive_files + cors_analysis first |
| D/F | High-value exposure | STOP automated scanning; manual verification NOW |

## Step 3: Finding-class pivots (verified paths)

```text
CORS reflection on authed API   -> bbp-api-audit Step 3 two-account replay
.env / .git / .svn exposed      -> ghost-scan-secrets + save raw HTTP to
                                   evidence/ BEFORE the file disappears
swagger/openapi.json            -> bbp-api-audit Step 1 schema-driven queue
actuator endpoints              -> bbp-spring-actuator-audit inventory sweep
ports 6379/27017/9200 unauth    -> SKILL.md encyclopedia service sections;
                                   document banner only unless scope allows
cert CN/SAN extra subdomains    -> feed back into subfinder list, re-triage
```

## Step 4: Evidence capture discipline

1. Save `triagetalon_pro.json` under programs/<slug>/recon/ untouched.
2. For every finding you pivot on, capture raw HTTP request+response
   (.txt) into evidence/ immediately — surfaces vanish.
3. Timestamp screenshots during the same session as the triage run.

## Step 5: When results look empty

```text
- Confirm DNS resolved (no wildcard sinkhole swallowing everything)
- Re-run with explicit scheme if domain serves only www.
- Cross-check with quick manual probes:
  curl -s -o NUL -w "%{http_code}" https://<domain>/.env
  curl -s https://<domain>/swagger.json | more
Empty tool output is a lead to verify manually, not a verdict.
```

## Output contract

triagetalon_pro.json keys consumed by downstream skills:
`grade`, `open_ports[]`, `cors_analysis[]`, `sensitive_files[]`,
`subdomains_from_cert[]`, `swagger_endpoints[]`.
