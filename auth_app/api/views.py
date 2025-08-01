from auth_app.models import UserProfile
from .serializers import UserProfileSerializer, RegistrationSerializer
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken


# View to list all user profiles or create a new one
class UserProfileList(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()  # All profiles from the database
    serializer_class = UserProfileSerializer  # Serializer used for output and input validation

# View to retrieve, update, or delete a specific user profile
class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()  # All profiles available for lookup
    serializer_class = UserProfileSerializer  # Serializer used for detail view

class RegistrationView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to register (no authentication required)

    # Handle POST request to register a new user
    def post(self, request):
        try:
            # Use the RegistrationSerializer to validate and save the user
            serializer = RegistrationSerializer(data=request.data)
            data = {}

            if serializer.is_valid():
                # Save the user and create authentication token
                saved_account = serializer.save()
                token, created = Token.objects.get_or_create(user=saved_account)

                # Prepare response data with token and user info
                data = {
                    'token': token.key,
                    'fullname': saved_account.first_name,
                    'email': saved_account.email,
                    'user_id': saved_account.id
                }

                return Response(data, status=status.HTTP_201_CREATED)

            # Return validation errors if input is invalid
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Catch any unexpected error and return 500
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        


class LoginView(ObtainAuthToken):
    permission_classes = [AllowAny]  # Allow unauthenticated users to access this view

    # Handle POST request for login
    def post(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            email = data.get('email')
            password = data.get('password')

            # Ensure both email and password are provided
            if not email or not password:
                return Response({'error': 'E-Mail und Passwort sind erforderlich.'}, status=400)

            from django.contrib.auth import get_user_model
            User = get_user_model()

            try:
                # Look up the user by email
                user = User.objects.get(email=email)

                # Insert username into the data (required by default ObtainAuthToken logic)
                data['username'] = user.username
            except User.DoesNotExist:
                return Response({'error': 'Benutzer mit dieser E-Mail nicht gefunden.'}, status=400)

            # Use the default serializer from ObtainAuthToken to validate credentials
            serializer = self.serializer_class(data=data, context={'request': request})

            # If credentials are valid, return token and user info
            if serializer.is_valid():
                user = serializer.validated_data['user']
                token, created = Token.objects.get_or_create(user=user)

                return Response({
                    'token': token.key,
                    'fullname': user.first_name,
                    'email': user.email,
                    'user_id': user.id
                }, status=status.HTTP_200_OK)

            # If serializer fails (wrong password, etc.)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Catch any unexpected error and return 500
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

