from django.contrib.auth.models import UserManager
from django.contrib.auth import get_user_model


class CustomUserManager(UserManager):

    def exists(self, data):
        """Check if an email exists"""
        my_user_model = get_user_model()
        email = data.get('email', '')
        if not email:
            return False
        return my_user_model.objects.filter(email=email).exists()
