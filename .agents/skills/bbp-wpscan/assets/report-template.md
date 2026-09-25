# WordPress Finding — Report Template

```markdown
## WordPress Plugin XSS/SQLi/RCE (<plugin> <version>): <summary>

**Severity**: High (CVSS 7.6-8.8)
**Asset**: https://target.example.com/wp-content/plugins/<plugin>/
**Type**: CWE-79 / CWE-89 / CWE-434 in third-party WordPress component

### Fingerprinting

```bash
wpscan --url https://target.example.com -e vp --plugins-detection aggressive
# -> <plugin> version <Y> detected via readme.txt / asset query strings
curl -s ".../plugins/<plugin>/readme.txt" | grep -i "Stable tag"   # confirms Y
```

### Vulnerability reproduction

(Per advisory class — fill exact request/response pair.)

```
GET /wp-admin/admin-ajax.php?action=<vuln_action>&id=1%20AND%201=1
-> row set differs vs 1=2 (boolean-based, 3-run consistent)
```

Screenshot: evidence/wppoc.png.

### Impact

Unauthenticated attacker can <read any user's submissions / extract DB
rows including user hashes>. Bounded to demonstrated read of own rows.

### Remediation

1. Update plugin to >= fixed version immediately.
2. If unfixed: deactivate and remove plugin; find maintained alternative.
3. Add WAF rule for the specific action/parameter until patched.
4. Audit other sites in fleet for same plugin/version.
```
