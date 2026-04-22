import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'management.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create School Admin user
username = 'admin'
email = 'admin@school.com'
password = 'Admin@2024'
role = 'ADMIN'

try:
    # Delete if exists
    User.objects.filter(username=username).delete()
    
    # Create new admin
    admin_user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        role=role,
        first_name='School',
        last_name='Admin'
    )
    
    print(f"✅ School Admin Created Successfully!")
    print(f"\n📋 Login Credentials:")
    print(f"   URL: http://127.0.0.1:8000/school-admin/login/")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"   Role: {role}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
