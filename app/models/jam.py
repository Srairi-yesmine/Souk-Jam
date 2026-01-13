from ..extensions import db
from datetime import datetime

class JamRequest(db.Model):
    __tablename__ = 'jam_requests'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum('pending', 'accepted', 'rejected', 'skipped', name='jam_status'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_requests')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_requests')

    __table_args__ = (db.Index('idx_sender_receiver', 'sender_id', 'receiver_id'),)