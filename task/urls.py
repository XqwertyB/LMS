from django.urls import path
from .views import GetTasksView, GetListGroupByTopic, GetListStudentbyTopic, CreateGroupTask, GetOneTask, UpdateTask

urlpatterns = [
    path('tasks/view/', GetTasksView.as_view()),
    path('tasks/groups/', GetListGroupByTopic.as_view()),
    path('tasks/group/students/', GetListStudentbyTopic.as_view()),
    path('tasks/create/', CreateGroupTask.as_view()),
    path('tasks/get/<str:pk>',GetOneTask.as_view()),
    path('tasks/update/<str:pk>',UpdateTask.as_view()),

]
