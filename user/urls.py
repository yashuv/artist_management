from django.urls import path
from .views import (
    DashboardViewAPIView,
    RegisterViewAPIView,
    LoginViewAPIView,
    LogoutView,
    ViewUsersAPIView,
    ViewUserAPIView,
    UpdateUserAPIView,
    DeleteUserAPIView,
)

urlpatterns = [
    path("", DashboardViewAPIView.as_view(), name="dashboard"),
    path("user/register/", RegisterViewAPIView.as_view(), name="user_register"),
    path("user/login/", LoginViewAPIView.as_view(), name="user_login"),
    path("user/logout/", LogoutView, name="user_logout"),
    path("user/<int:pk>/", ViewUserAPIView.as_view(), name="user_view"),
    path("all/", ViewUsersAPIView.as_view(), name="user_all"),
    path("user/edit/<int:pk>/", UpdateUserAPIView.as_view(), name="user_modify"),
    path("user/delete/<int:pk>/", DeleteUserAPIView.as_view(), name="user_delete"),
]
