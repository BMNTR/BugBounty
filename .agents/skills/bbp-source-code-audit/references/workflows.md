# Source Code Audit — Deep Workflows

Companion to SKILL.md. SAST tooling, sink hunting, taint tracing.

## Step 1: Repo recon

```bash
ls; cat README*; find . -maxdepth 2 -name "*.yml" | head   # CI pipelines
git log --oneline -20                                       # recent focus areas
find . -name "*.env*" -not -path "*/node_modules/*" | head
# Dependency manifests:
ls package.json requirements.txt go.mod pom.xml build.gradle Cargo.toml 2>/dev/null
```

## Step 2: Automated baseline

```bash
semgrep --config auto --json -o semgrep.json .
codeql database create db --language=<lang> && codeql database analyze db \
  --format=sarifv2.1.0 --output=codeql.sarif <queries-suite>
pip-audit -r requirements.txt ; npm audit --json ; cargo audit
gitleaks detect --source . --report-path leaks.json
```
Treat findings as LEADS; verify each manually before reporting.

## Step 3: Sink hunting by language (ripgrep)

```bash
rg -n "eval\(|exec\(|system\(|popen|child_process" --type py --type js
rg -n "query\(.*\+|execute\(.*\+|raw\("            # SQL string concat
rg -n "redirect\(.*request\.|open\(.*request\."     # open redirect / SSRF-ish
rg -n "pickle\.loads|yaml\.load\(" --type py        # unsafe deserialization
rg -n "render_template_string|innerHTML\s*="        # XSS sinks
rg -n "os\.path\.join\(.*,.*request"                # traversal joins
```

## Step 4: Taint tracing methodology (manual)

```text
1. SOURCE: enumerate request entry points (routes, handlers, parsers).
2. PROPAGATION: follow variable through assignments/calls; note sanitizers:
   - ORM parameterization = SQL safe
   - escape/html encode = XSS-safe for that context ONLY
   - allowlist validators = strong; blocklists = weak
3. SINK: does it reach dangerous API with attacker control intact?
4. EXPLOITABILITY: auth required? second-order? encoding layers?
Document source->sink path as file:line chain for the report.
```

## Step 5: Authz logic review patterns

```bash
rg -n "@login_required|@permission_required|requireAdmin|can\(" 
# Find endpoints MISSING decorators among similar siblings:
diff <(rg -o '@\w+\(' routes/admin.py | sort) <(rg -o '@\w+\(' routes/api.py | sort)
# IDOR: look for direct model.get(id) without owner filter:
rg -n "\.get\(.*_id|filterBy.*id=" models/ controllers/
```

## Step 6: Secrets & config hygiene

```bash
rg -niE "(api[_-]?key|secret|password)\s*[:=]\s*['\"][^'\"]{8,}" --no-ignore
git log -p -S "AKIA" | head          # historical key commits
```

## False-positive elimination

1. Every automated hit needs a human-traced taint path or it is noise.
2. Check middleware/guards BEFORE claiming missing authz (global filters).
3. Confirm exploitability against running instance where scope allows.

Report via assets/report-template.md with file:line evidence chains.
