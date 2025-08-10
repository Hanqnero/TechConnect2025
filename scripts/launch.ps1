# Launch backend (FastAPI) and frontend (Vite) accessible from local network
# - Computes local IPv4 and sets ALLOWED_ORIGINS accordingly for CORS
# - Runs uvicorn on 0.0.0.0:8000 using .venv
# - Runs Vite with --host so it listens on all interfaces

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-LocalIPv4 {
  try {
    $ips = [System.Net.Dns]::GetHostAddresses([System.Net.Dns]::GetHostName()) |
      Where-Object { $_.AddressFamily -eq [System.Net.Sockets.AddressFamily]::InterNetwork -and $_.IPAddressToString -notlike '127.*' -and $_.IPAddressToString -notlike '169.*' }
    if ($ips -and $ips[0].IPAddressToString) { return $ips[0].IPAddressToString }
  } catch {}
  try {
    $candidates = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
      Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.*' -and $_.IPAddress -ne '0.0.0.0' } |
      Sort-Object InterfaceMetric, PrefixLength
    if ($candidates -and $candidates[0].IPAddress) { return $candidates[0].IPAddress }
  } catch {}
  return '127.0.0.1'
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$ip = Get-LocalIPv4
if (-not $ip) { $ip = '127.0.0.1' }
$frontendOrigin = "http://$($ip):5173"

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

# Prefer npm.cmd to avoid npm.ps1 shim issues; fallback to cmd /c npm ...
$npmCmd = (Get-Command npm.cmd -ErrorAction SilentlyContinue).Path
if (-not $npmCmd) { $npmCmd = (Get-Command npm.exe -ErrorAction SilentlyContinue).Path }
if ($npmCmd) {
  $frontendExe = $npmCmd
  $frontendArgs = @("run", "dev", "--", "--host")
  Write-Host "Using npm at: $frontendExe" -ForegroundColor Cyan
} else {
  $frontendExe = "cmd.exe"
  $frontendArgs = @("/c", "npm", "run", "dev", "--", "--host")
  Write-Host "npm.cmd not found; using cmd /c npm" -ForegroundColor Yellow
}

Write-Host "Backend URL:   http://$($ip):8000" -ForegroundColor Green
Write-Host "Frontend URL:  http://$($ip):5173" -ForegroundColor Green

# Start processes in separate windows for clarity
Start-Process -FilePath $python -ArgumentList $backendArgs -WorkingDirectory $backendWD
Start-Process -FilePath $frontendExe -ArgumentList $frontendArgs -WorkingDirectory $frontendWD

Write-Host "Launched backend and frontend. Press Enter to exit this launcher (apps keep running)."
[void][System.Console]::ReadLine()
