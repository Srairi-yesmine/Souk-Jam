# User Role Setup for Souk'Jam

## Overview

Souk'Jam uses role-based access control to manage user capabilities:

- **owner**: Can create and manage instrument listings for rent
- **renter**: Can browse and rent instruments from owners
- **jammer**: Can discover and connect with musicians to jam together

## Current Setup Issue

By default, newly created users are assigned the **'jammer'** role. To create instrument listings, a user must have the **'owner'** role.

## How to Set User Roles

### Option 1: Using the Setup Script

1. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

2. Run the setup script:
   ```bash
   python setup_user_roles.py
   ```

This script will display all users and set the first user to the 'owner' role.

### Option 2: Direct Database Access

```python
from app import create_app
from app.models import User
from app.extensions import db

app = create_app()
with app.app_context():
    user = User.query.filter_by(email='your-email@example.com').first()
    if user:
        user.role = 'owner'
        db.session.commit()
        print(f"User role updated to: {user.role}")
```

### Option 3: Through Future UI

Once an admin panel is implemented, users can select their role(s) during signup or profile settings.

## Testing the Add Instrument Feature

1. Ensure your user account has the 'owner' role
2. Log in to the application
3. Navigate to the "Add" page
4. Fill in the instrument details (name, brand, type, price, location)
5. Optionally upload a photo
6. Click "Create Instrument"

## Error Messages

If you see the error "Only owners can create instruments", it means:
- Your user account doesn't have the 'owner' role
- Follow the setup instructions above to update your role

## Future Enhancements

- [ ] Admin panel for user role management
- [ ] Role selection during user registration
- [ ] Profile settings to change roles
- [ ] Verification system for owners
