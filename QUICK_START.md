# Multi-Face Detection & Recognition System - Quick Start

## ✨ New Features Implemented

### 1. Real-Time Multi-Face Detection
- Detects multiple faces in the same frame simultaneously
- Green boxes for recognized people, red for unknown
- Shows names and employee IDs on bounding boxes
- Displays confidence scores

### 2. Real-Time vs Manual Mode
- **Real-time Mode**: Continuous detection every second (toggle ON/OFF)
- **Manual Mode**: Click button to detect faces on demand

### 3. Employee ID Management
- Assign employee IDs during registration
- IDs displayed everywhere: boxes, gallery, face cards
- Optional field (can be left blank)

### 4. Gallery View
- New tab showing all registered faces with photos
- Grid layout with face images
- Shows name, employee ID, email, date added
- Delete button for each person

### 5. Detection Statistics
- Live counter showing:
  - Total detected faces
  - Number of recognized
  - Number of unknown

### 6. Detailed Face Cards
- Right panel shows info for each detected face
- Recognition status with checkmark/X
- Name, employee ID, confidence %
- Bounding box coordinates and size

## 🚀 Quick Start - Development Mode

### Terminal 1 - Backend:
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Terminal 2 - Frontend:
```powershell
cd frontend
npm install
npm run dev
```

Then open: http://localhost:3000

## 🐳 Quick Start - Docker Mode

```powershell
docker-compose up --build
```

Then open: http://localhost:3000

## 📝 How to Use

### Register Someone:
1. Click "Register" tab
2. Enter name, employee ID (optional), email (optional)
3. Either capture from webcam OR upload image
4. Click "Capture & Register" or "Register with Upload"
5. System validates one face is present
6. Person saved with unique ID

### Recognize Faces (Manual):
1. Click "Recognize" tab
2. Make sure real-time is OFF
3. Click "Detect & Recognize"
4. All faces detected with boxes
5. Details shown in right panel

### Real-Time Recognition:
1. Click "Recognize" tab
2. Toggle "Real-time" switch to ON
3. Detection happens automatically every second
4. Bounding boxes update continuously
5. Toggle OFF to stop

### View Gallery:
1. Click "Gallery" tab
2. See all registered people with photos
3. Click refresh to reload
4. Click delete to remove someone

## 🎯 Technical Architecture

### Backend (Flask + DeepFace):
- `DeepFace.extract_faces()` - Detects all faces with OpenCV backend
- `DeepFace.verify()` - Recognizes each face against database
- VGG-Face model preloaded on startup
- Recognition threshold: 0.6 distance metric

### Frontend (Next.js + React):
- Canvas overlay on webcam for bounding boxes
- Real-time loop with setInterval (1000ms)
- TypeScript interfaces for type safety
- Responsive CSS Grid for gallery

### Database:
- JSON file: `/backend/database/people.json`
- Images: `/backend/database/images/{uuid}.jpg`
- Each person has unique UUID

## 📊 API Endpoints

### POST /api/detect-and-recognize
Detects and recognizes all faces in image
**Request:**
```json
{
  "image": "data:image/jpeg;base64,..."
}
```
**Response:**
```json
{
  "faces": [
    {
      "bbox": {"x": 100, "y": 50, "w": 150, "h": 150},
      "detection_confidence": 0.99,
      "recognized": true,
      "person": {
        "name": "John Doe",
        "id": "uuid",
        "employee_id": "EMP001",
        "distance": 0.35,
        "confidence": 95.5
      }
    }
  ],
  "count": 1
}
```

### POST /api/register
Register new person with employee ID
**Request:**
```json
{
  "name": "John Doe",
  "employee_id": "EMP001",
  "email": "john@example.com",
  "image": "base64..."
}
```

### GET /api/people
Returns all registered people

### GET /api/people/{id}/image
Returns person's face image (JPEG)

### DELETE /api/people/{id}
Deletes person and their image

## 🔧 Configuration

### Adjust Detection Interval:
Edit `frontend/app/page.tsx` line ~109:
```typescript
realTimeIntervalRef.current = setInterval(() => {
  processFrame();
}, 1000); // Change this value (in milliseconds)
```

### Adjust Recognition Threshold:
Edit `backend/app.py`:
```python
THRESHOLD = 0.6  # Lower = stricter, Higher = more lenient
```

### Video Resolution:
Edit `frontend/app/page.tsx`:
```typescript
videoConstraints={{
  width: 640,
  height: 480,
  facingMode: 'user',
}}
```

## ⚡ Performance Tips

1. **Real-time lag?**
   - Increase detection interval (e.g., 2000ms instead of 1000ms)
   - Reduce video resolution
   - Ensure good lighting

2. **Poor recognition?**
   - Register person with multiple angles
   - Ensure good lighting during registration
   - Use front-facing photos
   - Adjust THRESHOLD value

3. **Backend slow?**
   - Models are preloaded, should be fast after first request
   - Check backend logs for errors
   - Ensure opencv detector is working

## 📁 Project Structure

```
facerec/
├── backend/
│   ├── app.py                    # Flask API (multi-face detection)
│   ├── requirements.txt
│   ├── database/
│   │   ├── people.json           # Person metadata
│   │   └── images/
│   │       └── {uuid}.jpg        # Face images
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── page.tsx              # Main component (canvas overlay)
│   │   └── page.module.css       # Styles
│   ├── lib/
│   │   └── api.ts                # API client
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── MULTI_FACE_DETECTION.md       # Full documentation
```

## 🐛 Troubleshooting

### Bounding boxes not showing:
- Open browser console (F12) for errors
- Check canvas element is overlaying video
- Verify backend is returning bbox coordinates

### Faces not recognized:
- Check at least one person is registered
- Verify lighting conditions
- Test with manual mode first
- Check backend logs for errors

### Real-time mode freezing:
- Backend might be slow - check logs
- Try increasing detection interval
- Check network connectivity
- Reduce video resolution

### Images not loading in gallery:
- Verify images exist in `backend/database/images/`
- Check file permissions
- Look for CORS errors in console
- Verify backend `/api/people/{id}/image` endpoint works

## 🎨 Color Coding

- **Green Box** = Recognized person
- **Red Box** = Unknown person
- **Green Card** = Recognized face info
- **Red Card** = Unknown face info

## 📸 Screenshot Flow

1. **Register Tab**: Webcam feed → Capture → Enter details → Save
2. **Recognize Tab**: Webcam feed with canvas overlay → Toggle real-time or manual → Bounding boxes appear → Face cards in sidebar
3. **Gallery Tab**: Grid of registered faces with photos → Click to view/delete

## 🚀 Next Steps

Potential enhancements:
- Adjustable detection interval slider in UI
- Face tracking across frames (smooth box movement)
- Multiple images per person for better accuracy
- Attendance logging with timestamps
- Face quality assessment before registration
- CSV export of recognition events
- Dark mode UI toggle

---

**Status**: ✅ Fully functional multi-face detection and recognition system with real-time capabilities!
