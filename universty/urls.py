from django.urls import path
from .views import (
    OtmList,OtmupdateAPIView,Otmtypelist,Otmshapedelete,
    OtmtypeupdateAPIView,Otmshapelist,OtmshapeupdateAPIView,
    Otmtypedelete,Citylist,CityupdateAPIView,Citydelete,
    OtmSectionlist,OtmSectionupdateAPIView,OtmSectiondelete,
    OtmGetAPIView,OtmtypeGetAPIView,OtmshapeGetAPIView,OtmCityGetAPIView,OtmSectionGetAPIView
    )
from .Fview import (
    Faculty_typelist,Faculty_typeupdateAPIView,Faculty_typedelete,Facultylist,
    FacultyupdateAPIView,Facultydelete,Departmentlist,DepartmentupdateAPIView,Departmentdelete,
    Sectionlist,SectionupdateAPIView,Sectiondelete,
    Faculty_typeGetAPIView,FacultyGetAPIView,DepartmentGetAPIView,SectionGetAPIView

    )
from .autoclickview import (GetCheckUniversity,GetOtmtype,GetOtmshape,
                            GetCity,GetOtmSection,GetOtmFaculty,GetOtmFacultytype,GetOtmDepartment)
urlpatterns = [
    path('otm/', OtmList.as_view(), name='Otm-list'),#get,Post
    path('otm/update/<str:pk>',OtmupdateAPIView.as_view(),name='Otm-update'),#method put,patch
    path('otm/get/<str:pk>', OtmGetAPIView.as_view(), name='Otm-get'),  # method get
    #hemisdan yuklavolish
    path('otm/hemis/get/',GetCheckUniversity.as_view()),



    path('otmtype/',Otmtypelist.as_view(),name='Otm-type'),#get,Post
    path('otmtype/update/<str:pk>',OtmtypeupdateAPIView.as_view(),name='Otmtype-update'),#method put,patch
    path('otmtype/delete/',Otmtypedelete.as_view()),
    path('otmtype/get/<str:pk>', OtmtypeGetAPIView.as_view(), name='Otmtype-get'),  # method get
    path('otmtype/hemis/get/',GetOtmtype.as_view()),

    path('otmshape/',Otmshapelist.as_view(),name='Otm-shape'),#get,Post
    path('otmshape/update/<str:pk>',OtmshapeupdateAPIView.as_view(),name='Otm-shape'),#get,Post
    path('otmshape/delete/',Otmshapedelete.as_view()),
    path('otmshape/get/<str:pk>', OtmshapeGetAPIView.as_view(), name='Otmshape-get'),  # method get
    path('otmshape/hemis/get/',GetOtmshape.as_view()),


    path('otmcity/',Citylist.as_view(),name='Otm-cty'),#get,Post
    path('otmcity/update/<str:pk>',CityupdateAPIView.as_view(),name='Otm-city'),#get,Post
    path('otmcity/delete/',Citydelete.as_view()),
    path('otmcity/get/<str:pk>', OtmCityGetAPIView.as_view(), name='Otmcity-get'),  # method get
    path('otmcity/hemis/get/',GetCity.as_view()),


    path('otmsection/',OtmSectionlist.as_view()),#get,Post
    path('otmsection/update/<str:pk>',OtmSectionupdateAPIView.as_view()),#get,Post
    path('otmsection/delete/',OtmSectiondelete.as_view()),
    path('otmsection/get/<str:pk>', OtmSectionGetAPIView.as_view()),  # method get
    path('otmsection/hemis/get/',GetOtmSection.as_view()),

    path('faculty_type/',Faculty_typelist.as_view()),
    path('faculty_type/update/<str:pk>',Faculty_typeupdateAPIView.as_view()),
    path('faculty_type/delete/',Faculty_typedelete.as_view()),
    path('faculty_type/get/<str:pk>', Faculty_typeGetAPIView.as_view()),  # method get
    path('faculty_type/hemis/get/',GetOtmFacultytype.as_view()),

    path('faculty/',Facultylist.as_view()),
    path('faculty/update/<str:pk>',FacultyupdateAPIView.as_view()),
    path('faculty/delete/',Facultydelete.as_view()),
    path('faculty/get/<str:pk>', FacultyGetAPIView.as_view()),  # method get

    path('department/',Departmentlist.as_view()),
    path('department/update/<str:pk>',DepartmentupdateAPIView.as_view()),
    path('department/delete/',Departmentdelete.as_view()),
    path('department/get/<str:pk>', DepartmentGetAPIView.as_view()),
    path('section/',Sectionlist.as_view()),
    path('section/update/<str:pk>',SectionupdateAPIView.as_view()),
    path('section/delete/',Sectiondelete.as_view()),
    path('section/get/<str:pk>', SectionGetAPIView.as_view()),
    path('otmfaculty/hemis/get/',GetOtmFaculty.as_view()),

    path('otmdepartment/hemis/get/',GetOtmDepartment.as_view())


    ]