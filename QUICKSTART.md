# Quick Start Guide

## Windows Setup

### 1. Install Python Backend

Open PowerShell and run:

```powershell
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt

# Start backend server
python app.py
```

Keep this terminal open. Backend will run on http://localhost:5000

### 2. Install Frontend (New Terminal)

Open a new PowerShell window:

```powershell
# Navigate to frontend folder
cd frontend

# Install Node.js dependencies
npm install

# Start frontend development server
npm run dev
```

Frontend will run on http://localhost:3000

### 3. Use the Application

1. Open your browser and go to http://localhost:3000
2. Allow webcam access when prompted
3. Click "Register New Face" to add yourself
4. Enter your name and click "Capture & Register"
5. Switch to "Recognize" mode and test face recognition

## Troubleshooting

### Python/pip not found
Install Python from: https://www.python.org/downloads/
Make sure to check "Add Python to PATH" during installation

### Node/npm not found
Install Node.js from: https://nodejs.org/

### Port already in use
- Backend (5000): Kill the process or change port in `backend/app.py`
- Frontend (3000): The app will offer to use port 3001

### Camera not working
- Check browser permissions
- Try different browser (Chrome/Edge recommended)
- Ensure no other application is using the camera

## Testing the App

1. **Register Test Users**: Add 2-3 people with their faces
2. **Test Recognition**: Try recognizing registered faces
3. **Test Unidentified**: Show the camera an unregistered face or object
4. **Check Scores**: Notice the confidence scores and distance metrics
5. **Manage Database**: Delete and re-add users

## Next Steps

- Adjust threshold in `backend/app.py` for better/worse matching
- Add multiple photos per person for better recognition
- Try different DeepFace models (VGG-Face, Facenet, etc.)
