from django.urls import path

from .views import LikeTeacherDetailAPIView
from .views import (
    OAuthCallbackView,
    OAuthAuthorizationView,
    GetTeacherApiView,
    GetTeacherSyncStatusAPIView,
    LikeTeacherApiView,
    GetTeacherLocalAPIView,
)

urlpatterns = [
    path('authorization', OAuthAuthorizationView.as_view(), name='oauth-authorization'),
    path('callback/<str:code>', OAuthCallbackView.as_view(), name='oauth-callback'),
    path('teachers/get/hemis', GetTeacherApiView.as_view(), name='get-hemis'),
    path(
        'teachers/get/hemis/status/<str:job_id>',
        GetTeacherSyncStatusAPIView.as_view(),
        name='get-hemis-status',
    ),
    path('teacher/get/<str:employee_id_number>', GetTeacherLocalAPIView.as_view(), name='get-hemis-local'),
    path('teacherlike/', LikeTeacherApiView.as_view(), name='teacher-filter'),
    path('teacherlike/<uuid:user_id>/detail/', LikeTeacherDetailAPIView.as_view(), name='teacher-filter-detail'),

]
