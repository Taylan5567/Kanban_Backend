from django.urls import path
from .views import BoardListView
from auth_app.api.views import RegistrationView, LoginView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('boards/', BoardListView.as_view(), name='board_list'),
]
