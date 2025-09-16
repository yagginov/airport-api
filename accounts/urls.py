from django.urls import path

from accounts.views import UserCreateView, UserDetailView

app_name = "accounts"

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="register"),
    path("me/", UserDetailView.as_view(), name="user-detail"),
]
