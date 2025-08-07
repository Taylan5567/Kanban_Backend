from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import BoardSerializer, TaskSerializer, TaskReviewSerializer, CommentSerializer
from .serializers import BoardDetailSerializer, BoardPatchSerializer, TaskPatchSerializer, TaskAssignedToMeSerializer
from core.models import Board, Task, Comment
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404


class BoardListView(APIView):
    """
    API endpoint to create a new board or list all boards where the user is an owner or a member.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Creates a new board with the authenticated user as the owner.
        Members can be optionally added via 'members' in the request body.
        """
        user = request.user
        data = request.data.copy()
        data['owner_id'] = user.id

        data.pop('members', None)

        serializer = BoardSerializer(data=data)
        if serializer.is_valid():
            board = serializer.save(owner=user)

            # Handle board members if provided
            member_ids = request.data.get('members', [])
            valid_users = User.objects.filter(id__in=member_ids)
            board.members.set(valid_users)

            response_data = {
                'id': board.id,
                'title': board.title,
                'member_count': board.members.count(),
                'ticket_count': board.ticket_count,
                'tasks_to_do_count': board.tasks_to_do_count,
                'tasks_high_prio_count': board.tasks_high_prio_count,
                'owner_id': user.id
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """
        Returns all boards where the authenticated user is either the owner or a member.
        """
        user = request.user
        boards = Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class BoardDetailsView(APIView):
    """
    Retrieve, update, or delete a specific board.

    Permissions:
        - Only the board owner or members can view or edit.
        - Only the owner can delete the board.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, board_id):
        """
        Returns detailed board information including all associated tasks.
        """
        board = get_object_or_404(Board, id=board_id)
        user = request.user

        if board.owner != user and user not in board.members.all():
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        board_data = BoardDetailSerializer(board).data
        return Response(board_data, status=status.HTTP_200_OK)

    def patch(self, request, board_id):
        """
        Partially updates the board (e.g. title or members).
        Only accessible to the board owner or members.
        """
        board = get_object_or_404(Board, id=board_id)
        user = request.user

        if user != board.owner and user not in board.members.all():
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        serializer = BoardPatchSerializer(board, data=data, partial=True, context={'request': request})

        if serializer.is_valid():
            updated_board = serializer.save()

            if 'members' in data:
                member_ids = data.get('members', [])
                valid_members = User.objects.filter(id__in=member_ids)
                updated_board.members.set(valid_members)

            board_data = BoardPatchSerializer(updated_board, context={'request': request}).data

            return Response(board_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, board_id):
        """
        Deletes the board.
        Only the board owner has permission to delete.
        """
        board = get_object_or_404(Board, id=board_id)

        if board.owner != request.user:
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
      
class EmailCheckView(APIView):
    """
    API view to check if a given email is registered in the system.

    URL pattern should include <str:email> as a parameter.

    Example:
        GET /api/email-check/test@example.com/

    Returns:
        - 200 OK with user data if email exists
        - 204 No Content if email does not exist
    """

    def get(self, request, email):
        exists = User.objects.filter(email=email).exists()

        if exists:
            user = User.objects.get(email=email)
            data = {
                "id": user.id,
                "email": user.email,
                "fullname": user.first_name
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "The email address is not registered."}, status=status.HTTP_204_NO_CONTENT)
        
class TaskCreateView(APIView):
    """
    API view to create a new task within a specific board.

    Permissions:
        - User must be authenticated and must be the owner or a member of the board.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Creates a new task if the user is authorized and all provided users are board members.

        Request body:
            - board (int): ID of the board
            - title (str): Title of the task
            - description (str): Task description
            - status (str): Task status (to-do, in-progress, done, review)
            - priority (str): Task priority (low, medium, high)
            - due_date (date): Optional due date
            - assignees (list[int]) or assignee_id (int)
            - reviewers (list[int]) or reviewer_id (int)

        Returns:
            - 201 Created with task data
            - 400 Bad Request if validation fails
            - 403 Forbidden if user not allowed
            - 500 Internal Server Error if an exception occurs
        """
        try:
            data = request.data
            board_id = data.get("board")

            if not board_id:
                return Response({"error": "Board ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            board = get_object_or_404(Board, id=board_id)
            user = request.user

            if user != board.owner and user not in board.members.all():
                return Response({"error": "Access denied. You are not a member of this board."}, status=status.HTTP_403_FORBIDDEN)

            assignee_ids = []
            if 'assignees' in data:
                assignee_ids = data.get('assignees', [])
            elif 'assignee_id' in data:
                assignee_ids = [data.get('assignee_id')]

            reviewer_ids = []
            if 'reviewers' in data:
                reviewer_ids = data.get('reviewers', [])
            elif 'reviewer_id' in data:
                reviewer_ids = [data.get('reviewer_id')]

            task = Task.objects.create(
                board=board,
                title=data.get("title"),
                description=data.get("description"),
                status=data.get("status"),
                priority=data.get("priority"),
                due_date=data.get("due_date")
            )

            task.assignees.set(assignee_ids)
            task.reviewers.set(reviewer_ids)

            serializer = TaskSerializer(task, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class MyTasksReviewsView(APIView):
    """
    API view to retrieve all tasks where the authenticated user is a reviewer.

    Permissions:
        - User must be authenticated.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Returns a list of tasks where the authenticated user is assigned as a reviewer.

        Response:
            - 200 OK with list of tasks
            - 500 Internal Server Error if an exception occurs
        """
        try:
            user = request.user
            tasks = Task.objects.filter(reviewers=user).distinct()
            serializer = TaskAssignedToMeSerializer(tasks, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class MyTasksAssignedView(APIView):
    """
    API view to retrieve all tasks assigned to the authenticated user.

    Permissions:
        - User must be authenticated.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Returns a list of tasks where the authenticated user is an assignee.

        Response:
            - 200 OK with list of tasks
            - 500 Internal Server Error if something goes wrong
        """
        try:
            user = request.user
            tasks = Task.objects.filter(assignees=user).distinct()
            serializer = TaskAssignedToMeSerializer(tasks, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MyTaskDetailsView(APIView):
    """
    API view to handle updating or deleting a specific task
    assigned to or reviewed by the authenticated user.

    Permissions:
        - User must be authenticated.
        - User must be either an assignee or reviewer for deletion.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request, task_id):
        """
        Partially update a task by task_id.

        Accepts updates to fields including assignees and reviewers.

        Returns:
            - 200 OK with updated task data
            - 400 Bad Request for invalid data
            - 404 Not Found if task doesn't exist
        """
        task = get_object_or_404(Task, id=task_id)
        user = request.user
        data = request.data.copy()
        serializer = TaskPatchSerializer(task, data=data, partial=True, context={'request': request})

        if serializer.is_valid():
            updated_task = serializer.save()
            
            assignee_ids = []
            if 'assignees' in data:
                assignee_ids = data.get('assignees', [])
            elif 'assignee_id' in data:
                assignee_ids = [data.get('assignee_id')]
            valid_assignees = User.objects.filter(id__in=assignee_ids)
            updated_task.assignees.set(valid_assignees)

            reviewer_ids = []
            if 'reviewers' in data:
                reviewer_ids = data.get('reviewers', [])
            elif 'reviewer_id' in data:
                reviewer_ids = [data.get('reviewer_id')]
            valid_reviewers = User.objects.filter(id__in=reviewer_ids)
            updated_task.reviewers.set(valid_reviewers)


            task_data = TaskPatchSerializer(updated_task, context={'request': request}).data

            return Response(task_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, task_id):
        """
        Delete a task if the user is an assignee or reviewer.

        Returns:
            - 204 No Content on success
            - 403 Forbidden if the user is unauthorized
            - 404 Not Found if task doesn't exist
        """
        task = get_object_or_404(Task, id=task_id)

        if request.user not in task.assignees.all() and request.user not in task.reviewers.all():
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CommentView(APIView):
    """
    API view to handle creating and retrieving comments for a specific task.

    Permissions:
        - Only authenticated users can access this view.
        - Users must be the board owner or a board member to view or add comments.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        """
        Handle POST request to create a new comment on a task.

        Args:
            request: The HTTP request object.
            task_id (int): ID of the task to which the comment belongs.

        Returns:
            HTTP 201 with serialized comment data if successful,
            HTTP 403 if access is denied,
            HTTP 400 if validation fails.
        """
        task = get_object_or_404(Task, id=task_id)

        if request.user != task.board.owner and request.user not in task.board.members.all():
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        data['author'] = request.user.id
        data['task'] = task.id

        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save(author=request.user, task=task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, task_id):
        """
        Handle GET request to retrieve all comments for a task.

        Args:
            request: The HTTP request object.
            task_id (int): ID of the task whose comments to retrieve.

        Returns:
            HTTP 200 with serialized list of comments,
            HTTP 403 if access is denied,
            HTTP 404 if task not found.
        """
        task = get_object_or_404(Task, id=task_id)

        if request.user != task.board.owner and request.user not in task.board.members.all():
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        comments = task.comments.all()
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class CommentDetailView(APIView):
    """
    API view to handle deletion of a specific comment.

    Permissions:
        - Only authenticated users can access this view.
        - Users can only delete comments if they are the board owner
          or a member of the board associated with the comment's task.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, task_id, comments_id):
        """
        Handle DELETE request for a specific comment.

        Args:
            request: The HTTP request object.
            task_id (int): ID of the task associated with the comment.
            comment_id (int): ID of the comment to delete.

        Returns:
            HTTP 204 if deleted successfully,
            HTTP 403 if access is denied,
            HTTP 404 if comment not found.
        """
        comments = get_object_or_404(Comment, id=comments_id, task__id=task_id)

        board = comments.task.board
        if request.user != board.owner and request.user not in board.members.all():
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        comments.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
