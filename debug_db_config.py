try:
    import os
    import django
    from pathlib import Path
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'management.settings')
    django.setup()
    
    from django.conf import settings
    
    print("Current Database Configuration:")
    print(f"DB ENGINE: {settings.DATABASES['default']['ENGINE']}")
    print(f"DB NAME: {settings.DATABASES['default']['NAME']}")
    print(f"DB USER: {settings.DATABASES['default'].get('USER', 'N/A')}")
    print(f"DB HOST: {settings.DATABASES['default'].get('HOST', 'N/A')}")
    print(f"DB PORT: {settings.DATABASES['default'].get('PORT', 'N/A')}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
