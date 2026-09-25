# Local Resource Map — HackerOne Disclosures

## What lives where (verified)

```
No local disclosure archive found under:
  C:\BugBounty\wordlists\  or  C:\BugBounty\tools\
```

Local assets that serve the same goal:
- `C:\BugBounty\.agents\skills\bbp-hackerone-disclosures\SKILL.md` — curated
  top disclosed reports with rankings/CVSS/CWE (this skill's core content)
- `C:\BugBounty\_templates\report.md` + `report-windows.md` — report formats
- `C:\BugBounty\.agents\skills\bbp-report-writer\` — assembly workflow
- `C:\BugBounty\.agents\skills\bbp-duplicate-guard\` — dedupe check workflow

## Fast lookups (verified)

| Task | Use |
|---|---|
| Learn report style for a vuln class | this skill's SKILL.md curated list |
| Format a submission | `_templates\report.md` |
| Avoid duplicates pre-hunt | bbp-duplicate-guard skill |

## Online sources (when you need raw disclosures)

```text
hackerone.com/hacktivity          -> browse disclosures
hackerone.com/<org>/hacktivity    -> per-program
API (no key needed for public):
curl -s "https://hackerone.com/graphql" ... # heavy; prefer web UI for reads
```

## Optional offline archive

Community mirrors exist; quality varies and they age quickly. If you
clone one, place under `C:\BugBounty\tools\h1-disclosures\` and add a
verified-path row to this file.
