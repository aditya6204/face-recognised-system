import os
import logging
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import numpy as np
from werkzeug.utils import secure_filename
import face_utils
import os.path
from models import db, User, FaceEncoding

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "face_recognition_secret")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the database
db.init_app(app)

# Ensure directories exist for temporary files
UPLOAD_FOLDER = 'face_data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Create tables if they don't exist
with app.app_context():
    db.create_all()
    logging.info("Database tables created")

# Helper functions
def load_data():
    try:
        # Get all users and their encodings
        users = User.query.all()
        
        # Format into dictionaries for compatibility with existing code
        user_dicts = [user.to_dict() for user in users]
        
        # Format encodings dictionary
        encodings = {}
        for user in users:
            if user.face_encoding:
                encodings[user.id] = user.face_encoding.get_encoding()
        
        return encodings, user_dicts
    except Exception as e:
        logging.error(f"Error loading face data from database: {str(e)}")
        return {}, []

def save_user_with_encoding(user_id, name, face_encoding_array):
    try:
        # Create new user
        user = User(id=user_id, name=name)
        db.session.add(user)
        
        # Create and associate face encoding
        face_encoding = FaceEncoding(user_id=user_id)
        face_encoding.set_encoding(face_encoding_array)
        db.session.add(face_encoding)
        
        # Commit to database
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error saving face data to database: {str(e)}")
        return False

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enroll')
def enroll():
    return render_template('enroll.html')

@app.route('/verify')
def verify():
    return render_template('verify.html')

@app.route('/manage')
def manage():
    _, users = load_data()
    return render_template('manage.html', users=users)

@app.route('/api/enroll', methods=['POST'])
def api_enroll():
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image provided'})
    
    image_file = request.files['image']
    name = request.form.get('name', '')
    
    if not name:
        return jsonify({'success': False, 'message': 'Name is required'})
    
    # Process the image
    try:
        # Save image temporarily
        temp_filename = os.path.join(UPLOAD_FOLDER, f"temp_{uuid.uuid4()}.jpg")
        image_file.save(temp_filename)
        
        # Detect and encode face
        face_encoding = face_utils.get_face_encoding(temp_filename)
        
        # Remove temporary file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        
        if face_encoding is None:
            return jsonify({'success': False, 'message': 'No face detected in the image'})
        
        # Check if user already exists
        existing_user = User.query.filter(User.name.ilike(name)).first()
        if existing_user:
            return jsonify({'success': False, 'message': 'User with this name already exists'})
        
        # Generate user ID
        user_id = str(uuid.uuid4())
        
        # Save the user and face encoding to database
        if save_user_with_encoding(user_id, name, face_encoding):
            return jsonify({'success': True, 'message': f'User {name} enrolled successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save user data'})
    
    except Exception as e:
        logging.error(f"Error in enrollment: {str(e)}")
        return jsonify({'success': False, 'message': f'Error during enrollment: {str(e)}'})

@app.route('/api/verify', methods=['POST'])
def api_verify():
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image provided'})
    
    image_file = request.files['image']
    
    # Process the image
    try:
        # Save image temporarily
        temp_filename = os.path.join(UPLOAD_FOLDER, f"temp_{uuid.uuid4()}.jpg")
        image_file.save(temp_filename)
        
        # Detect and encode face
        face_encoding = face_utils.get_face_encoding(temp_filename)
        
        # Remove temporary file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        
        if face_encoding is None:
            return jsonify({'success': False, 'message': 'No face detected in the image'})
        
        # Compare with stored encodings
        encodings, users = load_data()
        
        if not encodings:
            return jsonify({'success': False, 'message': 'No enrolled users found'})
        
        # Find the best match
        match = face_utils.find_face_match(face_encoding, encodings, users)
        
        if match:
            return jsonify({
                'success': True, 
                'authenticated': True,
                'user': match['name'],
                'confidence': match['confidence']
            })
        else:
            return jsonify({
                'success': True,
                'authenticated': False,
                'message': 'Face not recognized'
            })
    
    except Exception as e:
        logging.error(f"Error in verification: {str(e)}")
        return jsonify({'success': False, 'message': f'Error during verification: {str(e)}'})

@app.route('/api/delete_user', methods=['POST'])
def delete_user():
    user_id = request.form.get('user_id')
    if not user_id:
        flash('User ID is required', 'danger')
        return redirect(url_for('manage'))
    
    try:
        # Find the user by ID
        user = User.query.get(user_id)
        
        if user:
            # Delete the user (cascade will delete face encoding too)
            db.session.delete(user)
            db.session.commit()
            flash('User deleted successfully', 'success')
        else:
            flash('User not found', 'danger')
            
        return redirect(url_for('manage'))
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting user: {str(e)}")
        flash(f'Error deleting user: {str(e)}', 'danger')
        return redirect(url_for('manage'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
