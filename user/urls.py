from django.urls import path
from .views import (
    LoginView,
    LogOutView,
    ChangePasswordView,
    AdminListAPIView,
    TokenRefreshAPIView,
    AdminDetailAPIView,
    ChangeUserInformationAPIView,
    UsersListAPIView,
)

urlpatterns = [
    # User CRUD APIs
    path('admin/admins-list/', AdminListAPIView.as_view()),
    path('admin/users-list/', UsersListAPIView.as_view()),
    path('admin/account/me/', AdminDetailAPIView.as_view()),
    path('admin/login/', LoginView.as_view()),
    path('admin/token/refresh/', TokenRefreshAPIView.as_view()),
    path('token/refresh/', TokenRefreshAPIView.as_view()),
    path('admin/logout/', LogOutView.as_view()),
    path('logout/', LogOutView.as_view()),
    path('admin/change-password/', ChangePasswordView.as_view()),
    path('admin/change-information/', ChangeUserInformationAPIView.as_view()),
]
