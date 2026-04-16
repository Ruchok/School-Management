#!/usr/bin/env python
"""
Debug the login view response
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'management.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.test import Client
from django.urls import reverse

client = Client()

print("Testing login flow...")
print("="*60)

# Get login page
print("\nStep 1: GET /admin/login/")
response = client.get('/admin/login/')
print(f"Status: {response.status_code}")

# Post wrong password
print("\nStep 2: POST with wrong password")
response = client.post('/admin/login/', {'password': 'WrongPassword'})
print(f"Status: {response.status_code}")
print(f"Redirected: {response.status_code == 302}")
print(f"'Invalid password' in content: {'Invalid password' in response.content.decode()}")

# Post correct principle admin password
print("\nStep 3: POST with correct principle admin password")
response = client.post('/admin/login/', {'password': 'Principle@Admin123'}, follow=False)
print(f"Status: {response.status_code}")
print(f"Redirected: {response.status_code == 302}")
if response.status_code == 302:
    print(f"Redirect to: {response.url}")
print(f"Session after POST:")
for key, value in client.session.items():
    print(f"  {key}: {value}")

# Try following redirect
print("\nStep 4: Follow the redirect")
response = client.post('/admin/login/', {'password': 'Principle@Admin123'}, follow=True)
print(f"Final status: {response.status_code}")
print(f"Final URL: {response.redirect_chain}")
print(f"'Principle Admin Mode' in final content: {'Principle Admin Mode' in response.content.decode()}")

print("\nSession after follow:")
for key, value in client.session.items():
    print(f"  {key}: {value}")
