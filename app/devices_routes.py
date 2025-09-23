from flask import Blueprint, render_template, jsonify, request, abort
from .models import db
from datetime import datetime
import json

devices_bp = Blueprint('devices', __name__)

# Device Model (if not already defined in models.py)
class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(100), unique=True, nullable=False)
    device_type = db.Column(db.String(50), nullable=False)  # HDD, SSD, USB, etc.
    model = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    capacity = db.Column(db.String(50), nullable=True)
    manufacturer = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='active')  # active, wiped, inactive
    is_wipeable = db.Column(db.Boolean, default=True)
    supported_methods = db.Column(db.JSON, default=["NIST Purge", "DoD Wipe", "Zero Fill"])
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Wipe history relationship
    wipe_history = db.relationship('WipeHistory', backref='device', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'device_type': self.device_type,
            'model': self.model,
            'serial_number': self.serial_number,
            'capacity': self.capacity,
            'manufacturer': self.manufacturer,
            'status': self.status,
            'is_wipeable': self.is_wipeable,
            'supported_methods': self.supported_methods,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class WipeHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    wipe_method = db.Column(db.String(100), nullable=False)
    certificate_id = db.Column(db.String(100), nullable=True)
    wiped_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='completed')  # completed, failed, in_progress
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'wipe_method': self.wipe_method,
            'certificate_id': self.certificate_id,
            'wiped_at': self.wiped_at.isoformat(),
            'status': self.status
        }

# Device Management Routes
@devices_bp.route('/devices')
def devices():
    """Display devices management page"""
    return render_template('devices.html')

@devices_bp.route('/api/devices', methods=['GET'])
def get_devices():
    print("DEBUG: /api/devices GET route called")
    """Get all devices with optional filtering"""
    try:
        # Query parameters for filtering
        device_type = request.args.get('type')
        status = request.args.get('status')
        manufacturer = request.args.get('manufacturer')
        
        query = Device.query
        
        if device_type:
            query = query.filter_by(device_type=device_type)
        if status:
            query = query.filter_by(status=status)
        if manufacturer:
            query = query.filter(Device.manufacturer.ilike(f'%{manufacturer}%'))
        
        devices = query.order_by(Device.created_at.desc()).all()
        return jsonify({
            'success': True,
            'devices': [device.to_dict() for device in devices],
            'total': len(devices)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@devices_bp.route('/api/devices', methods=['POST'])
def create_device():
    """Create a new device"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['device_id', 'device_type', 'model', 'serial_number']):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Check if device_id or serial_number already exists
        existing_device = Device.query.filter(
            (Device.device_id == data['device_id']) | 
            (Device.serial_number == data['serial_number'])
        ).first()
        
        if existing_device:
            return jsonify({'success': False, 'error': 'Device ID or serial number already exists'}), 409
        
        device = Device(
            device_id=data['device_id'],
            device_type=data['device_type'],
            model=data['model'],
            serial_number=data['serial_number'],
            capacity=data.get('capacity'),
            manufacturer=data.get('manufacturer'),
            is_wipeable=data.get('is_wipeable', True),
            supported_methods=data.get('supported_methods', ["NIST Purge", "DoD Wipe", "Zero Fill"])
        )
        
        db.session.add(device)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Device created successfully',
            'device': device.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@devices_bp.route('/api/devices/<int:device_id>', methods=['GET'])
def get_device(device_id):
    """Get a specific device by ID"""
    try:
        device = Device.query.get_or_404(device_id)
        return jsonify({
            'success': True,
            'device': device.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': 'Device not found'}), 404

@devices_bp.route('/api/devices/<int:device_id>', methods=['PUT'])
def update_device(device_id):
    """Update a device"""
    try:
        device = Device.query.get_or_404(device_id)
        data = request.get_json()
        
        # Update allowed fields
        updatable_fields = ['model', 'capacity', 'manufacturer', 'status', 'is_wipeable', 'supported_methods']
        for field in updatable_fields:
            if field in data:
                setattr(device, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Device updated successfully',
            'device': device.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@devices_bp.route('/api/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    """Delete a device"""
    try:
        device = Device.query.get_or_404(device_id)
        
        # Check if device has wipe history
        if device.wipe_history:
            return jsonify({
                'success': False, 
                'error': 'Cannot delete device with wipe history. Deactivate instead.'
            }), 400
        
        db.session.delete(device)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Device deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@devices_bp.route('/api/devices/<int:device_id>/wipe-history', methods=['GET'])
def get_device_wipe_history(device_id):
    """Get wipe history for a specific device"""
    try:
        device = Device.query.get_or_404(device_id)
        history = WipeHistory.query.filter_by(device_id=device_id).order_by(WipeHistory.wiped_at.desc()).all()
        
        return jsonify({
            'success': True,
            'device_id': device_id,
            'history': [entry.to_dict() for entry in history],
            'total_wipes': len(history)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@devices_bp.route('/api/devices/<int:device_id>/status', methods=['PATCH'])
def update_device_status(device_id):
    """Update device status"""
    try:
        device = Device.query.get_or_404(device_id)
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({'success': False, 'error': 'Status field required'}), 400
        
        allowed_statuses = ['active', 'inactive', 'wiped', 'maintenance']
        if data['status'] not in allowed_statuses:
            return jsonify({'success': False, 'error': 'Invalid status'}), 400
        
        device.status = data['status']
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Device status updated to {data["status"]}',
            'device': device.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@devices_bp.route('/api/devices/statistics', methods=['GET'])
def get_device_statistics():
    """Get device statistics"""
    try:
        total_devices = Device.query.count()
        active_devices = Device.query.filter_by(status='active').count()
        wiped_devices = Device.query.filter_by(status='wiped').count()
        inactive_devices = Device.query.filter_by(status='inactive').count()
        
        # Device types breakdown
        device_types = db.session.query(
            Device.device_type, 
            db.func.count(Device.id).label('count')
        ).group_by(Device.device_type).all()
        
        # Recent wipe activity
        recent_wipes = WipeHistory.query.order_by(WipeHistory.wiped_at.desc()).limit(10).all()
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_devices': total_devices,
                'active_devices': active_devices,
                'wiped_devices': wiped_devices,
                'inactive_devices': inactive_devices,
                'device_types': {type_name: count for type_name, count in device_types},
                'recent_wipes': [wipe.to_dict() for wipe in recent_wipes]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
