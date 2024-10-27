"""
WSGI config for odalike project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
from dotenv import load_dotenv

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'odalike.settings')
load_dotenv(os.path.join('15minutewar.pythonanywhere.com', '.env'))
SECRET_KEY = os.getenv("SECRET_KEY")

application = get_wsgi_application()
