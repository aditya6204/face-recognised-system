from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pickle
import numpy as np

# This will be initialized in app.py
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    added = db.Column(db.DateTime, default=datetime.now)
    
    # Relationship with face encodings
    face_encoding = db.relationship('FaceEncoding', backref='user', uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.name}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'added': self.added.strftime("%Y-%m-%d %H:%M:%S") if self.added else None
        }

class FaceEncoding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, unique=True)
    encoding_data = db.Column(db.LargeBinary, nullable=False)
    
    def set_encoding(self, numpy_array):
        """Serialize numpy array to binary data"""
        self.encoding_data = pickle.dumps(numpy_array)
    
    def get_encoding(self):
        """Deserialize binary data to numpy array"""
        if self.encoding_data:
            return pickle.loads(self.encoding_data)
        return None
