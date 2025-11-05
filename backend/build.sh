#!/usr/bin/env bash
# Build script for backend deployment

set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
# --fake-initial: Skip CreateModel operations if tables already exist
python manage.py migrate --no-input --fake-initial
