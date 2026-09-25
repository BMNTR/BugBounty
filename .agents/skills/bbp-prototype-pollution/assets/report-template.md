# Prototype Pollution Finding — Report Template

```markdown
## Server-Side Prototype Pollution leading to <gadget impact>

**Severity**: High (CVSS 8.x per gadget outcome; Critical if RCE proven)
**Asset**: POST https://target.example.com/api/settings/import
**Type**: CWE-1321 Improperly Controlled Modification of Object Prototype Attributes

### Pollution primitive

```json
POST /api/settings/import
Content-Type: application/json

{"__proto__":{"status":555}}
```

Verification: subsequent GET /health returns HTTP 555 globally for all
users (default response status inherited from polluted Object.prototype).

### Gadget exploitation

```json
{"__proto__":{"body":"UNAUTHORIZED_ACCESS_MARKER"}}
```
All JSON error responses across the API now render attacker-controlled
body -> stored content-spoofing and cache poisoning chain demonstrated on
one cached URL (evidence: poisoned_cache.png, purged after capture).

### Impact

- Global response manipulation affecting every API consumer.
- Realistic abuse: phishing-quality content injection under valid TLS origin.

### Remediation

1. Upgrade <merge/query library> past fixed version; disable deep merge
   of user JSON.
2. Sanitize keys: reject `__proto__`, `constructor`, `prototype` at input
   validation boundary (all depths).
3. Consider Object.create(null) maps for sensitive config objects.
```
