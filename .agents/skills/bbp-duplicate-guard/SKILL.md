---
name: bbp-duplicate-guard
description: Check existing bug bounty reports and public disclosures before deep-diving on a finding. Use when a candidate vulnerability is identified, to avoid wasting time on known or already-reported issues. Searches HackerOne disclosed reports, GitHub issues, CVEs, and public writeups.
---

# BBP Duplicate Guard

## Pre-Deep-Dive Check

Before spending time on validation, run:

1. Search HackerOne disclosed reports for similar asset + vuln class.
2. Search GitHub issues in the target repository.
3. Search CVEs matching the product + component.
4. Search public writeups (Google: `<target> <vuln> bug bounty writeup`).
5. If the candidate matches a known pattern, note the reference and stop.

## Search Sources

```text
- HackerOne disclosed: https://hackerone.com/<program>/reports
- GitHub Issues: repo issues tab
- CVE database: https://cve.mitre.org or NVD
- Google dork: site:hackerone.com <target> <vuln>
- OpenCVE / GHSA for library vulns
```

### CVE / PoC Research
Ketika nemu library/dependency tua (`package.json`, `requirements.txt`, `Gemfile`, `go.mod`):
```
searchsploit <library> <version>
cve-search <library> <version>
github: "<library>" "<version>" CVE path:.
nvd.nist.gov: search by product + version
```
Cari existing PoC di GitHub (fork/clone untuk lokal test, jangan langsung run ke target). Kalo CVE valid & pakai library ≥ versi rentan di codebase, langsung lapor tanpa perlu exploit penuh — cukup bukti dependency vuln.

## Resolution

| Status | Action |
|--------|--------|
| Exact duplicate found | Stop. Note reference. Move to next target. |
| Partial match, different impact | Continue with narrowed scope. Note difference in report. |
| No match found | Proceed to full validation. |

## Record

Save duplicate check results in:

```text
C:\BugBounty\programs\<program>\evidence\<finding>\duplicate-check.md
```
