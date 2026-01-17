"""
Instrument Routes for Souk'Jam

This module handles all instrument-related operations including:
- Creating instrument listings (owners only)
- Searching and filtering instruments by location, type, price, etc.
- Sorting by distance, price, newest, or location
- Managing instrument details (CRUD operations)

Key Features:
- Location-based search with radius filtering
- Multiple sorting options (distance, price, date, location)
- Owner authorization for instrument management
- Photo upload support for instrument listings
- Geocoding integration for location handling

Security:
- JWT authentication required for all operations
- Owner-only permissions for create/update/delete
- Input validation and sanitization
"""

from flask_restx import Namespace, Resource, fields, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify, Blueprint
from werkzeug.utils import secure_filename
import os
import json
import traceback
from ..models import Instrument, User
from ..schemas import InstrumentSchema, SearchInstrumentSchema
from ..extensions import db
from ..services.storage import save_photo
from ..services.geocoding import geocode_location
from math import radians, sin, cos, sqrt, atan2

def calculate_distance(lat1, lng1, lat2, lng2):
    """
    Calculate the great circle distance between two points using the Haversine formula.

    Args:
        lat1, lng1: Coordinates of first point (degrees)
        lat2, lng2: Coordinates of second point (degrees)

    Returns:
        float: Distance in kilometers
    """
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def search_instruments(search_params):
    """
    Search and filter instruments based on various criteria.

    This function builds a dynamic SQL query based on search parameters
    and applies sorting. It handles location-based filtering, price ranges,
    instrument types, and multiple sorting options.

    Args:
        search_params (dict): Search parameters including filters and sorting

    Returns:
        list: List of instrument dictionaries with owner information
    """
    query = Instrument.query.join(User, Instrument.owner_id == User.id)

    # Location-based filtering
    location_param = search_params.get('location_name') or search_params.get('location')
    if location_param:
        lat, lng = geocode_location(location_param)
        if lat is not None and lng is not None:
            radius = search_params.get('radius_km', 50)  # Default 50km radius
            # For simplicity, we'll use a bounding box approximation
            # In production, you'd want proper geospatial queries
            query = query.filter(
                Instrument.location_lat.between(lat - radius/111, lat + radius/111),
                Instrument.location_lng.between(lng - radius/(111*cos(radians(lat))), lng + radius/(111*cos(radians(lat))))
            )

    # Owner filter
    if search_params.get('owner_id'):
        query = query.filter(Instrument.owner_id == search_params['owner_id'])

    # Type filter
    if search_params.get('type'):
        query = query.filter(Instrument.type.ilike(f"%{search_params['type']}%"))

    # Price filters
    if search_params.get('price_min'):
        query = query.filter(Instrument.price_per_day >= search_params['price_min'])
    if search_params.get('price_max'):
        query = query.filter(Instrument.price_per_day <= search_params['price_max'])

    # Status filter
    if search_params.get('status'):
        query = query.filter(Instrument.status == search_params['status'])
    else:
        # Default to available instruments only
        query = query.filter(Instrument.status == 'available')

    # Apply sorting BEFORE limit
    sort_by = search_params.get('sort_by') or search_params.get('sort') or 'distance'
    sort_order = search_params.get('sort_order') or search_params.get('order') or 'asc'

    # Apply database-level sorting for all non-distance sorts
    if sort_by in ['price', 'price_per_day']:
        query = query.order_by(Instrument.price_per_day.desc() if sort_order == 'desc' else Instrument.price_per_day.asc())
    elif sort_by == 'newest':
        query = query.order_by(Instrument.created_at.desc() if sort_order == 'desc' else Instrument.created_at.asc())
    elif sort_by == 'location':
        query = query.order_by(Instrument.location_name.desc() if sort_order == 'desc' else Instrument.location_name.asc())
    elif sort_by == 'owner':
        query = query.order_by(User.name.desc() if sort_order == 'desc' else User.name.asc())
    elif sort_by == 'owner_id':
        query = query.order_by(Instrument.owner_id.desc() if sort_order == 'desc' else Instrument.owner_id.asc())
    else:
        # Default to ID ordering for distance or other cases
        query = query.order_by(Instrument.id.asc())

    # Limit results AFTER ordering
    limit = min(search_params.get('limit', 20), 100)  # Max 100 results
    query = query.limit(limit)

    instruments = query.all()

    # Post-processing sort for distance (Python-level sorting)
    if sort_by == 'distance':
        if search_params.get('user_lat') and search_params.get('user_lng'):
            instruments.sort(key=lambda inst: calculate_distance(
                search_params['user_lat'], search_params['user_lng'],
                inst.location_lat or 0, inst.location_lng or 0
            ), reverse=(sort_order == 'desc'))
        else:
            # If no user location, sort by location name as fallback
            instruments.sort(key=lambda inst: inst.location_name or '', reverse=(sort_order == 'desc'))

    # Format results with owner name
    results = []
    for instrument in instruments:
        owner = User.query.get(instrument.owner_id)
        results.append({
            'id': instrument.id,
            'owner_id': instrument.owner_id,
            'owner_name': owner.name if owner else 'Unknown',
            'name': instrument.name,
            'brand': instrument.brand,
            'type': instrument.type,
            'description': instrument.description,
            'status': instrument.status,
            'price_per_day': instrument.price_per_day,
            'photo_url': instrument.photo_url,
            'location_name': instrument.location_name,
            'location_lat': instrument.location_lat,
            'location_lng': instrument.location_lng
        })

    return results
instruments_ns = Namespace('instruments', description='Instrument operations')

# Define Swagger models
instrument_model = instruments_ns.model('Instrument', {
    'id': fields.Integer(description='Instrument ID'),
    'owner_id': fields.Integer(description='Owner user ID'),
    'owner_name': fields.String(description='Owner name'),
    'name': fields.String(description='Instrument name', example='Fender Stratocaster'),
    'brand': fields.String(description='Instrument brand', example='Fender'),
    'type': fields.String(description='Instrument type', example='guitar'),
    'description': fields.String(description='Description', example='Electric guitar in good condition'),
    'status': fields.String(description='Availability status', example='available'),
    'price_per_day': fields.Float(description='Price per day', example=25.0),
    'photo_url': fields.String(description='Photo URL'),
    'location_name': fields.String(description='Location name', example='Paris, France'),
    'location_lat': fields.Float(description='Latitude', dump_only=True),
    'location_lng': fields.Float(description='Longitude', dump_only=True)
})

instrument_create_model = instruments_ns.model('InstrumentCreate', {
    'name': fields.String(required=True, description='Instrument name', example='Fender Stratocaster'),
    'brand': fields.String(description='Instrument brand', example='Fender'),
    'type': fields.String(required=True, description='Instrument type', example='guitar'),
    'description': fields.String(description='Description', example='Electric guitar in good condition'),
    'price_per_day': fields.Float(required=True, description='Price per day', example=25.0),
    'location_name': fields.String(required=True, description='Location name', example='Paris, France')
})

# Parser for search query parameters
search_parser = reqparse.RequestParser()
search_parser.add_argument('location', type=str, help='Search location name')
search_parser.add_argument('location_name', type=str, help='Search location name')
search_parser.add_argument('radius_km', type=float, help='Search radius in km')
search_parser.add_argument('type', type=str, help='Instrument type filter')
search_parser.add_argument('price_min', type=float, help='Minimum price')
search_parser.add_argument('price_max', type=float, help='Maximum price')
search_parser.add_argument('status', type=str, choices=['available', 'rented', 'unavailable'], help='Status filter')
search_parser.add_argument('owner_id', type=int, help='Filter by owner ID')
search_parser.add_argument('limit', type=int, default=20, help='Result limit')
search_parser.add_argument('sort_by', type=str, choices=['distance', 'price', 'price_per_day', 'newest', 'location', 'owner', 'owner_id'], default='distance', help='Sort criteria')
search_parser.add_argument('sort_order', type=str, choices=['asc', 'desc'], default='asc', help='Sort order')

instrument_schema = InstrumentSchema()
instruments_schema = InstrumentSchema(many=True)
search_schema = SearchInstrumentSchema()

@instruments_ns.route('/')
class InstrumentList(Resource):
    @jwt_required()
    @instruments_ns.expect(instrument_create_model)
    @instruments_ns.marshal_with(instrument_model, code=201, description='Instrument created successfully')
    @instruments_ns.response(401, 'Unauthorized')
    @instruments_ns.response(400, 'Invalid location')
    def post(self):
        """Create a new instrument listing"""
        user_id = int(get_jwt_identity())
        user = User.query.get_or_404(user_id)
        
        data = request.form.to_dict()
        photo = request.files.get('photo')
        photo_url = None
        
        if photo:
            photo_url = save_photo(photo)
        
        # Geocode location
        location_name = data.get('location_name')
        if not location_name:
            instruments_ns.abort(400, 'Location name is required')
        
        lat, lng = geocode_location(location_name)
        if lat is None or lng is None:
            instruments_ns.abort(400, 'Invalid location name')
        
        instrument = Instrument(
            owner_id=user_id,
            name=data['name'],
            brand=data.get('brand'),
            type=data['type'],
            description=data.get('description'),
            price_per_day=float(data['price_per_day']),
            photo_url=photo_url,
            location_name=location_name,
            location_lat=lat,
            location_lng=lng,
            tags=data.get('tags', [])
        )
        db.session.add(instrument)
        db.session.commit()
        
        # Return instrument with owner_name included
        result = {
            'id': instrument.id,
            'owner_id': instrument.owner_id,
            'owner_name': user.name,
            'name': instrument.name,
            'brand': instrument.brand,
            'type': instrument.type,
            'description': instrument.description,
            'status': instrument.status,
            'price_per_day': instrument.price_per_day,
            'photo_url': instrument.photo_url,
            'location_name': instrument.location_name,
            'location_lat': instrument.location_lat,
            'location_lng': instrument.location_lng
        }
        return result, 201

    @jwt_required()
    @instruments_ns.doc(params={
        'location': {'type': 'string', 'description': 'Search location name'},
        'location_name': {'type': 'string', 'description': 'Search location name'},
        'radius_km': {'type': 'float', 'description': 'Search radius in km'},
        'type': {'type': 'string', 'description': 'Instrument type filter'},
        'price_min': {'type': 'float', 'description': 'Minimum price'},
        'price_max': {'type': 'float', 'description': 'Maximum price'},
        'status': {'type': 'string', 'description': 'Status filter'},
        'owner_id': {'type': 'integer', 'description': 'Filter by owner ID'},
        'limit': {'type': 'integer', 'default': 20, 'description': 'Result limit'},
        'sort_by': {'type': 'string', 'enum': ['distance', 'price', 'price_per_day', 'newest', 'location', 'owner'], 'default': 'distance', 'description': 'Sort criteria'},
        'sort_order': {'type': 'string', 'enum': ['asc', 'desc'], 'default': 'asc', 'description': 'Sort order'}
    })
    @instruments_ns.marshal_with(instrument_model, as_list=True, description='List of instruments')
    @instruments_ns.response(401, 'Unauthorized')
    def get(self):
        """Search and list available instruments"""
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        # Parse query parameters (args is already a dict-like ParseResult object)
        args = search_parser.parse_args()

        # Convert to dict and remove None values
        data = {k: v for k, v in args.items() if v is not None}
        
        if not data.get('location_name') and user and user.location_lat and user.location_lng:
            # Use user's location for sorting
            data['user_lat'] = user.location_lat
            data['user_lng'] = user.location_lng

        results = search_instruments(data)
        return results

# Create blueprints for endpoints that need to handle FormData (to bypass RESTX validation)
instruments_bp = Blueprint('instruments_bp', __name__, url_prefix='/instruments')

# GET and DELETE via blueprint to avoid RESTX interference
@instruments_bp.route('/<int:id>', methods=['GET'])
@jwt_required(optional=True)
def get_instrument(id):
    """Get instrument details by ID"""
    try:
        instrument = Instrument.query.get_or_404(id)
        owner = User.query.get(instrument.owner_id)
        
        result = {
            'id': instrument.id,
            'owner_id': instrument.owner_id,
            'owner_name': owner.name if owner else 'Unknown',
            'name': instrument.name,
            'brand': instrument.brand,
            'type': instrument.type,
            'description': instrument.description,
            'status': instrument.status,
            'price_per_day': float(instrument.price_per_day) if instrument.price_per_day else 0,
            'photo_url': instrument.photo_url or '',
            'location_name': instrument.location_name or '',
            'location_lat': float(instrument.location_lat) if instrument.location_lat else None,
            'location_lng': float(instrument.location_lng) if instrument.location_lng else None
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@instruments_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_instrument(id):
    """Delete instrument (owner only) - only if no pending/confirmed rentals"""
    try:
        user_id = int(get_jwt_identity())
        instrument = Instrument.query.get_or_404(id)
        if instrument.owner_id != user_id:
            return jsonify({'message': 'Not authorized'}), 403
        
        # Check for active rentals
        from ..models import Rental
        active_rentals = Rental.query.filter(
            Rental.instrument_id == id,
            Rental.status.in_(['pending', 'confirmed'])
        ).count()
        
        if active_rentals > 0:
            return jsonify({'message': 'Cannot delete instrument with active or pending rentals'}), 400
        
        # Delete all rentals for this instrument at DB level to avoid any
        # ORM-side nullification/UPDATE that can trigger NOT NULL errors.
        # Use bulk delete with synchronize_session=False to run a direct SQL DELETE.
        Rental.query.filter(Rental.instrument_id == id).delete(synchronize_session=False)

        # Now delete the instrument
        db.session.delete(instrument)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'message': str(e)}), 500

@instruments_bp.route('/<int:id>', methods=['PUT'])
@jwt_required(optional=True)
def update_instrument(id):
    """Update instrument details (owner only) - handles FormData and JSON"""
    try:
        user_id = int(get_jwt_identity())
        instrument = Instrument.query.get_or_404(id)
        
        if instrument.owner_id != user_id:
            return jsonify({'message': 'Not authorized'}), 403
        
        # Handle both JSON and FormData requests
        try:
            if request.is_json:
                data = request.get_json() or {}
            else:
                data = request.form.to_dict() or {}
        except Exception as e:
            return jsonify({'message': f'Failed to parse request data: {str(e)}'}), 400
        
        # Update simple fields - be defensive about empty values
        updatable_fields = {
            'name': str,
            'brand': str,
            'type': str,
            'description': str,
            'price_per_day': float,
            'location_name': str,
            'status': str
        }
        
        for key, value_type in updatable_fields.items():
            if key in data:
                val = data.get(key)
                # Skip if None, empty string, or False
                if val is not None and str(val).strip() != '':
                    try:
                        if value_type == float:
                            converted_val = float(val)
                            setattr(instrument, key, converted_val)
                        else:
                            setattr(instrument, key, str(val).strip())
                    except (ValueError, TypeError) as e:
                        print(f"Error setting {key}: {e}")
                        continue
        
        # Handle photo update if provided
        try:
            photo = request.files.get('photo')
            if photo and photo.filename and photo.filename != '':
                photo_url = save_photo(photo)
                if photo_url:
                    instrument.photo_url = photo_url
        except Exception as e:
            print(f"Photo upload error: {e}")
            # Don't fail the whole request if photo upload fails
        
        # Handle tags if provided
        try:
            if 'tags' in data and data['tags']:
                if isinstance(data['tags'], str):
                    instrument.tags = json.loads(data['tags'])
                else:
                    instrument.tags = data['tags']
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Tags parsing error: {e}")
            pass  # Keep existing tags if parsing fails
        
        # Commit changes
        db.session.commit()
        
        # Get owner name for response
        owner = User.query.get(instrument.owner_id)
        
        # Prepare response data - ensure all fields are serializable
        try:
            price = float(instrument.price_per_day) if instrument.price_per_day else 0.0
        except (ValueError, TypeError):
            price = 0.0
        
        try:
            lat = float(instrument.location_lat) if instrument.location_lat else 0.0
        except (ValueError, TypeError):
            lat = 0.0
        
        try:
            lng = float(instrument.location_lng) if instrument.location_lng else 0.0
        except (ValueError, TypeError):
            lng = 0.0
        
        result = {
            'id': instrument.id,
            'owner_id': instrument.owner_id,
            'owner_name': owner.name if owner else 'Unknown',
            'name': instrument.name or '',
            'brand': instrument.brand or '',
            'type': instrument.type or '',
            'description': instrument.description or '',
            'status': instrument.status or 'available',
            'price_per_day': price,
            'photo_url': instrument.photo_url or '',
            'location_name': instrument.location_name or '',
            'location_lat': lat,
            'location_lng': lng
        }
        return jsonify(result), 200
    except Exception as e:
        print(f"Update instrument error: {e}")
        traceback.print_exc()
        return jsonify({'message': f'Server error: {str(e)}'}), 500