---
name: bbp-evoting-crypto-audit
description: Specialized skill for auditing e-voting cryptographic models. Use when testing systems like modern e-voting platforms to analyze individual/universal verifiability, mixnets, shuffle proofs, zero-knowledge proofs, and bulletin board integrity.
---

# E-Voting Cryptographic Audit

## Objective
Analyze and identify vulnerabilities in the specialized cryptographic protocols used in electronic voting systems. Standard TLS/signing audits (`bbp-crypto-audit`) are insufficient for the unique threat model of e-voting, which must guarantee both absolute ballot secrecy and absolute tally integrity.

## RoE / Scope Reminder
**CRITICAL:** Only test domains and source code explicitly listed in the program's IN-SCOPE configuration. Cryptographic auditing is primarily a source code and mathematical review task. Do not attempt to sabotage live election servers or interfere with active voting processes. Provide reproducible, mathematical proofs or specific code execution paths for any reported vulnerabilities.

## Core Concepts & Threat Models

### 1. Individual Verifiability (Cast as Intended)
- **Concept:** A voter can verify that the system correctly recorded their specific vote, usually via a Return Code.
- **Audit Focus:** Can an attacker (e.g., a malicious voting client/browser) alter the vote without changing the Return Code presented to the voter? Is the mapping between the choice and the Return Code securely established?

### 2. Universal Verifiability (Counted as Cast)
- **Concept:** Anyone (voter or external auditor) can cryptographically verify that all recorded votes were correctly decrypted and tallied without manipulation.
- **Audit Focus:** Review the mathematical proofs generated during the tally. Is it possible to forge a valid proof for an invalid tally?

### 3. Mixnet & Shuffle Proofs
- **Concept:** Ballots are encrypted. Before decryption, a mixnet shuffles the ballots to break the link between the voter and the ciphertext, ensuring secrecy.
- **Audit Focus:** Review the Zero-Knowledge Proof (ZKP) of the shuffle. Can a malicious mix node silently drop, duplicate, or modify a ballot without invalidating the ZKP? Is the randomness generation secure?

### 4. Zero-Knowledge Proofs (ZKP) & Control Components
- **Concept:** ZKPs are used to prove statements (e.g., "this ballot contains a valid option", "this shuffle is correct") without revealing the underlying data.
- **Audit Focus:** Review the implementation of the Fiat-Shamir heuristic. Are all inputs properly bound in the hash challenge? A missing variable in the hash can allow a prover to cheat.

### 5. Bulletin Board Integrity
- **Concept:** The public append-only log where encrypted votes and proofs are published.
- **Audit Focus:** Can an attacker delete or alter an entry on the bulletin board? Are digital signatures properly verified before accepting new entries?

## Auditing Approach
1. **Specification vs Implementation:** Always compare the formal cryptographic specification (often a PDF or academic paper) against the actual implementation in code (Java, Rust, etc.). Vulnerabilities almost always exist in the gap between the two.
2. **Library Misuse:** E-voting often relies on specific libraries (e.g., BouncyCastle). Look for insecure instantiations, side-channel vulnerabilities (timing attacks), or improper parameter validation.
3. **Random Number Generation:** Ensure `SecureRandom` is used exclusively. Predictable randomness destroys ZKPs and encryption schemes.

## Validation Checklist
- [ ] Has the specific cryptographic protocol (e.g., specific Mixnet type) been identified?
- [ ] Are all Zero-Knowledge Proofs correctly implementing the Fiat-Shamir heuristic (all parameters included in the challenge hash)?
- [ ] Is there a clear separation of trust (e.g., Control Components operated by different entities)?
- [ ] Can the mathematical vulnerability be proven with a practical code snippet or exploit script?
