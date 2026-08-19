from django.urls import path
from .views import (
    BspecialityList, BspecialityGetAPIView, BspecialityupdateAPIView, Bspecialitydelete,
    MspecialityList, MspecialityGetAPIView, MspecialityupdateAPIView, Mspecialitydelete,
    OspecialityList, OspecialityGetAPIView, OspecialityupdateAPIView, Ospecialitydelete,

)
from .autoclickview import GetBspeciality, GetMspeciality, GetOspeciality, GetDspeciality, AllGetspeciality

urlpatterns = [
    path('bspeciality/', BspecialityList.as_view(), ),  # get,Post
    path('bspeciality/update/<str:pk>', BspecialityupdateAPIView.as_view()),  # method put,patch
    path('bspeciality/delete/', Bspecialitydelete.as_view()),
    path('bspeciality/get/<str:pk>', BspecialityGetAPIView.as_view()),  # method get
    path('bspeciality/hemis/get/', GetBspeciality.as_view()),

    path('mspeciality/', MspecialityList.as_view(), ),  # get,Post
    path('mspeciality/update/<str:pk>', MspecialityupdateAPIView.as_view()),  # method put,patch
    path('mspeciality/delete/', Mspecialitydelete.as_view()),
    path('mspeciality/get/<str:pk>', MspecialityGetAPIView.as_view()),  # method get
    path('mspeciality/hemis/get/', GetMspeciality.as_view()),

    path('ospeciality/', OspecialityList.as_view(), ),  # get,Post
    path('ospeciality/update/<str:pk>', OspecialityupdateAPIView.as_view()),  # method put,patch
    path('ospeciality/delete/', Ospecialitydelete.as_view()),
    path('ospeciality/get/<str:pk>', OspecialityGetAPIView.as_view()),  # method get
    path('ospeciality/hemis/get/', GetOspeciality.as_view()),


    path('dspeciality/hemis/get/',GetDspeciality.as_view()),
    path('speciality/hemis/get/all/',AllGetspeciality.as_view()),
]
