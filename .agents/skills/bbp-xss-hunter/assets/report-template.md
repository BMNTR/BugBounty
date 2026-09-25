# XSS Finding — Report Template

```markdown
## Stored/Reflected/DOM XSS: <location summary>

**Severity**: High (CVSS 8.0+ if stored + admin-rendered; Medium 6.1 for
self-XSS-only unless combined with a delivery vector)
**Asset**: https://target.example.com/<path>
**Type**: CWE-79 Improper Neutralization of Input During Web Page Generation

### Injection context

Reflection lands inside: <HTML body / attribute / JS string / href>
Filter observed: <none / event-handler blocklist / tag blocklist>
Encoding applied by app: <none / HTML-entity on quotes only>

### Minimal reproduction

1. Submit payload into <param>:
```
GET /search?q="><svg onload=alert(document.domain)> HTTP/1.1
Host: target.example.com
```
2. Response contains unencoded reflection:
```
<input value=""><svg onload=alert(document.domain)>">
```
3. Open URL in browser -> alert fires with document.domain = target domain.

Screenshot: evidence/xss_fired.png (address bar visible, console clean).

### Impact

- Session hijack of any user viewing the page: document.cookie accessible
  because HttpOnly is absent on <cookie name> (verify before claiming).
- Admin backoffice rendering of stored value enables blind takeover path.
- Phishing via DOM rewrite under legitimate origin.

(State only what you verified. No cookie? Then impact = arbitrary JS in
origin context, keylogging, action forgery.)

### Remediation

1. Context-aware output encoding (HTML-encode in body, attribute-encode
   in attributes, JSON-serialize in scripts).
2. Sanitize rich input server-side with allowlist parser.
3. Add CSP without unsafe-inline; nonce-based script policy.
4. Set HttpOnly+Secure+SameSite on session cookies as defense-in-depth.
```
