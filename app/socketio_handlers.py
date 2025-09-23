from flask_socketio import SocketIO, emit, disconnect
from flask import request
from .models import CertificateVerification, db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def init_socketio_handlers(socketio):
    """Initialize SocketIO event handlers"""

    @socketio.on('connect')
    def handle_connect():
        client_ip = request.remote_addr
        logger.info(f"Client connected: {client_ip}")
        emit('status', {
            'message': 'Connected to Reboot-Reclaim server',
            'timestamp': datetime.now().isoformat()
        })

    @socketio.on('disconnect')
    def handle_disconnect():
        client_ip = request.remote_addr
        logger.info(f"Client disconnected: {client_ip}")

    @socketio.on('request_blockchain_status')
    def handle_blockchain_status():
        """Send current blockchain status to client"""
        try:
            certificates = CertificateVerification.query.order_by(CertificateVerification.chain_index).all()
            blockchain_data = []

            for cert in certificates:
                blockchain_data.append({
                    'certificate_id': cert.certificate_id,
                    'chain_index': cert.chain_index,
                    'certificate_hash': cert.certificate_hash,
                    'previous_hash': cert.previous_hash,
                    'created_at': cert.created_at.isoformat(),
                    'is_verified': cert.is_verified,
                    'verified_at': cert.verified_at.isoformat() if cert.verified_at else None
                })

            emit('blockchain_status', {
                'blockchain': blockchain_data,
                'total_certificates': len(blockchain_data),
                'chain_valid': all(cert.verify_chain_integrity() for cert in certificates),
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error getting blockchain status: {e}")
            emit('error', {'message': 'Failed to retrieve blockchain status'})

    @socketio.on('request_certificate_verification')
    def handle_certificate_verification(data):
        """Verify a certificate via WebSocket"""
        try:
            certificate_id = data.get('certificate_id')
            if not certificate_id:
                emit('error', {'message': 'Certificate ID is required'})
                return

            certificate = CertificateVerification.query.filter_by(certificate_id=certificate_id).first()

            if not certificate:
                emit('verification_result', {
                    'certificate_id': certificate_id,
                    'verified': False,
                    'message': 'Certificate not found',
                    'timestamp': datetime.now().isoformat()
                })
                return

            # Verify blockchain integrity
            chain_valid = certificate.verify_chain_integrity()

            # Mark as verified if not already
            if not certificate.is_verified:
                certificate.is_verified = True
                certificate.verified_at = datetime.utcnow()
                db.session.commit()

            emit('verification_result', {
                'certificate_id': certificate.certificate_id,
                'verified': True,
                'chain_valid': chain_valid,
                'chain_index': certificate.chain_index,
                'created_at': certificate.created_at.isoformat(),
                'verified_at': certificate.verified_at.isoformat(),
                'message': 'Certificate verified successfully' if chain_valid else 'Certificate verified but blockchain integrity compromised',
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Error verifying certificate: {e}")
            emit('error', {'message': 'Failed to verify certificate'})

    @socketio.on('request_device_status')
    def handle_device_status():
        """Send device status updates"""
        try:
            # This would integrate with your device management system
            # For now, sending mock data
            emit('device_status', {
                'devices': [
                    {
                        'id': 'HDD001',
                        'model': 'Seagate Barracuda 2TB',
                        'status': 'ready',
                        'capacity': '2TB',
                        'is_wipeable': True
                    },
                    {
                        'id': 'SSD001',
                        'model': 'Samsung 970 EVO 1TB',
                        'status': 'ready',
                        'capacity': '1TB',
                        'is_wipeable': True
                    }
                ],
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error getting device status: {e}")
            emit('error', {'message': 'Failed to retrieve device status'})

    @socketio.on('start_wipe_process')
    def handle_start_wipe(data):
        """Handle wipe process initiation"""
        try:
            device_id = data.get('device_id')
            wipe_method = data.get('wipe_method', 'Standard Wipe')

            if not device_id:
                emit('error', {'message': 'Device ID is required'})
                return

            # Emit progress updates
            for progress in range(0, 101, 10):
                emit('wipe_progress', {
                    'device_id': device_id,
                    'progress': progress,
                    'message': f'Wiping device... {progress}%',
                    'timestamp': datetime.now().isoformat()
                })

                # Simulate time delay
                socketio.sleep(0.5)

            # Emit completion
            emit('wipe_complete', {
                'device_id': device_id,
                'message': 'Device wipe completed successfully',
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Error during wipe process: {e}")
            emit('error', {'message': 'Failed to complete wipe process'})

    @socketio.on('ping')
    def handle_ping():
        """Respond to ping with pong"""
        emit('pong', {
            'timestamp': datetime.now().isoformat()
        })

    @socketio.on_error()
    def error_handler(e):
        """Handle SocketIO errors"""
        logger.error(f'SocketIO error: {e}')
        emit('error', {
            'message': 'An internal error occurred',
            'timestamp': datetime.now().isoformat()
        })
