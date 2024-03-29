"""Initialize global variables."""

# Do library imports
from pattoo import configuration

# Create global variables used by all applications
CONFIG = configuration.Config()

# Create global variables for the API
API_PREFIX = '/pattoo'
API_EXECUTABLE = 'pattoo-os-passived'
API_GUNICORN_AGENT = 'pattoo-os-passived-gunicorn'
POLLER_EXECUTABLE = 'pattoo-os-actived'
