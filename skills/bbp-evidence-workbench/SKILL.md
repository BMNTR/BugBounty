---
name: bbp-evidence-workbench
description: Organize bug bounty artifacts and proof-of-concept evidence. Use whenever creating, moving, packaging, hashing, or referencing bug bounty files under C:\BugBounty for reports, attachments, screenshots, videos, source excerpts, commands, and reproducible PoCs.
---

# BBP Evidence Workbench

## Folder Layout

Use this layout:

```text
C:\BugBounty\
  programs\
    <program-slug>\
      policy\
      source\
      downloads\
      evidence\
        <finding-slug>\
      reports\
      attachments\
  tools\
  skills\
```

## Evidence Rules

- Keep one folder per finding.
- Pin exact versions and commits.
- Save commands as text files.
- Save source excerpts with paths and line numbers.
- Hash downloaded binaries.
- Keep report drafts separate from raw evidence.
- Name files with readable slugs, not random names.

## Required Metadata

Every evidence folder should contain a short metadata file with:

```text
Program:
Asset:
Finding:
Date:
Researcher:
Validation boundary:
Repository / URL:
Commit / Version:
Local tools:
No live data tested:
```

## Attachment Packaging

For HackerOne or programs that request archives:

- create `.zip` containing PoC code, README, command log, and source excerpts
- avoid unnecessary large files
- do not include secrets, cookies, tokens, or credentials

For YesWeHack forms that only accept image/video:

- upload a concise screenshot or video
- paste code and commands in the report body
- mention local evidence path only in personal notes, not as a required artifact

## Verification Checklist

Before telling the user to submit:

- report body is copy-paste ready
- title matches the actual bug
- impact matches proof
- attachment exists and opens
- no private credentials are included
- no claim exceeds validation
