#!/usr/bin/env python3
"""verify_hygiene.py - Automated repository hygiene, security, and integrity gatekeeper.

Validates:
1. No sensitive files or leaked credentials tracked in git.
2. Root directory strictly conforms to AGENTS.md allowed file list.
3. No emojis in scripts (.ps1, .bat, .sh).
4. All local skills have valid YAML frontmatter in SKILL.md.
"""

import sys
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ALLOWED_ROOT_ITEMS = {
    "AGENTS.md",
    "SKILL.md",
    "README.md",
    "LICENSE",
    ".env",
    ".gitignore",
    "manifest.json",
    "skills-lock.json",
    "opencode.json",
    "cookies.txt",
    "assets",
    "bbcore",
    "orchestrate.ps1",
    "tools",
    "TriageTalon",
    "wordlists",
    "scripts",
    "_scripts",
    "_templates",
    ".agents",
    "programs",
    "temp",
    "reports",
    "_backups",
    ".github",
    ".opencode",
    ".openteams",
    ".git",
    "tests",
}

FORBIDDEN_TRACKED_PATTERNS = [
    r"^\.env",
    r"^cookies\.txt",
    r".*\.pcap$",
    r".*\.pcapng$",
    r".*\.har$",
    r".*\.key$",
    r".*\.pem$",
    r".*\.pfx$",
    r".*token\.txt$",
    r".*tokens\.txt$",
    r".*credentials\.json$",
    r"^hs_err_pid.*",
    r"^replay_pid.*",
    r"^programs/.*",
    r"^temp/.*",
    r"^reports/.*",
    r"^_backups/.*",
    r"^tools/.*",
    r"^wordlists/.*",
]

EMOJI_PATTERN = re.compile(
    r"[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf]"
)


def check_git_tracked_hygiene():
    errors = []
    try:
        r = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
        )
        tracked = [line.strip() for line in r.stdout.splitlines() if line.strip()]
    except Exception as exc:
        return [f"Failed to query git ls-files: {exc}"]

    for f in tracked:
        for pat in FORBIDDEN_TRACKED_PATTERNS:
            if re.match(pat, f, re.IGNORECASE):
                errors.append(f"Forbidden file tracked in git: {f} (matched {pat})")

    return errors


def check_root_hygiene():
    errors = []
    for item in ROOT.iterdir():
        name = item.name
        if name not in ALLOWED_ROOT_ITEMS:
            errors.append(f"Disallowed root item found: {name}")
    return errors


def check_no_emojis_in_scripts():
    errors = []
    script_suffixes = {".ps1", ".bat", ".sh"}
    try:
        r = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
        )
        tracked = [line.strip() for line in r.stdout.splitlines() if line.strip()]
    except Exception:
        tracked = []

    for f in tracked:
        p = ROOT / f
        if p.suffix.lower() in script_suffixes and p.exists():
            try:
                content = p.read_text(encoding="utf-8", errors="replace")
                if EMOJI_PATTERN.search(content):
                    errors.append(f"Script contains emojis (violates AGENTS.md): {f}")
            except Exception as e:
                errors.append(f"Could not read {f}: {e}")
    return errors


def check_skills_integrity():
    errors = []
    skills_dir = ROOT / ".agents" / "skills"
    if not skills_dir.exists():
        return ["Skills directory .agents/skills not found!"]

    for d in skills_dir.iterdir():
        if d.is_dir():
            skill_md = d / "SKILL.md"
            if not skill_md.exists():
                errors.append(f"Skill {d.name} missing SKILL.md")
                continue
            try:
                lines = skill_md.read_text(encoding="utf-8", errors="replace").splitlines()
                if not (len(lines) >= 3 and lines[0].strip() == "---"):
                    errors.append(f"Skill {d.name}/SKILL.md missing opening YAML frontmatter '---'")
                else:
                    frontmatter = []
                    closed = False
                    for line in lines[1:]:
                        if line.strip() == "---":
                            closed = True
                            break
                        frontmatter.append(line)
                    if not closed:
                        errors.append(f"Skill {d.name}/SKILL.md unclosed YAML frontmatter")
                    else:
                        fm_text = "\n".join(frontmatter)
                        if "name:" not in fm_text:
                            errors.append(f"Skill {d.name}/SKILL.md frontmatter missing 'name:'")
                        if "description:" not in fm_text:
                            errors.append(f"Skill {d.name}/SKILL.md frontmatter missing 'description:'")
            except Exception as e:
                errors.append(f"Error reading {skill_md}: {e}")
    return errors


def main():
    print("=" * 60)
    print(" REPOSITORY HYGIENE & INTEGRITY GATE")
    print("=" * 60)

    all_errors = []

    print("[*] Checking git tracked files for sensitive data...")
    tracked_errors = check_git_tracked_hygiene()
    if tracked_errors:
        all_errors.extend(tracked_errors)
        for e in tracked_errors:
            print(f"  [!] {e}")
    else:
        print("  [+] Clean - zero sensitive files tracked.")

    print("[*] Checking workspace root hygiene...")
    root_errors = check_root_hygiene()
    if root_errors:
        all_errors.extend(root_errors)
        for e in root_errors:
            print(f"  [!] {e}")
    else:
        print("  [+] Clean - root strictly matches allowed table.")

    print("[*] Checking scripts for forbidden emojis...")
    emoji_errors = check_no_emojis_in_scripts()
    if emoji_errors:
        all_errors.extend(emoji_errors)
        for e in emoji_errors:
            print(f"  [!] {e}")
    else:
        print("  [+] Clean - zero emojis in scripts.")

    print("[*] Checking skills frontmatter integrity...")
    skills_errors = check_skills_integrity()
    if skills_errors:
        all_errors.extend(skills_errors)
        for e in skills_errors:
            print(f"  [!] {e}")
    else:
        print("  [+] Clean - all skills have valid YAML frontmatter.")

    print("-" * 60)
    if all_errors:
        print(f"[!] FAILED: {len(all_errors)} hygiene issue(s) detected.")
        sys.exit(1)
    else:
        print("[+] SUCCESS: All repository hygiene & security gates PASSED!")
        sys.exit(0)


if __name__ == "__main__":
    main()
