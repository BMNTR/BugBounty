# BugBounty Agent Rules

## Bug Bounty Rules

- **WSL2 & LINUX ENVIRONMENT AUTHORIZATION**: The active WSL2 distribution (`Ubuntu`) is fully configured and available. Agents are explicitly authorized and encouraged to execute Linux-native security tools, high-speed Bash pipelines (`subfinder | httpx | nuclei`), and Linux-only utilities using `wsl bash -c "<command>"` or `wsl <command>`. Paths under `C:\BugBounty\` map directly to `/mnt/c/BugBounty/` inside WSL.
- **STRICT SCOPE ENFORCEMENT**: Work ONLY on explicitly in-scope assets defined in the program's scope config. You MUST verify every domain, IP, or endpoint against the IN-SCOPE list before running any tools. If it is not explicitly in-scope, or if it matches an OUT-OF-SCOPE rule, DO NOT touch it.
- **MANDATORY SCOPE GATE (RTFS GUARD)**: Before submitting ANY report and before closing/finishing work on a program, you MUST run the scope guard:
  1. Per-finding: `python bbcore/cli.py scope <slug> --check <asset>` — exit code 0 required before drafting the report.
  2. End-of-program: `python bbcore/cli.py scope <slug> --sweep` — must return CLEAN; redact/remove out-of-scope references from artifacts first.
  Skipping this gate is a process violation even if the bug itself is valid.
- Do not perform DoS, brute force, spam, credential stuffing, social engineering, phishing, or testing against other users.
- Do not use leaked credentials or private data.
- Do not fabricate screenshots, runtime results, impact, exploitability, or bounty expectations.
- Prefer local reproduction, source review, release binary inspection, unit tests, and non-destructive PoCs.
- Before reporting, run duplicate checks and confirm evidence exists.
- Do not report exposed public client-side keys by themselves (Sentry DSN, Firebase, Google Maps, analytics, telemetry, SDK keys). Reportable only when proven additional impact exists.
- **AUTOMATED EVIDENCE CAPTURE & VISIBLE POC**: To ensure undeniable visual proof without waiting for manual reproduction, whenever an agent executes a **Final PoC Validation**, it MUST save the raw HTTP request/response to a `.txt` file in `evidence/`. Because some AI agents (like Antigravity) run in isolated background services and CANNOT spawn windows on the interactive desktop, the agent MUST provide the exact command in a code block for the user to copy-paste into their own terminal, or for the user to pass to an interactive agent (like OpenCode). The command MUST use the array syntax: `Start-Process powershell.exe -ArgumentList '-ExecutionPolicy', 'Bypass', '-NoExit', '-File', 'C:\path\to\script.ps1'`.
- **NO EMOJIS IN SCRIPTS**: NEVER use emojis (e.g., 🚀, 📸) in any generated `.ps1`, `.bat`, or source code files. Windows PowerShell 5.1 and certain text encodings will fail to parse them, causing silent crashes or `ParserError`. Use standard ASCII (e.g., `[!]`, `[+]`) for emphasis.
- **STRICT DEFENSIVE PROGRAMMING & NULL GUARDS**: Always write null guards (`Number.isFinite(...)`, `optional chaining`, safe fallbacks) from line 1 of any generated code to prevent bot review complaints (such as Tembo Bot or Greptile). Avoid un-guarded `.toFixed()` or `.slice()` calls.
- **HUMANIZED PR DESCRIPTIONS**: Avoid generic AI templates with cheesy emojis (🐛 🔍 🛠️ 🧪). Write PR descriptions in a clean, direct, human software developer style.
- **IMAGE HANDLING (TEXT-ONLY MODELS)**: Models without native vision (e.g., DeepSeek free tiers) MUST NOT claim to "see" an image. When the user pastes or references an image (screenshot, evidence, chart), use the MCP `vision_describe(path)` or `vision_ocr(path)` tools to extract a text description/OCR result first, then work from that text. The `vision` MCP server lives at `C:\BugBounty\_scripts\vision-mcp.py` and requires `GEMINI_API_KEY` (or `VISION_API_KEY`/`OPENAI_API_KEY`) in `C:\BugBounty\.env`.
- **WORKSPACE HYGIENE — STRICT ENFORCEMENT**: The root `C:\BugBounty` directory is a CLEAN ZONE. The following rules are NON-NEGOTIABLE:

  **Root-level allowed files (do NOT add anything else here):**
  ```
  C:\BugBounty\
  ├── AGENTS.md          ← Agent rules (this file)
  ├── SKILL.md           ← Encyclopedia skill reference
  ├── README.md          ← Project overview
  ├── LICENSE            ← License
  ├── .env               ← Global env vars (API keys, tokens)
  ├── .gitignore         ← Git ignore rules
  ├── manifest.json      ← Skills manifest
  ├── skills-lock.json   ← Skills lock file
  ├── assets/            ← GitHub Banners/Images
  ├── bbcore/            ← Core orchestrator framework
  ├── orchestrate.ps1    ← Unified CLI entry point
  ├── tools/             ← Global Hacking Tools
  ├── TriageTalon/       ← Attack Surface Recon API
  └── wordlists/         ← Global Wordlists (SecLists, etc)
  ```

  **File placement rules — ALWAYS follow this:**
  ```
  programs/<target-name>/           ← ALL work for a specific program goes here
  programs/<target-name>/recon/     ← Subdomain lists, nuclei output, ffuf results
  programs/<target-name>/evidence/  ← Screenshots, HTTP dumps, PoC files (.txt, .png, .http)
  programs/<target-name>/reports/   ← Draft and final reports (.md)
  programs/<target-name>/scripts/   ← Target-specific scripts (.ps1, .py, .sh)
  programs/<target-name>/temp/      ← Temporary/scratch files (UI dumps, APK artifacts, session files, traffic logs)
  ```

  **Rules for agents:**
  1. BEFORE creating ANY file, identify the active program. All files MUST go into `programs/<target-name>/`.
  2. If a file is temporary (traffic log, screenshot, session dump, UI XML, APK artifact) → put it in `programs/<target-name>/temp/`.
  3. If a file is evidence/PoC → put it in `programs/<target-name>/evidence/`.
  4. If a file is a report draft → put it in `programs/<target-name>/reports/`.
  5. If a file is a recon output (subdomains, nuclei, ffuf) → put it in `programs/<target-name>/recon/`.
  6. NEVER write files to root, Desktop, Downloads, or any path outside `C:\BugBounty\programs\<target-name>\`.
  7. If no active program is set and you need scratch space, use `C:\BugBounty\temp\` ONLY — and remind the user to assign a program.
  8. `cookies.txt` is session-specific: keep it in `C:\BugBounty\temp\` if shared, or in `programs/<target-name>/temp/` if program-specific.
  9. Global utility scripts go in `C:\BugBounty\_scripts\`. Target-specific scripts go in `programs/<target-name>/scripts/`.
  10. When starting work on a new program, ALWAYS run: `New-Item -ItemType Directory -Force -Path "programs/<slug>/{recon,evidence,reports,scripts,temp}"` to pre-create the folder structure.

## Report Discipline Rules (Always-On)

These rules apply to EVERY interaction — drafting, discussing findings, validating reports, or estimating impact. They do NOT require invoking a skill.

### Evidence-First Principle
- **Never invent facts** about a target. CVEs, endpoints, parameters, library versions, headers, response bodies — if there is no direct evidence, say so explicitly. Do NOT fill gaps with plausible-sounding details.
- **Never write theoretical impact.** Phrases like "could lead to...", "may allow...", "an attacker with the right conditions..." are banned unless the hunter has proven the impact and you are summarizing confirmed proof.
- **Build impact bottom-up from evidence.** If the hunter asks "is this exploitable?" — ask what they *actually observed*, not what they think might happen.
- **If facts are missing, ask — do not write around the gap.** Offer alternatives (2-3 options at most), not single authoritative answers. The hunter must be able to defend every sentence to a triager.

### PoC Standard
- **A PoC is valid only if a triager with zero prior context can replay it from scratch.** Apply this bar to every PoC shown.
- Prefer raw HTTP request/response over curl, curl over scripts, scripts only when the bug genuinely cannot be expressed in one or two requests (race condition, multi-step chain, thousands of iterations).
- Strip session tokens and PII. Use `[REDACTED]` where something was removed. Do not fabricate values.
- Include only requests strictly necessary to reproduce. Cut recon noise, unrelated calls, and duplicate attempts.

### Anti-Overclaim Rules
- Do not rate severity by vulnerability *mechanism* — rate by *proven impact of the specific action*.
- CVSS `AC:L` requires the ID/resource to be discoverable at scale. Random UUIDv4, HMAC tokens, opaque long IDs → score `AC:H` and state where the ID would leak from.
- Do not claim "session theft" when the cookie is `HttpOnly`. Do not claim "account takeover" without a PoC that literally takes over an account.
- Do not claim "mass data breach" from a single cross-account read on a non-enumerable ID.
- For RCE: prove execution with a harmless marker (`id`, `whoami`, OOB callback) and stop. Do not pivot, escalate privileges, or run destructive commands to "demonstrate" reach.
- For SQLi: prove the primitive (sentinel value, controlled time-delay, boolean oracle) and stop. Do not dump tables or chain to `xp_cmdshell` to "prove" impact.

### Anti-Slop Rules
- No multi-paragraph OWASP intros. No generic mitigations like "validate user input". No Introduction / Background / Conclusion scaffolding for a one-step bug.
- No copy-pasted CWE descriptions in the report body (the platform renders CWE from the form field).
- Lab-notes style discovery narrative is more credible than a polished narrative with no failed attempts — keep dead ends and friction.

### When Suspicious Behavior Is Not Yet a Bug
- If the hunter describes behavior that is suspicious but not yet exploited → say "not yet a bug, here is what would prove it" instead of validating the claim.
- Do not call a DNS-only interaction an SSRF. Do not call a WAF block a confirmed SQLi. Do not call a stack trace mentioning `exec()` an RCE.

---

## Auto-Trigger Rules (Skill Auto-Invocation)

When ANY of the patterns below are detected in user input during a bug bounty context, **automatically apply the corresponding mode from `bbp-report-writer`** WITHOUT waiting to be explicitly asked. Read `C:\BugBounty\.agents\skills\bbp-report-writer\SKILL.md` first, then execute the matching mode.

| User says something like... | Auto-invoke |
|---|---|
| "help me write this up", "here are my notes", "write this report", "structure this finding", "I found a bug, help me report it" | **Mode 1: Write** — ask for missing inputs, then draft section by section |
| "is this ready to submit?", "triage this", "check my draft", "review my report", "should I submit this?", "is this good enough?" | **Mode 2: Triage** — ask for scope if missing, return READY/NEEDS FIXES/DO NOT SUBMIT verdict |
| "what do I need to prove for [vuln class]?", "what's the minimum proof?", "will this get rejected?", "is this enough evidence?", "common mistakes for [class]?" | **Mode 3: Gotchas** — show only the matching class section |
| Report draft or raw notes are pasted with no explicit instruction | Detect intent: if it looks like a finished draft, run **Mode 2 (Triage)**; if it looks like raw notes, run **Mode 1 (Write)** |
| A specific vuln class is mentioned in a draft being triaged | **Automatically append Mode 3 gotchas** for that class at the end of the triage output |

### OpenCode Slash Commands (explicit invocation)
- `/ywh-write [optional: raw notes]` — Mode 1 (Write)
- `/ywh-triage [optional: draft]` — Mode 2 (Triage)
- `/ywh-gotchas [optional: class name]` — Mode 3 (Gotchas)

---

## Templates

- `_templates/bb.toml` — scope config per program (copy & fill per target)
- `_templates/report.md` — General bug bounty report template (works for all platforms)

## Skill Reference

- Base skill: `C:\BugBounty\SKILL.md` — encyclopedia (37 sections, 95KB, commands & workflows)
- Core orchestrator: `C:\BugBounty\bbcore\` — proxy_manager, waf_detector, recon_runner, skill_loader, orchestrator
- CLI: `.\orchestrate.ps1` or `python bbcore/cli.py`
- Browser integration: `C:\ProjectBrowser\bounty_integration.py`
- Skills: `C:\BugBounty\.agents\skills\` — 80 skills, load via `/skill <name>`:
  - **bbp-ops** — `bbp-program-orchestrator`, `bbp-program-triage`, `bbp-duplicate-guard`, `bbp-evidence-workbench`, `bbp-report-writer`
  - **bbp-recon** — `bbp-web-recon`, `bbp-subdomain-takeover`, `bbp-cloud-security-audit`
  - **bbp-web-attacks** — `bbp-xss-hunter`, `bbp-sqli-hunter`, `bbp-ssrf-hunter`, `bbp-osci-hunter`, `bbp-xxe-hunter`, `bbp-prototype-pollution`, `bbp-cache-poisoning`, `bbp-file-upload-lfi`, `bbp-advanced-fuzzing`
  - **bbp-web-security** — `bbp-api-audit`, `bbp-auth-bypass`, `bbp-graphql-audit`, `bbp-business-logic`, `bbp-waf-bypass`, `bbp-wpscan`, `bbp-spring-actuator-audit`, `bbp-rsocket-testing`, `bbp-java-deserialization`
  - **bbp-mobile** — `bbp-android-apk-audit`, `bbp-mobile-reverse-engine`, `bbp-mobile-dynamic-analysis`, `bbp-mobile-ipc-exploit`, `bbp-mobile-local-storage`
  - **bbp-source-review** — `bbp-source-code-audit`, `bbp-rust-security-review`, `bbp-crypto-audit`, `code-security`, `vulnhunter`, `bbp-evoting-crypto-audit`
  - **bbp-reference** — `bbp-payloads-all-the-things`, `bbp-hackerone-disclosures`, `bbp-nuclei-templates`, `bbp-cve-poc-db`, `bbp-hacktricks`, `bbp-seclists`
  - **web-extended** — `testing-cors-misconfiguration`, `testing-for-host-header-injection`, `testing-for-open-redirect-vulnerabilities`, `testing-websocket-api-security`, `exploiting-websocket-vulnerabilities`, `detecting-shadow-api-endpoints`, `performing-api-inventory-and-discovery`, `performing-api-rate-limiting-bypass`, `testing-for-email-header-injection`
  - **llm-security** — `detecting-ai-model-prompt-injection-attacks`, `detecting-indirect-prompt-injection`, `testing-prompt-injection-in-rag-pipelines`, `testing-for-system-prompt-leakage`
  - **ghost-security** — `ghost-proxy`, `ghost-repo-context`, `ghost-report`, `ghost-scan-code`, `ghost-scan-deps`, `ghost-scan-secrets`, `ghost-validate`
  - **binary-analysis** — `binary-analysis-patterns`, `binary-hardening`, `binary-triage`, `ctf-reverse`, `protocol-reverse-engineering`, `rev-frida`
  - **windows-security** — `windows-av-evasion`, `windows-lateral-movement`, `windows-privilege-escalation`
  - **agent-core** — `agent-browser`, `find-skills`

## Slash Commands

### `/program <url> [name]`

**Program workflow orchestrator.** Triggers automated recon and initial triage.
**Agent Rule:** If the user types this command, IMMEDIATELY call the `bbp-program-orchestrator` skill (which will instruct the AI to execute `.\orchestrate.ps1 init <url> [name]`) and follow its instructions without asking.

### `/recon <domain> [--skip-nuclei] [--skip-ffuf]**

**WAF-aware recon pipeline.** Automated proxy rotation, dynamic rate limiting based on WAF detection.
Runner: `.\orchestrate.ps1 recon <domain>`

### `/proxy <mode> [arg]`

**Proxy manager.**
Modes: `direct`, `tor`, `static <url>`, `rotate <file>`
Runner: `.\orchestrate.ps1 proxy <mode> [arg]`

### `/report <slug>`

**Generate report** from collected findings.
Runner: `.\orchestrate.ps1 report <slug>`

### `/bb <command> [args]`

**Alias for BugBounty Orchestrator.** All the above commands can also be executed via:
`.\orchestrate.ps1 <command> [args]`
Or directly: `python bbcore/cli.py <command> [args]`

### `/browser`

**Launch Shield Browser** with active BugBounty integration.
Runner: `.\orchestrate.ps1 browser`

## Scan Loop

### 1. Prioritize based on findings
1. Critical/high nuclei → validate & exploit deeper
2. Hidden Content / Admin Panels (from ffuf) → manual review, bypass auth
3. API endpoints & Hidden Params (from arjun/ffuf) → sqlmap, test auth, test IDOR/BOLA
4. JWT/auth endpoints → crypto review
5. Open ports (nmap) → service-specific checks
6. Low/medium nuclei → validate, skip if FP
7. Remaining alive hosts → deep crawling, js analysis

### 2. Depth over breadth
- Found SQLi? Pivot: sqlmap --os-shell, enumerate tables. Don't switch host.
- Found XSS? Try blind XSS, eval-based polyglots.
- **3 bypass attempts minimum** before declaring unexploitable.

### 3. WAF Evasion & Rate Limiting
Default tool flags often trigger WAFs (Cloudflare/Imperva) because of default User-Agents (e.g., go-http-client) and static/robotic request intervals. Use these techniques:

- **User-Agent Spoofing:** Always use a real browser UA.
  - `nuclei`: Use `-H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."` or set it in `.nuclei-config.yaml`.
  - `ffuf`: Use `-H "User-Agent: Mozilla/5.0..."`
  - `sqlmap`: Always use `--random-agent`
- **Jitter / Randomized Delay:** Do not use flat intervals. WAFs detect consistent timing patterns.
  - `ffuf`: Use `-p "0.1-0.5"` (random delay between 0.1 and 0.5 seconds).
  - `nuclei`: Use `-rate-limit 30 -bulk-size 25` and add delay if necessary.
  - `katana`: Use `-delay 2s` (or more if blocked).
- **Payload Strategy:** Send raw payloads (without encoding) during initial discovery. Only use encoding (URL/Double/Null-byte) **after** detecting a block, to avoid *false negatives*.

### 5. Error recovery

| Error | Action |
|-------|--------|
| WAF block (403/429) | try `-H "X-Forwarded-For: 127.0.0.1"`, slow rate, alternative endpoints |
| Payload filtered | URL encoding, double encoding, null bytes, alt syntax |
| Tool crash/timeout | retry once with longer timeout, then skip |
| No results from tool | retry with aggressive/deep flags before giving up |
| Network error | retry after 30s, skip after 3 failures |

### 6. Termination
Stop when: queue empty AND all alive hosts through ≥1 vuln scan **OR** user says stop **OR** 3 consecutive runs produce zero new findings.

### 7. Documentation
Save progress in `programs/<slug>/state.json`:
```json
{ "phase": "recon_done", "alive": 42, "done": ["nuclei", "ffuf"], "queue": ["sqlmap-/api/login"] }
```

## Passive Reconnaissance

Run **before active scanning** — zero interaction with target.

### TriageTalon (Passive Attack Surface Triage)
Use the `bbp-triagetalon-pro` skill/tool at this stage **before** using active and aggressive scanners like Nuclei. TriageTalon is designed to map the attack surface **passively and stealthily** (without sending malicious payloads or triggering WAF rate limits). Its main targets are finding open ports, CORS misconfigurations, and sensitive endpoints (Swagger, Actuator, `.env`).

### Google Dorking
Search for exposed files, config leaks, and admin panels via search engines:
```
site:target.com ext:sql | ext:bak | ext:swp | ext:env
site:target.com intitle:"index of" | intext:"phpinfo()"
site:target.com intitle:"login" | intitle:"admin" inurl:admin
site:target.com inurl:wp-config | inurl:config.php
site:target.com filetype:log | filetype:conf | filetype:ini
```
Use `site:` with verified subdomains. Also check `cache:` to view older versions of pages that might have been deleted but are still indexed.

### GitHub Dorking
Search for leaked credentials and internal paths in public repos:
```
"target.com" "api_key" | "secret" | "password" | "token"
"target.com" "aws_access_key_id" | "AKIA" | "-----BEGIN RSA PRIVATE KEY-----"
"target.com" filename:.env | filename:config.json | filename:credentials
org:targetorg "security" | "vulnerability" | "TODO"
```
Priority: high-star repos, recent commits, gists. Use search qualifiers: `language:`, `path:`, `extension:`.

### Shodan / Censys
Search for exposed services, open databases, and default creds:
```
shodan search "hostname:target.com"
shodan search "ssl:target.com"
censys search "services.service_name: HTTP and dns.names: target.com"
```
Focus: port 22 (SSH), 3306 (MySQL), 27017 (MongoDB), 6379 (Redis), 9200 (Elasticsearch), 3389 (RDP), 5432 (PostgreSQL), and non-standard ports.

### Wayback Machine / URL History
```
gau --subs target.com
waybackurls target.com
```
Extract endpoints, parameters, and JS paths from historical data — many hidden endpoints that are no longer linked might still be accessible via Wayback.

## Cookie/Login Setup

Private programs (YesWeHack private, H1 private, Bugcrowd private) need authentication.

1. Login to the platform in your browser
2. Export cookies using `.\scripts\setup-cookies.ps1`
3. Save cookies to `cookies.txt` (Netscape format)
4. Run `/program` again — script will auto-detect and use the cookies

The script checks for `cookies.txt` in the project root. If present, it sends the cookies with every program page fetch.

## Scripts

### Core Orchestrator (bbcore)
- `.\orchestrate.ps1 init <url> [slug]` — init workspace + bb.toml
- `.\orchestrate.ps1 recon <domain>` — WAF-aware recon (auto proxy, rate limiting)
- `.\orchestrate.ps1 proxy <mode> [arg]` — proxy rotation (direct/tor/static/rotate)
- `.\orchestrate.ps1 report <slug>` — generate report from `_templates/report.md`
- `.\orchestrate.ps1 status` — orchestrator status
- `.\orchestrate.ps1 programs` — list all programs
- `.\orchestrate.ps1 skills` — list 80 available skills
- `.\orchestrate.ps1 browser` — launch Shield Browser with BB integration

### Original Scripts (also callable via bbcore)
- `.\scripts\source_audit.ps1 -Path <path>` — source code audit (semgrep, codeql, ripgrep)
- `.\scripts\dependency_audit.ps1 -Path <path>` — dependency vulnerability scanning
- `.\scripts\mobile_audit.ps1 -ApkPath <path>` — Android APK analysis
- `.\scripts\secrets_scan.ps1 -Path <path>` — secret scanning (gitleaks, trufflehog)
- `.\scripts\update_all_tools.ps1` — update all tools and wordlists
- `.\_scripts\inject-cookies.ps1` — inject cookies from cookies.txt
- `.\_scripts\load-cookies.ps1` — load cookies.txt for authenticated scanning

### Legacy (Bash/WSL — still work but prefer bbcore)
- `wsl bash scripts/program.sh -u <url>` — legacy orchestrator
- `wsl bash scripts/recon.sh -d target.com` — legacy recon pipeline

## Lessons Learned

1. **Screenshot while scans are running**, don't wait until they finish — real-time terminal proof + timestamp.
2. **Manual verification immediately** after finding a vulnerability — endpoints can suddenly return 404 or get blocked by WAF.
3. **Save interactsh/OAST logs yourself** — don't just rely on nuclei output.
4. **Check response body** — a 200 OK could be an SPA catch-all or a WAF block page, not a real endpoint.
5. **Prioritize manual RCE** — automated scans are for discovery, manual exploitation is for final validation.
6. **File Timestamps** — CreationTime/LastWriteTime can serve as forensic evidence in case of a dispute.
7. **Check program exclusion list before reporting** — TikTok excludes "Missing anti-clickjacking mechanisms" and "Software version disclosure / Banner identification / Descriptive error messages or headers". Clickjacking requires a PoC for a sensitive (state-changing) action, not just framing. Info disclosure headers are almost always rejected by large programs. Check the policy first to avoid wasting time.
8. **H1 clickjacking = low/medium only if sensitive action** — Framing alone without a sensitive action (post/delete/edit) is not enough. Large programs usually require demonstrable impact.

## External References

Useful repos integrated into workflow:
- `projectdiscovery/nuclei-templates` — 5000+ YAML templates (auto-updated). AI can generate custom templates from CVEs.
- `swisskyrepo/PayloadsAllTheThings` — structured payload reference per vulnerability class.
- `danielmiessler/SecLists` — wordlists for content discovery (referenced in SKILL.md commands).
- `PortSwigger/Web-Security-Academy` — free labs for practice and technique validation.

## Obsidian Integration & Context Retrieval

- **CROSS-REFERENCING TARGET STATUS**: Whenever the user asks for the status, updates, or recent activity regarding a specific bug bounty target or program (e.g., "how is target X going?", "where did we leave off on Y?"), you MUST NOT rely solely on the main target note in `02 - Program Targets`.
- You **MUST** proactively use `grep_search` or `call_mcp_tool` (filesystem) to search the following directories for the target's name before responding:
  1. `C:\Users\rafli\Documents\Obsidian Vault\07 - Daily Hunting Logs\` (to find active escalations and recent session context).
  2. `C:\Users\rafli\Documents\Obsidian Vault\02 - Program Targets\Findings\` (to find specific bug details).
- Only answer the user AFTER you have synthesized the information from the main target note, the daily logs, and the findings.
