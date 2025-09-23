from flask import Blueprint, render_template, jsonify
from .models import CertificateVerification

blockchain_bp = Blueprint('blockchain', __name__)

@blockchain_bp.route('/blockchain')
def blockchain():
    """Display the certificate blockchain"""
    certificates = CertificateVerification.query.order_by(CertificateVerification.chain_index).all()
    return render_template('blockchain.html', certificates=certificates)

@blockchain_bp.route('/api/blockchain')
def get_blockchain():
    """API endpoint to get blockchain data"""
    certificates = CertificateVerification.query.order_by(CertificateVerification.chain_index).all()
    blockchain_data = []

    for cert in certificates:
        blockchain_data.append({
            'certificate_id': cert.certificate_id,
            'chain_index': cert.chain_index,
            'certificate_hash': cert.certificate_hash,
            'previous_hash': cert.previous_hash,
            'created_at': cert.created_at.isoformat(),
            'is_verified': cert.is_verified
        })

    return jsonify({
        'blockchain': blockchain_data,
        'total_certificates': len(blockchain_data),
        'chain_valid': all(cert.verify_chain_integrity() for cert in certificates)
    })

@blockchain_bp.route('/api/verify_chain/<certificate_id>')
def verify_chain(certificate_id):
    """API endpoint to verify a specific certificate's chain integrity"""
    certificate = CertificateVerification.query.filter_by(certificate_id=certificate_id).first()

    if not certificate:
        return jsonify({"error": "Certificate not found"}), 404

    chain_valid = certificate.verify_chain_integrity()

    return jsonify({
        'certificate_id': certificate.certificate_id,
        'chain_index': certificate.chain_index,
        'chain_valid': chain_valid,
        'previous_hash': certificate.previous_hash,
        'certificate_hash': certificate.certificate_hash
    })
