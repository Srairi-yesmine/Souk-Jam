from ..extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    location_name = db.Column(db.String(255))
    location_lat = db.Column(db.Float)
    location_lng = db.Column(db.Float)
    role = db.Column(db.Enum('owner', 'renter', 'jammer', name='user_role'), nullable=False, default='jammer')
    genres_enjoyed = db.Column(db.JSON, default=list)
    instruments_played = db.Column(db.JSON, default=list)
    instruments_owned = db.Column(db.JSON, default=list)
    is_active_for_jam = db.Column(db.Boolean, default=False)
    profile_photo_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    instruments = db.relationship('Instrument', backref='owner', lazy=True)
    rentals = db.relationship('Rental', backref='renter', lazy=True)

    def __init__(self, **kwargs):
        """Normalize email to lowercase on user creation"""
        if 'email' in kwargs:
            kwargs['email'] = kwargs['email'].strip().lower()
        super(User, self).__init__(**kwargs)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_email(email):
        """Find user by email (case-insensitive, whitespace-tolerant)"""
        if not email:
            return None
        normalized_email = email.strip().lower()
        return User.query.filter_by(email=normalized_email).first()