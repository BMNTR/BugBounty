<#
.SYNOPSIS
    Re-apply the Windows spawn EINVAL fix to REA (morluto/rea) after install/upgrade.
.DESCRIPTION
    Root cause: dist/application/RuntimeExecutableDiagnostics.js calls
    spawn(path, ['--version']) without shell:true. On Windows, npm/npx resolve
    to npm.CMD / npx.CMD, and Node throws EINVAL synchronously for script
    files spawned without a shell. The throw escapes the Promise executor,
    rejects inspectRuntimeExecutables(), and crashes `rea doctor` + `rea setup`
    with {"code":"UNKNOWN","message":"spawn EINVAL"}.

    This script patches the installed file idempotently:
      1. .cmd/.bat candidates are probed via cmd shell (quoted path).
      2. Any other synchronous spawn throw resolves as an unhealthy
         candidate instead of crashing doctor/setup.

    Re-run after every `npm install -g rea-agents` / `npm update -g rea-agents`.
    Upstream issue: https://github.com/morluto/rea/issues (spawn EINVAL on Windows)
#>

$ErrorActionPreference = 'Stop'

$target = Join-Path (npm root -g) 'rea-agents/dist/application/RuntimeExecutableDiagnostics.js'

if (-not (Test-Path $target)) {
    Write-Error "REA dist file not found: $target (is rea-agents installed globally?)"
    exit 1
}

$content = Get-Content $target -Raw

if ($content -match 'requiresShellExecution') {
    Write-Host '[=] Patch already applied, nothing to do.' -ForegroundColor Gray
    exit 0
}

$old = @'
const executeVersion = (path, timeoutMs, effectivePath) => new Promise((resolve) => {
    const child = spawn(path, ["--version"], {
        windowsHide: true,
        env: environmentWithPath(effectivePath),
        stdio: ["ignore", "pipe", "pipe"],
    });
'@

$new = @'
/** Windows script shims (.cmd/.bat, e.g. npm/npx) cannot be spawned without a shell. */
const requiresShellExecution = (path) => process.platform === "win32" &&
    (path.toLowerCase().endsWith(".cmd") || path.toLowerCase().endsWith(".bat"));
const executeVersion = (path, timeoutMs, effectivePath) => new Promise((resolve) => {
    const scripted = requiresShellExecution(path);
    let child;
    try {
        child = spawn(scripted ? `"${path}"` : path, ["--version"], {
            windowsHide: true,
            env: environmentWithPath(effectivePath),
            stdio: ["ignore", "pipe", "pipe"],
            ...(scripted ? { shell: true } : {}),
        });
    }
    catch (cause) {
        resolve({
            ok: false,
            failure: classifyProbeFailure(cause instanceof Error ? cause : new Error("Runtime version probe failed to start"), { exitCode: null, signalCode: null }, ""),
        });
        return;
    }
'@

if (-not $content.Contains($old)) {
    Write-Error 'Expected code block not found - dist file may have changed upstream. Review manually.'
    exit 1
}

$content = $content.Replace($old, $new)
Set-Content -NoNewline -Encoding utf8 $target $content

Write-Host '[+] Patch applied. Verifying with `rea doctor`...' -ForegroundColor Cyan
rea doctor --json | Select-Object -First 5 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host '[+] `rea doctor` completed without crash.' -ForegroundColor Green
} else {
    Write-Host '[!] `rea doctor` still exits non-zero - check output (may be legit FAILs like missing Hopper).' -ForegroundColor Yellow
}
