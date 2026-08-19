from django.urls import path
from .views import (Subject_Content_IN_SYSTEM_Active, Subject_Content_IN_SYSTEM_Inactive, ContentAllView, Writescore, \
                    Role_typeList, RoletypeupdateAPIView, RoletypeGetAPIView, Roletypedelete, Content_teacherList, \
                    Content_teacherdelete, Content_teacherGetAPIView, Content_group_view, \
                    Task_typeList, Task_typeupdateAPIView, Task_typeGetAPIView, Task_typedelete, \
                    ContentCount, GetTrainingTypeView, ChangeTrainingType_Content,DeleteContentTeacher,Content_teacher_subjectView)
from .autoclickview import GetRoletype

urlpatterns = [

    path('getcontent/subjects/active/get/', Subject_Content_IN_SYSTEM_Active.as_view()),
    path('getcontent/subjects/inactive/get/', Subject_Content_IN_SYSTEM_Inactive.as_view()),
    path('getcontent/all/', ContentAllView.as_view()),
    # path('content/check/score/', Writescore.as_view()),

    # path('roletype/', Role_typeList.as_view()),
    # path('roletype/update/<str:pk>', RoletypeupdateAPIView.as_view()),  # method put,patch
    # path('roletype/delete/', Roletypedelete.as_view()),
    # path('roletype/get/<str:pk>', RoletypeGetAPIView.as_view()),  # method get
    # path('roletype/hemis/get/', GetRoletype.as_view()),

    path('content_teacher/', Content_teacherList.as_view()),
    # path('content_teacher/update/<str:pk>', Content_teacherupdateAPIView.as_view()),  # method put,patch
   # path('content_teacher/delete/', Content_teacherdelete.as_view()),
    path('content_teacher/get/<str:pk>', Content_teacherGetAPIView.as_view()),  # method get
    # path('content_teacher/hemis/get/', GetRoletype.as_view()),

    path('content_group/', Content_group_view.as_view()),

    path('tasktype/', Task_typeList.as_view()),
    path('tasktype/update/<str:pk>', Task_typeupdateAPIView.as_view()),  # method put,patch
    path('tasktype/delete/', Task_typedelete.as_view()),
    path('tasktype/get/<str:pk>', Task_typeGetAPIView.as_view()),  # method get

    path('content/count/', ContentCount.as_view()),
    path('training/getlist/', GetTrainingTypeView.as_view()),
    path('content_teacher/list/<uuid:pk>',Content_teacher_subjectView.as_view()),
    path('content_teacher/edite/<uuid:pk>', ChangeTrainingType_Content.as_view()),
    path('content_teacher/delete/<uuid:pk>', DeleteContentTeacher.as_view())
]
