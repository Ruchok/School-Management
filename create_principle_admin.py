#!/usr/bin/env python
"""
Script to create a Principle Admin user in the system.
This user will have full access to all admin functionality.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'management.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from users.models import CustomUser

def create_principle_admin():
    """Create principle admin user"""
    username = 'principle_admin'
    email = 'principle@school.edu'
    first_name = 'Principle'
    last_name = 'Admin'
    
    # Check if user already exists
    if CustomUser.objects.filter(username=username).exists():
        print(f"✓ Principle Admin user '{username}' already exists")
        user = CustomUser.objects.get(username=username)
    else:
        # Create the principle admin user
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password='Principle@Admin123',  # Temporary password (uses password-based auth, not this)
            role=CustomUser.Roles.PRINCIPLE_ADMIN
        )
        user.is_staff = True
        user.is_superuser = False
        user.save()
        print(f"✓ Created Principle Admin user: {username}")
        print(f"  Email: {email}")
        print(f"  Role: {CustomUser.Roles.PRINCIPLE_ADMIN}")
    
    # Display login information
    print("\n" + "="*60)
    print("PRINCIPLE ADMIN LOGIN CREDENTIALS")
    print("="*60)
    print(f"URL: http://127.0.0.1:8000/admin/login/")
    print(f"Username: {username}")
    print(f"Password: Principle@Admin123")
    print(f"Access Level: Full system access (as Principle Admin)")
    print("="*60)
    
    return user

if __name__ == '__main__':
    print("Creating Principle Admin user...")
    create_principle_admin()
    print("\n✓ Setup complete!")
