from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
import os

def create_app():
    app = Flask(__name__)

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:5680@localhost/certificates_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-here'

    # Initialize database
    from .models import db
    db.init_app(app)

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    # Add logging middleware to log all incoming requests
    @app.before_request
    def log_request_info():
        import logging
        logging.basicConfig(level=logging.INFO)
        logging.info(f"Incoming request: {request.method} {request.path}")

    # Register blueprints
    from .routes import main
    from .blockchain_routes import blockchain_bp
    from .devices_routes import devices_bp
    from .certificate_upload_routes import certificate_upload_bp
    from .certificate_routes import certificate_bp

    app.register_blueprint(main)
    app.register_blueprint(blockchain_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(certificate_upload_bp)
    app.register_blueprint(certificate_bp)

    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

    return app, socketio
