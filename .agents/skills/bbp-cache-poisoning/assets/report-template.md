# Cache Poisoning Finding — Report Template

```markdown
## Web Cache Poisoning via unkeyed <X-Forwarded-Host> on <path>

**Severity**: High (CVSS 7.5)
**Asset**: https://target.example.com/ (CDN: <provider>, cache key excludes header)
**Type**: CWE-444 HTTP Semantic Misinterpretation / Cache Poisoning

### Primitive

Header `X-Forwarded-Host` is reflected into the response but excluded
from the cache key:

```bash
curl -s -H "X-Forwarded-Host: attacker.tld" \
  "https://target.example.com/?cb=1" | grep -o 'src="https://attacker.tld[^"]*"'
# -> <script src="https://attacker.tld/analytics.js">
```

### Poisoning proof

1. Request WITH header + unique buster -> stored (X-Cache: MISS then HIT).
2. Fresh browser WITHOUT header receives attacker-controlled script URL
   (screenshot evidence/poison_hit.png, two different networks).
3. Payload was passive marker only; no real visitor traffic intercepted.

### Impact

- Persistent JS execution context on the site's main origin for all
  visitors hitting the poisoned cache node until TTL expiry (~<TTL>s).
- Enables credential capture, redirect, defacement at CDN scale.

### Remediation

1. Remove X-Forwarded-* trust at app layer unless from known proxy IPs;
   normalize at the edge instead.
2. Include security-sensitive headers in cache key or vary on them.
3. Restrict caching of HTML responses carrying reflected input.
4. Add CDN config tests to CI (unkeyed-input regression suite).
```
