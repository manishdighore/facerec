# FaceRec - Quick Start with UV (PowerShell)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FaceRec - Quick Start with UV" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check UV
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "[!] UV not found. Installing..." -ForegroundColor Yellow
    irm https://astral.sh/uv/install.ps1 | iex
    Write-Host "[*] Restart PowerShell and run this script again." -ForegroundColor Yellow
    exit 1
}

# Backend setup
Write-Host "[1/5] Setting up backend..." -ForegroundColor Green
Push-Location backend

if (-not (Test-Path ".venv")) {
    Write-Host "[*] Creating venv..." -ForegroundColor Gray
    uv venv
}

Write-Host "[2/5] Installing dependencies..." -ForegroundColor Green
& .\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt

Write-Host "[3/5] Downloading models..." -ForegroundColor Green
python download_models.py

Write-Host "[4/5] Starting backend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\.venv\Scripts\Activate.ps1; python app.py"

Pop-Location

# Frontend
Write-Host "[5/5] Starting frontend..." -ForegroundColor Green
Push-Location frontend
if (-not (Test-Path "node_modules")) {
    npm install
}
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm run dev"
Pop-Location

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  Backend:  http://localhost:5000" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan

Start-Sleep -Seconds 3
Start-Process "http://localhost:3000"
