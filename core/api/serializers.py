from rest_framework import serializers
from core.models import Board, Task, Comment
from django.contrib.auth.models import User

class BoardSerializer(serializers.ModelSerializer):
    # Computed fields returned in the serialized output
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
        ]
        extra_kwargs = {
            'owner': {'read_only': True}  # Owner should not be set manually via API
        }

    # Custom create method (can be extended later if needed)
    def create(self, validated_data):
        return Board.objects.create(**validated_data)

    # Returns the number of members in the board
    def get_member_count(self, obj):
        return obj.members.count()

    # Returns the number of tickets (currently same as member count — may need correction)
    def get_ticket_count(self, obj):
        return obj.members.count()  # Possibly incorrect logic — see note below

    # Returns the number of tasks with any status (currently no status filter applied)
    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter().count()  # No filter means it returns all tasks

    # Returns the number of tasks with high priority
    def get_task_high_priority_count(self, obj):
        return obj.tasks.filter(priority='high').count()



class BoardMemberSerializer(serializers.ModelSerializer):
    # Serializer for representing board members (User model)

    class Meta:
        model = User  # Refers to the custom or built-in User model
        fields = ['id', 'email', 'fullname']  # Fields to include in the serialized output



class TaskSerializer(serializers.ModelSerializer):
    # Computed fields for assignees, reviewers, and number of comments
    assignees = serializers.SerializerMethodField()
    reviewers = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task  # This serializer is based on the Task model
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority',
            'assignees', 'reviewers', 'due_date', 'comments_count'
        ]

    # Return a list of dictionaries with details of each assignee
    def get_assignees(self, obj):
        return [
            {
                'id': user.id,
                'email': user.email,
                'fullname': user.first_name  # Adjust if you use full name field
            }
            for user in obj.assignees.all()
        ]

    # Return a list of dictionaries with details of each reviewer
    def get_reviewers(self, obj):
        return [
            {
                'id': user.id,
                'email': user.email,
                'fullname': user.first_name  # Adjust if you use full name field
            }
            for user in obj.reviewers.all()
        ]

    # Return the total number of comments related to the task
    def get_comments_count(self, obj):
        return obj.comments.count() if hasattr(obj, 'comments') else 0

    
class TaskReviewSerializer(serializers.ModelSerializer):
    # Computed fields: list of reviewers and number of comments
    comments_count = serializers.SerializerMethodField()
    reviewers = serializers.SerializerMethodField()

    class Meta:
        model = Task  # This serializer is based on the Task model
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority',
            'reviewers', 'due_date', 'comments_count'
        ]

    # Return a list of dictionaries with details of each reviewer
    def get_reviewers(self, obj):
        return [
            {
                'id': user.id,
                'email': user.email,
                'fullname': user.first_name  # Use full name if available
            }
            for user in obj.reviewers.all()
        ]

    # Return the total number of comments on this task
    def get_comments_count(self, obj):
        return obj.comments.count() if hasattr(obj, 'comments') else 0

    

class BoardDetailSerializer(serializers.ModelSerializer):
    # Serialize all members using the BoardMemberSerializer
    members = BoardMemberSerializer(many=True)

    # Serialize all tasks associated with the board using TaskSerializer
    # 'source="tasks.all"' ensures that all related tasks are included
    tasks = TaskSerializer(many=True, source='tasks.all')

    # Include the owner's user ID as a plain integer field
    owner_id = serializers.IntegerField(source='owner.id')

    class Meta:
        model = Board  # This serializer is based on the Board model
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']

class CommentSerializer(serializers.ModelSerializer):
    # Returns the author's first name using a custom method
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment  # This serializer is based on the Comment model
        fields = ['id', 'created_at', 'author', 'content']  # Fields to be included in the output

    # Custom method to get the author's first name
    def get_author(self, obj):
        return obj.author.first_name  # Adjust if you prefer full name or email

