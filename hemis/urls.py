from django.urls import path
from .views import (
        HemisModellist,HemisModelupdateAPIView,HemisModelDeactive,
        HemisTokenlist,HemisTokenupdateAPIView,HemisTokenDeactive,
        HemisBaselist,HemisBaseupdateAPIView,HemisBaseDeactive,
)
from .getallview import GetAll

urlpatterns = [


    # path('hemisaccount/',HemisModellist.as_view(),name='hemis-account'),#get,Post
    # path('hemisaccount/update/<str:pk>',HemisModelupdateAPIView.as_view(),name='hemis-account-update'),#method put,patch
    # path('hemisaccount/delete/',HemisModelDeactive.as_view()),
    #
    # path('hemistoken/',HemisTokenlist.as_view(),name='hemis-token'),#get,Post
    # path('hemistoken/update/<str:pk>',HemisTokenupdateAPIView.as_view(),name='hemis-token-update'),#get,Post
    # path('hemistoken/deactive/',HemisTokenDeactive.as_view()),
    #
    # path('hemisbase/',HemisBaselist.as_view(),name='hemis-base'),#get,Post
    # path('hemisbase/update/<str:pk>',HemisBaseupdateAPIView.as_view(),name='hemis-base-update'),#get,Post
    # path('hemisbase/deactive/',HemisBaseDeactive.as_view()),
    #
    path('hemis/getall/',GetAll.as_view()),
    ]