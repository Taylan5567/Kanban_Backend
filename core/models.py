from django.db import models
from auth_app.models import User

class Board(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='board_members', blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boards_owned')
    member_count = models.IntegerField(default=0)
    ticket_count = models.PositiveIntegerField(default=0)
    tasks_to_do_count = models.PositiveIntegerField(default=0)
    task_high_priority_count = models.PositiveIntegerField(default=0)


    def __str__(self):
        return self.title


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('to_do', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('review', 'Review'),
    ]

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=100)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    assignees = models.ManyToManyField(User, blank=True, related_name='assigned_tasks')
    reviewers = models.ManyToManyField(User, blank=True, related_name='reviewed_tasks')
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to_do')

    def __str__(self):
        return f"{self.title}: {self.description[:50]}"


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments_written')
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author}: {self.content}"