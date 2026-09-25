#!/usr/bin/env python3
# triage_nuclei.py - Authorized-use-only local helper for bug bounty recon workspaces.
# Parses nuclei JSONL output files and prints findings sorted by severity so the
# operator can prioritize manual validation. Runs entirely offline on local files.

import json
import sys
from pathlib import Path

SEVERITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "info": 4,
    "unknown": 5,
}


def load_findings(paths):
    """Read one or more nuclei .jsonl files, return deduplicated finding dicts."""
    if not paths:
        print("[!] No input files given. Usage: triage_nuclei.py FILE.jsonl [FILE2.jsonl ...]")
        return []

    seen = set()
    findings = []
    for raw_path in paths:
        path = Path(raw_path)
        if not path.is_file():
            print("[!] Skipping missing file: {}".format(path))
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print("[!] Cannot read {}: {}".format(path, exc))
            continue

        for line_no, line in enumerate(text.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                # Older nuclei versions emit plain-text lines; skip them quietly.
                continue
            if not isinstance(entry, dict):
                continue

            info = entry.get("info") or {}
            sev = str(info.get("severity") or "unknown").lower()
            key = (
                str(entry.get("template-id") or info.get("name") or ""),
                str(entry.get("host") or entry.get("matched-at") or ""),
                str(entry.get("matched-at") or ""),
            )
            if key in seen:
                continue
            seen.add(key)
            findings.append(
                {
                    "severity": sev,
                    "template_id": key[0],
                    "name": str(info.get("name") or key[0] or "(unnamed)"),
                    "host": key[1],
                    "matched_at": key[2],
                    "file": "{}:{}".format(path.name, line_no),
                }
            )
    return findings


def main(argv):
    findings = load_findings(argv[1:])
    if not findings:
        print("[+] No structured findings found across inputs.")
        return 0

    findings.sort(key=lambda f: SEVERITY_ORDER.get(f["severity"], 99))

    counts = {}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1

    print("[+] Findings summary (deduplicated):")
    for sev in sorted(counts, key=lambda s: SEVERITY_ORDER.get(s, 99)):
        print("    {:8s} {}".format(sev, counts[sev]))
    print()

    current_sev = None
    for f in findings:
        if f["severity"] != current_sev:
            current_sev = f["severity"]
            print("=" * 70)
            print("[{}] {}".format(current_sev.upper(), "-" * max(0, 60 - len(current_sev))))
        print("  {} | {}".format(f["name"], f["host"]))
        if f["matched_at"] and f["matched_at"] != f["host"]:
            print("      matched: {}".format(f["matched_at"]))
        print("      source:  {}".format(f["file"]))
        print("      action:  re-send exact request manually before promoting to evidence/")
    print()
    print("[!] Nuclei output = leads, not confirmed bugs. Validate each manually.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
