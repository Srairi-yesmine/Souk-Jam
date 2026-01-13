"""
Geocoding Service for Souk'Jam

This module provides location geocoding functionality specifically optimized for Tunisia.
It converts location names (cities, regions) to latitude/longitude coordinates for
location-based features like instrument search and jam matching.

Key Features:
- Multiple geocoding strategies for improved accuracy
- Tunisia-specific validation and corrections
- Fallback mechanisms for failed geocoding attempts
- Rate limiting and error handling

Supported Services:
- Nominatim (OpenStreetMap) - Primary free service
- Google Maps Geocoding API - Optional premium fallback
"""

from flask import current_app
from geopy.geocoders import Nominatim, GoogleV3
import os
import time
import logging

# Get logger that works outside Flask context
logger = logging.getLogger(__name__)

# Tunisia geographic bounds for coordinate validation
TUNISIA_BOUNDS = {
    'north': 37.5,  # Northernmost point (Bizerte)
    'south': 30.2,  # Southernmost point (Tataouine)
    'east': 11.6,   # Easternmost point (Zarzis)
    'west': 7.5     # Westernmost point (Gafsa)
}

def geocode_location(location_name):
    """
    Advanced geocoding for Tunisia with multiple strategies for accuracy.

    This function tries multiple geocoding approaches to ensure the best possible
    coordinate accuracy for Tunisian locations. It validates results against
    Tunisia's geographic bounds and provides fallback options.

    Args:
        location_name (str): Location name (e.g., "Tunis, Tunisia", "Sfax")

    Returns:
        tuple: (latitude, longitude) or (None, None) if geocoding fails
    """
    if not location_name:
        return None, None

    normalized_location = location_name.lower().strip()

    # Try multiple geocoding strategies in order of preference
    strategies = [
        _geocode_with_nominatim_structured,
        _geocode_with_nominatim_freetext,
        _geocode_with_google_if_available,
        _geocode_with_fallback_coordinates
    ]

    for strategy in strategies:
        try:
            lat, lng = strategy(normalized_location, location_name)
            if lat is not None and lng is not None:
                if _is_within_tunisia_bounds(lat, lng):
                    logger.info(f"Successfully geocoded '{location_name}' using {strategy.__name__}: {lat}, {lng}")
                    return lat, lng
                else:
                    logger.warning(f"Coordinates for '{location_name}' outside Tunisia: {lat}, {lng}")
        except Exception as e:
            logger.debug(f"Strategy {strategy.__name__} failed for '{location_name}': {e}")
            continue

    logger.error(f"All geocoding strategies failed for: {location_name}")
    return None, None

def _geocode_with_nominatim_structured(normalized_location, original_location):
    """Try structured geocoding with Nominatim"""
    geolocator = Nominatim(user_agent="souk-jam-api")

    # Parse location components
    parts = [x.strip() for x in original_location.split(",")]
    parts = [x for x in parts if x]

    # Try different structured formats
    if len(parts) >= 2:
        # Format: "City, Region, Tunisia"
        structured_query = {
            "city": parts[0],
            "state": parts[1] if len(parts) > 1 else None,
            "country": "Tunisia"
        }

        location = geolocator.geocode(structured_query, country_codes=['TN'], exactly_one=True)
        if location:
            return location.latitude, location.longitude

    return None, None

def _geocode_with_nominatim_freetext(normalized_location, original_location):
    """Try free text geocoding with multiple variations"""
    geolocator = Nominatim(user_agent="souk-jam-api")

    # Try different query variations
    queries = [
        original_location,
        f"{original_location}, Tunisia" if not original_location.lower().endswith("tunisia") else original_location,
        f"{original_location}, TN",  # ISO country code
    ]

    for query in queries:
        location = geolocator.geocode(query, country_codes=['TN'], exactly_one=True)
        if location:
            return location.latitude, location.longitude

        # Add small delay to avoid rate limiting
        time.sleep(0.1)

    return None, None

def _geocode_with_google_if_available(normalized_location, original_location):
    """Use Google Maps Geocoding API if API key is available"""
    google_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not google_api_key:
        return None, None

    try:
        geolocator = GoogleV3(api_key=google_api_key)

        # Add Tunisia bias
        location = geolocator.geocode(
            original_location,
            components={"country": "TN"},
            exactly_one=True
        )

        if location:
            return location.latitude, location.longitude

    except Exception as e:
        logger.warning(f"Google Maps geocoding failed: {e}")

    return None, None

def _geocode_with_fallback_coordinates(normalized_location, original_location):
    """Fallback to manual coordinates for known locations"""
    # Keep the manual corrections as last resort
    TUNISIA_LOCATION_CORRECTIONS = {
        "megrine, ben arous, tunisia": (36.7681, 10.2361),
        "megrine ben arous tunisia": (36.7681, 10.2361),
        "ben arous, tunisia": (36.7545, 10.2220),
        "tunis, tunisia": (36.8065, 10.1815),
        "sousse, tunisia": (35.8256, 10.6369),
        "sfax, tunisia": (34.7406, 10.7603),
        "monastir, tunisia": (35.7833, 10.8333),
        "kairouan, tunisia": (35.6781, 10.0963),
        "bizerte, tunisia": (37.2744, 9.8739),
        "gabès, tunisia": (33.8815, 10.0982),
        "ariana, tunisia": (36.8625, 10.1956),
        "gafsa, tunisia": (34.4250, 8.7842),
        "medenine, tunisia": (33.3549, 10.5055),
        "tatouine, tunisia": (32.9297, 10.4518),
        "kébili, tunisia": (33.7044, 8.9690),
        "tozeur, tunisia": (33.9197, 8.1335),
        "beja, tunisia": (36.7256, 9.1817),
        "jendouba, tunisia": (36.5011, 8.7802),
        "el kef, tunisia": (36.1742, 8.7147),
        "siliana, tunisia": (36.0849, 9.3708),
        "zaghouan, tunisia": (36.4029, 10.1423),
        "sidi bouzid, tunisia": (35.0382, 9.4849),
        "mahdia, tunisia": (35.5047, 11.0622),
        "nabeul, tunisia": (36.4561, 10.7376),
        "hammamet, tunisia": (36.4000, 10.6167),
    }

    return TUNISIA_LOCATION_CORRECTIONS.get(normalized_location, (None, None))

def _is_within_tunisia_bounds(lat, lng):
    """Check if coordinates are within Tunisia's approximate bounds"""
    return (TUNISIA_BOUNDS['south'] <= lat <= TUNISIA_BOUNDS['north'] and
            TUNISIA_BOUNDS['west'] <= lng <= TUNISIA_BOUNDS['east'])

def reverse_geocode(lat, lng):
    """
    Reverse geocode coordinates to get a human-readable address.
    """
    if not (lat and lng):
        return None

    geolocator = Nominatim(user_agent="souk-jam-api")

    try:
        location = geolocator.reverse((lat, lng), exactly_one=True)
        if location:
            # Extract just the city/region part, not the full address
            address_parts = location.address.split(', ')
            if len(address_parts) >= 2:
                # Return something like "City, Region"
                return f"{address_parts[0]}, {address_parts[1]}"
            return location.address
    except Exception as e:
        logger.error(f"Reverse geocoding error for {lat}, {lng}: {e}")

    return None
