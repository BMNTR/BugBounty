---
name: bbp-report-writer
description: Write copy-paste-ready bug bounty reports for HackerOne, YesWeHack, and similar platforms. Use after a validated finding to create concise, human-style reports with title, summary, affected code/assets, reproduction, impact, remediation, attachments, and honest validation boundaries.
---

# BBP Report Writer

## Core Rules

- Be accurate, reproducible, and human-sounding.
- Do not exaggerate severity or impact.
- Do not claim live testing, customer data access, server compromise, or payment impact unless proven.
- Include exact asset, version, commit, endpoint, component, payload, and PoC.
- State validation boundaries clearly.
- One vulnerability per report unless chaining is required for impact.
- Reject report drafts that only show a public client-side key or SDK identifier, such as a Sentry DSN, Firebase key, Google Maps key, analytics key, telemetry endpoint, or mobile SDK public key. Write a report only when the evidence proves additional security impact beyond intended public client behavior.

## Platform Format Selection

Always choose the report structure from the submission platform.

For HackerOne reports, use the normal HackerOne-style structure:

```markdown
# <Title>

## Summary

## Affected Code

## Reproduction

## Impact

## Suggested Fix

## Notes
```

For YesWeHack reports, YWH uses structured metadata fields in the submission form plus free-text description sections:

**Metadata fields** (fill in the form):
- **Scope** — affected in-scope asset (domain, URL, APK, repo)
- **Host** — specific host/endpoint (e.g. `api.target.com`)
- **Bug Type** — CWE (e.g. CWE-79: XSS, CWE-200: Information Exposure)
- **Vulnerable Part** — specific file, endpoint, or component (e.g. `/api/v1/users`, `src/auth.rs:42`)
- **Parameter** — affected parameter name (e.g. `user_id`, `redirect_url`)
- **Payload** — the payload used in PoC
- **CVSS** — severity vector and score (e.g. `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N`)

**Description body** (free text, copy-paste into Bug Description field):

```markdown
## DESCRIPTION

## EXPLOITATION

## POC

## RISK

## REMEDIATION
```

If the platform displays a different report template in the form, preserve the platform's section names and adapt the finding into that structure. Do not force the HackerOne format into YesWeHack, and do not force the YesWeHack format into HackerOne.

## Section Mapping

When converting between formats:

- HackerOne `Summary` maps to YesWeHack `DESCRIPTION`.
- HackerOne `Reproduction` maps to YesWeHack `EXPLOITATION`.
- HackerOne `Affected Code` and proof snippets map to YesWeHack `POC`.
- HackerOne `Impact` maps to YesWeHack `RISK`.
- HackerOne `Suggested Fix` maps to YesWeHack `REMEDIATION`.
- HackerOne `Notes` should be folded into the most relevant YesWeHack section, usually `POC` or `RISK`.

**YWH metadata to HackerOne equivalent:**
- Scope → affected URL / asset in Summary
- Host → affected URL in Summary
- Bug Type → Weakness/CWE field in H1 form
- Vulnerable Part → Affected Code section
- Parameter → mention in Reproduction
- Payload → mention in Reproduction / PoC
- CVSS → Severity dropdown in H1 form

## Style

- Start with the core bug, not background.
- Use short paragraphs.
- Put commands in fenced code blocks.
- Put source snippets in fenced code blocks.
- Use bullets for affected paths and suggested fixes.
- Avoid marketing language and certainty beyond proof.

## Validation Boundary Phrases

Use one when appropriate:

```text
No live service, customer data, payment flow, or production account data was tested.
```

```text
This report is based on local source review and a local unit-test reproduction.
```

```text
This was validated against the official release APK manifest and matching source code.
```

## Title Pattern

Use:

```text
<Specific vulnerable component> lets <attacker type> <security impact>
```

Examples:

```text
Exported Android MainActivity lets third-party apps force PIA VPN connect/disconnect through shortcut actions
Signed precompute codes can be replayed across unrelated flag groups to override flag values
VM CPU timeout can be swallowed by precompile handlers and converted into a successful CALL return
```

## Final Submission Checklist

Before submission, verify:

- asset selected is exactly in scope
- weakness/CWE matches root cause
- severity matches proof
- impact dropdown matches proof
- issue is not merely exposed Sentry/Firebase/Google/analytics/telemetry/mobile SDK public key material
- attachment matches platform requirements
- duplicate search was performed
- report does not disclose secrets or private user data
