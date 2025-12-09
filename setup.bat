@echo off
echo ========================================
echo Face Recognition App - Complete Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Python found: 
python --version
echo [OK] Node.js found: 
node --version
echo.

echo ========================================
echo Step 1: Setting up Python Backend
echo ========================================
cd backend

if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies (this may take a few minutes)...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)

echo [OK] Backend setup complete!
echo.

cd ..

echo ========================================
echo Step 2: Setting up Next.js Frontend
echo ========================================
cd frontend

echo Installing Node.js dependencies (this may take a few minutes)...
npm install
if errorlevel 1 (
    echo [ERROR] Failed to install Node.js dependencies
    pause
    exit /b 1
)

echo [OK] Frontend setup complete!
echo.

cd ..

echo ========================================
echo Setup Complete! 
echo ========================================
echo.
echo To start the application:
echo.
echo 1. Backend:  Double-click "start-backend.bat"
echo    OR run:   cd backend ^& venv\Scripts\activate ^& python app.py
echo.
echo 2. Frontend: Double-click "start-frontend.bat" (in a new terminal)
echo    OR run:   cd frontend ^& npm run dev
echo.
echo 3. Open browser: http://localhost:3000
echo.
echo ========================================
echo.
pause
