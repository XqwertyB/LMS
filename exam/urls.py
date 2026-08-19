from django.urls import path
from .views import (
    ExamCreateAPIView,
    ExamGroupUpdateView,
    ExamStatusApiView,
    ExamListsAPIView,
    ExamUpdateFullAPIView,
    QuestionAPIView,
    QAAPIView,
    DetailExamApiView,
    ResultList,
    ResultCreateAPIView,
    ExamDeleteGroupUpdateView,
    ResultListForGroup,
    ExamStudentUpdateStatusAPIView,
    QuestionUpdateAPIView,
    QuestionDetailGetAPIView,
    QuestionGetListApiView,
    ExamDeleteAPIView,
    ExamListForStudent,
    ResultListForExam,
    QuestionDeleteAPIView,
    StudentExamAnswerUpdateAPIView,
    CorrectAnswersCountAPIView,
    IsSelectedAnswersAPIView,
    ResultListForStudent,
    IsStudentSelectedAnswersProfileAPIView,
    ExamListForIsFinishStudent,
    SeansDeleteAPIView,
    CheckContinue,
    IsLogoutApiView,
    TexnikAPIView,
    CheckAttemptsAPIView
)

urlpatterns = [
    # test endpoint
    path('test/create', QuestionAPIView.as_view(), name='test-create'),
    path('test/<uuid:exam>/list', QuestionGetListApiView.as_view(), name='test-list'),
    path('test/<uuid:pk>/get', QuestionDetailGetAPIView.as_view(), name='test-get'),
    path('test/<uuid:pk>/delete', QuestionDeleteAPIView.as_view(), name='test-delete'),
    path('test/<uuid:pk>/update', QuestionUpdateAPIView.as_view(), name='test-update'),
    path('test/begin/', QAAPIView.as_view(), name='test-get'),
    # path('test/<uuid:exam>/for/<uuid:student>/', QAAPIView.as_view(), name='test-get'),

    # exam endpoint
    path('exam/create', ExamCreateAPIView.as_view(), name='exam-create'),
    path('exam/<uuid:pk>/delete', ExamDeleteAPIView.as_view(), name='exam-delete'),
    path('exams', ExamListsAPIView.as_view(), name='exam-list'),
    path('exam-detail/<uuid:pk>', DetailExamApiView.as_view(), name='exam-detail'),
    path('exam/<uuid:pk>/update', ExamUpdateFullAPIView.as_view(), name='exam-update'),
    path('exam-status/<uuid:pk>', ExamStatusApiView.as_view(), name='exam-status'),
    path('exam/<uuid:pk>/student-status/<uuid:student_id>/', ExamStudentUpdateStatusAPIView.as_view(),
         name='exam-status-student'),
    path('exam/<uuid:id>/update-groups', ExamGroupUpdateView.as_view(), name='exam-update-groups'),
    path('exam/<uuid:id>/delete-groups', ExamDeleteGroupUpdateView.as_view(), name='exam-delete-groups'),

    # result endpoint
    path('result/create', ResultCreateAPIView.as_view(), name='result-create'),
    path('result', ResultList.as_view(), name='result-list'),
    path('result/<uuid:exam_id>/group/<uuid:group_id>/', ResultListForGroup.as_view(), name='result-list'),
    path('result/<uuid:exam_id>/student/<uuid:student_id>/', ResultListForStudent.as_view(),
         name='result-list-student'),
    path('result-exam/<uuid:exam_id>/', ResultListForExam.as_view(), name='result-list-exam'),

    # exam-for-student
    path('exam-list/<uuid:student>', ExamListForStudent.as_view(), name='exam-for-student'),
    path('exam-list-finish/<uuid:student>', ExamListForIsFinishStudent.as_view(), name='exam-for-student-finish'),
    path('student-exam-answers/<uuid:exam_id>/for/<uuid:student_id>/', StudentExamAnswerUpdateAPIView.as_view(),
         name='studentexamanswer-list'),
    path('student-select-answers-get/<uuid:exam_id>/for/<uuid:student_id>/', IsSelectedAnswersAPIView.as_view(),
         name='studentexamanswer-list-get'),
    path('student-select-answers-get-profile/<uuid:exam_id>/for/<uuid:student_id>/',
         IsStudentSelectedAnswersProfileAPIView.as_view(),
         name='studentexamanswer-list-get-profile'),

    path('exam-finish/<uuid:exam_id>/finish/<uuid:student_id>/', CorrectAnswersCountAPIView.as_view(),
         name='exam-finish'),

    # Seans

    path('exam-seans/', SeansDeleteAPIView.as_view(), name='exam-seans'),
    path('check-continue/', CheckContinue.as_view(), name='check-continue'),
    path('check-logout/', IsLogoutApiView.as_view(), name='check-logout'),
    path('cut-seans/', TexnikAPIView.as_view(), name='cat-logout'),
    path('check-attempts/<uuid:student_id>/for/<uuid:exam_id>', CheckAttemptsAPIView.as_view(), name='check-attempts'),

]
