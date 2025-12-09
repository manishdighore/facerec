@echo off
echo Starting Face Recognition Frontend...
cd frontend
if not exist node_modules (
    echo Installing dependencies...
    npm install
)
echo.
echo Starting Next.js development server on http://localhost:3000
echo.
npm run dev
