#!/usr/bin/env python
"""
Setup script to initialize user roles for testing.
This script helps set up users with the correct roles (owner, renter, jammer).
"""

from app import create_app
from app.models import User
from app.extensions import db

def main():
    app = create_app()
    with app.app_context():
        print("=" * 60)
        print("Souk'Jam User Role Setup")
        print("=" * 60)
        
        # Get all users
        users = User.query.all()
        
        if not users:
            print("\nNo users found in database.")
            return
        
        print(f"\nFound {len(users)} user(s):\n")
        for user in users:
            print(f"ID: {user.id}")
            print(f"  Email: {user.email}")
            print(f"  Name: {user.name}")
            print(f"  Current Role: {user.role}")
            print()
        
        # Set roles for testing
        print("\nSetting up roles for testing...")
        
        # First user (ahmed.ben ali1) - make owner
        user = User.query.filter_by(id=1).first()
        if user:
            user.role = 'owner'
            print(f"✓ User '{user.email}' role set to 'owner'")
        
        db.session.commit()
        print("\n✓ Roles updated successfully!")
        print("\nNote: Only 'owner' role users can create instruments.")
        print("Users with 'jammer' role can only join jam sessions.")
        print("Users with 'renter' role can rent instruments.")

if __name__ == '__main__':
    main()
