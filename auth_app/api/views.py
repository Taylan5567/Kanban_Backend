from auth_app.models import UserProfile
from .serializers import UserProfileSerializer, RegistrationSerializer
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken


class UserProfileList(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = RegistrationSerializer(data=request.data)
            data = {}
            if serializer.is_valid():
                saved_account = serializer.save()
                token, created = Token.objects.get_or_create(user=saved_account)

                data = {
                    'token': token.key,
                    'fullname': saved_account.first_name,
                    'email': saved_account.email,
                    'user_id': saved_account.id
                }

                return Response(data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class LoginView(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return Response({'error': 'E-Mail und Passwort sind erforderlich.'}, status=400)

            
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(email=email)
                data['username'] = user.username 
            except User.DoesNotExist:
                return Response({'error': 'Benutzer mit dieser E-Mail nicht gefunden.'}, status=400)

           
            serializer = self.serializer_class(data=data, context={'request': request})

            if serializer.is_valid():
                user = serializer.validated_data['user']
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'fullname': user.first_name,
                    'email': user.email,
                    'user_id': user.id
                }, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
