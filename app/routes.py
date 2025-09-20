from flask import Blueprint, render_template, jsonify, request, redirect, url_for, send_file, flash
from .mock_data import mock_drives_data
from .wiping_logic import simulate_wipe
from .certificate_generator import CertificateGenerator
from .models import CertificateVerification, db
import os
import uuid
import hashlib
from datetime import datetime

main = Blueprint('main', __name__)

# Global variable to track progress
progress_value = 0

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/features')
def features():
    return render_template('features.html')

@main.route('/workflow')
def workflow():
    return render_template('workflow.html')

@main.route('/certificates')
def certificates():
    return render_template('certificates.html')

@main.route('/compliance')
def compliance():
    return render_template('compliance.html')

@main.route('/documentation')
def documentation():
    return render_template('docs.html')

@main.route('/audit')
def audit():
    return render_template('audit.html')

@main.route('/impact')
def impact():
    return render_template('impact.html')

@main.route('/team')
def team():
    return render_template('team.html')

@main.route('/faq')
def faq():
    return render_template('FAQ.html')

@main.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main.route('/terms')
def terms():
    return render_template('terms.html')

@main.route('/contact')
def contact():
    return render_template('contact.html')

@main.route('/demo')
def demo():
    return render_template('demo.html')

# API Routes
@main.route('/api/progress')
def get_progress():
    global progress_value
    if progress_value < 100:
        progress_value += 5
        status = f"Wiping in progress... {progress_value}%"
    else:
        status = "✅ Wipe Completed Successfully"
    return jsonify({"progress": progress_value, "status": status})

@main.route('/api/drives')
def get_drives():
    return jsonify(mock_drives_data)

@main.route('/api/wipe/<drive_id>', methods=['POST'])
def wipe_drive(drive_id):
    drive = next((d for d in mock_drives_data if d['id'] == drive_id), None)
    if not drive:
        return jsonify({"error": "Drive not found"}), 404
    if not drive.get('is_wipeable', True):
        return jsonify({"error": "Drive not wipeable"}), 400
    
    # Simulate the wipe process
    simulate_wipe(drive_id, drive['type'], mock_drives_data)
    
    # Reset progress for next operation
    global progress_value
    progress_value = 0
    
    return jsonify({"message": "Wipe completed successfully", "drive_id": drive_id})

# Redirect routes for .html URLs to their proper route paths
@main.route('/index.html')
def index_html():
    return redirect(url_for('main.home'))

@main.route('/about.html')
def about_html():
    return redirect(url_for('main.about'))

@main.route('/features.html')
def features_html():
    return redirect(url_for('main.features'))

@main.route('/workflow.html')
def workflow_html():
    return redirect(url_for('main.workflow'))

@main.route('/certificates.html')
def certificates_html():
    return redirect(url_for('main.certificates'))

@main.route('/compliance.html')
def compliance_html():
    return redirect(url_for('main.compliance'))

@main.route('/documentation.html')
def documentation_html():
    return redirect(url_for('main.documentation'))

@main.route('/audit.html')
def audit_html():
    return redirect(url_for('main.audit'))

@main.route('/impact.html')
def impact_html():
    return redirect(url_for('main.impact'))

@main.route('/team.html')
def team_html():
    return redirect(url_for('main.team'))

@main.route('/faq.html')
def faq_html():
    return redirect(url_for('main.faq'))

@main.route('/privacy.html')
def privacy_html():
    return redirect(url_for('main.privacy'))

@main.route('/terms.html')
def terms_html():
    return redirect(url_for('main.terms'))

@main.route('/contact.html')
def contact_html():
    return redirect(url_for('main.contact'))

@main.route('/demo.html')
def demo_html():
    return redirect(url_for('main.demo'))

@main.route('/download_certificate/<drive_id>')
def download_certificate(drive_id):
    drive = next((d for d in mock_drives_data if d['id'] == drive_id), None)
    if not drive:
        return jsonify({"error": "Drive not found"}), 404

    # Generate a unique serial number for the certificate
    serial_number = str(uuid.uuid4())

    # Use a default wipe method or get from drive info if available
    wipe_method = drive.get('supported_methods', ['NIST Purge'])[0]

    cert_gen = CertificateGenerator()
    cert_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'certificates')
    cert_path = os.path.join(cert_dir, f"certificate_{serial_number}.pdf")

    # Ensure certificates directory exists
    os.makedirs(cert_dir, exist_ok=True)

    cert_gen.output_path = cert_path
    cert_path, random_text = cert_gen.generate_certificate(drive, wipe_method, serial_number)

    # Store verification data in database
    verification_key = CertificateVerification.hash_text(random_text)
    cert_verification = CertificateVerification(
        certificate_id=serial_number,
        verification_key=verification_key,
        random_text=random_text
    )

    try:
        db.session.add(cert_verification)
        db.session.commit()
    except Exception as e:
        # If database operation fails, still allow certificate download
        print(f"Database error: {e}")

    return send_file(cert_path, as_attachment=True, download_name=f"certificate_{serial_number}.pdf")

# Certificate Verification Routes
@main.route('/verify')
def verify():
    return render_template('verify.html')

@main.route('/verify_certificate', methods=['POST'])
def verify_certificate():
    verification_code = request.form.get('verification_code', '').strip()

    if not verification_code:
        flash('Please enter a verification code', 'error')
        return redirect(url_for('main.verify'))

    # Hash the entered code
    entered_hash = CertificateVerification.hash_text(verification_code)

    # Check if the hash exists in database
    certificate = CertificateVerification.query.filter_by(verification_key=entered_hash).first()

    if certificate:
        # Mark as verified
        certificate.is_verified = True
        certificate.verified_at = datetime.utcnow()
        db.session.commit()

        return render_template('verify.html',
                             verified=True,
                             certificate=certificate,
                             message="✅ Certificate Verified Successfully!")
    else:
        return render_template('verify.html',
                             verified=False,
                             message="❌ Invalid verification code. Certificate not found.")
