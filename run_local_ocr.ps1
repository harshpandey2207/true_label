param(
    [int]$Port = 8000,
    [switch]$Reload
)

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonCandidates = @(
    (Join-Path $repoRoot "venv\Scripts\python.exe"),
    (Join-Path $repoRoot ".venv\Scripts\python.exe")
)
$python = $pythonCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $python) {
    throw "No project Python environment found. Create venv and install backend/requirements.txt plus backend/requirements-ocr.txt first."
}

# OCR is deliberately opt-in for deployments. This launcher makes the local
# developer choice explicit while leaving the process-scoped environment only.
$env:TRUE_LABEL_ENABLE_LOCAL_OCR = "1"
if (-not $env:TRUE_LABEL_OCR_ENGINE) {
    $env:TRUE_LABEL_OCR_ENGINE = "rapidocr"
}

$uvicornArgs = @(
    "-m", "uvicorn", "backend.app.main:app",
    "--host", "127.0.0.1",
    "--port", $Port.ToString()
)
if ($Reload) {
    $uvicornArgs += "--reload"
}

Push-Location $repoRoot
try {
    & $python @uvicornArgs
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
