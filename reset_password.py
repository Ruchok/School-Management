import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'management.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Delete existing and recreate
User.objects.filter(username='jjknadmin').delete()

# Create superuser with correct password
user = User.objects.create_superuser(
    username='jjknadmin',
    email='admin@school.com',
    password='jjkm1234'
)

print(f"✓ Superuser recreated: {user.username}")
print(f"✓ Password check: {user.check_password('jjkm1234')}")
print(f"✓ Is superuser: {user.is_superuser}")
