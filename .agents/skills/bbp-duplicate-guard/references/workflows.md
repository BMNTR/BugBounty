# Duplicate Guard Workflows

Search strategy and decision tree for dedupe checks before investing validation
hours. Complements SKILL.md's pre-deep-dive check list; this file adds the concrete
query patterns, the decision tree, and the duplicate-vs-variant rules.

## When to Run

- **Mandatory**: after a candidate finding is confirmed reproducible, before writing the report.
- **Early pass** (5-minute version): when choosing between multiple candidates, run
  Stage 1 only on each to rank by novelty.

## Stage 1: HackerOne Disclosures (5 minutes)

Platform dorks (works in any search engine):

```text
site:hackerone.com "target.com" xss
site:hackerone.com "target.com" "subdomain takeover"
site:hackerone.com/hackreports "api.target.com"
site:bugcrowd.com/disclosures target.com
```

If the program has public disclosures, browse its reports page filtered by your
vuln class and skim titles first - most duplicates die at title level:

```text
https://hackerone.com/<program>/hackreports?order_field=report_id&vuln_type=<id>
```

Note the vuln type IDs you need once per program; they are stable.

## Stage 2: Google Dorks for Writeups (3 minutes)

```text
"target.com" bug bounty writeup <vuln-class>
"target.com" "<endpoint-path>" vulnerability
"<program-name>" disclosed report <year>
intext:"target.com" intitle:"writeup|disclosure|responsible disclosure"
site:medium.com OR site:infosecwriteups.com target.com <vuln-class>
```

A public writeup describing your exact bug means it is already known even if never
fixed - triagers will mark it duplicate or informative.

## Stage 3: GitHub Dorks (4 minutes)

```text
# issues/PRs in the target's own repos
org:<target-org> is:issue <component-name>
repo:<target-org>/<repo> <vuln-keyword>

# leaked discussion of the bug elsewhere
"<target.com>" "<unique error string from the PoC>"

# known CVE coverage when the finding is a library issue
"<library-name>" "<version>" CVE
```

The unique-error-string trick is the highest-precision query in this whole skill:
paste an error message or path that ONLY appears in your finding. Any hit = someone
already walked this road.

## Stage 4: CVE / GHSA Check (2 minutes, library findings only)

```bash
searchsploit <library> <version>
# NVD: https://nvd.nist.gov/vuln/search/results?query=<product>&search_type=all
# OSV: https://api.osv.dev/v1/query -d '{"package":{"name":"<lib>","ecosystem":"npm"}}'
```

Version comparison rule from SKILL.md applies: vulnerable range must include the
exact deployed version. `>=` boundaries matter; check the fixed-version field.

## Dedupe Decision Tree

Run in order at each node; follow YES branches first:

```text
Q1. Does an existing report/writeup describe the SAME endpoint/component?
    NO  -> novel so far -> continue to Q3
    YES -> Q2

Q2. Does it also name the SAME root cause?
    NO  -> VARIANT. Different root cause on same component = new report.
           Cite prior report as related context.
    YES -> Q2b. Same impact chain too?
           YES -> EXACT DUPLICATE. Stop. Record reference, move to next candidate.
           NO  -> PARTIAL. New report must prove the NEW impact explicitly.

Q3. Is the vuln CLASS reported before on the same asset but different location?
    NO  -> proceed with full confidence.
    YES -> still valid, but expect faster triage skepticism:
           lead the report with what makes this instance distinct.

Q4. Is the underlying behavior INTENDED functionality misused?
    (rate limits, missing security headers, logout CSRF...)
    YES -> check program exclusions before spending ANY more time.
    NO  -> proceed.
```

## What Counts as Duplicate vs Variant vs New

| Situation | Verdict |
|-----------|---------|
| Same root cause + same asset, reported 2 years ago, unfixed | Duplicate (known issue) |
| Same endpoint, XSS via different sink (reflected param vs stored JSON) | Variant - reportable |
| IDOR on `/users/{id}`, later found same flaw on `/orders/{id}` | Variant if separate code paths; duplicate if one shared authorization middleware bug |
| Same CVE class, different service instance not covered by prior fix | Variant - verify fix scope first |
| Prior report closed as Informative/N/A | Not a true duplicate, but cite it and explain why yours differs materially |
| Your finding needs a 2-step chain where prior was single-step | New - the chain IS the contribution |

## Recording Results

Save every completed check to
`programs/<slug>/evidence/<finding-slug>/duplicate-check.md`:

```markdown
# Duplicate Check - <finding-slug>

Date: YYYY-MM-DD
Candidate: <one-line description>
Asset: <in-scope host/path>

## Searches performed
- H1 disclosures: query=<...>, results reviewed=<N>, relevant hits=<list or none>
- Google dorks: queries used=<...>, hits=<...>
- GitHub: org/repo queries=<...>, hits=<...>
- CVE/GHSA: applicable yes/no, result=<...>

## Closest match found
Report/URL: <link>
Overlap: <same endpoint / same class / ...>
Difference: <root cause / impact / location>

## Verdict
[ ] exact-duplicate  [ ] variant  [ ] no-match
Reasoning: <2 sentences>
```

Rules of thumb:

- A verdict of "no-match" requires at least Stages 1-3 executed and recorded.
- Citing the closest match inside your report (as related work) builds triager trust
  and preempts a lazy duplicate closure.
- If two candidates tie in severity, prefer the one whose duplicate-check came back cleaner.
