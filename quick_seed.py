#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'management.settings')
django.setup()

from academics.models import SchoolClass, StudentProfile, Subject
from users.models import CustomUser
from django.utils import timezone
from datetime import timedelta

# Create a class if not exists
classroom, _ = SchoolClass.objects.get_or_create(
    name="Class 6",
    section="A"
)
print(f"✓ Class: {classroom}")

# Create a subject
subject, _ = Subject.objects.get_or_create(
    name="Bengali",
    code="BNG-DEMO",
    classroom=classroom
)
print(f"✓ Subject: {subject}")

# Create 3 test students
for i in range(1, 4):
    username = f"teststudent{i}{i}"
    first_name = f"TestStudent{i}"
    
    user, created = CustomUser.objects.get_or_create(
        username=username,
        defaults={
            "first_name": first_name,
            "last_name": "Demo",
            "role": CustomUser.Roles.STUDENT,
            "email": f"test{i}@example.com"
        }
    )
    
    if created:
        user.set_password("test1234")
        user.save()
        print(f"  ✓ Created user: {user.username}")
    
    student_profile, created = StudentProfile.objects.get_or_create(
        user=user,
        defaults={
            "classroom": classroom,
            "roll_number": f"6A-{i:03d}-TEST",
            "admission_date": timezone.now().date(),
            "guardian_name": f"Guardian {i}",
            "guardian_phone": "01700000000"
        }
    )
    
    if created:
        print(f"  ✓ Created student: {student_profile.user.first_name}")
    else:
        print(f"  • Student already exists: {student_profile.user.first_name}")

print("\n✅ Done! Test data created.")
