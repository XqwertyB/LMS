import logging
import time
from datetime import datetime

import requests
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from config.permissions import AllowOnlyTrustedOrigins
from config.settings import (
    CLIENT_SECRET, CLIENT_ID, REDIRECT_URI, API_TOKEN,
    AUTHORIZE_URL, TOKEN_URL, RESOURCE_OWNER_URL)
from hemis.models import Hemis_Base, HemisToken
from shared.models import EmployeeStatus, Gender
from shared.permissions import IsTeacher, IsAdminOrTeacher
from shared.utils import CustomPageNumberPagination
from universty.models import Department, Faculty
from user.models import User
from user.serializers import MyTokenObtainPairSerializer
from .client import OAuth2Client
from .models import Employee
from .serializers import TeacherSerializer
from .synchronized.view import (
    EmployeeClient,
    get_sync_teachers_job,
    start_sync_teachers_job,
)

logger = logging.getLogger(__name__)


class OAuthAuthorizationView(APIView):
    def get(self, request):
        client = OAuth2Client(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            authorize_url=AUTHORIZE_URL,
            token_url=TOKEN_URL,
            resource_owner_url=RESOURCE_OWNER_URL
        )
        authorization_url = client.get_authorization_url()
        return Response({'authorization_url': authorization_url}, status=status.HTTP_200_OK)


class OAuthCallbackView(APIView):
    def get(self, request, *args, **kwargs):
        full_info = {}
        auth_code = self.kwargs.get('code')

        if not auth_code:
            return Response({'error': 'Authorization code is missing'}, status=status.HTTP_400_BAD_REQUEST)

        client = OAuth2Client(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            authorize_url=AUTHORIZE_URL,
            token_url=TOKEN_URL,
            resource_owner_url=RESOURCE_OWNER_URL
        )
        access_token_response = client.get_access_token(auth_code)

        if 'access_token' in access_token_response:
            access_token = access_token_response['access_token']
            user_details = client.get_user_details(access_token)

            try:
                user = User.objects.get(username=user_details['employee_id_number'])

                token_serializer = MyTokenObtainPairSerializer()
                custom_token = token_serializer.get_token(user)
                full_info['backend_token'] = custom_token

            except ObjectDoesNotExist:
                full_info['backend_token'] = None

            full_info['details'] = user_details
            full_info['token'] = access_token

            return Response(full_info, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to obtain access token'}, status=status.HTTP_400_BAD_REQUEST)


counter = []


class GetTeacherApiView(APIView):
    """HEMIS teacher sinxronlash — background threadda ishga tushadi.

    Tashqi proxy/nginx timeoutidan saqlanish uchun darhol 202 qaytaradi.
    Sinxron natijani olish uchun ?wait=1 yuborish mumkin (eski xulq-atvor).
    """
    permission_classes = [AllowOnlyTrustedOrigins, IsAdminOrTeacher, ]

    def get(self, request, *args, **kwargs):
        hemis = Hemis_Base.objects.filter(own_uniq=9).first()
        if not hemis:
            return Response(
                {"error": "Hemis url topilmadi"},
                status=status.HTTP_400_BAD_REQUEST
            )

        token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
        if not token:
            return Response(
                {"error": "Token topilmadi"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Eski sinxron xulq-atvor uchun ?wait=1
        if request.query_params.get("wait") in ("1", "true", "yes"):
            client = EmployeeClient(hemis, token)
            start = time.time()
            result = client.sync_teachers(max_workers=10)
            result["elapsed_time"] = round(time.time() - start, 2)
            return Response(result, status=status.HTTP_200_OK)

        job = start_sync_teachers_job(hemis, token, max_workers=10)
        status_url = request.build_absolute_uri(
            f"/api/teachers/get/hemis/status/{job['job_id']}"
        )
        return Response(
            {
                "message": "Sinxronlash background threadda boshlandi",
                "job_id": job["job_id"],
                "status": job["status"],
                "started_at": job["started_at"],
                "already_running": job.get("already_running", False),
                "status_url": status_url,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class GetTeacherSyncStatusAPIView(APIView):
    """Background sinxronlash holatini tekshirish."""
    permission_classes = [AllowOnlyTrustedOrigins, IsAdminOrTeacher, ]

    def get(self, request, job_id, *args, **kwargs):
        job = get_sync_teachers_job(job_id)
        if job is None:
            return Response(
                {
                    "error": "Job topilmadi. Boshqa worker jarayonida boshlangan yoki tarixdan o'chirilgan bo'lishi mumkin."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"job_id": job_id, **job}, status=status.HTTP_200_OK)


# class GetTeacherApiView(APIView):
#     def get(self, request, *args, **kwargs):
#         start_time = datetime.now()  # Timing starts here
#
#         # Fetch Hemis Base object
#         hemis = Hemis_Base.objects.select_related('hemis_user').filter(own_uniq=9).first()
#         if not hemis:
#             logger.error(f"Hemis_Base not found for own_uniq=9")
#             return Response({'error': 'Hemis modulida birktrilmagan'}, status=status.HTTP_400_BAD_REQUEST)
#
#         base_url = hemis.base_url + hemis.path_url
#         checkapi = hemis.openapi
#
#         # Fetch token
#         token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
#         if not token:
#             logger.error(f"No active token found for hemis_user={hemis.hemis_user}")
#             return Response({'error': 'Faol token mavjud emas!'}, status=status.HTTP_400_BAD_REQUEST)
#
#         if checkapi:
#             return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'})
#
#         headers = {
#             'Content-Type': 'application/json',
#             'Authorization': f"{token.hemis_token_type} {token.hemis_token}"
#         }
#         params = {'limit': '200', 'type': 'teacher'}
#
#         # Fetch page count
#         try:
#             page_count_response = requests.get(base_url, headers=headers, params=params)
#             page_count_response.raise_for_status()
#             page_count = page_count_response.json()['data']['pagination']['pageCount']
#         except Exception as e:
#             logger.error(f"Failed to fetch page count: {e}")
#             return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#
#         unique_employees = set()
#         unique_employees_list = []
#
#         for page in range(1, int(page_count) + 1):
#             self.fetch_and_process_page(page, base_url, headers, params, unique_employees, unique_employees_list)
#
#         duration = datetime.now() - start_time  # Calculate duration
#
#         return Response({
#             'message': 'Success',
#             'count_set': len(unique_employees),
#             'count_list': len(unique_employees_list),
#             'count_list_set': len(set(unique_employees_list)),
#             'time_taken': str(duration)
#         })
#
#     def fetch_and_process_page(self, page, base_url, headers, params, unique_employees, unique_employees_list):
#         try:
#             params['page'] = str(page)
#             response = requests.get(base_url, headers=headers, params=params)
#             response.raise_for_status()
#             data = response.json()
#
#             # Sleep to avoid server overload
#             sleep(0.2)
#
#             if data['data']:
#                 employee_items = data['data']['items']
#                 self.create_or_update_employees(employee_items, unique_employees, unique_employees_list)
#         except Exception as e:
#             logger.error(f"Error processing page {page}: {e}")
#
#     def create_or_update_employees(self, employee_items, unique_employees, unique_employees_list):
#         for item in employee_items:
#             employee_id_number = item['employee_id_number']
#             #
#             # # Update or create User
#             # user, _ = User.objects.update_or_create(
#             #     username=employee_id_number,
#             #     defaults={
#             #         'role': 'teacher',
#             #         'first_name': item['first_name'],
#             #         'last_name': item['second_name'],
#             #         'password': make_password(employee_id_number),
#             #     }
#             # )
#             #
#             # # Update or create Employee
#             # Employee.objects.update_or_create(
#             #     hemis_id=str(item['id']),
#             #     defaults={
#             #         'user': user,
#             #         'department': self.get_department(item['department']['id']),
#             #         'e_status': self.get_employee_status(item['employeeStatus']['code']),
#             #         'gender': self.get_gender(item['gender']['code']),
#             #         'first_name': item['first_name'],
#             #         'second_name': item['second_name'],
#             #         'full_name': item['full_name'],
#             #         'father_name': item['third_name'],
#             #         'birth_date': item['birth_date'],
#             #     }
#             # )
#
#             unique_employees.add(employee_id_number)
#             unique_employees_list.append(employee_id_number)

# def get_department(self, department_id):
#     return Department.objects.filter(hemisid=department_id).first()
#
# def get_employee_status(self, status_code):
#     return EmployeeStatus.objects.filter(code=status_code).first()
#
# def get_gender(self, gender_code):
#     return Gender.objects.filter(code=gender_code).first()


# class GetTeacherApiView(APIView):
#
#     def get(self, request, *args, **kwargs):
#         start_time = datetime.now()  # Timing starts here
#
#         try:
#             hemis = Hemis_Base.objects.select_related('hemis_user').get(own_uniq=9)
#         except Hemis_Base.DoesNotExist:
#             logger.error(f"Error in {self.__class__.__name__}.get: Hemis_Base retrieval failed")
#             return Response({'error': 'Hemis modulida birktrilmagan'}, status=status.HTTP_400_BAD_REQUEST)
#
#         baseurl = hemis.base_url
#         pathurl = hemis.path_url
#         checkapi = hemis.openapi
#
#         try:
#             token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
#             if not token:
#                 raise ValueError("No active token found")
#         except Exception as e:
#             logger.error(f"Error in {self.__class__.__name__}.get: Token retrieval failed: {e}")
#             return Response({'error': 'Faol token mavjud emas!'}, status=status.HTTP_400_BAD_REQUEST)
#
#         if checkapi:
#             return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'})
#
#         headers = {
#             'Content-Type': 'application/json',
#             'Authorization': f"{token.hemis_token_type} {token.hemis_token}"
#         }
#         base_url = baseurl + pathurl
#         params = {'limit': '200', 'type': 'teacher'}
#
#         # Fetch the page count
#         try:
#             page_count_response = requests.get(base_url, headers=headers, params=params)
#             page_count_response.raise_for_status()
#             page_count = page_count_response.json()['data']['pagination']['pageCount']
#         except Exception as e:
#             logger.error(f"Error in {self.__class__.__name__}.get: {e}")
#             return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#
#         unique_employees = set()  # Use a set to ensure unique employees
#
#         # Sequentially fetch data page by page
#         for page in range(1, int(page_count) + 1):
#             self.fetch_and_process_page(page, base_url, headers, params, unique_employees)
#             time.sleep(0.5)
#
#         end_time = datetime.now()  # Timing ends here
#         duration = end_time - start_time  # Calculate duration
#
#         return Response({'message': 'Success', 'count': len(unique_employees), 'time_taken': str(duration)})
#
#     def fetch_and_process_page(self, page, base_url, headers, params, unique_employees):
#         try:
#             params['page'] = str(page)
#             response = requests.get(base_url, headers=headers, params=params)
#             response.raise_for_status()
#             data = response.json()
#
#             if data['data']:
#                 employee_items = data['data']['items']
#                 self.create_or_update_employees(employee_items, unique_employees)
#         except Exception as e:
#             logger.error(f"Error in {self.__class__.__name__}.fetch_and_process_page: {e}")
#
#     @staticmethod
#     def retry_operation(func, retries=3):
#         """Retry function to handle deadlocks"""
#         for attempt in range(retries):
#             try:
#                 return func()
#             except OperationalError:
#                 logger.warning(f"Deadlock detected, retrying... {attempt + 1}/{retries}")
#                 time.sleep(1)  # Wait for 1 second before retrying
#         raise OperationalError("Failed after multiple retries")
#
#     @transaction.atomic
#     def create_or_update_employees(self, employee_items, unique_employees):
#         # Prefetch related objects to avoid querying for each loop iteration
#         existing_faculties = Faculty.objects.all()
#         existing_departments = Department.objects.select_related('faculty').all()
#         existing_genders = Gender.objects.all()
#         existing_statuses = EmployeeStatus.objects.all()
#
#         for item in employee_items:
#             try:
#                 employee_id_number = item['employee_id_number']
#
#                 # Skip if the employee already exists
#                 if Employee.objects.filter(employee_id_number=employee_id_number).exists():
#                     logger.info(f"Employee with ID {employee_id_number} already exists. Skipping...")
#                     continue
#
#                 faculty_id = item['department']['parent']
#                 department_id = item['department']['id']
#
#                 # Find or create related Faculty and Department
#                 faculty = next((f for f in existing_faculties if f.hemisid == faculty_id), None)
#                 if not faculty:
#                     faculty = Faculty(hemisid=faculty_id)
#                     faculty.save()
#
#                 department = next((d for d in existing_departments if d.hemisid == department_id), None)
#                 if not department:
#                     department = Department(
#                         hemisid=department_id,
#                         faculty=faculty,
#                         name=item['department']['name'],
#                         kod=item['department']['code']
#                     )
#                     department.save()
#
#                 gender = next((g for g in existing_genders if g.code == item['gender']['code']), None)
#                 if not gender:
#                     gender = Gender(code=item['gender']['code'])
#                     gender.save()
#
#                 employee_status = next((s for s in existing_statuses if s.code == item['employeeStatus']['code']), None)
#                 if not employee_status:
#                     employee_status = EmployeeStatus(code=item['employeeStatus']['code'])
#                     employee_status.save()
#
#                 # Retry operation to handle deadlocks while creating User
#                 user = self.retry_operation(lambda: User.objects.get_or_create(
#                     username=employee_id_number,
#                     defaults={
#                         'role': 'teacher',
#                         'first_name': item['first_name'],
#                         'last_name': item['second_name'],
#                         'password': make_password(employee_id_number)
#                     }
#                 )[0])
#
#                 # Create Employee record
#                 Employee.objects.create(
#                     user=user,
#                     employee_id_number=employee_id_number,
#                     hemis_id=str(item['id']),
#                     department=department,
#                     e_status=employee_status,
#                     gender=gender,
#                     first_name=item['first_name'],
#                     second_name=item['second_name'],
#                     full_name=item['full_name'],
#                     father_name=item['third_name'],
#                     birth_date=item['birth_date']
#                 )
#                 unique_employees.add(employee_id_number)  # Add to the set
#
#             except Exception as e:
#                 logger.error(f"Error in {self.__class__.__name__}.create_or_update_employees: {e}")


class LikeTeacherApiView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdminOrTeacher, ]

    def get(self, request, *args, **kwargs):
        try:
            employees = Employee.objects.filter(status_action=True).order_by('full_name')
            paginator = CustomPageNumberPagination()
            fullname = request.query_params.get('fullname')
            if fullname is not None:
                employees = employees.filter(full_name__icontains=fullname)

            paginated_queryset = paginator.paginate_queryset(employees, request, view=self)
            if paginated_queryset is not None:
                serializer = TeacherSerializer(paginated_queryset, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = TeacherSerializer(employees, many=True)
            return Response(serializer.data)

        except Exception as ex:
            error_message = str(ex)

            return Response({'errors': error_message}, status=status.HTTP_400_BAD_REQUEST)


class LikeTeacherDetailAPIView(RetrieveAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdminOrTeacher]
    serializer_class = TeacherSerializer
    lookup_field = "user__id"
    lookup_url_kwarg = "user_id"

    queryset = Employee.objects.select_related(
        "user",
        "department",
        "e_status",
        "gender",
    )

    @swagger_auto_schema(
        operation_summary="Teacher detail (user_id bo‘yicha)",
        tags=["Teacher Like"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class GetTeacherLocalAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdminOrTeacher, ]

    def get(self, request, employee_id_number):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(API_TOKEN)
        }
        base_url = 'https://tsue.tsue.uz/rest/v1/data/employee-list'
        params = {'limit': '200', 'type': 'teacher', 'search': employee_id_number}

        try:
            response = requests.get(base_url, headers=headers, params=params)
            data = response.json()['data']['items']
            if not data:
                return Response(
                    {
                        'status': False,
                        'message': "O'qituvchi topilmadi..."
                    }
                )
            respone_data = response.json()['data']['items'][0]
            user = User.objects.filter(username=employee_id_number).first()
            if user is None:
                return Response(
                    {
                        'status': False,
                        'message': "O'qituvchi topilmadi..."
                    }
                )
            else:
                respone_data['backend_token'] = user.token()
                return Response(response.json()['data']['items'][0])

        except Exception as e:
            logger.error(f"Error response employee: {e}")
