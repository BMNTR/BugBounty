# WAF Bypass Finding — Report Template

```markdown
## Access Control Bypass via spoofable client-IP header on <path>

**Severity**: High (CVSS 7.5) — adjust per exposed function
**Asset**: https://target.example.com/admin (IP allowlisted at edge)
**Type**: CWE-290 Authentication Bypass by Spoofing

### Root cause

Admin route gate reads `X-Forwarded-For` from client-supplied request,
trusting it as source IP.

### Reproduction

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://target.example.com/admin
# 403
curl -s -H "X-Forwarded-For: 127.0.0.1" \
  https://target.example.com/admin | grep -c "<admin-ui-marker>"
# 200 with admin UI rendered
```

Screenshot: evidence/admin_via_xff.png.

### Impact

Any external attacker can reach administrative interface by adding one
header, enabling <describe actual functions found: user listing shown in
response excerpt>.

### Remediation

1. Derive client IP ONLY from the trusted proxy hop immediately adjacent
   to the app; strip client-supplied forwarding headers at edge.
2. Enforce authn/authz on /admin independent of network location.
3. Add regression test: admin route must 403 with arbitrary XFF values.
```
