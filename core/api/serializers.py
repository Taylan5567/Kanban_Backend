from rest_framework import serializers
from core.models import Board
from django.contrib.auth.models import User

class BoardSerializer(serializers.ModelSerializer): 
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

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter().count()


