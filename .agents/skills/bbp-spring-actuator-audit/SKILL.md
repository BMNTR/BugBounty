---
name: bbp-spring-actuator-audit
description: Specialized skill for identifying and exploiting Spring Boot Actuator endpoints. Use when testing Java/Spring applications to find exposed endpoints like /actuator/env, /actuator/heapdump, or /actuator/jolokia that can lead to information disclosure or RCE.
---

# Spring Boot Actuator Audit

## Objective
Detect, interact with, and escalate vulnerabilities arising from exposed Spring Boot Actuator endpoints. This is highly relevant when a reverse proxy (like Apache) misconfiguration exposes internal paths (e.g. `/actuator` or `/manage`).

## RoE / Scope Reminder
**CRITICAL:** Only test domains and IP addresses explicitly listed in the program's IN-SCOPE configuration. DO NOT perform DoS attacks or attempt to overwrite production environment variables unless safe exploitation is verified. Heap dumps MUST be handled securely and deleted after analysis.

## Key Endpoints to Check
Spring Boot Actuator can be exposed on custom paths, but common ones include:
- `/actuator`
- `/actuator/env`
- `/actuator/heapdump`
- `/actuator/jolokia`
- `/actuator/gateway/routes`
- `/actuator/httptrace` (or `/actuator/httpexchanges` in newer versions)
- `/actuator/logfile`

## Exploitation Paths

### 1. Secret Leakage via `/actuator/env`
- **Method:** GET `/actuator/env`
- **Goal:** Look for AWS keys, database passwords, JWT secrets, or API keys.
- **Bypass:** Spring Boot 2.x+ masks secrets by default (e.g., `******`). To unmask, you can sometimes use the `/actuator/heapdump` method.

### 2. Deep Secret Extraction via `/actuator/heapdump`
- **Method:** GET `/actuator/heapdump`
- **Goal:** Download the JVM heap dump (HPROF file) to extract masked environment variables in plaintext.
- **Analysis:** Use Eclipse MAT (Memory Analyzer Tool) or OQL to query strings containing sensitive keys (like password, token, secret).

### 3. Remote Code Execution via `/actuator/jolokia`
- **Condition:** Jolokia library is on the classpath.
- **Method:** POST to Jolokia endpoints to manipulate JMX MBeans.
- **Goal:** Typical vectors include `ch.qos.logback.classic.jmx.JMXConfigurator` (Logback JMX RCE) or `java.lang:type=Memory` manipulation.

### 4. RCE via Spring Cloud Gateway (`/actuator/gateway/routes`)
- **Condition:** Spring Cloud Gateway is used (CVE-2022-22947).
- **Method:** POST a new route to `/actuator/gateway/routes/<id>` with a malicious SpEL expression in the filter.
- **Trigger:** POST `/actuator/gateway/refresh` to trigger execution.

## Tooling
- `projectdiscovery/nuclei-templates/http/misconfiguration/spring-boot/`
- Custom `curl` scripts for structured verification.
- OQL queries for heap dump analysis.

## Validation Checklist
- [ ] Are actuator endpoints exposed directly or via bypasses (e.g., `/..;/actuator/env`)?
- [ ] Are the exposed endpoints leaking sensitive data?
- [ ] Can the heapdump be successfully parsed?
- [ ] Can an RCE vector (Jolokia, SpEL) be triggered non-destructively (e.g., DNS ping/OAST)?
