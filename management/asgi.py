"""
ASGI config for management project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os
import sys

# Register PyMySQL as MySQLdb before importing Django
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except Exception:
    pass

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'management.settings')

application = get_asgi_application()
