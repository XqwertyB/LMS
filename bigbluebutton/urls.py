from django.urls import path
from .views import (
    Bigbluebutton_open_meeting, Bigbluebutton_join_mentor, BigbluebuttonJoinAttendee,
    Bigbluebutton_end_meeting, Bigbluebutton_realtime_meeting, Bigbluebutton_getinfo_meeting,
    BigbluebuttonMainCreateList, BigbluebuttonMainupdateAPIView, BigbluebuttonMainGetAPIView, BigbluebuttonMaindelete,
    Bigbluebutton_subCreateList, Bigbluebutton_subupdateAPIView, Bigbluebutton_subGetAPIView, Bigbluebutton_subdelete,
    Bigbluebutton_ModelCreateList, Bigbluebutton_ModelupdateAPIView, Bigbluebutton_ModelGetAPIView,
    Bigbluebutton_Modeldelete
)

urlpatterns = [
    path('bigbluebutton_main/', BigbluebuttonMainCreateList.as_view(), ),  # get,Post
    path('bigbluebutton_main/update/<str:pk>', BigbluebuttonMainupdateAPIView.as_view()),  # method put,patch
    path('bigbluebutton_main/delete/', BigbluebuttonMainGetAPIView.as_view()),
    path('bigbluebutton_main/get/<str:pk>', BigbluebuttonMaindelete.as_view()),  # method get

    path('bigbluebutton_sub/', Bigbluebutton_subCreateList.as_view(), ),  # get,Post
    path('bigbluebutton_sub/update/<str:pk>', Bigbluebutton_subupdateAPIView.as_view()),  # method put,patch
    path('bigbluebutton_sub/delete/', Bigbluebutton_subGetAPIView.as_view()),
    path('bigbluebutton_sub/get/<str:pk>', Bigbluebutton_subdelete.as_view()),  # method get

    path('bigbluebutton_model/', Bigbluebutton_ModelCreateList.as_view(), ),  # get,Post
    path('bigbluebutton_model/update/<str:pk>', Bigbluebutton_ModelupdateAPIView.as_view()),  # method put,patch
    path('bigbluebutton_model/delete/', Bigbluebutton_ModelGetAPIView.as_view()),
    path('bigbluebutton_model/get/<str:pk>', Bigbluebutton_Modeldelete.as_view()),  # method get

    # +
    path('bigbluebutton/createroom/', Bigbluebutton_open_meeting.as_view()),
    path('bigbluebutton/join/moderator/', Bigbluebutton_join_mentor.as_view()),
    path('bigbluebutton/join/attendee/', BigbluebuttonJoinAttendee.as_view()),
    path('bigbluebutton/endroom/', Bigbluebutton_end_meeting.as_view()),
    path('bigbluebutton/isrunning/', Bigbluebutton_realtime_meeting.as_view()),
    path('bigbluebutton/getinfo/', Bigbluebutton_getinfo_meeting.as_view())
]
