"""
Flask Extension Instances

This module creates global instances of Flask extensions that are initialized
in the application factory function. These instances are imported and used
throughout the application.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_restx import Api

# Database ORM extension for SQLAlchemy models and queries
db = SQLAlchemy()

# Database migration management extension
migrate = Migrate()

# JWT token management for authentication
jwt = JWTManager()

# REST API framework with automatic Swagger documentation
api = Api(
    title='Souk\'Jam - Musical Instrument Rental API',
    version='1.0',
    description='API for renting musical instruments and matching musicians for jam sessions in Tunisia',
    doc='/docs'  # Swagger UI documentation endpoint
)