# Souk’Jam , Musical Instrument Rental & Jam Matching Platform

Souk’Jam is a full-stack web platform designed to help musicians rent musical instruments and find compatible jam partners based on musical preferences, skills, and geographic proximity.

The project was developed as part of the Web Services course and demonstrates the design and implementation of a RESTful API, secure authentication, geolocation services, and a similarity-based matching algorithm.

---

## Project Motivation

Finding musicians to jam with spontaneously and accessing musical instruments when needed are recurring challenges for musicians.

Souk’Jam addresses these problems by combining:
- A peer-to-peer musical instrument rental system
- A musician discovery and matching feature
- A structured price negotiation workflow
- Geolocation-based search and matching

A preliminary survey conducted via Google Forms (approximately 20 respondents including musicians, non-musicians, instrument owners, and enthusiasts) showed:
- 70% willingness to rent musical instruments
- 90% openness to participating in jam sessions

---

## Architecture Overview

- Frontend: React + Vite
- Backend: Python Flask (REST API)
- Database: SQLite (development), PostgreSQL (production)
- Authentication: JWT (JSON Web Tokens)
- API Documentation: Swagger UI
- Geolocation: Nominatim API + Haversine formula

---

## Project Structure

├── app/ # Backend (Flask)
│ ├── models/ # SQLAlchemy models
│ ├── routes/ # API endpoints
│ ├── services/ # Business logic (matching, distance, etc.)
│ ├── extensions.py
│ └── config.py
├── frontend/ # React + Vite frontend
│ ├── src/
│ │ ├── components/
│ │ └── api.js
│ └── package.json
├── migrations/ # Alembic migrations
├── tests/ # Unit and integration tests
├── uploads/ # Uploaded images
└── README.md

## Authentication and Authorization

- JWT-based stateless authentication
- Secure password hashing
- Unique email constraint
- Role-based access control (owner, renter, jammer)
- All authorization logic enforced on the backend

### Authentication Flow
POST /auth/register
POST /auth/login → returns JWT token
Authorization: Bearer <token>


---

## API Endpoints Summary

This is a high-level overview of the most important endpoints.  
The full API contains more than 25 endpoints and is fully documented in Swagger UI.

### Authentication (`/auth`)
- POST /auth/register
- POST /auth/login
- GET /auth/profile

### Instruments (`/instruments`)
- GET /instruments (filters, sorting, pagination)
- POST /instruments (owner only)
- GET /instruments/{id}
- PATCH /instruments/{id}
- DELETE /instruments/{id}

### Rentals (`/rentals`)
- POST /rentals
- GET /rentals
- PATCH /rentals/{id}/counter-offer
- PATCH /rentals/{id}/accept
- PATCH /rentals/{id}/reject

### Jam Matching (`/jam`)
- POST /jam/discover
- POST /jam/request
- GET /jam/matches

---

## Musician Matching Algorithm

The matching logic is implemented in `jam_similarity.py`.

- User coordinates are resolved using the Nominatim geocoding service
- Distance is calculated using the Haversine formula
- Musicians are ranked by descending compatibility score

---

## Rental Negotiation Workflow

1. A renter creates a rental request for an instrument
2. The owner can accept, reject, or send a counter-offer
3. A negotiated price may be proposed and revised
4. The rental is either confirmed or cancelled

Statuses are tracked using:
- `status`: pending, confirmed, cancelled, completed
- `owner_response`: pending, accepted, rejected, counter_offer

---

## Testing and Quality Assurance

- Unit tests for business logic
- Integration tests for API endpoints
- Manual API testing using Insomnia
- Frontend tested through real API interaction
- REST-compliant error handling with descriptive messages

---

## Tools Used

- Visual Studio Code (integrated terminal and debugging)
- GitHub (version control)
- Insomnia (manual API testing)
- Swagger UI (interactive API documentation)
- Docker (containerization)
- ClickUp (project management)
- Eraser (architecture and data diagrams)
- Figma (UI/UX design)

---

## Running the Project Locally

### Backend

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
flask run
cd frontend
npm install
npm run dev


