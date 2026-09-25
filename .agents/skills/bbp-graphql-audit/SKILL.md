---
name: bbp-graphql-audit
description: Specialized skill for auditing GraphQL APIs, including endpoint discovery, introspection and its bypasses, schema analysis, authorization (BOLA) testing on queries/mutations, batching abuse, and mutation exploitation. Use during authorized bug bounty work against in-scope GraphQL endpoints.
version: "2.0"
---

# GraphQL Audit Skill

Methodology for attacking modern GraphQL APIs: discover the endpoint, map
the schema (with or without introspection), then test authorization,
injection, and batching/alias abuse on every operation.

## When to Use

- Recon found `/graphql`, `/api/graphql`, `/v1/graphql`, `/graphiql`,
  `/altair`, `/playground` or any endpoint accepting `application/json`
  POST with a `query` field
- JS bundles reference graphql clients (Apollo, urql, Relay) or `.graphql`
  query strings
- Target exposes subscriptions over WebSocket

## Prerequisites

- Burp + InQL extension; graphw00f; clairvoyance (schema recovery)
- Two accounts for BOLA tests
- The bundled helper: `python scripts/graphql_recon.py --url ...`

## Workflow

### Step 1: Endpoint & Engine Discovery

```bash
# Fingerprint engine + detect endpoint (graphw00f)
wsl graphw00f -f -t https://target.example.com

# Common paths to probe (POST {"query":"{__typename}"})
# /graphql /graphiql /api/graphql /api/graphiql /v1/graphql /v2/graphql
# /graphql/console /gql /service/graphql /index.php?graphql=true
curl -s -X POST https://target.example.com/api/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __typename }"}'
```

### Step 2: Introspection (and bypasses when blocked)

```bash
# Full introspection dump via InQL or:
python scripts/graphql_recon.py --url https://target.example.com/api/graphql \
  --introspect --out schema.json
```

If disabled, try in order (see references/workflows.md for full payloads):

1. Different content types (`application/graphql`, form-encoded)
2. GET-based introspection with query params
3. Probing fields via error suggestions: `Did you mean 'user'?` ->
   feed to **clairvoyance** to rebuild the schema offline
4. Field-level probes using `__typename` on known object names

### Step 3: Schema Analysis

From the dumped schema, build an attack queue:

| Look for | Why |
|---|---|
| Queries taking ID args | BOLA candidates |
| Mutations (create/update/delete) | authz + mass assignment |
| Fields named admin/internal/token/email/ssn | info disclosure |
| Deprecated-but-present fields | often lack new auth checks |
| Circular relations (user->posts->user) | depth/alias abuse potential |

Visualize with GraphQL Voyager if available.

### Step 4: Authorization Testing (BOLA/BFLA)

For EVERY query/mutation with an identifier, replay as User A requesting
User B's objects:

```bash
curl -s -X POST https://target.example.com/api/graphql \
  -H "Authorization: Bearer $TOKEN_A" -H "Content-Type: application/json" \
  -d '{"query":"query { user(id: 102) { id email phone ssn } }"}'
```

Also test:
- Unauthenticated access to authenticated operations
- Operation-level auth gaps (mutation callable by low-priv role)
- Object-level gaps inside collections (`orders { items { user {...} } }`)

### Step 5: Mutation Exploitation

```bash
# Mass assignment: add fields not present in the UI's mutation
-d '{"query":"mutation { updateProfile(input:{bio:\"x\", isAdmin:true}) { ok } }"}'

# Cross-type injection where input types are loosely validated
# Test every mutation twice: once as owner, once as non-owner
```

### Step 6: Batching / Alias Abuse (low-volume, no DoS)

Keep request counts tiny — prove the flaw, do not stress the service.

```graphql
# Rate-limit evasion via aliases (single request, many operations)
mutation {
  l1: login(user:"admin", pass:"guess1") { token }
  l2: login(user:"admin", pass:"guess2") { token }
}

# Same-object alias duplication reveals missing per-operation limits
query { o1: order(id:1){total} o2: order(id:1){total} }
```

Detect batching support by sending `[{"query":"..."},{"query":"..."}]` as a
JSON array once. If both answers return, batching is ON -> flag it.

### Step 7: Injection & Misc

- SQLi/NoSQLi through typed arguments (strings reach resolvers)
- SSRF via URL-typed fields (image/avatar URLs)
- XSS stored via string fields rendered in dashboards
- Subscriptions: connect via WS unauthenticated; subscribe to other users'
  channels if channel names are guessable
- CSRF: state-changing mutations without CSRF tokens when cookie-authed
  (`Content-Type` sniffing, SimpleRequest POST forms)

### Step 8: Report

Use `assets/graphql-report.md`. Include full request/response pairs per
finding; never include DoS-scale evidence.

## Key Concepts

| Concept | Description |
|---------|-------------|
| Introspection | Self-describing schema query; often disabled in prod |
| BOLA | Object access without ownership check inside resolver |
| Aliases | Multiple operations of same field in one request |
| Batching | JSON array of queries processed server-side in one call |
| Persisted queries | Pre-registered hashes; arbitrary queries may be rejected |

## Tools

| Tool | Purpose |
|------|---------|
| InQL (Burp) | Introspection dump, query templates |
| graphw00f | Engine fingerprinting |
| clairvoyance | Schema recovery from suggestion errors |
| GraphQL Voyager | Schema relationship visualization |
| scripts/graphql_recon.py | Endpoint probe + introspect + suggest-leak |

## Output Format

Evidence under `programs/<slug>/evidence/`; report via
`assets/graphql-report.md`.
