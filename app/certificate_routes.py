from flask import Blueprint, send_from_directory, jsonify
import os

certificate_bp = Blueprint('certificate_bp', __name__)

@certificate_bp.route('/certificates/<filename>')
def download_certificate(filename):
    certificate_directory = os.path.join(os.getcwd(), 'app', 'certificates')
    return send_from_directory(certificate_directory, filename, as_attachment=True)

@certificate_bp.route('/api/certificates')
def list_certificates():
    """List all available certificates"""
    certificate_directory = os.path.join(os.getcwd(), 'app', 'certificates')
    try:
        files = os.listdir(certificate_directory)
        certificates = []
        for file in files:
            if file.endswith('.pdf'):
                file_path = os.path.join(certificate_directory, file)
                file_stats = os.stat(file_path)
                certificates.append({
                    'filename': file,
                    'size': file_stats.st_size,
                    'created': file_stats.st_ctime,
                    'modified': file_stats.st_mtime
                })
        return jsonify(certificates)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
