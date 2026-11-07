<#
.SYNOPSIS
  BugBounty Orchestrator — unified CLI for proxy, recon, skills, reporting, and browser.
.DESCRIPTION
  Delegates to bbcore/cli.py for all commands. One entry point for everything.
.EXAMPLE
  .\orchestrate.ps1 status
  .\orchestrate.ps1 recon example.com
  .\orchestrate.ps1 proxy tor
  .\orchestrate.ps1 browser
#>
param(
  [Parameter(Position=0)][string]$Command,
  [Parameter(ValueFromRemainingArguments=$true)]$Args_
)

$BB_DIR = if ($PSScriptRoot) { $PSScriptRoot } else { "C:\BugBounty" }
$PYTHON = "python"
$CLI_PY = Join-Path $BB_DIR "bbcore\cli.py"

switch ($Command) {
  'browser' {
    $browserPath = "C:\ProjectBrowser\main.py"
    if (-not (Test-Path $browserPath)) { Write-Host "[-] Browser not found"; exit 1 }
    Write-Host "[+] Launching Shield Browser..."
    & $PYTHON $browserPath
  }
  'wsl' {
    $cmd = $Args_ -join ' '
    Write-Host "[+] Executing in Ubuntu WSL: $cmd"
    wsl bash -c "$cmd"
  }
  default {
    if (-not $Command -or $Command -eq 'help') {
      & $PYTHON $CLI_PY help
    } else {
      & $PYTHON $CLI_PY $Command @Args_
    }
  }
}
