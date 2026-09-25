param([Parameter(Mandatory=$true)][string]$Path)
if (-not (Test-Path -LiteralPath $Path)) {
  Write-Host "[!] File not found: $Path" -ForegroundColor Red
  exit 1
}
$Host.UI.RawUI.WindowTitle = "EVIDENCE - $([System.IO.Path]::GetFileName($Path))"
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " EVIDENCE: $Path" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Get-Content -LiteralPath $Path
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " End of evidence - screenshot this window for report."
Write-Host "====================================================" -ForegroundColor Cyan