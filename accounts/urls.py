from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

from accounts.views import UserCreateView, UserDetailView

app_name = "accounts"

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="register"),
    path("me/", UserDetailView.as_view(), name="user-detail"),
    # jwt
    path("token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/blacklist/", TokenBlacklistView.as_view(), name="token-blacklist"),
]
