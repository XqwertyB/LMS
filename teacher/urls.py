from django.urls import path
from .views import (
    Teacher_Contents_get, Teacher_Content_get,
    Teacher_View_Topic, Teacher_Active_Topic, Teacher_Add_Topic,
    Teacher_get_basic_id, Teacher_change_Topic, Topic_Video_Add,
    Topic_View, Topic_File_Add, Topic_Video_Delete,
    Topic_File_Delete, Topic_bigbluebutton_create,
    Task_list_students, Task_student_mark,
    Bigbluebutton_check_session,
    Bigbluebutton_restart,
    Bigbluebutton_check_session_restart,
    Topic_bigbluebutton_view,
    TaskViewTeacher,
    TaskdetailTeacher,
    TaskcreateTeacher,
    Taskfileadd,
    TaskupdateTeacher,
    Taskfiledelete,
    Taskgroupview,
    Taskstudentview,
    Taskgoupadd,
    Taskgoupdelete,
    TaskCreatewithfile,
    Taskactionstudentview,
    Task_student_actions_change,
    Taskfupdateview,
    GetScorelimit,
    GetScoreTopiclimit,
    Room_list_View, Content_teacher_list_View,
    Room_Lesson_Create_View, Room_Lesson_Update_View, LessonRoom_bbb_create
    # Teacher_Topic_count
)

urlpatterns = [

    path('teacher_content/', Teacher_Contents_get.as_view()),  # filterlab olish
    path('teacher_contents/', Teacher_Content_get.as_view()),  # shu oqtuvchga birktrilgan fanlar barchasini olish

    path('teacher_topics/', Teacher_View_Topic.as_view()),
    # Content yani fanga tegishli kontentlar o`qtuvchi orqali filter qilib olish
    path('teacher_topic/active/', Teacher_Active_Topic.as_view()),
    # Yartilgan mavzu topic id orqali falolni yoki faolmasni ocrish

    path('teacher_topic/add/', Teacher_Add_Topic.as_view()),
    path('teacher_topic/change/<str:pk>/', Teacher_change_Topic.as_view()),
    path('teacher_get_basic_id/', Teacher_get_basic_id.as_view()),
    #  path('teacher_topic/count/', Teacher_Topic_count.as_view()),

    path('teacher_topic/view/', Topic_View.as_view()),
    path('teacher_topic/add/video/', Topic_Video_Add.as_view()),
    path('teacher_topic/delete/video/', Topic_Video_Delete.as_view()),
    path('teacher_topic/add/file/', Topic_File_Add.as_view()),
    path('teacher_topic/delete/file/', Topic_File_Delete.as_view()),

    path('teacher/bigbluebutton/view/<str:pk>', Topic_bigbluebutton_view.as_view()),
    path('teacher/bigbluebutton/create/', Topic_bigbluebutton_create.as_view()),
    path('teacher/bigbluebutton/check_session/', Bigbluebutton_check_session.as_view()),
    path('teacher/bigbluebutton/restart/<str:pk>', Bigbluebutton_restart.as_view()),
    path('teacher/bibluebutton/check_session/restart/', Bigbluebutton_check_session_restart.as_view()),
    path('teacher_task_list/students/', Task_list_students.as_view()),
    # path('teacher_task_list/students/',) Filter keyin
    path('teacher_task/student/mark/', Task_student_mark.as_view()),

    # Task
    # path('teacher/task/create/', TaskcreateTeacher.as_view()),  # +
    path('teacher/task/<uuid:task_id>/add_file/', Taskfileadd.as_view()),  # +
    path('teacher/task/<uuid:task_id>/<int:teacher_id>/delete_file/<uuid:pk>', Taskfiledelete.as_view()),  # +
    path('teacher/task/view/', TaskViewTeacher.as_view()),
    path('teacher/task/detail/<uuid:pk>', TaskdetailTeacher.as_view()),
    # path('teacher/task/<uuid:pk>/update/', TaskupdateTeacher.as_view()),
    path('teacher/task/group/view/', Taskgroupview.as_view()),
    path('teacher/task/student/view/', Taskstudentview.as_view()),
    path('teacher/task/<uuid:task_id>/<uuid:group_id>/student_action/view/', Taskactionstudentview.as_view()),
    path('teacher/task/<uuid:task_id>/group/add/', Taskgoupadd.as_view()),
    path('teacher/task/<uuid:task_id>/<int:teacher_id>/group/<uuid:pk>/delete/', Taskgoupdelete.as_view()),
    # path('teacher/task/<uuid:task_id>/student/add',Taskstudentadd.as_view()),
    path('teacher/task/fcreate/', TaskCreatewithfile.as_view()),
    path('teacher/task/fupdate/<uuid:pk>/', Taskfupdateview.as_view()),
    path('teacher/task/<uuid:task_id>/<uuid:group_id>/student/status_change/<uuid:pk>/',
         Task_student_actions_change.as_view()),
    path('teacher/task/score/', GetScorelimit.as_view()),
    path('teacher/topic/score/', GetScoreTopiclimit.as_view()),
    path('content_teacher/teacher/list/', Content_teacher_list_View.as_view()),
    #   qo`shilgan Roomlar
    path('lessonroom/', Room_list_View.as_view()),
    path('lessonroom/create/', Room_Lesson_Create_View.as_view()),
    path('lessonroom/get/<uuid:pk>',Room_Lesson_Update_View.as_view()),
    #zoom!
    path('lessonroom/bbb/create/',LessonRoom_bbb_create.as_view()),




]
