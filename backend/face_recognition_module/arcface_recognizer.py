"""
ArcFace Face Recognition Module using ONNX Runtime
Based on: https://github.com/vectornguyen76/face-recognition

ArcFace is a state-of-the-art face recognition model known for its
robustness to variations in lighting, pose, and facial expressions.
"""

import os
import cv2
import numpy as np
import onnxruntime


class ArcFaceRecognizer:
    """
    ArcFace Face Recognition using ONNX Runtime.
    
    This recognizer extracts 512-dimensional face embeddings that can be
    used for face verification and identification.
    """
    
    def __init__(self, model_file=None, session=None):
        """
        Initialize ArcFace recognizer.
        
        Args:
            model_file: Path to the ONNX model file
            session: Existing ONNX Runtime session (optional)
        """
        self.model_file = model_file
        self.session = session
        
        if self.session is None:
            assert self.model_file is not None
            assert os.path.exists(self.model_file), f"Model file not found: {self.model_file}"
            # Try GPU first, fallback to CPU
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
            self.session = onnxruntime.InferenceSession(
                self.model_file,
                providers=providers
            )
            print(f"ArcFace using provider: {self.session.get_providers()[0]}")
        
        self._init_vars()

    def _init_vars(self):
        """Initialize model variables from the ONNX model."""
        input_cfg = self.session.get_inputs()[0]
        self.input_name = input_cfg.name
        self.input_shape = input_cfg.shape
        
        output_cfg = self.session.get_outputs()[0]
        self.output_name = output_cfg.name
        
        # Expected input size (typically 112x112 for ArcFace)
        if len(self.input_shape) >= 3:
            self.input_size = (self.input_shape[2], self.input_shape[3]) if len(self.input_shape) == 4 else (112, 112)
        else:
            self.input_size = (112, 112)

    def preprocess(self, face_image):
        """
        Preprocess face image for ArcFace model.
        
        Args:
            face_image: Input face image (BGR format, should be aligned)
            
        Returns:
            Preprocessed image tensor ready for inference
        """
        # Convert BGR to RGB
        if len(face_image.shape) == 3 and face_image.shape[2] == 3:
            face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
        
        # Resize to expected input size if necessary
        if face_image.shape[:2] != self.input_size:
            face_image = cv2.resize(face_image, self.input_size)
        
        # Normalize to [-1, 1] (standard for ArcFace: (x - 127.5) / 127.5)
        face_image = face_image.astype(np.float32)
        face_image = (face_image - 127.5) / 127.5
        
        # Transpose to NCHW format (batch, channels, height, width)
        face_image = face_image.transpose(2, 0, 1)
        face_image = np.expand_dims(face_image, axis=0)
        
        return face_image

    def get_embedding(self, face_image):
        """
        Extract face embedding from an aligned face image.
        
        Args:
            face_image: Aligned face image (BGR format, 112x112)
            
        Returns:
            numpy.ndarray: Normalized 512-dimensional face embedding
        """
        # Preprocess the image
        input_tensor = self.preprocess(face_image)
        
        # Run inference
        outputs = self.session.run([self.output_name], {self.input_name: input_tensor})
        embedding = outputs[0][0]
        
        # Normalize the embedding
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding

    def get_embeddings_batch(self, face_images):
        """
        Extract face embeddings from a batch of aligned face images.
        
        Args:
            face_images: List of aligned face images (BGR format, 112x112)
            
        Returns:
            numpy.ndarray: Array of normalized 512-dimensional face embeddings
        """
        if len(face_images) == 0:
            return np.array([])
        
        embeddings = []
        for face_image in face_images:
            embedding = self.get_embedding(face_image)
            embeddings.append(embedding)
        
        return np.array(embeddings)


def compare_encodings(query_encoding, known_encodings):
    """
    Compare a query face encoding against known encodings.
    
    Uses cosine similarity (dot product of normalized vectors).
    
    Args:
        query_encoding: numpy.ndarray of shape (512,) - the query face embedding
        known_encodings: numpy.ndarray of shape (N, 512) - known face embeddings
        
    Returns:
        Tuple of (score, best_match_index) where:
            - score: Similarity score (0-1, higher is more similar)
            - best_match_index: Index of the best matching encoding
    """
    if len(known_encodings) == 0:
        return 0.0, -1
    
    # Compute cosine similarities (dot product since vectors are normalized)
    similarities = np.dot(known_encodings, query_encoding.T)
    
    best_match_index = np.argmax(similarities)
    best_score = similarities[best_match_index]
    
    # Ensure score is a scalar
    if hasattr(best_score, '__iter__'):
        best_score = float(best_score.flat[0])
    else:
        best_score = float(best_score)
    
    return best_score, int(best_match_index)


def compute_similarity(embedding1, embedding2):
    """
    Compute cosine similarity between two face embeddings.
    
    Args:
        embedding1: First face embedding (512-dimensional)
        embedding2: Second face embedding (512-dimensional)
        
    Returns:
        float: Cosine similarity score (0-1)
    """
    return float(np.dot(embedding1, embedding2))
