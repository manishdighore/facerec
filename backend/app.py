"""
Flask Face Recognition Backend using InsightFace (SCRFD + ArcFace)
Based on: https://github.com/vectornguyen76/face-recognition

This backend uses:
- SCRFD for fast and accurate face detection with facial landmarks
- ArcFace for robust face embedding extraction
- Cosine similarity for face matching

Architecture Reference: https://github.com/vectornguyen76/face-recognition
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
import json
import base64
import os
import uuid
import hashlib
from datetime import datetime
import traceback
from PIL import Image
import io
import time

# Import face detection and recognition modules
from face_detection.scrfd_detector import SCRFD
from face_recognition_module.arcface_recognizer import ArcFaceRecognizer, compare_encodings
from face_alignment.alignment import norm_crop
from download_models import check_and_download_models

app = Flask(__name__)
CORS(app)

# ============================================================================
# Configuration
# ============================================================================

# Database configuration
DB_FOLDER = os.path.join(os.path.dirname(__file__), 'database', 'faces')
DB_JSON = os.path.join(os.path.dirname(__file__), 'database', 'people.json')
IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'database', 'images')
ENCODINGS_DIR = os.path.join(os.path.dirname(__file__), 'database', 'encodings')
MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')

# Model paths - Download models and place them in the models directory
# Using InsightFace buffalo_l model pack models
SCRFD_MODEL_PATH = os.path.join(MODELS_DIR, 'det_10g.onnx')
ARCFACE_MODEL_PATH = os.path.join(MODELS_DIR, 'w600k_r50.onnx')

# Detection configuration
DETECTION_THRESHOLD = 0.5  # Face detection confidence threshold
DETECTION_INPUT_SIZE = (640, 640)  # SCRFD input size

# Recognition configuration
RECOGNITION_THRESHOLD = 0.25  # Minimum similarity score for recognition (0-1, higher is stricter)
FACE_ALIGN_SIZE = 112  # Face alignment size for ArcFace

# Create necessary directories
os.makedirs(DB_FOLDER, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(ENCODINGS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# ============================================================================
# Model Initialization
# ============================================================================

# Check and download models if needed
print("\n" + "="*60)
print("Checking for required models...")
print("="*60)
model_status = check_and_download_models(MODELS_DIR)

# Initialize face detector (SCRFD)
detector = None
if model_status.get('scrfd', False):
    try:
        detector = SCRFD(model_file=SCRFD_MODEL_PATH)
        print(f"✓ SCRFD detector loaded from {SCRFD_MODEL_PATH}")
    except Exception as e:
        print(f"✗ Failed to load SCRFD detector: {e}")
else:
    print(f"✗ SCRFD model not available - face detection disabled")

# Initialize face recognizer (ArcFace)
recognizer = None
if model_status.get('arcface', False):
    try:
        recognizer = ArcFaceRecognizer(model_file=ARCFACE_MODEL_PATH)
        print(f"✓ ArcFace recognizer loaded from {ARCFACE_MODEL_PATH}")
    except Exception as e:
        print(f"✗ Failed to load ArcFace recognizer: {e}")
else:
    print(f"✗ ArcFace model not available - face recognition disabled")

# Cache for face encodings (for faster real-time detection)
encodings_cache = {}
names_cache = {}

# Unknown person tracking
unknown_faces = {}  # Track unknown faces by session
unknown_counter = 0  # Global counter for unknown IDs

# Face tracking state - store embeddings for proper similarity comparison
face_tracking_counter = 0
face_tracking_embeddings = {}  # Map tracking ID to embedding
TRACKING_SIMILARITY_THRESHOLD = 0.6  # Threshold for considering same person across frames

# ============================================================================
# Database Operations
# ============================================================================

# Initialize JSON database
if not os.path.exists(DB_JSON):
    with open(DB_JSON, 'w') as f:
        json.dump([], f)


def load_database():
    """Load the people database from JSON"""
    try:
        with open(DB_JSON, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading database: {e}")
        return []


def save_database(people):
    """Save the people database to JSON"""
    try:
        with open(DB_JSON, 'w') as f:
            json.dump(people, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving database: {e}")
        return False


def load_person_encoding(person_id):
    """Load face encoding from file or cache"""
    if person_id in encodings_cache:
        return encodings_cache[person_id]
    
    encoding_path = os.path.join(ENCODINGS_DIR, f"{person_id}.npy")
    if os.path.exists(encoding_path):
        encoding = np.load(encoding_path)
        encodings_cache[person_id] = encoding
        return encoding
    
    return None


def save_person_encoding(person_id, encoding):
    """Save face encoding to file and cache"""
    encoding_path = os.path.join(ENCODINGS_DIR, f"{person_id}.npy")
    np.save(encoding_path, encoding)
    encodings_cache[person_id] = encoding


def load_all_encodings():
    """Load all face encodings into cache for faster recognition"""
    people = load_database()
    for person in people:
        person_id = person.get('id')
        load_person_encoding(person_id)
        names_cache[person_id] = person.get('name')
    return len(encodings_cache)


# ============================================================================
# Image Processing Utilities
# ============================================================================

def base64_to_image(base64_str):
    """Convert base64 string to numpy array (BGR format)"""
    try:
        # Remove data URL prefix if present
        if ',' in base64_str:
            base64_str = base64_str.split(',')[1]
        
        # Decode base64
        img_data = base64.b64decode(base64_str)
        
        # Use PIL to handle the image properly
        pil_image = Image.open(io.BytesIO(img_data))
        
        # Convert to RGB
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Convert to numpy array (RGB)
        img_rgb = np.array(pil_image)
        
        # Convert RGB to BGR for OpenCV
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        
        return img_bgr
    except Exception as e:
        print(f"Error converting base64 to image: {e}")
        traceback.print_exc()
        return None


def process_uploaded_file(file):
    """Process uploaded file to numpy array (BGR format)"""
    try:
        pil_image = Image.open(file)
        
        # Convert to RGB
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        img_rgb = np.array(pil_image)
        
        # Convert RGB to BGR for OpenCV
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        
        return img_bgr
    except Exception as e:
        print(f"Error processing uploaded file: {e}")
        traceback.print_exc()
        return None


# ============================================================================
# Face Detection and Recognition Functions
# ============================================================================

def detect_faces(image, thresh=None, input_size=None):
    """
    Detect faces in an image using SCRFD.
    
    Args:
        image: Input image (BGR format)
        thresh: Detection threshold (optional)
        input_size: Model input size (optional)
        
    Returns:
        List of dicts with 'bbox', 'landmarks', 'confidence' for each detected face
    """
    if detector is None:
        raise RuntimeError("Face detector not initialized. Please check model file.")
    
    thresh = thresh or DETECTION_THRESHOLD
    input_size = input_size or DETECTION_INPUT_SIZE
    
    try:
        bboxes, landmarks = detector.detect(image, thresh=thresh, input_size=input_size)
        
        results = []
        for i in range(len(bboxes)):
            bbox = bboxes[i]
            x1, y1, x2, y2, score = bbox[0], bbox[1], bbox[2], bbox[3], bbox[4]
            
            result = {
                'bbox': {
                    'x': int(x1),
                    'y': int(y1),
                    'w': int(x2 - x1),
                    'h': int(y2 - y1)
                },
                'confidence': float(score) / 100 if score > 1 else float(score),
                'landmarks': landmarks[i].tolist() if landmarks is not None else None
            }
            results.append(result)
        
        return results
    except Exception as e:
        print(f"Error detecting faces: {e}")
        traceback.print_exc()
        return []


def extract_face_embedding(image, landmarks):
    """
    Extract face embedding from an image using facial landmarks for alignment.
    
    Args:
        image: Input image (BGR format)
        landmarks: Facial landmarks array of shape (5, 2)
        
    Returns:
        numpy.ndarray: 512-dimensional face embedding
    """
    if recognizer is None:
        raise RuntimeError("Face recognizer not initialized. Please check model file.")
    
    try:
        # Convert landmarks to proper format
        if isinstance(landmarks, list):
            landmarks = np.array(landmarks, dtype=np.float32)
        
        # Align face using landmarks
        aligned_face = norm_crop(image, landmarks, image_size=FACE_ALIGN_SIZE)
        
        # Extract embedding
        embedding = recognizer.get_embedding(aligned_face)
        
        return embedding
    except Exception as e:
        print(f"Error extracting face embedding: {e}")
        traceback.print_exc()
        return None


def recognize_face(face_embedding, people):
    """
    Recognize a face against the database of registered people.
    
    Args:
        face_embedding: numpy.ndarray of shape (512,)
        people: List of person records from database
        
    Returns:
        Dict with 'recognized', 'person', 'unknown_id', 'tracking_id' keys
    """
    global unknown_counter, face_tracking_counter
    
    try:
        if len(people) == 0:
            return {'recognized': False, 'person': None, 'unknown_id': None, 'tracking_id': None}
        
        # Assign tracking ID based on embedding similarity to previous frames
        tracking_id = None
        best_tracking_similarity = 0
        
        # Compare with all tracked faces from previous frames
        for tid, tracked_embedding in face_tracking_embeddings.items():
            similarity = float(np.dot(face_embedding, tracked_embedding) / 
                             (np.linalg.norm(face_embedding) * np.linalg.norm(tracked_embedding)))
            if similarity > best_tracking_similarity and similarity >= TRACKING_SIMILARITY_THRESHOLD:
                best_tracking_similarity = similarity
                tracking_id = tid
        
        # If no match found, assign new tracking ID
        if tracking_id is None:
            face_tracking_counter += 1
            tracking_id = face_tracking_counter
        
        # Update tracked embedding (keep it fresh with latest detection)
        face_tracking_embeddings[tracking_id] = face_embedding.copy()
        
        # Load all known encodings
        known_encodings = []
        known_people = []
        
        for person in people:
            person_id = person.get('id')
            encoding = load_person_encoding(person_id)
            
            if encoding is not None:
                known_encodings.append(encoding)
                known_people.append(person)
        
        if len(known_encodings) == 0:
            return {'recognized': False, 'person': None, 'unknown_id': None, 'tracking_id': tracking_id}
        
        known_encodings = np.array(known_encodings)
        
        # Compare face with all known faces using cosine similarity
        score, best_match_idx = compare_encodings(face_embedding, known_encodings)
        
        if score >= RECOGNITION_THRESHOLD and best_match_idx >= 0:
            person = known_people[best_match_idx]
            return {
                'recognized': True,
                'person': {
                    'name': person.get('name'),
                    'id': person.get('id'),
                    'employee_id': person.get('employee_id'),
                    'similarity': float(score),
                    'confidence': float(score * 100)  # Convert to percentage
                },
                'unknown_id': None,
                'tracking_id': tracking_id
            }
        else:
            # Use tracking ID for unknown persons
            unknown_id = f"Unknown-{tracking_id}"
            
            return {
                'recognized': False, 
                'person': None,
                'unknown_id': unknown_id,
                'tracking_id': tracking_id
            }
    except Exception as e:
        print(f"Error in recognize_face: {e}")
        traceback.print_exc()
        return {'recognized': False, 'person': None, 'unknown_id': None, 'tracking_id': None}


# ============================================================================
# API Endpoints
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'library': 'InsightFace (SCRFD + ArcFace)',
        'detector': 'SCRFD' if detector is not None else 'Not loaded',
        'recognizer': 'ArcFace' if recognizer is not None else 'Not loaded',
        'detection_threshold': DETECTION_THRESHOLD,
        'recognition_threshold': RECOGNITION_THRESHOLD,
        'registered_people': len(load_database()),
        'cached_encodings': len(encodings_cache)
    })


@app.route('/api/detect-and-recognize', methods=['POST'])
def detect_and_recognize():
    """Detect all faces in image and recognize each one"""
    start_time = time.time()
    try:
        if detector is None or recognizer is None:
            return jsonify({
                'error': 'Models not loaded. Please ensure SCRFD and ArcFace models are available.',
                'scrfd_path': SCRFD_MODEL_PATH,
                'arcface_path': ARCFACE_MODEL_PATH
            }), 500
        
        # Get image from request
        img = None
        region = None
        if 'image' in request.files:
            img = process_uploaded_file(request.files['image'])
        elif request.json and 'image' in request.json:
            img = base64_to_image(request.json['image'])
            region = request.json.get('region')  # Get detection region if provided
        
        if img is None:
            return jsonify({'error': 'No valid image provided'}), 400
        
        # Debug: Log image dimensions
        img_h, img_w = img.shape[:2]
        print(f"[DEBUG] Input image dimensions: {img_w}x{img_h}")
        
        # If region is specified, crop the image to that region
        if region:
            x, y, w, h = region['x'], region['y'], region['width'], region['height']
            # Ensure region is within image bounds
            x = max(0, min(x, img_w - 1))
            y = max(0, min(y, img_h - 1))
            w = min(w, img_w - x)
            h = min(h, img_h - y)
            img_crop = img[y:y+h, x:x+w]
            region_offset = (x, y)
            print(f"[DEBUG] Using detection region: x={x}, y={y}, w={w}, h={h}")
        else:
            img_crop = img
            region_offset = (0, 0)
        
        # Detect faces
        detect_start = time.time()
        detected_faces = detect_faces(img_crop)
        detect_time = (time.time() - detect_start) * 1000
        print(f"[TIMING] Face detection: {detect_time:.2f}ms")
        
        if detected_faces:
            for i, face_data in enumerate(detected_faces):
                bbox = face_data['bbox']
                print(f"[DEBUG] Face {i}: bbox={bbox}")
        
        if not detected_faces:
            return jsonify({
                'faces': [],
                'count': 0,
                'message': 'No faces detected'
            })
        
        # Load database
        people = load_database()
        
        # Recognize each face
        recognize_start = time.time()
        results = []
        for face_data in detected_faces:
            landmarks = face_data.get('landmarks')
            bbox = face_data['bbox']
            
            # Adjust bbox coordinates if we cropped the image
            if region:
                bbox['x'] += region_offset[0]
                bbox['y'] += region_offset[1]
            
            if landmarks is not None:
                # Adjust landmark coordinates if we cropped
                if region:
                    landmarks_adjusted = np.array(landmarks, dtype=np.float32)
                    landmarks_adjusted[:, 0] += region_offset[0]
                    landmarks_adjusted[:, 1] += region_offset[1]
                    landmarks = landmarks_adjusted.tolist()
                
                # Extract face embedding using aligned face from original image
                face_embedding = extract_face_embedding(img, landmarks)
                
                if face_embedding is not None:
                    recognition_result = recognize_face(face_embedding, people)
                else:
                    recognition_result = {'recognized': False, 'person': None, 'unknown_id': None, 'tracking_id': None}
            else:
                recognition_result = {'recognized': False, 'person': None, 'unknown_id': None, 'tracking_id': None}
            
            results.append({
                'bbox': bbox,
                'detection_confidence': face_data['confidence'],
                'recognized': recognition_result['recognized'],
                'person': recognition_result['person'],
                'unknown_id': recognition_result.get('unknown_id'),
                'tracking_id': recognition_result.get('tracking_id')
            })
        
        recognize_time = (time.time() - recognize_start) * 1000
        total_time = (time.time() - start_time) * 1000
        print(f"[TIMING] Face recognition: {recognize_time:.2f}ms")
        print(f"[TIMING] Total processing: {total_time:.2f}ms")
        
        return jsonify({
            'faces': results,
            'count': len(results),
            'image_width': img_w,
            'image_height': img_h,
            'latency': {
                'detection_ms': round(detect_time, 2),
                'recognition_ms': round(recognize_time, 2),
                'total_ms': round(total_time, 2)
            }
        })
    
    except Exception as e:
        print(f"Error in detect-and-recognize: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/register', methods=['POST'])
def register_person():
    """Register a new person with their face"""
    try:
        if detector is None or recognizer is None:
            return jsonify({
                'error': 'Models not loaded. Please ensure SCRFD and ArcFace models are available.'
            }), 500
        
        # Check if it's JSON or form data
        if request.is_json:
            data = request.json
            name = data.get('name')
            email = data.get('email', '')
            employee_id = data.get('employee_id', '')
            image_data = data.get('image')
            
            if not name:
                return jsonify({'error': 'Name is required'}), 400
            
            if not image_data:
                return jsonify({'error': 'Image is required'}), 400
            
            img = base64_to_image(image_data)
        else:
            # Form data
            name = request.form.get('name')
            email = request.form.get('email', '')
            employee_id = request.form.get('employee_id', '')
            
            if not name:
                return jsonify({'error': 'Name is required'}), 400
            
            # Get image
            img = None
            if 'image' in request.files:
                img = process_uploaded_file(request.files['image'])
            elif 'image' in request.form:
                img = base64_to_image(request.form['image'])
        
        if img is None:
            return jsonify({'error': 'No valid image provided'}), 400
        
        # Detect faces
        detected_faces = detect_faces(img)
        
        if len(detected_faces) == 0:
            return jsonify({'error': 'No face detected in image'}), 400
        
        if len(detected_faces) > 1:
            return jsonify({'error': 'Multiple faces detected. Please provide image with single face'}), 400
        
        face_data = detected_faces[0]
        landmarks = face_data.get('landmarks')
        
        if landmarks is None:
            return jsonify({'error': 'Could not detect facial landmarks'}), 400
        
        # Extract face embedding
        face_embedding = extract_face_embedding(img, landmarks)
        
        if face_embedding is None:
            return jsonify({'error': 'Failed to extract face features'}), 400
        
        # Generate unique ID
        person_id = str(uuid.uuid4())
        
        # Save face encoding
        save_person_encoding(person_id, face_embedding)
        
        # Save image
        image_filename = f"{person_id}.jpg"
        image_path = os.path.join(IMAGES_DIR, image_filename)
        cv2.imwrite(image_path, img)
        
        # Save aligned face as well
        aligned_face = norm_crop(img, np.array(landmarks, dtype=np.float32), image_size=FACE_ALIGN_SIZE)
        aligned_path = os.path.join(IMAGES_DIR, f"{person_id}_aligned.jpg")
        cv2.imwrite(aligned_path, aligned_face)
        
        # Load database
        people = load_database()
        
        # Add new person
        new_person = {
            'id': person_id,
            'name': name,
            'email': email,
            'employee_id': employee_id,
            'image_path': image_path,
            'aligned_path': aligned_path,
            'encoding_path': os.path.join(ENCODINGS_DIR, f"{person_id}.npy"),
            'added_date': datetime.now().isoformat(),
            'image_count': 1
        }
        
        people.append(new_person)
        
        # Save database
        if not save_database(people):
            return jsonify({'error': 'Failed to save to database'}), 500
        
        # Update cache
        names_cache[person_id] = name
        
        return jsonify({
            'message': 'Person registered successfully',
            'person': {
                'id': person_id,
                'name': name,
                'email': email,
                'employee_id': employee_id,
                'added_date': new_person['added_date'],
                'image_count': 1
            }
        })
    
    except Exception as e:
        print(f"Error in register: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/people', methods=['GET'])
def get_people():
    """Get all registered people"""
    try:
        people = load_database()
        
        # Return simplified data
        result = []
        for person in people:
            result.append({
                'id': person.get('id'),
                'name': person.get('name'),
                'email': person.get('email', ''),
                'employee_id': person.get('employee_id', ''),
                'added_date': person.get('added_date', ''),
                'image_count': person.get('image_count', 1)
            })
        
        return jsonify({'people': result})
    
    except Exception as e:
        print(f"Error in get_people: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/people/<person_id>', methods=['DELETE'])
def delete_person(person_id):
    """Delete a person from the database"""
    try:
        people = load_database()
        
        # Find person
        person = None
        for p in people:
            if p.get('id') == person_id:
                person = p
                break
        
        if not person:
            return jsonify({'error': 'Person not found'}), 404
        
        # Delete image files
        image_path = person.get('image_path')
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                print(f"Error deleting image: {e}")
        
        aligned_path = person.get('aligned_path')
        if aligned_path and os.path.exists(aligned_path):
            try:
                os.remove(aligned_path)
            except Exception as e:
                print(f"Error deleting aligned image: {e}")
        
        # Delete encoding file
        encoding_path = os.path.join(ENCODINGS_DIR, f"{person_id}.npy")
        if os.path.exists(encoding_path):
            try:
                os.remove(encoding_path)
            except Exception as e:
                print(f"Error deleting encoding: {e}")
        
        # Remove from caches
        if person_id in encodings_cache:
            del encodings_cache[person_id]
        if person_id in names_cache:
            del names_cache[person_id]
        
        # Remove from database
        people = [p for p in people if p.get('id') != person_id]
        
        if not save_database(people):
            return jsonify({'error': 'Failed to save to database'}), 500
        
        return jsonify({'message': 'Person deleted successfully'})
    
    except Exception as e:
        print(f"Error in delete_person: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/people/<person_id>/image', methods=['GET'])
def get_person_image(person_id):
    """Get a person's image"""
    try:
        people = load_database()
        
        # Find person
        person = None
        for p in people:
            if p.get('id') == person_id:
                person = p
                break
        
        if not person:
            return jsonify({'error': 'Person not found'}), 404
        
        image_path = person.get('image_path')
        if not image_path or not os.path.exists(image_path):
            return jsonify({'error': 'Image not found'}), 404
        
        return send_file(image_path, mimetype='image/jpeg')
    
    except Exception as e:
        print(f"Error in get_person_image: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Startup
# ============================================================================

# Preload encodings on startup
print("\n" + "="*50)
print("Preloading face encodings...")
try:
    num_loaded = load_all_encodings()
    print(f"✓ Loaded {num_loaded} face encodings successfully!")
except Exception as e:
    print(f"Warning during encoding preload: {e}")


if __name__ == '__main__':
    print(f"\n{'='*50}")
    print("Flask Face Recognition Backend")
    print("Library: InsightFace (SCRFD + ArcFace)")
    print(f"Detector: {'SCRFD' if detector else 'Not loaded'}")
    print(f"Recognizer: {'ArcFace' if recognizer else 'Not loaded'}")
    print(f"Detection Threshold: {DETECTION_THRESHOLD}")
    print(f"Recognition Threshold: {RECOGNITION_THRESHOLD}")
    print(f"Registered People: {len(load_database())}")
    print(f"{'='*50}\n")
    
    if detector is None or recognizer is None:
        print("⚠ WARNING: Models not fully loaded!")
        print("\nPlease download the required models:")
        print(f"  1. SCRFD: Place det_10g.onnx in {MODELS_DIR}")
        print(f"  2. ArcFace: Place w600k_r50.onnx in {MODELS_DIR}")
        print("\nOr run: python -c \"from insightface.app import FaceAnalysis; FaceAnalysis(name='buffalo_l').prepare(ctx_id=-1)\"")
        print("")
    
    # Use port 5001 to avoid conflict with macOS AirPlay Receiver on port 5000
    app.run(host='0.0.0.0', port=5001, debug=True)
