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

    # Blockchain-like functionality
    previous_hash = db.Column(db.String(256), nullable=True)  # Hash of previous certificate
    certificate_hash = db.Column(db.String(256), nullable=False)  # Hash of current certificate
    chain_index = db.Column(db.Integer, default=0)  # Position in the certificate chain

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

    @staticmethod
    def calculate_certificate_hash(certificate_data, previous_hash=None):
        """Calculate the hash for a certificate including blockchain linking"""
        import hashlib
        import json

        # Create certificate data dictionary
        cert_dict = {
            'certificate_id': certificate_data.get('certificate_id'),
            'random_text': certificate_data.get('random_text'),
            'created_at': certificate_data.get('created_at', datetime.utcnow().isoformat()),
            'previous_hash': previous_hash
        }

        # Convert to JSON string for consistent hashing
        cert_string = json.dumps(cert_dict, sort_keys=True)
        return hashlib.sha256(cert_string.encode()).hexdigest()

    @staticmethod
    def get_last_certificate():
        """Get the last certificate in the chain"""
        return CertificateVerification.query.order_by(CertificateVerification.chain_index.desc()).first()

    def verify_chain_integrity(self):
        """Verify if this certificate's chain is intact"""
        if self.previous_hash is None:
            # First certificate in chain - should have chain_index 0
            return self.chain_index == 0

        # Find the previous certificate
        previous_cert = CertificateVerification.query.filter_by(certificate_hash=self.previous_hash).first()

        if not previous_cert:
            return False

        # Verify the chain index is sequential
        if self.chain_index != previous_cert.chain_index + 1:
            return False

        # Verify the previous certificate's hash matches
        expected_previous_hash = previous_cert.certificate_hash
        return self.previous_hash == expected_previous_hash
