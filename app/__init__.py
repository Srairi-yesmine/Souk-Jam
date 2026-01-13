"""
Souk'Jam Flask Application Factory

This module creates and configures the main Flask application for the Souk'Jam platform,
which provides instrument rental and jam matching services for musicians in Tunisia.

Key Components:
- Flask-RESTX API for REST endpoints
- JWT authentication for user sessions
- SQLAlchemy ORM for database operations
- Flask-Migrate for database schema management
"""

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restx import Api
from flask_cors import CORS
from .config import Config
from .extensions import db, migrate, jwt, api
import os

def create_app(config_class=Config):
    """
    Application factory function that creates and configures the Flask app.

    Args:
        config_class: Configuration class to use (defaults to Config)

    Returns:
        Flask application instance with all extensions initialized
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS with wildcard - radical fix for all preflight issues
    CORS(app, 
         resources={r"/*": {
             "origins": app.config.get('CORS_ORIGINS', '*'),
             "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "expose_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "max_age": 3600
         }})
    
    # Add before_request handler to catch all OPTIONS requests
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = jsonify({"status": "ok"})
            response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
            response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, PATCH, OPTIONS")
            response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
            response.headers.add("Access-Control-Allow-Credentials", "true")
            response.headers.add("Access-Control-Max-Age", "3600")
            return response, 200

    # Initialize core Flask extensions
    db.init_app(app)          # SQLAlchemy database ORM
    migrate.init_app(app, db) # Database migration management
    jwt.init_app(app)         # JWT token authentication

    # Initialize REST API framework (after CORS)
    api.init_app(app)

    # Register API namespaces (endpoints)
    from .auth.routes import auth_ns
    from .routes.instruments import instruments_ns
    from .routes.jam import jam_ns
    from .routes.rental import rental_ns
    api.add_namespace(auth_ns, path='/auth')           # Authentication endpoints
    api.add_namespace(instruments_ns, path='/instruments') # Instrument management
    api.add_namespace(jam_ns, path='/jam')             # Jam matching features
    api.add_namespace(rental_ns, path='/rentals')      # Rental management

    # Serve static files (uploaded images) from the uploads folder
    uploads_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    os.makedirs(uploads_path, exist_ok=True)
    
    @app.route('/uploads/<path:filepath>')
    def serve_upload(filepath):
        """Serve uploaded files from the uploads directory"""
        from flask import send_file, abort
        file_path = os.path.join(uploads_path, filepath)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return send_file(file_path)
        abort(404)

    # Health check endpoint for monitoring
    @app.route('/health')
    def health():
        return {'status': 'ok'}

    return app