@echo off
echo ========================================
echo   FaceRec - Quick Start with UV
echo ========================================
echo.

:: Check if uv is installed
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] UV not found. Installing UV...
    powershell -Command "irm https://astral.sh/uv/install.ps1 | iex"
    echo [*] Please restart this script after UV installation.
    pause
    exit /b 1
)

echo [1/5] Setting up Python backend...
cd backend

:: Create venv if not exists
if not exist ".venv" (
    echo [*] Creating virtual environment...
    uv venv
)

:: Activate and install deps
call .venv\Scripts\activate.bat
echo [2/5] Installing Python dependencies...
uv pip install -r requirements.txt

:: Download models
echo [3/5] Downloading face recognition models...
python download_models.py

:: Start backend in background
echo [4/5] Starting backend server...
start "FaceRec Backend" cmd /k "call .venv\Scripts\activate.bat && python app.py"

:: Start frontend
cd ..\frontend
echo [5/5] Starting frontend...
if not exist "node_modules" (
    echo [*] Installing npm packages...
    call npm install
)
start "FaceRec Frontend" cmd /k "npm run dev"

cd ..
echo.
echo ========================================
echo   App is starting!
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:5000
echo ========================================
echo.
echo Press any key to open the app in browser...
pause >nul
start http://localhost:3000
