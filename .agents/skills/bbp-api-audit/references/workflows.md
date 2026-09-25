# API Audit — Deep Workflows

Companion to SKILL.md. OWASP API Top 10 matrix, discovery, replay testing.

## Step 1: API surface discovery

```bash
# Docs endpoints (try each):
/swagger.json /v2/swagger.json /v3/api-docs /openapi.json /api-docs
/swagger-ui/ /swagger-ui.html /doc /docs /redoc

curl -s https://target.example.com/v3/api-docs | jq '.paths | keys'

# Shadow APIs from JS bundles:
grep -rEho '"/(api|v[0-9])/[a-z0-9/_-]+"' *.js | sort -u
# From wayback:
gau target.example.com 2>/dev/null | grep -E '/(api|v[0-9])/' | sort -u
```

## Step 2: Per-endpoint test matrix (run for EVERY endpoint)

```text
[BOLA]     swap object IDs across two accounts; path/body/query variants
[BFLA]     call admin operations with low-priv token
[BOPLA]    add unexpected fields: isAdmin, role, verified, price, owner_id
[AUTHN]    drop/expire/garble token; token from other env (staging?)
[RATE]     read X-RateLimit-* headers; burst 2x limit on OTP/login;
           check per-IP vs per-account keying
[INPUT]    type confusion: string->array, int->object, huge payloads,
           JSON depth, duplicate keys {"id":1,"id":2}
[SSRF]     url/webhook/avatar fields -> OOB probe
[MAPPING]  HTTP verbs: GET on /users/1 vs PUT/PATCH/DELETE same path;
           method override headers (X-HTTP-Method-Override)
```

## Step 3: Two-account BOLA replay loop

```bash
# A owns object 101, B owns 102.
for id in 101 102; do
  curl -s -H "Authorization: Bearer $TOK_A" \
    https://target.example.com/api/v1/orders/$id -o resp_$id.json
done
diff <(jq . resp_101.json) <(jq . resp_102.json)
# If A receives B's data -> BOLA. Repeat write ops (PATCH/DELETE) LAST and
# only against objects you own.
```

## Step 4: Mass assignment field probing

```bash
BASE=$(curl -s .../me -H "Authorization: Bearer $T")
echo "$BASE" | jq .        # note ALL returned fields incl internal ones
# Replay PATCH echoing back EVERY field modified to privileged values:
curl -X PATCH .../me -H "Authorization: Bearer $T" -H "Content-Type: application/json" \
  -d '{"email":"me@x.tld","plan":"enterprise","is_staff":true,"credit":999}'
# Success signal: response echoes new values OR downstream behavior changes.
```

## Step 5: Rate-limit & enumeration checks

```text
OTP/login/reset: count attempts until block; measure window reset.
Keying tests: same account different IPs; same IP different accounts.
Response diffing for user enumeration: login vs reset error wording,
timing differences (hash verification skip on unknown user).
```

## False-positive elimination

1. BOLA: confirm with FRESH tokens twice; some caches leak stale data.
2. Rate limits: distinguish soft warnings (headers) from real blocks.
3. Mass assignment: verify persistence (GET after PATCH), not just echo.

## Severity guidance

BOLA on PII: High (8.x). Admin op reachable by user role: High/Critical
by blast radius. Missing rate limit alone: usually Medium unless money/auth.
Use assets/report-template.md.
