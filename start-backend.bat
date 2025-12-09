@echo off
echo Starting Face Recognition Backend...
cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo Installing/updating dependencies...
pip install -r requirements.txt
echo.
echo Starting Flask server on http://localhost:5000
echo.
python app.py
