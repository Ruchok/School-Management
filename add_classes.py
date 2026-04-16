import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'management.settings')
django.setup()

from academics.models import SchoolClass

# Create classes 6 to 10
classes_data = [
    {'name': '6', 'section': 'A'},
    {'name': '6', 'section': 'B'},
    {'name': '7', 'section': 'A'},
    {'name': '7', 'section': 'B'},
    {'name': '8', 'section': 'A'},
    {'name': '8', 'section': 'B'},
    {'name': '9', 'section': 'A'},
    {'name': '9', 'section': 'B'},
    {'name': '10', 'section': 'A'},
    {'name': '10', 'section': 'B'},
]

for class_data in classes_data:
    school_class, created = SchoolClass.objects.get_or_create(
        name=class_data['name'],
        section=class_data['section']
    )
    if created:
        print(f"✓ Created: {school_class}")
    else:
        print(f"→ Already exists: {school_class}")

print("\n✓ All classes have been added successfully!")
