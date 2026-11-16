param([switch]$Text, [switch]$Mute, [switch]$DryRun, [string]$Engine, [switch]$DebugVoice)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$pythonExe = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonExe)) { throw 'Primero ejecuta .\scripts\install.ps1' }
$assistantArgs = @('-m', 'asistente.main')
if ($Text) { $assistantArgs += '--text' }
if ($Mute) { $assistantArgs += '--mute' }
if ($DryRun) { $assistantArgs += '--dry-run' }
if ($Engine) { $assistantArgs += @('--engine', $Engine) }
if ($DebugVoice) { $assistantArgs += '--debug-voice' }
Push-Location (Join-Path $projectRoot 'src')
try { & $pythonExe @assistantArgs; $assistantExit = $LASTEXITCODE }
finally { Pop-Location }
exit $assistantExit
