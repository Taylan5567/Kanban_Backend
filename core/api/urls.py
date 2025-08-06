from django.urls import path
from .views import (
    BoardListView, EmailCheckView, MyTasksAssignedView, TaskCreateView,
    BoardDetailsView, MyTasksReviewsView, MyTaskDetailsView,
    CommentView, CommentDetailView
)
from auth_app.api.views import RegistrationView, LoginView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('boards/', BoardListView.as_view(), name='board_list'),
    path('boards/<int:board_id>/', BoardDetailsView.as_view()), 
    path('email-check/<str:email>/', EmailCheckView.as_view(), name='email_check'),
    path('tasks/', TaskCreateView.as_view(), name="task_create"),
    path('tasks/assigned-to-me/', MyTasksAssignedView.as_view(), name='assigned_to_me'),
    path('tasks/reviewing/', MyTasksReviewsView.as_view(), name='assigned_to_me'),
    path('tasks/<int:task_id>/', MyTaskDetailsView.as_view(), name='details-task'),
    path('tasks/<int:task_id>/comments/', CommentView.as_view(), name='comment'),
    path('tasks/<int:task_id>/comments/<int:comments_id>/', CommentDetailView.as_view(), name='comment-detail'),
]
