---
name: bbp-report-writer
description: Write and self-triage bug bounty reports for HackerOne, YesWeHack, and similar platforms. Structures drafts from raw hunter notes, validates before submission, and applies per-class gotcha checks. Use after a validated finding.
---

# BBP Report Writer

## Core Rules

- Be accurate, reproducible, and human-sounding.
- Do not exaggerate severity or impact.
- Do not claim live testing, customer data access, server compromise, or payment impact unless proven.
- Include exact asset, version, commit, endpoint, component, payload, and PoC.
- State validation boundaries clearly.
- One vulnerability per report unless chaining is required for impact.
- Reject report drafts that only show a public client-side key or SDK identifier (Sentry DSN, Firebase key, Google Maps key, analytics key, telemetry endpoint, mobile SDK public key). Write a report only when evidence proves additional security impact.

---

## Mode 1 -- Write (structuring raw notes into a report)

Trigger: hunter says "help me write this up", "here are my notes", "what sections do I need", or pastes raw lab notes.

**Required inputs before drafting:**
- The confirmed finding (what is the bug, what did you observe)
- The affected asset / endpoint / parameter
- The PoC (request/response, command, or steps)
- The impact (what can an attacker actually do, proven)

If any of the above is missing, **ask for it before drafting**. Do not fill the gap.

### Required Body Sections (in order)

1. **Description** -- 1-3 sentences. What the bug is, factual and specific. No CWE ID here (platform renders it from the form). No OWASP intro.
2. **Vulnerability Discovery** -- Testing narrative. What you tried, what you noticed, what made you dig in. Lab-notes style. Dead ends and friction are credible; a polished narrative with no failed attempts is not.
3. **Proof of Concept (PoC)** -- Raw HTTP request/response preferred. curl acceptable. Screenshot when visual proof matters. Video for multi-step or timing-dependent bugs. Strip session tokens and PII; use [REDACTED].
4. **Exploitation** -- Numbered steps, one action per step. State preconditions upfront (anonymous / authenticated / which role / required victim interaction / required browser). Include expected vs actual at the step where the bug manifests.
5. **Impact** -- Bottom-up from evidence only. No theoretical chains.
6. **Remediation** (optional)
7. **References** (optional)

### PoC Selection Guide

| Bug type | Best PoC format |
|---|---|
| Simple request/response | Raw HTTP (Burp Repeater paste) |
| Needs auth context | curl with -H "Cookie: ..." |
| Visual (XSS alert, UI render) | Screenshot + the request that produced it |
| Timing / race condition | Script (minimal, commented) + raw requests |
| Multi-step chain | Numbered steps + script as supporting artifact |

Do not wrap in a script unless it is genuinely needed. For a bug provable in one or two requests, a raw request beats a Python script -- the triager can replay it directly without reading, trusting, or running code.

---

## Platform Format Selection

Always match the submission platform structure.

### HackerOne

```
# <Title>

## Summary

## Affected Code

## Reproduction

## Impact

## Suggested Fix

## Notes
```

### YesWeHack

**Metadata fields** (fill in the submission form):
- **Scope** -- affected in-scope asset (domain, URL, APK, repo)
- **Host** -- specific host/endpoint (e.g. api.target.com)
- **Bug Type** -- CWE (e.g. CWE-79: XSS, CWE-200: Information Exposure)
- **Vulnerable Part** -- specific file, endpoint, or component (e.g. /api/v1/users)
- **Parameter** -- affected parameter name (e.g. user_id, redirect_url)
- **Payload** -- the payload used in PoC
- **CVSS** -- severity vector and score (e.g. CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)

**Description body** (free text, copy-paste into Bug Description field):

```
## DESCRIPTION

## EXPLOITATION

## POC

## RISK

## REMEDIATION
```

### Section Mapping (HackerOne <-> YesWeHack)

| HackerOne | YesWeHack |
|---|---|
| Summary | DESCRIPTION |
| Reproduction | EXPLOITATION |
| Affected Code + proof | POC |
| Impact | RISK |
| Suggested Fix | REMEDIATION |
| Notes | fold into POC or RISK |

---

## Mode 2 -- Triage (self-validate before submission)

Trigger: hunter says "triage this", "is this ready to submit?", "check my draft", or pastes a draft report.

**Required inputs:**
- The draft report (markdown or plain text)
- The program scope page and rules of engagement

If either is missing, ask for it. Do not guess scope from a domain name.

### Output Format

Return only this structure. Omit sections that are empty (except VERDICT and What's good):

```
VERDICT: [READY TO SUBMIT | NEEDS FIXES | DO NOT SUBMIT]

## Critical (blocks submission)
- [issue] --> [fix]

## Major (needs fixing)
- [issue] --> [fix]

## Minor (cleanup)
- [issue] --> [fix]

## What's good
- [things to keep]
```

### Triage Checklist (run in order)

**1. Scope**
- CRITICAL: Asset not in the in-scope list or matching wildcard.
- CRITICAL: Staging / preview / dev environment not explicitly listed.
- CRITICAL: Vuln class excluded by the program (missing headers, SPF/DKIM/DMARC, self-XSS, logout CSRF, clickjacking on non-sensitive pages, rate-limit without impact, raw scanner output).
- CRITICAL: Testing violated rules (DoS, mass PII download, credential bruteforce, account spam, social engineering).
- MAJOR: Severity claimed exceeds the program cap for this class.
- MAJOR: Gray-area asset not explicitly listed -- recommend pre-approval or add a boundary note.

**2. Evidence**
- CRITICAL: Impact claimed is not proven in the PoC (theoretical chain).
- CRITICAL: PoC cannot be replayed by a triager with zero prior context.
- MAJOR: Key details missing (endpoint, parameter, payload, request, response).
- MAJOR: Session tokens or PII not redacted; or values fabricated.
- MINOR: PoC is a script when raw requests would suffice.

**3. CVSS / Severity**
- MAJOR: Score inflated by mechanism rather than proven impact.
- MAJOR: AC:L claimed on a non-enumerable identifier (random UUID, HMAC, opaque token) -- should be AC:H.
- MAJOR: "Session theft" claimed with HttpOnly cookie.
- MAJOR: "Account takeover" claimed without a PoC that literally takes over an account.
- MAJOR: "Mass data breach" claimed from a single self-owned resource read.

**4. Anti-Slop**
- MAJOR: Multi-paragraph OWASP intro present.
- MAJOR: Generic mitigation phrases like "validate user input" without specifics.
- MINOR: CWE ID repeated in the report body (platform renders it from the form).
- MINOR: Polished discovery narrative with no failed attempts or friction.

**5. Duplicate check**
- MAJOR: No mention that a duplicate search was performed.

---

## Mode 3 -- Gotchas (per-class checks)

Trigger: automatically when a report claims a specific vulnerability class. Apply only the matching section.

---

### XSS

**Minimum proof**
- JS execution on target origin (alert(document.domain) proves it; alert(1) does not prove origin).
- Injection context stated: HTML body / attribute / JS / CSS / URL / JSON.
- Type stated: reflected / stored / DOM.

**Common N/A (likely rejected)**
- alert(1) on null origin, sandboxed iframe, data: / blob: URL.
- Self-XSS (requires victim to paste payload themselves).
- HTML injection without JS execution, unless tied to a demonstrated attack.
- XSS via a Markdown / template renderer the target does not actually use.
- javascript: href requiring the victim to manually paste the URL.

**Overclaim traps**
- "Session theft" claim but cookie is HttpOnly -- JS cannot read it.
- "Account takeover" without a PoC that actually takes over an account.
- "CSP bypass" without showing the CSP header and the bypass technique.

---

### SQLi

**Minimum proof** (one of)
- Data extraction: sentinel value, table name, DB version returned.
- Time-based: controlled SLEEP(n) payload, multiple runs at varying n.
- Boolean-based: controlled true/false oracle with response differential.

**Common N/A (likely rejected)**
- WAF blocked the payload -> "SQLi confirmed". The WAF blocked; that is the end of the proof.
- Error message mentioning SQL without controlled injection.
- Generic HTTP 500 on quote characters.
- DB banner / version leaked without proving injection.

**Overclaim traps**
- "Full database compromise" without dumping a controlled sentinel row.
- Do NOT escalate into destructive post-exploitation to "prove" impact. Prove the primitive, describe the impact, stop there. Dumping the DB, chaining to xp_cmdshell, or writing files breaches most program rules.

---

### SSRF

**Minimum proof**
- Inbound request observed on hunter-controlled endpoint (Burp Collaborator, webhook.site, or hunter's server). Include the inbound log.
- For blind SSRF: time-based confirmation with multiple controlled hosts.
- Reach demonstrated: at least one of internal hostname, cloud metadata (169.254.169.254), localhost service, or protocol smuggling (file://, gopher://, dict://). Collaborator hit alone is not enough.
- Response data exfiltrated if claimed (show the internal endpoint content).

**Common N/A (likely rejected)**
- DNS resolution only -- proves lookup, not HTTP request.
- Blind SSRF to attacker-controlled domain only, no reach demonstrated.
- SSRF to public domains only.
- Request blocked by WAF / library / network policy.

**Overclaim traps**
- "Cloud metadata access" without showing the metadata response body.
- "Internal network scan" without one successful internal hit.
- Blind SSRF claimed High/Critical without demonstrated reach -- typically Low or N/A.

---

### IDOR / BOLA

**Minimum proof**
- Two hunter-controlled accounts, A and B.
- Account A reads / modifies / deletes a resource belonging to B.
- Response containing B's data shown, with B's identifier visible.

**Common N/A (likely rejected)**
- Sequential / predictable IDs without showing actual unauthorized access.
- Reading own data via someone else's ID (same effective access level).
- Resources that are public by design.
- Admin endpoints accessible only to admins.

**Overclaim traps**
- "Mass account takeover" without showing the takeover primitive on B.
- Single-account "discovery" with cross-tenant impact claims but no second tenant tested.
- Non-guessable identifier (random UUIDv4, HMAC, long opaque token) scored as if IDs were enumerable -- score AC:H and state where the ID would leak from.

---

### CSRF

**Minimum proof**
- Working PoC HTML page (hosted or pasted in full) that, when visited by an authenticated victim, performs the sensitive action.
- The action must be sensitive: state change, privilege grant, data modification -- NOT logout, NOT search.
- SameSite cookie status verified -- Lax blocks most cross-site POSTs; the PoC must work despite it.

**Common N/A (likely rejected)**
- CSRF on logout, search, or other low-impact actions.
- "No CSRF token present" without showing exploitation works.
- SameSite=Lax/Strict cookies blocking the cross-site request.

**Overclaim traps**
- "Account takeover via CSRF" without a chain that actually takes over.
- Rating severity by the CSRF mechanism rather than the action. CSRF on a reversible, low-value state change is Low even with a perfect PoC. High requires a genuinely sensitive action: email/password change, fund transfer, privilege grant, deletion of victim data.

---

### RCE

**Minimum proof** (one of)
- In-band command output (id, whoami, hostname).
- Out-of-band callback to hunter-controlled endpoint with a unique payload-specific marker.
- Injection point and payload shown literally.

**Common N/A (likely rejected)**
- "Suspicious behavior on payload submission" without command execution.
- Stack trace mentioning system() / exec() without controlled execution.
- Theoretical RCE via a vulnerable dependency without proving reachability in the application's code path.

**Overclaim traps**
- "Full server compromise" without showing the privilege level. Prove execution with a harmless marker (id, whoami, hostname, or OOB callback) and stop. Do NOT pivot, escalate privileges, move laterally, read other users' data, or run destructive commands.
- "RCE" that is actually code injection in a sandboxed context (sandboxed template engine, browser-side eval -- that is XSS, not RCE).

---

### SSTI

**Minimum proof**
- Template syntax confirmed ({{7*7}} -> 49, <%=7*7%> -> 49, etc.).
- Template engine identified (Jinja2, Twig, Velocity, Freemarker, ...).
- Sandbox escape shown if the engine is sandboxed.
- For RCE impact: apply RCE minimum proof above.

**Common N/A (likely rejected)**
- HTML / text reflection of {{7*7}} as a literal string (no evaluation).
- Math eval in a sandboxed expression engine without an escape path.

**Server-side vs client-side**
- {{7*7}} -> 49 in a client-side framework (Angular, Vue) is CSTI, not SSTI. Different class, different impact, different report.

---

## Style

- Start with the core bug, not background.
- Use short paragraphs.
- Put commands in fenced code blocks.
- Put source snippets in fenced code blocks.
- Use bullets for affected paths and suggested fixes.
- Avoid marketing language and certainty beyond proof.

## Title Pattern

```
<Specific vulnerable component> lets <attacker type> <security impact>
```

Examples:
```
Exported Android MainActivity lets third-party apps force PIA VPN connect/disconnect through shortcut actions
Signed precompute codes can be replayed across unrelated flag groups to override flag values
Reflected XSS in /search via the q parameter lets unauthenticated attackers execute JS in victim sessions
```

## Validation Boundary Phrases

Use one when appropriate:

```
No live service, customer data, payment flow, or production account data was tested.
```
```
This report is based on local source review and a local unit-test reproduction.
```
```
This was validated against the official release APK manifest and matching source code.
```

## Final Submission Checklist

Before submission, verify:

- [ ] Asset selected is exactly in-scope
- [ ] Weakness / CWE matches root cause
- [ ] Severity matches proof, not mechanism
- [ ] CVSS AC vector matches ID discoverability
- [ ] Impact claimed is backed by evidence in the PoC
- [ ] PoC is reproducible by a triager with zero prior context
- [ ] Issue is not merely exposed public key material (Sentry, Firebase, Google, analytics, SDK)
- [ ] Attachment matches platform requirements
- [ ] Duplicate search was performed
- [ ] Report does not disclose secrets or private user data
- [ ] Session tokens and PII are redacted in all screenshots and requests
