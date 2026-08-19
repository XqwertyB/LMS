from django.urls import path
from .views import (
    SubjectgroupcreateList, SubjectgroupupdateAPIView, SubjectgroupGetAPIView, Subjectgroupedelete,
    SubjectcreateList, SubjectupdateAPIView, SubjectGetAPIView, Subjectdelete,
    Subject_blockcreateList, Subject_blockupdateAPIView, Subject_blockGetAPIView, Subject_blockdelete,
    Subject_typecreateList, Subject_typeupdateAPIView, Subject_typeGetAPIView, Subject_typedelete,
    Subject_exam_finishcreateList, Subject_exam_finishupdateAPIView, Subject_exam_finishGetAPIView,
    Subject_exam_finishdelete, SubjectsListApiView

)

from .autoclickview import (
    GetSubject, GetSubjectblock, GetSubject_exam_finish, GetSubjecttype, Getsubject_list,
    Getsubject_listNew, GetSubjectNew_versionList, OneCurriclumGetHemis, Getzerosubject_listNew)

urlpatterns = [

    path('subjectgroup/', SubjectgroupcreateList.as_view(), ),  # get,Post
    path('subjectgroup/update/<str:pk>', SubjectgroupupdateAPIView.as_view()),  # method put,patch
    path('subjectgroup/delete/', Subjectgroupedelete.as_view()),
    path('subjectgroup/get/<str:pk>', SubjectgroupGetAPIView.as_view()),  # method get
    # path('subjectgroup/hemis/get/', GetSubjecttype.as_view()),

    path('subject/', SubjectcreateList.as_view(), ),  # get,Post
    path('subject/update/<str:pk>', SubjectupdateAPIView.as_view()),  # method put,patch
    path('subject/delete/', Subjectdelete.as_view()),
    path('subject/get/<str:pk>', SubjectGetAPIView.as_view()),  # method get
    path('subject/hemis/get/', GetSubject.as_view()),

    path('subjectblock/', Subject_blockcreateList.as_view(), ),  # get,Post
    path('subjectblock/update/<str:pk>', Subject_blockupdateAPIView.as_view()),  # method put,patch
    path('subjectblock/delete/', Subject_blockGetAPIView.as_view()),
    path('subjectblock/get/<str:pk>', Subject_blockdelete.as_view()),  # method get
    path('subjectblock/hemis/get/', GetSubjectblock.as_view()),

    path('subjecttype/', Subject_typecreateList.as_view(), ),  # get,Post
    path('subjecttype/update/<str:pk>', Subject_typeupdateAPIView.as_view()),  # method put,patch
    path('subjecttype/delete/', Subject_typedelete.as_view()),
    path('subjecttype/get/<str:pk>', Subject_typeGetAPIView.as_view()),  # method get
    path('subjecttype/hemis/get/', GetSubjecttype.as_view()),

    path('subjectexamfinsh/', Subject_exam_finishcreateList.as_view(), ),  # get,Post
    path('subjectexamfinsh/update/<str:pk>', Subject_exam_finishupdateAPIView.as_view()),  # method put,patch
    path('subjectexamfinsh/delete/', Subject_exam_finishdelete.as_view()),
    path('subjectexamfinsh/get/<str:pk>', Subject_exam_finishGetAPIView.as_view()),  # method get
    path('subjectexamfinsh/hemis/get/', GetSubject_exam_finish.as_view()),

    path('subject_curriculum/hemis/get/', Getsubject_list.as_view()),
    path('subject_curriculum/hemis/get/full/', Getsubject_listNew.as_view()),
    path('subject_curriculum/zero/hemis/get/full/', Getzerosubject_listNew.as_view()),
    path('subject_curriculum/hemis/new/get/', GetSubjectNew_versionList.as_view()),
    path('subject_curriculum/hemis/getone/<int:cur_id>', OneCurriclumGetHemis.as_view()),
    path('subjects/curriculum/<uuid:curriculum_id>/smester/<uuid:semester_id>', SubjectsListApiView.as_view()),
]
