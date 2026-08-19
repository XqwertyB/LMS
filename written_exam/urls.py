from django.urls import path

from written_exam.another_views.admin_view.views import AdminResetStudentExamDeviceAPIView
from written_exam.another_views.student_view import views as student_views
from written_exam.another_views.teacher_view import views as teacher_views
from written_exam.another_views.admin_view import views as admin_views

urlpatterns = [
    # O‘qitchi uchun savol va savol to‘plamlari CRUD endpointlari

    path("teacher-collections/", teacher_views.QuestionCollectionListAPIView.as_view()),
    path("teacher-collections/create/", teacher_views.QuestionCollectionCreateAPIView.as_view()),
    path("teacher-collections/<uuid:pk>/", teacher_views.QuestionCollectionUpdateAPIView.as_view()),
    path("teacher-collections/<uuid:pk>/delete/", teacher_views.QuestionCollectionDeleteAPIView.as_view()),
    path("teacher-questions/", teacher_views.QuestionListAPIView.as_view()),
    path("teacher-questions/create/", teacher_views.QuestionCreateAPIView.as_view()),
    path("teacher-questions/<uuid:pk>/update/", teacher_views.QuestionUpdateAPIView.as_view()),
    path("teacher-questions/<uuid:pk>/detail/", teacher_views.QuestionDetailAPIView.as_view()),
    path("teacher-questions/<uuid:pk>/delete/", teacher_views.QuestionDeleteAPIView.as_view()),
    path("teacher-exams/list/", teacher_views.TeacherExamListAPIView.as_view()),
    path("teacher-exams/<uuid:exam_id>/question-requirements/",
         teacher_views.TeacherExamQuestionRequirementAPIView.as_view()),
    path("teacher/exams/<uuid:exam_id>/add-questions/",
         teacher_views.TeacherExamAddQuestionsAPIView.as_view()),
    path("teacher-written-exams/questions/", teacher_views.WrittenExamQuestionListAPIView.as_view()),
    path("teacher-written-exams/<uuid:exam_id>/questions/<uuid:question_id>/remove/",
         teacher_views.WrittenExamQuestionDeleteAPIView.as_view()),

    path("teacher-written-exams/<uuid:exam_id>/results/", teacher_views.ExamResultsAPIView.as_view()),
    path("teacher-written-exams/<uuid:exam_id>/students/<uuid:student_id>/attempt/",
         teacher_views.ExamStudentLastAttemptAPIView.as_view()),
    path("teacher-written-exams/grade-answer/", teacher_views.GradeAttemptAPIView.as_view()),
    path("teacher-written-exams/<uuid:exam_id>/groups/", teacher_views.ExamGroupsAPIView.as_view()),

    # Yozma imtihon yaratish endpointi

    path('admin-written-exams/list/', admin_views.WrittenExamListAPIView.as_view()),
    path('admin-written-exams/create/', admin_views.WrittenExamCreateAPIView.as_view()),
    path("admin-written-exams/<uuid:pk>/update-status/", admin_views.WrittenExamStatusUpdateAPIView.as_view()),
    path("admin-written-exams/<uuid:pk>/detail/", admin_views.WrittenExamDetailAPIView.as_view()),
    path("admin-written-exams/<uuid:exam_id>/groups/", admin_views.AdminExamGroupStatsAPIView.as_view()),
    path("admin-written-exams/<uuid:exam_id>/group/<uuid:group_id>/students/",
         admin_views.AdminExamGroupStatsAPIView.as_view()),
    path("admin-written-exams/<uuid:pk>/update/", admin_views.WrittenExamUpdateAPIView.as_view()),
    path("admin-written-exam/<uuid:pk>/delete/", admin_views.WrittenExamDeleteAPIView.as_view()),
    path("admin-written-exams/assign-groups/", admin_views.AssignGroupsToExamAPIView.as_view()),
    path("admin-written-exams/remove-group/", admin_views.RemoveGroupFromExamAPIView.as_view()),
    path("admin-written-exams/access-students/", admin_views.ExamAccessStudentListAPIView.as_view()),
    path("admin-written-exams/update-access-status/", admin_views.UpdateExamAccessStatusAPIView.as_view()),
    path("admin-written-exams/<uuid:exam_id>/questions/", admin_views.ExamQuestionShow.as_view()),

    path("admin-written-exams/<uuid:exam_id>/results/", admin_views.ExamResultAPIView.as_view()),
    path("admin-written-exams/<uuid:exam_id>/logs/", admin_views.ExamLogsAPIView.as_view()),

    path(
        "admin-written-exams/<uuid:exam_id>/students/<uuid:student_id>/device-reset/", AdminResetStudentExamDeviceAPIView.as_view(),
    ),

    # Yozma imtihon talaba endpointi
    path('student-written-exams/list/', student_views.StudentExamList.as_view()),
    path('student-written-exams/<uuid:exam_id>/name/', student_views.StudentExamNameAPIView.as_view()),
    path('student-written-exams/<uuid:exam_id>/start/', student_views.StudentStartExamView.as_view()),
    path('student-written-exams/<uuid:exam_id>/questions/', student_views.ExamQuestionsAPIView.as_view()),
    path('student-written-exams/<uuid:question_id>/question/', student_views.ExamOneQuestionAPIView.as_view()),
    path('student-written-exams/save-answer/', student_views.SaveAnswerAPIView.as_view()),
    path('student-written-exams/<uuid:exam_id>/timer/', student_views.ExamTimeAPIView.as_view()),
    path('student-written-exams/finish/', student_views.FinishExamAPIView.as_view()),
    path('student-written-exams/activity/', student_views.ExamActivityView.as_view()),
    path('student-written-exams/results/', student_views.StudentExamResultListAPIView.as_view()),
]
