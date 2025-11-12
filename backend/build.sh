#!/usr/bin/env bash
# Build script for backend deployment

set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations with smart table detection
# This script checks if tables exist and handles migrations accordingly
python migrate_safe.py
