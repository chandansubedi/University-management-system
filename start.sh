#!/usr/bin/env bash
set -o errexit

# Run migrations
python manage.py migrate --noinput

# Collect static files (if not done in build)
python manage.py collectstatic --noinput

# Get port from Render's environment variable, default to 8000 if not set
PORT=${PORT:-8000}

# Bind to 0.0.0.0 (all interfaces) and the port from Render
exec python manage.py runserver 0.0.0.0:$PORT

