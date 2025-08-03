from rest_framework import serializers
from auth_app.models import UserProfile
from django.contrib.auth.models import User

# Basic serializer for the UserProfile model
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile  # Refers to your custom user profile model
        fields = '__all__'   # Includes all model fields in the serialized output


# Serializer used during registration to create a new user
class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)  # Password confirmation field

    class Meta:
        model = UserProfile  # Technically, this serializer creates a User, not a UserProfile
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {
                'write_only': True  # Don't expose password in response
            }
        }

    # Save method to manually create a User object
    def save(self, **kwargs):
        """
        Save method to manually create a User object.

        1. Checks if a user with the given email already exists.
        2. Creates a new User instance (not yet saved).
        3. Checks if passwords match.
        4. Hashes the password and saves the user.

        :raises serializers.ValidationError: If a user with the given email already exists or if passwords don't match.
        :return: The created User object.
        """
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']
        email = self.validated_data['email']
        fullname = self.validated_data['fullname']

        # Check if a user with this email already exists
        if User.objects.filter(username=email).exists():
            raise serializers.ValidationError("Ein Benutzer mit dieser E-Mail existiert bereits.")

        # Create a new User instance (not yet saved)
        user = User(
            email=email,
            username=email,            # Username set to email (common pattern)
            first_name=fullname
        )

        # Ensure passwords match
        if pw != repeated_pw:
            raise serializers.ValidationError({'error': 'Password dont match'})

        # Hash the password and save the user
        user.set_password(pw)
        user.save()
        return user

    # Optional: clean email with additional check
    def validate_email(self, value):
        """
        Validates that the given email does not already exist in the User model.

        :param value: The email address to validate.
        :type value: str
        :raises serializers.ValidationError: If the email already exists in the database.
        :return: The validated email value if it's unique.
        :rtype: str
        """

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value
