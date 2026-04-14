#!/usr/bin/env python
"""
Direct migration runner using system Python with proper setup.
"""
import os
import sys
import django
from pathlib import Path

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'management.settings')

# Setup Django
django.setup()

# Import and run migrations
from django.core.management import call_command

print("Running migrations...")
call_command('migrate', verbosity=2)
print("Migration complete!")
