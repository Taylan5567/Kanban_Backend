from django.urls import path
from .views import BoardListView, EmailCheckView, MyTasksView, TaskCreateView
from auth_app.api.views import RegistrationView, LoginView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('boards/', BoardListView.as_view(), name='board_list'),
    path('boards/<int:board_id>', BoardListView.as_view()),
    path('email-check/', EmailCheckView.as_view(), name='email_check'),
    path('tasks/', TaskCreateView.as_view(), name="task_create"),
    path('tasks/assigned-to-me/', MyTasksView.as_view(), name='assigned_to_me')
]
