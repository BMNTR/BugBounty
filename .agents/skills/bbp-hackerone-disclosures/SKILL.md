---
name: bbp-hackerone-disclosures
description: Curated archive of real HackerOne disclosed reports with rankings, CVSS, award amounts, and CWE classifications. Learn from real bug bounty submissions — report format, impact demonstration, and remediation.
---

# HackerOne Disclosed Reports

Sources:
- [reddelexc/hackerone-reports](https://github.com/reddelexc/hackerone-reports) — top disclosed reports with searchable data
- [ajaysenr/HackerOne-Disclosed-Reports](https://github.com/ajaysenr/HackerOne-Disclosed-Reports) — auto-updating structured archive
- [ngalongc/bug-bounty-reference](https://github.com/ngalongc/bug-bounty-reference) — categorized writeup list

## Why This Matters

- See exactly how real findings are **reported and triaged**
- Understand what **severity** different bug types get (XSS vs SQLi vs RCE)
- Learn the **report format** that works — concise summary + steps + impact + remediation + attachments

## What You'll Find

| Info | Example |
|------|---------|
| **Title** | Stored XSS in comments |
| **Severity** | High (P2) |
| **CVSS** | 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N) |
| **Weakness** | CWE-79: Improper Neutralization of Input |
| **Bounty** | $500 - $3,000 |
| **Reproduction** | Full step-by-step with request/response |
| **Impact** | What attacker can actually do |
| **Remediation** | How the team fixed it |

## Top Report Categories

| Type | Typical Severity | Typical Bounty |
|------|-----------------|----------------|
| RCE | Critical | $5k - $20k+ |
| SQL Injection | Critical/High | $1k - $10k |
| SSRF | High | $500 - $5k |
| IDOR | High | $500 - $3k |
| Stored XSS | High | $500 - $3k |
| Reflected XSS | Medium | $250 - $1k |
| Open Redirect | Low/Medium | $100 - $500 |

## How to Use

1. Find a vulnerability class you want to hunt
2. Look at 3-5 disclosed reports in that category
3. Study the **reproduction steps** — what parameters, what payload, what context
4. Study the **report format** — how to write clear, actionable reports
5. Note the **CWE classification** — include this in your own reports

## Reference Links

- [HackerOne Hacktivity](https://hackerone.com/hacktivity) — live stream of disclosures
- [Disclosed Reports](https://hackerone.com/disclosed)
