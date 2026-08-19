from django.urls import path

from .views import (
    ScreenModelAPIView,
    ScreenListsAPIView,
    ScreenDetailView
)

urlpatterns = [
    path('autoproctor/create/', ScreenModelAPIView.as_view()),
    path('autoproctor/list/', ScreenListsAPIView.as_view()),
    path('autoproctor/<uuid:student_id>/detail/<uuid:exam_id>/', ScreenDetailView.as_view())
]
