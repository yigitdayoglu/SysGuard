$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$MainScript = Join-Path $ProjectRoot "main.py"

if (Test-Path $VenvPython) {
    & $VenvPython $MainScript app
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    & py $MainScript app
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python $MainScript app
} else {
    throw "Python was not found. Install Python 3.11+ or create .venv before launching SysGuard."
}
