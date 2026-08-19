from django.urls import path

from .views import (
    APILogsListAPIView
)

urlpatterns = [
    path('logs/', APILogsListAPIView.as_view()),
]
