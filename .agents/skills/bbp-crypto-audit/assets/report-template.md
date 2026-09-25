# Crypto Finding — Report Template

```markdown
## Cryptographic Weakness: <algorithm/usage> in <component>

**Severity**: High/Medium per exploitability (CVSS 5.x-8.x)
**Asset**: repo/service, component path
**Type**: CWE-327 / CWE-330 / CWE-326

### Weak pattern found

```python
# src/auth/tokens.py:31
digest = hashlib.md5(secret + payload).hexdigest()   # MAC via raw hash
token = f"{payload}.{digest}"
```

Issues: MD5 (broken), naive secret-prefix MAC (length-extension class),
non-constant-time string comparison at line 44.

### Exploitability analysis

Length extension demonstrated LOCALLY with own captured token:
appended `&admin=1` with valid continuation digest using hash_extender;
server accepted (verification code path reached — debug log line cited).

### Impact

Attacker holding any valid token can forge arbitrary authorized payload
extensions without knowing the secret.

### Remediation

1. Replace with HMAC-SHA256 (`hmac.new(key, msg, hashlib.sha256)`).
2. Compare with `hmac.compare_digest`.
3. Rotate existing secrets; invalidate outstanding tokens.
4. Add vector tests rejecting extended-token fixtures.
```
