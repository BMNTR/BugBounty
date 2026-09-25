param(
  [string]$ProcessName = 'WindowsTerminal',
  [string]$TitleMatch = 'Windows PowerShell',
  [string]$OutPath = 'C:\BugBounty\programs\toom-baumarkt-ywh\evidence\window-shot.png'
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

Add-Type @'
using System;
using System.Runtime.InteropServices;
public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
public class W32 {
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
  [DllImport("dwmapi.dll")] public static extern int DwmGetWindowAttribute(IntPtr hWnd, int dwAttribute, out RECT pvAttribute, int cbAttribute);
}
'@
[W32]::SetProcessDPIAware() | Out-Null

$p = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue |
     Where-Object { $_.MainWindowHandle -ne 0 -and $_.MainWindowTitle -like "*$TitleMatch*" } |
     Select-Object -First 1
if (-not $p) { Write-Host "[!] window not found: $ProcessName / $TitleMatch"; exit 1 }

[W32]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 600

$r = New-Object RECT
$ok = $false
try {
  $hr = [W32]::DwmGetWindowAttribute($p.MainWindowHandle, 9, [ref]$r, [System.Runtime.InteropServices.Marshal]::SizeOf([type][RECT]))
  if ($hr -eq 0) { $ok = $true } else { [W32]::GetWindowRect($p.MainWindowHandle, [ref]$r) | Out-Null; $ok = $true }
} catch {
  [W32]::GetWindowRect($p.MainWindowHandle, [ref]$r) | Out-Null; $ok = $true
}
$w = $r.Right - $r.Left
$h = $r.Bottom - $r.Top
Write-Host "[*] bounds: ${w}x${h} title=$($p.MainWindowTitle)"

$bmp = New-Object System.Drawing.Bitmap($w, $h)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc()
$okPrint = [W32]::PrintWindow($p.MainWindowHandle, $hdc, 2)
$g.ReleaseHdc($hdc)
if (-not $okPrint) {
  Write-Host "[*] PrintWindow returned false, fallback: CopyFromScreen"
  $g.Dispose(); $bmp.Dispose()
  $bmp = New-Object System.Drawing.Bitmap($w, $h)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  try { $g.CopyFromScreen($r.Left, $r.Top, 0, 0, $bmp.Size) } catch { Write-Host "[!] capture failed: $_"; exit 1 }
}
$bmp.Save($OutPath, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()

# brightness/variance check to ensure not blank
Add-Type -AssemblyName System.Drawing
$chk = New-Object System.Drawing.Bitmap($OutPath)
$total = 0.0; $n = 0; $min = 255.0; $max = 0.0
for ($x = 0; $x -lt $chk.Width; $x += 16) {
  for ($y = 0; $y -lt $chk.Height; $y += 16) {
    $c = $chk.GetPixel($x, $y)
    $lum = ($c.R * 0.299) + ($c.G * 0.587) + ($c.B * 0.114)
    $total += $lum; $n++
    if ($lum -lt $min) { $min = $lum }
    if ($lum -gt $max) { $max = $lum }
  }
}
$chk.Dispose()
$avg = [Math]::Round($total / $n, 1)
$range = [Math]::Round($max - $min, 1)
Write-Host "[+] saved: $OutPath ($w x $h) lum_range=$range avg=$avg (blank if range<4)"