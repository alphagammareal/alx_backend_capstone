from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from .views import RegisterView, ProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    # JWT Login
    path('login/', TokenObtainPairView.as_view(), name='jwt-login'),
    path('refresh/', TokenRefreshView.as_view(), name='jwt-refresh'),
    # Profile
    path('profile/', ProfileView.as_view(), name='profile'),
]
