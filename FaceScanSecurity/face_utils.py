import cv2
import numpy as np
from datetime import datetime
import logging
import os
import pickle

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def get_timestamp():
    """Get current timestamp in readable format"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_face_encoding(image_path):
    """Extract face features from an image file"""
    try:
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            logging.warning("Could not load image")
            return None
            
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            logging.warning("No faces detected in the image")
            return None
        
        # Get the largest face (assuming it's the main subject)
        largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
        x, y, w, h = largest_face
        
        # Extract face region
        face_img = gray[y:y+h, x:x+w]
        
        # Resize to a standard size
        face_img = cv2.resize(face_img, (100, 100))
        
        # Flatten the image to create a feature vector
        face_vector = face_img.flatten()
        
        # Normalize the vector
        face_vector = face_vector / 255.0
        
        return face_vector
    
    except Exception as e:
        logging.error(f"Error in face encoding: {str(e)}")
        return None

def find_face_match(face_encoding, stored_encodings, users, tolerance=0.8):
    """Find a matching face in stored encodings using a simple distance metric"""
    try:
        if not stored_encodings:
            return None
        
        # Create a list of known encodings and IDs
        known_encodings = []
        known_ids = []
        
        for user_id, encoding in stored_encodings.items():
            known_encodings.append(encoding)
            known_ids.append(user_id)
        
        if not known_encodings:
            return None
        
        # Find the best match using Euclidean distance
        best_match_index = -1
        best_match_distance = float('inf')
        
        for i, encoding in enumerate(known_encodings):
            # Calculate distance
            distance = np.linalg.norm(face_encoding - encoding)
            
            if distance < best_match_distance:
                best_match_distance = distance
                best_match_index = i
        
        # Lower distance is better, higher similarity percentage
        max_distance = np.sqrt(len(face_encoding))  # Maximum possible distance
        similarity = max(0, 100 - (best_match_distance / max_distance * 100))
        confidence = round(similarity, 2)
        
        # Set a threshold for matches
        threshold = (1 - tolerance) * 100
        
        if confidence >= threshold:
            matched_id = known_ids[best_match_index]
            
            # Find user info
            matched_user = next((user for user in users if user['id'] == matched_id), None)
            
            if matched_user:
                # Return user info with confidence
                return {
                    'id': matched_id,
                    'name': matched_user['name'],
                    'confidence': confidence
                }
        
        return None
    
    except Exception as e:
        logging.error(f"Error in face matching: {str(e)}")
        return None

def detect_faces_from_image(image_data):
    """Detect faces in a raw image data"""
    try:
        # Convert image data to numpy array
        np_arr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Format similarly to face_recognition library for compatibility
        face_locations = []
        for (x, y, w, h) in faces:
            # Convert to format: (top, right, bottom, left)
            face_locations.append((y, x+w, y+h, x))
        
        return face_locations, img
    
    except Exception as e:
        logging.error(f"Error in face detection: {str(e)}")
        return [], None
