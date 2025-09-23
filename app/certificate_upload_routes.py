from flask import Blueprint, request, jsonify
from .models import CertificateVerification, db
from datetime import datetime
import json
import hashlib

certificate_upload_bp = Blueprint('certificate_upload', __name__)

@certificate_upload_bp.route('/upload_certificate', methods=['POST'])
def upload_certificate():
    """Receive certificate from desktop wiping tool"""
    try:
        certificate_data = request.get_json()

        if not certificate_data:
            return jsonify({"error": "No certificate data provided"}), 400

        # Validate required fields
        required_fields = ['certificate_id', 'device_info', 'wipe_method', 'timestamp', 'certificate_hash']
        for field in required_fields:
            if field not in certificate_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Verify certificate integrity
        if not verify_certificate_integrity(certificate_data):
            return jsonify({"error": "Certificate integrity check failed"}), 400

        # Check if certificate already exists
        existing_cert = CertificateVerification.query.filter_by(
            certificate_id=certificate_data['certificate_id']
        ).first()

        if existing_cert:
            return jsonify({"error": "Certificate already exists"}), 409

        # Get the last certificate in the chain for blockchain functionality
        last_certificate = CertificateVerification.get_last_certificate()
        previous_hash = last_certificate.certificate_hash if last_certificate else None
        chain_index = (last_certificate.chain_index + 1) if last_certificate else 0

        # Prepare certificate data for hash calculation
        cert_data_for_hash = {
            'certificate_id': certificate_data['certificate_id'],
            'device_info': certificate_data['device_info'],
            'wipe_method': certificate_data['wipe_method'],
            'timestamp': certificate_data['timestamp']
        }

        # Calculate the certificate hash including blockchain linking
        certificate_hash = CertificateVerification.calculate_certificate_hash(
            cert_data_for_hash, previous_hash
        )

        # Create verification record
        verification_key = CertificateVerification.hash_text(
            certificate_data.get('signature', certificate_data['certificate_id'])
        )

        cert_verification = CertificateVerification(
            certificate_id=certificate_data['certificate_id'],
            verification_key=verification_key,
            random_text=certificate_data.get('signature', certificate_data['certificate_id']),
            previous_hash=previous_hash,
            certificate_hash=certificate_hash,
            chain_index=chain_index,
            is_verified=True,  # Desktop tool certificates are pre-verified
            verified_at=datetime.utcnow()
        )

        # Store additional metadata
        cert_verification.device_info = json.dumps(certificate_data['device_info'])
        cert_verification.wipe_method = certificate_data['wipe_method']
        cert_verification.wiper_version = certificate_data.get('wiper_version', '1.0.0')

        db.session.add(cert_verification)
        db.session.commit()

        print(f"✅ Certificate {certificate_data['certificate_id']} uploaded and added to blockchain (Chain Index: {chain_index})")
        if previous_hash:
            print(f"   ↳ Linked to previous certificate: {previous_hash[:16]}...")

        return jsonify({
            "message": "Certificate uploaded successfully",
            "certificate_id": certificate_data['certificate_id'],
            "chain_index": chain_index,
            "blockchain_hash": certificate_hash
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error uploading certificate: {e}")
        return jsonify({"error": str(e)}), 500

def verify_certificate_integrity(certificate_data):
    """Verify the integrity of uploaded certificate"""
    try:
        # Recalculate certificate hash
        cert_data_for_hash = {
            'certificate_id': certificate_data['certificate_id'],
            'device_info': certificate_data['device_info'],
            'wipe_method': certificate_data['wipe_method'],
            'timestamp': certificate_data['timestamp']
        }

        # Calculate hash without previous_hash (since this is a new certificate)
        cert_string = json.dumps(cert_data_for_hash, sort_keys=True)
        calculated_hash = hashlib.sha256(cert_string.encode()).hexdigest()

        # Compare with provided hash
        return calculated_hash == certificate_data['certificate_hash']

    except Exception as e:
        print(f"Certificate integrity verification failed: {e}")
        return False

@certificate_upload_bp.route('/sync_certificates', methods=['POST'])
def sync_certificates():
    """Sync multiple certificates from desktop tool"""
    try:
        sync_data = request.get_json()

        if not sync_data or 'certificates' not in sync_data:
            return jsonify({"error": "No certificates data provided"}), 400

        uploaded_count = 0
        failed_count = 0

        for cert_data in sync_data['certificates']:
            try:
                # Use the same upload logic for each certificate
                response = upload_certificate()
                # This is a simplified version - in practice you'd call the upload function directly
                if response[1] == 201:  # HTTP 201 Created
                    uploaded_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
                print(f"Failed to sync certificate {cert_data.get('certificate_id', 'unknown')}: {e}")

        return jsonify({
            "message": "Sync completed",
            "uploaded": uploaded_count,
            "failed": failed_count,
            "total": len(sync_data['certificates'])
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@certificate_upload_bp.route('/desktop_status', methods=['GET'])
def desktop_status():
    """Get status information for desktop tool"""
    try:
        total_certificates = CertificateVerification.query.count()
        recent_certificates = CertificateVerification.query.order_by(
            CertificateVerification.created_at.desc()
        ).limit(5).all()

        return jsonify({
            "status": "online",
            "total_certificates": total_certificates,
            "recent_certificates": [
                {
                    "certificate_id": cert.certificate_id,
                    "created_at": cert.created_at.isoformat(),
                    "wipe_method": getattr(cert, 'wipe_method', 'Unknown'),
                    "device_model": json.loads(getattr(cert, 'device_info', '{}')).get('model', 'Unknown')
                }
                for cert in recent_certificates
            ]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
