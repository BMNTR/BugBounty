#!/usr/bin/env python3
# hash_evidence.py - Authorized-use-only local helper for bug bounty evidence folders.
# Generates a MANIFEST.txt containing SHA256 hashes, sizes, and timestamps for every
# file in one or more evidence directories. Runs entirely offline on local files.

import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

MANIFEST_NAME = "MANIFEST.txt"


def sha256_of(path, chunk_size=65536):
    """Stream-hash a file. Returns hex digest or None on read failure."""
    digest = hashlib.sha256()
    try:
        with open(path, "rb") as handle:
            while True:
                chunk = handle.read(chunk_size)
                if not chunk:
                    break
                digest.update(chunk)
    except OSError as exc:
        print("[!] Cannot read {}: {}".format(path, exc))
        return None
    return digest.hexdigest()


def process_folder(folder):
    """Hash every regular file in folder; return (manifest_lines, ok_count, fail_count)."""
    lines = [
        "MANIFEST generated: {}".format(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")),
        "Folder: {}".format(folder.resolve()),
        "Algorithm: SHA256",
        "-" * 100,
        "{:<64} {:<12} {:<24} {}".format("SHA256", "BYTES", "MODIFIED (UTC)", "FILE"),
    ]
    ok = 0
    failed = 0

    try:
        entries = sorted(p for p in folder.iterdir() if p.is_file())
    except OSError as exc:
        print("[!] Cannot list {}: {}".format(folder, exc))
        return [], 0, 1

    for path in entries:
        if path.name == MANIFEST_NAME:
            continue
        file_hash = sha256_of(path)
        if file_hash is None:
            failed += 1
            continue
        try:
            stat = path.stat()
            size = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        except OSError as exc:
            print("[!] Stat failed for {}: {}".format(path, exc))
            size = -1
            modified = "unknown"
        rel_name = path.name
        if len(rel_name) > 30:
            rel_name = "..." + rel_name[-27:]
        lines.append("{:<64} {:<12} {:<24} {}".format(file_hash, size, modified, rel_name))
        print("[+] {} ({})".format(file_hash[:16], path.name))
        ok += 1
    return lines, ok, failed


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("-")]
    if not args:
        print("Usage: hash_evidence.py <evidence-folder> [<folder2> ...]")
        print("Writes MANIFEST.txt into each folder with SHA256 of all files.")
        return 1

    total_ok = 0
    total_fail = 0
    for raw in args:
        folder = Path(raw)
        if not folder.is_dir():
            print("[!] Not a directory, skipping: {}".format(folder))
            total_fail += 1
            continue

        lines, ok, failed = process_folder(folder)
        manifest_path = folder / MANIFEST_NAME
        try:
            manifest_path.write_text("\n".join(lines) + "\n", encoding="ascii")
            print("[+] Wrote {} ({} files hashed)".format(manifest_path, ok))
        except OSError as exc:
            print("[!] Cannot write {}: {}".format(manifest_path, exc))
            failed += 1
        total_ok += ok
        total_fail += failed

    print()
    print("[+] Summary: {} files hashed, {} errors/skips.".format(total_ok, total_fail))
    return 0 if total_fail == 0 else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
