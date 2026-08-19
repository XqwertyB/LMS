from django.urls import path
from .views import TeacherList_View, Content_teacher_List_View, Topic_teacher_list_View, Room_BigbluebuttonListView, \
    EnterRoom,GetInfoRoom,RealRoomListView,ListMettingRoomDelete

urlpatterns = [
    path('statistic/teacher/', TeacherList_View.as_view()),
    path('statistic/<uuid:pk>/list/',Content_teacher_List_View.as_view()),
    path('statistic/topic/<uuid:pk>/',Topic_teacher_list_View.as_view()),

    path('monitoring/list/',Room_BigbluebuttonListView.as_view()),
    path('monitoring/bbb-enter/<uuid:pk>',EnterRoom.as_view()),
    path('monitoring/bbb-getinfo/<uuid:pk>',GetInfoRoom.as_view()),
    path('monitoring/bbb-real/list/',RealRoomListView.as_view()),

    path('low/bbb/delete/',ListMettingRoomDelete.as_view()),



]
