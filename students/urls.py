from django.urls import path

from .additional.views import FullStudentListAPIView
from .additional.views import StudentBulkUpdateAPIView
from .oAuth2_views import StudentAuthorizationView
from .oAuth2_views import StudentCallbackView
from .synchronization.hemis_sync_views import HemisDaytimeStudentsAPIView
from .synchronization.hemis_sync_views import HemisDistanceStudentsAPIView
from .synchronization.hemis_sync_views import HemisEveningStudentsAPIView
from .synchronization.hemis_sync_views import HemisExternalStudentsAPIView
from .synchronization.hemis_sync_views import HemisJointDaytimeStudentsAPIView
from .synchronization.hemis_sync_views import HemisJointDistanceStudentsAPIView
from .synchronization.hemis_sync_views import HemisJointEveningStudentsAPIView
from .synchronization.hemis_sync_views import HemisJointExternalStudentsAPIView
from .synchronization.hemis_sync_views import HemisSecondDegreeDaytimeStudentsAPIView
from .synchronization.hemis_sync_views import HemisSecondDegreeDistanceStudentsAPIView
from .synchronization.hemis_sync_views import HemisSecondDegreeEveningStudentsAPIView
from .synchronization.hemis_sync_views import HemisSecondDegreeExternalStudentsAPIView
from .synchronization.hemis_sync_views import HemisSpecialExternalStudentsAPIView
from .views import StudentALLApiView
from .views import StudentAllINApiView
from .views import StudentApiView
from .views import StudentDetail
from .views import StudentForGroupApiView
from .views import StudentImageCheckApiView
from .views import StudentListAPIView
from .views import StudentMasofaikkiniApiView
from .views import StudentPatchView
from .views import StudentQoshmaApiView
from .views import StudentSecondSrtqApiView

urlpatterns = [
    path('students/get/hemis', StudentApiView.as_view(), name='student-a-create'),
    path('students/get/hemis-masofa2/', StudentMasofaikkiniApiView.as_view(), name='student2-a-create'),
    path('students/get/hemis-qoshma/', StudentQoshmaApiView.as_view(), name='student-a-create'),
    path('students/get/hemis-second/', StudentSecondSrtqApiView.as_view(), name='student-a-create-second'),
    path('students/get/hemis-all/', StudentALLApiView.as_view(), name='student-a-create-second'),

    ##########################################
    path('students/get/all', StudentListAPIView.as_view(), name='student-all-get'),
    path('students-full-get', FullStudentListAPIView.as_view(), name='student-full-get'),
    path('get/student/<str:student_id_number>/', StudentDetail.as_view(), name='student-get-detail'),
    path('get/image/<str:student_id_number>/', StudentImageCheckApiView.as_view(), name='student-get-image'),
    path('student-group/<uuid:group_id>/', StudentForGroupApiView.as_view(), name='student-get-for-group'),
    path('student/<str:pk>/patch/', StudentPatchView.as_view(), name='student-patch'),
    path("students/bulk-update/", StudentBulkUpdateAPIView.as_view(), name="students-bulk-update"),
    path('students/get/hemis/allin/', StudentAllINApiView.as_view()),
    path('authorization-student', StudentAuthorizationView.as_view()),
    path('student-callback/', StudentCallbackView.as_view()),

    ###########################################

    # ------------------ Asosiy ta'lim ------------------

    path("students/get/external/", HemisExternalStudentsAPIView.as_view()),
    path("students/get/daytime/", HemisDaytimeStudentsAPIView.as_view()),
    path("students/get/evening/", HemisEveningStudentsAPIView.as_view()),
    path("students/get/distance/", HemisDistanceStudentsAPIView.as_view()),

    # ------------------ Ikkinchi oliy ------------------

    path("students/get/second-degree/daytime/", HemisSecondDegreeDaytimeStudentsAPIView.as_view()),
    path("students/get/second-degree/evening/", HemisSecondDegreeEveningStudentsAPIView.as_view()),
    path("students/get/second-degree/external/", HemisSecondDegreeExternalStudentsAPIView.as_view()),
    path("students/get/second-degree/distance/", HemisSecondDegreeDistanceStudentsAPIView.as_view()),

    # ------------------ Qo‘shma ta'lim ------------------

    path("students/get/joint/daytime/", HemisJointDaytimeStudentsAPIView.as_view()),
    path("students/get/joint/evening/", HemisJointEveningStudentsAPIView.as_view()),
    path("students/get/joint/external/", HemisJointExternalStudentsAPIView.as_view()),
    path("students/get/joint/distance/", HemisJointDistanceStudentsAPIView.as_view()),

    # ------------------ Maxsus ------------------

    path("students/get/special/external/", HemisSpecialExternalStudentsAPIView.as_view()),

]
