from django.urls import path
from .views import (
    ConnectSpecialityList, ConnectSpecialityGetAPIView, ConnectSpecialityupdateAPIView, ConnectSpecialitydelete

)
from .autoclickview import GetConnectSpeciality
from speciality.urls import AllGetspeciality
urlpatterns = [
    path('connectspeciality/', ConnectSpecialityList.as_view(), ),  # get,Post
    path('connectspeciality/update/<str:pk>', ConnectSpecialityupdateAPIView.as_view()),  # method put,patch
    path('connectspeciality/delete/', ConnectSpecialitydelete.as_view()),
    path('connectspeciality/get/<str:pk>', ConnectSpecialityGetAPIView.as_view()),  # method get
    path('connectspeciality/hemis/get/', AllGetspeciality.as_view()),

]