# Evidence Workbench Workflows

Concrete procedures for naming, hashing, capturing, and packaging evidence under
`C:\BugBounty\programs\<slug>\`. Complements the folder layout and rules in SKILL.md.

## Folder Placement Rules (from root AGENTS.md)

Non-negotiable mapping - memorize once, apply forever:

| File type | Destination |
|-----------|-------------|
| subdomain lists, nuclei/ffuf/httpx raw output | `programs/<slug>/recon/` |
| screenshots, HTTP dumps, PoC files per finding | `programs/<slug>/evidence/<finding-slug>/` |
| draft + final reports (.md) | `programs/<slug>/reports/` |
| scratch: session dumps, UI XML, APK artifacts, traffic logs | `programs/<slug>/temp/` |
| shared session files (`cookies.txt`) | `C:\BugBounty\temp\` or program temp |
| global utility scripts | `C:\BugBounty\_scripts\` |
| target-specific scripts | `programs/<slug>/scripts/` |

Never write to root, Desktop, Downloads, or any path outside
`C:\BugBounty\programs\<target-name>\` (except the two `_scripts`/`temp` exceptions).

## File Naming Conventions

Pattern: `<date>-<finding-slug>-<artifact-type>.<ext>` with date first so directory
listings sort chronologically:

```text
2026-08-24-idor-orders-endpoint-request.txt
2026-08-24-idor-orders-endpoint-response.txt
2026-08-24-idor-orders-endpoint-poc.png
2026-08-24-xss-search-param-poc.mp4
```

Artifact type vocabulary (keep it closed):

```text
request / response / poc / payload / log / screenshot / notes / metadata
```

Rules:

- Slugs are lowercase kebab-case, max ~40 chars.
- No spaces, no special characters, ASCII only - these files cross platform and
  tool boundaries (zip, WSL paths, upload forms).
- One finding = one folder; never mix findings inside one evidence folder.
- Raw tool output that supports no specific finding stays in `recon/`, not evidence.

## Hashing Evidence (Chain of Custody)

Hash every artifact when a finding folder is finalized. PowerShell:

```powershell
Get-ChildItem "programs\<slug>\evidence\<finding>" -File |
  Get-FileHash -Algorithm SHA256 |
  Format-Table Hash, Path -AutoSize
```

Write the output into `MANIFEST.txt` in the same folder. The helper script
`scripts/hash_evidence.py` in this skill does exactly this (plus sizes and
timestamps) for one or more folders - use it to avoid manual copy errors.

Why it matters: file CreationTime/LastWriteTime plus SHA256 give you forensic
evidence if an originality dispute ever arises (AGENTS.md lesson 6). Hash BEFORE
uploading anything anywhere; note the hash of the final zip too.

## Screenshot Capture Standards

A screenshot is evidence only if it proves the claim unaided:

1. Full browser window visible including address bar with the exact URL.
2. Payload/result visible in frame - annotate with rectangles or arrows, never crop out context.
3. System clock in frame is nice-to-have; filename date prefix covers timestamp needs.
4. For request/response pairs, prefer raw HTTP dump (.txt) PLUS screenshot of the
   rendered effect - text survives review tools better than images.
5. Videos (for YWH forms): under 60 seconds, start already showing the URL bar,
   narrate nothing, let the PoC run visibly end-to-end.

Tooling: `gowitness` batch shots during recon go to `recon/screenshots/`; only
shots backing a promoted finding get copied into its evidence folder.

## Chain-of-Custody Notes

Every finding folder gets `metadata.txt` (format from SKILL.md) plus these custody lines:

```text
Captured by:   <researcher alias>
Capture date:  <YYYY-MM-DD HH:MM TZ>
Environment:   <local lab | live in-scope asset | release binary | source checkout>
Integrity:     SHA256 manifest present (MANIFEST.txt), hashed at <time>
Alterations:   none | redaction applied on <file> at <time> (secret masking only)
Storage:       local workspace only until submission; uploaded copies listed below
Uploads:       <platform>: submitted <date>, attachment names <...>
```

Redactions are allowed ONLY for secret masking (show first 4 + last 4 chars) and
third-party personal data removal. Record every redaction in the Alterations line -
an undisclosed edit discovered later destroys credibility.

## Packaging for Submission

HackerOne-style (archive accepted):

```powershell
$src = "programs\<slug>\evidence\<finding>"
Compress-Archive -Path "$src\*" -DestinationPath "$src\<finding>-poc.zip" -Force
Get-FileHash "$src\<finding>-poc.zip" -Algorithm SHA256 | Format-List
```

Zip contents checklist:

```text
README.md            what each file shows, in reading order
command-log.txt      exact commands executed, in order
request.txt          raw HTTP request(s)
response.txt         raw response excerpt(s)
poc.png / poc.mp4    visual proof if applicable
MANIFEST.txt         hashes + timestamps
metadata.txt         custody block from above
```

Exclusions - NEVER inside a package: cookies, tokens, real credentials, third-party
user data, internal-only hostnames outside scope, your own client secrets unrelated
to the finding.

YesWeHack-style (image/video-only forms): upload the single best visual, paste all
code and commands into the report body itself, keep local archive for your records.

## Final Verification Pass

Before declaring evidence complete:

- [ ] every file opens and matches its name
- [ ] MANIFEST hashes regenerate correctly against current files
- [ ] zero credentials/secrets in any included text
- [ ] redactions recorded in metadata.txt
- [ ] zip re-downloads and extracts cleanly (test after upload if platform allows)
