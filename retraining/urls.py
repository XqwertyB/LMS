from django.urls import path, include
from . import views
from .views import TextTestQuestionsAPIView

app_name = 'retraining'

urlpatterns = [
    path('groups/', include([
        path('', views.ReTrainingGroupListCreateAPIView.as_view(), name='group-list-create'),
        path('<uuid:pk>/', views.ReTrainingGroupDetailAPIView.as_view(), name='group-detail'),
        path('<uuid:group_pk>/students/', views.ReTrainingStudentListAPIView.as_view(), name='group-students'),
        path('<uuid:group_pk>/students/add/', views.ReTrainingStudentAddToGroupAPIView.as_view(), name='add-student-to-group'),
        path('<uuid:group_pk>/students/<uuid:student_pk>/remove/', views.ReTrainingStudentRemoveFromGroupAPIView.as_view(), name='remove-student-from-group'),
        path('groups/<uuid:pk>/start-meeting/', views.ReTrainingGroupStartMeetingAPIView.as_view(), name='group-start-meeting'),

    ])),

    path('students/', include([
        path('add/', views.ReTrainingStudentAddAPIView.as_view(), name='student-add'),
        path('<uuid:pk>/', views.ReTrainingStudentDetailAPIView.as_view(), name='student-detail'),
        path('bulk/', views.BulkStudentAddAPIView.as_view(), name='bulk-students'),
    ])),

    path('assignments/', include([
        path('', views.AssignmentListCreateAPIView.as_view(), name='assignment-list-create'),
        path('<uuid:id>/', views.AssignmentDetailAPIView.as_view(), name='assignment-detail'),
       # path('<uuid:pk>/submit/', views.AssignmentSubmitAPIView.as_view(), name='assignment-submit'),
        path('<uuid:pk>/statistics/', views.AssignmentStatisticsAPIView.as_view(), name='assignment-statistics'),
        path('<uuid:pk>/results/', views.AssignmentResultsAPIView.as_view(), name='assignment-results'),
        path('<uuid:id>/upload-file/', views.TeacherUploadAssignmentFileAPIView.as_view(), name='assignment-upload-file'),
        path('<uuid:pk>/export-pdf/', views.ExportAssignmentStatisticsPDFAPIView.as_view(), name='assignment_export_pdf'),
    ])),

  #  path('submissions/<uuid:pk>/grade/', views.GradeSubmissionAPIView.as_view(), name='grade-submission'),

    path('tests/', include([
        path('start/', views.TestTakeAPIView.as_view(), name='test-start'),
        path('submit/', views.TestSubmitAPIView.as_view(), name='test-submit'),
        path('<uuid:assignment_id>/questions/', views.TestQuestionsAPIView.as_view(), name='test-questions'),

        path('questions/<uuid:assignment_id>/', TextTestQuestionsAPIView.as_view()),
    ])),

    path('my-assignments/', views.StudentAssignmentListAPIView.as_view(), name='student-assignments'),
    path('my-results/', views.StudentResultsAPIView.as_view(), name='student-results'),
]


