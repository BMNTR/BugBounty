# Crypto Audit — Deep Workflows

Companion to SKILL.md. Algorithm review, randomness, key management, TLS.

## Step 1: Algorithm red-flag sweep

```bash
rg -niE "md5|sha1(?![0-9])|des-|rc4|blowfish|ecb" src/ --glob '!*test*'
rg -niE "PBKDF2.{0,20}(1000|5000|10000)|iterations?\s*[:=]\s*(1000|5000)" src/
```

```text
Red flags table:
MD5/SHA1            integrity only; never passwords/signatures
DES/3DES-single/RC4 broken legacy ciphers
ECB mode            pattern leakage (encrypt sample, look for repeats)
Static IV / zero IV with CBC
PBKDF2 < 100k iter, or unsalted fast hashes for passwords
RSA PKCS1v1.5 encryption (prefer OAEP); RSA <2048 bits
JWT HS256 shared secrets < 32 bytes entropy
```

## Step 2: Randomness review

```bash
rg -nE "Math\.random|random\.randint|time\(\).*seed|srand\(" src/
rg -nE "SecureRandom|crypto_rng|OsRng|getrandom|secrets\." src/
# Token generation paths MUST use CSPRNG. Trace reset-token/OTP/session-id
# generation end-to-end; predictability = account takeover class.
```

## Step 3: Key management checks

```text
- Hardcoded keys/secrets in source or config committed to repo
- Same key across environments (staging artifact == prod key)
- Keys derivable from public values (hash of username as AES key)
- No rotation mechanism; keys older than policy horizon
- IV reused across messages with same key under CTR/CBC
```

## Step 4: Protocol-level review

```text
MAC-then-encrypt ordering issues (padding oracle exposure)
Missing AEAD tag verification path (GCM tag ignored?)
Nonce counter reuse risk in CTR/GCM under concurrency
Signature verification: does it verify over RAW bytes the attacker sent?
Canonicalization before verify (XML DSig wrapping, JWT header confusion)
```

## Step 5: TLS posture

```bash
testssl.sh --quiet https://target.example.com | grep -E "VULN|FAIL|WARN"
# Check: TLS1.0/1.1 enabled, weak suites (CBC-SHA1, RC4), cert chain,
# HSTS absence, OCSP stapling.
```

## Step 6: Practical oracle tests (where live testing is in scope)

```text
Padding oracle: submit manipulated ciphertexts; time/error diffing across
  ~2 requests/byte max on YOUR OWN session token only.
ECB detection: encrypt crafted multi-block plaintext of repeated pattern;
  inspect output block equality via API behavior that echoes ciphertext.
Hash length extension: services using md5/sha1(secret||data) MAC scheme;
  extend your own valid request — hashp/hash_extender tools.
```

## False-positive elimination

1. Weak algorithm flagged must be REACHABLE for security decisions, not
   dead code or non-security checksum use.
2. Confirm library defaults vs explicit choices (many wrappers harden).
3. For oracle claims: statistical evidence table required, not one hit.

Report via assets/report-template.md.
