from django.urls import path
from .views import (
    BoardListView, EmailCheckView, MyTasksAssignedView, TaskCreateView,
    BoardDetailsView, MyTasksReviewsView, MyTaskDetailsView,
    CommentView, CommentDetailView
)
from auth_app.api.views import RegistrationView, LoginView

urlpatterns = [
    # User registration and login endpoints
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),

    # Board endpoints
    path('boards/', BoardListView.as_view(), name='board_list'),  # Create & list boards
    path('boards/<int:board_id>/', BoardDetailsView.as_view()),   # Retrieve, update, or delete a specific board

    # Email existence check
    path('email-check/', EmailCheckView.as_view(), name='email_check'),

    # Task creation
    path('tasks/', TaskCreateView.as_view(), name="task_create"),

    # Get tasks assigned to the authenticated user
    path('tasks/assigned-to-me/', MyTasksAssignedView.as_view(), name='assigned_to_me'),

    # Get tasks the authenticated user is reviewing
    path('tasks/reviewing/', MyTasksReviewsView.as_view(), name='assigned_to_me'),  # 🔁 note: name is reused

    # Retrieve, update, or delete a specific task
    path('tasks/<int:task_id>/', MyTaskDetailsView.as_view(), name='details-task'),

    # Add or list comments for a task
    path('tasks/<int:task_id>/comments/', CommentView.as_view(), name='comment'),

    # Delete a specific comment from a task
    path('tasks/<int:task_id>/comments/<int:comments_id>/', CommentDetailView.as_view(), name='comment-detail'),
]
