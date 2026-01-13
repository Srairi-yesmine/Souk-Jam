"""
Jam Routes for Souk'Jam

This module handles jam session discovery and matching functionality.
It provides endpoints for finding compatible musicians, sending jam requests,
and managing mutual matches based on musical preferences and profiles.

Features:
- User discovery based on musical compatibility
- Role-based matching (jammers with owners, etc.)
- Similarity scoring using multi-factor algorithm
- Jam request system with pending/accepted/rejected states
- Mutual match detection for confirmed connections

Integration:
- Uses JamSimilarityService for intelligent user matching
- Leverages user profiles (genres, instruments, location)
- Supports skipping users to refine discovery
"""

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from ..models import User, JamRequest
from ..extensions import db
from ..services.jam_similarity import JamSimilarityService
import logging

logger = logging.getLogger(__name__)

jam_ns = Namespace('jam', description='Jam operations')

# Define Swagger models
user_discover_model = jam_ns.model('UserDiscover', {
    'id': fields.Integer(description='User ID'),
    'name': fields.String(description='User name'),
    'location_name': fields.String(description='Location name'),
    'role': fields.String(description='User role'),
    'genres_enjoyed': fields.List(fields.String, description='Genres enjoyed'),
    'instruments_played': fields.List(fields.Raw, description='Instruments played'),
    'similarity_score': fields.Float(description='Similarity score')
})

jam_request_model = jam_ns.model('JamRequest', {
    'id': fields.Integer(description='Request ID'),
    'sender_id': fields.Integer(description='Sender user ID'),
    'receiver_id': fields.Integer(description='Receiver user ID'),
    'status': fields.String(description='Request status'),
    'created_at': fields.DateTime(description='Created at')
})

@jam_ns.route('/discover')
class JamDiscover(Resource):
    @jwt_required()
    @jam_ns.marshal_with(user_discover_model, as_list=True, description='List of users for jam discovery')
    def get(self):
        """
        Discover compatible users for jamming.

        This endpoint finds users who are musically compatible based on:
        - Role compatibility (jammers match with owners, etc.)
        - Shared musical genres and instruments
        - Location proximity (future enhancement)
        - Similarity scoring algorithm

        Returns users sorted by compatibility score.
        """
        try:
            current_user_id = int(get_jwt_identity())
            current_user = User.query.get_or_404(current_user_id)

            # Get limit parameter from query string
            limit_param = request.args.get('limit', default=20, type=int)

            # Get all users except current user
            all_users = User.query.filter(User.id != current_user_id).all()

            # Filter by role compatibility - be more permissive
            compatible_users = JamSimilarityService.get_role_compatible_users(current_user, all_users)

            # If no compatible users with jam filter, include all users who have genres or instruments
            if not compatible_users:
                compatible_users = [u for u in all_users if u.genres_enjoyed or u.instruments_played]

            # If still no users, return all other users
            if not compatible_users:
                compatible_users = all_users

            # Calculate similarity scores and get top matches
            scored_matches = JamSimilarityService.find_similar_users(
                current_user=current_user,
                candidates=compatible_users,
                min_score=0.0,  # Accept any score
                limit=limit_param
            )

            # Format response
            result = []
            for match in scored_matches:
                user = match['user']
                result.append({
                    'id': user.id,
                    'name': user.name,
                    'location_name': user.location_name or 'Unknown',
                    'role': user.role,
                    'genres_enjoyed': user.genres_enjoyed or [],
                    'instruments_played': user.instruments_played or [],
                    'profile_photo_url': user.profile_photo_url or '',
                    'similarity_score': match['similarity_score']
                })

            return result
        except Exception as e:
            logger.error(f"Error in JamDiscover.get(): {str(e)}", exc_info=True)
            jam_ns.abort(500, f'Error discovering users: {str(e)}')

@jam_ns.route('/request/<int:user_id>')
class JamRequestSend(Resource):
    @jwt_required()
    @jam_ns.response(201, 'Jam request sent')
    @jam_ns.response(400, 'Invalid request')
    def post(self, user_id):
        """
        Send a jam request to another user.

        Creates a pending jam request. If both users send requests to each other,
        they become mutual matches visible in the /matches endpoint.
        """
        try:
            current_user_id = int(get_jwt_identity())

            # Verify both users exist
            current_user = User.query.get(current_user_id)
            target_user = User.query.get(user_id)
            
            if not current_user or not target_user:
                return {'message': 'One or both users not found'}, 400

            if current_user_id == user_id:
                return {'message': 'Cannot send request to yourself'}, 400

            # Check if request already exists
            existing = JamRequest.query.filter(
                ((JamRequest.sender_id == current_user_id) & (JamRequest.receiver_id == user_id)) |
                ((JamRequest.sender_id == user_id) & (JamRequest.receiver_id == current_user_id))
            ).first()

            if existing:
                return {'message': 'Request already exists'}, 400

            jam_request = JamRequest(sender_id=current_user_id, receiver_id=user_id)
            db.session.add(jam_request)
            db.session.commit()

            return {'message': 'Jam request sent'}, 201
        except Exception as e:
            logger.error(f"Error in JamRequestSend.post(): {str(e)}", exc_info=True)
            return {'message': f'Error sending jam request: {str(e)}'}, 500

@jam_ns.route('/skip/<int:user_id>')
class JamSkip(Resource):
    @jwt_required()
    @jam_ns.response(200, 'User skipped')
    def post(self, user_id):
        """
        Skip a user in jam discovery.

        This prevents the user from appearing in future discovery results
        and helps refine the matching algorithm.
        """
        try:
            current_user_id = int(get_jwt_identity())

            # Create a skipped request
            jam_request = JamRequest(sender_id=current_user_id, receiver_id=user_id, status='skipped')
            db.session.add(jam_request)
            db.session.commit()

            return {'message': 'User skipped'}, 200
        except Exception as e:
            logger.error(f"Error in JamSkip.post(): {str(e)}", exc_info=True)
            return {'message': f'Error skipping user: {str(e)}'}, 500

@jam_ns.route('/matches')
class JamMatches(Resource):
    @jwt_required()
    @jam_ns.marshal_with(user_discover_model, as_list=True, description='Mutual jam matches')
    def get(self):
        """
        Get mutual jam matches.

        Returns users who have sent jam requests to the current user AND
        the current user has sent requests back to them. These are confirmed
        mutual connections ready for jamming.
        """
        current_user_id = int(get_jwt_identity())

        # Find users who have sent requests to current user and current user has sent back
        mutual_user_ids = db.session.query(JamRequest.sender_id).filter(
            JamRequest.receiver_id == current_user_id,
            JamRequest.status == 'pending'
        ).intersect(
            db.session.query(JamRequest.receiver_id).filter(
                JamRequest.sender_id == current_user_id,
                JamRequest.status == 'pending'
            )
        ).all()

        mutual_user_ids = [uid[0] for uid in mutual_user_ids]

        users = User.query.filter(User.id.in_(mutual_user_ids)).all()

        result = []
        for user in users:
            result.append({
                'id': user.id,
                'name': user.name,
                'location_name': user.location_name,
                'role': user.role,
                'genres_enjoyed': user.genres_enjoyed or [],
                'instruments_played': user.instruments_played or [],
                'similarity_score': 100  # Mutual matches get max score
            })

        return result