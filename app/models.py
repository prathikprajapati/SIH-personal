from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class CertificateVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.String(100), unique=True, nullable=False)
    verification_key = db.Column(db.String(256), nullable=False)  # SHA256 hash
    random_text = db.Column(db.Text, nullable=False)  # Original random text
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    verified_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<CertificateVerification {self.certificate_id}>'

    @staticmethod
    def generate_random_text():
        """Generate a random text for QR code"""
        return str(uuid.uuid4())

    @staticmethod
    def hash_text(text):
        """Hash the text using SHA256"""
        import hashlib
        return hashlib.sha256(text.encode()).hexdigest()
