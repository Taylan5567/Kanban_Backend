from rest_framework import serializers
from auth_app.models import UserProfile
from django.contrib.auth.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def save(self, **kwargs):
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']
        email = self.validated_data['email']
        fullname = self.validated_data['fullname']

        if User.objects.filter(username=email).exists():
            raise serializers.ValidationError("Ein Benutzer mit dieser E-Mail existiert bereits.")


        user = User(
            email=email,
            username=email,
            first_name=fullname
        )

        if pw != repeated_pw:
            raise serializers.ValidationError({'error': 'Password dont match'})
        
        user.set_password(pw)
        user.save()
        return user

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value


