# Create desktop shortcut for IB Data Manager

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$desktopPath = [Environment]::GetFolderPath("Desktop")

# Create main application shortcut
$shortcutPath = Join-Path $desktopPath "IB Data Manager.lnk"
$WshShell = New-Object -ComObject WScript.Shell
$shortcut = $WshShell.CreateShortcut($shortcutPath)

# Get Python executable path
$pythonPath = (Get-Command python).Source
$mainPyPath = Join-Path $scriptPath "main.py"

$shortcut.TargetPath = $pythonPath
$shortcut.Arguments = "`"$mainPyPath`""
$shortcut.WorkingDirectory = $scriptPath
$shortcut.Description = "Interactive Brokers Data Manager"
$shortcut.IconLocation = $pythonPath

$shortcut.Save()

Write-Host "✓ Desktop shortcut created successfully!" -ForegroundColor Green
Write-Host "Location: $shortcutPath" -ForegroundColor Cyan

# Create batch file shortcut
$batchShortcutPath = Join-Path $desktopPath "IB Data Manager (Batch).lnk"
$batchShortcut = $WshShell.CreateShortcut($batchShortcutPath)

$batchPath = Join-Path $scriptPath "run_app.bat"

$batchShortcut.TargetPath = $batchPath
$batchShortcut.WorkingDirectory = $scriptPath
$batchShortcut.Description = "Interactive Brokers Data Manager (Batch)"
$batchShortcut.IconLocation = "%SystemRoot%\System32\cmd.exe"

$batchShortcut.Save()

Write-Host "✓ Batch shortcut created successfully!" -ForegroundColor Green
Write-Host "Location: $batchShortcutPath" -ForegroundColor Cyan

Write-Host "`nYou can now double-click 'IB Data Manager' on your desktop to start the application." -ForegroundColor Yellow
