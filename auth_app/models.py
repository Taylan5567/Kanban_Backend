from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    # One-to-one relationship with Django's built-in User model
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Primary key for the profile (separate from the User ID)
    id = models.AutoField(primary_key=True)

    # Full name of the user (used instead of first_name/last_name)
    fullname = models.CharField(max_length=100)

    # Unique email address for the profile
    email = models.EmailField(unique=True)

    # Hashed password (Note: This is not automatically encrypted!)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.fullname  # String representation of the profile
