# Upstream issue draft — morluto/rea (file manual, token tidak punya akses issues)

URL: https://github.com/morluto/rea/issues/new

## Title
`rea doctor` / `rea setup` crash on Windows with spawn EINVAL (npm/npx .CMD probe)

## Body
(structured report — copy-paste)

---
## Summary
`rea doctor` and `rea setup` crash on Windows with `{"code":"UNKNOWN","message":"spawn EINVAL"}` instead of reporting diagnostics.

## Environment
- OS: Windows 11 x64
- Node: v22.22.2 (also affects any Node on Windows)
- rea-agents: 3.2.1 (global npm install)

## Root cause
`dist/application/RuntimeExecutableDiagnostics.js` → `executeVersion()` does:

```js
const child = spawn(path, ["--version"], { windowsHide: true, env, stdio: [...] });
```

`discoverToolCandidates()` on win32 resolves `npm`/`npx` to `npm.CMD` / `npx.CMD`. Spawning a `.CMD`/`.BAT` without `shell: true` throws **synchronously** (`EINVAL`) on Windows. The throw happens inside the `new Promise` executor, so it becomes a rejection that propagates through `probeCandidate` → `mapConcurrentBounded` → `inspectRuntimeExecutables` → `collectDoctorDiagnostics`, crashing both `doctor` and `setup` (both go through `createSystemDoctorHost()`).

Stack trace (via direct `runDoctor` import):

```
Error: spawn EINVAL
    at ChildProcess.spawn (node:internal/child_process:420:11)
    at spawn (node:child_process:787:9)
    at .../dist/application/RuntimeExecutableDiagnostics.js:79:19
    at executeVersion (.../RuntimeExecutableDiagnostics.js:78:60)
```

Verified: `spawn('C:\Program Files\nodejs\npm.CMD', ['--version'])` throws `EINVAL` synchronously; with `shell: true` + quoted path it returns the version correctly.

## Suggested fix
In `executeVersion()`:

1. Route `.cmd`/`.bat` candidates through the shell with a quoted path:
```js
const scripted = process.platform === "win32" &&
  (path.toLowerCase().endsWith(".cmd") || path.toLowerCase().endsWith(".bat"));
child = spawn(scripted ? `"${path}"` : path, ["--version"], {
  ...,
  ...(scripted ? { shell: true } : {}),
});
```
2. Wrap `spawn` in try/catch so any future synchronous spawn throw resolves as an unhealthy candidate (`runtime_spawn_failed`) instead of crashing the whole doctor run. Note `runtimeChecks()` marks `node-toolchains` failed if ANY candidate is unhealthy, so fix (1) matters — a catch-only fix would still report healthy toolchains as broken.

## Impact
Every standard Windows Node installation (npm/npx are `.CMD` shims) hits this — `doctor`/`setup` are unusable on Windows without the patch.

## Local workaround applied
Patched installed dist file + saved re-apply script at `programs/_shared/scripts/rea-win32-fix.ps1` (idempotent, re-run after every rea-agents upgrade until upstream fixes it).
---
