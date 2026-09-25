# Report Writer Workflows

Assembly procedure from validated finding to submission-ready report. Complements
the core rules, platform formats, and title pattern in SKILL.md - this file covers
the workflow order, severity justification math, impact narrative rules, and
platform quirks in depth.

## Assembly Workflow

Run these 7 steps strictly in order. Skipping ahead is how reports get inflated.

### Step 1: Freeze the evidence

- Finding folder complete per bbp-evidence-workbench (request, response, PoC, manifest).
- Re-run the exact PoC command once more immediately before drafting; endpoints die.
  If it no longer reproduces, stop - draft nothing until you know why.
- Duplicate check saved (`duplicate-check.md`) with a verdict.

### Step 2: Pick the title (formula-driven)

Base formula from SKILL.md:

```text
<Specific vulnerable component> lets <attacker type> <security impact>
```

Variants that triagers accept well:

```text
<IDOR|SQLi|SSRF> in <component> allows <attacker type> to <impact>
Unauthenticated <action> on <endpoint> exposes <data class>
<Privilege level> user can <forbidden action> via <parameter/mechanism>
Stored XSS in <field> executes in <victim context> when <trigger>
Race condition in <operation> enables <double-spend/duplicate-state outcome>
```

Title tests: does it name the asset component? the attacker precondition? the
consequence? If any of the three is missing or vague ("Security issue in portal"),
rewrite.

### Step 3: Draft Summary and Reproduction from artifacts only

Write Reproduction by transcribing your frozen `command-log.txt` - not from memory.
Every step must be independently runnable by a triager who has never seen your setup:
exact URLs, exact payloads, account prerequisites stated up front.

Summary = 3-4 sentences: what + where + who can do it + why it matters. No history,
no speculation, no "I noticed that maybe".

Quality contrast for the Summary section:

```text
WEAK : "While exploring the target I noticed an endpoint that might have a
        security issue with authorization which could potentially be dangerous."
STRONG: "GET /api/v2/invoices/<id> returns any tenant's invoice without an
         ownership check. Any authenticated free-tier user can read paid-tier
         invoices by iterating numeric IDs. Confirmed across 5 sampled IDs
         using two researcher accounts."
```

The weak version forces triagers to do the analyst's job; the strong version can
be triaged in one read.

### Step 4: Severity justification with CVSS

Build the vector honestly, then let the calculator produce the score. Do not pick a
score first and reverse-engineer the vector. Common honest mappings:

```text
Unauthenticated read of sensitive data, no user interaction:
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N          -> 7.5 High

Authenticated low-priv IDOR affecting other users' data:
CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N           -> 6.4 Medium

Stored XSS hitting other users (self-XSS alone is NOT this):
CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N           -> 5.4 Medium

Reflected XSS requiring victim click:
CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N           -> 6.1 Medium

Server-side RCE / metadata credential theft:
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N            -> 10.0 Critical

Blind SSRF with confirmed internal reach but no data returned:
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N            -> 5.8 Medium
```

Rules: `S:C` requires actual privilege-boundary crossing across security scopes -
do not set Changed scope because it raises the score. If AC depends on luck or
user configuration, use `AC:H` and accept the lower score. The program's own
severity matrix overrides CVSS when they conflict - check it before submitting.

### Step 5: Impact narrative rules

Structure every Impact section as an attacker-path chain:

```text
Step 1: attacker does X (proven by PoC)
Step 2: which yields Y (proven)
Step 3: enabling Z (either proven, or written as "likely enables...; not validated")
```

Honest-math rules:

- Quantify with what you measured: "listing exposed ~40 backup objects" beats "massive data exposure".
- Never claim customer-data access, payment impact, or server compromise unless the PoC shows exactly that.
- Chained findings: each link must be individually demonstrated in the same report.
- If business context is unknown (e.g., what the leaked tokens unlock), state the assumption explicitly instead of asserting.
- One vulnerability per report; mention related issues as "also present" only if same root cause.

### Step 6: Platform formatting

HackerOne markdown quirks:

- Standard markdown works: headers, lists, fenced code blocks, bold/italic.
- Tables render but wide tables wrap badly - keep tables under ~5 columns.
- Inline HTML is stripped/unreliable - never rely on `<img>` tags; upload images via attachment UI.
- Consecutive blank lines collapse; use single blank lines between sections.
- Long unbroken strings (tokens, vectors) can overflow mobile view - break them manually.
- Reference attachments by filename in text so reviewers connect them ("see `response.txt`").
- Severity/CVSS go into form fields AND state them once in the body for context.

YesWeHack: fill structured metadata fields first (Scope, Host, Bug Type/CWE,
Vulnerable Part, Parameter, Payload, CVSS) then paste the free-text body using the
DESCRIPTION/EXPLOITATION/POC/RISK/REMEDIATION section names - mapping table is in SKILL.md.

### Step 7: Checklist gate

Run the Final Submission Checklist in SKILL.md verbatim. Then one extra human pass:

- Read the whole report aloud once; anything you would not say to a senior engineer gets cut.
- Confirm the validation boundary sentence appears somewhere real (Impact or Notes).
- Confirm zero secrets in every code block (grep your own draft for `AKIA`, `eyJ`,
  `sk_live`, password fields).

## Anti-Patterns That Get Reports Closed

- "Impact could potentially potentially lead to full compromise" chains with no proof links.
- Reporting missing security headers / banner disclosure as standalone findings.
- Public client-side SDK keys as the entire finding (SKILL.md rejection rule).
- Rate limiting absence without demonstrated abuse consequence in scope.
- Copy-pasted generic remediation ("implement input validation") instead of a specific fix.
- Title says Critical, body proves Medium - instant credibility loss.

## Revision Discipline

When triagers ask questions, update the report body itself (append "Update <date>:"),
not just comment threads, so the report stays self-contained after resolution.

## Post-Submission Communication Rules

- Answer triager questions with artifacts (raw request/response), never with restated claims.
- If asked to prove higher impact you did not test, either do it safely within scope
  or reply with the validation boundary - do not improvise a claim under pressure.
- Severity disputes: respond once, with the CVSS vector breakdown and the program's
  own severity matrix line item; then accept the outcome. Arguing three rounds burns
  reputation that outlasts the report.
- Fix verification: retest with the ORIGINAL PoC command from your frozen log; if it
  still reproduces after "resolved" closure, reopen with the fresh response attached
  and a new timestamp.

## Attachment Ordering Convention

Reviewers read top-down. Order attachments so the story reads without explanation:

```text
1. poc.png / poc.mp4        <- the visual payoff first
2. request.txt              <- what to send
3. response.txt             <- what comes back proving it
4. command-log.txt          <- full session for reproducers
5. MANIFEST.txt             <- integrity metadata, last
```

Name them so alphabetical order matches reading order where the platform sorts by name.
