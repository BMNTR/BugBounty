---
name: bbp-rsocket-testing
description: Specialized skill for auditing RSocket protocol implementations. Use when testing modern Java/Spring or reactive microservices that expose RSocket endpoints for potential injection, data leakage, or authorization bypasses.
---

# RSocket Protocol Testing

## Objective
Audit RSocket endpoints which operate on a distinct framing protocol (reactive streams) entirely separate from standard HTTP. Standard HTTP proxies and scanners (like Burp or Nuclei) often fail to parse or inspect RSocket traffic.

## RoE / Scope Reminder
**CRITICAL:** Only test domains, IPs, and ports explicitly listed in the program's IN-SCOPE configuration. RSocket testing can inadvertently cause high load (via Request-Stream/Channel). Avoid aggressive fuzzing. Focus on logic flaws, authorization bypasses, and data validation.

## RSocket Fundamentals
RSocket supports 4 interaction models:
1. **Fire-and-Forget:** Send a single request, no response expected (often used for telemetry/logs).
2. **Request-Response:** Standard 1-to-1 interaction (similar to HTTP).
3. **Request-Stream:** Send 1 request, receive a stream of responses (often used for real-time feeds).
4. **Request-Channel:** Bi-directional stream of requests and responses.

## Auditing Approach

### 1. Connection & Routing
- **Transport:** RSocket can run over TCP, WebSocket, or Aeron.
- **Routing:** Spring Boot uses `metadataPush` or specific routing metadata frames (MimeType: `message/x.rsocket.routing.v0`) to route payloads to `@MessageMapping` handlers.
- **Goal:** Map all available routes by analyzing client-side JS (if WebSockets are used) or decompiling the Java backend.

### 2. Authorization Bypass
- RSocket handlers (`@MessageMapping`) often bypass standard Spring Security HTTP filters.
- **Check:** Are the RSocket endpoints protected by RSocketSecurity? Can an unauthenticated user call an administrative route?

### 3. Payload Injection (Data Validation)
- Payloads are typically JSON or CBOR (MimeType: `application/json` or `application/cbor`).
- **Goal:** Test standard injection vectors (SQLi, NoSQLi, Command Injection, XSS if reflected elsewhere) within the payload frames.

### 4. Denial of Service (DoS)
- Reactive streams can suffer from memory exhaustion if backpressure is not handled correctly.
- *(Note: Do NOT exploit this during Bug Bounty, but you can theoretically point out missing `@Valid` annotations or unbounded stream allocations if source code is available).*

## Tooling
- **RSocket CLI (rsocket-cli):** The `curl` equivalent for RSocket. Use it to send specific frames and interact with the server.
- **Wireshark:** Has a built-in RSocket dissector for inspecting TCP/WebSocket frames.

## Validation Checklist
- [ ] Has the transport mechanism (TCP vs WebSocket) been identified?
- [ ] Have all `@MessageMapping` routes been enumerated?
- [ ] Have authentication/authorization controls been verified on the RSocket level?
- [ ] Have payloads been tested for injection vulnerabilities?
