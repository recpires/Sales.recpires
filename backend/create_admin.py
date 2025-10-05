#!/usr/bin/env python
"""
Script to create admin superuser for production
Usage: python create_admin.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Admin credentials
USERNAME = 'admin'
EMAIL = 'admin@example.com'
PASSWORD = 'superadmin@1234'

# Check if admin already exists
if User.objects.filter(username=USERNAME).exists():
    print(f'❌ User "{USERNAME}" already exists!')
    user = User.objects.get(username=USERNAME)
    print(f'   Email: {user.email}')
    print(f'   Is superuser: {user.is_superuser}')
    print(f'   Is staff: {user.is_staff}')
else:
    # Create superuser
    user = User.objects.create_superuser(
        username=USERNAME,
        email=EMAIL,
        password=PASSWORD
    )
    print(f'✅ Superuser "{USERNAME}" created successfully!')
    print(f'   Email: {EMAIL}')
    print(f'   Password: {PASSWORD}')
    print(f'   Access admin at: /admin/')
