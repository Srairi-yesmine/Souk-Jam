from ..extensions import db
from datetime import datetime

class Rental(db.Model):
    __tablename__ = 'rentals'
    id = db.Column(db.Integer, primary_key=True)
    instrument_id = db.Column(db.Integer, db.ForeignKey('instruments.id'), nullable=False)
    renter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    negotiated_price = db.Column(db.Float, nullable=True)
    status = db.Column(db.Enum('pending', 'confirmed', 'completed', 'cancelled', name='rental_status'), default='pending')
    owner_response = db.Column(db.Enum('pending', 'accepted', 'rejected', 'counter_offer', name='owner_response_status'), default='pending')
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)