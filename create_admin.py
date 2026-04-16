import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'management.settings')
django.setup()

from django.contrib.auth.models import User

# Delete existing user if exists
User.objects.filter(username='jjknadmin').delete()

# Create new superuser
user = User.objects.create_superuser(
    username='jjknadmin',
    email='admin@jjkn.com',
    password='jjkm1234'
)
print(f"✓ Superuser created: {user.username}")
