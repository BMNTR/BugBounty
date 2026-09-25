# Source Code Finding — Report Template

```markdown
## <Vuln Class>: <function> allows <impact> via <source>

**Severity**: High (CVSS 7.x)
**Asset**: repo <name>@<commit sha>, path <file:line>
**Type**: CWE-XXX

### Taint chain

```
SOURCE : src/routes/user.py:42   request.args["file"]
FLOW   : src/services/files.py:88 open(base_dir + name)
SINK   : src/services/files.py:89 send_file(...)
```

Sanitizers checked en route: NONE (only `name` length check at line 41).

### Proof-of-concept (local test)

```
GET /download?file=../config/database.yml
-> returns DB config contents (redacted excerpt attached)
```
Reproduced against local instance built from audited commit.

### Impact

Authenticated low-priv user reads arbitrary files as service account.

### Remediation

1. Resolve final path via `os.path.realpath` and enforce prefix allowlist.
2. Reject separators and `..` segments before join.
3. Add regression test: traversal payloads return 400.

### Verification status

Confirmed live: yes/no (if no, state exactly what blocks live confirmation).
```
