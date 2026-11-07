#!/usr/bin/env python3
"""workflow_tools.py - bug-hunting acceleration tools for the BugBounty workspace.

Modules:
  js_recon      - JS bundle intelligence: extract endpoints/secrets/sourcemaps
  skill_router  - map detected technology stack to relevant bbp-* skills,
                  enqueue into program state.json
  diff_monitor  - snapshot vs current recon delta (new subdomains/hosts)
  oob_logger    - manage per-program interactsh-client logging session
  hunt_plan     - generate prioritized HUNT_PLAN.md per program
  scope_guard   - verify assets/findings against policy/bb.toml scope;
                  end-of-program sweep for out-of-scope artifacts

All commands operate ONLY on local workspace data except js_recon/oob which
contact targets the user has declared in their own program scope.
"""

import fnmatch
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

try:
    import tomllib  # Python 3.11+
except ImportError:  # pragma: no cover
    tomllib = None

BB_DIR = Path(__file__).resolve().parent.parent
PROGRAMS_DIR = BB_DIR / "programs"
SKILLS_DIR = BB_DIR / ".agents" / "skills"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

MAX_JS_FILES = 100


# --------------------------------------------------------------------------
# shared helpers
# --------------------------------------------------------------------------

def _program_dir(slug: str) -> Path:
    p = PROGRAMS_DIR / slug
    if not p.is_dir():
        raise FileNotFoundError(f"program folder not found: {p}")
    return p


def _recon_dir(slug: str) -> Path:
    d = _program_dir(slug) / "recon"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _temp_dir(slug: str) -> Path:
    d = _program_dir(slug) / "temp"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _load_state(slug: str) -> dict:
    f = _program_dir(slug) / "state.json"
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            pass
    return {}


def _save_state(slug: str, state: dict) -> None:
    f = _program_dir(slug) / "state.json"
    f.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _read_lines(path: Path) -> list:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line:
            out.append(line)
    return out


def _primary_domain(slug: str, override=None):
    if override:
        return override
    # Prefer declared scope/state over guessing from slug text (slugs use
    # dashes, so naive slug.replace('-','.') would corrupt real dashes).
    st = _load_state(slug)
    for key in ("recon_domain", "url"):
        v = st.get(key)
        if v:
            s = str(v).lower()
            if "://" in s:
                from urllib.parse import urlparse as _up
                s = _up(s).netloc or s
            s = s.split("/")[0].split(":")[0].lstrip(".")
            if "." in s:
                return s
    for cand in (_program_dir(slug) / "policy" / "bb.toml",
                 _program_dir(slug) / "bb.toml"):
        if cand.exists() and tomllib:
            try:
                data = tomllib.loads(cand.read_text(encoding="utf-8"))
                domains = data.get("recon", {}).get("domains") or []
                if domains:
                    return str(domains[0])
            except Exception:
                pass
    # last resort: underscores are unambiguous; dashes stay as-is
    return slug.replace("_", ".")


# --------------------------------------------------------------------------
# 1. JS intelligence pipeline
# --------------------------------------------------------------------------

SECRET_PATTERNS = {
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "github_token": re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    "slack_token": re.compile(r"xox[baprs]-[A-Za-z0-9\-]{10,}"),
    "google_api": re.compile(r"AIza[0-9A-Za-z_\-]{30,}"),
    "jwt": re.compile(r"eyJ[A-Za-z0-9_\-]{15,}\.[A-Za-z0-9_\-]{15,}\."),
    "firebase_url": re.compile(r"[a-z0-9\-]+\.firebaseio\.com"),
    "private_key_hint": re.compile(r"BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY"),
}

ENDPOINT_RE = re.compile(r"""["'`](/[A-Za-z0-9_\-][A-Za-z0-9_\-\./]{2,80})["'`]""")
FULLURL_RE = re.compile(r"https?://[A-Za-z0-9_\-\./]{4,120}")

JS_URL_SOURCES = ("katana", "gau", "wayback", "urls", "js_urls")


def _collect_js_urls(slug: str, seed_domain: str) -> set:
    urls = set()
    rdir = _recon_dir(slug)
    for txt in rdir.glob("*.txt"):
        name = txt.stem.lower()
        if not any(s in name for s in JS_URL_SOURCES):
            continue
        for line in _read_lines(txt):
            if ".js" in line and line.startswith("http"):
                urls.add(line.split("?")[0])
    # live seed page: pull script tags from the primary domain landing page
    if len(urls) < 5 and seed_domain:
        try:
            import urllib.request
            req = urllib.request.Request(
                f"https://{seed_domain}", headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=12) as r:
                html = r.read(400000).decode("utf-8", errors="replace")
            for m in re.finditer(r'src=["\']([^"\']+\.js[^"\']*)["\']', html):
                u = m.group(1)
                if u.startswith("//"):
                    u = "https:" + u
                elif u.startswith("/"):
                    u = f"https://{seed_domain}{u}"
                if u.startswith("http"):
                    urls.add(u)
        except Exception as exc:
            print(f"[!] seed fetch failed for {seed_domain}: {exc}")
    return {u for u in urls if ".js" in u.lower()}


def run_js_recon(args):
    """jsrecon <slug> [seed_domain]"""
    if not args:
        print("[-] Usage: jsrecon <slug> [seed_domain]")
        return 1
    slug = args[0]
    seed = args[1] if len(args) > 1 else None
    pdir = _program_dir(slug)
    rdir = _recon_dir(slug)
    tdir = _temp_dir(slug) / "js"
    tdir.mkdir(parents=True, exist_ok=True)

    urls = sorted(_collect_js_urls(slug, seed))[:MAX_JS_FILES]
    print(f"[*] {len(urls)} JS candidates")
    if not urls:
        print("[-] No JS sources. Run recon/katana first or pass seed_domain.")
        return 1

    import urllib.request
    endpoints = set()
    fullurls = set()
    secrets_hits = []
    smaps = []
    fetched = 0
    for i, u in enumerate(urls, 1):
        dest = tdir / f"{i:03d}_{re.sub(r'[^A-Za-z0-9]', '_', u[-70:])}.js"
        try:
            req = urllib.request.Request(u, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=12) as r:
                body = r.read(3000000).decode("utf-8", errors="replace")
            dest.write_text(body, encoding="utf-8")
            fetched += 1
        except Exception:
            continue
        for m in ENDPOINT_RE.finditer(body):
            ep = m.group(1)
            if not re.match(r"/\d", ep) and "font" not in ep and ".png" not in ep \
               and ".svg" not in ep and ".css" not in ep and ".woff" not in ep:
                endpoints.add(ep)
        for m in FULLURL_RE.finditer(body):
            fullurls.add(m.group(0))
        for label, rx in SECRET_PATTERNS.items():
            for m in rx.finditer(body):
                snippet = m.group(0)
                redacted = snippet[:10] + "***" if len(snippet) > 14 else "***"
                secrets_hits.append({"type": label, "file": u,
                                     "sample": redacted})
        if "sourceMappingURL" in body:
            smaps.append(u)
        time.sleep(0.25)
        if i % 10 == 0:
            print(f"    [{i}/{len(urls)}] downloaded={fetched}")

    (rdir / "js_endpoints.txt").write_text(
        "\n".join(sorted(endpoints)), encoding="utf-8")
    (rdir / "js_fullurls.txt").write_text(
        "\n".join(sorted(fullurls)), encoding="utf-8")
    summary = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "candidates": len(urls), "downloaded": fetched,
        "unique_endpoints": len(endpoints),
        "secrets_candidates": len(secrets_hits),
        "sourcemaps": len(smaps),
    }
    (rdir / "js_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")

    if secrets_hits:
        lines = ["# JS Secret Candidates (verify manually, redacted samples)",
                 ""]
        for h in secrets_hits[:50]:
            lines.append(f"- [{h['type']}] {h['file']}")
            lines.append(f"  sample: `{h['sample']}`")
        (rdir / "js_secrets.md").write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(summary, indent=2))
    if smaps:
        print(f"[+] {len(smaps)} sourcemaps referenced - try downloading "
              f".map for original sources")
    print("[+] Endpoints saved to recon/js_endpoints.txt")
    print("[>] NEXT: feed into bbp-api-audit (BOLA/mass-assignment matrix);")
    print("    verify every secret candidate manually before reporting.")
    return 0


# --------------------------------------------------------------------------
# 2. Tech -> skill router
# --------------------------------------------------------------------------

TECH_SKILL_MAP = [
    (r"wordpress|\bwp-", "bbp-wpscan", "WordPress detected"),
    (r"graphql|apollo", "bbp-graphql-audit", "GraphQL surface detected"),
    (r"spring|actuator|jolokia|tomcat|jboss|wildfly", "bbp-spring-actuator-audit",
     "Java/Spring stack detected"),
    (r"cloudflare|akamai|incapsula|imperva|sucuri|f5|big-?ip", "bbp-waf-bypass",
     "WAF/edge vendor detected"),
    (r"varnish|squid|cloudfront|fastly|x-cache|x-varnish", "bbp-cache-poisoning",
     "Caching layer detected"),
    (r"swagger|openapi|api-?gateway|\brest\b|application/json", "bbp-api-audit",
     "API surface detected"),
    (r"jwt|oauth|auth0|okta|keycloak|identityserver|saml", "bbp-auth-bypass",
     "Auth framework detected"),
    (r"s3\.amazonaws|azurewebsites|storage\.googleapis|blob\.core", "bbp-cloud-security-audit",
     "Cloud storage surface detected"),
    (r"x-powered-by: express|node\.js|php|laravel|symfony|django", "bbp-file-upload-lfi",
     "Server runtime commonly paired with upload/LFI issues"),
    (r"websocket|ws://|socket\.io", "testing-websocket-api-security",
     "WebSocket endpoint detected"),
    (r"chatgpt|openai|llm|\bai[-_]assistant|copilot", "detecting-indirect-prompt-injection",
     "LLM feature keywords detected"),
]

FINDING_SKILL_MAP = [
    (r"takeover", "bbp-subdomain-takeover", "takeover finding class"),
    (r"cve-", "bbp-cve-poc-db", "CVE hit - lookup PoC db"),
    (r"(ssrf)", "bbp-ssrf-hunter", "SSRF signal"),
    (r"(xss)", "bbp-xss-hunter", "XSS signal"),
    (r"(sqli|sql injection)", "bbp-sqli-hunter", "SQLi signal"),
    (r"(\.env|secret|password)", "bbp-file-upload-lfi", "exposure signal"),
]


def _scan_tech_signals(slug: str):
    signals = []  # (source, matched_text)
    rdir = _recon_dir(slug)
    httpx_files = list(rdir.glob("*httpx*")) + list(rdir.glob("*alive*"))
    for hf in httpx_files:
        for line in _read_lines(hf)[:2000]:
            low = line.lower()
            if "[" in line and "]" in line:  # httpx tech columns
                signals.append((hf.name, line))
    nuclei = rdir / "nuclei.txt"
    if not nuclei.exists():
        alt = list(rdir.glob("*nuclei*"))
        nuclei = alt[0] if alt else None
    if nuclei and nuclei.exists():
        for line in _read_lines(nuclei)[:2000]:
            signals.append((nuclei.name, line))
    tt = rdir / "triagetalon_pro.json"
    if tt.exists():
        try:
            data = json.loads(tt.read_text(encoding="utf-8"))
            signals.append((tt.name, json.dumps(data)[:20000]))
        except (ValueError, OSError):
            pass
    return signals


def run_route(args):
    """route <slug> [--dry]"""
    if not args:
        print("[-] Usage: route <slug> [--dry]")
        return 1
    slug = args[0]
    dry = "--dry" in args
    signals = _scan_tech_signals(slug)
    blob = "\n".join(s[1] for s in signals).lower()
    if not blob.strip():
        print("[-] No recon signals found. Run 'recon' or 'triagetalon' first.")
        return 1

    found = []
    seen = set()
    for rx, skill, why in TECH_SKILL_MAP + FINDING_SKILL_MAP:
        if re.search(rx, blob) and skill not in seen:
            if (SKILLS_DIR / skill).is_dir():
                found.append((skill, why))
                seen.add(skill)
            else:
                print(f"[!] mapped skill missing on disk: {skill}")

    print(f"[*] Signals scanned from {len(signals)} source lines")
    if not found:
        print("[-] No specific skill mapping triggered. Default loop applies.")
        return 0
    print("[+] Recommended skill queue:")
    queue_items = []
    rank = 1
    for skill, why in found:
        line = f"  {rank}. {skill:38s} <- {why}"
        print(line)
        queue_items.append(f"skill:{skill}")
        rank += 1

    if not dry:
        state = _load_state(slug)
        q = state.get("queue", [])
        for item in queue_items:
            if item not in q:
                q.append(item)
        state["queue"] = q
        state["routed_at"] = datetime.now().isoformat(timespec="seconds")
        _save_state(slug, state)
        print(f"[+] {len(queue_items)} items appended to state.json queue")
    else:
        print("[*] dry-run: state.json untouched")
    return 0


# --------------------------------------------------------------------------
# 3. Recon diff monitor
# --------------------------------------------------------------------------

def _extract_hosts(httpx_lines):
    hosts = set()
    for line in httpx_lines:
        first = line.split()[0] if line.split() else ""
        host = urlparse(first).netloc if "://" in first else first
        if host:
            hosts.add(host.lower())
    return hosts


def run_diff(args):
    """diff <slug> [--no-update]"""
    if not args:
        print("[-] Usage: diff <slug> [--no-update]")
        return 1
    slug = args[0]
    no_update = "--no-update" in args
    rdir = _recon_dir(slug)
    base = rdir / "_baseline"
    base.mkdir(parents=True, exist_ok=True)

    cur_subs = set(_read_lines(rdir / "subs.txt"))
    # recon_runner writes alive.txt; older skill docs reference httpx.txt —
    # accept both so diff never silently sees 0 hosts.
    httpx_lines = _read_lines(rdir / "alive.txt") + _read_lines(rdir / "httpx.txt")
    cur_hosts = _extract_hosts(httpx_lines)

    old_subs_f = base / "subs.txt"
    old_hosts_f = base / "hosts.txt"
    is_first = not old_subs_f.exists()

    old_subs = set(_read_lines(old_subs_f))
    old_hosts = set(_read_lines(old_hosts_f))

    new_subs = sorted(cur_subs - old_subs)
    gone_subs = sorted(old_subs - cur_subs)
    new_hosts = sorted(cur_hosts - old_hosts)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    lines = [f"# Recon Diff {slug} @ {stamp}", ""]
    if is_first:
        lines.append("First baseline created - no comparison yet.")
    else:
        lines.append(f"## NEW subdomains ({len(new_subs)})")
        lines += [f"- {s}" for s in new_subs] or ["- (none)"]
        lines.append("")
        lines.append(f"## NEW live hosts ({len(new_hosts)})")
        lines += [f"- {h}" for h in new_hosts] or ["- (none)"]
        if gone_subs:
            lines.append("")
            lines.append(f"## disappeared ({len(gone_subs)}) <- takeover check!")
            lines += [f"- {s}" for s in gone_subs]
    report = rdir / f"diff_{stamp}.txt"
    report.write_text("\n".join(lines), encoding="utf-8")

    if is_first or not no_update:
        (old_subs_f).write_text("\n".join(sorted(cur_subs)), encoding="utf-8")
        (old_hosts_f).write_text("\n".join(sorted(cur_hosts)), encoding="utf-8")

    print("\n".join(lines))
    print(f"[+] Report: {report.name} | baseline "
          f"{'created' if is_first or not no_update else 'kept (--no-update)'}")
    if gone_subs:
        print("[!] Disappeared hosts are prime bbp-subdomain-takeover targets.")
    return 0


# --------------------------------------------------------------------------
# 4. OOB interaction logger
# --------------------------------------------------------------------------

def _oob_dir(slug: str) -> Path:
    d = _temp_dir(slug) / "oob"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _find_interactsh():
    for cand in ("interactsh-client",):
        try:
            subprocess.run([cand, "-version"], capture_output=True, timeout=10)
            return cand, False
        except (OSError, subprocess.TimeoutExpired):
            continue
    try:
        r = subprocess.run(["wsl", "bash", "-lc", "command -v interactsh-client"],
                           capture_output=True, timeout=20)
        if r.returncode == 0 and r.stdout.strip():
            return "wsl", True
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None, False


def run_oob(args):
    """oob <slug> start|stop|status|tail"""
    if len(args) < 2:
        print("[-] Usage: oob <slug> start|stop|status|tail")
        return 1
    slug, action = args[0], args[1]
    odir = _oob_dir(slug)
    pid_file = odir / "pid.txt"
    log_file = odir / "interactions.log"
    tool, use_wsl = _find_interactsh()
    if action == "start":
        if not tool:
            print("[-] interactsh-client not found (Windows PATH / WSL). "
                  "Install: go install -v github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest")
            return 1
        if pid_file.exists():
            print(f"[!] Already running (pid file {pid_file.name}). Stop first.")
            return 1
        if use_wsl:
            log_wsl = str(log_file).replace("C:\\", "/mnt/c/").replace("\\", "/")
            exe = ["wsl", "bash", "-lc",
                   f"interactsh-client -json > {log_wsl} 2>&1"]
        else:
            exe = [tool, "-json"]
        with open(log_file, "ab") as lf:
            proc = subprocess.Popen(exe, stdout=lf, stderr=subprocess.STDOUT)
        pid_file.write_text(str(proc.pid), encoding="utf-8")
        url_hint = log_file
        print(f"[+] OOB session started (pid {proc.pid}), log: {url_hint}")
        print("[>] Payload marker tip: use unique subdirs per finding, "
              "e.g. <finding-id>.<oast-domain>")
        return 0
    if action == "stop":
        if not pid_file.exists():
            print("[-] No active session recorded.")
            return 1
        pid = pid_file.read_text(encoding="utf-8").strip()
        try:
            subprocess.run(["taskkill", "/PID", pid, "/T", "/F"],
                           capture_output=True, timeout=15)
            print(f"[+] Stopped pid {pid}")
        except Exception as exc:
            print(f"[!] taskkill issue: {exc}")
        # Sessions started via WSL leave interactsh-client alive inside WSL
        # even after the wrapper pid dies — best-effort cleanup.
        try:
            subprocess.run(["wsl", "bash", "-lc", "pkill -f interactsh-client"],
                           capture_output=True, timeout=15)
        except Exception:
            pass
        pid_file.unlink(missing_ok=True)
        return 0
    if action == "status":
        running = pid_file.exists()
        n_int = 0
        if log_file.exists():
            n_int = sum(1 for l in _read_lines(log_file) if '"protocol"' in l
                        or '"remote-address"' in l)
        print(f"session={'ACTIVE' if running else 'idle'} | "
              f"interaction-lines~{n_int} | log={log_file.name}")
        return 0
    if action == "tail":
        n = 20
        if len(args) > 2 and args[2].isdigit():
            n = int(args[2])
        if not log_file.exists():
            print("[-] No log yet.")
            return 1
        for line in _read_lines(log_file)[-n:]:
            print(line[:300])
        return 0
    print(f"[-] Unknown action '{action}'")
    return 1


# --------------------------------------------------------------------------
# 5. Hunt plan generator
# --------------------------------------------------------------------------

def run_plan(args):
    """plan <slug>"""
    if not args:
        print("[-] Usage: plan <slug>")
        return 1
    slug = args[0]
    pdir = _program_dir(slug)

    scope_summary = ["(policy/bb.toml not found - fill it!)"]
    scope_path = pdir / "policy" / "bb.toml"
    if not scope_path.exists():
        scope_path = pdir / "bb.toml"
    if scope_path.exists() and tomllib:
        try:
            data = tomllib.loads(scope_path.read_text(encoding="utf-8"))
            sc = data.get("scope", {})
            ins = sc.get("in_scope", [])
            outs = sc.get("out_of_scope", [])
            prog = data.get("program", {})
            scope_summary = (
                [f"Program : {prog.get('name', slug)} "
                 f"({prog.get('platform', '?')})"]
                + [f"In-scope : {s}" for s in ins]
                + [f"EXCLUDED : {s}" for s in outs])
        except Exception as exc:
            scope_summary = [f"(bb.toml parse error: {exc})"]

    signals = _scan_tech_signals(slug)
    blob = "\n".join(s[1] for s in signals).lower()
    routed = []
    seen = set()
    for rx, skill, why in TECH_SKILL_MAP + FINDING_SKILL_MAP:
        if re.search(rx, blob) and skill not in seen and (SKILLS_DIR / skill).is_dir():
            routed.append((skill, why))
            seen.add(skill)

    phases = [
        ("P0 - Passive triage", ["bbp-triagetalon-pro", "bbp-program-triage"]),
        ("P1 - Active recon", ["bbp-web-recon"]),
        ("P2 - Tech-routed attacks", [s for s, _ in routed]),
        ("P3 - Core web battery",
         ["bbp-auth-bypass", "bbp-api-audit", "bbp-business-logic",
          "bbp-xss-hunter", "bbp-sqli-hunter"]),
        ("P4 - Closing", []),
    ]
    md = ["# HUNT PLAN - " + slug, "",
          f"_Generated {datetime.now().isoformat(timespec='seconds')}_", "",
          "## Scope (RTFS CHECKPOINT)", "```"] + scope_summary + ["```", ""]
    md += ["## Phase checklist", ""]
    for title, sk in phases:
        md.append(f"### {title}")
        if not sk:
            md.append("- [ ] Final scope sweep: "
                      "`python bbcore/cli.py scope " + slug + " --sweep`")
            md.append("- [ ] Every finding re-checked: "
                      "`python bbcore/cli.py scope " + slug + " --check <asset>`")
        for s in sk:
            md.append(f"- [ ] Load skill `{s}` and execute its workflow")
        md.append("")
    md += ["## Hard rules", "",
           "- Out-of-scope asset found by accident: STOP, do not touch.",
           "- Evidence first, screenshot during action, save OOB logs locally.",
           "- 3 bypass attempts minimum before declaring unexploitable."]
    out = pdir / "HUNT_PLAN.md"
    out.write_text("\n".join(md), encoding="utf-8")
    print(f"[+] Hunt plan written: {out}")
    if routed:
        print(f"    Routed {len(routed)} tech-specific skills into the plan.")
    return 0


# --------------------------------------------------------------------------
# 6. Scope guard (RTFS protection)
# --------------------------------------------------------------------------

_WILDCARD_OK = re.compile(r"^[a-z0-9*\-.]+$")


def load_scope(slug: str):
    pdir = _program_dir(slug)
    scope_path = pdir / "policy" / "bb.toml"
    if not scope_path.exists():
        scope_path = pdir / "bb.toml"
    if not scope_path.exists():
        return None
    if tomllib:
        data = tomllib.loads(scope_path.read_text(encoding="utf-8"))
        sc = data.get("scope", {})
        return {"in": [str(x).lower() for x in sc.get("in_scope", [])],
                "out": [str(x).lower() for x in sc.get("out_of_scope", [])]}
    # minimal fallback parser (lines inside arrays)
    ins, outs, bucket = [], [], None
    for line in scope_path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("in_scope"): bucket = ins; continue
        if s.startswith("out_of_scope"): bucket = outs; continue
        if bucket is not None:
            m = re.match(r'^"([^"]+)"', s)
            if m: bucket.append(m.group(1).lower())
            elif "]" in s: bucket = None
    return {"in": ins, "out": outs}


def _matches(a: str, pat: str) -> bool:
    """Bug-bounty wildcard semantics: '*.x.com' matches x.com AND any sub."""
    pat = (pat or "").lower().strip().rstrip("/")
    if pat.startswith("*."):
        base = pat[2:]
        return a == base or a.endswith("." + base)
    return a == pat


def check_asset(scope, asset: str):
    a = asset.strip().lower()
    if "://" in a:
        a = urlparse(a).netloc or a
    a = a.split("/")[0].split(":")[0].lstrip(".")
    for pat in scope.get("out", []):
        if _matches(a, pat):
            return "OUT", f"matches EXCLUSION {pat}"
    for pat in scope.get("in", []):
        # Explicit match only. Short names like 'api' do NOT match
        # 'api.example.com' — add the full host to bb.toml instead.
        # (The old prefix heuristic caused false-IN verdicts.)
        if _matches(a, pat):
            return "IN", f"matches scope entry {pat}"
    return "UNKNOWN", ("no explicit match - treat as OUT until proven otherwise"
                       " (RTFS!)")


_DOMAIN_RE = re.compile(
    r"\b(?:[a-z0-9](?:[a-z0-9\-]*[a-z0-9])?\.)+[a-z]{2,}\b", re.IGNORECASE)


def run_scope(args):
    """scope <slug> [--check <asset>] [--sweep]"""
    if not args:
        print("[-] Usage: scope <slug> [--check <asset>] [--sweep]")
        return 1
    slug = args[0]
    scope = load_scope(slug)
    if scope is None:
        print("[-] No bb.toml found. Fill scope FIRST: "
              "programs/<slug>/policy/bb.toml")
        return 1

    if "--check" in args:
        idx = args.index("--check")
        if len(args) <= idx + 1:
            print("[-] --check requires an asset (domain/url)")
            return 1
        asset = args[idx + 1]
        verdict, reason = check_asset(scope, asset)
        icon = {"IN": "[+]", "OUT": "[!]", "UNKNOWN": "[?]"}.get(verdict, "[?]")
        print(f"{icon} VERDICT: {verdict:7s} | {asset}")
        print(f"    reason: {reason}")
        if verdict != "IN":
            print("    >>> DO NOT TEST THIS ASSET. Re-read the program policy.")
        return 0 if verdict == "IN" else 2

    if "--sweep" in args:
        pdir = _program_dir(slug)
        violations = {}
        checked = 0
        for sub in ("evidence", "reports", "recon"):
            base = pdir / sub
            if not base.is_dir():
                continue
            for f in base.rglob("*"):
                if not f.is_file() or f.suffix.lower() in (".png", ".jpg",
                                                           ".jpeg", ".gif",
                                                           ".zip", ".pdf"):
                    continue
                try:
                    text = f.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                domain_hits = sorted(set(_DOMAIN_RE.findall(text)))
                for m in domain_hits:
                    checked += 1
                    v, reason = check_asset(scope, m)
                    if v == "OUT":
                        violations.setdefault(m, []).append(
                            f"{sub}/{f.name}: {reason}")
        print(f"[*] Sweep complete. Unique domains evaluated: {checked}")
        print("[*] Note: .png/.jpg/.zip/.pdf skipped (no OCR) — check screenshots manually.")
        if not violations:
            print("[+] CLEAN - no out-of-scope assets referenced in artifacts.")
            return 0
        print(f"[!] {len(violations)} OUT-OF-SCOPE domains appear in your "
              "artifacts:")
        for dom, where in sorted(violations.items()):
            print(f"  [!] {dom}")
            for w in where[:3]:
                print(f"      - {w}")
        print(">>> Remove/redact these before submission, or justify why the")
        print(">>> reference exists (e.g., upstream doc quote). RTFS guard.")
        return 2

    # default: show scope card
    print("=" * 62)
    print(" SCOPE CARD (memorize before every session)")
    print("=" * 62)
    for pat in scope["in"]:
        print(f"  IN      {pat}")
    for pat in scope["out"]:
        print(f"  OUT     {pat}")
    print("-" * 62)
    print(" usage: scope <slug> --check <asset>   before touching anything")
    print("        scope <slug> --sweep            before closing/reporting")
    return 0
