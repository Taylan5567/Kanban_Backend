from rest_framework import serializers
from core.models import Board, Task, Comment
from django.contrib.auth.models import User

class BoardSerializer(serializers.ModelSerializer):
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
            'members'
        ]
        extra_kwargs = {
            'owner': {'read_only': True}  
        }

    def create(self, validated_data):
        return Board.objects.create(**validated_data)

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.members.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter().count()  

    def get_task_high_priority_count(self, obj):
        return obj.tasks.filter(priority='high').count()



class BoardMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = User 
        fields = ['id', 'email', 'fullname'] 



class TaskSerializer(serializers.ModelSerializer):
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

        return [
            {
                'id': user.id,
                'email': user.email,
                'fullname': user.first_name  
            }
            for user in obj.assignees.all()
        ]
    
    def get_reviewers(self, obj):
        return [
            {
                'id': user.id,
                'email': user.email,
                'fullname': user.first_name 
            }
            for user in obj.reviewers.all()
        ]

    def get_comments_count(self, obj):
        return obj.comments.count() if hasattr(obj, 'comments') else 0

    
class TaskReviewSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField()
    reviewers = serializers.SerializerMethodField()

    class Meta:
        model = Task  
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority',
            'reviewers', 'due_date', 'comments_count'
        ]

    def get_reviewers(self, obj):
        return [
            {
                'id': user.id,
                'email': user.email,
                'fullname': user.first_name  
            }
            for user in obj.reviewers.all()
        ]

    def get_comments_count(self, obj):
        return obj.comments.count() if hasattr(obj, 'comments') else 0

    

class BoardDetailSerializer(serializers.ModelSerializer):
    members = BoardMemberSerializer(many=True)
    tasks = TaskSerializer(many=True, source='tasks.all')
    owner_id = serializers.IntegerField(source='owner.id')

    class Meta:
        model = Board  
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment  
        fields = ['id', 'created_at', 'author', 'content']  

    def get_author(self, obj):
        """
        Returns the first name of the author of a comment.

        Args:
            obj (Comment): The Comment instance for which the author's first name is to be retrieved.

        Returns:
            str: The first name of the author of the comment.
        """
        return obj.author.first_name 

