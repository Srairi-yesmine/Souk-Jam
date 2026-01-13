"""
Authentication Routes for Souk'Jam

This module handles user authentication and registration operations.
It provides secure user registration with password validation, JWT-based
login, and user management endpoints.

Features:
- User registration with strong password requirements
- JWT token-based authentication
- Location geocoding during registration
- User profile management
- Secure password hashing and verification

Security Features:
- Password strength validation (8+ chars, mixed case, numbers, special chars)
- Email uniqueness checking
- JWT token generation for authenticated sessions
- Protected endpoints requiring authentication
"""

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask import request
from werkzeug.utils import secure_filename
from ..models import User
from ..schemas import UserSchema
from ..extensions import db
from ..services.geocoding import geocode_location
from ..services.storage import save_photo
import re

def validate_password(password):
    """
    Validate password strength requirements.

    Password must contain:
    - At least 8 characters
    - One uppercase letter
    - One lowercase letter
    - One number
    - One special character

    Args:
        password (str): Password to validate

    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, "Password is valid"

auth_ns = Namespace('auth', description='Authentication operations')

# Define Swagger models for API documentation
user_model = auth_ns.model('User', {
    'id': fields.Integer(description='User ID'),
    'email': fields.String(description='User email', example='user@example.com'),
    'name': fields.String(description='User name', example='John Doe'),
    'location_name': fields.String(description='Location name', example='Paris, France'),
    'location_lat': fields.Float(description='Latitude', dump_only=True),
    'location_lng': fields.Float(description='Longitude', dump_only=True),
    'profile_photo_url': fields.String(description='Profile photo URL'),
    'role': fields.String(description='User role', example='jammer'),
    'genres_enjoyed': fields.List(fields.String, description='Genres enjoyed', example=['rock', 'jazz']),
    'instruments_played': fields.List(fields.Raw, description='Instruments played', example=[{'instrument_type': 'guitar', 'skill_level': 'intermediate'}]),
    'instruments_owned': fields.List(fields.String, description='Instruments owned', example=['guitar', 'drums']),
    'is_active_for_jam': fields.Boolean(description='Active for jam', example=False)
})

register_model = auth_ns.model('Register', {
    'email': fields.String(required=True, description='User email', example='user@example.com'),
    'password': fields.String(required=True, description='Password', example='securepassword'),
    'name': fields.String(required=True, description='User name', example='John Doe'),
    'location_name': fields.String(description='Location name', example='Paris, France'),
    'role': fields.String(description='User role', example='jammer'),
    'genres_enjoyed': fields.List(fields.String, description='Genres enjoyed', example=['rock', 'jazz']),
    'instruments_played': fields.List(fields.Raw, description='Instruments played', example=[{'instrument_type': 'guitar', 'skill_level': 'intermediate'}]),
    'instruments_owned': fields.List(fields.String, description='Instruments owned', example=['guitar', 'drums']),
    'is_active_for_jam': fields.Boolean(description='Active for jam', example=False)
})

login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, description='User email', example='user@example.com'),
    'password': fields.String(required=True, description='Password', example='securepassword')
})

token_model = auth_ns.model('Token', {
    'access_token': fields.String(description='JWT access token'),
    'id': fields.Integer(description='User ID')
})

change_password_model = auth_ns.model('ChangePassword', {
    'old_password': fields.String(required=True, description='Current password'),
    'new_password': fields.String(required=True, description='New password')
})

email_check_model = auth_ns.model('EmailCheck', {
    'email': fields.String(required=True, description='Email to check')
})

user_schema = UserSchema()

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_model)
    @auth_ns.marshal_with(user_model, code=201, description='User registered successfully')
    @auth_ns.response(400, 'Email already registered, invalid location, or weak password')
    def post(self):
        """
        Register a new user account.

        This endpoint creates a new user account with validation for:
        - Unique email address
        - Strong password requirements
        - Valid location (geocoded to coordinates)
        - Optional musical preferences and instruments
        """
        data = request.get_json()

        # Check for existing email
        if User.query.filter_by(email=data['email']).first():
            auth_ns.abort(400, 'Email already registered')

        # Validate password strength
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            auth_ns.abort(400, message)

        # Geocode location if provided
        location_name = data.get('location_name')
        lat, lng = None, None
        if location_name:
            lat, lng = geocode_location(location_name)
            if lat is None or lng is None:
                auth_ns.abort(400, 'Invalid location name')

        # Create new user
        user = User(email=data['email'], name=data['name'],
                    location_name=location_name,
                    location_lat=lat, location_lng=lng,
                    role=data.get('role', 'jammer'),
                    genres_enjoyed=data.get('genres_enjoyed', []),
                    instruments_played=data.get('instruments_played', []),
                    instruments_owned=data.get('instruments_owned', []),
                    is_active_for_jam=data.get('is_active_for_jam', False))
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return user, 201

@auth_ns.route('/users')
class UserList(Resource):
    @jwt_required()
    @auth_ns.marshal_with(user_model, as_list=True, description='List of users')
    @auth_ns.response(401, 'Unauthorized')
    def get(self):
        """
        Get all users (requires authentication).

        Note: Currently allows any authenticated user to view all users.
        In production, consider adding admin role restrictions.
        """
        users = User.query.all()
        return users

@auth_ns.route('/users/<int:user_id>')
class UserDetail(Resource):
    @jwt_required()
    @auth_ns.marshal_with(user_model, description='User details')
    @auth_ns.response(404, 'User not found')
    def get(self, user_id):
        """Get detailed information for a specific user by ID."""
        user = User.query.get_or_404(user_id)
        return user

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.marshal_with(token_model, description='Login successful')
    @auth_ns.response(401, 'Invalid credentials')
    def post(self):
        """
        Authenticate user and return JWT access token.

        Validates email/password combination and returns a JWT token
        for authenticated API access.
        """
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        if not user or not user.check_password(data['password']):
            auth_ns.abort(401, 'Invalid credentials')
        access_token = create_access_token(identity=str(user.id))
        return {'access_token': access_token, 'id': user.id}, 200

@auth_ns.route('/users/<int:user_id>/profile-photo')
class UserProfilePhoto(Resource):
    @jwt_required()
    @auth_ns.marshal_with(user_model, description='User with updated profile photo')
    @auth_ns.response(401, 'Unauthorized')
    @auth_ns.response(404, 'User not found')
    @auth_ns.response(400, 'Invalid file type or no file provided')
    def put(self, user_id):
        """Upload or update user profile photo.
        
        Accepts multipart form data with 'profile_photo' file field.
        Only the user can update their own profile photo.
        Supported formats: PNG, JPG, JPEG, GIF
        """
        current_user_id = int(get_jwt_identity())
        
        # User can only update their own profile photo
        if current_user_id != user_id:
            auth_ns.abort(401, 'You can only update your own profile photo')
        
        user = User.query.get_or_404(user_id)
        
        # Check if file is in request
        if 'profile_photo' not in request.files:
            auth_ns.abort(400, 'No file provided. Use "profile_photo" field in form data')
        
        file = request.files['profile_photo']
        
        if file.filename == '':
            auth_ns.abort(400, 'No file selected')
        
        # Save the photo
        photo_url = save_photo(file)
        if not photo_url:
            auth_ns.abort(400, 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF')
        
        # Update user profile photo
        user.profile_photo_url = photo_url
        db.session.commit()
        
        return user, 200

@auth_ns.route('/users/<int:user_id>/change-password')
class ChangePassword(Resource):
    @jwt_required()
    @auth_ns.expect(change_password_model)
    @auth_ns.response(200, 'Password changed successfully')
    @auth_ns.response(401, 'Unauthorized or incorrect current password')
    @auth_ns.response(400, 'Invalid new password')
    @auth_ns.response(404, 'User not found')
    def post(self, user_id):
        """Change user password.
        
        User can only change their own password.
        New password must meet strength requirements.
        """
        current_user_id = int(get_jwt_identity())
        
        # User can only change their own password
        if current_user_id != user_id:
            auth_ns.abort(401, 'You can only change your own password')
        
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Verify old password
        if not user.check_password(data.get('old_password')):
            auth_ns.abort(401, 'Incorrect current password')
        
        # Validate new password strength
        is_valid, message = validate_password(data.get('new_password'))
        if not is_valid:
            auth_ns.abort(400, message)
        
        # Update password
        user.set_password(data['new_password'])
        db.session.commit()
        
        return {'message': 'Password changed successfully'}, 200

@auth_ns.route('/check-email')
class CheckEmail(Resource):
    @auth_ns.expect(email_check_model)
    @auth_ns.response(200, 'Email check result')
    def post(self):
        """Check if email exists in the system.
        
        Returns whether an email is already registered.
        Useful for registration form validation.
        """
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            auth_ns.abort(400, 'Email is required')
        
        exists = User.query.filter_by(email=email).first() is not None
        
        return {'email': email, 'exists': exists}, 200