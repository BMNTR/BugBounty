---
name: bbp-nuclei-templates
description: Reference for projectdiscovery/nuclei-templates — 12,000+ YAML templates for automated vulnerability scanning. AI uses this to select the right templates based on recon findings, prioritize by severity, and run targeted scans.
---

# Nuclei Templates Reference

Source: [projectdiscovery/nuclei-templates](https://github.com/projectdiscovery/nuclei-templates) (12.6k⭐, 12k+ templates)

## Template Categories

| Directory | Count | Use Case |
|-----------|-------|----------|
| `http/cves/` | 3,587 | CVE-based vulnerability checks |
| `http/vulnerabilities/` | 6,468 | Generic vuln detection (XSS, SQLi, LFI, SSRF, etc.) |
| `http/exposures/` | 1,141 | Exposed configs, logs, backup files, .git, .env |
| `http/misconfiguration/` | — | Open S3 buckets, debug endpoints, default creds |
| `http/crlf/` | — | CRLF injection detection |
| `http/default-login/` | — | Default credential checks |
| `http/technologies/` | — | Tech stack fingerprinting (Wappalyzer-style) |
| `http/takeovers/` | — | Subdomain takeover detection |
| `http/dast/` | 240 | DAST-style parameter fuzzing |
| `dns/` | 23 | DNS-specific checks |
| `ssl/` | 38 | TLS/SSL misconfigurations |
| `cloud/` | 659 | AWS/Azure/GCP misconfigurations |
| `workflows/` | 205 | Multi-step scan workflows |
| `code/` | 251 | SAST-style code analysis |

## KEV Coverage (Actively Exploited)

| Source | Templates | Scan Flag |
|--------|-----------|-----------|
| CISA KEV | 454 | `nuclei -tags kev` |
| VulnCheck KEV | 1,449 | `nuclei -tags vkev` |
| Both | 407 | `nuclei -tags kev,vkev` |

Total unique KEV templates: 1,496

## Automation Usage

```powershell
# Scan all alive hosts with critical severity
nuclei -l alive.txt -severity critical -rate-limit 30

# Scan for CVEs from recon data
nuclei -l alive.txt -t cves/ -rate-limit 50

# Scan specific tech stack
nuclei -l alive.txt -t exposures/configs/ -t misconfiguration/

# Scan KEV (actively exploited)
nuclei -l alive.txt -tags kev -rate-limit 30

# Tech stack detection then targeted scan (workflow)
nuclei -l alive.txt -t workflows/tech-detect.yaml
```

## AI Decision Matrix

| If nuclei finds | Then run |
|----------------|----------|
| CVE match | Load CVE PoC repo skill → attempt exploitation |
| Technology X | Run technology-specific templates |
| Low/Info only | Ignore, move to manual review |
| Critical/High | Deep scan with matching payload templates |
