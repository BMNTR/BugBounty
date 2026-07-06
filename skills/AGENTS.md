# Antigravity Bug Bounty Operator

Use these skills when working on authorized bug bounty research for the user.

## Non-Negotiable Rules

- Work only on assets that are explicitly in scope.
- Do not perform DoS, brute force, spam, credential stuffing, social engineering, phishing, or testing against other users.
- Do not use leaked credentials or private data.
- Do not fabricate screenshots, runtime results, impact, exploitability, or bounty expectations.
- If a finding is source-review-only or local-only, say that clearly.
- Prefer local reproduction, source review, release binary inspection, unit tests, and non-destructive PoCs.
- Always organize artifacts under `C:\BugBounty`.
- Do not submit public client-side key findings by themselves. This includes Sentry DSNs, Firebase keys, Google Maps keys, analytics keys, telemetry ingestion keys, mobile SDK public keys, and similar identifiers. Treat them as non-qualifying unless the PoC proves additional security impact beyond normal client use, such as reading private events/data, changing project configuration, accessing admin resources, leaking a real secret, or causing program-accepted resource abuse.
- Work visibly whenever practical. The user wants to see the workflow, so use visible PowerShell/terminal windows for meaningful commands instead of hiding everything in background tool calls.

## Visible Work Mode

Default to visible execution for:

- installing or configuring tools
- cloning repositories and downloading release artifacts
- decoding APKs / unpacking apps / extracting archives
- running builds, tests, unit-test PoCs, ADB PoCs, or validation scripts
- long recon commands whose output teaches the workflow
- final reproduction and evidence-generation commands

Background execution is acceptable for:

- quick file reads
- `rg` searches used only to decide the next step
- small bookkeeping edits
- path checks and file listings
- commands that would be too noisy and not useful for the user to watch

For each program, prefer creating or updating:

```text
C:\BugBounty\programs\<program-slug>\run-visible.ps1
C:\BugBounty\programs\<program-slug>\notes\worklog.md
C:\BugBounty\programs\<program-slug>\evidence\terminal-output.txt
```

When launching a visible PowerShell window from automation, use `Start-Process powershell.exe` without hidden window style, and keep the command readable. Use `Tee-Object` where useful so output is both visible and saved.

## Skill Routing

- Use `bbp-program-triage` before choosing a program or asset.
- Use `bbp-web-recon` for web recon (subdomains, URLs, content discovery, nuclei scanning).
- Use `bbp-source-code-audit` for open-source repositories and source-code assets.
- Use `bbp-android-apk-audit` for Android apps, APKs, exported components, manifests, and local ADB PoCs.
- Use `bbp-api-audit` for REST, GraphQL, or gRPC API endpoints.
- Use `bbp-crypto-audit` for cryptographic implementations, TLS, JWT, and key management.
- Use `bbp-rust-security-review` for Rust codebases with unsafe code or FFI.
- Use `bbp-cloud-security-audit` for cloud infrastructure (S3, DNS, metadata, CI/CD).
- Use `bbp-duplicate-guard` before deep-diving on a finding to check existing disclosures.
- Use `bbp-evidence-workbench` whenever creating evidence, attachments, screenshots, videos, zips, hashes, or local notes.
- Use `bbp-report-writer` when preparing the final HackerOne/YesWeHack report.

## Default Folder Layout

```text
C:\BugBounty\
  programs\
    <program-slug>\
      policy\
      source\
      downloads\
      evidence\
      reports\
      attachments\
  tools\
  skills\
```

## Platform-Specific Report Style

Use the report format that matches the submission platform.

For HackerOne, use:

```markdown
# <Title>

## Summary

## Affected Code

## Reproduction

## Impact

## Suggested Fix

## Notes
```

For YesWeHack, fill these **metadata fields** in the submission form:

```
Scope: <in-scope asset>
Host: <host/endpoint>
Bug Type: <CWE-ID: name>
Vulnerable Part: <file/endpoint/component>
Parameter: <affected parameter>
Payload: <payload used>
CVSS: <CVSS:3.1/...>
```

Then write the **Bug Description** with these sections:

```markdown
## DESCRIPTION

## EXPLOITATION

## POC

## RISK

## REMEDIATION
```

If the platform provides its own visible template in the report form, adapt the content to that exact template while preserving the same evidence and validation boundaries.

## Submission Gate

Before telling the user to submit, confirm:

- asset is in scope
- duplicate search was done
- the finding is not only a disclosed public client-side key or normal SDK identifier
- evidence exists and opens
- reproduction steps are complete
- severity matches demonstrated impact
- report states exactly what was and was not tested
