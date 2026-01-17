"""
File Storage Service for Souk'Jam

This module handles secure file uploads and storage for instrument photos.
It provides validation, unique filename generation, and safe file handling
to prevent security vulnerabilities.

Features:
- File type validation (images only)
- Secure filename sanitization
- Unique filename generation to prevent conflicts
- Organized upload directory structure
"""

import os
from werkzeug.utils import secure_filename
from flask import current_app
import uuid

# Allowed file extensions for security (images only)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """
    Check if a file has an allowed extension.

    Args:
        filename (str): Original filename from upload

    Returns:
        bool: True if file extension is allowed, False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_photo(file):
    """
    Save an uploaded photo file with security measures.

    This function validates the file, generates a unique filename to prevent
    conflicts and security issues, and saves it to the upload directory.

    Args:
        file: Flask file object from request.files

    Returns:
        str: Filename (not full path) for database storage, or None if save fails
    """
    if file and allowed_file(file.filename):
        # Sanitize original filename to prevent path traversal attacks
        filename = secure_filename(file.filename)

        # Generate unique filename using UUID to prevent conflicts
        unique_filename = f"{uuid.uuid4()}_{filename}"

        # Create full filepath in upload directory
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)

        # Save the file
        file.save(filepath)

        # Return just the filename for storage in database
        # The /uploads/ prefix is added by the frontend when displaying
        return unique_filename

    return None