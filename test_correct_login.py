#!/usr/bin/env python
"""
Test the correct school admin login URL
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

print('Testing login at correct URL: /school-admin/login/')
print('='*60)

# Test GET
print('\nGET /school-admin/login/')
response = client.get('/school-admin/login/')
print(f'Status: {response.status_code}')
print(f'Contains "Admin Panel": {"Admin Panel" in response.content.decode()}')

# Test POST with principle admin password
print('\nPOST /school-admin/login/ with Principle@Admin123')
response = client.post('/school-admin/login/', {'password': 'Principle@Admin123'}, follow=False)
print(f'Status: {response.status_code}')
print(f'Redirected: {response.status_code == 302}')
if response.status_code == 302:
    print(f'Redirect to: {response.url}')

# Check session
print(f'\nSession variables:')
for key, value in client.session.items():
    print(f'  {key}: {value}')

# Follow redirect
print('\nFollowing redirect...')
response = client.get('/school-admin/dashboard/')
print(f'Status: {response.status_code}')
print(f'Contains "Principle Admin Mode": {"Principle Admin Mode" in response.content.decode()}')

# Test with school admin password
print('\n' + '='*60)
print('Testing School Admin login...')
print('='*60)

client2 = Client()
print('\nPOST /school-admin/login/ with School@Admin123')
response = client2.post('/school-admin/login/', {'password': 'School@Admin123'}, follow=False)
print(f'Status: {response.status_code}')
print(f'Redirected: {response.status_code == 302}')

# Check session
print(f'\nSession variables:')
for key, value in client2.session.items():
    print(f'  {key}: {value}')

print(f'\nContains "School Admin Mode": {"School Admin Mode" in client2.get("/school-admin/dashboard/").content.decode()}')

print('\n' + '='*60)
print('✓ Login tests complete!')
print('='*60)
