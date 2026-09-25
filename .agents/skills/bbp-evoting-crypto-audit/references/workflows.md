# eVoting Crypto Audit — Structured Review Framework

Companion to SKILL.md. Review questionnaire approach for voting systems
where live testing is rarely authorized; most output is documented
analysis, not exploitation.

## Scope framing (do this FIRST)

```text
Assets: protocol specs, whitepapers, client code, server code, public
bulletin board endpoints, verifier tools.
Out of scope typically: live election manipulation. NEVER attempt to
influence a real election; analysis is on TEST artifacts only.
```

## Pillar 1 — Individual verifiability questionnaire

```text
[ ] Can a single voter confirm THEIR ballot is recorded as cast?
    - Is the receipt unique per ballot yet privacy-preserving?
    - Can a coerced voter fake receipts (re-vote/receipt-freeness)?
[ ] Ballot secrecy vs receipt tension resolved how? (crypto vs policy)
[ ] What exactly does the tracker/hash bind to? (race, choices, nonce)
```

## Pillar 2 — Universal verifiability questionnaire

```text
[ ] Bulletin board append-only? Who can write? Signature on entries?
[ ] Total recorded == total eligible cast? Where enforced?
[ ] Mixnet: how many mixes, who operates them, independent?
    - Per-mix proof type (Chaumian, Bayer-Groth) verified by whom?
    - ElGamal re-encryption key handling between stages
[ ] Tally decryption: threshold t-of-n? Share verification published?
[ ] Are ALL proofs publicly checkable with an open verifier tool?
    - Run the official verifier against PUBLISHED test data yourself.
```

## Pillar 3 — ZK proof soundness questions

```text
[ ] Fiat-Shamir transform: transcript hashed over FULL context or
    partial message? (classic broken-transform bug class)
[ ] Proof reuse across ballots accepted? (nonce/challenge binding)
[ ] Range proofs actually enforce 1 candidate per race? Test with
    crafted ballots in the reference implementation's test harness.
[ ] Trusted setup ceremony: per-election or reused? Toxic waste handled?
```

## Pillar 4 — Bulletin board integrity

```text
[ ] Hash chain linking? Verify chain on sample dataset.
[ ] Signature scheme + key transparency for trustees.
[ ] Replay/rollback detection mechanism.
[ ] Availability model: what happens to votes during partition?
```

## Common real-world failure patterns to check

```text
1. Verifier tool trusts server-provided "proof" without checking math.
2. Mix stage count small enough that one operator breaks privacy.
3. Receipt shows vote content -> coercion market.
4. Client-side tallying trusting server JSON blindly.
5. Challenge not bound to voter+ballot -> proof replay across ballots.
6. Eligibility list vs ballot box mismatch unverified at end.
```

## Reporting format

Findings are ANALYSIS findings: cite spec section + code file:line,
describe attack scenario on paper, rate severity by election-integrity
impact, propose protocol fix. Use assets/report template of crypto-audit
as base, adding an "Election integrity impact" section.
