# Multi-Face Detection & Recognition System

## Overview
This application now supports real-time detection and recognition of multiple faces in the same camera feed.

## New Features

### 1. **Multi-Face Detection**
- Detects all faces in a single frame
- Shows bounding boxes around each detected face
- Color-coded boxes:
  - **Green**: Recognized person
  - **Red**: Unknown person

### 2. **Real-Time Recognition**
- Toggle real-time mode ON/OFF
- Continuous detection every second when enabled
- Manual capture mode still available

### 3. **Employee ID Management**
- Assign employee IDs during registration
- IDs displayed on bounding boxes and in the gallery
- Optional field (can be left blank)

### 4. **Registered Faces Gallery**
- New "Gallery" tab to view all registered people
- Shows face images with details:
  - Name
  - Employee ID
  - Email
  - Registration date
- Delete functionality for each person

### 5. **Detection Statistics**
- Real-time stats display:
  - Total detected faces
  - Number of recognized faces
  - Number of unknown faces

### 6. **Detailed Face Information**
- Right panel shows detailed info for each detected face:
  - Recognition status
  - Name and employee ID
  - Confidence percentage
  - Bounding box coordinates and size

## How to Use

### Registration with Employee ID
1. Click the **Register** tab
2. Enter the person's full name
3. Enter their employee ID (optional)
4. Enter email (optional)
5. Either:
   - Click "Capture & Register" to use webcam
   - OR upload an image file
6. System validates that only one face is present
7. Person is saved with a unique UUID

### Multi-Face Recognition

#### Manual Mode (Default)
1. Click the **Recognize** tab
2. Click "Detect & Recognize" button
3. All faces in the frame are detected and recognized
4. Bounding boxes appear on the video feed
5. Face details appear in the right panel

#### Real-Time Mode
1. Click the **Recognize** tab
2. Toggle the "Real-time" switch to ON
3. System automatically detects faces every second
4. Bounding boxes update in real-time
5. Toggle OFF to stop automatic detection

### View Registered People
1. Click the **Gallery** tab
2. See all registered people with their photos
3. Click "Delete" to remove someone from the database
4. Click "Refresh" to reload the list

## Backend API Changes

### New Endpoint: `/api/detect-and-recognize`
**POST** - Detects and recognizes multiple faces

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
        "id": "uuid-here",
        "employee_id": "EMP001",
        "distance": 0.35,
        "confidence": 95.5
      }
    }
  ],
  "count": 1
}
```

### Updated Endpoint: `/api/register`
Now accepts `employee_id` field:
```json
{
  "name": "John Doe",
  "employee_id": "EMP001",
  "email": "john@example.com",
  "image": "base64..."
}
```

### New Endpoint: `/api/people/<person_id>/image`
**GET** - Returns the registered face image as JPEG

## Technical Details

### Face Detection
- Uses OpenCV detector backend via DeepFace
- `DeepFace.extract_faces()` detects all faces in frame
- Returns bounding box coordinates (x, y, w, h) for each face

### Face Recognition
- Uses VGG-Face model for recognition
- Each detected face is compared against database
- Recognition threshold: 0.6 (distance metric)
- Confidence calculated as: `(1 - distance) * 100`

### Canvas Overlay
- HTML5 Canvas positioned over webcam video
- Real-time drawing of bounding boxes and labels
- Coordinates scaled from detection resolution (640x480) to video dimensions

### Performance
- Detection interval: 1 second (real-time mode)
- Models preloaded on backend startup
- Image format: JPEG with 90% quality
- Database: JSON file + JPEG images

## Running the Application

### Development Mode
```bash
# Start backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py

# Start frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Docker Mode
```bash
docker-compose up --build
```

Access at: http://localhost:3000

## File Structure
```
facerec/
├── backend/
│   ├── app.py                 # Flask API with multi-face detection
│   ├── database/
│   │   ├── people.json        # Person metadata
│   │   └── images/            # Face images (UUID.jpg)
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Main component with canvas overlay
│   │   └── page.module.css    # Styles for UI and bounding boxes
│   └── lib/
│       └── api.ts             # API client with new types
└── docker-compose.yml         # Container orchestration
```

## Troubleshooting

### Bounding boxes not showing
- Check browser console for errors
- Ensure canvas is overlaying video correctly
- Verify backend is returning bbox coordinates

### Recognition not working
- Make sure at least one person is registered
- Check lighting conditions
- Verify webcam is working properly

### Real-time mode laggy
- Adjust detection interval in code (line 109 in page.tsx)
- Check backend response times
- Consider reducing video resolution

## Future Enhancements
- Adjustable detection interval slider
- Face tracking across frames
- Multiple image storage per person for better accuracy
- Export attendance logs based on detection timestamps
- Face quality assessment before registration
