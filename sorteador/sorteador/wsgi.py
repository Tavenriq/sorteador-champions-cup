"""
WSGI config for sorteador project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

# Garante que a pasta que contem o manage.py esteja no sys.path (necessario na Vercel)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sorteador.settings')

application = get_wsgi_application()

# A Vercel procura por uma variavel chamada "app"
app = application
