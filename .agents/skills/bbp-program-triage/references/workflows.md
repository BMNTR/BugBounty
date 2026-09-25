# Program Triage Workflows

Scoring rubric and decision procedure for deciding whether a bug bounty program
deserves hours. Use before running any recon. Complements the workflow + output
format defined in SKILL.md.

## Scoring Rubric

Score each dimension 0-5. Total 25 points. Nothing gets scored without reading
the actual policy page - assumptions score zero across all dimensions.

| Dim | Question | 0 points | 5 points |
|-----|----------|----------|----------|
| S1 Scope breadth | How many distinct assets can you actually test? | 1 vague wildcard | multiple web apps + APIs + mobile/source, clearly listed |
| S2 Exclusion hygiene | How hostile is the exclusion list? | excludes everything interesting (no auth testing, no rate limit changes at all, no subdomain takeover, no automated scanning) | short list of genuinely dangerous things only |
| S3 Bounty sanity | Are payouts real for realistic bugs? | $50-$300 top range or "swag" | mid-tier >= $500 for medium XSS/IDOR-class bugs |
| S4 Asset freshness | Is the attack surface alive and changing? | parked pages, stale stack | active releases, changelogs, new features shipping |
| S5 Payout history | Do researchers actually get paid? | no disclosed reports ever | regular disclosures with awarded amounts visible |

Weighting: multiply by importance for your goals - typical weights
S1 x2, S2 x2, S3 x1, S4 x1, S5 x1 (max weighted = 35).

Verdict thresholds:

- **>= 24**: strong program. Start passive recon immediately.
- **15-23**: workable. Pick the single best asset; timebox first session.
- **8-14**: weak. Only worth it if you have unique access (source invite, private scope).
- **< 8**: skip. Log why so future-you does not re-evaluate.

### Dimension details

**S1 Scope breadth.** Count asset types, not just lines in scope table.
`*.target.com` alone with zero exclusions beats five domains behind a wall of rules.
Source code / open-source scope scores high for local-validation hunters; live-only
web scope scores high for web hunters. Match to your skill set.

**S2 Exclusion red flags.** These specific exclusions are time-wasters:

```text
"any findings requiring automated scanning"      -> kills your entire toolchain
"subdomain takeover"                             -> removes the highest-signal easy class
"rate limiting / lack thereof"                   -> most-reported noise class, but banning
                                                    ALL rate-limit testing hints at hostile triage
"self-XSS", "CSRF on non-sensitive actions"       -> normal, fine
"anything not explicitly listed as in-scope"     -> default-deny scope, very slow
```

Also check the exclusion list for the two classic large-company rejects noted in
root AGENTS.md lessons: missing anti-clickjacking without sensitive action PoC,
and banner/version/header disclosure. If those dominate their past rejections,
expect low acceptance odds generally.

**S3 Bounty table sanity.** Red flags: critical ceiling under $500; "bounties paid
at our discretion"; VDP-style language ("we offer recognition") inside a bounty
program listing. Green flags: published CVSS-to-dollar mapping; separate mobile/API
tables; recent increases.

**S4 Asset freshness.** Check release notes, app store version history, changelog,
recent subdomains (`new-`, `beta-`, `api-v2`). A stale surface means every bug was
found years ago.

**S5 Historical payouts.** On HackerOne check disclosed report count and median award;
on Bugcrowd check leaderboard activity; on YesWeHack check public stats. Zero
disclosures after 3+ years usually means either dead program or brutal duplicates -
both bad.

## Decision Checklist

Run top to bottom; stop at first "no":

1. [ ] Policy read completely (including FAQ - exclusions hide there)?
2. [ ] At least one asset I am technically equipped to test?
3. [ ] Account/KYC/Signal requirements satisfiable right now? (If blocked -> record and exit.)
4. [ ] No forbidden technique overlaps my planned methodology?
5. [ ] Scope list contains zero ambiguous entries affecting my target choice?
6. [ ] Scored >= 15 weighted total?
7. [ ] Duplicate-guard quick pass shows the surface is not strip-mined already?

Passing 1-7: create `programs/<slug>/` workspace, fill bb.toml, start Workflow C of
bbp-program-orchestrator.

## Time-Waster Red Flags

Programs matching these get logged as "skip" regardless of other scores:

- **Info-only scope**: entire scope limited to information disclosure classes.
- **VDP trap**: titled like a bounty program but policy says recognition/no monetary.
- **Discretionary payment language** combined with a history of $0 closures.
- **KYC + Signal + invitation walls** when you cannot satisfy them today.
- **Default-deny scope** ("only what is explicitly listed") where the list has one SPA.
- **Aggressive legal posture**: mandatory dedicated researcher agreements, background checks.
- **Ghost programs**: last response SLA breach measured in months per their own stats page.

## Worked Scoring Example

Program X: wildcard `*.x.com` + one API, exclusions ban automated tools entirely,
critical ceiling $1,500, app store shows monthly releases, 60 disclosed reports
with visible awards.

```text
S1 Scope breadth      = 3  (one broad wildcard + API; no mobile/source)
S2 Exclusion hygiene  = 2  ("no automated scanning" kills the standard pipeline;
                            manual-only methodology required)
S3 Bounty sanity      = 4  (realistic mid-tier numbers)
S4 Asset freshness    = 5  (monthly releases)
S5 Payout history     = 4  (steady disclosures)
Weighted: 3x2 + 2x2 + 4x1 + 5x1 + 4x1 = 25 -> WORKABLE
```

Interpretation: proceed, but plan a manual-first session (ffuf/nuclei only on
explicitly permitted targets, or skip to pure manual testing). The S2=2 penalty
changes methodology, not the verdict alone - that is the point of weighting.

## Account & Access Handling Flow

```text
Policy requires login?
  -> create researcher account yourself if allowed; never use borrowed/shared accounts
  -> record test-account credentials in local vault, NEVER in evidence folders

Policy requires Signal/KYC/invite?
  -> cannot satisfy right now -> mark BLOCKED in triage-notes.md with the exact
     requirement text -> re-check quarterly

Program issues dedicated test accounts after approval?
  -> wait for provisioning before ANY authenticated request
  -> unauthenticated surface may be tested while waiting if policy allows
```

## SLA Interpretation

Response metrics printed on the program page predict how your report will be treated:

- First-response median > 30 days -> expect long silences; batch findings instead
  of reporting each immediately.
- High closure rate as Informative/N/A -> read 10 closed reports before drafting
  yours; learn their exact acceptance bar.
- Bounties paid within days of triage -> healthy; single high-quality report beats
  five rushed ones.

## Recording the Verdict

Record the verdict in `programs/<slug>/reports/triage-notes.md` using the exact output
format from SKILL.md (Verdict / Best target / Needs account / Safe first checks /
Do not test / Next action) plus the rubric scores, e.g.:

```text
S1=4 S2=3 S3=4 S4=2 S5=4  weighted=29 -> STRONG
```

## Re-Triage Triggers

A previously skipped or deprioritized program moves up the queue when any of these change:
scope additions announced, bounty table raised, new asset type added (mobile/source),
or a fresh disclosure wave proves triage is responsive again. Re-run this rubric fully -
do not carry old scores over.
