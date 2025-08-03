from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import BoardSerializer, TaskSerializer, TaskReviewSerializer, CommentSerializer
from core.models import Board, Task, Comment
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404


class BoardListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data.copy()
        data['owner_id'] = user.id 
        token = Token.objects.get(user=user)

        serializer = BoardSerializer(data=data)
        if serializer.is_valid():
            board = serializer.save(owner=user)
            member_ids = request.data.get('members', [])
            valid_users = User.objects.filter(id__in=member_ids)
            board.members.set(valid_users)

            response_data = {
                'id': board.id,
                'title': board.title,
                'member_count': board.members.count(),
                'ticket_count': board.ticket_count,
                'tasks_to_do_count': board.tasks_to_do_count,
                'tasks_high_prio_count': board.task_high_priority_count,
                'owner_id': user.id
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        user = request.user
        boards = Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    

class BoardDetailsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, board_id):
        board = get_object_or_404(Board, id=board_id)
        user = request.user

        if board.owner != user and user not in board.members.all():
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        board.data = BoardSerializer(board).data
        tasks = board.tasks.all()
        tasks = tasks.filter(Q(assignees=user) | Q(reviewers=user))
        board.data['tasks'] = TaskSerializer(tasks, many=True).data
        return Response(board.data, status=status.HTTP_200_OK)

    def patch(self, request, board_id):
        board = get_object_or_404(Board, id=board_id)

        if request.user != board.owner and request.user not in board.members.all():
            return Response({'detail': 'Access denied'}, status=403)

        data = request.data.copy()
        serializer = BoardSerializer(board, data=data, partial=True, context={'request': request})

        if serializer.is_valid():
            updated_board = serializer.save()

            if 'members' in data:
                member_ids = data.get('members', [])
                valid_members = User.objects.filter(id__in=member_ids)
                updated_board.members.set(valid_members)


            board_data = BoardSerializer(updated_board).data
            tasks = updated_board.tasks.all()
            board_data['tasks'] = TaskSerializer(tasks, many=True).data

            return Response(board_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, board_id):
        board = get_object_or_404(Board, id=board_id)

        if board.owner != request.user:
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


      
class EmailCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get('email')

        if not email:
            return Response(
                {'error': 'Missing email address in query parameters.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
            return Response({
                'id': user.id,
                'email': user.email,
                'fullname': user.first_name
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {'error': 'User with this email does not exist.'},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

class TaskCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            board_id = data.get("board") 

            if not board_id:
                return Response({"error": "Board-ID fehlt."}, status=status.HTTP_400_BAD_REQUEST)

            board = get_object_or_404(Board, id=board_id)
            user = request.user

            if user != board.owner and user not in board.members.all():
                return Response({"error": "Zugriff verweigert. Kein Mitglied dieses Boards."}, status=403)
            
            assignees = data.get("assignees", [])
            reviewers = data.get("reviewers", [])


            assignees = User.objects.filter(id__in=assignees)
            reviewers = User.objects.filter(id__in=reviewers)

            

            if not all(user in board.members.all() for user in assignees):
                return Response({"error": "Ein oder mehrere Assignees sind keine Mitglieder des Boards."}, status=400)

            if not all(user in board.members.all() for user in reviewers):
                return Response({"error": "Ein oder mehrere Reviewer sind keine Mitglieder des Boards."}, status=400)

            task = Task.objects.create(
                board=board,
                title=data.get("title"),
                description=data.get("description"),
                status=data.get("status"),
                priority=data.get("priority"),
                due_date=data.get("due_date")
            )

            task.assignees.set(assignees)
            task.reviewers.set(reviewers)

            serializer = TaskSerializer(task, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        


class MyTasksReviewsView(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        try:
            user = request.user
            tasks = Task.objects.filter(reviewers=user).distinct()
            serializer = TaskReviewSerializer(tasks, many=True, context={'request': request})

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'errors': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

        
class MyTasksAssignedView(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        try:
            user = request.user 
            task = Task.objects.filter(assignees=user).distinct()
            serializer = TaskSerializer(task, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'errors': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

class MyTaskDetailsView(APIView):
    permission_classes = [IsAuthenticated]  

    def patch(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)

        data = request.data.copy()

        serializer = TaskSerializer(task, data=data, partial=True, context={'request': request})

        if serializer.is_valid():
            updated_task = serializer.save()

            if 'assignees' in data:
                assignee_ids = data.get('assignees', [])
                valid_assignees = User.objects.filter(id__in=assignee_ids)
                updated_task.assignees.set(valid_assignees)

            if 'reviewers' in data:
                reviewer_ids = data.get('reviewers', [])
                valid_reviewers = User.objects.filter(id__in=reviewer_ids)
                updated_task.reviewers.set(valid_reviewers)

            return Response(TaskSerializer(updated_task).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)

        if request.user not in task.assignees.all() and request.user not in task.reviewers.all():
            return Response({'detail': 'Zugriff verweigert'}, status=status.HTTP_403_FORBIDDEN)

        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CommentView(APIView):
    permission_classes = [IsAuthenticated]  

    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)


        if request.user != task.board.owner and request.user not in task.board.members.all():
            return Response({'detail': 'Access denied'}, status=403)

        data = request.data.copy()
        data['author'] = request.user.id 
        data['task'] = task.id           

        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save(author=request.user, task=task)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)

    def get(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        user = request.user

        if request.user != task.board.owner and request.user not in task.board.members.all():
            return Response({'detail': 'Access denied'}, status=403)
        
        serializer = CommentSerializer(task.comments.all(), many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class CommentDetailView(APIView):
    permission_classes = [IsAuthenticated]  

    def delete(self, request, task_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, task__id=task_id)

        if request.user != comment.task.board.owner and request.user not in comment.task.board.members.all():
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

