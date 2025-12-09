from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from deepface import DeepFace
import cv2
import numpy as np
import json
import base64
import os
import uuid
from datetime import datetime
import traceback

app = Flask(__name__)
CORS(app)

# Database configuration
DB_FOLDER = os.path.join(os.path.dirname(__file__), 'database', 'faces')
DB_JSON = os.path.join(os.path.dirname(__file__), 'database', 'people.json')
IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'database', 'images')

# Model configuration
MODEL_NAME = 'VGG-Face'
THRESHOLD = 0.6

# Create necessary directories
os.makedirs(DB_FOLDER, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

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
    """Convert base64 string to numpy array"""
    try:
        # Remove data URL prefix if present
        if ',' in base64_str:
            base64_str = base64_str.split(',')[1]
        
        # Decode base64
        img_data = base64.b64decode(base64_str)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Error converting base64 to image: {e}")
        return None

def process_uploaded_file(file):
    """Process uploaded file to numpy array"""
    try:
        file_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Error processing uploaded file: {e}")
        return None

def detect_and_extract_faces(img):
    """
    Detect and extract faces from image using DeepFace.
    Returns list of dicts with bbox, face, and confidence.
    """
    try:
        # Use DeepFace to extract faces
        faces = DeepFace.extract_faces(
            img_path=img,
            detector_backend='opencv',
            enforce_detection=False,
            align=True
        )
        
        results = []
        for face_data in faces:
            # Get facial area (bbox)
            facial_area = face_data.get('facial_area', {})
            
            # Extract face image
            face_img = face_data.get('face')
            
            # Convert face from 0-1 range to 0-255 if needed
            if face_img is not None and face_img.max() <= 1.0:
                face_img = (face_img * 255).astype(np.uint8)
            
            # Get confidence
            confidence = face_data.get('confidence', 0)
            
            results.append({
                'bbox': {
                    'x': facial_area.get('x', 0),
                    'y': facial_area.get('y', 0),
                    'w': facial_area.get('w', 0),
                    'h': facial_area.get('h', 0)
                },
                'face': face_img,
                'confidence': confidence
            })
        
        return results
    except Exception as e:
        print(f"Error detecting faces: {e}")
        traceback.print_exc()
        return []

def recognize_face(face_img, people):
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
        
        # Save temporary face image
        temp_face_path = os.path.join(IMAGES_DIR, f'temp_{uuid.uuid4()}.jpg')
        cv2.imwrite(temp_face_path, face_img)
        
        best_match = None
        best_distance = float('inf')
        
        # Compare with all registered people
        for person in people:
            try:
                person_image_path = person.get('image_path')
                if not person_image_path or not os.path.exists(person_image_path):
                    continue
                
                # Verify face
                result = DeepFace.verify(
                    img1_path=temp_face_path,
                    img2_path=person_image_path,
                    model_name=MODEL_NAME,
                    detector_backend='opencv',
                    enforce_detection=False
                )
                
                distance = result.get('distance', float('inf'))
                verified = result.get('verified', False)
                
                # Check if this is the best match
                if verified and distance < best_distance and distance <= THRESHOLD:
                    best_distance = distance
                    best_match = {
                        'name': person.get('name'),
                        'id': person.get('id'),
                        'employee_id': person.get('employee_id'),
                        'distance': distance,
                        'confidence': 1 - (distance / THRESHOLD) if THRESHOLD > 0 else 0
                    }
            except Exception as e:
                print(f"Error verifying against {person.get('name')}: {e}")
                continue
        
        # Clean up temp file
        try:
            if os.path.exists(temp_face_path):
                os.remove(temp_face_path)
        except:
            pass
        
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
        'model': MODEL_NAME,
        'threshold': THRESHOLD
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
        detected_faces = detect_and_extract_faces(img)
        
        if not detected_faces:
            return jsonify({
                'faces': [],
                'count': 0
            })
        
        # Load database
        people = load_database()
        
        # Recognize each face
        results = []
        for face_data in detected_faces:
            face_img = face_data['face']
            recognition_result = recognize_face(face_img, people)
            
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
        detected_faces = detect_and_extract_faces(img)
        
        if len(detected_faces) == 0:
            return jsonify({'error': 'No face detected in image'}), 400
        
        if len(detected_faces) > 1:
            return jsonify({'error': 'Multiple faces detected. Please provide image with single face'}), 400
        
        # Generate unique ID and save image
        person_id = str(uuid.uuid4())
        image_filename = f"{person_id}.jpg"
        image_path = os.path.join(IMAGES_DIR, image_filename)
        
        # Save the original image
        cv2.imwrite(image_path, img)
        
        # Load database
        people = load_database()
        
        # Add new person
        new_person = {
            'id': person_id,
            'name': name,
            'email': email,
            'employee_id': employee_id,
            'image_path': image_path,
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
                'employee_id': employee_id
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
                'added_date': person.get('added_date') or person.get('registered_at'),
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

# Preload model on startup
print("Preloading VGG-Face model...")
try:
    # Create a dummy image to trigger model loading
    dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
    DeepFace.represent(
        img_path=dummy_img,
        model_name=MODEL_NAME,
        detector_backend='opencv',
        enforce_detection=False
    )
    print(f"✓ {MODEL_NAME} model loaded successfully!")
except Exception as e:
    print(f"Warning during model preload: {e}")

if __name__ == '__main__':
    print(f"\n{'='*50}")
    print(f"Flask Face Recognition Backend")
    print(f"Model: {MODEL_NAME}")
    print(f"Threshold: {THRESHOLD}")
    print(f"{'='*50}\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
