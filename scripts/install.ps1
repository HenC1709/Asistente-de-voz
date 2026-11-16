param([string]$Python = 'python', [switch]$Dev, [switch]$Offline)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Push-Location $projectRoot
try {
    & $Python -c 'import sys; sys.exit(0 if (3, 11) <= sys.version_info[:2] < (3, 13) else 1)'
    if ($LASTEXITCODE -ne 0) { throw 'Necesitas Python 3.11 o 3.12. Instala Python y usa -Python con su ruta si es necesario.' }
    & $Python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear .venv.' }
    $pythonExe = Join-Path $projectRoot '.venv\Scripts\python.exe'
    $requirements = if ($Dev) { 'requirements-dev.txt' } else { 'requirements.txt' }
    & $pythonExe -m pip install -r $requirements
    if ($LASTEXITCODE -ne 0) { throw 'Falló la instalación de dependencias.' }
    if ($Offline) {
        & $pythonExe -m pip install -r requirements-offline.txt
        if ($LASTEXITCODE -ne 0) { throw 'Falló la instalación de Vosk.' }
        & (Join-Path $PSScriptRoot 'download_model.ps1')
    }
    & $pythonExe -m pip install --no-deps -e .
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo registrar el paquete local.' }
    & $pythonExe -m asistente.main --check
    if ($LASTEXITCODE -ne 0) { throw 'La comprobación inicial falló.' }
    Write-Host 'Listo. Ejecuta .\scripts\start.ps1 o .\scripts\start.ps1 -Text'
} finally { Pop-Location }
