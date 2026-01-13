# 📸 Profile Photo Feature - User Guide

## ✅ Feature Added

Users can now upload and manage their profile photos. The feature includes:
- Upload profile photos (PNG, JPG, JPEG, GIF)
- Update existing profile photos
- Own-profile-only permissions (users can only update their own photo)
- Secure file storage with UUID naming to prevent conflicts

---

## Endpoint

### Upload/Update Profile Photo
```
PUT /auth/users/<user_id>/profile-photo
```

**Authorization:** Required (JWT token)
**Content-Type:** multipart/form-data
**Permission:** Users can only update their own profile photo

---

## How to Use

### 1. Get JWT Token First

```bash
TOKEN=$(curl -s -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "ahmed.ben ali1@example.com", "password": "password123"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Token: $TOKEN"
```

### 2. Upload Profile Photo (Using curl)

```bash
curl -X PUT http://localhost:5000/auth/users/1/profile-photo \
  -H "Authorization: Bearer $TOKEN" \
  -F "profile_photo=@/path/to/your/photo.jpg"
```

**Supported File Types:**
- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)

---

## Testing in Insomnia

### 1. Setup Login Request
- **Method:** POST
- **URL:** `http://localhost:5000/auth/login`
- **Body (JSON):**
  ```json
  {
    "email": "ahmed.ben ali1@example.com",
    "password": "password123"
  }
  ```
- **Response:** Copy the `access_token`

### 2. Create Profile Photo Upload Request
- **Method:** PUT
- **URL:** `http://localhost:5000/auth/users/1/profile-photo`
- **Headers:**
  - Key: `Authorization`
  - Value: `Bearer <your_token>`
- **Body:** 
  - Type: **form-data**
  - Key: `profile_photo`
  - Value: Select a file (image)
  - Type: File

### 3. Send Request
- Click **Send**
- Expected Response: 200 OK with updated user object including `profile_photo_url`

---

## Response Example

**Success Response (200 OK):**
```json
{
  "id": 1,
  "email": "ahmed.ben ali1@example.com",
  "name": "Ahmed Ben Ali",
  "location_name": "Ariana, Tunisia",
  "location_lat": 36.8625,
  "location_lng": 10.1939,
  "profile_photo_url": "/uploads/a1b2c3d4-e5f6_photo.jpg",
  "role": "owner",
  "genres_enjoyed": ["rock", "jazz"],
  "instruments_played": [],
  "instruments_owned": ["guitar", "drums"],
  "is_active_for_jam": false
}
```

---

## Error Responses

### 400 - No file provided
```json
{
  "message": "No file provided. Use \"profile_photo\" field in form data"
}
```

### 400 - Invalid file type
```json
{
  "message": "Invalid file type. Allowed: PNG, JPG, JPEG, GIF"
}
```

### 401 - Unauthorized (wrong user)
```json
{
  "message": "You can only update your own profile photo"
}
```

### 404 - User not found
```json
{
  "message": "404 Not Found"
}
```

---

## Technical Details

### File Storage
- **Location:** `/uploads/` directory
- **Filename:** UUID-based (e.g., `a1b2c3d4-e5f6_original-name.jpg`)
- **Why UUID:** Prevents filename conflicts and prevents users from accessing other files

### Security Features
- File type validation (only images allowed)
- Secure filename sanitization
- JWT authentication required
- User can only update their own photo
- Maximum file size: Configurable (default unlimited at Flask level)

### Database
- **Table:** users
- **Column:** profile_photo_url (String, nullable)
- **Type:** Stores relative URL path to the uploaded file

---

## Integration with Other Features

### Get User Profile
You can retrieve the profile photo URL by getting user details:

```bash
curl http://localhost:5000/auth/users/1 \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

The response will include:
```json
{
  "profile_photo_url": "/uploads/a1b2c3d4-e5f6_photo.jpg"
}
```

### Access the Photo
The photo can be accessed directly via HTTP:
```
http://localhost:5000/uploads/a1b2c3d4-e5f6_photo.jpg
```

---

## Python Example

```python
import requests
from requests.auth import HTTPBearerAuth

# Login
login_resp = requests.post(
    'http://localhost:5000/auth/login',
    json={'email': 'ahmed.ben ali1@example.com', 'password': 'password123'}
)
token = login_resp.json()['access_token']

# Upload profile photo
with open('my_photo.jpg', 'rb') as f:
    files = {'profile_photo': f}
    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.put(
        'http://localhost:5000/auth/users/1/profile-photo',
        files=files,
        headers=headers
    )
    print(resp.json())
```

---

## Database Schema

```sql
-- users table (updated)
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    name VARCHAR(100) NOT NULL,
    location_name VARCHAR(255),
    location_lat FLOAT,
    location_lng FLOAT,
    profile_photo_url VARCHAR(255),  -- NEW COLUMN
    role VARCHAR(20) NOT NULL,
    genres_enjoyed JSON,
    instruments_played JSON,
    instruments_owned JSON,
    is_active_for_jam BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## Migration Info

- **Revision:** add_profile_photo
- **File:** `/migrations/versions/add_profile_photo_to_users.py`
- **Status:** ✅ Applied
- **Changes:**
  - Added `profile_photo_url` VARCHAR(255) NULL column to users table

---

## What's Next?

The profile photo feature is ready for:
- ✅ User profile management
- ✅ Displaying user avatars in jam sessions
- ✅ Owner verification with photo
- ✅ Rental request trust signals

Consider adding:
- Photo crop/resize on upload
- Multiple photo support
- Photo deletion endpoint
- Photo verification/approval workflow
