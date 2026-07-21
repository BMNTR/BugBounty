---
name: bbp-program-orchestrator
description: Program workflow orchestrator. Call this first when starting a new target.
---

# Program Workflow Orchestrator

Call this first when starting a new target.

## Phase 1 — Autonomous Recon:
1. Run `wsl bash scripts/program.sh -u <url>` which:
   - Fetches the program page and extracts scope domains
   - Classifies target type (web, API, mobile, source, cloud, crypto, rust)
   - Runs Passive Recon first (Google dorking, GitHub dorking, Shodan, Wayback)
   - Runs full recon pipeline automatically:
     - subfinder, assetfinder, amass (passive) for subdomain enumeration
     - **SCOPE FILTERING**: ALL discovered subdomains MUST be filtered against the in-scope and out-of-scope rules before proceeding.
     - dnsx for DNS resolution (on filtered domains)
     - naabu for fast port scanning (feed open ports to nmap)
     - httpx for HTTP probing (find alive servers on open ports)
     - gau, waybackurls for URL history (ONLY on alive HTTP hosts)
     - SecretFinder / subjs on JS files to extract leaked credentials
     - katana, hakrawler for active web crawling
     - arjun, ffuf for hidden parameter and content discovery
     - dalfox for automated XSS scanning on discovered parameters (use interactsh-client for blind XSS)
     - nuclei for vulnerability scanning (use interactsh-client for OAST/Blind bugs)
   - Runs classification-specific scans:
     - **API**: endpoint discovery from URL corpus, live path probing
     - **Cloud**: S3/GCP bucket enumeration, DNS CNAME takeover checks
     - **Crypto**: nmap TLS cipher scan, JWT endpoint detection
     - **Mobile**: APK download + apktool decompile
     - **Source**: git clone for local analysis
     - **Windows/Binary**: identify executable files for local reverse engineering
   - Saves all raw outputs to `programs/<slug>/recon/`
   - Saves nuclei findings to `programs/<slug>/evidence/`
   - Merges and deduplicates all results
   - Populates `attack_surface.md`, `findings.md`, `final_report.md` with real data
   - Writes classification to `classification.json` for skill routing

## Phase 2 — Skill loading:
- Load `bbp-program-triage` to validate the target
- Load skills matching the program classification:
  - **Web** → `bbp-web-recon`, `bbp-wpscan`, `bbp-advanced-fuzzing`, `bbp-auth-bypass`
  - **API** → `bbp-api-audit`, `bbp-advanced-fuzzing`, `bbp-auth-bypass`
  - **Mobile** → `bbp-android-apk-audit`
  - **Source Code** → `bbp-source-code-audit`
  - **Cryptography** → `bbp-crypto-audit`
  - **Rust** → `bbp-rust-security-review`
  - **Cloud** → `bbp-cloud-security-audit`
  - **Windows** → `binary-triage`, `windows-privilege-escalation`, `windows-lateral-movement`
  - **Binary** → `binary-triage`, `binary-analysis-patterns`, `ctf-reverse`, `protocol-reverse-engineering`
- Always load: `bbp-evidence-workbench`, `bbp-report-writer`, `bbp-duplicate-guard`, `bbp-edoverflow-cheatsheet`, `bbp-payloads-all-the-things`, `bbp-hackerone-disclosures`, `bbp-nuclei-templates`, `bbp-cve-poc-db`, `bbp-hacktricks`, `bbp-seclists`

## Phase 3 — Execution:
- Run the selected skills against the program workspace
- Use `wsl bash scripts/recon.sh -d <domain>` for web targets
- Use `.\scripts\source_audit.ps1 -Path <path>` for source targets
- Use `.\scripts\secrets_scan.ps1 -Path <path>` for secrets scanning
- Use `.\scripts\mobile_audit.ps1 -ApkPath <path>` for mobile APK analysis
- Use `.\scripts\dependency_audit.ps1 -Path <path>` for dependency vuln scanning
- Use `.\scripts\cloud_audit.ps1 -Domain <domain>` for cloud targets
- Use `.\scripts\crypto_audit.ps1 -Domain <domain>` for crypto targets
- Document every finding in `findings.md`
- Continue until all high-risk components have been reviewed

## Phase 4 — Report:
- Load `bbp-report-writer` to generate final report
- Save to `programs/<slug>/final_report.md`
- Attach evidence from `programs/<slug>/evidence/`

## Example:
```
/program https://hackerone.com/example-program
/program https://yeswehack.com/programs/example-program my-program
```
