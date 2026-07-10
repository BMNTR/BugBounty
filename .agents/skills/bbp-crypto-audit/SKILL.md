---
name: bbp-crypto-audit
description: Review cryptographic implementations in authorized bug bounty targets. Use when the target uses custom crypto, implements TLS, handles certificates, performs signing/verification, generates random numbers, stores secrets, or processes encrypted data. Covers algorithm choice, implementation flaws, protocol issues, and key management.
---

# BBP Crypto Audit

## Check Categories

### Algorithm Choice
- Weak/deprecated algorithms: MD4, MD5, SHA-1, RC4, DES, 3DES, ECB mode.
- Export-grade ciphers: 40/56-bit keys, DHE_EXPORT, RSA_EXPORT.
- Non-standard or homegrown crypto.

### Implementation Flaws
- Constant-time comparison for HMAC/ signatures (timing oracle via `==` or `!=`).
- Padding oracle: CBC mode with PKCS#7 padding, error messages revealing padding validity.
- IV reuse: static IV, counter reuse in CTR/GCM mode.
- Nonce reuse in ChaCha20-Poly1305 or AES-GCM.

### Protocol Issues
- TLS version downgrade (allow TLS <1.2).
- Certificate validation: skipping hostname check, accepting self-signed, expired.
- Mixed content: HTTPS page loading HTTP resources.
- JWT algorithm confusion: `alg: none`, RS256→HS256 key confusion.

### Key Management
- Hardcoded keys/secrets in source or config.
- Key reuse across environments or purposes.
- Weak key derivation (low PBKDF2 iterations, fast hash for passwords).
- Entropy: weak `rand()` usage, predictable seeds.

## Tools

```bash
# TLS scanning
nmap --script ssl-enum-ciphers -p 443 <target>
testssl.sh <target>

# JWT inspection
python3 -c "import jwt; jwt.decode(<token>, options={'verify_signature': False})"
```

## Evidence

Save as:

```text
C:\BugBounty\programs\<program>\evidence\<finding>/
```

Include: relevant code snippets, tool output, impact assessment.
