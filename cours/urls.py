from django.urls import path
from .views import ViewStudentSubjects_active, ViewStudentSubjects_inactive, ViewSutudentSubject_topic, \
    ViewSutudenttopic_one, ViewTaskStudents, ViewTasktake, ViewSutudentSubject_topic_task, Takebigbluebutton, \
    TaskcheckView, TasktimecheckView, ResultsView, Lesson_Room_list_View, TakebigbluebuttonLesson,Checkin_Join

urlpatterns = [
    path('student/content/get_all_active/', ViewStudentSubjects_active.as_view()),
    path('student/content/get_all_inactive/', ViewStudentSubjects_inactive.as_view()),
    path('student/content/topic/get_all/', ViewSutudentSubject_topic.as_view()),
    path('student/content/topic/task/get_all/', ViewSutudentSubject_topic_task.as_view()),  #####
    path('student/content/topic/one/', ViewSutudenttopic_one.as_view()),
    path('student/topic/tasks/', ViewTaskStudents.as_view()),
    path('student/task/', ViewTasktake.as_view()),
    path('student/topic/bigbluebutton/', Takebigbluebutton.as_view()),
    path('student/task/check/', TaskcheckView.as_view()),
    path('student/task/time-check/', TasktimecheckView.as_view()),
    path('student/results/',ResultsView.as_view()),
    path('student/lesson_room/',Lesson_Room_list_View.as_view()),
    path('student/lesson_room/bbb/',TakebigbluebuttonLesson.as_view()),
    path('student/lesson_room/bbb/attendee/',Checkin_Join.as_view()),
]
