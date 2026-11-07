---
name: bbp-rea-wrapper
description: Wrapper for REA (Reverse Engineering Assistant) CLI and MCP server for binary, mobile APK, Electron, and native application reverse engineering.
---

# REA Wrapper Skill

Wrapper untuk REA (Reverse Engineering Assistant) oleh morluto/rea — CLI + MCP server untuk reverse engineering binary, mobile apps, Electron apps, dan native applications.

## Prerequisites

- Node.js >= 22.19.0
- REA installed globally: `npm install -g rea-agents`
- Optional: Hopper Disassembler (macOS/Linux) untuk decompilation mendalam
- Optional: Ghidra 12.1.4 + JDK 21 untuk read-only analysis

## Usage

## Batasan Windows (verified 2026-10-05, REA 3.2.1 + Ghidra 12.1.4)
- Deep native analysis (decompile PE/ELF/Mach-O via hopper/ghidra) **DITOLAK di Windows** oleh admission gate REA (`unsupported_host` — Job Object/DACL proof belum diimplementasi upstream).
- Yang **jalan di Windows**: JS/Electron artifact analysis (`analyze-javascript-application`), managed .NET static, evidence/compare, browser & Electron observation, V8 Inspector.
- Untuk decompile APK/native depth di Windows: pakai skill `bbp-mobile-reverse-engine` (jadx/apktool) atau WSL + Ghidra langsung.

### Via CLI (Standalone)

```powershell
# Basic recon pada target in-scope
.\.agents\skills\bbp-rea-wrapper\scripts\rea-recon.ps1 -TargetPath "C:\path\to\target.apk" -Slug "myprogram"

# Dengan provider spesifik
.\.agents\skills\bbp-rea-wrapper\scripts\rea-recon.ps1 -TargetPath "C:\path\to\target.app" -Slug "myprogram" -Provider hopper
```

### Via MCP (Claude Code, Cursor, dll)

Tambahkan ke config MCP client:
```json
{
  "mcpServers": {
    "rea": {
      "command": "npx",
      "args": ["-y", "rea-agents@latest", "mcp"]
    }
  }
}
```

Atau gunakan file config siap pakai: `C:\BugBounty\.agents\skills\bbp-rea-wrapper\scripts\mcp-rea.json`

## Available MCP Tools (100+)

### Session Management
- `open_binary` — Buka target, pilih provider (hopper/ghidra/auto)
- `close_binary` — Tutup session, simpan snapshot
- `get_evidence_bundle` — Ambil evidence immutable
- `export_evidence_bundle` / `import_evidence_bundle` — Portability

### Static Analysis (Artifact Provider)
- `inspect_artifact` — Inspect APK, IPA, ASAR, Mach-O, ELF, PE, plist
- `list_documents` / `list_procedures` / `list_strings` / `list_names` / `list_segments`
- `extract_artifact` — Ekstrak file dari archive

### Deep Analysis (Hopper/Ghidra Provider)
- `procedure_pseudo_code` / `procedure_assembly` — Decompile fungsi
- `get_call_graph` — Call graph lengkap
- `find_xrefs_to_name` — Cross-references ke symbol/string
- `trace_feature` — Trace fitur dari string ke code
- `batch_decompile` — Decompile batch procedures
- `analyze_function` — Analisis mendalam single function

### Native macOS (No Hopper needed)
- `inspect_macho` — Mach-O metadata, code signatures
- `inspect_plist` — Parse Info.plist, entitlements
- `inspect_signature` — Code signature verification
- `list_architectures` — Arsitektur binary
- `demangle_swift` — Swift symbol demangling

### JavaScript/Electron/Browser
- `analyze_javascript_application` — Static ASAR/JS graph
- `reconcile_javascript_runtime` — Static + runtime reconciliation
- `inspect_electron_page` / `list_electron_targets` — Electron renderer inspection
- `list_browser_targets` / `inspect_web_page` / `observe_web_session` — CDP passive observation
- `list_javascript_runtime_targets` / `observe_javascript_runtime` — V8 Inspector attach-only

### Managed Code (.NET/PE)
- `inspect_managed_artifact` — PE/CLI metadata
- `inspect_managed_members` — Type/method inventory
- `inspect_managed_native_boundaries` — P/Invoke, native boundaries
- `verify_managed_native_boundaries` — Verify P/Invoke declarations

### Evidence & Comparison
- `compare_evidence_bundles` — Compare dua evidence bundle
- `compare_function_dossiers` — Compare function-level changes
- `compare_process_captures` — Compare process capture runs
- `verify_reconstruction` — Verify reconstruction specs

## Output Structure

```
programs/<slug>/
├── recon/
│   ├── <target>_<timestamp>_overview.json      # Binary overview
│   ├── <target>_<timestamp>_secrets.json       # Secret patterns found
│   ├── <target>_<timestamp>_traces.json        # Feature traces
│   ├── <target>_<timestamp>_procedures.json    # All procedures
│   ├── <target>_<timestamp>_strings.json       # All strings
│   └── <target>_<timestamp>_names.json         # All symbols
└── evidence/
    └── <target>_<timestamp>_evidence.json      # Immutable evidence bundle
```

## Scope & Safety Rules

| ✅ Allowed | ❌ Forbidden |
|------------|--------------|
| Target **in-scope** mobile/desktop app | Target out-of-scope |
| Binary resmi (Play Store, App Store, vendor) | Binary dari sumber tidak resmi |
| Analisis **static/local only** | Dynamic analysis butuh MITM user lain |
| Evidence untuk laporan triager | PoC destructive (RCE, data exfil) |

## Integration dengan bbcore

```powershell
# Di orchestrate.ps1 recon phase, tambahkan:
.\.agents\skills\bbp-rea-wrapper\scripts\rea-recon.ps1 -TargetPath $apkPath -Slug $slug
```

## Troubleshooting

**`rea doctor` / `rea setup` error `spawn EINVAL` di Windows:**
- Root cause: REA probe `npm.CMD`/`npx.CMD` via `spawn` tanpa `shell:true` → Node throw EINVAL (upstream bug, draft issue di `.agents/skills/bbp-rea-wrapper/scripts/rea-upstream-issue-draft.md`)
- Sudah di-patch lokal. Kalau error muncul lagi (habis `npm update -g rea-agents`), jalankan ulang:
  ```powershell
  powershell -ExecutionPolicy Bypass -File "C:\BugBounty\.agents\skills\bbp-rea-wrapper\scripts\rea-win32-fix.ps1"
  ```

**Hopper tidak terdeteksi:**
```bash
export HOPPER_LAUNCHER_PATH=/Applications/Hopper\ Disassembler.app/Contents/MacOS/hopper
rea doctor --json
```

**Ghidra tidak terdeteksi:**
```bash
export GHIDRA_INSTALL_DIR=/path/to/ghidra_12.1.4_PUBLIC
export JAVA_HOME=/path/to/jdk-21
rea doctor --json
```

## References

- Repo: https://github.com/morluto/rea
- Docs: https://github.com/morluto/rea/tree/main/docs
- NPM: https://www.npmjs.com/package/rea-agents