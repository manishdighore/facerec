# Quick Run Guide

## Prerequisites
- Python 3.10+
- Node.js 18+
- [uv](https://docs.astral.sh/uv/) (fast Python package manager)

## One-Command Start

**Windows:**
```bash
run.bat
```

**PowerShell:**
```powershell
.\run.ps1
```

## Manual Steps

### 1. Backend (Terminal 1)
```bash
cd backend
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt
uv run python download_models.py
uv python app.py
```

### 2. Frontend (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```

### 3. Open App
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## Model Download
The SCRFD (face detection) and ArcFace (face recognition) models download automatically.
To pre-download manually:
```bash
cd backend
python download_models.py
```
