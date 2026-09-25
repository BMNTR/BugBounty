# Program Orchestrator Workflows

Companion to the 4-phase flow in SKILL.md. This file covers the concrete setup
steps: workspace initialization, scope config handling, execution sequencing,
and progress tracking. Run everything from `C:\BugBounty`.

## Workflow A: Initialize a New Program Workspace

Run this before any recon. It creates the canonical folder structure required by
root AGENTS.md:

```powershell
$slug = "example-target"
New-Item -ItemType Directory -Force -Path "programs/$slug/recon",
  "programs/$slug/evidence", "programs/$slug/reports",
  "programs/$slug/scripts", "programs/$slug/temp" | Out-Null
```

Resulting layout (all future files for this program go inside it):

```text
programs/example-target/
  recon/      subdomain lists, nuclei output, ffuf results, dnsx/httpx raw
  evidence/   screenshots, HTTP dumps, PoC files (.txt/.png/.http), per-finding folders
  reports/    draft and final reports (.md)
  scripts/    target-specific helper scripts only
  temp/       scratch: session dumps, UI XML, APK artifacts, traffic logs
```

Or via the CLI entry point, which does the same plus scope scaffolding:

```powershell
.\orchestrate.ps1 init https://hackerone.com/<program> $slug
```

## Workflow B: Scope Config (bb.toml)

Every program gets a filled copy of `_templates/bb.toml`. Copy first, edit second:

```powershell
Copy-Item _templates\bb.toml "programs\$slug\bb.toml"
```

Minimum fields to fill before any active tool runs:

```toml
[program]
name = "example-target"          # slug used in all paths
platform = "hackerone"           # hackerone | bugcrowd | yeswehack | other
url = "https://hackerone.com/<program>"

[scope]
in_scope = [
  "*.example.com",
  "api.example.com",
]
out_of_scope = [
  "blog.example.com",            # example exclusion rule
]

[rules]
max_rate_limit = 30             # hard ceiling; WAF detection may lower it
allowed_methods = ["GET", "POST"]
forbidden = ["dos", "brute-force", "spam", "social-engineering"]

[contact]
researcher_alias = "<your alias if program requires header>"
```

Scope enforcement rules that apply at every stage:

1. Every discovered domain/IP is checked against `in_scope` AND `out_of_scope` rules.
2. Wildcard entries match subdomains only when explicitly listed.
3. Ambiguous or conflicting scope -> treat as out of scope until clarified.
4. The filter step runs after every enumeration tool, not once at the start.

Filtering pattern used by the pipeline (repeat after each discovery stage):

```bash
# keep only hosts matching in-scope patterns, drop anything matching exclusions
grep -E "(^|\.)example\.com$" allsubs.txt \
  | grep -vE "^blog\.example\.com$" > scoped.txt
```

## Workflow C: Execution Sequencing (Passive-First)

Order matters: passive stages cost nothing and shape everything after them.

```text
[0] init + bb.toml + folders          no target interaction
[1] passive recon                     crt.sh, gau, waybackurls, dorks, Shodan
[2] subdomain enum                    subfinder -all, amass enum -passive
    -> SCOPE FILTER
[3] dnsx resolution                   resolved.txt, takeover-candidates.txt
    -> takeover candidates found? load bbp-subdomain-takeover NOW
[4] httpx probing                     alive.txt with tech-detect
[5] nuclei tiered scan                critical/high first, then medium/low/info
[6] ffuf content discovery            top-value alive hosts only
[7] katana crawl + param harvest      feeds manual exploitation skills
[8] gowitness screenshots             triage aid for alive.txt
```

Decision points between stages:

| After stage | If you see | Do this |
|-------------|-----------|---------|
| [2] | huge subdomain count (>2k) | sample top-value names manually; do not blast all through nuclei |
| [3] | dangling CNAMEs | pause pipeline; validate takeover first |
| [4] | WordPress/Jenkins/Grafana detected | route to bbp-wpscan / actuator / matching skill |
| [5] | any critical hit | stop scanning; manual validation immediately (endpoints die fast) |
| [6] | swagger/openapi/actuator/.git | pivot to API/source/cloud skill; skip rest of ffuf |

## Workflow D: Progress Tracking (state.json)

Write `programs/<slug>/state.json` after every completed stage so any agent can
resume without redoing work:

```json
{
  "slug": "example-target",
  "phase": "recon_done",
  "updated": "2026-08-24T14:30:00Z",
  "scope_checked": true,
  "alive": 42,
  "done": ["init", "passive", "subfinder", "dnsx", "httpx", "nuclei-high"],
  "queue": [
    "ffuf-main-app",
    "validate-nuclei-CVE-hit-on-api.example.com"
  ],
  "findings_open": [
    { "id": "exposed-env-api01", "status": "needs-validation", "severity": "high" }
  ],
  "notes": "WAF=cloudflare on www, rate limit dropped to rl20"
}
```

Conventions:

- `phase`: one of `init`, `recon_running`, `recon_done`, `exploitation`, `reporting`.
- `done` uses exact stage names so re-runs are idempotent.
- `queue` entries name a concrete action + asset, never vague labels.
- Update `updated` timestamp on every write; stale state.json means re-check scope.

## Workflow E: Skill Routing After Classification

Once classification is known (from `classification.json` produced by Phase 1), load
the matching skills exactly as mapped in SKILL.md Phase 2. Always-loaded reference
skills (evidence, report-writer, duplicate-guard, payloads, disclosures) come last so
their context does not crowd out execution skills during long sessions.

## Anti-Patterns

- Running active tools before bb.toml exists and is read.
- Filtering scope only once at the beginning instead of after each discovery stage.
- Writing recon output anywhere except `programs/<slug>/recon/` (root is a clean zone).
- Treating state.json as optional - it is the handoff format between sessions.
- Continuing a full pipeline run after a confirmed critical finding; validate first,
  the queue survives overnight.
