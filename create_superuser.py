import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'management.settings')
django.setup()

User = get_user_model()

# Create superuser
username = 'schooladmin'
email = 'admin@school.local'
password = 'SchoolAdmin@2024'

try:
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        print(f"✅ Superuser '{username}' password updated!")
    else:
        user = User.objects.create_superuser(username=username, email=email, password=password)
        print(f"✅ Superuser '{username}' created successfully!")
    
    print(f"\n📋 Superuser Credentials:")
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    print(f"\n🔗 Admin Panel: http://127.0.0.1:8014/admin/")
    
except Exception as e:
    print(f"❌ Error: {e}")
