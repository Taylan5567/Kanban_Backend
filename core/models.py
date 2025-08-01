from django.db import models
from auth_app.models import User

# Represents a project board (e.g., for tasks, like in a Kanban board)
class Board(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    title = models.CharField(max_length=100)  # Board title
    members = models.ManyToManyField(User, related_name='board_members', blank=True)
    # Users who are members of the board (excluding the owner)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boards_owned')
    # The user who created/owns the board
    member_count = models.IntegerField(default=0)  # Cached member count (for performance)
    ticket_count = models.PositiveIntegerField(default=0)  # Total number of tasks/tickets
    tasks_to_do_count = models.PositiveIntegerField(default=0)  # Number of 'to-do' tasks
    task_high_priority_count = models.PositiveIntegerField(default=0)  # Number of high priority tasks

    def __str__(self):
        return self.title  # String representation (used in admin, shell, etc.)

# Represents a task or ticket inside a board
class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('to-do', 'to-do'),
        ('in-progress', 'in-progress'),
        ('done', 'done'),
        ('review', 'review'),
    ]

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    # The board to which this task belongs
    title = models.CharField(max_length=100)  # Title of the task
    description = models.TextField()  # Detailed description of the task
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    # Task priority: low, normal, or high
    assignees = models.ManyToManyField(User, blank=True, related_name='assigned_tasks')
    # Users assigned to this task
    reviewers = models.ManyToManyField(User, blank=True, related_name='reviewed_tasks')
    # Users responsible for reviewing the task
    due_date = models.DateField(null=True, blank=True)  # Optional due date
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to_do')
    # Status of the task (e.g., to-do, in-progress, etc.)

    def __str__(self):
        return f"{self.title}: {self.description[:50]}"  # Short summary of the task

# Represents a comment left by a user on a task
class Comment(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    # The task this comment is associated with
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments_written')
    # The user who wrote the comment
    content = models.CharField(max_length=255)  # The comment text
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the comment was created

    def __str__(self):
        return f"{self.author}: {self.content}"  # Short summary of the comment
