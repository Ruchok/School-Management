#!/usr/bin/env python
"""
Simple password test
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'management.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.conf import settings

admin_password = getattr(settings, 'SCHOOL_ADMIN_PASSWORD', 'Admin@123')
principle_password = getattr(settings, 'PRINCIPLE_ADMIN_PASSWORD', 'Principle@Admin123')

print(f"SCHOOL_ADMIN_PASSWORD: '{admin_password}'")
print(f"PRINCIPLE_ADMIN_PASSWORD: '{principle_password}'")

test_password1 = 'Principle@Admin123'
test_password2 = 'School@Admin123'

print(f"\nTest 1: '{test_password1}' == '{principle_password}'")
print(f"Result: {test_password1 == principle_password}")

print(f"\nTest 2: '{test_password2}' == '{admin_password}'")
print(f"Result: {test_password2 == admin_password}")

# Test via Django client
from django.test import Client

client = Client()

# First test a GET to see if login page loads
print("\n" + "-"*60)
print("GET /admin/login/")
response = client.get('/admin/login/')
print(f"Status: {response.status_code}")
print(f"Content length: {len(response.content)}")
print(f"'Principle Admin' in content: {'Principle Admin' in response.content.decode()}")

# Then test POST
print("\n" + "-"*60)
print("POST /admin/login/ with password='Principle@Admin123'")
response = client.post('/admin/login/', {'password': 'Principle@Admin123'})
print(f"Status: {response.status_code}")
print(f"URL after POST: {response.url if hasattr(response, 'url') else 'N/A'}")
print(f"'Principle Admin' in content: {'Principle Admin' in response.content.decode()}")

# Check session
print(f"\nSession content:")
for key, value in client.session.items():
    print(f"  {key}: {value}")
