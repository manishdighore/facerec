# Backend - Flask Face Recognition API

This is the backend server for the face recognition application using DeepFace.

## Quick Start

1. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python app.py
```

Server runs on: http://localhost:5000

## API Documentation

### POST /api/recognize
Recognize a face from a captured image.

**Request:**
```json
{
  "image": "data:image/jpeg;base64,..."
}
```

**Response (Identified):**
```json
{
  "identified": true,
  "person": {
    "id": "john_doe_20241130120000",
    "name": "John Doe",
    "email": "john@example.com",
    "added_date": "2024-11-30T12:00:00"
  },
  "confidence": 95.5,
  "distance": 0.32,
  "threshold": 0.6
}
```

**Response (Unidentified):**
```json
{
  "identified": false,
  "message": "No matching face found",
  "person": null,
  "confidence": 0,
  "best_distance": 0.75
}
```

### POST /api/register
Register a new person's face.

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "image": "data:image/jpeg;base64,..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Face registered successfully",
  "person": {
    "id": "john_doe_20241130120000",
    "name": "John Doe",
    "email": "john@example.com",
    "added_date": "2024-11-30T12:00:00",
    "image_count": 1
  }
}
```

### GET /api/people
Get all registered people.

**Response:**
```json
{
  "people": [
    {
      "id": "john_doe_20241130120000",
      "name": "John Doe",
      "email": "john@example.com",
      "added_date": "2024-11-30T12:00:00",
      "image_count": 1
    }
  ]
}
```

### DELETE /api/people/<person_id>
Delete a person from the database.

**Response:**
```json
{
  "success": true,
  "message": "Person deleted successfully"
}
```

## Configuration

### Change Recognition Model

Edit `app.py` line ~80:
```python
result = DeepFace.verify(
    temp_path, 
    img_path,
    model_name='VGG-Face',  # Change this
    enforce_detection=False
)
```

Available models:
- VGG-Face (default)
- Facenet
- OpenFace
- DeepFace
- DeepID
- ArcFace
- Dlib

### Adjust Recognition Threshold

Edit `app.py` line ~75:
```python
threshold = 0.6  # Lower = stricter, Higher = looser
```

## Database

Images are stored in `database/faces/<person_id>/face_1.jpg`
Metadata is stored in `database/people.json`
