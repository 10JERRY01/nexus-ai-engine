#!/bin/sh

# This is our container's startup script.

echo "Starting Gunicorn web server..."

# Start the Gunicorn server.
# This will be the main process for the container.
gunicorn --bind 0.0.0.0:5000 --workers 1 --threads 4 --timeout 120 app:app