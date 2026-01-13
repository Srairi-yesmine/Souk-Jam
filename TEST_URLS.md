# 📋 Complete API Endpoints Documentation

## 🔐 Authentication Endpoints

### Register New User
```
POST http://localhost:5000/auth/register
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password": "SecurePass123!",
  "name": "John Musician",
  "location_name": "Tunis, Tunisia",
  "role": "jammer",
  "genres_enjoyed": ["rock", "jazz"],
  "instruments_played": [{"instrument_type": "guitar", "skill_level": "intermediate"}],
  "instruments_owned": ["guitar"],
  "is_active_for_jam": true
}
```

### Check if Email Exists
```
POST http://localhost:5000/auth/check-email
Content-Type: application/json

{
  "email": "user@example.com"
}
```
**Response:** `{"email": "user@example.com", "exists": true/false}`

### Login
```
POST http://localhost:5000/auth/login
Content-Type: application/json

{
  "email": "ahmed.ben ali1@example.com",
  "password": "password123"
}
```
**Response:** Returns `access_token` to use in Authorization header

### Change Password
```
POST http://localhost:5000/auth/users/{user_id}/change-password
Authorization: Bearer {TOKEN}
Content-Type: application/json

{
  "old_password": "password123",
  "new_password": "NewSecurePass123!"
}
```
**Note:** User can only change their own password

### Get All Users
```
GET http://localhost:5000/auth/users
Authorization: Bearer {TOKEN}
```

### Get User Details
```
GET http://localhost:5000/auth/users/{user_id}
Authorization: Bearer {TOKEN}
```

### Upload Profile Photo
```
PUT http://localhost:5000/auth/users/{user_id}/profile-photo
Authorization: Bearer {TOKEN}
Content-Type: multipart/form-data

Field: profile_photo (file)
Supported formats: PNG, JPG, JPEG, GIF
```

---

## 🎸 Instrument Endpoints

### Get All Instruments (with sorting & filtering)
```
GET http://localhost:5000/instruments/?sort_by=price_per_day&sort_order=desc&limit=10
Authorization: Bearer {TOKEN}
```

**Query Parameters:**
- `sort_by`: distance | price | price_per_day | newest | location | owner | owner_id
- `sort_order`: asc | desc
- `limit`: number of results (default 20)
- `type`: filter by instrument type
- `price_min`: minimum price
- `price_max`: maximum price
- `radius_km`: search radius in km
- `owner_id`: filter by owner ID
- `status`: available | rented | unavailable

**Examples:**

Price Sorting (Highest First):
```
GET http://localhost:5000/instruments/?sort_by=price_per_day&sort_order=desc&limit=5
Authorization: Bearer {TOKEN}
```

Price Sorting (Lowest First):
```
GET http://localhost:5000/instruments/?sort_by=price_per_day&sort_order=asc&limit=5
Authorization: Bearer {TOKEN}
```

Newest Instruments First (Default Sorting):
```
GET http://localhost:5000/instruments/?sort_by=newest&sort_order=desc&limit=10
Authorization: Bearer {TOKEN}
```

By Owner ID (Ascending):
```
GET http://localhost:5000/instruments/?sort_by=owner_id&sort_order=asc&limit=10
Authorization: Bearer {TOKEN}
```

By Owner ID (Descending):
```
GET http://localhost:5000/instruments/?sort_by=owner_id&sort_order=desc&limit=10
Authorization: Bearer {TOKEN}
```

By Distance (From User Location):
```
GET http://localhost:5000/instruments/?sort_by=distance&sort_order=asc&limit=5
Authorization: Bearer {TOKEN}
```

### Get Instrument Details
```
GET http://localhost:5000/instruments/{instrument_id}
Authorization: Bearer {TOKEN}
```

### Create Instrument Listing
```
POST http://localhost:5000/instruments/
Authorization: Bearer {TOKEN}
Content-Type: multipart/form-data

Fields:
- name: Instrument name (required)
- brand: Brand name
- type: Instrument type (required)
- description: Description
- price_per_day: Rental price per day (required)
- location_name: Location name
- photo: Image file (optional)
- tags: JSON array of tags
```

### Update Instrument
```
PUT http://localhost:5000/instruments/{instrument_id}
Authorization: Bearer {TOKEN}
Content-Type: application/json

{
  "name": "Updated Name",
  "price_per_day": 75.00
}
```

### Delete Instrument
```
DELETE http://localhost:5000/instruments/{instrument_id}
Authorization: Bearer {TOKEN}
```

---

## 💰 Rental Endpoints

### Create Rental Request
```
POST http://localhost:5000/rentals/
Authorization: Bearer {TOKEN}
Content-Type: application/json

{
  "instrument_id": 1,
  "start_date": "2026-02-01",
  "end_date": "2026-02-05",
  "comment": "I would like to rent this for a performance"
}
```

**Important:**
- Total price is automatically calculated: `(end_date - start_date) * instrument.price_per_day`
- Cannot rent for dates that have already passed
- Owner cannot rent their own instrument
- Both dates must be in the future

**Response:** Returns rental object with status `pending` and `owner_response: pending`

### Get User's Rentals
```
GET http://localhost:5000/rentals/
Authorization: Bearer {TOKEN}
```

**Query Parameters:**
- `status`: pending | confirmed | completed | cancelled
- `owner_response`: pending | accepted | rejected | counter_offer
- `limit`: number of results (default 20)

**Important:** Each user only sees their own rentals (where they are either renter or instrument owner)

**Examples:**

Get Pending Rentals:
```
GET http://localhost:5000/rentals/?owner_response=pending&limit=10
Authorization: Bearer {TOKEN}
```

Get Confirmed Rentals:
```
GET http://localhost:5000/rentals/?status=confirmed&limit=10
Authorization: Bearer {TOKEN}
```

### Get Rental Details
```
GET http://localhost:5000/rentals/{rental_id}
Authorization: Bearer {TOKEN}
```

### Send Counter-Offer (Renter only)
Renter suggests different price (owner can accept, reject, or negotiate)

```
PATCH http://localhost:5000/rentals/{rental_id}/counter-offer
Authorization: Bearer {RENTER_TOKEN}
Content-Type: application/json

{
  "negotiated_price": 75.0
}
```

**Response:** Returns rental with `owner_response: "counter_offer"` and `negotiated_price: 75.0`

### Accept Rental Request (Owner only)
Owner accepts the rental at current or negotiated price

```
PATCH http://localhost:5000/rentals/{rental_id}/accept
Authorization: Bearer {OWNER_TOKEN}
Content-Type: application/json

{}
```

**Response:** Returns rental with `status: "confirmed"` and `owner_response: "accepted"`
- If `negotiated_price` exists (from renter counter-offer), uses that as `total_price`
- Otherwise uses original `total_price`

### Reject Rental Request (Owner only)
Owner rejects the rental request

```
PATCH http://localhost:5000/rentals/{rental_id}/reject
Authorization: Bearer {OWNER_TOKEN}
Content-Type: application/json

{}
```

**Response:** Returns rental with `status: "cancelled"` and `owner_response: "rejected"`

---

## 🎵 Jam Endpoints

### Discover Compatible Musicians
```
GET http://localhost:5000/jam/discover
Authorization: Bearer {TOKEN}
```

**Features:**
- Finds users who are musically compatible based on genres and instruments
- Role-based matching (jammers with other musicians)
- Returns users sorted by compatibility score
- Includes similarity scoring (0-100)

**Response Example:**
```json
[
  {
    "id": 5,
    "name": "Ahmed Ben Ali",
    "location_name": "Tunis, Tunisia",
    "role": "owner",
    "genres_enjoyed": ["rock", "jazz"],
    "instruments_played": [{"instrument_type": "guitar", "skill_level": "advanced"}],
    "similarity_score": 85.5
  }
]
```

### Send Jam Request
```
POST http://localhost:5000/jam/request/{user_id}
Authorization: Bearer {TOKEN}
```

**Response:** `{"message": "Jam request sent"}` (201)

**Important:** If both users send requests to each other, they become mutual matches

### Skip User in Discovery
```
POST http://localhost:5000/jam/skip/{user_id}
Authorization: Bearer {TOKEN}
```

**Response:** `{"message": "User skipped"}` (200)

**Note:** Skipped users won't appear in future discovery results

### Get Mutual Jam Matches
```
GET http://localhost:5000/jam/matches
Authorization: Bearer {TOKEN}
```

**Returns:** Users who have sent jam requests to you AND you've sent requests back to them

---

## 🧪 Complete Test Workflow

### Step 1: Check Email Availability
```bash
curl -X POST http://localhost:5000/auth/check-email \
  -H "Content-Type: application/json" \
  -d '{"email": "newuser@example.com"}' | python -m json.tool
```

### Step 2: Register New User
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPass123!",
    "name": "Test User",
    "location_name": "Tunis, Tunisia",
    "role": "jammer",
    "genres_enjoyed": ["rock", "jazz"],
    "instruments_played": [{"instrument_type": "guitar", "skill_level": "intermediate"}],
    "is_active_for_jam": true
  }' | python -m json.tool
```

### Step 3: Login
```bash
TOKEN=$(curl -s -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "ahmed.ben ali1@example.com", "password": "password123"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Token: $TOKEN"
```

### Step 4: Browse Instruments (Sorted by Newest)
```bash
curl http://localhost:5000/instruments/?sort_by=newest&sort_order=desc&limit=5 \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

### Step 5: Create Rental Request
```bash
curl -X POST http://localhost:5000/rentals/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "instrument_id": 1,
    "start_date": "2026-02-01",
    "end_date": "2026-02-05",
    "comment": "Need this for a gig"
  }' | python -m json.tool
```

### Step 6: Renter Sends Counter-Offer
```bash
curl -X PATCH http://localhost:5000/rentals/1/counter-offer \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"negotiated_price": 75.0}' | python -m json.tool
```

### Step 7: Owner Accepts Counter-Offer
```bash
OWNER_TOKEN=$(curl -s -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "mehdi.khemiri5@example.com", "password": "password123"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

curl -X PATCH http://localhost:5000/rentals/1/accept \
  -H "Authorization: Bearer $OWNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' | python -m json.tool
```

### Step 8: Discover Musicians for Jamming
```bash
curl http://localhost:5000/jam/discover \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

### Step 9: Send Jam Request
```bash
curl -X POST http://localhost:5000/jam/request/5 \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

### Step 10: Get Mutual Jam Matches
```bash
curl http://localhost:5000/jam/matches \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

### Step 11: Change Password
```bash
curl -X POST http://localhost:5000/auth/users/1/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "password123",
    "new_password": "NewSecurePass123!"
  }' | python -m json.tool
```

---

## 📊 Testing in Insomnia/Postman

### Common Test Credentials
```
Email: ahmed.ben ali1@example.com
Password: password123
ID: 1

Email: mehdi.khemiri5@example.com
Password: password123
ID: 20
```

### Headers Required
```
Authorization: Bearer {TOKEN}
Content-Type: application/json (for JSON requests)
Content-Type: multipart/form-data (for file uploads)
```

---

## ✅ All Features Implemented

| Feature | Status | Endpoint |
|---------|--------|----------|
| User Registration | ✅ | POST /auth/register |
| Email Verification | ✅ | POST /auth/check-email |
| User Login | ✅ | POST /auth/login |
| Change Password | ✅ | POST /auth/users/{id}/change-password |
| Profile Photo Upload | ✅ | PUT /auth/users/{id}/profile-photo |
| Get All Users | ✅ | GET /auth/users |
| Get User Details | ✅ | GET /auth/users/{id} |
| Price Sorting DESC | ✅ | GET /instruments/?sort_by=price_per_day&sort_order=desc |
| Price Sorting ASC | ✅ | GET /instruments/?sort_by=price_per_day&sort_order=asc |
| Newest First (Default) | ✅ | GET /instruments/?sort_by=newest&sort_order=desc |
| Owner ID Sorting | ✅ | GET /instruments/?sort_by=owner_id&sort_order=asc/desc |
| Distance Sorting | ✅ | GET /instruments/?sort_by=distance&sort_order=asc |
| Create Instrument | ✅ | POST /instruments/ |
| Get Instruments | ✅ | GET /instruments/ |
| Get Instrument Details | ✅ | GET /instruments/{id} |
| Update Instrument | ✅ | PUT /instruments/{id} |
| Delete Instrument | ✅ | DELETE /instruments/{id} |
| Create Rental | ✅ | POST /rentals/ |
| Auto-Calculate Price | ✅ | POST /rentals/ (price calculated from days*rate) |
| Past Date Prevention | ✅ | POST /rentals/ (cannot rent past dates) |
| Owner Self-Rent Prevention | ✅ | POST /rentals/ (owner cannot rent own instrument) |
| Get User Rentals | ✅ | GET /rentals/ |
| Get Rental Details | ✅ | GET /rentals/{id} |
| Renter Counter-Offer | ✅ | PATCH /rentals/{id}/counter-offer |
| Owner Accept | ✅ | PATCH /rentals/{id}/accept |
| Owner Reject | ✅ | PATCH /rentals/{id}/reject |
| Discover Musicians | ✅ | GET /jam/discover |
| Send Jam Request | ✅ | POST /jam/request/{id} |
| Skip User | ✅ | POST /jam/skip/{id} |
| Get Mutual Matches | ✅ | GET /jam/matches |

---

## 🚀 Architecture Overview

### Price Negotiation Flow (Rental System)
1. **Renter** creates rental request with start/end dates
2. System automatically calculates price: `(end_date - start_date) * instrument.price_per_day`
3. **Renter** can send counter-offer with different price
4. **Owner** can:
   - Accept at original or counter-offer price
   - Reject the rental
   - Send their own counter-offer (negotiation)
5. Once accepted, rental status becomes "confirmed"

### Jam Matching Flow
1. **User A** discovers compatible musicians via `/jam/discover`
2. **User A** sends jam request to **User B** via `/jam/request/{id}`
3. **User B** receives request and can send request back to **User A**
4. When both have pending requests to each other, they appear in `/jam/matches`
5. Mutual matches can now connect for jamming

### Security & Validation
- All rental dates must be in the future
- Owners cannot rent their own instruments
- Email uniqueness verified during registration
- Strong password enforcement (8+ chars, mixed case, numbers, special chars)
- JWT token-based authentication
- User-specific data access (can only see their own rentals)

