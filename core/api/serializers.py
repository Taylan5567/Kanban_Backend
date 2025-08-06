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
    task_high_priority_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'task_high_priority_count',
            'owner',
            'members',
        ]
        extra_kwargs = {
            'owner': {'read_only': True}
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

    def get_task_high_priority_count(self, obj):
        """
        Return the number of high priority tasks.
        """
        return obj.tasks.filter(priority='high').count()

class BoardMemberSerializer(serializers.ModelSerializer):
    """
    Serializer for representing a board member.
    """

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']



class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task objects. Includes nested user info for assignees and reviewers,
    and a count of related comments.
    """
    assignees = serializers.SerializerMethodField()
    reviewers = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority',
            'assignees', 'reviewers', 'due_date', 'comments_count'
        ]

    def get_assignees(self, obj):
        """
        Returns a list of assigned users with id, email, and full name.
        """
        return [
            {
                'id': user.id,
                'email': user.email,
                'fullname': f"{user.first_name} {user.last_name}".strip()
            }
            for user in obj.assignees.all()
        ]

    def get_reviewers(self, obj):
        """
        Returns a list of reviewers with id, email, and full name.
        """
        return [
            {
                'id': user.id,
                'email': user.email,
                'fullname': f"{user.first_name} {user.last_name}".strip()
            }
            for user in obj.reviewers.all()
        ]

    def get_comments_count(self, obj):
        """
        Returns the number of comments related to the task.
        """
        return obj.comments.count() if hasattr(obj, 'comments') else 0
    
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
                'fullname': f"{user.first_name} {user.last_name}".strip()
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
    tasks = TaskSerializer(many=True, source='tasks.all')
    owner_id = serializers.IntegerField(source='owner.id')

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']

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

