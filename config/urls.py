from rest_framework.authentication import TokenAuthentication
from django.conf import settings
from django.contrib import admin

from django.urls import path, include, re_path
from django.views.static import serve
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated

from shared.generate_swagger_settings import BothHttpAndHttpsSchemaGenerator

schema_view = get_schema_view(
    openapi.Info(
        title="Moodle LMS API",
        default_version='v1',
        description="Moodle LMS API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="JabborbekQobilov@gmail.com"),
        license=openapi.License(name="By Jabborbek"),
    ),
    generator_class=BothHttpAndHttpsSchemaGenerator,
    public=True,
    permission_classes=[permissions.AllowAny, ],
)

urlpatterns = [
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    path('api-docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
    path('api/', include('action_logs.urls')),
    path('api/', include('universty.urls')),
    path('api/', include('hemis.urls')),
    path('api/', include('speciality.urls')),
    path('api/', include('learning_process.urls')),
    path('api/', include('mixcontent.urls')),
    path('api/', include('semestr.urls')),
    path('api/', include('group.urls')),
    path('api/', include('students.urls')),
    path('api/', include('employee.urls')),
    path('api/', include('shared.urls')),
    path('api/', include('subjects.urls')),
    path('api/', include('bigbluebutton.urls')),
    path('api/', include('content.urls')),
    path('api/', include('exam.urls')),
    path('api/', include('teacher.urls')),
    path('api/', include('cours.urls')),
    path('api/', include('task.urls')),
    path('api/', include('user.urls')),
    path('api/', include('autoproctor.urls')),
    path('api/', include('videosteam.urls')),
    path('api/', include('middle_exam.urls')),
    path('api/', include('visitors.urls')),
    path('api/', include('written_exam.urls')),
    path('api/retraining/', include('retraining.urls')),
    path('api/',include("grades.urls")),
]
