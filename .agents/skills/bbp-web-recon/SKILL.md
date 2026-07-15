---
name: bbp-web-recon
description: Guide for executing and analyzing web reconnaissance. Use this skill to orchestrate automated recon using recon.ps1 and to interpret the results for manual testing pivoting.
---

# Web Reconnaissance & Analysis

**CRITICAL RULE**: Do NOT manually execute individual recon tools (like `subfinder`, `httpx`, `ffuf`, `nuclei`) in the terminal. That is inefficient. Instead, rely on the automated pipeline and use this skill to analyze the output.

## 1. Execution
If recon has not yet been performed, run the automated pipeline:
```powershell
.\scripts\recon.ps1 -Domain <target.com>
# Add -Quick for fast scans or -Nuclei for full vulnerability scanning
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
