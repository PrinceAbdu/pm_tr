"""
WSGI config for traveller project.
It exposes the WSGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""
import os
import traceback
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from django.core.wsgi import get_wsgi_application

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traveller.settings')

# Get the original application
try:
    logger.info("Initializing Django WSGI application")
    original_application = get_wsgi_application()
    logger.info("Django WSGI application initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Django WSGI application: {str(e)}")
    logger.error(traceback.format_exc())
    raise

# Create a wrapper that catches and logs exceptions
def application(environ, start_response):
    logger.info(f"Received request: {environ.get('PATH_INFO', 'unknown path')}")
    try:
        return original_application(environ, start_response)
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"CRITICAL ERROR in request: {str(e)}")
        logger.error(error_details)
        print(f"CRITICAL ERROR: {error_details}", file=sys.stderr)
        start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
        return [b"Internal Server Error - Details logged"]

# Define both 'application' and 'app' for compatibility
app = application
