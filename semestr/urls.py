from django.urls import path

from .service import GetZeroHsemesterAction
from .views import (
    HCourseList, HCourseGetAPIView, HCourseupdateAPIView, HCoursedelete,
    HsemesterList, HsemesterGetAPIView, HsemesterupdateAPIView, Hsemesterdelete,
    Hsemester_actionList, Hsemester_actionGetAPIView, Hsemester_actionupdateAPIView, Hsemester_actiondelete,
    SmesterCurrListApiView,

)

from .autoclickview import GetHCourse, GetHsemester, GetHsemesterAction,GetThisYearHsemesterAction

urlpatterns = [
    path('hcourse/', HCourseList.as_view(), ),  # get,Post
    path('hcourse/update/<str:pk>', HCourseupdateAPIView.as_view()),  # method put,patch
    path('hcourse/delete/', HCoursedelete.as_view()),
    path('hcourse/get/<str:pk>', HCourseGetAPIView.as_view()),  # method get
    path('hcourse/hemis/get/', GetHCourse.as_view()),

    path('hsemester/', HsemesterList.as_view(), ),  # get,Post
    path('hsemester/update/<str:pk>', HsemesterupdateAPIView.as_view()),  # method put,patch
    path('hsemester/delete/', Hsemesterdelete.as_view()),
    path('hsemester/get/<str:pk>', HsemesterGetAPIView.as_view()),  # method get
    path('hsemester/hemis/get/', GetHsemester.as_view()),

    path('hsemesteraction/', Hsemester_actionList.as_view(), ),  # get,Post
    path('hsemesteraction/update/<str:pk>', Hsemester_actionupdateAPIView.as_view()),  # method put,patch
    path('hsemesteraction/delete/', Hsemester_actiondelete.as_view()),
    path('hsemesteraction/get/<str:pk>', Hsemester_actionGetAPIView.as_view()),  # method get
    # path('ospeciality/hemis/get/', GetOspeciality.as_view()),

    path('hsemesteraction/hemis/get/', GetHsemesterAction.as_view()),
    path('hsemestraction/zero/hemis/get/',GetZeroHsemesterAction.as_view()),

    path('hsemesteraction/hemis/get/active/', GetThisYearHsemesterAction.as_view()),

    path('smester/with-curr/get/<uuid:curriculum_id>', SmesterCurrListApiView.as_view()),

]
