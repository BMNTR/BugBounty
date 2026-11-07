#!/usr/bin/env python3
"""
BBOrch CLI — direct Python entry point for BugBounty Orchestrator.
Usage: python cli.py <command> [args...]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from bbcore.orchestrator import Orchestrator

orc = Orchestrator()


def cmd_init(args):
    url = args[0] if args else ""
    name = args[1] if len(args) > 1 else None
    slug = orc.init_program(url, name)
    print(f"[+] Program: {slug.slug}")
    print(f"    Type:   {slug.get('classification')}")
    print(f"    Dir:    {slug.dir}")


def cmd_recon(args):
    domain = args[0] if args else ""
    skip_nuclei = "--skip-nuclei" in args or "-sn" in args
    skip_ffuf = "--skip-ffuf" in args or "-sf" in args
    result = orc.run_recon(domain, skip_nuclei=skip_nuclei, skip_ffuf=skip_ffuf)
    print(json.dumps(result, indent=2))


def cmd_proxy(args):
    if not args:
        print(f"Proxy: {orc.proxy.status_text()} | Mode: {orc.proxy.mode}")
        return
    mode = args[0]
    if mode == "direct":
        orc.set_proxy_mode("direct")
        print("[+] Proxy: Direct")
    elif mode == "tor":
        ok = orc.start_tor()
        print(f"[+] Tor: {'started' if ok else 'FAILED'}")
    elif mode == "static":
        url = args[1] if len(args) > 1 else ""
        orc.set_proxy_static(url)
        print(f"[+] Proxy: static {url}")
    elif mode == "rotate":
        f = args[1] if len(args) > 1 else ""
        orc.load_proxy_file(f)
    s = orc.status()
    print(f"  Mode: {s['proxy_mode']} | Status: {s['proxy_status']}")


def cmd_report(args):
    slug = args[0] if args else ""
    orc.generate_report(slug)


def cmd_status(args):
    s = orc.status()
    print(json.dumps(s, indent=2))


def cmd_programs(args):
    for p in orc.list_programs():
        print(f"  {p.get('slug','?'):25s} status={p.get('status','?'):20s} url={p.get('url','?')}")


def cmd_skills(args):
    for s in orc.skills.list_available():
        print(f"  {s}")
    print(f"\nTotal: {len(orc.skills.list_available())} skills")


def cmd_source(args):
    path = args[0] if args else "."
    print(orc.run_source_audit(path))

def cmd_secrets(args):
    path = args[0] if args else "."
    print(orc.run_secrets_scan(path))

def cmd_mobile(args):
    apk = args[0] if args else ""
    if not apk:
        print("[-] Usage: mobile <apk_path>"); return
    print(orc.run_mobile_audit(apk))

def cmd_deps(args):
    path = args[0] if args else "."
    print(orc.run_dependency_audit(path))

def cmd_help(args):
    print("""BugBounty Orchestrator CLI

Commands:
  init <url> [slug]         - Init workspace (+ bb.toml)
  recon <domain>            - WAF-aware recon pipeline
  jsrecon <slug> [seed]     - JS bundle intel: endpoints/secrets/sourcemaps
  route <slug> [--dry]      - Tech-detect -> auto-queue matching skills
  diff <slug> [--no-update] - Delta vs baseline recon (new/gone assets)
  oob <slug> start|stop|status|tail - Per-program interactsh session log
  plan <slug>               - Generate HUNT_PLAN.md (scope + routed phases)
  scope <slug> [--check <asset>|--sweep] - RTFS guard vs policy/bb.toml
  next <slug> / next-done <slug> [--skip] - consume skill queue (route output)
  backup <slug>...|--all   - zip program evidence into _backups/
  doctor                   - one-shot environment health check
  proxy [mode] [arg]        - Proxy: direct|tor|static|rotate
  report <slug>             - Generate report from template
  source <path>             - Source code audit (semgrep+codeql)
  secrets <path>            - Secrets scan (gitleaks+trufflehog)
  mobile <apk_path>         - Mobile APK analysis (apktool+jadx)
  deps <path>               - Dependency vuln scan (trivy+grype)
  status                    - Show orchestrator status
  programs                  - List all program workspaces
  skills                    - List all available skills
  help                      - Show this help
""")


def cmd_triagetalon(args):
    domain = args[0] if args else ""
    if len(args) > 1:
        slug = args[1]
    elif orc.program:
        slug = orc.program.slug
    else:
        from bbcore.orchestrator import slugify
        slug = slugify(domain)
    if not domain:
        print("[-] Usage: triagetalon <domain> [slug]")
        return
    import subprocess
    recon_script = Path(__file__).resolve().parent.parent / "TriageTalon" / "recon_local_pro.py"
    cmd = [sys.executable, str(recon_script), domain, slug]
    subprocess.run(cmd)


def cmd_jsrecon(args):
    from bbcore.workflow_tools import run_js_recon
    sys.exit(run_js_recon(args) or 0)


def cmd_route(args):
    from bbcore.workflow_tools import run_route
    sys.exit(run_route(args) or 0)


def cmd_diff(args):
    from bbcore.workflow_tools import run_diff
    sys.exit(run_diff(args) or 0)


def cmd_oob(args):
    from bbcore.workflow_tools import run_oob
    sys.exit(run_oob(args) or 0)


def cmd_plan(args):
    from bbcore.workflow_tools import run_plan
    sys.exit(run_plan(args) or 0)


def cmd_scope(args):
    from bbcore.workflow_tools import run_scope
    sys.exit(run_scope(args) or 0)


def cmd_doctor(args):
    from bbcore.ops_tools import run_doctor
    sys.exit(run_doctor(args) or 0)


def cmd_next(args):
    from bbcore.ops_tools import run_next
    if "--done" in args or "--skip" in args:
        print("[-] Use: next-done <slug> [--skip]")
        return
    sys.exit(run_next(args) or 0)


def cmd_next_done(args):
    from bbcore.ops_tools import run_next_done
    sys.exit(run_next_done(args) or 0)


def cmd_backup(args):
    from bbcore.ops_tools import run_backup
    sys.exit(run_backup(args) or 0)


COMMANDS = {
    "init": cmd_init,
    "recon": cmd_recon,
    "triagetalon": cmd_triagetalon,
    "proxy": cmd_proxy,
    "report": cmd_report,
    "source": cmd_source,
    "secrets": cmd_secrets,
    "mobile": cmd_mobile,
    "deps": cmd_deps,
    "jsrecon": cmd_jsrecon,
    "route": cmd_route,
    "diff": cmd_diff,
    "oob": cmd_oob,
    "plan": cmd_plan,
    "scope": cmd_scope,
    "doctor": cmd_doctor,
    "next": cmd_next,
    "next-done": cmd_next_done,
    "backup": cmd_backup,
    "status": cmd_status,
    "programs": cmd_programs,
    "skills": cmd_skills,
    "help": cmd_help,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        cmd_help([])
        sys.exit(1)
    COMMANDS[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    main()
