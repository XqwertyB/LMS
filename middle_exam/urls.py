from django.urls import path
from .views import ALL_GET_MIDDLE_EXAM

urlpatterns = [
    path('teacher/middle/<uuid:connect_id>',ALL_GET_MIDDLE_EXAM.as_view())
]
