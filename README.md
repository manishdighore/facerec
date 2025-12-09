# Face Recognition App

A real-time face recognition application using DeepFace (VGG-Face model) with Next.js frontend and Flask backend.

## Features

- ðŸŽ¥ Real-time webcam capture
- ðŸ” Face recognition with confidence scores
- âž• Register new faces to the database
- ðŸ“Š Display match scores and distance metrics
- ðŸ‘¥ Manage registered people
- âŒ Unidentified face detection
- ðŸ’¾ Local file-based database (images + JSON)

## Project Structure

```
facerec/
â”œâ”€â”€ backend/          # Flask API server
â”‚   â”œâ”€â”€ app.py        # Main Flask application
â”‚   â”œâ”€â”€ requirements.txt
â”‚   â””â”€â”€ database/
â”‚       â”œâ”€â”€ faces/    # Stored face images (organized by person)
â”‚       â””â”€â”€ people.json  # Person metadata
â”‚
â””â”€â”€ frontend/         # Next.js application
    â”œâ”€â”€ app/          # Next.js app directory
    â”œâ”€â”€ lib/          # API utilities
    â””â”€â”€ package.json
```

## Prerequisites

### Option 1: Docker (Recommended)
- Docker Desktop installed
- Docker Compose installed (comes with Docker Desktop)

### Option 2: Manual Setup
- Python 3.8+ (for backend)
- Node.js 18+ and npm (for frontend)
- Webcam access

## Quick Start with Docker ðŸ³

The easiest way to run the application:

```bash
# Start everything with one command
docker-compose up --build

# Or run in background
docker-compose up -d

# Windows: Use the batch file
docker-start.bat
```

Then open http://localhost:3000 in your browser!

To stop:
```bash
docker-compose down

# Windows: Use the batch file
docker-stop.bat
```

See [DOCKER.md](DOCKER.md) for detailed Docker instructions.

## Manual Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Start the Flask server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## Usage

### Register a New Face

1. Click the "âž• Register New Face" button
2. Enter the person's name (required) and email (optional)
3. Position your face in the webcam
4. Click "âœ… Capture & Register"

### Recognize a Face

1. Click the "ðŸ” Recognize" button
2. Position your face in the webcam
3. Click "ðŸ“¸ Capture & Recognize"
4. View the results:
   - **Identified**: Shows name, email, confidence score, and distance
   - **Unidentified**: Shows message indicating no match found

### Manage People

- View all registered people in the right panel
- Delete people by clicking the ðŸ—‘ï¸ button
- Refresh the list with the ðŸ”„ button

## API Endpoints

### Backend API

- `GET /api/health` - Health check
- `POST /api/recognize` - Recognize face from base64 image
- `POST /api/register` - Register new face with name and email
- `GET /api/people` - Get all registered people
- `DELETE /api/people/<person_id>` - Delete a person

## Configuration

### Recognition Threshold

The recognition threshold is set to `0.6` in `backend/app.py`. You can adjust this value:
- Lower values = stricter matching (fewer false positives)
- Higher values = looser matching (more false positives)

```python
threshold = 0.6  # Adjust in app.py
```

### Model Selection

The app uses the VGG-Face model by default. You can change this in `backend/app.py`:

```python
result = DeepFace.verify(
    temp_path, 
    img_path,
    model_name='VGG-Face',  # Options: VGG-Face, Facenet, OpenFace, DeepFace, DeepID, ArcFace, Dlib
    enforce_detection=False
)
```

## Database Structure

### Folder Structure
```
backend/database/
├── faces/
│   ├── john_doe_20241130120000/
│   │   └── face_1.jpg
│   └── jane_smith_20241130120100/
│       └── face_1.jpg
└── people.json
```

### people.json Format
```json
[
  {
    "id": "john_doe_20241130120000",
    "name": "John Doe",
    "email": "john@example.com",
    "added_date": "2024-11-30T12:00:00",
    "image_count": 1
  }
]
```

## Troubleshooting

### Backend Issues

1. **Import errors**: Make sure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. **TensorFlow/Keras issues**: The app uses `tf-keras` which is compatible with newer TensorFlow versions.

3. **OpenCV issues**: Install system dependencies if needed (Linux):
   ```bash
   sudo apt-get install libgl1-mesa-glx
   ```

### Frontend Issues

1. **Webcam not working**: Grant browser permission to access the camera

2. **API connection failed**: Ensure backend is running on port 5000

3. **CORS errors**: CORS is enabled in the Flask app, but check firewall settings

## Technologies Used

### Backend
- Flask - Web framework
- DeepFace - Face recognition library
- OpenCV - Image processing
- NumPy - Numerical operations

### Frontend
- Next.js 14 - React framework
- TypeScript - Type safety
- react-webcam - Webcam access
- Axios - HTTP client

## Performance Notes

- First recognition may take longer as models are loaded
- Recognition time: ~1-3 seconds per image
- Supports multiple faces in database
- Local storage only (no cloud dependencies)

## Security Considerations

- All data stored locally
- No external API calls for face recognition
- Webcam access requires user permission
- Consider encryption for production use
