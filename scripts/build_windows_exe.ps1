$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$Python = $null
$IconFile = Join-Path $ProjectRoot "assets\SysGuard.ico"
$IconArgs = @()

Set-Location $ProjectRoot

if (Test-Path $VenvPython) {
    $Python = $VenvPython
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $Python = "py"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $Python = "python"
} else {
    throw "Python was not found. Install Python 3.11+ and run '.\.venv\Scripts\pip install -r requirements-dev.txt' before packaging."
}

& $Python scripts\generate_visual_assets.py

if (Test-Path $IconFile) {
    $IconArgs = @("--icon", $IconFile)
}

& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --name "SysGuard" `
    @IconArgs `
    --hidden-import "tkinter" `
    --hidden-import "psutil" `
    --hidden-import "watchdog" `
    --hidden-import "watchdog.observers.read_directory_changes" `
    --hidden-import "watchdog.observers.polling" `
    --hidden-import "pythoncom" `
    --hidden-import "pywintypes" `
    --hidden-import "win32com.shell" `
    --paths "$ProjectRoot" `
    app_entry.py

Write-Host "Built Windows executable at: $ProjectRoot\dist\SysGuard\SysGuard.exe"
