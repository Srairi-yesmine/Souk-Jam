# Souk'Jam - Project Development Guide

## 📚 Executive Summary

**Souk'Jam** is a full-stack web platform designed to connect musicians for jam sessions and facilitate musical instrument rentals in Tunisia. The platform enables users to discover compatible musicians, negotiate rental prices, and build a musical community.

**Platform Type:** Social Matching + Rental Marketplace  
**Primary Users:** Musicians, instrument owners, and renters  
**Key Technologies:** Flask (Backend), React + Vite (Frontend), PostgreSQL (Database)  
**Deployment:** Docker-ready with Flask + SQLAlchemy

---

## 🎯 Project Objectives

### Primary Goals
1. **Musician Discovery:** Help musicians find compatible jam session partners
2. **Instrument Rentals:** Enable affordable access to musical instruments
3. **Community Building:** Create a vibrant Tunisian music community
4. **Price Negotiation:** Implement dynamic rental pricing with counter-offers

### Success Metrics
- User registrations and active participants
- Successful jam matches (mutual requests)
- Completed rentals and revenue
- User engagement (searches, requests)

---

## 🏗️ Architecture Overview

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + Vite | Modern, fast UI with component-based architecture |
| **UI Framework** | CSS Modules | Scoped styling, custom design system |
| **State Management** | React Hooks | Local state with context API |
| **API Client** | Fetch API | RESTful API communication |
| **Backend** | Flask 2.x | Lightweight Python web framework |
| **ORM** | SQLAlchemy | Database abstraction and relationships |
| **Auth** | JWT (Flask-JWT-Extended) | Token-based authentication |
| **Database** | SQLite/PostgreSQL | Relational data storage |
| **File Storage** | Local filesystem | Profile/instrument photos |
| **Geocoding** | External API | Location → coordinates conversion |

### Project Structure

```
Souk'Jam/
├── frontend/                      # React + Vite web application
│   ├── src/
│   │   ├── components/           # Reusable UI components
│   │   │   ├── Navigation.jsx    # Top navigation bar
│   │   │   ├── Auth.jsx          # Login/register forms
│   │   │   ├── InstrumentBrowser.jsx
│   │   │   ├── InstrumentCard.jsx
│   │   │   ├── InstrumentCreate.jsx
│   │   │   ├── JamDiscovery.jsx
│   │   │   ├── RentalManager.jsx
│   │   │   ├── Profile.jsx
│   │   │   └── *.module.css      # Component-scoped styles
│   │   ├── pages/                # Full-page components
│   │   ├── utils/                # Helper functions
│   │   │   └── imageUrl.js       # Image URL resolution
│   │   ├── api.js                # API wrapper (jamAPI, instrumentsAPI, rentalsAPI)
│   │   ├── App.jsx               # Main app layout with routing
│   │   └── App.module.css        # Global + hero styles
│   ├── index.css                 # Global CSS + brand color variables
│   ├── package.json              # Frontend dependencies
│   └── vite.config.js            # Vite build config
│
├── app/                          # Flask backend application
│   ├── __init__.py              # Flask app factory (create_app)
│   ├── config.py                # Configuration (dev, test, prod)
│   ├── extensions.py            # Global extensions (db, jwt, api)
│   │
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py              # User model + password methods
│   │   ├── instrument.py        # Instrument rental listing
│   │   ├── rental.py            # Rental transaction
│   │   └── jam.py               # Jam request/matching
│   │
│   ├── routes/                  # API endpoints (Flask-RESTX)
│   │   ├── instruments.py       # GET/POST instruments, search, filters
│   │   ├── jam.py               # Discover, request, skip, matches
│   │   └── rental.py            # Rental CRUD + negotiation
│   │
│   ├── auth/
│   │   └── routes.py            # Register, login, profile endpoints
│   │
│   ├── schemas/                 # Marshmallow serialization
│   │   ├── __init__.py
│   │   ├── user.py              # User serialization + validation
│   │   ├── instrument.py        # Instrument serialization
│   │   ├── rental.py            # Rental serialization
│   │   └── search.py            # Search parameter schema
│   │
│   └── services/                # Business logic
│       ├── geocoding.py         # Location → lat/lng conversion
│       ├── jam_similarity.py    # Musician compatibility scoring
│       └── storage.py           # File upload handling
│
├── migrations/                   # Alembic database migrations
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
│       ├── *_initial_migration.py
│       └── *_jam_fields_migration.py
│
├── tests/
│   └── test_app.py             # Unit and integration tests
│
├── uploads/                      # File storage for photos
│
├── requirements.txt             # Python dependencies
├── seed.py                      # Database seeding script
├── Dockerfile                   # Docker container definition
├── docker-compose.yml           # Multi-container orchestration
├── CLASS_DIAGRAM_DEV.md        # Detailed class diagram
├── PROJECT_GUIDE.md            # This file
└── README.md                    # Quick start guide

```

---

## 📊 Core Features & User Flows

### Feature 1: User Authentication & Profiles

**Endpoints:**
- `POST /auth/register` - Create new account
- `POST /auth/login` - Authenticate and receive JWT token
- `GET /auth/profile` - Fetch current user profile
- `PUT /auth/profile` - Update profile (name, location, preferences)
- `POST /auth/upload-photo` - Upload profile photo

**User Types:**
- **Jammer** (musician): Participates in jam sessions (DEFAULT role)
- **Owner**: Owns instruments for rental
- **Renter**: Rents instruments from owners

**Profile Data:**
- Musical genres enjoyed (rock, jazz, classical, oriental, etc.)
- Instruments played with skill levels
- Location (auto-geocoded to lat/lng)
- Profile photo

---

### Feature 2: Instrument Rental Marketplace

**Endpoints:**
- `GET /instruments/` - Search & browse with filters
- `POST /instruments/` - Create listing (owners only)
- `PUT /instruments/{id}` - Edit listing
- `DELETE /instruments/{id}` - Remove listing
- `POST /instruments/{id}/upload-photo` - Add instrument photo

**Search Filters:**
- Name/brand search
- Instrument type (guitar, drums, piano, etc.)
- Price range (min/max per day)
- Location & proximity radius
- Tags (custom keywords)
- Sorting (price, date, distance)

**Listing Data:**
- Name, brand, type, description
- Daily rental price (in TND)
- Status (available, rented, unavailable)
- Location + GPS coordinates
- Photo + tags
- Owner details

---

### Feature 3: Rental Negotiation

**Flow:**
1. Renter selects dates and instrument → Creates rental request
2. Owner receives notification
3. Owner can:
   - **Accept** → Rental confirmed, both notified
   - **Reject** → Rental cancelled
   - **Counter-offer** → Suggests different price
4. If counter: Renter can accept new price or reject
5. Once confirmed: Rental is active until end date
6. After completion: Both can rate/review

**Data:**
- Start/end dates
- Total price (calculated) + negotiated price
- Status progression: pending → confirmed → completed/cancelled
- Owner response: pending/accepted/rejected/counter_offer
- Comment field for notes

---

### Feature 4: Jam Discovery & Matching

**Endpoints:**
- `GET /jam/discover` - Find compatible musicians
- `POST /jam/request/{user_id}` - Send jam request
- `POST /jam/skip/{user_id}` - Skip user (won't show again)
- `GET /jam/matches` - Get mutual matches

**Matching Algorithm (Similarity Scoring):**
1. **Genre Overlap** - Weighted score based on shared music genres
2. **Instrument Overlap** - Shared instruments played
3. **Skill Level Compatibility** - Similar experience levels
4. **Geographic Proximity** - Users within reasonable distance
5. **Availability** - User marked as "active for jam"

**Matching States:**
- `pending` - Request sent, awaiting response
- `accepted` - Recipient accepted jam session
- `rejected` - Recipient declined
- `skipped` - Sender skipped this user
- **Mutual Match** - Both sent requests (auto-detected)

---

## 🔐 Authentication & Security

### JWT Token Flow

```
1. User submits credentials → POST /auth/login
2. Backend validates & generates JWT token
3. Frontend stores token in memory (volatile)
4. All subsequent requests include Authorization header:
   Authorization: Bearer <jwt_token>
5. Backend verifies token with @jwt_required() decorator
6. Logout: Clear token from frontend (no server-side revocation)
```

### Protected Endpoints

All endpoints except auth require valid JWT:
```python
@jwt_required()
def protected_route():
    current_user_id = int(get_jwt_identity())
    # Use user_id for authorization checks
```

### Password Handling

- Passwords hashed with bcrypt (werkzeug.security)
- Never stored in plaintext
- Never returned in API responses
- Validation on registration (min 6 chars recommended)

---

## 💾 Database Design

### Core Tables

#### **users**
- Credentials (email, password_hash)
- Profile (name, location, photo)
- Preferences (genres_enjoyed, instruments_played)
- Roles & flags (role, is_active_for_jam)
- Timestamps (created_at)

#### **instruments**
- Listing details (name, brand, type, description)
- Pricing & availability (price_per_day, status)
- Location (name, lat, lng)
- Media (photo_url)
- Tags (JSON array)

#### **rentals**
- Transaction data (instrument_id, renter_id, start_date, end_date)
- Pricing (total_price, negotiated_price)
- Status (rental_status, owner_response)
- Communication (comment field)

#### **jam_requests**
- Participants (sender_id, receiver_id)
- Status tracking
- Timestamps

### Relationships

```
User (1) ──owns──→ (N) Instrument
User (1) ──makes──→ (N) Rental (as renter)
Instrument (1) ──has──→ (N) Rental
User (1) ──sends──→ (N) JamRequest (as sender)
User (1) ──receives──→ (N) JamRequest (as receiver)
```

---

## 🎨 Frontend Design System

### Color Palette

```css
:root {
  --brand-green: #7ed957;      /* Primary accent color */
  --brand-purple: #5500ff;     /* Secondary/action color (prices, send buttons) */
  --text-primary: #333;        /* Main text */
  --bg-white: #ffffff;         /* Card/modal backgrounds */
  --bg-light: #f5f5f5;         /* Light backgrounds */
  --border-light: #e0e0e0;     /* Subtle borders */
}
```

### Typography

- **Font:** Poppins (primary), Urbanist (fallback)
- **Weights:** 300 (light), 400 (regular), 600 (bold), 700 (extra bold), 800 (black)
- **Hierarchy:**
  - H1: 56px, weight 800 (hero title)
  - H2: 32px, weight 700 (section headers)
  - H3: 24px, weight 600 (card titles)
  - Body: 14-16px, weight 400

### Component Patterns

- **Cards:** White bg, subtle shadow, hover lift effect
- **Buttons:**
  - Green gradient for primary actions (rent, add, accept)
  - Purple solid for send/request actions
  - Outline for secondary actions
- **Forms:** Light gray inputs, green focus borders
- **Navigation:** Fixed top, transparent over hero, opaque on scroll
- **Hero:** Full-viewport image background with text overlay

---

## 🚀 Deployment & Running

### Development Mode

**Backend:**
```bash
cd /Users/srairi/Desktop/Souk'Jam
source .venv/bin/activate
python -m flask run  # Default: http://localhost:5000
```

**Frontend:**
```bash
cd /Users/srairi/Desktop/Souk'Jam/frontend
npm run dev  # Default: http://localhost:5173 (or 3003)
```

**Database:**
- SQLite (dev): `instance/app.db`
- Run migrations: `flask db upgrade`
- Seed sample data: `python seed.py`

### Production Deployment

**Docker Compose:**
```bash
docker-compose up --build
# Services: Flask (port 5000) + Frontend (port 3000)
```

**Environment Variables:**
```
FLASK_ENV=production
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=<random-secret>
UPLOAD_FOLDER=/uploads
```

---

## 🧪 Testing

### Running Tests

```bash
pytest tests/
pytest tests/test_app.py::test_user_register
pytest --cov=app  # Coverage report
```

### Test Coverage

- User authentication (register, login, profile)
- Instrument CRUD operations
- Rental negotiation flow
- Jam discovery & matching
- Search & filtering

---

## 📝 Code Conventions

### Python (Backend)

```python
# Models: CamelCase, inherit db.Model
class User(db.Model):
    # Attributes: snake_case
    first_name = db.Column(db.String(50))
    # Relationships: descriptive names
    instruments = db.relationship('Instrument', backref='owner')
    
    def method_name(self):
        """Clear docstring explaining behavior"""
        pass

# Routes: RESTful, use Flask-RESTX namespaces
@instruments_ns.route('/')
class InstrumentList(Resource):
    @jwt_required()
    def post(self):
        """Create instrument"""
        pass

# Services: Static methods for utility logic
class JamSimilarityService:
    @staticmethod
    def calculate_similarity_score(user1, user2):
        pass
```

### JavaScript (Frontend)

```javascript
// Components: PascalCase, functional components
export default function InstrumentCard({ instrument, onRent }) {
  return <div>...</div>
}

// Hooks: camelCase
const [instruments, setInstruments] = useState([])

// API calls: Group in api.js
const instrumentsAPI = {
  list: () => api.get('/instruments/'),
  create: (data) => api.post('/instruments/', data)
}

// Styling: CSS Modules for scoping
import styles from './Component.module.css'
// Usage: className={styles.containerClass}
```

---

## 🔍 Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "Cannot find module" | Missing package | `npm install` or `pip install -r requirements.txt` |
| CORS errors | Backend not running | Start Flask with `flask run` |
| Images not loading | Wrong image URL | Check imageUrl.js, ensure `/uploads` path |
| JWT errors | Token expired/invalid | Re-login, check token expiry config |
| Database locked | Migration conflict | Reset: `rm instance/app.db && flask db upgrade` |

---

## 📚 API Documentation

### Base URL
- Development: `http://localhost:5000`
- Production: `https://soukjam.com` (when deployed)

### Authentication

```
Header: Authorization: Bearer <jwt_token>
Token lifetime: 24 hours (configurable)
```

### Response Format

```json
{
  "data": {...},
  "message": "Success",
  "status": 200
}
```

### Error Handling

```json
{
  "message": "Error description",
  "status": 400
}
```

### Endpoint Categories

1. **Auth Routes** (`/auth/`)
   - register, login, profile, upload-photo

2. **Instruments** (`/instruments/`)
   - List, create, update, delete, search, upload-photo

3. **Jam Discovery** (`/jam/`)
   - discover, request, skip, matches

4. **Rentals** (`/rentals/`)
   - List, create, counter-offer, accept, reject, complete

---

## 🎓 Learning Resources

### Architecture Concepts

- **MVC Pattern:** Models (User, Instrument), Views (React components), Controllers (routes)
- **JWT Authentication:** Stateless token-based auth
- **RESTful APIs:** Resource-based URLs, standard HTTP methods
- **Component Architecture:** Reusable, composable UI elements

### Related Technologies

- **Flask:** Lightweight Python web framework
- **SQLAlchemy:** Python ORM for database
- **React:** JavaScript UI library with hooks
- **CSS Modules:** Local scope CSS for components
- **Vite:** Fast build tool for React

---

## 📋 Development Roadmap

### MVP (Current)
- ✅ User auth & profiles
- ✅ Instrument rental marketplace
- ✅ Jam discovery & matching
- ✅ Rental negotiation

### Phase 2 (Planned)
- Reviews & ratings
- Payment integration
- Messaging system
- Calendar integration
- Mobile app

### Phase 3 (Future)
- AI-powered matching
- Community events
- Live jam sessions
- Music lessons marketplace

---

## 🤝 Contributing

### Code Review Checklist

- [ ] Code follows conventions (naming, structure)
- [ ] Database migrations included
- [ ] API endpoints documented
- [ ] Frontend components tested
- [ ] Error handling implemented
- [ ] No console errors/warnings
- [ ] Responsive design verified

### Commit Message Format

```
[feature|fix|refactor|docs] Brief description

- Detailed change 1
- Detailed change 2
```

---

## 📞 Support & Contact

**Project Manager:** Souk'Jam Team  
**Repository:** https://github.com/Srairi-yesmine/Souk-Jam  
**Branch:** main (development)

---

## 📄 Documentation Files

- **README.md** - Quick start guide
- **CLASS_DIAGRAM_DEV.md** - Detailed class diagrams & relationships
- **PROJECT_GUIDE.md** - This comprehensive guide
- **PROFILE_PHOTO_GUIDE.md** - Photo upload specifications
- **TEST_SORTING.md** - Search sorting documentation
- **TEST_URLS.md** - API endpoint testing reference

---

**Last Updated:** January 13, 2026  
**Version:** 1.0 - Project Overview & Development Guide  
**Scope:** Full-stack Souk'Jam Platform

