# Fuzzing Finding — Report Template

```markdown
## <Hidden Endpoint / Parameter / Vhost>: <summary>

**Severity**: Medium-High depending on exposed function (CVSS 5.3-8.x)
**Asset**: https://target.example.com/<discovered-path>
**Type**: CWE-284 / CWE-200 (exposed debug/admin functionality)

### Discovery method

ffuf run (wordlist common.txt, jitter 0.1-0.5s, UA browser-real):

```
GET /<path> -> HTTP 200 (len 4821) vs baseline 404 (len 153)
```
Full log: programs/<slug>/recon/ffuf_dirs.json

### What the endpoint exposes

- <e.g., /internal/debug returns stack traces incl. framework version>
- Auth required? <no / yes-bypassable-via-X>

### Impact

Honest framing: exposure of internal surface expands attack area and may
leak <info>. Do NOT inflate to RCE without proof.

### Remediation

1. Remove/disable <endpoint> in production builds.
2. Deny-by-default routing; explicit allowlist of public paths.
3. Uniform 404 responses (identical body/length) to prevent size oracle.
```
