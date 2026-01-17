from ..extensions import db
from datetime import datetime

class Instrument(db.Model):
    __tablename__ = 'instruments'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(50))
    type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Enum('available', 'rented', 'unavailable', name='instrument_status'), default='available')
    price_per_day = db.Column(db.Float, nullable=False)
    photo_url = db.Column(db.String(255))
    location_name = db.Column(db.String(255))
    location_lat = db.Column(db.Float)
    location_lng = db.Column(db.Float)
    tags = db.Column(db.JSON)  # List of strings
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Cascade delete: when instrument is deleted, all rentals are also deleted
    rentals = db.relationship('Rental', backref='instrument', lazy=True, cascade='all, delete', foreign_keys='Rental.instrument_id')