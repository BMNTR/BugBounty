# Subdomain Takeover — Report Template

```markdown
## Subdomain Takeover: <subdomain> (dangling <provider> record)

**Severity**: High/Critical (CVSS 7.5-9.1 depending on impact path)
**Asset**: <subdomain>.target.com
**Type**: Subdomain Takeover / Improper DNS Record Management
**OWASP**: A05:2021 Security Misconfiguration

### Evidence 1 - Dangling DNS record

```
$ dig +short CNAME <subdomain>.target.com
<vendor-host>.<provider-domain>
$ dig +short A <subdomain>.target.com
(no answer)
```

### Evidence 2 - Vendor fingerprint

Screenshot: fingerprint_screenshot.png showing vendor response:

```
<body snippet matching provider "unclaimed resource" signature>
```

### Evidence 3 - Resource claim PoC (only if policy permits)

Screenshot: poc_marker.png showing the subdomain serving the authorized
marker page after claiming `<resource-name>` on <provider>.

### Impact

- An attacker can serve arbitrary content on a subdomain of target.com,
  enabling phishing that is indistinguishable from legitimate infrastructure.
- Parent-domain cookies scoped to `.target.com` are readable/overwriteable.
- OAuth/Social login flows using redirect URIs under this subdomain can be
  hijacked to steal authorization codes/tokens (if applicable, demonstrate).
- CSP/report-uri or CORS policies referencing this subdomain degrade.

### Remediation

1. Remove the dangling CNAME for `<subdomain>` pointing to
   `<vendor-host>` immediately.
2. Inventory ALL third-party records (CNAME/TXT/MX/NS) and validate each
   against live resources; add monitoring for future deprovisioning drift.
3. Where supported, use service-side custom-domain verification (e.g., AWS
   Certificate Manager validation, Azure custom domain TXT validation) so
   unclaimed names cannot be re-bound.

### Reproduction steps (numbered, exact)

1. dig CNAME ... (output above)
2. curl https://<subdomain>/ -> vendor error page (screenshot)
3. Register `<resource-name>` on <provider> [policy note if skipped]
4. Publish marker page; screenshot served content at https://<subdomain>/
5. Deprovision claimed resource after evidence capture
```
