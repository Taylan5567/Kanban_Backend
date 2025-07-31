from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import BoardSerializer
from core.models import Board
from rest_framework.permissions import IsAuthenticated
from .permissions import IsStaffOrReadOnly
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication

class BoardListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        boards = Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

        serializer = BoardSerializer(boards, many=True, context={'request': request})
       
        if not request.user.is_authenticated:
            return Response({"error": "Nicht authentifiziert"}, status=401)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        data = request.data.copy()
        data['owner_id'] = request.user.id
        token = Token.objects.get(user=user)
        boards = Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

        serializer = BoardSerializer(data=data)

        if serializer.is_valid():
            board = serializer.save(owner=request.user)
            data = {
                'token': token.key,
                'title': board.title,
                'members': [members.id for members in board.members.all()],
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

           
      
