---
name: bbp-auth-bypass
description: Specialized skill for finding Authentication, Authorization, and Identity vulnerabilities including IDOR, OAuth flaws, and JWT attacks.
---

# Authentication & Authorization Bypass Skill

This skill provides methodologies for attacking identity and access management controls.

## Workflow

### 1. Insecure Direct Object Reference (IDOR) / BOLA
- **Discovery:** Identify endpoints that use incremental IDs (e.g., `user_id=1234`, `/api/orders/5678`).
- **Testing Methodology:**
  1. Create two accounts (Attacker and Victim).
  2. Capture a request from the Attacker account modifying or reading a resource.
  3. Change the resource ID in the request to match the Victim's resource ID.
  4. If the request succeeds and affects the Victim's data, it's an IDOR.
- **Bypass Techniques:**
  - Add arrays: `{"id": [1234, 5678]}`
  - Wildcards: `{"id": "*"}`
  - Parameter pollution: `?id=1234&id=5678`
  - Wrap in objects: `{"id": {"id": 5678}}`
  - Change request method: Convert `POST` to `PUT` or `PATCH`.

### 2. JSON Web Token (JWT) Attacks
- **Analysis:** Decode the JWT at `jwt.io` to understand the payload structure.
- **Exploitation:**
  - **None Algorithm:** Change the algorithm header (`alg`) to `none` and remove the signature part of the token.
  - **Key Confusion (RS256 to HS256):** If the server expects an asymmetric key (RS256) but accepts a symmetric algorithm (HS256), sign the token using the public key as the symmetric secret.
  - **Weak Secrets:** Try brute-forcing the secret key using tools like `hashcat` with the `rockyou.txt` wordlist.
  - **JFK (JSON Web Key) Injection:** Inject a malicious key via the `jwk` or `jku` header parameters.

### 3. OAuth 2.0 & SSO Vulnerabilities
- **Implicit Grant Flow:** The access token is returned in the URL fragment (`#access_token=...`). Susceptible to leakage via `Referer` headers or open redirects.
- **CSRF on Authorization (State Parameter):** If the `state` parameter is missing or not validated, an attacker can link their own social account to the victim's profile.
- **Redirect URI Manipulation:** Alter the `redirect_uri` parameter to point to an attacker-controlled server to steal the authorization code. Bypass filters by appending paths (`https://target.com.attacker.com`) or using directory traversal (`https://target.com/callback/../../attacker.com`).

### 4. Password Reset & Account Takeover (ATO)
- **Host Header Injection:** Alter the `Host` header or inject `X-Forwarded-Host: attacker.com` during password reset. The generated reset link might point to the attacker's domain, leaking the token when clicked.
- **Email Parameter Pollution:** Inject multiple emails: `email=victim@a.com&email=attacker@a.com`. The token might be sent to both.
- **Token Predictability:** Analyze the entropy of the reset token. If it's a short numeric PIN or a predictable timestamp hash, brute-force it.
