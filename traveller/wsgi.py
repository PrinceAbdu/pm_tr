"""
WSGI config for traveller project.
It exposes the WSGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""
import os
import traceback
import sys

from django.core.wsgi import get_wsgi_application

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traveller.settings')

# Get the original application
original_application = get_wsgi_application()

# Create a wrapper that catches and logs exceptions
def application(environ, start_response):
    try:
        return original_application(environ, start_response)
    except Exception:
        error_details = traceback.format_exc()
        print(f"CRITICAL ERROR: {error_details}", file=sys.stderr)
        start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
        return [b"Internal Server Error"]

# Define both 'application' and 'app' for compatibility
app = application
