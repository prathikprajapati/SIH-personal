import os
from app import create_app
from app.certificate_generator import CertificateGenerator
from app.models import db, CertificateVerification
from datetime import datetime

def generate_and_store_certificate():
    app, socketio = create_app()
    with app.app_context():
        # Sample drive info
        drive_info = {
            "model": "Seagate Barracuda 2TB",
            "serial_number": "SN-HDD-123456789",
            "capacity": "2 TB"
        }
        wipe_method = "NIST Purge (Overwrite)"
        serial_number = "CERT-" + datetime.utcnow().strftime("%Y%m%d%H%M%S")

        cert_gen = CertificateGenerator(f"certificate_{serial_number}.pdf")
        cert_path, random_text = cert_gen.generate_certificate(drive_info, wipe_method, serial_number)

        # Get last certificate for blockchain linking
        last_cert = CertificateVerification.get_last_certificate()
        previous_hash = last_cert.certificate_hash if last_cert else None
        chain_index = (last_cert.chain_index + 1) if last_cert else 0

        certificate_data = {
            "certificate_id": serial_number,
            "random_text": random_text,
            "created_at": datetime.utcnow().isoformat()
        }

        certificate_hash = CertificateVerification.calculate_certificate_hash(certificate_data, previous_hash)
        verification_key = CertificateVerification.hash_text(random_text)

        cert_verification = CertificateVerification(
            certificate_id=serial_number,
            verification_key=verification_key,
            random_text=random_text,
            previous_hash=previous_hash,
            certificate_hash=certificate_hash,
            chain_index=chain_index
        )

        db.session.add(cert_verification)
        db.session.commit()

        print(f"Certificate generated and stored: {cert_path}")
        print(f"Certificate ID: {serial_number}")
        print(f"Verification key: {verification_key}")

if __name__ == "__main__":
    generate_and_store_certificate()
