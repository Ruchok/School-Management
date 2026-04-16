#!/usr/bin/env python
"""
Test script to verify Principle Admin authentication is working
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'management.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.test import Client
from django.contrib import messages
from users.models import CustomUser

def test_principle_admin_auth():
    """Test principle admin authentication"""
    client = Client()
    
    print("\n" + "="*60)
    print("Testing Principle Admin Authentication System")
    print("="*60)
    
    # Check if principle admin user exists
    if CustomUser.objects.filter(username='principle_admin').exists():
        user = CustomUser.objects.get(username='principle_admin')
        print(f"\n✓ Principle Admin user exists:")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Role: {user.role}")
        print(f"  Full Name: {user.get_full_name()}")
    else:
        print("\n✗ Principle Admin user NOT found")
        return False
    
    # Test login with Principle Admin password
    print("\n" + "-"*60)
    print("Testing Principle Admin Login...")
    print("-"*60)
    
    response = client.post('/admin/login/', {
        'password': 'Principle@Admin123'
    }, follow=True)
    
    session = client.session
    print(f"  Response status: {response.status_code}")
    print(f"  Session keys: {list(session.keys())}")
    print(f"  principle_admin_authenticated: {session.get('principle_admin_authenticated')}")
    print(f"  principle_admin: {session.get('principle_admin')}")
    
    if session.get('principle_admin_authenticated'):
        print("✓ Principle Admin login successful")
        print(f"  Session: principle_admin_authenticated = {session.get('principle_admin_authenticated')}")
        print(f"  principle_admin = {session.get('principle_admin')}")
    else:
        print("✗ Principle Admin login failed")
        return False
    
    # Test dashboard access
    print("\n" + "-"*60)
    print("Testing Dashboard Access...")
    print("-"*60)
    
    response = client.get('/admin/dashboard/')
    if response.status_code == 200:
        print("✓ Dashboard accessible to Principle Admin")
        if 'Principle Admin Mode' in response.content.decode():
            print("✓ Dashboard shows Principle Admin status")
        else:
            print("⚠ Dashboard doesn't explicitly show Principle Admin status")
    else:
        print(f"✗ Dashboard not accessible (Status: {response.status_code})")
        return False
    
    # Test School Admin password
    print("\n" + "-"*60)
    print("Testing School Admin Login...")
    print("-"*60)
    
    client = Client()  # Fresh client
    response = client.post('/admin/login/', {
        'password': 'School@Admin123'
    }, follow=True)
    
    session = client.session
    print(f"  Response status: {response.status_code}")
    print(f"  school_admin_authenticated: {session.get('school_admin_authenticated')}")
    print(f"  principle_admin_authenticated: {session.get('principle_admin_authenticated')}")
    
    if session.get('school_admin_authenticated') and not session.get('principle_admin_authenticated'):
        print("✓ School Admin login successful")
        print(f"  Session: school_admin_authenticated = {session.get('school_admin_authenticated')}")
        print(f"  principle_admin_authenticated = {session.get('principle_admin_authenticated')}")
    else:
        print("✗ School Admin login failed or mixed up roles")
        return False
    
    # Test dashboard with School Admin
    print("\n" + "-"*60)
    print("Testing Dashboard Access (School Admin)...")
    print("-"*60)
    
    response = client.get('/admin/dashboard/')
    if response.status_code == 200:
        print("✓ Dashboard accessible to School Admin")
        if 'School Admin Mode' in response.content.decode():
            print("✓ Dashboard shows School Admin status")
        else:
            print("⚠ Dashboard doesn't explicitly show School Admin status")
    else:
        print(f"✗ Dashboard not accessible (Status: {response.status_code})")
        return False
    
    # Test logout
    print("\n" + "-"*60)
    print("Testing Logout...")
    print("-"*60)
    
    response = client.get('/admin/logout/', follow=True)
    session = client.session
    
    if not session.get('school_admin_authenticated') and not session.get('principle_admin_authenticated'):
        print("✓ Logout successful - session cleared")
    else:
        print("✗ Logout failed - session not cleared")
        return False
    
    print("\n" + "="*60)
    print("✓ All authentication tests passed!")
    print("="*60)
    print("\nLOGIN CREDENTIALS:")
    print("  School Admin Password: School@Admin123")
    print("  Principle Admin Password: Principle@Admin123")
    print("  Login URL: http://127.0.0.1:8000/admin/login/")
    print("="*60 + "\n")
    
    return True

if __name__ == '__main__':
    try:
        success = test_principle_admin_auth()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
