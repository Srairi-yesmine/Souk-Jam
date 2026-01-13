"""
Jam Similarity Service - Advanced User Matching Algorithm

This module implements sophisticated algorithms for matching musicians based on
multiple compatibility factors. It's the core intelligence behind Souk'Jam's
jam session matching feature, helping musicians find compatible partners.

Matching Factors (with weights):
- Location proximity (25%): Physical distance between users
- Genre compatibility (30%): Shared musical genres and preferences
- Instrument compatibility (30%): Complementary instruments and skills
- Skill level matching (15%): Appropriate skill level compatibility

The algorithm produces a similarity score from 0-100, where higher scores
indicate better matches for jam sessions.
"""

from math import radians, sin, cos, sqrt, atan2
from typing import List, Dict, Any, Optional
from ..models import User
import logging

logger = logging.getLogger(__name__)


class JamSimilarityService:
    """
    Service for calculating similarity scores between users for jam matching.

    This class implements a multi-factor similarity algorithm that considers:
    - Geographic proximity for feasible meetups
    - Musical genre preferences for style compatibility
    - Instrument skills for complementary roles in jam sessions
    - Skill levels for appropriate collaboration difficulty
    """

    # Weight constants for different similarity factors
    WEIGHTS = {
        'distance': 0.25,      # 25% weight for location proximity
        'genres': 0.30,        # 30% weight for genre compatibility
        'instruments': 0.30,   # 30% weight for instrument compatibility
        'skills': 0.15         # 15% weight for skill level compatibility
    }

    # Distance thresholds in km with corresponding scores
    DISTANCE_THRESHOLDS = [
        (5, 100),    # Within 5km: perfect score
        (10, 90),    # Within 10km: very good
        (25, 75),    # Within 25km: good
        (50, 50),    # Within 50km: moderate
        (100, 25),   # Within 100km: low
        (float('inf'), 0)  # Beyond 100km: no score
    ]

    # Complementary instrument pairs that work well together
    COMPLEMENTARY_INSTRUMENTS = [
        {'guitar', 'vocals'},
        {'guitar', 'drums'},
        {'bass', 'drums'},
        {'piano', 'vocals'},
        {'piano', 'violin'},
        {'violin', 'cello'},
        {'saxophone', 'piano'},
        {'trumpet', 'piano'},
        {'flute', 'piano'},
        {'double bass', 'piano'},
        {'oud', 'violin'},
        {'oud', 'qanun'},
        {'ney', 'violin'},
        {'accordion', 'guitar'},
        {'accordion', 'vocals'}

    ]

    # Skill level mappings for compatibility calculation
    SKILL_LEVELS = {
        'beginner': 1,
        'intermediate': 2,
        'advanced': 3,
        'expert': 4
    }

    @staticmethod
    def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate great circle distance between two points using Haversine formula.

        Args:
            lat1, lng1: Coordinates of first point
            lat2, lng2: Coordinates of second point

        Returns:
            Distance in kilometers
        """
        if not all([lat1, lng1, lat2, lng2]):
            return float('inf')

        R = 6371  # Earth radius in km

        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        return R * c

    @staticmethod
    def get_distance_score(distance: float) -> float:
        """
        Convert distance to a score based on predefined thresholds.

        Args:
            distance: Distance in kilometers

        Returns:
            Score between 0-100
        """
        for threshold, score in JamSimilarityService.DISTANCE_THRESHOLDS:
            if distance <= threshold:
                return score
        return 0

    @staticmethod
    def calculate_genre_similarity(genres1: List[str], genres2: List[str]) -> float:
        """
        Calculate genre similarity using Jaccard similarity coefficient.

        Args:
            genres1, genres2: Lists of genre strings

        Returns:
            Similarity score between 0-100
        """
        # Handle old data: convert None to empty list
        genres1 = genres1 or []
        genres2 = genres2 or []
        
        if not genres1 or not genres2:
            return 0

        # Safely convert to lowercase, handling non-string types
        set1 = set(str(g).lower() for g in genres1 if g)
        set2 = set(str(g).lower() for g in genres2 if g)

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        if union == 0:
            return 0

        # Jaccard similarity
        jaccard = intersection / union

        # Boost score for exact matches
        if set1 == set2:
            jaccard *= 1.2

        return min(jaccard * 100, 100)

    @staticmethod
    def calculate_instrument_similarity(instruments1: List[Dict], instruments2: List[Dict]) -> float:
        """
        Calculate instrument compatibility score.

        Considers:
        - Same instruments played
        - Complementary instrument pairs
        - Instrument variety

        Args:
            instruments1, instruments2: Lists of instrument dicts with 'instrument_type' and 'skill_level'

        Returns:
            Similarity score between 0-100
        """
        # Handle old data: convert None to empty list
        instruments1 = instruments1 or []
        instruments2 = instruments2 or []
        
        if not instruments1 or not instruments2:
            return 0

        # Safely extract instrument types, handling different data formats
        types1 = set()
        types2 = set()
        
        for inst in instruments1:
            if isinstance(inst, dict):
                inst_type = inst.get('instrument_type', '')
            elif isinstance(inst, str):
                inst_type = inst
            else:
                inst_type = str(inst)
            if inst_type:
                types1.add(inst_type.lower())
        
        for inst in instruments2:
            if isinstance(inst, dict):
                inst_type = inst.get('instrument_type', '')
            elif isinstance(inst, str):
                inst_type = inst
            else:
                inst_type = str(inst)
            if inst_type:
                types2.add(inst_type.lower())

        score = 0

        # Same instruments bonus
        same_instruments = len(types1 & types2)
        score += same_instruments * 20  # 20 points per same instrument

        # Complementary instruments bonus
        for pair in JamSimilarityService.COMPLEMENTARY_INSTRUMENTS:
            pair_lower = {inst.lower() for inst in pair}
            if pair_lower.issubset(types1 | types2):
                score += 15  # 15 points for complementary pairs

        # Instrument variety bonus (encourage diverse groups)
        total_unique = len(types1 | types2)
        if total_unique >= 3:
            score += 10
        elif total_unique >= 2:
            score += 5

        # Penalty for too many overlapping instruments (avoid duplicate roles)
        overlap_ratio = same_instruments / max(len(types1), len(types2), 1)
        if overlap_ratio > 0.7:
            score *= 0.8  # 20% penalty

        return min(score, 100)

    @staticmethod
    def calculate_skill_similarity(instruments1: List[Dict], instruments2: List[Dict]) -> float:
        """
        Calculate skill level compatibility.

        Args:
            instruments1, instruments2: Lists of instrument dicts with skill levels

        Returns:
            Similarity score between 0-100
        """
        # Handle old data: convert None to empty list
        instruments1 = instruments1 or []
        instruments2 = instruments2 or []
        
        if not instruments1 or not instruments2:
            return 50  # Neutral score if no skill info

        # Safely extract skill levels, handling different data formats
        skills1 = []
        for inst in instruments1:
            if isinstance(inst, dict):
                skill = inst.get('skill_level', 'intermediate')
            else:
                skill = 'intermediate'
            skill_level = JamSimilarityService.SKILL_LEVELS.get(skill, 2)
            skills1.append(skill_level)
        
        skills2 = []
        for inst in instruments2:
            if isinstance(inst, dict):
                skill = inst.get('skill_level', 'intermediate')
            else:
                skill = 'intermediate'
            skill_level = JamSimilarityService.SKILL_LEVELS.get(skill, 2)
            skills2.append(skill_level)

        if not skills1 or not skills2:
            return 50

        avg_skill1 = sum(skills1) / len(skills1)
        avg_skill2 = sum(skills2) / len(skills2)

        skill_diff = abs(avg_skill1 - avg_skill2)

        # Score based on skill difference
        if skill_diff <= 0.3:
            return 100  # Very compatible
        elif skill_diff <= 0.7:
            return 80   # Compatible
        elif skill_diff <= 1.0:
            return 60   # Moderately compatible
        elif skill_diff <= 1.5:
            return 30   # Somewhat compatible
        else:
            return 10   # Not very compatible

    @classmethod
    def calculate_similarity_score(cls, user1: User, user2: User) -> float:
        """
        Calculate comprehensive similarity score between two users.

        Args:
            user1, user2: User model instances

        Returns:
            Similarity score between 0-100
        """
        scores = {}

        # Distance score
        if (user1.location_lat and user1.location_lng and
            user2.location_lat and user2.location_lng):
            distance = cls.calculate_distance(
                user1.location_lat, user1.location_lng,
                user2.location_lat, user2.location_lng
            )
            scores['distance'] = cls.get_distance_score(distance)
        else:
            scores['distance'] = 0

        # Genre score
        scores['genres'] = cls.calculate_genre_similarity(
            user1.genres_enjoyed or [],
            user2.genres_enjoyed or []
        )

        # Instrument score
        scores['instruments'] = cls.calculate_instrument_similarity(
            user1.instruments_played or [],
            user2.instruments_played or []
        )

        # Skill score
        scores['skills'] = cls.calculate_skill_similarity(
            user1.instruments_played or [],
            user2.instruments_played or []
        )

        # Weighted final score
        final_score = sum(
            scores[factor] * cls.WEIGHTS[factor]
            for factor in cls.WEIGHTS.keys()
        )

        logger.debug(f"Similarity scores for users {user1.id} and {user2.id}: {scores}, final: {final_score}")

        return round(final_score, 2)

    @classmethod
    def find_similar_users(cls, current_user: User, candidates: List[User],
                          min_score: float = 20.0, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Find and rank similar users for jam matching.

        Args:
            current_user: The user looking for matches
            candidates: List of potential match candidates
            min_score: Minimum similarity score to include
            limit: Maximum number of results to return

        Returns:
            List of dicts with user and similarity_score keys, sorted by score desc
        """
        scored_users = []

        for candidate in candidates:
            if candidate.id == current_user.id:
                continue

            score = cls.calculate_similarity_score(current_user, candidate)

            if score >= min_score:
                scored_users.append({
                    'user': candidate,
                    'similarity_score': score
                })

        # Sort by score descending
        scored_users.sort(key=lambda x: x['similarity_score'], reverse=True)

        return scored_users[:limit]

    @classmethod
    def get_role_compatible_users(cls, current_user: User, all_users: List[User]) -> List[User]:
        """
        Filter users based on role compatibility for jam matching.

        Args:
            current_user: The user looking for matches
            all_users: All potential users

        Returns:
            Filtered list of compatible users
        """
        compatible_users = []

        for user in all_users:
            if user.id == current_user.id:
                continue

            # Role-based filtering logic
            if current_user.role == 'owner':
                # Owners can jam with musicians and renters who are active
                if user.role in ['jammer', 'renter'] and user.is_active_for_jam:
                    compatible_users.append(user)
            elif current_user.role == 'renter':
                # Renters can only jam if they're active, and match with musicians/owners
                if (current_user.is_active_for_jam and
                    user.role in ['jammer', 'owner']):
                    compatible_users.append(user)
            elif current_user.role == 'jammer':
                # Musicians can jam with anyone who is active
                if user.is_active_for_jam:
                    compatible_users.append(user)

        return compatible_users