from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import face_recognition
import cv2
import numpy as np
import json
import base64
import os
import uuid
from datetime import datetime
import traceback
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

# Database configuration
DB_FOLDER = os.path.join(os.path.dirname(__file__), 'database', 'faces')
DB_JSON = os.path.join(os.path.dirname(__file__), 'database', 'people.json')
IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'database', 'images')
ENCODINGS_DIR = os.path.join(os.path.dirname(__file__), 'database', 'encodings')

# Model configuration
TOLERANCE = 0.6  # Lower is more strict (0.6 is default, good balance)
MODEL = 'hog'  # 'hog' is faster, 'cnn' is more accurate but requires GPU

# Create necessary directories
os.makedirs(DB_FOLDER, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(ENCODINGS_DIR, exist_ok=True)

# Cache for face encodings (for faster real-time detection)
encodings_cache = {}

# Initialize JSON database
if not os.path.exists(DB_JSON):
    with open(DB_JSON, 'w') as f:
        json.dump([], f)

# Helper functions
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

def base64_to_image(base64_str):
    """Convert base64 string to numpy array (RGB format for face_recognition)"""
    try:
        # Remove data URL prefix if present
        if ',' in base64_str:
            base64_str = base64_str.split(',')[1]
        
        # Decode base64
        img_data = base64.b64decode(base64_str)
        
        # Use PIL to handle the image properly
        pil_image = Image.open(io.BytesIO(img_data))
        
        # Convert to RGB (face_recognition requires RGB)
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Convert to numpy array
        img = np.array(pil_image)
        
        return img
    except Exception as e:
        print(f"Error converting base64 to image: {e}")
        traceback.print_exc()
        return None

def process_uploaded_file(file):
    """Process uploaded file to numpy array (RGB format)"""
    try:
        pil_image = Image.open(file)
        
        # Convert to RGB
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        img = np.array(pil_image)
        return img
    except Exception as e:
        print(f"Error processing uploaded file: {e}")
        traceback.print_exc()
        return None

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

def detect_and_extract_faces(img, model='hog'):
    """
    Detect and extract faces from image using face_recognition.
    Returns list of dicts with bbox, face, and face_encoding.
    model: 'hog' (faster, CPU) or 'cnn' (more accurate, GPU recommended)
    """
    try:
        # Detect face locations
        face_locations = face_recognition.face_locations(img, model=model)
        
        # Get face encodings
        face_encodings = face_recognition.face_encodings(img, face_locations)
        
        results = []
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Extract face region
            face_img = img[top:bottom, left:right]
            
            # Calculate bounding box
            bbox = {
                'x': left,
                'y': top,
                'w': right - left,
                'h': bottom - top
            }
            
            results.append({
                'bbox': bbox,
                'face': face_img,
                'encoding': face_encoding,
                'confidence': 1.0  # face_recognition doesn't provide confidence, so we use 1.0
            })
        
        return results
    except Exception as e:
        print(f"Error detecting faces: {e}")
        traceback.print_exc()
        return []

def recognize_face(face_encoding, people):
    """
    Recognize a face against the database of registered people.
    Returns dict with recognized status and person details.
    """
    try:
        if len(people) == 0:
            return {
                'recognized': False,
                'person': None
            }
        
        best_match = None
        best_distance = float('inf')
        
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
            return {
                'recognized': False,
                'person': None
            }
        
        # Compare face with all known faces
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=TOLERANCE)
        
        # Find best match
        for i, (match, distance) in enumerate(zip(matches, face_distances)):
            if match and distance < best_distance:
                best_distance = distance
                person = known_people[i]
                
                best_match = {
                    'name': person.get('name'),
                    'id': person.get('id'),
                    'employee_id': person.get('employee_id'),
                    'distance': float(distance),
                    'confidence': float((1 - distance) * 100)  # Convert to percentage
                }
        
        if best_match:
            return {
                'recognized': True,
                'person': best_match
            }
        else:
            return {
                'recognized': False,
                'person': None
            }
    except Exception as e:
        print(f"Error in recognize_face: {e}")
        traceback.print_exc()
        return {
            'recognized': False,
            'person': None
        }

# API Endpoints

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'library': 'face_recognition',
        'model': MODEL,
        'tolerance': TOLERANCE,
        'registered_people': len(load_database())
    })

@app.route('/api/detect-and-recognize', methods=['POST'])
def detect_and_recognize():
    """Detect all faces in image and recognize each one"""
    try:
        # Get image from request
        img = None
        if 'image' in request.files:
            img = process_uploaded_file(request.files['image'])
        elif request.json and 'image' in request.json:
            img = base64_to_image(request.json['image'])
        
        if img is None:
            return jsonify({'error': 'No valid image provided'}), 400
        
        # Detect faces
        detected_faces = detect_and_extract_faces(img, model=MODEL)
        
        if not detected_faces:
            return jsonify({
                'faces': [],
                'count': 0,
                'message': 'No faces detected'
            })
        
        # Load database
        people = load_database()
        
        # Recognize each face
        results = []
        for face_data in detected_faces:
            face_encoding = face_data['encoding']
            recognition_result = recognize_face(face_encoding, people)
            
            results.append({
                'bbox': face_data['bbox'],
                'detection_confidence': face_data['confidence'],
                'recognized': recognition_result['recognized'],
                'person': recognition_result['person']
            })
        
        return jsonify({
            'faces': results,
            'count': len(results)
        })
    
    except Exception as e:
        print(f"Error in detect-and-recognize: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register_person():
    """Register a new person with their face"""
    try:
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
        detected_faces = detect_and_extract_faces(img, model=MODEL)
        
        if len(detected_faces) == 0:
            return jsonify({'error': 'No face detected in image'}), 400
        
        if len(detected_faces) > 1:
            return jsonify({'error': 'Multiple faces detected. Please provide image with single face'}), 400
        
        # Generate unique ID
        person_id = str(uuid.uuid4())
        
        # Save face encoding
        face_encoding = detected_faces[0]['encoding']
        save_person_encoding(person_id, face_encoding)
        
        # Save image (convert RGB to BGR for OpenCV)
        image_filename = f"{person_id}.jpg"
        image_path = os.path.join(IMAGES_DIR, image_filename)
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.imwrite(image_path, img_bgr)
        
        # Load database
        people = load_database()
        
        # Add new person
        new_person = {
            'id': person_id,
            'name': name,
            'email': email,
            'employee_id': employee_id,
            'image_path': image_path,
            'encoding_path': os.path.join(ENCODINGS_DIR, f"{person_id}.npy"),
            'added_date': datetime.now().isoformat(),
            'image_count': 1
        }
        
        people.append(new_person)
        
        # Save database
        if not save_database(people):
            return jsonify({'error': 'Failed to save to database'}), 500
        
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
        
        # Delete image file
        image_path = person.get('image_path')
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                print(f"Error deleting image: {e}")
        
        # Delete encoding file
        encoding_path = os.path.join(ENCODINGS_DIR, f"{person_id}.npy")
        if os.path.exists(encoding_path):
            try:
                os.remove(encoding_path)
            except Exception as e:
                print(f"Error deleting encoding: {e}")
        
        # Remove from cache
        if person_id in encodings_cache:
            del encodings_cache[person_id]
        
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

# Preload encodings on startup
print("Preloading face encodings...")
try:
    people = load_database()
    for person in people:
        person_id = person.get('id')
        load_person_encoding(person_id)
    print(f"✓ Loaded {len(encodings_cache)} face encodings successfully!")
except Exception as e:
    print(f"Warning during encoding preload: {e}")

if __name__ == '__main__':
    print(f"\n{'='*50}")
    print(f"Flask Face Recognition Backend")
    print(f"Library: face_recognition (dlib)")
    print(f"Model: {MODEL}")
    print(f"Tolerance: {TOLERANCE}")
    print(f"Registered People: {len(load_database())}")
    print(f"{'='*50}\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
