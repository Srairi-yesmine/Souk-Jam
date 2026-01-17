"""
Flask Application Configuration

This module defines configuration classes for different environments.
Configuration is loaded from environment variables with fallback defaults.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Base configuration class with default settings.

    Environment variables can override these defaults for different deployments.
    """

    # Flask application secret key for sessions and security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')

    # JWT secret key for token signing and verification
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')

    # Database connection string (SQLite for development, PostgreSQL for production)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')

    # Disable SQLAlchemy modification tracking for performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File upload configuration
    UPLOAD_FOLDER = 'uploads'                    # Directory for uploaded files
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024       # Maximum file size (50MB for high-quality images)

    # Flask environment setting
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # CORS configuration
    CORS_HEADERS = 'Content-Type'
    CORS_EXPOSE_HEADERS = ['Content-Type', 'Authorization']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
    CORS_ORIGINS = [
        'http://localhost:3000', 'http://localhost:3001', 'http://localhost:3002', 'http://localhost:3003',
        'http://127.0.0.1:3000', 'http://127.0.0.1:3001', 'http://127.0.0.1:3002', 'http://127.0.0.1:3003'
    ]