#!/usr/bin/env python
"""
Check what the login POST response contains
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'management.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.test import Client

client = Client()

print("POST /admin/login/ with wrong password")
response = client.post('/admin/login/', {'password': 'WrongPassword'})

print(f"Status: {response.status_code}")
print(f"Content-Type: {response.get('Content-Type', 'N/A')}")
print(f"Content length: {len(response.content)}")

content = response.content.decode()

# Check for key elements
print(f"\nKey elements in response:")
print(f"  'Admin Panel' in content: {'Admin Panel' in content}")
print(f"  'Invalid password' in content: {'Invalid password' in content}")
print(f"  '<form' in content: {'<form' in content}")
print(f"  'csrf' in content: {'csrf' in content}")
print(f"  'password' in content: {'password' in content}")

# Print first 500 chars of content
print(f"\nFirst 500 chars of response:")
print(content[:500])
