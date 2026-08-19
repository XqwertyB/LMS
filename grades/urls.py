from django.urls import path
from .views import SubjectCurriculumListAPIView, CreateGradeSheetView, CalculateJNView, ConnectGradeListView, \
    GradeDetailView, CalculateONView, CalculateYNView, StudentForGroupApiView

urlpatterns = [

    path("grade/subject-curriculum/", SubjectCurriculumListAPIView.as_view(), name="subject-curriculum-list"
         ),
    path("grades/list/", ConnectGradeListView.as_view()),
    path("grades/<uuid:connect_id>/detail/", GradeDetailView.as_view()),
    path("grades/create/", CreateGradeSheetView.as_view()),
    path("grades/<uuid:connect_id>/calculate-jn/", CalculateJNView.as_view()),
    path("grades/<uuid:connect_id>/calculate-on/", CalculateONView.as_view()),
    path("grades/<uuid:connect_id>/calculate-yn/", CalculateYNView.as_view()),

    path("grades/students/group/<uuid:group_id>", StudentForGroupApiView.as_view(), name="student-for-group"),
]
