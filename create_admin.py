import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_admin():
    User = get_user_model()
    
    # Get credentials from environment variables or use defaults
    username = os.environ.get('ADMIN_USERNAME')
    email = os.environ.get('ADMIN_EMAIL')
    password = os.environ.get('ADMIN_PASSWORD')

    # Only run if environment variables are provided, to prevent accidental defaults in logs
    if not all([username, email, password]):
        print("Skipping superuser creation: ADMIN_USERNAME, ADMIN_EMAIL, or ADMIN_PASSWORD not set.")
        return

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser '{username}' successfully created.")
    else:
        print(f"Superuser '{username}' already exists. Skipping.")

if __name__ == "__main__":
    create_admin()
