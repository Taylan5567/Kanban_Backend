from django.db import models
from auth_app.models import User

# Represents a project board (e.g., for tasks, like in a Kanban board)
class Board(models.Model):
    """
    Model representing a project board that organizes tasks
    and can be shared among multiple users.

    Attributes:
        id (int): Primary key of the board.
        title (str): Name of the board.
        members (ManyToMany): Users who are members of the board.
        owner (ForeignKey): The user who owns (created) the board.
        member_count (int): Number of members in the board.
        ticket_count (int): Number of tasks (tickets) on the board.
        tasks_to_do_count (int): Number of tasks with status 'to-do'.
        task_high_priority_count (int): Number of tasks with high priority.
    """

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    members = models.ManyToManyField(
        User,
        related_name='board_members',
        blank=True
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='boards_owned'
    )
    member_count = models.IntegerField(default=0)
    ticket_count = models.PositiveIntegerField(default=0)
    tasks_to_do_count = models.PositiveIntegerField(default=0)
    tasks_high_prio_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        """
        Returns a human-readable representation of the board,
        typically used in the Django admin panel and logs.
        """
        return self.title

# Represents a task or ticket inside a board
class Task(models.Model):
    """
    Model representing a task within a board.

    Attributes:
        board (ForeignKey): The board this task belongs to.
        title (str): Title of the task.
        description (str): Detailed description of the task.
        priority (str): Priority level of the task (low, medium, high).
        assignees (ManyToMany): Users assigned to work on the task.
        reviewers (ManyToMany): Users responsible for reviewing the task.
        due_date (date): Optional due date for the task.
        status (str): Current status of the task 
                      (to-do, in-progress, done, review).
    """

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('to-do', 'to-do'),
        ('in-progress', 'in-progress'),
        ('done', 'done'),
        ('review', 'review'),
    ]

    board = models.ForeignKey(
        'Board',
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    assignees = models.ManyToManyField(
        User,
        related_name='assigned_tasks'
    )
    reviewers = models.ManyToManyField(
        User,
        related_name='reviewed_tasks'
    )
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='to-do'
    )

    def __str__(self):
        """
        Returns a short, readable string representation of the task,
        including the title and a preview of the description.
        """
        return f"{self.title}: {self.description[:50]}"

class Comment(models.Model):
    """
    Model representing a comment on a task.

    Attributes:
        id (int): Primary key of the comment.
        task (ForeignKey): The task that this comment belongs to.
        author (ForeignKey): The user who wrote the comment.
        content (str): The text content of the comment.
        created_at (datetime): Timestamp when the comment was created.
    """

    id = models.AutoField(primary_key=True)
    task = models.ForeignKey(
        'Task',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments_written'
    )
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a readable string representation of the comment.
        """
        return f"{self.author}: {self.content[:50]}"