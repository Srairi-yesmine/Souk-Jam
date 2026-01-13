# 🎵 Souk'Jam - Musical Jam Session Platform

A sophisticated Flask-based REST API platform for connecting musicians across Tunisia. Souk'Jam enables instrument rental, location-based jam session discovery, and intelligent musician matching using multi-factor compatibility algorithms.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Setup & Installation](#setup--installation)
- [Database Models](#database-models)
- [API Endpoints](#api-endpoints)
- [Testing Guide](#testing-guide)
- [Jam Session Feature](#jam-session-feature)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

### Core Platform Features

1. **User Management**
   - Secure user registration with strong password validation
   - JWT-based authentication for API access
   - Role-based user profiles (Jammer, Owner, Renter)
   - Location-based user profiles with geocoding

2. **Instrument Rental Marketplace**
   - Browse available instruments with detailed specifications
   - Advanced search and filtering capabilities
   - Location-based distance calculations (Haversine formula)
   - Pricing in Tunisian Dinars (TND)
   - Rental request management

3. **Jam Session Discovery & Matching**
   - Intelligent user discovery based on musical compatibility
   - Multi-factor similarity scoring algorithm
   - Mutual jam match detection
   - Skip users to refine discovery results

4. **Advanced Search & Sorting**
   - Filter instruments by type, price, location
   - Sort by distance, price, newest, location, or owner
   - Location-aware distance calculations for nearest instruments

5. **Media Management**
   - Secure file upload for user profiles and instrument photos
   - Support for PNG, JPG, GIF formats
   - UUID-based filename generation for security

---

## 🏗️ Architecture

### Project Structure

```
Souk'Jam/
├── app/
│   ├── __init__.py                    # Flask app factory
│   ├── config.py                      # Configuration management
│   ├── extensions.py                  # Global extensions (db, jwt, api)
│   ├── auth/
│   │   └── routes.py                  # Authentication endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                    # User model & relationships
│   │   ├── instrument.py              # Instrument model
│   │   ├── rental.py                  # Rental model
│   │   └── jam.py                     # JamRequest model
│   ├── routes/
│   │   ├── instruments.py             # Instrument CRUD & search
│   │   └── jam.py                     # Jam discovery endpoints
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py                    # User serialization schema
│   │   ├── instrument.py              # Instrument serialization
│   │   ├── rental.py                  # Rental serialization
│   │   └── search.py                  # Search parameter schemas
│   └── services/
│       ├── geocoding.py               # Location → Coordinates conversion
│       ├── jam_similarity.py          # Musician compatibility algorithm
│       └── storage.py                 # File upload handling
├── migrations/                        # Database migrations
├── tests/                             # Test suite
├── instance/                          # Instance-specific files
├── uploads/                           # File storage directory
├── requirements.txt                   # Python dependencies
├── seed.py                            # Database seeding script
├── docker-compose.yml                 # Docker Compose configuration
└── Dockerfile                         # Docker container definition
```

### Core Services

#### 1. JamSimilarityService (`app/services/jam_similarity.py`)

Multi-factor user matching algorithm calculating compatibility scores:

- **Location Compatibility (25%)**: Haversine distance formula
  - Converts distance (km) to compatibility score
  - Closer musicians score higher
  
- **Genre Similarity (30%)**: Jaccard similarity index
  - Shared musical genres between users
  - Common taste increases compatibility
  
- **Instrument Complementarity (30%)**: Pair matching
  - Users with complementary instruments score higher
  - Bonus points for complementary instrument pairs
  
- **Skill Level Compatibility (15%)**: Skill matching
  - Similar skill levels increase compatibility
  - Prevents mismatched experience levels

**Total Score**: Weighted combination of all factors (0-100)

#### 2. GeocodingService (`app/services/geocoding.py`)

Tunisia-optimized location resolution with multiple strategies:

1. **Structured Nominatim Query**: City + Tunisia search
2. **Free-text Nominatim**: Direct location string lookup
3. **Google Maps API** (optional): If API key configured
4. **Manual Fallback**: 20 predefined Tunisian city coordinates

Validates all coordinates within Tunisia bounds:
- **North**: 37.5°N
- **South**: 30.2°N  
- **East**: 11.6°E
- **West**: 7.5°W

#### 3. StorageService (`app/services/storage.py`)

Secure file upload handling:

- Validates file extensions: PNG, JPG, JPEG, GIF
- Uses `secure_filename()` + UUID for collision-free naming
- Stores files in `uploads/` directory
- Returns `/uploads/{uuid_filename}` URL for retrieval

---

## 🛠️ Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Framework** | Flask | 2.3.3 |
| **REST API** | Flask-RESTX | 1.2.0 |
| **ORM** | SQLAlchemy | 3.0.5 |
| **Database** | SQLite (dev) / PostgreSQL (prod) | Latest |
| **Authentication** | Flask-JWT-Extended | 4.5.3 |
| **Migrations** | Flask-Migrate (Alembic) | 4.0.5 |
| **Validation** | Marshmallow | 3.20.1 |
| **Geocoding** | Geopy | 2.3.0 |
| **Image Processing** | Pillow | 10.0.1 |
| **Testing** | Pytest | 7.4.0 |
| **Security** | Bcrypt | 4.0.1 |
| **Python** | Python | 3.9.6 |

---

## 📦 Setup & Installation

### 1. Prerequisites

- Python 3.9+
- Git
- Virtual environment tool (venv)
- Docker & Docker Compose (optional)

### 2. Clone Repository

```bash
git clone <repository-url>
cd Souk'Jam
```

### 3. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Environment Configuration

Create `.env` file in project root:

```env
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///instance/app.db
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
GOOGLE_MAPS_API_KEY=your-api-key-optional
```

### 6. Database Setup

```bash
# Initialize migrations (if first time)
flask db init

# Apply migrations
flask db upgrade

# Seed database with sample data
python seed.py
```

### 7. Run Application

```bash
# Development server
flask run

# Server will be available at http://localhost:5000
# Swagger UI documentation at http://localhost:5000/doc
```

### 8. Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at http://localhost:5000
```

---

## 💾 Database Models

### User Model

```python
{
  "id": integer,
  "email": string,              # Unique, required
  "password_hash": string,      # Bcrypt hashed
  "name": string,
  "location_name": string,      # e.g., "Tunis, Tunisia"
  "location_lat": float,        # Geocoded latitude
  "location_lng": float,        # Geocoded longitude
  "role": enum["jammer", "owner", "renter"],
  "genres_enjoyed": json,       # List of music genres
  "instruments_played": json,   # List of {instrument_type, skill_level}
  "instruments_owned": json,    # List of instrument types
  "is_active_for_jam": boolean,
  "created_at": datetime,
  "updated_at": datetime
}
```

### Instrument Model

```python
{
  "id": integer,
  "owner_id": integer,          # Foreign key to User
  "name": string,               # e.g., "Fender Stratocaster"
  "instrument_type": string,    # e.g., "guitar", "drums", "keyboard"
  "brand": string,              # Manufacturer name
  "price_per_day": float,       # Rental price in TND
  "location_name": string,      # Rental location
  "location_lat": float,
  "location_lng": float,
  "description": string,        # Details about condition, features
  "image_url": string,          # Path to instrument photo
  "available": boolean,
  "created_at": datetime,
  "updated_at": datetime
}
```

### Rental Model

```python
{
  "id": integer,
  "instrument_id": integer,     # Foreign key to Instrument
  "renter_id": integer,         # Foreign key to User
  "start_date": date,
  "end_date": date,
  "total_price": float,
  "status": enum["pending", "active", "completed", "cancelled"],
  "created_at": datetime
}
```

### JamRequest Model

```python
{
  "id": integer,
  "sender_id": integer,         # User sending request
  "receiver_id": integer,       # User receiving request
  "status": enum["pending", "accepted", "rejected", "skipped"],
  "created_at": datetime
}
```

---

## 🔌 API Endpoints

### Authentication (`/auth`)

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe",
  "location_name": "Tunis, Tunisia",
  "role": "jammer",
  "genres_enjoyed": ["rock", "jazz"],
  "instruments_played": [
    {"instrument_type": "guitar", "skill_level": "intermediate"}
  ],
  "instruments_owned": ["guitar"],
  "is_active_for_jam": true
}

Response: 201 Created
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "location_name": "Tunis, Tunisia",
  ...
}
```

**Password Requirements:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character (!@#$%^&*(),.?":{}|<>)

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Get All Users
```http
GET /auth/users
Authorization: Bearer <access_token>

Response: 200 OK
[
  {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    ...
  },
  ...
]
```

#### Get User Details
```http
GET /auth/users/<user_id>
Authorization: Bearer <access_token>

Response: 200 OK
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  ...
}
```

### Instruments (`/instruments`)

#### Get All Instruments (with search & filtering)
```http
GET /instruments?
  location_name=Tunis&
  max_distance=50&
  sort=distance&
  sort_by=asc&
  price_min=10&
  price_max=100&
  instrument_type=guitar&
  owner_id=1

Authorization: Bearer <access_token>

Response: 200 OK
[
  {
    "id": 1,
    "name": "Fender Stratocaster",
    "instrument_type": "guitar",
    "brand": "Fender",
    "price_per_day": 25.0,
    "location_name": "Tunis, Tunisia",
    "location_lat": 36.8,
    "location_lng": 10.2,
    "available": true,
    "distance_km": 2.5,
    "owner": {
      "id": 2,
      "name": "Guitar Owner"
    }
  },
  ...
]
```

**Query Parameters:**
- `location_name`: Filter by location
- `max_distance`: Max distance in km from location
- `sort`: Sort field (distance, price, price_per_day, newest, location, owner)
- `sort_by`: Sort order (asc, desc)
- `price_min`: Minimum price (TND)
- `price_max`: Maximum price (TND)
- `instrument_type`: Filter by instrument type
- `owner_id`: Filter by owner user ID

#### Create Instrument
```http
POST /instruments
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Fender Stratocaster",
  "instrument_type": "guitar",
  "brand": "Fender",
  "price_per_day": 25.0,
  "location_name": "Tunis, Tunisia",
  "description": "Classic electric guitar in excellent condition",
  "available": true
}

Response: 201 Created
```

#### Get Instrument Details
```http
GET /instruments/<instrument_id>
Authorization: Bearer <access_token>

Response: 200 OK
{
  "id": 1,
  "name": "Fender Stratocaster",
  ...
}
```

#### Update Instrument
```http
PUT /instruments/<instrument_id>
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "price_per_day": 30.0,
  "available": false
}

Response: 200 OK
```

#### Delete Instrument
```http
DELETE /instruments/<instrument_id>
Authorization: Bearer <access_token>

Response: 204 No Content
```

### Jam Sessions (`/jam`)

#### Discover Compatible Musicians
```http
GET /jam/discover
Authorization: Bearer <access_token>

Response: 200 OK
[
  {
    "id": 5,
    "name": "Jane Musician",
    "location_name": "Sfax, Tunisia",
    "role": "owner",
    "genres_enjoyed": ["rock", "blues"],
    "instruments_played": [
      {"instrument_type": "drums", "skill_level": "advanced"}
    ],
    "similarity_score": 78.5
  },
  ...
]
```

Returns up to 20 users sorted by compatibility score (highest first).

#### Send Jam Request
```http
POST /jam/request/<user_id>
Authorization: Bearer <access_token>

Response: 201 Created
{
  "message": "Jam request sent"
}
```

#### Skip User in Discovery
```http
POST /jam/skip/<user_id>
Authorization: Bearer <access_token>

Response: 200 OK
{
  "message": "User skipped"
}
```

#### Get Mutual Jam Matches
```http
GET /jam/matches
Authorization: Bearer <access_token>

Response: 200 OK
[
  {
    "id": 5,
    "name": "Jane Musician",
    "location_name": "Sfax, Tunisia",
    "role": "owner",
    "genres_enjoyed": ["rock", "blues"],
    "instruments_played": [...],
    "similarity_score": 100
  },
  ...
]
```

Returns only users who have both:
1. Sent a jam request to the current user
2. Received a jam request back from the current user

---

## 🧪 Testing Guide

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_app.py

# Run with coverage
pytest --cov=app tests/

# Verbose output
pytest -v
```

### Test Structure

```
tests/
└── test_app.py            # Health check and integration tests
```

### Current Test Coverage

- Health check endpoint (`GET /health`)
- Database initialization
- Flask app creation

### Testing Best Practices

1. Use in-memory SQLite for test database
2. Clear database between tests
3. Mock external services (Geopy)
4. Test both success and error cases
5. Verify JWT token generation

---

## 🎸 Jam Session Feature - Complete Testing Guide

The Jam Session feature enables musicians to discover compatible musicians and create mutual connections for jamming together.

### How It Works

1. **User A** browses compatible musicians via `/jam/discover`
2. **User A** sends a jam request to **User B** via `/jam/request/<user_b_id>`
3. **User B** also sends a jam request to **User A** via `/jam/request/<user_a_id>`
4. When mutual requests exist, both appear in `/jam/matches`

### Testing with Insomnia

#### Step 1: Get JWT Tokens for Two Users

**Create User 1 (Jammer - Guitarist)**
```http
POST http://localhost:5000/auth/register
Content-Type: application/json

{
  "email": "guitarist@soukjam.tn",
  "password": "JamSesh123!",
  "name": "Ahmed Guitarist",
  "location_name": "Tunis, Tunisia",
  "role": "jammer",
  "genres_enjoyed": ["rock", "metal"],
  "instruments_played": [
    {"instrument_type": "guitar", "skill_level": "advanced"}
  ],
  "is_active_for_jam": true
}
```

**Create User 2 (Drummer)**
```http
POST http://localhost:5000/auth/register
Content-Type: application/json

{
  "email": "drummer@soukjam.tn",
  "password": "DrumsRock123!",
  "name": "Fatima Drummer",
  "location_name": "Tunis, Tunisia",
  "role": "jammer",
  "genres_enjoyed": ["rock", "funk"],
  "instruments_played": [
    {"instrument_type": "drums", "skill_level": "intermediate"}
  ],
  "is_active_for_jam": true
}
```

Note the returned `id` values for each user. Let's say:
- User 1 (Guitarist) ID: `1`
- User 2 (Drummer) ID: `2`

**Login as User 1**
```http
POST http://localhost:5000/auth/login
Content-Type: application/json

{
  "email": "guitarist@soukjam.tn",
  "password": "JamSesh123!"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

Save this token as `TOKEN_USER1` in Insomnia environment variables.

**Login as User 2**
```http
POST http://localhost:5000/auth/login
Content-Type: application/json

{
  "email": "drummer@soukjam.tn",
  "password": "DrumsRock123!"
}
```

Save response token as `TOKEN_USER2`.

#### Step 2: Test Discovery

**User 1 Discovers Musicians**
```http
GET http://localhost:5000/jam/discover
Authorization: Bearer {{TOKEN_USER1}}
```

Response:
```json
[
  {
    "id": 2,
    "name": "Fatima Drummer",
    "location_name": "Tunis, Tunisia",
    "role": "jammer",
    "genres_enjoyed": ["rock", "funk"],
    "instruments_played": [
      {"instrument_type": "drums", "skill_level": "intermediate"}
    ],
    "similarity_score": 75.5
  }
]
```

**User 2 Discovers Musicians**
```http
GET http://localhost:5000/jam/discover
Authorization: Bearer {{TOKEN_USER2}}
```

Response shows User 1 with compatibility score.

#### Step 3: Test Jam Requests

**User 1 Sends Jam Request to User 2**
```http
POST http://localhost:5000/jam/request/2
Authorization: Bearer {{TOKEN_USER1}}
```

Response:
```json
{
  "message": "Jam request sent"
}
```

**User 2 Sends Jam Request Back to User 1**
```http
POST http://localhost:5000/jam/request/1
Authorization: Bearer {{TOKEN_USER2}}
```

Response:
```json
{
  "message": "Jam request sent"
}
```

#### Step 4: Test Mutual Matches

**User 1 Views Matches**
```http
GET http://localhost:5000/jam/matches
Authorization: Bearer {{TOKEN_USER1}}
```

Response:
```json
[
  {
    "id": 2,
    "name": "Fatima Drummer",
    "location_name": "Tunis, Tunisia",
    "role": "jammer",
    "genres_enjoyed": ["rock", "funk"],
    "instruments_played": [
      {"instrument_type": "drums", "skill_level": "intermediate"}
    ],
    "similarity_score": 100
  }
]
```

**User 2 Views Matches**
```http
GET http://localhost:5000/jam/matches
Authorization: Bearer {{TOKEN_USER2}}
```

Returns User 1 in the matches.

#### Step 5: Test Skip Feature

**Create User 3 (for skip testing)**
```http
POST http://localhost:5000/auth/register
Content-Type: application/json

{
  "email": "bassist@soukjam.tn",
  "password": "BassLines123!",
  "name": "Mohamed Bassist",
  "location_name": "Sousse, Tunisia",
  "role": "jammer",
  "genres_enjoyed": ["funk", "soul"],
  "instruments_played": [
    {"instrument_type": "bass", "skill_level": "beginner"}
  ],
  "is_active_for_jam": true
}
```

**User 1 Skips User 3**
```http
POST http://localhost:5000/jam/skip/3
Authorization: Bearer {{TOKEN_USER1}}
```

Response:
```json
{
  "message": "User skipped"
}
```

User 3 will no longer appear in User 1's discover results (marked as 'skipped').

### Similarity Score Calculation

The compatibility score is calculated based on:

| Factor | Weight | How It's Calculated |
|--------|--------|-------------------|
| Location | 25% | Haversine distance formula (closer = higher) |
| Genres | 30% | Jaccard similarity (shared genres) |
| Instruments | 30% | Complementary pairs (guitar+drums=higher) |
| Skills | 15% | Skill level compatibility |

**Example Calculation:**
- Location score: 80% of 25% = 20%
- Genres score: 100% of 30% = 30% (100% genre overlap)
- Instruments score: 95% of 30% = 28.5% (perfect complementary pair)
- Skills score: 60% of 15% = 9% (different skill levels)
- **Total: 87.5%**

### Troubleshooting Jam Feature

| Issue | Cause | Solution |
|-------|-------|----------|
| No users in discover | No other active users | Create more test users with `is_active_for_jam: true` |
| Mutual match not showing | Only one request sent | Both users must send requests to each other |
| Low similarity scores | Different locations/genres | Users must be in same region or share genres |
| Request fails with "already exists" | Duplicate request | Each user pair can only have one request |

---

## ⚙️ Configuration

### Environment Variables

```env
# Flask Configuration
FLASK_APP=app
FLASK_ENV=development|production
DEBUG=True|False

# Security Keys
SECRET_KEY=your-secret-key-minimum-32-chars
JWT_SECRET_KEY=your-jwt-secret-key-minimum-32-chars

# Database
DATABASE_URL=sqlite:///instance/app.db
SQLALCHEMY_TRACK_MODIFICATIONS=False

# File Storage
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16 MB

# Optional: Google Maps Geocoding
GOOGLE_MAPS_API_KEY=your-api-key-optional

# Server
FLASK_RUN_PORT=5000
FLASK_RUN_HOST=0.0.0.0
```

### Tunisian Cities in Database

The application includes geocoding support for 20 major Tunisian cities:

- Tunis, Ariana, Ben Arous, Manouba (Grand Tunis)
- Sfax, Tataouine, Tozeur
- Sousse, Monastir, Mahdia, Kairouan
- Djerba, Rades
- Sidi Bouzid, Chebika
- Khroumirie, Tabarka
- And more...

All are validated within Tunisia's geographic bounds.

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Database Migration Errors
```bash
# Reset migrations
rm -rf migrations/
flask db init
flask db migrate -m "initial migration"
flask db upgrade
python seed.py
```

#### 2. Port Already in Use
```bash
# Find process on port 5000
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
flask run --port 5001
```

#### 3. Import Errors
```bash
# Ensure .venv is activated
source .venv/bin/activate

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

#### 4. Location Geocoding Fails
- Verify location name format: "City, Country"
- Check internet connectivity for Nominatim service
- Verify coordinates fall within Tunisia bounds
- Check `app/services/geocoding.py` for supported cities

#### 5. JWT Token Errors
```
"Invalid token" or "Missing Authorization Header"
```

Solutions:
- Ensure token is passed in `Authorization: Bearer <token>` header
- Verify token hasn't expired (default: 30 days)
- Check `JWT_SECRET_KEY` is consistent in `.env`

#### 6. File Upload Fails
- Check `uploads/` directory exists and has write permissions
- Verify file extension is in allowed list (png, jpg, jpeg, gif)
- Check file size is under 16 MB limit
- Ensure UPLOAD_FOLDER path is correct

#### 7. Sorting Not Working
- Verify `sort` parameter is in valid list: `distance`, `price`, `price_per_day`, `newest`, `location`, `owner`
- For distance sorting, provide `location_name` parameter
- Check `sort_by` is either `asc` or `desc`

### Debug Mode

Enable detailed logging:

```python
# In app/__init__.py
if app.config['DEBUG']:
    logging.basicConfig(level=logging.DEBUG)
    logger.setLevel(logging.DEBUG)
```

### Health Check

```bash
curl http://localhost:5000/health

Response:
{
  "status": "ok"
}
```

---

## 📚 API Documentation

Interactive Swagger UI documentation is available at:

```
http://localhost:5000/doc
```

This provides:
- Live API endpoint testing
- Request/response schemas
- Parameter descriptions
- Authentication requirements

---

## 🔐 Security Considerations

1. **Password Security**
   - Bcrypt hashing with salt rounds
   - Strict validation requirements
   - Never exposed in API responses

2. **JWT Authentication**
   - Tokens include user ID as identity
   - Configurable expiration (default: 30 days)
   - HMAC-SHA256 signature verification

3. **File Upload Security**
   - Filename sanitization with `secure_filename()`
   - UUID for collision prevention
   - Extension whitelist validation

4. **Database Security**
   - SQL injection prevention via SQLAlchemy ORM
   - Parameterized queries
   - Input validation on all endpoints

5. **Location Privacy**
   - Coordinates stored but user location not exposed by default
   - Distance calculations use Haversine formula
   - Can be enhanced with geofencing

---

## 📄 License

This project is part of the Souk'Jam platform. All rights reserved.

---

## 👥 Team & Support

For issues, feature requests, or contributions, please contact the development team.

**Last Updated:** 2024
**Version:** 1.0.0