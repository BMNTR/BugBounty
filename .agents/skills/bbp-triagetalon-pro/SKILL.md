---
name: bbp-triagetalon-pro
description: Execute passive local attack surface triage using TriageTalon Local Pro engine. Performs passive port scanning, CORS exploitation testing, Swagger/Actuator/sensitive file probing, and certificate subdomain discovery without rate limits.
---

# BBP TriageTalon Local Pro

Use this skill when initializing or triaging a target domain to quickly isolate high-value exposures (CORS misconfigurations, exposed `.env`/`.git`/`swagger`, open databases/management ports).

## Workflow

1. Identify the target domain and active program workspace slug in `programs/<target-name>/`.
2. Run the TriageTalon Local Pro engine:
   ```powershell
   python C:\BugBounty\TriageTalon\recon_local_pro.py <domain> <target-name>
   ```
   Or via the central orchestrator CLI:
   ```powershell
   .\orchestrate.ps1 triagetalon <domain> <target-name>
   ```
3. Review the generated output at `programs/<target-name>/recon/triagetalon_pro.json`.

## Analysis & Pivoting

- **If Grade is C, D, or F**: Examine `sensitive_files` and `cors_analysis` immediately.
- **If CORS issue reported**: Switch to **`bbp-business-logic`** or **`bbp-api-audit`** to craft a PoC exploiting origin reflection.
- **If `.env` or `.git` found**: Immediately run **`bbp-file-upload-lfi`** / **`ghost-scan-secrets`** and save evidence into `programs/<target-name>/evidence/`.
- **If Swagger / Actuator exposed**: Switch to **`bbp-spring-actuator-audit`** or **`bbp-api-audit`**.
- **If Open Ports (22, 3306, 5432, 6379, 27017)**: Document unauthenticated access opportunities.
