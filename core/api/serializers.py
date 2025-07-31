from rest_framework import serializers
from core.models import Board, Task
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
            ]
        extra_kwargs = {
            'owner': {'read_only': True}
        }

    def create(self, validated_data):
        return Board.objects.create( **validated_data)

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
    assignee = serializers.SerializerMethodField()
    reviewer = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer', 'due_date', 'comments_count'
        ]

    def get_assignee(self, obj):
        if obj.assignee:
            return {
                'id': obj.assignee.id,
                'email': obj.assignee.email,
                'fullname': obj.assignee.fullname
            }
        return None

    def get_reviewer(self, obj):
        if obj.reviewer:
            return {
                'id': obj.reviewer.id,
                'email': obj.reviewer.email,
                'fullname': obj.reviewer.fullname
            }
        return None

    def get_comments_count(self, obj):
        return obj.comments.count() 
    

class BoardDetailSerializer(serializers.ModelSerializer):
    members = BoardMemberSerializer(many=True)
    tasks = TaskSerializer(many=True)
    owner_id = serializers.IntegerField(source='owner.id')

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']
