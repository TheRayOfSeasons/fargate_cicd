#!/bin/sh

# Exit script for any errors with code 0.
set -e

# Migrate
python manage.py migrate

# Collect static
python manage.py collectstatic --no-input

# Run Django application with uwsgi
uwsgi --socket :8000 --master --enable-threads --module tito.wsgi
