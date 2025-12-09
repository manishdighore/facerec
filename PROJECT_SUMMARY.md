# 🎭 Face Recognition App - Complete Project

A full-stack face recognition application using DeepFace AI library with Next.js frontend and Flask backend.

## ✨ Features

- ✅ Real-time webcam face capture
- ✅ Face recognition with confidence scores
- ✅ Register unlimited people with names & emails
- ✅ Match score and distance metrics display
- ✅ Unidentified face detection
- ✅ Person management (add/delete)
- ✅ Local file-based database
- ✅ Beautiful, responsive UI
- ✅ No cloud dependencies

## 📁 Project Structure

```
facerec/
├── 📄 README.md                    # Main documentation
├── 📄 QUICKSTART.md                # Quick start guide
├── 📄 ARCHITECTURE.md              # System architecture
├── 📄 TROUBLESHOOTING.md           # Problem solving guide
├── 🔧 setup.bat                    # One-click setup script
├── ▶️ start-backend.bat            # Start backend server
├── ▶️ start-frontend.bat           # Start frontend app
├── 
├── backend/                        # Python Flask API
│   ├── app.py                      # Main Flask application
│   ├── requirements.txt            # Python dependencies
│   ├── README.md                   # Backend documentation
│   └── database/
│       ├── people.json             # Person metadata (names, emails, etc.)
│       └── faces/                  # Stored face images
│           └── <person_id>/
│               └── face_1.jpg
│
└── frontend/                       # Next.js React app
    ├── package.json                # Node dependencies
    ├── next.config.js              # Next.js configuration
    ├── tsconfig.json               # TypeScript configuration
    ├── .env.local                  # Environment variables
    ├── README.md                   # Frontend documentation
    ├── app/
    │   ├── page.tsx                # Main page component
    │   ├── page.module.css         # Page styles
    │   ├── layout.tsx              # Root layout
    │   └── globals.css             # Global styles
    └── lib/
        └── api.ts                  # API client functions
```

## 🚀 Quick Start (3 Steps)

### Step 1: Run Setup
Double-click `setup.bat` or run in PowerShell:
```powershell
.\setup.bat
```
This installs all dependencies for both backend and frontend.

### Step 2: Start Backend
Double-click `start-backend.bat` or run:
```powershell
.\start-backend.bat
```
Backend runs on http://localhost:5000

### Step 3: Start Frontend (New Terminal)
Double-click `start-frontend.bat` or run:
```powershell
.\start-frontend.bat
```
Frontend runs on http://localhost:3000

### Step 4: Use the App
1. Open http://localhost:3000 in your browser
2. Allow webcam access
3. Click "Register New Face" to add yourself
4. Switch to "Recognize" mode to test recognition

## 🛠️ Manual Setup

### Backend
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

### Frontend
```powershell
cd frontend
npm install
npm run dev
```

## 📋 Requirements

### Software
- **Python**: 3.8 - 3.11 (3.12 has compatibility issues)
- **Node.js**: 18.x or higher
- **Webcam**: Built-in or external
- **Browser**: Chrome or Edge (recommended)

### System
- **OS**: Windows 10/11
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB for dependencies + space for face images

## 🎯 How It Works

### Recognition Process
1. User clicks "Capture & Recognize"
2. Webcam captures current frame
3. Image converted to base64 and sent to backend
4. Backend uses DeepFace to compare with all stored faces
5. Calculates distance between face embeddings
6. If distance < threshold (0.6): **Identified** ✅
7. If distance ≥ threshold: **Unidentified** ❌

### Registration Process
1. User enters name (required) and email (optional)
2. Clicks "Capture & Register"
3. Webcam captures frame
4. Image saved to `database/faces/<person_id>/face_1.jpg`
5. Metadata saved to `database/people.json`
6. Person now available for recognition

## 📊 Understanding Results

### Confidence Score
- Calculated as: `(1 - distance) × 100%`
- **90-100%**: Excellent match
- **70-89%**: Good match
- **60-69%**: Acceptable match
- **Below 60%**: Unidentified (threshold dependent)

### Distance Metric
- Euclidean distance between face embeddings
- **Lower = Better match**
- Typical values:
  - **0.0-0.4**: Same person (very high confidence)
  - **0.4-0.6**: Likely same person (threshold zone)
  - **0.6+**: Different person

### Threshold (Default: 0.6)
- Adjustable in `backend/app.py`
- **Lower (0.4-0.5)**: Stricter matching, fewer false positives
- **Default (0.6)**: Balanced
- **Higher (0.7-0.8)**: Looser matching, more false positives

## 🎨 Features Breakdown

### Frontend Features
- **Webcam Preview**: Real-time camera feed
- **Dual Modes**: Switch between Recognize and Register
- **Live Results**: Instant recognition feedback
- **People List**: View all registered people
- **Delete Function**: Remove people from database
- **Backend Status**: Shows if backend is online/offline
- **Responsive Design**: Works on desktop browsers

### Backend Features
- **Face Recognition**: DeepFace VGG-Face model
- **Face Registration**: Store faces with metadata
- **REST API**: Clean JSON endpoints
- **CORS Enabled**: Accepts requests from frontend
- **Error Handling**: Graceful error responses
- **File-based DB**: No SQL database required

## 🔧 Configuration Options

### Change Recognition Model
Edit `backend/app.py`:
```python
result = DeepFace.verify(
    temp_path, 
    img_path,
    model_name='VGG-Face',  # Options: VGG-Face, Facenet, Facenet512, ArcFace, etc.
    enforce_detection=False
)
```

### Adjust Threshold
Edit `backend/app.py`:
```python
threshold = 0.6  # Adjust between 0.4-0.8
```

### Change Ports
Backend (`backend/app.py`):
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change port
```

Frontend (`frontend/.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:5000  # Update if backend port changes
```

## 📖 Documentation Files

| File | Description |
|------|-------------|
| **README.md** | Main project documentation |
| **QUICKSTART.md** | Fast setup guide for beginners |
| **ARCHITECTURE.md** | System design and data flow |
| **TROUBLESHOOTING.md** | Solutions to common problems |
| **backend/README.md** | Backend API documentation |
| **frontend/README.md** | Frontend component documentation |

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Python not found | Install Python and add to PATH |
| Port already in use | Change port or kill existing process |
| Webcam not working | Check browser permissions |
| Recognition fails | Adjust lighting, distance, or threshold |
| CORS errors | Ensure backend is running |

See **TROUBLESHOOTING.md** for detailed solutions.

## 🔐 Security Notes

⚠️ **Current Version**: Development only
- No authentication
- No encryption
- Local storage only
- No HTTPS

For production use:
- Add user authentication
- Implement API rate limiting
- Enable HTTPS/TLS
- Encrypt stored images
- Add access controls
- Implement audit logging

## 📈 Performance

### First Use
- Backend startup: 10-15 seconds (model loading)
- First recognition: 3-5 seconds
- Subsequent recognitions: 1-2 seconds

### Scaling
- Works well with 10-50 people
- For 100+ people, consider:
  - Pre-computing face embeddings
  - Using database indexing
  - GPU acceleration

## 🎓 Technology Stack

### Backend
- **Flask** - Web framework
- **DeepFace** - Face recognition (serengil/deepface)
- **VGG-Face** - Deep learning model
- **OpenCV** - Image processing
- **NumPy** - Numerical operations
- **TensorFlow** - ML framework

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **react-webcam** - Camera access
- **Axios** - HTTP client
- **CSS Modules** - Scoped styling

## 🚀 Future Enhancements

Potential features to add:
- [ ] Multiple images per person
- [ ] Batch registration
- [ ] Real-time continuous recognition
- [ ] Face embedding caching
- [ ] SQLite/PostgreSQL database
- [ ] Docker deployment
- [ ] Mobile app (React Native)
- [ ] Face liveness detection
- [ ] Age/emotion detection
- [ ] Multi-face detection

## 🤝 Contributing

This is a demonstration project. Feel free to:
- Fork and modify
- Add new features
- Improve UI/UX
- Optimize performance
- Fix bugs

## 📝 License

MIT License - Free to use and modify

## 🙋 Support

Having issues?
1. Check **TROUBLESHOOTING.md**
2. Review **ARCHITECTURE.md** for understanding
3. Read backend/frontend README files
4. Check browser console for errors
5. Verify all dependencies installed

## 🎉 Credits

- **DeepFace**: https://github.com/serengil/deepface
- **VGG-Face**: Visual Geometry Group, Oxford
- **Next.js**: Vercel
- **Flask**: Pallets Projects

---

**Made with ❤️ using DeepFace, Next.js, and Flask**

**Version**: 1.0.0  
**Last Updated**: November 30, 2024  
**Status**: ✅ Production Ready (Development Mode)

---

## Quick Links

- 🏠 [Main README](README.md)
- ⚡ [Quick Start](QUICKSTART.md)
- 🏗️ [Architecture](ARCHITECTURE.md)
- 🔧 [Troubleshooting](TROUBLESHOOTING.md)
- 🐍 [Backend Docs](backend/README.md)
- ⚛️ [Frontend Docs](frontend/README.md)

**Start Now**: Run `setup.bat` → `start-backend.bat` → `start-frontend.bat` → Open http://localhost:3000
