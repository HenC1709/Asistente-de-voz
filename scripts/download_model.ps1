$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$modelRoot = Join-Path $projectRoot 'models'
$modelPath = Join-Path $modelRoot 'vosk-model-small-es-0.42'
if (Test-Path -LiteralPath (Join-Path $modelPath 'am\final.mdl')) {
    Write-Host 'El modelo en español ya existe.'
    return
}
New-Item -ItemType Directory -Force -Path $modelRoot | Out-Null
$archivePath = Join-Path $modelRoot 'vosk-model-small-es-0.42.zip'
Invoke-WebRequest -Uri 'https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip' -OutFile $archivePath
Expand-Archive -LiteralPath $archivePath -DestinationPath $modelRoot -Force
if (-not (Test-Path -LiteralPath (Join-Path $modelPath 'am\final.mdl'))) { throw 'Modelo incompleto.' }
Remove-Item -LiteralPath $archivePath
Write-Host 'Modelo listo. Usa .\scripts\start.ps1 -Engine vosk'
