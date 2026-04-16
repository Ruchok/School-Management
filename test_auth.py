import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'management.settings')
django.setup()

from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

# Try to authenticate
user = authenticate(username='jjknadmin', password='jjkm1234')
print(f"Authentication result: {user}")

# Check user exists
try:
    u = User.objects.get(username='jjknadmin')
    print(f"User found: {u}, is_staff: {u.is_staff}, is_superuser: {u.is_superuser}")
    print(f"Password check: {u.check_password('jjkm1234')}")
except User.DoesNotExist:
    print("User not found")
