# Quick Start Guide - Updated with face_recognition

## Prerequisites

### macOS
```bash
# Install cmake (required for dlib)
brew install cmake

# Verify installation
cmake --version
```

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y build-essential cmake libopenblas-dev liblapack-dev
```

### Windows
1. Install Visual Studio Build Tools from https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install CMake from https://cmake.org/download/
3. Make sure to add CMake to PATH during installation

## Installation Steps

### 1. Backend Setup

```bash
cd backend

# Option A: Using pip
pip install -r requirements.txt

# Option B: Using uv (faster)
uv pip install -r requirements.txt

# Option C: Using the automated script
../setup-backend.sh
```

**Note**: The first time you install dlib, it will compile from source. This takes 3-5 minutes.

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Or if you prefer yarn
yarn install
```

### 3. Verify Installation

```bash
cd backend
python test_installation.py
```

You should see:
```
🎉 All tests passed! Your installation is ready.
```

## Running the Application

### Terminal 1 - Backend
```bash
cd backend
python app.py
```

You should see:
```
==================================================
Flask Face Recognition Backend
Library: face_recognition (dlib)
Model: hog
Tolerance: 0.6
Registered People: 0
==================================================

 * Running on http://0.0.0.0:5000
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

You should see:
```
▲ Next.js 14.2.x
- Local:        http://localhost:3000
```

### Access the Application

Open your browser and navigate to: **http://localhost:3000**

## Features

### 1. **Real-Time Detection** ⚡
- Click "Real-time Detection" toggle
- Processes webcam frames every second
- Much faster than the old DeepFace implementation

### 2. **Register New Person** 📸
- Switch to "Register" tab
- Enter name, email, and employee ID
- Capture or upload photo
- Face encoding is computed and cached

### 3. **View Gallery** 👥
- Switch to "Gallery" tab
- See all registered people
- Delete people if needed

### 4. **Single Detection** 🔍
- In "Recognize" tab
- Click "Capture & Detect"
- Instant recognition from cached encodings

## Performance Comparison

| Action | Old (DeepFace) | New (face_recognition) |
|--------|---------------|----------------------|
| Initial load | 10-15s | <1s |
| Detection | 1-2s | 0.1-0.2s |
| Recognition | 5-10s | 0.2-0.4s |
| Real-time FPS | 0.2-0.5 | 3-10 |

## Configuration

Edit `backend/app.py` to customize:

```python
# Line ~28-29
TOLERANCE = 0.6  # Lower = stricter (0.4-0.5 for high security, 0.6 default)
MODEL = 'hog'    # 'hog' for CPU (fast), 'cnn' for GPU (more accurate)
```

### Tolerance Guide
- `0.4`: Very strict, fewer false positives
- `0.5`: Strict, good for security applications
- `0.6`: Default, balanced accuracy/speed
- `0.7`: Relaxed, more matches

### Model Options
- `hog`: Fast, CPU-friendly, 99.38% accuracy
- `cnn`: Slower, GPU-recommended, 99.65% accuracy

## Docker Deployment

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:5000

## Troubleshooting

### Backend won't start
```bash
# Check if port 5000 is in use
lsof -i :5000

# Kill the process if needed
kill -9 <PID>

# Or use a different port
# Edit app.py, change: app.run(host='0.0.0.0', port=5001, debug=True)
```

### Frontend won't start
```bash
# Check if port 3000 is in use
lsof -i :3000

# Use a different port
PORT=3001 npm run dev
```

### "No face detected" error
- Ensure good lighting
- Face should be clearly visible
- Try moving closer to camera
- Check webcam permissions

### Slow performance
- Lower image resolution in frontend
- Use `MODEL = 'hog'` instead of 'cnn'
- Close other applications
- Check CPU usage

### Import errors
```bash
# Reinstall dependencies
cd backend
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

## API Endpoints

Test the backend directly:

```bash
# Health check
curl http://localhost:5000/api/health

# Get all people
curl http://localhost:5000/api/people

# Delete a person
curl -X DELETE http://localhost:5000/api/people/{person_id}
```

## Development Tips

### Watch for changes
```bash
# Backend auto-reloads on changes (debug=True)
cd backend
python app.py

# Frontend auto-reloads
cd frontend
npm run dev
```

### View logs
- Backend: Check terminal output
- Frontend: Check browser console (F12)

### Clear database
```bash
cd backend/database
rm people.json
rm -rf images/*
rm -rf encodings/*
```

## Next Steps

1. ✅ Install and verify setup
2. ✅ Register a few test people
3. ✅ Test recognition with webcam
4. ✅ Try real-time detection
5. ✅ Adjust tolerance if needed
6. ✅ Deploy to production

## Support

- 📚 [Migration Guide](./MIGRATION_GUIDE.md)
- 📊 [Performance Comparison](./COMPARISON.md)
- 🐛 [Troubleshooting](./TROUBLESHOOTING.md)
- 📖 [face_recognition docs](https://github.com/ageitgey/face_recognition)

---

**Congratulations!** 🎉 Your face recognition system is now running with the fast face_recognition library!
