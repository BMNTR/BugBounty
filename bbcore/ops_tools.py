#!/usr/bin/env python3
"""ops_tools.py - workspace health, queue consumption, and evidence backup.

Modules:
  doctor   - one-shot environment health check (tools, wsl, env keys, git)
  next     - pop the next queued skill item from state.json and print
             the workflow entrypoint for the agent
  backup   - timestamped zip archive of a program folder into _backups/

ASCII only. No emojis. Null-guarded throughout.
"""

import json
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

BB_DIR = Path(__file__).resolve().parent.parent
PROGRAMS_DIR = BB_DIR / "programs"
SKILLS_DIR = BB_DIR / ".agents" / "skills"
BACKUPS_DIR = BB_DIR / "_backups"


# --------------------------------------------------------------------------
# doctor
# --------------------------------------------------------------------------

def _check(name: str, ok: bool, detail: str = "") -> bool:
    icon = "[+]" if ok else "[!]"
    line = f"  {icon} {name}"
    if detail:
        line += f" - {detail}"
    print(line)
    return ok


def run_doctor(args):
    """doctor - full environment health check."""
    print("=" * 62)
    print(" BUGBOUNTY WORKSPACE DOCTOR")
    print("=" * 62)
    problems = 0

    # python version
    v = sys.version_info
    vok = _check("python", v >= (3, 11),
                 f"{v.major}.{v.minor}.{v.micro} (tomllib needs 3.11+)")
    problems += 0 if vok else 1

    # WSL alive + core pipeline tools inside WSL
    try:
        r = subprocess.run(["wsl", "bash", "-lc", "echo ok"],
                           capture_output=True, timeout=20)
        wsl_ok = r.returncode == 0 and b"ok" in r.stdout
    except (OSError, subprocess.TimeoutExpired):
        wsl_ok = False
    problems += 0 if _check("wsl", wsl_ok) else 1

    if wsl_ok:
        tools = ("subfinder httpx nuclei ffuf katana gau interactsh-client").split()
        r = subprocess.run(
            ["wsl", "bash", "-lc",
             "for t in " + " ".join(tools) +
             "; do command -v $t >/dev/null 2>&1 && echo \"+ $t\" "
             "|| echo \"- $t\"; done"],
            capture_output=True, text=True, timeout=60)
        missing = [l.split()[1] for l in r.stdout.splitlines() if l.startswith("-")]
        have = len(tools) - len(missing)
        detail = ("missing: " + ",".join(missing)) if missing else ""
        ok = _check(f"wsl pipeline tools ({have}/{len(tools)})", not missing, detail)
        problems += 0 if ok else 1

    # local tools dir essentials
    for p in ("TriageTalon\\recon_local_pro.py", "bbcore\\cli.py",
              "_templates\\bb.toml", "scripts\\notify.ps1"):
        problems += 0 if _check(p, (BB_DIR / p).exists()) else 1

    # env keys present (names only, never values)
    env_file = BB_DIR / ".env"
    env_keys = set()
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8",
                                       errors="replace").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                env_keys.add(line.split("=", 1)[0].strip())
    expected = {"OPENAI_API_KEY"}
    miss_keys = sorted(expected - env_keys)
    kdetail = ("missing: " + ",".join(miss_keys)) if miss_keys else ""
    kok = _check(".env required keys", not miss_keys, kdetail)
    problems += 0 if kok else 1

    # git clean
    try:
        r = subprocess.run(["git", "status", "--short"], cwd=BB_DIR,
                           capture_output=True, text=True, timeout=30)
        dirty = r.stdout.strip()
        gdetail = dirty.splitlines()[0][:60] if dirty else ""
        gok = _check("git working tree clean", not dirty, gdetail)
        problems += 0 if gok else 1
    except (OSError, subprocess.TimeoutExpired):
        problems += 0 if _check("git", False, "not runnable") else 1

    # disk free on C:
    try:
        import shutil
        free_gb = shutil.disk_usage("C:\\").free / (1024 ** 3)
        dok = _check(f"disk free {free_gb:.0f} GB", free_gb > 5,
                     "low space" if free_gb <= 5 else "")
        problems += 0 if dok else 1
    except OSError:
        pass

    # skills integrity quick count (local baseline 76 as of 2026-09; global
    # skills in ~/.agents/skills resolve via SkillLoader fallback)
    n_skills = len([d for d in SKILLS_DIR.iterdir() if d.is_dir()]) \
        if SKILLS_DIR.is_dir() else 0
    problems += 0 if _check(f"skills installed ({n_skills})", n_skills >= 70) else 1

    # backups freshness warning
    backups = BACKUPS_DIR.glob("*.zip") if BACKUPS_DIR.is_dir() else []
    latest = max((b.stat().st_mtime for b in backups), default=0)
    age_days = (datetime.now().timestamp() - latest) / 86400 if latest else None
    if latest:
        _check(f"last backup {age_days:.1f} days ago", age_days <= 14,
               "run 'backup <slug>' per active program")
    else:
        _check("backups", False,
               "NONE yet - programs/ is NOT in git; use 'backup <slug>'")
        problems += 1

    print("-" * 62)
    if problems == 0:
        print("[+] ALL GREEN")
        return 0
    print(f"[!] {problems} issue(s) found - fix above before hunting.")
    return 1


# --------------------------------------------------------------------------
# next - consume state.json queue
# --------------------------------------------------------------------------

def run_next(args):
    """next <slug> - print next queued skill entrypoint."""
    if not args:
        print("[-] Usage: next <slug>")
        return 1
    slug = args[0]
    sf = PROGRAMS_DIR / slug / "state.json"
    if not sf.exists():
        print("[-] No state.json. Run 'route <slug>' after recon first.")
        return 1
    try:
        state = json.loads(sf.read_text(encoding="utf-8"))
    except ValueError:
        print("[-] state.json unreadable.")
        return 1
    queue = [q for q in state.get("queue", []) if q]
    doing = state.get("doing")
    if doing:
        print(f"[!] In-progress: {doing}")
        print("    Finish or clear it first: next <slug> --done|--skip")
        return 1
    if not queue:
        print("[+] Queue empty. Run 'route <slug>' after new recon data.")
        return 0

    nxt, rest = queue[0], queue[1:]
    skill = nxt[6:] if nxt.startswith("skill:") else nxt
    md = SKILLS_DIR / skill / "SKILL.md"
    wf = SKILLS_DIR / skill / "references" / "workflows.md"
    print(f"[>] NEXT: {skill}")
    print(f"    skill   : {md}")
    if wf.exists():
        print(f"    deep-dive: {wf}")
    print("    action  : load SKILL.md and execute its Workflow section now.")

    state["queue"] = rest
    state["doing"] = skill
    sf.write_text(json.dumps(state, indent=2), encoding="utf-8")

    if "--done" in args or "--skip" in args:
        pass  # handled below via explicit flags
    print(f"[+] state.json updated ({len(rest)} left in queue)")
    return 0


def run_next_done(args):
    """Mark current in-progress item done/skip: next-done <slug> [--skip]"""
    if not args:
        print("[-] Usage: next-done <slug> [--skip]")
        return 1
    slug = args[0]
    sf = PROGRAMS_DIR / slug / "state.json"
    if not sf.exists():
        print("[-] No state.json.")
        return 1
    state = json.loads(sf.read_text(encoding="utf-8"))
    doing = state.pop("doing", None)
    if not doing:
        print("[-] Nothing in progress.")
        return 1
    if "--skip" in args:
        skipped = state.setdefault("skipped", [])
        if doing not in skipped:
            skipped.append(doing)
        print(f"[-] Skipped: {doing}")
    else:
        done = state.setdefault("done", [])
        if doing not in done:
            done.append(doing)
        print(f"[+] Done: {doing}")
    sf.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return 0


# --------------------------------------------------------------------------
# backup - zip a program folder
# --------------------------------------------------------------------------

def run_backup(args):
    """backup <slug> [<slug2> ...] | backup --all"""
    targets = []
    if "--all" in args:
        targets = [d.name for d in PROGRAMS_DIR.iterdir() if d.is_dir()]
    elif args:
        targets = args
    else:
        print("[-] Usage: backup <slug>... | --all")
        return 1
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    made = 0
    for slug in targets:
        src = PROGRAMS_DIR / slug
        if not src.is_dir():
            print(f"[-] skip (not found): {slug}")
            continue
        dest = BACKUPS_DIR / f"{slug}_{stamp}.zip"
        n = 0
        with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
            for f in src.rglob("*"):
                if f.is_file():
                    try:
                        z.write(f, f.relative_to(src.parent))
                        n += 1
                    except OSError as exc:
                        print(f"[!] skip locked file {f.name}: {exc}")
        size_mb = dest.stat().st_size / (1024 * 1024)
        print(f"[+] {dest.name}  ({n} files, {size_mb:.1f} MB)")
        made += 1
    print(f"[+] {made} archive(s) in {BACKUPS_DIR}")
    print("[!] Zip lokal tetap single-copy. Sinkronkan _backups/ ke cloud/drive"
          " lain untuk perlindungan penuh.")
    return 0


COMMANDS = {
    "doctor": run_doctor,
    "next": run_next,
    "next-done": run_next_done,
    "backup": run_backup,
}
