from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

def create_app():
    app = Flask(__name__)

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/certificates_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-here'

    # Initialize database
    from .models import db
    db.init_app(app)

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    from .routes import main
    app.register_blueprint(main)

    return app
