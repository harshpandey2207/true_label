<#
.SYNOPSIS
Builds the Flutter web app for the existing Vercel static deployment.

.DESCRIPTION
Keeps frontend/.env available for local development, then writes the public
Render API origin into the generated web asset that Vercel serves.
#>

$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    flutter build web --release
    if ($LASTEXITCODE -ne 0) {
        throw "Flutter web build failed with exit code $LASTEXITCODE."
    }

    $generatedEnv = Join-Path $PSScriptRoot 'build\web\assets\.env'
    if (-not (Test-Path -LiteralPath $generatedEnv)) {
        throw "Flutter did not generate the expected environment asset: $generatedEnv"
    }

    $productionEnv = "# True Label production web configuration`nAPI_BASE_URL=https://true-label-backend.onrender.com`n"
    [System.IO.File]::WriteAllText(
        $generatedEnv,
        $productionEnv,
        [System.Text.UTF8Encoding]::new($false)
    )
    Write-Host 'Vercel build is ready in frontend/build/web and points to the Render backend.'
}
finally {
    Pop-Location
}
