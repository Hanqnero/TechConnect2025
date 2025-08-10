# Launch backend (FastAPI) and frontend (Vite) accessible from local network
# - Computes local IPv4 and sets ALLOWED_ORIGINS accordingly for CORS
# - Runs uvicorn on 0.0.0.0:8000 using .venv
# - Runs Vite with --host so it listens on all interfaces

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-LocalIPv4 {
  $candidates = Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.*' -and $_.IPAddress -ne '0.0.0.0' } |
    Sort-Object InterfaceMetric, PrefixLength
  if ($candidates -and $candidates[0].IPAddress) { return $candidates[0].IPAddress }
  return '127.0.0.1'
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$ip = Get-LocalIPv4
$frontendOrigin = "http://$ip:5173"

# Allow current machine and LAN origin for CORS
$env:ALLOWED_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173,$frontendOrigin"
Write-Host "Using ALLOWED_ORIGINS=$env:ALLOWED_ORIGINS" -ForegroundColor Cyan

# Backend
$backendWD = $repoRoot
$python = Join-Path $repoRoot ".venv/Scripts/python.exe"
if (-not (Test-Path $python)) { throw ".venv Python not found at $python" }
$backendArgs = "-m", "uvicorn", "app.app:app", "--reload", "--host", "0.0.0.0", "--port", "8000"

# Frontend
$frontendWD = Join-Path $repoRoot "frontend"
$npm = "npm"
$frontendArgs = @("run", "dev", "--", "--host")

Write-Host "Backend URL:   http://$ip:8000" -ForegroundColor Green
Write-Host "Frontend URL:  http://$ip:5173" -ForegroundColor Green

# Start processes in separate windows for clarity
Start-Process -FilePath $python -ArgumentList $backendArgs -WorkingDirectory $backendWD
Start-Process -FilePath $npm -ArgumentList $frontendArgs -WorkingDirectory $frontendWD

Write-Host "Launched backend and frontend. Press Enter to exit this launcher (apps keep running)."
[void][System.Console]::ReadLine()
