from django.urls import path
from .views import (
    GroupList, GroupupdateAPIView, GroupGetAPIView, Groupdelete, GroupListApiView

)

from .autoclickview import GetGroup, GetReGroup, GetALLGroup

urlpatterns = [
    path('group/', GroupList.as_view(), ),  # get,Post
    path('group/update/<str:pk>', GroupupdateAPIView.as_view()),  # method put,patch
    path('group/delete/', Groupdelete.as_view()),
    path('group/get/<str:pk>', GroupGetAPIView.as_view()),  # method get
    path('group/hemis/get/', GetGroup.as_view()),
    path('groups-list/', GroupListApiView.as_view(), name='group-list'),
    path('groups/hemis/get/masofaviy/',GetReGroup.as_view()),
    path('groups/hemis/get/all/',GetALLGroup.as_view())
]
