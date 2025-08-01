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

    # Create a new board
    def post(self, request):
        user = request.user
        data = request.data.copy()
        data['owner_id'] = user.id  # Set the owner to the current user
        token = Token.objects.get(user=user)

        # Validate and create the board
        serializer = BoardSerializer(data=data)
        if serializer.is_valid():
            board = serializer.save(owner=user)
            member_ids = request.data.get('members', [])
            valid_users = User.objects.filter(id__in=member_ids)
            board.members.set(valid_users)

            response_data = {
                'token': token.key,
                'board': board.id,
                'title': board.title,
                'member_count': board.members.count(),
                'ticket_count': board.ticket_count,
                'tasks_to_do_count': board.tasks_to_do_count,
                'tasks_high_prio_count': board.task_high_priority_count,
                'owner_id': user.id
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # List all boards owned by or shared with the user
    def get(self, request):
        user = request.user
        boards = Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    

class BoardDetailsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Get specific board by ID
    def get(self, request, board_id):
        board = get_object_or_404(Board, id=board_id)
        user = request.user

        # Only allow access to owner or members
        if board.owner != user and user not in board.members.all():
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer = BoardSerializer(board)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Partial update of a board
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

            return Response(BoardSerializer(updated_board).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a board (only owner allowed)
    def delete(self, request, board_id):
        board = get_object_or_404(Board, id=board_id)

        if board.owner != request.user:
            return Response({'detail': 'Access denied'}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)

        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


      
class EmailCheckView(APIView):
    permission_classes = [IsAuthenticated]

    # GET method to check if a user with the provided email exists
    def get(self, request):
        # Get the email from the query parameters (?email=...)
        email = request.query_params.get('email')

        if not email:
            return Response(
                {'error': 'Missing email address in query parameters.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Attempt to retrieve the user by email
            user = User.objects.get(email=email)
            return Response({
                'id': user.id,
                'email': user.email,
                'fullname': user.first_name  # or user.get_full_name() if preferred
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {'error': 'User with this email does not exist.'},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            # Catch all other unexpected exceptions
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

class TaskCreateView(APIView):
    permission_classes = [IsAuthenticated]

    # Handle POST request to create a new task
    def post(self, request):
        try:
            data = request.data
            board_id = data.get("board")  # Get the board ID from the request

            # If board ID is missing, return error
            if not board_id:
                return Response({"error": "Board-ID fehlt."}, status=400)

            # Try to retrieve the board by ID
            board = get_object_or_404(Board, id=board_id)
            user = request.user

            # Only the board owner or its members can create tasks
            if user != board.owner and user not in board.members.all():
                return Response({"error": "Zugriff verweigert. Kein Mitglied dieses Boards."}, status=403)

            # Get assignee and reviewer user IDs from request
            assignee_ids = data.get("assignee_ids", [])
            reviewer_ids = data.get("reviewer_ids", [])

            # Fetch the corresponding User objects
            assignees = User.objects.filter(id__in=assignee_ids)
            reviewers = User.objects.filter(id__in=reviewer_ids)

            # Check if all assignees are members of the board
            if not all(user in board.members.all() for user in assignees):
                return Response({"error": "Ein oder mehrere Assignees sind keine Mitglieder des Boards."}, status=400)

            # Check if all reviewers are members of the board
            if not all(user in board.members.all() for user in reviewers):
                return Response({"error": "Ein oder mehrere Reviewer sind keine Mitglieder des Boards."}, status=400)

            # Create the task instance
            task = Task.objects.create(
                board=board,
                title=data.get("title"),
                description=data.get("description"),
                status=data.get("status"),
                priority=data.get("priority"),
                due_date=data.get("due_date")
            )

            # Assign assignees and reviewers to the task
            task.assignees.set(assignees)
            task.reviewers.set(reviewers)

            # Serialize and return the created task
            serializer = TaskSerializer(task, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Catch any unexpected exception
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        


class MyTasksReviewsView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access this view

    def get(self, request):
        try:
            user = request.user
            tasks = Task.objects.filter(reviewers=user).distinct()
            serializer = TaskReviewSerializer(tasks, many=True, context={'request': request})

            # Return tasks the user is reviewing
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            # Return server error if an exception occurs
            return Response({'errors': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

        
class MyTasksAssignedView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access this view

    # Handle GET request to retrieve all tasks assigned to the current user
    def get(self, request):
        try:
            user = request.user  # Get the currently authenticated user

            # Query all tasks where the user is listed as an assignee
            task = Task.objects.filter(assignees=user).distinct()

            # Serialize the task list
            serializer = TaskSerializer(task, many=True, context={'request': request})

            # Return serialized data with 200 OK
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            # Catch any unexpected errors and return a 500 Internal Server Error
            return Response({'errors': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

class MyTaskDetailsView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access this view

    # Handle PATCH request to update a specific task
    def patch(self, request, tasks_id):
        # Retrieve the task by ID or return 404 if not found
        task = get_object_or_404(Task, id=tasks_id)

        data = request.data.copy()

        # Create a serializer instance with partial update enabled
        serializer = TaskSerializer(task, data=data, partial=True, context={'request': request})

        # Validate and save the task
        if serializer.is_valid():
            updated_task = serializer.save()

            # If new assignees are provided, update them
            if 'assignees' in data:
                assignee_ids = data.get('assignees', [])
                valid_assignees = User.objects.filter(id__in=assignee_ids)
                updated_task.assignees.set(valid_assignees)

            # If new reviewers are provided, update them
            if 'reviewers' in data:
                reviewer_ids = data.get('reviewers', [])
                valid_reviewers = User.objects.filter(id__in=reviewer_ids)
                updated_task.reviewers.set(valid_reviewers)

            # Return updated task data
            return Response(TaskSerializer(updated_task).data, status=status.HTTP_200_OK)

        # If validation fails, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Handle DELETE request to remove a task
    def delete(self, request, task_id):
        # Retrieve the task or return 404 if not found
        task = get_object_or_404(Task, id=task_id)

        # Only allow deletion if the user is an assignee or reviewer
        if request.user not in task.assignees.all() and request.user not in task.reviewers.all():
            return Response({'detail': 'Zugriff verweigert'}, status=status.HTTP_403_FORBIDDEN)

        # Delete the task and return 204 No Content
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CommentView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users are allowed

    # Handle POST request to add a comment to a task
    def post(self, request, task_id):
        # Retrieve the task or return 404 if not found
        task = get_object_or_404(Task, id=task_id)

        # Only the board owner or its members can comment
        if request.user != task.board.owner and request.user not in task.board.members.all():
            return Response({'detail': 'Access denied'}, status=403)

        data = request.data.copy()
        data['author'] = request.user.id  # Set the current user as the author
        data['task'] = task.id            # Set the current task as the target

        # Serialize the comment
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            # Save the comment with related user and task
            serializer.save(author=request.user, task=task)
            return Response(serializer.data, status=201)

        # If validation fails, return errors
        return Response(serializer.errors, status=400)

    # Handle GET request to retrieve all comments for a task
    def get(self, request, task_id):
        # Retrieve the task or return 404 if not found
        task = get_object_or_404(Task, id=task_id)
        user = request.user

        # Only the board owner or its members can view comments
        if request.user != task.board.owner and request.user not in task.board.members.all():
            return Response({'detail': 'Access denied'}, status=403)

        # Serialize all comments related to the task
        serializer = CommentSerializer(task.comments.all(), many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class CommentDetailView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users are allowed

    # Handle DELETE request to delete a specific comment from a task
    def delete(self, request, task_id, comment_id):
        # Retrieve the comment by ID and associated task ID, or return 404 if not found
        comment = get_object_or_404(Comment, id=comment_id, task__id=task_id)

        # Only the board owner or its members can delete a comment
        if request.user != comment.task.board.owner and request.user not in comment.task.board.members.all():
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        # Delete the comment and return 204 No Content
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

