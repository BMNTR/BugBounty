# RSocket Testing — Deep Workflows

Companion to SKILL.md. Framing, rsc CLI, routing authz gaps.

## Step 1: Locate RSocket endpoints

```text
- WebSocket upgrade paths: /rsocket, /ws, /streaming
- TCP ports beside HTTPS on app servers (6000-7000 range, custom)
- Spring apps: check JS bundles for RSocketClient / rsocket-js imports;
  config keys spring.rsocket.server.* in leaked env/actuator
```

## Step 2: Handshake with rsc CLI

```bash
# Install rsocket-cli (rsc) per upstream docs; then:
rsc ws://target.example.com/rsocket --stream --route greet --data "hi"
# Frames to expect in Burp (WS tab): SETUP then METADATA_PUSH/REQUEST_x
# Composite metadata format: message/x.rsocket.routing.v0 + auth entries.

# Raw metadata crafting (base64 of routing table):
echo -n "payments.refund" | base64   # embed as routing metadata tag 0x01
```

## Step 3: Route enumeration oracle

```bash
# Unknown route vs known route differ in error frame:
for r in user.profile admin.list payments.refund internal.debug; do
  echo "== $r"
  timeout 8 rsc ws://target/rsocket --request --route "$r" \
    --data '{}' --metadataMimeType message/x.rsocket.routing.v0 \
    --dataMimeType application/json 2>&1 | head -3
done
# ApplicationError text leaks handler existence; map ALL routes this way.
```

## Step 4: Interaction model abuse matrix

For each discovered route test all models:

```text
REQUEST_RESPONSE   normal call
REQUEST_FNF        fire-and-forget -> often SKIPS auth interceptors; state changes!
REQUEST_STREAM     streaming pull beyond authorized page size
REQUEST_CHANNEL    bidirectional; test server push after cancel
METADATA_PUSH      global metadata writes if permitted (document only)
```

FNF is the classic gap: no response channel means some security handlers
never run. Verify via observable side effects through a legit read route.

## Step 5: Auth metadata checks

```text
- Simple auth metadata (user:pass base64) sent on CONNECT vs per-request?
- Does SETUP without credentials still allow FNF routes? (common bypass)
- JWT-in-metadata: tamper alg/claims like HTTP JWT flows.
- Connection reuse: can one authenticated connection's channel be shared
  across principals by replaying frames with different routing tables?
```

## False-positive elimination

1. Confirm route execution via STATE CHANGE observed on legitimate path,
   not error-text differences alone.
2. Distinguish app-level AccessDenied (secured) from connection-level
   rejects that simply indicate wrong framing.
3. Re-test after reconnect — some setups cache authorization per session.

## Remediation guidance

```java
// Spring pattern: enforce at socket level for every interaction type
RSocketInterceptor security = ... // deny unless principal has role for route
RSocketFactory.receive().addSocketAcceptorPlugin(security)...
```

Deny-by-default + explicit route table + tests asserting anonymous FNF
rejection. Use assets/report-template.md for findings.
