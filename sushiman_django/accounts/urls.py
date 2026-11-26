from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('refresh/', views.RefreshView.as_view(), name='refresh_token'),
    path('csrf/', views.CsrfTokenView.as_view(), name='csrf_token'),
    path('register/', views.RegisterUserView.as_view(), name='register_user'),
    path('login/', views.UserLoginView.as_view(), name='login_user'),
    path('profile/me/', views.UserProfileView.as_view(), name='profile_user'),
]