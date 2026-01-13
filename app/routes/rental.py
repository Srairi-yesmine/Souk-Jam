"""
Rental Routes for Souk'Jam

This module handles rental operations including:
- Creating rental requests with comments
- Price negotiation (counter-offers like Uber/Bolt)
- Owner responses (accept/reject/counter-offer)
- Rental history and management
"""

from flask_restx import Namespace, Resource, fields, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from ..models import Rental, Instrument, User
from ..extensions import db
from datetime import datetime

rental_ns = Namespace('rentals', description='Rental operations')

# Swagger models
rental_model = rental_ns.model('Rental', {
    'id': fields.Integer(description='Rental ID'),
    'instrument_id': fields.Integer(description='Instrument ID'),
    'renter_id': fields.Integer(description='Renter user ID'),
    'owner_id': fields.Integer(description='Instrument owner user ID'),
    'renter_name': fields.String(description='Renter name'),
    'instrument_name': fields.String(description='Instrument name'),
    'start_date': fields.Date(description='Start date'),
    'end_date': fields.Date(description='End date'),
    'total_price': fields.Float(description='Original requested price'),
    'negotiated_price': fields.Float(description='Owner counter-offer price'),
    'status': fields.String(description='Rental status'),
    'owner_response': fields.String(description='Owner response status'),
    'comment': fields.String(description='Renter comment'),
    'created_at': fields.DateTime(description='Created at'),
    'updated_at': fields.DateTime(description='Updated at')
})

rental_create_model = rental_ns.model('CreateRental', {
    'instrument_id': fields.Integer(required=True, description='Instrument ID'),
    'start_date': fields.Date(required=True, description='Start date (YYYY-MM-DD)'),
    'end_date': fields.Date(required=True, description='End date (YYYY-MM-DD)'),
    'comment': fields.String(description='Optional comment')
})

rental_counter_offer_model = rental_ns.model('CounterOffer', {
    'negotiated_price': fields.Float(required=True, description='Counter-offer price')
})

rental_response_model = rental_ns.model('RentalResponse', {
    'status': fields.String(required=True, enum=['accepted', 'rejected'], description='Accept or reject')
})

# Request parsers
rental_filter_parser = reqparse.RequestParser()
rental_filter_parser.add_argument('status', type=str, help='Filter by status')
rental_filter_parser.add_argument('owner_response', type=str, help='Filter by owner response')
rental_filter_parser.add_argument('limit', type=int, default=20, help='Result limit')


@rental_ns.route('/')
class RentalList(Resource):
    @jwt_required()
    @rental_ns.expect(rental_create_model)
    @rental_ns.marshal_with(rental_model, code=201, description='Rental request created')
    @rental_ns.response(400, 'Invalid input')
    @rental_ns.response(404, 'Instrument not found')
    def post(self):
        """Create a new rental request with optional comment"""
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validate instrument exists
        instrument = Instrument.query.get_or_404(data['instrument_id'])
        
        # Check if owner is trying to rent own instrument
        if instrument.owner_id == user_id:
            rental_ns.abort(400, 'Owner cannot rent their own instrument')
        
        # Parse dates
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        # Validate dates are not in the past
        today = datetime.utcnow().date()
        if start_date < today or end_date < today:
            rental_ns.abort(400, 'Cannot rent for dates that have already passed')
        
        # Validate start_date is before end_date
        if start_date >= end_date:
            rental_ns.abort(400, 'Start date must be before end date')
        
        # Calculate total price: (end_date - start_date) * price_per_day
        num_days = (end_date - start_date).days
        calculated_price = num_days * instrument.price_per_day
        
        # Create rental
        rental = Rental(
            instrument_id=data['instrument_id'],
            renter_id=user_id,
            start_date=start_date,
            end_date=end_date,
            total_price=calculated_price,
            comment=data.get('comment'),
            status='pending',
            owner_response='pending'
        )
        
        db.session.add(rental)
        db.session.commit()
        
        return rental_to_dict(rental), 201
    
    @jwt_required()
    @rental_ns.doc(params={
        'status': {'type': 'string', 'description': 'Filter by status'},
        'owner_response': {'type': 'string', 'description': 'Filter by owner response'},
        'limit': {'type': 'integer', 'default': 20, 'description': 'Result limit'}
    })
    @rental_ns.marshal_with(rental_model, as_list=True, description='List of rentals')
    def get(self):
        """Get rentals (filtered by user's role: owner/renter)"""
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        args = rental_filter_parser.parse_args()
        
        # Get rentals where user is owner or renter
        query = Rental.query.filter(
            (Rental.renter_id == user_id) | (Rental.instrument.has(owner_id=user_id))
        )
        
        # Apply filters
        if args.status:
            query = query.filter_by(status=args.status)
        if args.owner_response:
            query = query.filter_by(owner_response=args.owner_response)
        
        # Limit results
        rentals = query.limit(args.limit).all()
        return [rental_to_dict(r) for r in rentals]


@rental_ns.route('/<int:rental_id>')
class RentalDetail(Resource):
    @jwt_required()
    @rental_ns.marshal_with(rental_model, description='Rental details')
    @rental_ns.response(404, 'Rental not found')
    def get(self, rental_id):
        """Get rental details"""
        user_id = int(get_jwt_identity())
        rental = Rental.query.get_or_404(rental_id)
        
        # Verify user has access (is renter or instrument owner)
        if rental.renter_id != user_id and rental.instrument.owner_id != user_id:
            rental_ns.abort(403, 'Access denied')
        
        return rental_to_dict(rental)


@rental_ns.route('/<int:rental_id>/counter-offer')
class RentalCounterOffer(Resource):
    @jwt_required()
    @rental_ns.expect(rental_counter_offer_model)
    @rental_ns.marshal_with(rental_model, description='Counter-offer sent')
    @rental_ns.response(403, 'Only renter can send counter-offers')
    @rental_ns.response(404, 'Rental not found')
    def patch(self, rental_id):
        """Renter sends counter-offer price (owner can accept, reject, or negotiate)"""
        user_id = int(get_jwt_identity())
        rental = Rental.query.get_or_404(rental_id)
        
        # Only renter can make counter-offer
        if rental.renter_id != user_id:
            rental_ns.abort(403, 'Only renter can send counter-offers')
        
        data = request.get_json()
        rental.negotiated_price = data['negotiated_price']
        rental.owner_response = 'counter_offer'
        rental.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return rental_to_dict(rental)


@rental_ns.route('/<int:rental_id>/accept')
class RentalAccept(Resource):
    @jwt_required()
    @rental_ns.marshal_with(rental_model, description='Rental accepted')
    @rental_ns.response(400, 'Cannot accept rental at this time')
    @rental_ns.response(403, 'Only instrument owner can accept rental')
    @rental_ns.response(404, 'Rental not found')
    def patch(self, rental_id):
        """Owner accepts rental request"""
        user_id = int(get_jwt_identity())
        rental = Rental.query.get_or_404(rental_id)
        
        # Only owner can accept
        if rental.instrument.owner_id != user_id:
            rental_ns.abort(403, 'Only instrument owner can accept rental')
        
        if rental.owner_response not in ['pending', 'counter_offer']:
            rental_ns.abort(400, 'Cannot accept rental at this time')
        
        # Use negotiated price if available, otherwise original price
        final_price = rental.negotiated_price or rental.total_price
        
        rental.status = 'confirmed'
        rental.owner_response = 'accepted'
        rental.total_price = final_price
        rental.updated_at = datetime.utcnow()
        
        # Update instrument status
        rental.instrument.status = 'rented'
        
        db.session.commit()
        
        return rental_to_dict(rental)


@rental_ns.route('/<int:rental_id>/reject')
class RentalReject(Resource):
    @jwt_required()
    @rental_ns.marshal_with(rental_model, description='Rental rejected')
    @rental_ns.response(400, 'Cannot reject rental at this time')
    @rental_ns.response(403, 'Only instrument owner can reject rental')
    @rental_ns.response(404, 'Rental not found')
    def patch(self, rental_id):
        """Owner rejects rental request"""
        user_id = int(get_jwt_identity())
        rental = Rental.query.get_or_404(rental_id)
        
        # Only owner can reject
        if rental.instrument.owner_id != user_id:
            rental_ns.abort(403, 'Only instrument owner can reject rental')
        
        if rental.owner_response not in ['pending', 'counter_offer']:
            rental_ns.abort(400, 'Cannot reject rental at this time')
        
        rental.status = 'cancelled'
        rental.owner_response = 'rejected'
        rental.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return rental_to_dict(rental)


@rental_ns.route('/by-renter/<int:renter_id>')
class RentalByRenter(Resource):
    @jwt_required()
    @rental_ns.marshal_with(rental_model, as_list=True, description='List of rentals by renter')
    @rental_ns.response(404, 'User not found')
    def get(self, renter_id):
        """Get all rental requests from a specific renter"""
        User.query.get_or_404(renter_id)
        rentals = Rental.query.filter_by(renter_id=renter_id).all()
        return [rental_to_dict(r) for r in rentals]


@rental_ns.route('/by-owner/<int:owner_id>')
class RentalByOwner(Resource):
    @jwt_required()
    @rental_ns.marshal_with(rental_model, as_list=True, description='List of rental requests for owner instruments')
    @rental_ns.response(404, 'User not found')
    def get(self, owner_id):
        """Get all rental requests for an owner's instruments"""
        User.query.get_or_404(owner_id)
        rentals = Rental.query.join(Instrument).filter(Instrument.owner_id == owner_id).all()
        return [rental_to_dict(r) for r in rentals]


def rental_to_dict(rental):
    """Convert rental to dictionary with related data"""
    return {
        'id': rental.id,
        'instrument_id': rental.instrument_id,
        'renter_id': rental.renter_id,
        'owner_id': rental.instrument.owner_id if rental.instrument else None,
        'renter_name': rental.renter.name if rental.renter else None,
        'instrument_name': rental.instrument.name if rental.instrument else None,
        'start_date': rental.start_date.isoformat() if rental.start_date else None,
        'end_date': rental.end_date.isoformat() if rental.end_date else None,
        'total_price': rental.total_price,
        'negotiated_price': rental.negotiated_price,
        'status': rental.status,
        'owner_response': rental.owner_response,
        'comment': rental.comment,
        'created_at': rental.created_at.isoformat() if rental.created_at else None,
        'updated_at': rental.updated_at.isoformat() if rental.updated_at else None
    }
