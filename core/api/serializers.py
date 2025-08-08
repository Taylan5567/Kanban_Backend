from rest_framework import serializers
from core.models import Board, Task, Comment
from django.contrib.auth.models import User

class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer for the Board model. Includes dynamic fields for counts related to board members and tasks.
    """
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'tasks_high_prio_count',
            'owner_id',
        ]
        extra_kwargs = {
            'owner_id': {'read_only': True}
        }

    def create(self, validated_data):
        """
        Create a new Board instance using the validated data.
        """
        return Board.objects.create(**validated_data)

    def get_member_count(self, obj):
        """
        Return the number of members in the board.
        """
        return obj.members.count()

    def get_ticket_count(self, obj):
        """
        Return the number of tasks (tickets) associated with the board.
        """
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """
        Return the number of tasks in 'to-do' status.
        """
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        """
        Return the number of high priority tasks.
        """
        return obj.tasks.filter(priority='high').count()

class BoardMemberSerializer(serializers.ModelSerializer):
    """
    Serializer for representing a board member.
    """
    fullname = serializers.CharField(source='first_name')


    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

class TaskAssigneeSerializer(serializers.ModelSerializer):
    """
    Serializer for representing a task assignee.
    """
    fullname = serializers.CharField(source='first_name')

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

class TaskReviewerSerializer(serializers.ModelSerializer):
    """
    Serializer for representing a task reviewer.
    """
    fullname = serializers.CharField(source='first_name')


    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task objects. Includes nested user info for assignees and reviewers,
    and a count of related comments.
    """
    assignee = serializers.SerializerMethodField(source='assignees', read_only=True)
    reviewer = serializers.SerializerMethodField(source='reviewers', read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer', 'due_date', 'comments_count'
        ]

    def get_comments_count(self, obj):
        """
        Returns the number of comments related to the task.
        """
        return obj.comments.count() if hasattr(obj, 'comments') else 0
    
    def get_assignee(self, obj):
        """
        Returns the first user from the assignees list as a dictionary.
        """
        user = obj.assignees.first()
        if user:
            return {
            "id": user.id,
            "email": user.email,
            "fullname": f"{user.first_name}"
            }
        return None

    def get_reviewer(self, obj):
        """
        Returns the first user from the reviewers list as a dictionary.
        """
        user = obj.reviewers.first()
        if user:
            return {
            "id": user.id,
            "email": user.email,
            "fullname": f"{user.first_name}"
            }
        return None
    
class TaskReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for tasks assigned to the user as a reviewer.
    Includes reviewer details and comment count.
    """
    comments_count = serializers.SerializerMethodField()
    reviewers = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority',
            'reviewers', 'due_date', 'comments_count'
        ]

    def get_reviewers(self, obj):
        """
        Returns a list of reviewers with id, email, and full name.
        """
        return [
            {
                'id': user.id,
                'email': user.email,
                'fullname': f"{user.first_name}".strip()
            }
            for user in obj.reviewers.all()
        ]

    def get_comments_count(self, obj):
        """
        Returns the number of comments associated with the task.
        """
        return obj.comments.count() if hasattr(obj, 'comments') else 0

class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a single board.
    Includes board members, tasks, and owner ID.
    """
    members = BoardMemberSerializer(many=True)
    tasks = TaskSerializer(many=True)

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'owner_id',
            'members',
            'tasks'
        ]
        extra_kwargs = {
            'owner_id': {'read_only': True}
        }

class CommentSerializer(serializers.ModelSerializer):

    """
    Serializer for task comments.
    Includes author name, content, and creation timestamp.
    """
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']

    def get_author(self, obj):
        return obj.author.first_name


class BoardPatchSerializer(serializers.ModelSerializer):
    """
    Serializer for partially updating a Board.
    - `members` is write-only and expects user IDs.
    - `members_data` provides read-only detailed member info.
    - `owner_data` provides read-only owner info.
    """
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, write_only=True)
    members_data = BoardMemberSerializer(many=True, read_only=True, source='members')
    owner_data = BoardMemberSerializer(read_only=True, source='owner')

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'owner_data','members_data']

class TaskPatchSerializer(serializers.ModelSerializer):
    """
    Serializer for PATCH updates on Task model.
    Includes nested representations of assignees and reviewers.
    """
    assignee = serializers.SerializerMethodField(source='assignees')
    reviewer = serializers.SerializerMethodField(source='reviewers')

    class Meta:
        model = Task
        fields = ['id', 
                  'title', 
                  'description', 
                  'status', 
                  'priority', 
                  'assignee', 
                  'reviewer', 
                  'due_date']
        
    def get_assignee(self, obj):
        """
        Returns the first user from the assignees list as a dictionary.
        """
        user = obj.assignees.first()
        if user:
            return {
            "id": user.id,
            "email": user.email,
            "fullname": f"{user.first_name}"
            }
        return None

    def get_reviewer(self, obj):
        """
        Returns the first user from the reviewers list as a dictionary.
        """
        user = obj.reviewers.first()
        if user:
            return {
            "id": user.id,
            "email": user.email,
            "fullname": f"{user.first_name}"
            }
        return None


class TaskAssignedToMeSerializer(serializers.ModelSerializer):
    """
    Serializer for tasks assigned to or reviewed by the authenticated user.

    Returns:
        - A single assignee and reviewer object (first user from each)
        - Board ID as integer
        - Comment count
    """
    assignee = serializers.SerializerMethodField(source='assignees', read_only=True)
    reviewer = serializers.SerializerMethodField(source='reviewers', read_only=True)
    board = serializers.IntegerField(source='board.id', read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id',
            'board',
            'title',
            'description',
            'status',
            'priority',
            'assignee',
            'reviewer',
            'due_date',
            'comments_count'
        ]

    def get_assignee(self, obj):
        """
        Returns the first user from the assignees list as a dictionary.
        """
        user = obj.assignees.first()
        if user:
            return {
            "id": user.id,
            "email": user.email,
            "fullname": f"{user.first_name}"
            }
        return None

    def get_reviewer(self, obj):
        """
        Returns the first user from the reviewers list as a dictionary.
        """
        user = obj.reviewers.first()
        if user:
            return {
            "id": user.id,
            "email": user.email,
            "fullname": f"{user.first_name}"
            }
        return None


    def get_comments_count(self, obj):
        """
        Returns the number of comments associated with the task.
        """
        return obj.comments.count()
