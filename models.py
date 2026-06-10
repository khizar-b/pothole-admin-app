from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Admin {self.username}>'

class PotholeRecord(db.Model):
    __tablename__ = 'pothole_records'
    
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    bbox_x = db.Column(db.Float, nullable=False)
    bbox_y = db.Column(db.Float, nullable=False)
    bbox_width = db.Column(db.Float, nullable=False)
    bbox_height = db.Column(db.Float, nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    impact_score = db.Column(db.Float, nullable=False, default=0.0)
    bike_impact = db.Column(db.String(20), nullable=False, default='low')
    car_impact = db.Column(db.String(20), nullable=False, default='low')
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.String(80), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'image_name': self.image_name,
            'timestamp': self.timestamp.isoformat(),
            'bounding_box': {
                'x': self.bbox_x,
                'y': self.bbox_y,
                'width': self.bbox_width,
                'height': self.bbox_height
            },
            'confidence_score': self.confidence_score,
            'impact_score': self.impact_score,
            'bike_impact': self.bike_impact,
            'car_impact': self.car_impact,
            'gps_location': {
                'latitude': self.latitude,
                'longitude': self.longitude
            },
            'uploaded_at': self.uploaded_at.isoformat(),
            'uploaded_by': self.uploaded_by
        }
    
    def __repr__(self):
        return f'<PotholeRecord {self.image_name}>'
