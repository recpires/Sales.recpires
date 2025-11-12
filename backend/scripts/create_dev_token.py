import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','core.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
username = 'dev_super'
password = 'P@ssw0rd123'
user, created = User.objects.get_or_create(username=username)
if created:
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f'Created superuser: {username}')
else:
    # Ensure it's a superuser and password updated
    user.is_superuser = True
    user.is_staff = True
    user.set_password(password)
    user.save()
    print(f'Updated existing user and set as superuser: {username}')

# Generate JWT tokens
from rest_framework_simplejwt.tokens import RefreshToken
refresh = RefreshToken.for_user(user)
access = str(refresh.access_token)
print('ACCESS_TOKEN:', access)
print('REFRESH_TOKEN:', str(refresh))

# Print auth header for convenience
print('\nUse this Authorization header:')
print('Authorization: Bearer ' + access)
