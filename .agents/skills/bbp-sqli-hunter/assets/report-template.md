# SQL Injection Finding — Report Template

```markdown
## SQL Injection: <endpoint + parameter>

**Severity**: High/Critical (CVSS 9.1 if full DB read; 8.6 read-only subset)
**Asset**: https://target.example.com/item?id=1
**Type**: CWE-89 Improper Neutralization of Special Elements used in an SQL Command

### Fingerprint

- Context: numeric parameter, no quotes required
- DBMS: MySQL (confirmed via extractvalue error surfacing version())
- Technique proven: boolean-based + error-based (time-based also works)

### Minimal reproduction

Truthy vs falsy pair with stable diff:

```
GET /item?id=1 AND 1=1     -> HTTP 200, item "Widget A" rendered
GET /item?id=1 AND 1=2     -> HTTP 200, "item not found" variant
```

Data extraction proof (single value, non-destructive):

```
GET /item?id=1 AND extractvalue(1,concat(0x7e,version()))
-> XPATH syntax error: '~8.0.34'
```

Screenshot: evidence/sqli_version.png. sqlmap session:
programs/<slug>/temp/sqlmap/ (log included).

### Impact

- Authenticated-nothing read of database content demonstrated for the
  users table email column (3 rows shown as proof, then stopped).
- Path to full PII dump is trivial from here (same query pattern).

(Do not claim card data/passwords without extracting YOUR OWN row only.)

### Remediation

1. Parameterized queries / prepared statements everywhere (no string concat).
2. Allowlist validation on numeric IDs (`intval` + range check).
3. Least-privilege DB account for app runtime.
4. Disable verbose SQL errors to clients; log server-side with alerting.
```
