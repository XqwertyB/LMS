from django.urls import path
from .views import (
    EducationyearList, EducationyearGetAPIView, EducationyearupdateAPIView, Educationyeardelete,
    EducationtypeList, EducationtypeGetAPIView, EducationtypeupdateAPIView, Educationtypedelete,
    EducationformList, EducationformGetAPIView, EducationformupdateAPIView, Educationformdelete,
    MarkingSystemList, MarkingSystemGetAPIView, MarkingSystemupdateAPIView, MarkingSystemdelete,
    CurriculumList, CurriculumGetAPIView, CurriculumupdateAPIView, Curriculumdelete,
    Science_branchList, Science_branchGetAPIView, Science_branchupdateAPIView, Science_branchdelete,
    EducationlangList, EducationlangupdateAPIView, Educationlangdelete, EducationlangGetAPIView, GetCurriculumOne

)
from .autoclickview import GetEducationyear, GetEducationtype, GetEducationform, GetCurriculum, GetScience_branch, \
    GetEducationlang, GetOtherCurriculum, GetSrtqiCurriculum, GetQoshmaCurriculum, GetMasofa2Curriculum, \
    GetAllINCurriculum, GetCurriculum_active, GetCurriculum_activetoday, GetKundizgiCurriculum, \
    GetCurriculum_activeSkipe, GetSrtqi2Curriculum

urlpatterns = [
    path('educationyear/', EducationyearList.as_view(), ),  # get,Post
    path('educationyear/update/<str:pk>', EducationyearupdateAPIView.as_view()),  # method put,patch
    path('educationyear/delete/', Educationyeardelete.as_view()),
    path('educationyear/get/<str:pk>', EducationyearGetAPIView.as_view()),  # method get
    path('educationyear/hemis/get/', GetEducationyear.as_view()),
    # +
    path('educationtype/', EducationtypeList.as_view(), ),  # get,Post
    path('educationtype/update/<str:pk>', EducationtypeupdateAPIView.as_view()),  # method put,patch
    path('educationtype/delete/', Educationtypedelete.as_view()),
    path('educationtype/get/<str:pk>', EducationtypeGetAPIView.as_view()),  # method get
    path('educationtype/hemis/get/', GetEducationtype.as_view()),
    # +
    path('educationform/', EducationformList.as_view(), ),  # get,Post
    path('educationform/update/<str:pk>', EducationformupdateAPIView.as_view()),  # method put,patch
    path('educationform/delete/', Educationformdelete.as_view()),
    path('educationform/get/<str:pk>', EducationformGetAPIView.as_view()),  # method get
    path('educationform/hemis/get/', GetEducationform.as_view()),

    # +
    path('markingsystemList/', MarkingSystemList.as_view(), ),  # get,Post
    path('markingsystemList/update/<str:pk>', MarkingSystemupdateAPIView.as_view()),  # method put,patch
    path('markingsystemList/delete/', MarkingSystemdelete.as_view()),
    path('markingsystemList/get/<str:pk>', MarkingSystemGetAPIView.as_view()),  # method get
    #    path('educationform/hemis/get/', GetEducationform.as_view()),
    # +
    path('curriculum/', CurriculumList.as_view(), ),  # get,Post
    path('curriculum/update/<str:pk>', CurriculumupdateAPIView.as_view()),  # method put,patch
    path('curriculum/delete/', Curriculumdelete.as_view()),
    path('curriculum/get/<str:pk>', CurriculumGetAPIView.as_view()),  # method get
    path('curriculum/hemis/get/', GetCurriculum.as_view()),
    path('curriculum/hemis/get2/', GetOtherCurriculum.as_view()),
    path('curriculum/hemis/get/sirtqi/', GetSrtqiCurriculum.as_view()),
    path('curriculum/hemis/get/sirtqi2/', GetSrtqi2Curriculum.as_view()),

    path('curriculum/hemis/get/masofa2/', GetMasofa2Curriculum.as_view()),
    path('curriculum/hemis/get/qoshma/', GetQoshmaCurriculum.as_view()),
    path('curriculum/hemis/getall/in/', GetAllINCurriculum.as_view()),
    path('curriculum/hemis/getall/active/', GetCurriculum_active.as_view()),
    path('curriculum/hemis/getall/active/reason/', GetCurriculum_activeSkipe.as_view()),

    path('curriculum/hemis/getall/active/year/', GetCurriculum_activetoday.as_view()),
    path('curriculum/hemis/get/kunduzgi/', GetKundizgiCurriculum.as_view()),
    # +
    path('science_branch/', Science_branchList.as_view(), ),  # get,Post
    path('science_branch/update/<str:pk>', Science_branchupdateAPIView.as_view()),  # method put,patch
    path('science_branch/delete/', Science_branchdelete.as_view()),
    path('science_branch/get/<str:pk>', Science_branchGetAPIView.as_view()),  # method get
    path('science_branch/hemis/get/', GetScience_branch.as_view()),
    # +
    path('educationlang/', EducationlangList.as_view(), ),  # get,Post
    path('educationlang/update/<str:pk>', EducationlangupdateAPIView.as_view()),  # method put,patch
    path('educationlang/delete/', Educationlangdelete.as_view()),
    path('educationlang/get/<str:pk>', EducationlangGetAPIView.as_view()),  # method get
    path('educationlang/hemis/get/', GetEducationlang.as_view()),
    # +
    path('curriculum/get-info-name/<uuid:pk>', GetCurriculumOne.as_view()),

    # path('')
]
