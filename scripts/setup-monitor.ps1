param(
    [Parameter(Mandatory=$true)]
    [string]$TargetUrl,
    
    [Parameter(Mandatory=$false)]
    [string]$ProgramName = "bugbounty",
    
    [Parameter(Mandatory=$false)]
    [int]$Hours = 6
)

$actionScript = "C:\BugBounty\scripts\program.ps1"
$taskName = "BugBountyMonitor_$ProgramName"

# Delete existing task if present
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue | Out-Null

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$actionScript`" -Url `"$TargetUrl`" -ProgramName `"$ProgramName`""
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours $Hours)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal | Out-Null

Write-Output "[+] Task Scheduler registered: $taskName"
Write-Output "    It will run every $Hours hours completely in the background."
Write-Output "    Target: $TargetUrl"
Write-Output "    You will receive Discord notifications when new findings appear."
