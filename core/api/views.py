from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import BoardSerializer, TaskSerializer
from core.models import Board, Task
from rest_framework.permissions import IsAuthenticated
from .permissions import IsStaffOrReadOnly
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404


class BoardListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, board_id):
        board = get_object_or_404(Board, id=board_id)

        user = request.user
        if board.owner != user and user not in board.members.all():
            return Response({'error': 'Zugriff verweigert'}, status=status.HTTP_403_FORBIDDEN)

        serializer = BoardSerializer(board)
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
            
            member_ids = request.data.get('members', [])
            valid_users = User.objects.filter(id__in=member_ids)
            board.members.set(valid_users)

            data = {
                'token': token.key,
                'board': board.id,
                'title': board.title,
                'member_count': board.members.count(),
                'ticket_count': board.ticket_count,
                'tasks_to_do_count': board.tasks_to_do_count,
                'tasks_high_prio_count': board.task_high_priority_count,
                'owner_id': user.id
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, board_id):
        board = get_object_or_404(Board, id=board_id)

        if request.user != board.owner and request.user not in board.members.all():
            return Response({'detail': 'Zugriff verweigert'}, status=403)

        data = request.data.copy()

        serializer = BoardSerializer(board, data=data, partial=True, context={'request': request})

        if serializer.is_valid():
            updated_board = serializer.save()

            if 'members' in data:
                member_ids = data.get('members', [])
                valid_members = User.objects.filter(id__in=member_ids)
                updated_board.members.set(valid_members)

            return Response(BoardSerializer(updated_board).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, board_id):
        board = get_object_or_404(Board, id=board_id)

        if board.owner != request.user:
            return Response({'detail': 'Zugriff verweigert'}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        
        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
      
class EmailCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get('email')

        if not email:
            return Response({'error': 'E-Mail Adresse existiert nicht oder gibts nicht'}, status=status.HTTP_400_BAD_REQUEST)
        
        try: 
            user = User.objects.get(email=email)
            return Response({
                'id': user.id,
                'email': user.email,
                'fullname': user.first_name
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class TaskCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            board_id = data.get("board")

            if not board_id:
                return Response({"error": "Board-ID fehlt."}, status=400)

            board = get_object_or_404(Board, id=board_id)

            user = request.user
            if user != board.owner and user not in board.members.all():
                return Response({"error": "Zugriff verweigert. Kein Mitglied dieses Boards."}, status=403)

            assignee_id = data.get("assignee_id")
            reviewer_id = data.get("reviewer_id")

            assignee = None
            reviewer = None

            if assignee_id:
                assignee = get_object_or_404(User, id=assignee_id)
                if assignee not in board.members.all():
                    return Response({"error": "Assignee ist kein Mitglied des Boards."}, status=400)

            if reviewer_id:
                reviewer = get_object_or_404(User, id=reviewer_id)
                if reviewer not in board.members.all():
                    return Response({"error": "Reviewer ist kein Mitglied des Boards."}, status=400)

            task = Task.objects.create(
                board=board,
                title=data.get("title"),
                description=data.get("description"),
                status=data.get("status"),
                priority=data.get("priority"),
                due_date=data.get("due_date")
            )

            if assignee:
                task.assignee.add(assignee)
            if reviewer:
                task.reviewers.add(reviewer)

            serializer = TaskSerializer(task, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
   
        

class MyTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            tasks = Task.objects.filter(assignee=user).distinct()
            serializer = TaskSerializer(tasks, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e: 
            return Response({'errors': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)