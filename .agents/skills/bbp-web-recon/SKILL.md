---
name: bbp-web-recon
description: WAF-aware web reconnaissance using bbcore orchestrator. Auto-detects WAF, rotates proxies, runs subfinder→httpx→nuclei→ffuf→katana→gowitness, and triages with TriageTalon.
---

# Web Reconnaissance & Analysis

**CRITICAL RULE**: Do NOT manually execute individual recon tools. Use the unified orchestrator.

## 1. Execution

### Quick recon (WAF-aware, auto proxy):
```powershell
.\orchestrate.ps1 recon <domain>
```

### Deep recon (+ TriageTalon port/CORS/sensitive scan):
```powershell
.\orchestrate.ps1 recon <domain>
.\orchestrate.ps1 triagetalon <domain> <slug>
```

### Proxy options:
```powershell
.\orchestrate.ps1 proxy tor                    # Via Tor
.\orchestrate.ps1 proxy rotate proxies.txt     # Rotate from list
.\orchestrate.ps1 proxy direct                 # No proxy
```

## 2. Analyzing Recon Outputs

Once `recon.ps1` or `/program` finishes, review the files generated in `programs/<target>/recon/` and `programs/<target>/evidence/`.

### Prioritization Strategy
1. **Critical/High Vulnerabilities (`nuclei-*.txt`)**: Immediately validate these manually. Do not blindly report them; trace the logic and prove the impact.
2. **Hidden Content (`ffuf.json` / `endpoints.txt`)**: Look for sensitive paths like `/admin`, `/api/v1`, `/swagger.json`, `/metrics`, or exposed backups (`.env.bak`, `.git`).
3. **JavaScript Files (`js.txt`)**: Look for hardcoded credentials or API keys. You can run `.\scripts\secrets_scan.ps1` on downloaded JS files.
4. **Parameters (`params.txt`)**: Feed interesting parameters into specialized testing (e.g., test `url=`, `redirect=` for SSRF, `id=` for IDOR/SQLi).

## 3. Pivoting: When to Switch Skills

Reconnaissance is just data gathering. Your real job is to exploit. Based on the signals you find in the recon output, immediately transition to the appropriate manual exploitation skill:

| Signal Found in Recon | Switch To Skill / Next Action |
|-----------------------|-------------------------------|
| Cloud Metadata or `url=`, `file=` params | **`bbp-ssrf-hunter`** |
| File Upload functionality (`/upload`, `/avatar`) | **`bbp-file-upload-lfi`** |
| GraphQL endpoint (`/graphql`) | **`bbp-graphql-audit`** |
| API Endpoints (`/api/`, Swagger/OpenAPI docs) | **`bbp-api-audit`** |
| Auth mechanisms (JWT, OAuth, `/login`, password reset) | **`bbp-auth-bypass`** |
| Reflected parameters | **`bbp-xss-hunter`** |
| Shopping Cart / Checkout / Wallet | **`bbp-business-logic`** |
| WordPress detected | **`bbp-wpscan`** |

## 4. Quick Manual Checks
While reviewing endpoints manually in the browser or via proxy, always do quick checks:
- **SSTI**: Inject `{{7*7}}`, `#{7*7}`, `${{7*7}}`, `{{7*'7'}}` into reflected parameters. If the response evaluates it (e.g., returns `49` or `777`), SSTI is likely present.
- **Error Forcing**: Input characters like `'`, `"`, `%00`, `[]` into parameters to trigger verbose errors and disclose framework/database versions.
