#!/usr/bin/env python
"""
Debug script to test the login view directly
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'management.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.test import Client
from django.test import RequestFactory
from school_admin.views import AdminLoginView
from django.conf import settings

# Test using RequestFactory to inspect the view directly
factory = RequestFactory()

print("Testing AdminLoginView directly...")
print(f"SCHOOL_ADMIN_PASSWORD: {settings.SCHOOL_ADMIN_PASSWORD}")
print(f"PRINCIPLE_ADMIN_PASSWORD: {settings.PRINCIPLE_ADMIN_PASSWORD}")

# Test with POST request
request = factory.post('/admin/login/', {'password': 'Principle@Admin123'})
request.session = {}

view = AdminLoginView()
response = view.post(request)

print(f"\nResponse type: {type(response)}")
print(f"Response status code: {response.status_code}")
print(f"Session after POST: {request.session}")

if 'principle_admin_authenticated' in request.session:
    print(f"✓ Session variable set: principle_admin_authenticated = {request.session['principle_admin_authenticated']}")
else:
    print("✗ Session variable NOT set")

# Also test with wrong password
print("\n" + "-"*60)
print("Testing with wrong password...")
request2 = factory.post('/admin/login/', {'password': 'WrongPassword'})
request2.session = {}

view2 = AdminLoginView()
response2 = view2.post(request2)

print(f"Response status code: {response2.status_code}")
print(f"Session: {request2.session}")
