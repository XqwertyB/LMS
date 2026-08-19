from django.urls import path

from .views import (
    GenderGetApiView,
    StudentStatusGetApiView,
    FormOfPaymentGetApiView,
    StateGetApiView,
    CitizenshipGetApiView,
    Social_Category_GetApiView,
    H_Accommodation_GetApiView,
    EmployeeStatusApiView,
    ExamTypesGetApiView,
    ExamTypeApiView,
    GetIpAddressAPIView,
    TrainingTypesGetApiView, VideoStream, Hemis_get_step_by_step, GetStudent, StudentStatusAllGetApiView
)

urlpatterns = [
    path('gender/hemis/get/', GenderGetApiView.as_view()),
    path('student-status/hemis/get/', StudentStatusGetApiView.as_view()),
    path('payment-form/hemis/get/', FormOfPaymentGetApiView.as_view()),
    path('state/hemis/get/', StateGetApiView.as_view()),
    path('citizenship/hemis/get/', CitizenshipGetApiView.as_view()),
    path('social-category/hemis/get/', Social_Category_GetApiView.as_view()),
    path('accommodation/hemis/get/', H_Accommodation_GetApiView.as_view()),
    path('employee-status/hemis/get/', EmployeeStatusApiView.as_view()),
    path('exam-types/hemis/get/', ExamTypesGetApiView.as_view()),
    path('training-types/hemis/get/', TrainingTypesGetApiView.as_view()),
    path('exam-types/get', ExamTypeApiView.as_view()),
    path('get-ip-address/', GetIpAddressAPIView.as_view()),

    path('stream-video/', VideoStream.as_view(), name='stream-video'),
    path('own/get/hemis/', Hemis_get_step_by_step.as_view()),
    path('own/get/student/', GetStudent.as_view()),
    path('get/student-status/', StudentStatusAllGetApiView.as_view())
]
