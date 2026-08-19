import logging
import os
import os
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

import requests
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework import status
from rest_framework import views
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from config import settings
from config.permissions import AllowOnlyTrustedOrigins
from config.settings import HEMIS_URL
from group.models import Group
from hemis.models import HemisToken
from hemis.models import Hemis_Base
from learning_process.models import Educationform
from learning_process.models import Educationlang
from learning_process.models import Educationtype
from learning_process.models import Educationyear
from semestr.models import HCourse
from semestr.models import Hsemester_action
from shared.models import FormOfPayment
from shared.models import Gender
from shared.models import H_Accommodation
from shared.models import H_Citizenship_type
from shared.models import H_Social_Category
from shared.models import H_Student_Status
from shared.models import State
from shared.permissions import IsAdmin
from shared.permissions import IsAdminOrTeacher
from shared.permissions import IsStudent
from shared.permissions import IsTeacherOrStudent
from speciality.models import AllSpeciality
from universty.models import City
from universty.models import Faculty
from user.models import User
from user.serializers import MyTokenObtainPairSerializer
from .models import Student
from .serializers import S_StudentImageSerializer
from .serializers import StudentForGroupSerializer
from .serializers import StudentLoginSerializer
from .serializers import StudentSerializer
from .serializers import StudentUpdateSerializer

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class StudentApiView(views.APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

    def get(self, request, format=None):
        start_time = time.time()

        try:
            hemis = Hemis_Base.objects.get(own_uniq=8)
        except Hemis_Base.DoesNotExist:
            return Response({'error': '❌ Hemis modulida biriktirilmagan!'})

        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi

        token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
        if not token:
            return Response({'error': '❌ Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': '❌ Ushbu API token talab qiladi!'})

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"{token.hemis_token_type} {token.hemis_token}"
        }
        params = {
            'page': '1',
            'limit': '200',
            '_education_form': '16'
        }
        response = requests.get(baseurl + pathurl, headers=headers, params=params)

        no_image = []
        exceptions = []

        def create_or_update_students(data):
            try:
                # 1️⃣ FK obyektlarni oldindan yig‘ib olish
                fk_fields = {
                    'gender': (Gender, 'code', 'gender', 'code'),
                    'new_specialty': (AllSpeciality, 'id', 'specialty', 'spec_id'),
                    'studentStatus': (H_Student_Status, 'code', 'studentStatus', 'code'),
                    'educationForm': (Educationform, 'code', 'educationForm', 'code'),
                    'educationType': (Educationtype, 'code', 'educationType', 'code'),
                    'educationYear': (Educationyear, 'code', 'educationYear', 'code'),
                    'paymentForm': (FormOfPayment, 'code', 'paymentForm', 'code'),
                    'group': (Group, 'id', 'group', 'h_id'),
                    'faculty': (Faculty, 'id', 'department', 'hemisid'),
                    'level': (HCourse, 'code', 'level', 'code'),
                    'semester': (Hsemester_action, 'id', 'semester', 'h_id'),
                    'country': (State, 'code', 'country', 'code'),
                    'province': (City, 'code', 'province', 'code'),
                    'district': (City, 'code', 'district', 'code'),
                    'citizenship': (H_Citizenship_type, 'code', 'citizenship', 'code'),
                    'socialCategory': (H_Social_Category, 'code', 'socialCategory', 'code'),
                    'accommodation': (H_Accommodation, 'code', 'accommodation', 'code'),
                }

                all_instances = {}
                for key, (model_cls, id_field, data_key, lookup) in fk_fields.items():
                    ids = [item.get(data_key, {}).get(id_field) for item in data if
                           data_key in item and id_field in item.get(data_key, {})]
                    instances = model_cls.objects.filter(**{f"{lookup}__in": ids}).distinct()
                    all_instances[key] = {getattr(instance, lookup): instance for instance in instances}

                edu_lang_ids = [item['group']['educationLang']['code'] for item in data if
                                'group' in item and 'educationLang' in item['group']]
                edu_langs = Educationlang.objects.filter(code__in=edu_lang_ids)
                all_instances['educationLang'] = {lang.code: lang for lang in edu_langs}

                # 2️⃣ Talabalarni qayta ishlash
                def process_student(i):

                    try:
                        user, created = User.objects.get_or_create(
                            username=i['student_id_number'],
                            defaults={
                                'role': 'student',
                                'password': make_password(i['student_id_number']),
                                'first_name': i['first_name'],
                                'last_name': i['second_name']
                            }
                        )
                        if not created:
                            user.first_name = i['first_name']
                            user.last_name = i['second_name']
                            user.save()

                        student_data = {
                            'user': user,
                            'first_name': i['first_name'],
                            'second_name': i['second_name'],
                            'third_name': i['third_name'],
                            'full_name': i['full_name'],
                            'student_id_number': i['student_id_number'],
                            'birth_date': i['birth_date'],
                            'gender': all_instances['gender'][i['gender']['code']],
                            'new_specialty': all_instances['new_specialty'][i['specialty']['id']],
                            'studentStatus': all_instances['studentStatus'][i['studentStatus']['code']],
                            'educationForm': all_instances['educationForm'][i['educationForm']['code']],
                            'educationType': all_instances['educationType'][i['educationType']['code']],
                            'educationYear': all_instances['educationYear'][i['educationYear']['code']],
                            'paymentForm': all_instances['paymentForm'][i['paymentForm']['code']],
                            'group': all_instances['group'][i['group']['id']],
                            'faculty': all_instances['faculty'][i['department']['id']],
                            'educationLang': all_instances['educationLang'][i['group']['educationLang']['code']],
                            'level': all_instances['level'][i['level']['code']],
                            'semester': all_instances['semester'][i['semester']['id']],
                            'country': all_instances['country'][i['country']['code']],
                            'province': all_instances['province'][i['province']['code']],
                            'district': all_instances['district'][i['district']['code']],
                            'citizenship': all_instances['citizenship'][i['citizenship']['code']],
                            'socialCategory': all_instances['socialCategory'][i['socialCategory']['code']],
                            'accommodation': all_instances['accommodation'][i['accommodation']['code']],
                            'year_of_enter': str(i['year_of_enter']),
                            'avg_gpa': i['avg_gpa'],
                            'total_credit': i['total_credit'],
                        }

                        # 📌 Rasm yuklash
                        image_url = i.get('image')
                        if image_url:
                            response = requests.get(image_url)
                            if response.status_code != 200:
                                raise ValidationError(f"⚠️ {i['full_name']} uchun rasm yuklab bo‘lmadi: {image_url}")

                            directory = 'students/'
                            media_dir = os.path.join(settings.MEDIA_ROOT, directory)
                            os.makedirs(media_dir, exist_ok=True)

                            image_name = os.path.basename(image_url)
                            image_path = os.path.join(directory, image_name)

                            full_path = os.path.join(settings.MEDIA_ROOT, image_path)
                            if os.path.exists(full_path):
                                os.remove(full_path)

                            with open(full_path, 'wb') as f:
                                f.write(response.content)

                            student_data['image'] = image_path
                        else:
                            no_image.append(i.get('full_name'))

                        Student.objects.update_or_create(
                            student_id_number=i['student_id_number'],
                            defaults=student_data
                        )

                    except Exception as e:
                        tb = traceback.extract_tb(e.__traceback__)[-1]
                        line_no = tb.lineno
                        class_name = e.__class__.__name__
                        error_message = (
                            f"❌ Xatolik [{class_name}] - {i.get('student_id_number')} "
                            f"talabani qayta ishlashda. "
                            f"Qator: {line_no}. Sabab: {str(e)}"
                        )
                        exceptions.append(error_message)

                # 🔄 ThreadPool bilan tezlashtirish
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = [executor.submit(process_student, i) for i in data]
                    for future in as_completed(futures):
                        future.result()

            except Exception as e:
                tb = traceback.extract_tb(e.__traceback__)[-1]
                exceptions.append(
                    f"❌ Global xatolik qator {tb.lineno}: {str(e)}"
                )

        # 🔗 API’dan barcha sahifalarni olish
        def get_hemis_url(result):
            total_pages = int(result.json()['data']['pagination']['pageCount'])
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = []
                for page in range(1, total_pages + 1):
                    headers = {
                        'Content-Type': 'application/json',
                        'Authorization': f"{token.hemis_token_type} {token.hemis_token}"
                    }
                    params = {
                        'page': page,
                        'limit': '200',
                        '_education_form': '16'
                    }
                    time.sleep(0.1)  # Rate limit uchun
                    futures.append(executor.submit(requests.get, baseurl + pathurl, headers=headers, params=params))

                for future in as_completed(futures):
                    response = future.result()
                    if response.status_code == 429:
                        time.sleep(int(response.headers.get('Retry-After', 5)))
                        continue
                    data = response.json()['data']['items']
                    create_or_update_students(data)

        get_hemis_url(response)
        elapsed_time = time.time() - start_time

        if not exceptions:
            return Response({
                'status': status.HTTP_200_OK,
                'message': '✅ Talabalar bazaga qo‘shildi va yangilandi!',
                'execution_time': f'{elapsed_time:.2f} soniya',
                'no_images': no_image,
            })
        else:
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': '⚠️ Quyidagi xatoliklar topildi:',
                'execution_time': f'{elapsed_time:.2f} soniya',
                'no_images': no_image,
                'exceptions': exceptions,
            })


# ----------------------------------------------------------------------------------------------------------------------
@method_decorator(csrf_exempt, name='dispatch')
class StudentSecondApiView(views.APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

    def get(self, request, format=None):
        start_time = time.time()

        try:
            hemis = Hemis_Base.objects.get(own_uniq=8)
        except Hemis_Base.DoesNotExist:
            return Response({'error': 'Hemis modulida biriktirilmagan'})

        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi

        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
        except HemisToken.DoesNotExist:
            return Response({'error': 'Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'})

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"{token.hemis_token_type} {token.hemis_token}"
        }
        params = {
            'page': '1',
            'limit': '200',
            '_education_form': '15'
        }
        response = requests.get(baseurl + pathurl, headers=headers, params=params)

        no_image = []
        exceptions = []

        def create_or_update_students(data):
            try:
                fk_fields = {
                    'gender': (Gender, 'code', 'gender', 'code'),
                    'new_specialty': (AllSpeciality, 'spec_id', 'specialty', 'id'),
                    'studentStatus': (H_Student_Status, 'code', 'studentStatus', 'code'),
                    'educationForm': (Educationform, 'code', 'educationForm', 'code'),
                    'educationType': (Educationtype, 'code', 'educationType', 'code'),
                    'educationYear': (Educationyear, 'code', 'educationYear', 'code'),
                    'paymentForm': (FormOfPayment, 'code', 'paymentForm', 'code'),
                    'group': (Group, 'id', 'group', 'h_id'),
                    'faculty': (Faculty, 'id', 'department', 'hemisid'),
                    'level': (HCourse, 'code', 'level', 'code'),
                    'semester': (Hsemester_action, 'id', 'semester', 'h_id'),
                    'country': (State, 'code', 'country', 'code'),
                    'province': (City, 'code', 'province', 'code'),
                    'district': (City, 'code', 'district', 'code'),
                    'citizenship': (H_Citizenship_type, 'code', 'citizenship', 'code'),
                    'socialCategory': (H_Social_Category, 'code', 'socialCategory', 'code'),
                    'accommodation': (H_Accommodation, 'code', 'accommodation', 'code'),
                }

                all_instances = {}
                for key, (model_cls, id_field, data_key, lookup) in fk_fields.items():
                    ids = [item.get(data_key, {}).get(id_field) for item in data if
                           data_key in item and id_field in item.get(data_key, {})]
                    instances = model_cls.objects.filter(**{f"{lookup}__in": ids}).distinct()
                    all_instances[key] = {getattr(instance, lookup): instance for instance in instances}

                def process_student(i):
                    try:
                        user, created = User.objects.get_or_create(
                            username=i['student_id_number'],
                            defaults={
                                'role': 'student',
                                'password': make_password(i['student_id_number']),
                                'first_name': i['first_name'],
                                'last_name': i['second_name']
                            }
                        )
                        if not created:
                            user.first_name = i['first_name']
                            user.last_name = i['second_name']
                            user.save()

                        student_data = {
                            'user': user,
                            'first_name': i['first_name'],
                            'second_name': i['second_name'],
                            'third_name': i['third_name'],
                            'full_name': i['full_name'],
                            'student_id_number': i['student_id_number'],
                            'birth_date': i['birth_date'],
                            'gender': all_instances['gender'][i['gender']['code']],
                            'new_specialty': all_instances['new_specialty'][i['specialty']['id']],
                            'studentStatus': all_instances['studentStatus'][i['studentStatus']['code']],
                            'educationForm': all_instances['educationForm'][i['educationForm']['code']],
                            'educationType': all_instances['educationType'][i['educationType']['code']],
                            'educationYear': all_instances['educationYear'][i['educationYear']['code']],
                            'paymentForm': all_instances['paymentForm'][i['paymentForm']['code']],
                            'group': all_instances['group'][i['group']['id']],
                            'faculty': all_instances['faculty'][i['department']['id']],
                            'level': all_instances['level'][i['level']['code']],
                            'semester': all_instances['semester'][i['semester']['id']],
                            'country': all_instances['country'][i['country']['code']],
                            'province': all_instances['province'][i['province']['code']],
                            'district': all_instances['district'][i['district']['code']],
                            'citizenship': all_instances['citizenship'][i['citizenship']['code']],
                            'socialCategory': all_instances['socialCategory'][i['socialCategory']['code']],
                            'accommodation': all_instances['accommodation'][i['accommodation']['code']],
                            'year_of_enter': str(i['year_of_enter']),
                            'avg_gpa': i['avg_gpa'],
                            'total_credit': i['total_credit'],
                        }

                        image_url = i.get('image')
                        if image_url:
                            response = requests.get(image_url)
                            if response.status_code != 200:
                                raise ValidationError(f"Image at {image_url} could not be fetched.")

                            directory = 'students/'
                            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, directory)):
                                os.makedirs(os.path.join(settings.MEDIA_ROOT, directory))

                            image_name = os.path.basename(image_url)
                            image_path = os.path.join(directory, image_name)

                            if os.path.exists(os.path.join(settings.MEDIA_ROOT, image_path)):
                                os.remove(os.path.join(settings.MEDIA_ROOT, image_path))

                            with open(os.path.join(settings.MEDIA_ROOT, image_path), 'wb') as f:
                                f.write(response.content)

                            student_data['image'] = image_path

                        else:
                            no_image.append(i.get('full_name'))

                        Student.objects.update_or_create(
                            student_id_number=i['student_id_number'],
                            defaults=student_data
                        )

                    except Exception as e:
                        class_name = e.__class__.__name__
                        error_message = f"Error in {class_name} while processing student {i.get('student_id_number')}: {str(e)}"
                        exceptions.append(error_message)
                        raise  # Stop execution

                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = [executor.submit(process_student, i) for i in data]
                    for future in as_completed(futures):
                        try:
                            future.result()
                        except Exception as exc:
                            print(f'Error 2-row: {exc}')
                            exceptions.append(str(exc))

            except ValidationError as e:
                logger.error(f'Error 3-row: {e}')

                exceptions.append({'validation_error': str(e)})
            except Exception as e:
                exceptions.append(str(e))

        def get_hemis_url(result):
            total_pages = int(result.json()['data']['pagination']['pageCount'])
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for page in range(1, total_pages + 1):
                    headers = {
                        'Content-Type': 'application/json',
                        'Authorization': f"{token.hemis_token_type} {token.hemis_token}"
                    }
                    params = {
                        'page': page,
                        'limit': '200',
                        '_education_form': '15'
                    }
                    # Add a delay to prevent exceeding rate limits
                    time.sleep(0.1)  # 10 requests per second => 0.1 second delay
                    futures.append(executor.submit(requests.get, baseurl + pathurl, headers=headers, params=params))

                for future in as_completed(futures):
                    response = future.result()
                    if response.status_code == 429:
                        logger.warning("Rate limit exceeded, retrying after a short delay...")
                        time.sleep(
                            int(response.headers.get('Retry-After', 5)))  # Wait as instructed by server or 5 seconds
                        continue  # Skip processing and retry later

                    data = response.json()['data']['items']
                    create_or_update_students(data)

        get_hemis_url(response)
        end_time = time.time()
        elapsed_time = end_time - start_time

        if not exceptions:
            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Baza qo`shildi va yangilandi!',
                    'execution_time': f'{elapsed_time:.2f} seconds',
                    'no_images': no_image,
                }
            )
        else:
            return Response(
                {
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': 'Quyidagi modullarda kamchilik topildi',
                    'execution_time': f'{elapsed_time:.2f} seconds',
                    'no_images': no_image,
                    'exceptions': exceptions,
                }
            )


@method_decorator(csrf_exempt, name='dispatch')
class StudentALLApiView(views.APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdminOrTeacher, ]

    def get(self, request, format=None):
        start_time = time.time()

        try:
            hemis = Hemis_Base.objects.get(own_uniq=8)
        except Hemis_Base.DoesNotExist:
            return Response({'error': 'Hemis modulida biriktirilmagan'})

        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi

        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
        except HemisToken.DoesNotExist:
            return Response({'error': 'Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'})

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"{token.hemis_token_type} {token.hemis_token}"
        }
        params = {
            'page': '1',
            'limit': '200',
        }
        response = requests.get(baseurl + pathurl, headers=headers, params=params)

        no_image = []
        exceptions = []

        def create_or_update_students(data):
            try:
                fk_fields = {
                    'gender': (Gender, 'code', 'gender', 'code'),
                    'new_specialty': (AllSpeciality, 'id', 'specialty', 'spec_id'),
                    'studentStatus': (H_Student_Status, 'code', 'studentStatus', 'code'),
                    'educationForm': (Educationform, 'code', 'educationForm', 'code'),
                    'educationType': (Educationtype, 'code', 'educationType', 'code'),
                    'educationYear': (Educationyear, 'code', 'educationYear', 'code'),
                    'paymentForm': (FormOfPayment, 'code', 'paymentForm', 'code'),
                    'group': (Group, 'id', 'group', 'h_id'),
                    'faculty': (Faculty, 'id', 'department', 'hemisid'),
                    'level': (HCourse, 'code', 'level', 'code'),
                    'semester': (Hsemester_action, 'id', 'semester', 'h_id'),
                    'country': (State, 'code', 'country', 'code'),
                    'province': (City, 'code', 'province', 'code'),
                    'district': (City, 'code', 'district', 'code'),
                    'citizenship': (H_Citizenship_type, 'code', 'citizenship', 'code'),
                    'socialCategory': (H_Social_Category, 'code', 'socialCategory', 'code'),
                    'accommodation': (H_Accommodation, 'code', 'accommodation', 'code'),
                }

                all_instances = {}
                for key, (model_cls, id_field, data_key, lookup) in fk_fields.items():
                    ids = [item.get(data_key, {}).get(id_field) for item in data if
                           data_key in item and id_field in item.get(data_key, {})]
                    instances = model_cls.objects.filter(**{f"{lookup}__in": ids}).distinct()
                    all_instances[key] = {getattr(instance, lookup): instance for instance in instances}

                def process_student(i):
                    try:
                        user, created = User.objects.get_or_create(
                            username=i['student_id_number'],
                            defaults={
                                'role': 'student',
                                'password': make_password(i['student_id_number']),
                                'first_name': i['first_name'],
                                'last_name': i['second_name']
                            }
                        )
                        if not created:
                            user.first_name = i['first_name']
                            user.last_name = i['second_name']
                            user.save()
                        # print(i)
                        student_data = {
                            'user': user,
                            'first_name': i['first_name'],
                            'second_name': i['second_name'],
                            'third_name': i['third_name'],
                            'full_name': i['full_name'],
                            'student_id_number': i['student_id_number'],
                            'birth_date': i['birth_date'],
                            'gender': all_instances['gender'][i['gender']['code']],
                            'new_specialty': all_instances['new_specialty'][i['specialty']['id']],
                            'studentStatus': all_instances['studentStatus'][i['studentStatus']['code']],
                            'educationForm': all_instances['educationForm'][i['educationForm']['code']],
                            'educationType': all_instances['educationType'][i['educationType']['code']],
                            'educationYear': all_instances['educationYear'][i['educationYear']['code']],
                            'paymentForm': all_instances['paymentForm'][i['paymentForm']['code']],
                            'group': all_instances['group'][i['group']['id']],
                            'faculty': all_instances['faculty'][i['department']['id']],
                            'level': all_instances['level'][i['level']['code']],
                            'semester': all_instances['semester'][i['semester']['id']],
                            'country': all_instances['country'][i['country']['code']],
                            'province': all_instances['province'][i['province']['code']],
                            'district': all_instances['district'][i['district']['code']],
                            'citizenship': all_instances['citizenship'][i['citizenship']['code']],
                            'socialCategory': all_instances['socialCategory'][i['socialCategory']['code']],
                            'accommodation': all_instances['accommodation'][i['accommodation']['code']],
                            'year_of_enter': str(i['year_of_enter']),
                            'avg_gpa': i['avg_gpa'],
                            'total_credit': i['total_credit'],
                        }

                        image_url = i.get('image')
                        if image_url:
                            response = requests.get(image_url)
                            if response.status_code != 200:
                                raise ValidationError(f"Image at {image_url} could not be fetched.")

                            directory = 'students/'
                            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, directory)):
                                os.makedirs(os.path.join(settings.MEDIA_ROOT, directory))

                            image_name = os.path.basename(image_url)
                            image_path = os.path.join(directory, image_name)

                            if os.path.exists(os.path.join(settings.MEDIA_ROOT, image_path)):
                                os.remove(os.path.join(settings.MEDIA_ROOT, image_path))

                            with open(os.path.join(settings.MEDIA_ROOT, image_path), 'wb') as f:
                                f.write(response.content)

                            student_data['image'] = image_path

                        else:
                            no_image.append(i.get('full_name'))

                        Student.objects.update_or_create(
                            student_id_number=i['student_id_number'],
                            defaults=student_data
                        )

                    except Exception as e:
                        class_name = e.__class__.__name__
                        error_message = f"Error in {class_name} while processing student {i.get('student_id_number')}: {str(e)}"
                        exceptions.append(error_message)
                        raise  # Stop execution

                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = [executor.submit(process_student, i) for i in data]
                    for future in as_completed(futures):
                        try:
                            future.result()
                        except Exception as exc:
                            print(f'Error 2-row: {exc}')

                            exceptions.append(str(exc))


            except ValidationError as e:
                logger.error(f'Error 3-row: {e}')

                exceptions.append({'validation_error': str(e)})
            except Exception as e:
                exceptions.append(str(e))

        def get_hemis_url(result):
            total_pages = int(result.json()['data']['pagination']['pageCount'])
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for page in range(1, total_pages + 1):
                    headers = {
                        'Content-Type': 'application/json',
                        'Authorization': f"{token.hemis_token_type} {token.hemis_token}"
                    }
                    params = {
                        'page': page,
                        'limit': '200'
                    }
                    # Add a delay to prevent exceeding rate limits
                    time.sleep(0.1)  # 10 requests per second => 0.1 second delay
                    futures.append(executor.submit(requests.get, baseurl + pathurl, headers=headers, params=params))

                for future in as_completed(futures):
                    response = future.result()
                    if response.status_code == 429:
                        logger.warning("Rate limit exceeded, retrying after a short delay...")
                        time.sleep(
                            int(response.headers.get('Retry-After', 5)))  # Wait as instructed by server or 5 seconds
                        continue  # Skip processing and retry later

                    data = response.json()['data']['items']
                    create_or_update_students(data)

        get_hemis_url(response)
        end_time = time.time()
        elapsed_time = end_time - start_time

        if not exceptions:
            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Baza qo`shildi va yangilandi!',
                    'execution_time': f'{elapsed_time:.2f} seconds',
                    'no_images': no_image,
                }
            )
        else:
            return Response(
                {
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': 'Quyidagi modullarda kamchilik topildi',
                    'execution_time': f'{elapsed_time:.2f} seconds',
                    'no_images': no_image,
                    'exceptions': exceptions,
                }
            )


class StudentDetail(APIView):
    serializer_class = StudentSerializer
    permission_classes = [AllowOnlyTrustedOrigins, IsStudent]

    def get_object(self, student_id_number):
        try:
            return Student.objects.get(student_id_number=student_id_number)
        except Student.DoesNotExist:
            return None

    def get(self, request, student_id_number, *args, **kwargs):
        student = self.get_object(student_id_number)
        user = request.user

        if student.user_id != user.id:
            return Response({
                "status": False,
                "message": "Siz bu talabaning maʼlumotlarini ko‘ra olmaysiz!"
            }, status=status.HTTP_403_FORBIDDEN)

        if student:
            serializer = self.serializer_class(student, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "status": False,
                "message": "Talaba topilmadi!"
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class StudentListAPIView(generics.ListAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdminOrTeacher, ]
    queryset = Student.objects.all().order_by('id')
    serializer_class = StudentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['group', 'faculty', 'paymentForm', 'educationYear', 'educationType', 'educationForm',
                        'studentStatus', 'specialty', 'level', 'semester', 'socialCategory']
    search_fields = ['full_name', 'student_id_number']


class StudentImageCheckApiView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, ]
    serializer_class = S_StudentImageSerializer

    def get_object(self, student_id_number):
        try:
            return Student.objects.get(student_id_number=student_id_number)
        except Student.DoesNotExist:
            return None

    def get(self, request, student_id_number, *args, **kwargs):
        student = self.get_object(student_id_number)

        if student:
            serializer = self.serializer_class(student, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "status": False,
                "message": "Talaba topilmadi!"
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class StudentForGroupApiView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsTeacherOrStudent, ]
    serializer_class = StudentForGroupSerializer

    def get(self, request, group_id, *args, **kwargs):
        queryset = Student.objects.filter(group_id=group_id)

        if queryset.exists():
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "status": False,
                "message": "Talaba topilmadi!"
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class LoginView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, ]

    @swagger_auto_schema(request_body=StudentLoginSerializer)
    def post(self, request, *args, **kwargs):
        login = request.data.get('login')
        password = request.data.get('password')

        if not login:
            return Response(
                {"status": False,
                 "message": "Loginni kiritish majburiy"
                 }, status=status.HTTP_400_BAD_REQUEST)
        if not password:
            return Response(
                {
                    "status": False,
                    "message": "Parolni kiritish majburiy"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            student = Student.objects.get(student_id_number=login)
        except Student.DoesNotExist:
            return Response({
                "status": False,
                "message": "Talaba topilmadi!"
            }, status=status.HTTP_404_NOT_FOUND)

        if student.is_active is False:
            return Response({
                "status": False,
                "message": "Siz ushbu tizimdan foydalana olmaysiz, iltimos ma'muriyat bilan bog'laning!"
            }, status=status.HTTP_403_FORBIDDEN)

        login_url = f"{HEMIS_URL}/rest/v1/auth/login"
        payload = {
            "login": login,
            "password": password
        }

        response = requests.post(login_url, json=payload, timeout=20)

        if response.status_code == 200:
            response_data = {}
            account_info_url = f"{HEMIS_URL}/rest/v1/account/me"
            token = response.json()['data']['token']
            headers = {
                "Authorization": f"Bearer {token}"
            }
            account_response = requests.get(account_info_url, headers=headers)
            fields_to_check = ['passport_pin', 'passport_number', 'email', 'phone', 'university', 'educationLang',
                               'address', 'validateUrl']

            update_fields = {}
            for field in fields_to_check:
                if field in account_response.json()['data']:
                    education_lang, created = Educationlang.objects.get_or_create(
                        code=account_response.json()['data']['educationLang']['code'])
                    setattr(student, 'educationLang', education_lang)
                    update_fields['educationLang'] = education_lang

                if not getattr(student, field) and field in account_response.json()['data']:
                    setattr(student, field, account_response.json()['data'][field])
                    update_fields[field] = account_response.json()['data'][field]
            if update_fields:
                student.save(update_fields=list(update_fields.keys()))
                user_instance = student.user

                token_serializer = MyTokenObtainPairSerializer()
                custom_token = token_serializer.get_token(user_instance)

                response_data = {
                    'success': account_response.json()['success'],
                    'error': account_response.json()['error'],
                    'code': account_response.json()['code'],
                    'token': token,
                    'custom_token': custom_token,
                    'data': account_response.json()['data']

                }
            return Response(response_data, status=account_response.status_code)
        else:
            return Response(
                {
                    "error": response.json()["error"]
                }, status=response.status_code)


class StudentPatchView(generics.GenericAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentUpdateSerializer
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

    def patch(self, request, *args, **kwargs):
        student_id = kwargs.get('pk')  # Assuming the primary key is passed in the URL
        try:
            student = Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Talaba topilmadi!'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(student, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class StudentMasofaikkiniApiView(views.APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

    def get(self, request, format=None):
        start_time = time.time()

        try:
            hemis = Hemis_Base.objects.get(own_uniq=8)
        except Hemis_Base.DoesNotExist:
            return Response({'error': '❌ Hemis modulida biriktirilmagan!'})

        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi

        token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
        if not token:
            return Response({'error': '❌ Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': '❌ Ushbu API token talab qiladi!'})

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"{token.hemis_token_type} {token.hemis_token}"
        }
        params = {
            'page': '1',
            'limit': '200',
            '_education_form': '22'
        }
        response = requests.get(baseurl + pathurl, headers=headers, params=params)

        no_image = []
        exceptions = []

        def create_or_update_students(data):
            try:
                # 1️⃣ FK obyektlarni oldindan yig‘ib olish
                fk_fields = {
                    'gender': (Gender, 'code', 'gender', 'code'),
                    'new_specialty': (AllSpeciality, 'id', 'specialty', 'spec_id'),
                    'studentStatus': (H_Student_Status, 'code', 'studentStatus', 'code'),
                    'educationForm': (Educationform, 'code', 'educationForm', 'code'),
                    'educationType': (Educationtype, 'code', 'educationType', 'code'),
                    'educationYear': (Educationyear, 'code', 'educationYear', 'code'),
                    'paymentForm': (FormOfPayment, 'code', 'paymentForm', 'code'),
                    'group': (Group, 'id', 'group', 'h_id'),
                    'faculty': (Faculty, 'id', 'department', 'hemisid'),
                    'level': (HCourse, 'code', 'level', 'code'),
                    'semester': (Hsemester_action, 'id', 'semester', 'h_id'),
                    'country': (State, 'code', 'country', 'code'),
                    'province': (City, 'code', 'province', 'code'),
                    'district': (City, 'code', 'district', 'code'),
                    'citizenship': (H_Citizenship_type, 'code', 'citizenship', 'code'),
                    'socialCategory': (H_Social_Category, 'code', 'socialCategory', 'code'),
                    'accommodation': (H_Accommodation, 'code', 'accommodation', 'code'),
                }

                all_instances = {}
                for key, (model_cls, id_field, data_key, lookup) in fk_fields.items():
                    ids = [item.get(data_key, {}).get(id_field) for item in data if
                           data_key in item and id_field in item.get(data_key, {})]
                    instances = model_cls.objects.filter(**{f"{lookup}__in": ids}).distinct()
                    all_instances[key] = {getattr(instance, lookup): instance for instance in instances}

                edu_lang_ids = [item['group']['educationLang']['code'] for item in data if
                                'group' in item and 'educationLang' in item['group']]
                edu_langs = Educationlang.objects.filter(code__in=edu_lang_ids)
                all_instances['educationLang'] = {lang.code: lang for lang in edu_langs}

                # 2️⃣ Talabalarni qayta ishlash
                def process_student(i):

                    try:
                        user, created = User.objects.get_or_create(
                            username=i['student_id_number'],
                            defaults={
                                'role': 'student',
                                'password': make_password(i['student_id_number']),
                                'first_name': i['first_name'],
                                'last_name': i['second_name']
                            }
                        )
                        if not created:
                            user.first_name = i['first_name']
                            user.last_name = i['second_name']
                            user.save()

                        student_data = {
                            'user': user,
                            'first_name': i['first_name'],
                            'second_name': i['second_name'],
                            'third_name': i['third_name'],
                            'full_name': i['full_name'],
                            'student_id_number': i['student_id_number'],
                            'birth_date': i['birth_date'],
                            'gender': all_instances['gender'][i['gender']['code']],
                            'new_specialty': all_instances['new_specialty'][i['specialty']['id']],
                            'studentStatus': all_instances['studentStatus'][i['studentStatus']['code']],
                            'educationForm': all_instances['educationForm'][i['educationForm']['code']],
                            'educationType': all_instances['educationType'][i['educationType']['code']],
                            'educationYear': all_instances['educationYear'][i['educationYear']['code']],
                            'paymentForm': all_instances['paymentForm'][i['paymentForm']['code']],
                            'group': all_instances['group'][i['group']['id']],
                            'faculty': all_instances['faculty'][i['department']['id']],
                            'educationLang': all_instances['educationLang'][i['group']['educationLang']['code']],
                            'level': all_instances['level'][i['level']['code']],
                            'semester': all_instances['semester'][i['semester']['id']],
                            'country': all_instances['country'][i['country']['code']],
                            'province': all_instances['province'][i['province']['code']],
                            'district': all_instances['district'][i['district']['code']],
                            'citizenship': all_instances['citizenship'][i['citizenship']['code']],
                            'socialCategory': all_instances['socialCategory'][i['socialCategory']['code']],
                            'accommodation': all_instances['accommodation'][i['accommodation']['code']],
                            'year_of_enter': str(i['year_of_enter']),
                            'avg_gpa': i['avg_gpa'],
                            'total_credit': i['total_credit'],
                        }

                        # 📌 Rasm yuklash
                        image_url = i.get('image')
                        if image_url:
                            response = requests.get(image_url)
                            if response.status_code != 200:
                                raise ValidationError(f"⚠️ {i['full_name']} uchun rasm yuklab bo‘lmadi: {image_url}")

                            directory = 'students/'
                            media_dir = os.path.join(settings.MEDIA_ROOT, directory)
                            os.makedirs(media_dir, exist_ok=True)

                            image_name = os.path.basename(image_url)
                            image_path = os.path.join(directory, image_name)

                            full_path = os.path.join(settings.MEDIA_ROOT, image_path)
                            if os.path.exists(full_path):
                                os.remove(full_path)

                            with open(full_path, 'wb') as f:
                                f.write(response.content)

                            student_data['image'] = image_path
                        else:
                            no_image.append(i.get('full_name'))

                        Student.objects.update_or_create(
                            student_id_number=i['student_id_number'],
                            defaults=student_data
                        )

                    except Exception as e:
                        tb = traceback.extract_tb(e.__traceback__)[-1]
                        line_no = tb.lineno
                        class_name = e.__class__.__name__
                        error_message = (
                            f"❌ Xatolik [{class_name}] - {i.get('student_id_number')} "
                            f"talabani qayta ishlashda. "
                            f"Qator: {line_no}. Sabab: {str(e)}"
                        )
                        exceptions.append(error_message)

                # 🔄 ThreadPool bilan tezlashtirish
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = [executor.submit(process_student, i) for i in data]
                    for future in as_completed(futures):
                        future.result()

            except Exception as e:
                tb = traceback.extract_tb(e.__traceback__)[-1]
                exceptions.append(
                    f"❌ Global xatolik qator {tb.lineno}: {str(e)}"
                )

        # 🔗 API’dan barcha sahifalarni olish
        def get_hemis_url(result):
            total_pages = int(result.json()['data']['pagination']['pageCount'])
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = []
                for page in range(1, total_pages + 1):
                    headers = {
                        'Content-Type': 'application/json',
                        'Authorization': f"{token.hemis_token_type} {token.hemis_token}"
                    }
                    params = {
                        'page': page,
                        'limit': '200',
                        '_education_form': '22'
                    }
                    time.sleep(0.1)  # Rate limit uchun
                    futures.append(executor.submit(requests.get, baseurl + pathurl, headers=headers, params=params))

                for future in as_completed(futures):
                    response = future.result()
                    if response.status_code == 429:
                        time.sleep(int(response.headers.get('Retry-After', 5)))
                        continue
                    data = response.json()['data']['items']
                    create_or_update_students(data)

        get_hemis_url(response)
        elapsed_time = time.time() - start_time

        if not exceptions:
            return Response({
                'status': status.HTTP_200_OK,
                'message': '✅ Talabalar bazaga qo‘shildi va yangilandi!',
                'execution_time': f'{elapsed_time:.2f} soniya',
                'no_images': no_image,
            })
        else:
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': '⚠️ Quyidagi xatoliklar topildi:',
                'execution_time': f'{elapsed_time:.2f} soniya',
                'no_images': no_image,
                'exceptions': exceptions,
            })


@method_decorator(csrf_exempt, name='dispatch')
class StudentQoshmaApiView(views.APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

    def get(self, request, format=None):
        start_time = time.time()

        try:
            hemis = Hemis_Base.objects.get(own_uniq=8)
        except Hemis_Base.DoesNotExist:
            return Response({'error': '❌ Hemis modulida biriktirilmagan!'})

        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi

        token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
        if not token:
            return Response({'error': '❌ Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': '❌ Ushbu API token talab qiladi!'})

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"{token.hemis_token_type} {token.hemis_token}"
        }
        params = {
            'page': '1',
            'limit': '200',
            '_education_form': '23'
        }
        response = requests.get(baseurl + pathurl, headers=headers, params=params)

        no_image = []
        exceptions = []

        def create_or_update_students(data):
            try:
                # 1️⃣ FK obyektlarni oldindan yig‘ib olish
                fk_fields = {
                    'gender': (Gender, 'code', 'gender', 'code'),
                    'new_specialty': (AllSpeciality, 'id', 'specialty', 'spec_id'),
                    'studentStatus': (H_Student_Status, 'code', 'studentStatus', 'code'),
                    'educationForm': (Educationform, 'code', 'educationForm', 'code'),
                    'educationType': (Educationtype, 'code', 'educationType', 'code'),
                    'educationYear': (Educationyear, 'code', 'educationYear', 'code'),
                    'paymentForm': (FormOfPayment, 'code', 'paymentForm', 'code'),
                    'group': (Group, 'id', 'group', 'h_id'),
                    'faculty': (Faculty, 'id', 'department', 'hemisid'),
                    'level': (HCourse, 'code', 'level', 'code'),
                    'semester': (Hsemester_action, 'id', 'semester', 'h_id'),
                    'country': (State, 'code', 'country', 'code'),
                    'province': (City, 'code', 'province', 'code'),
                    'district': (City, 'code', 'district', 'code'),
                    'citizenship': (H_Citizenship_type, 'code', 'citizenship', 'code'),
                    'socialCategory': (H_Social_Category, 'code', 'socialCategory', 'code'),
                    'accommodation': (H_Accommodation, 'code', 'accommodation', 'code'),
                }

                all_instances = {}
                for key, (model_cls, id_field, data_key, lookup) in fk_fields.items():
                    ids = [item.get(data_key, {}).get(id_field) for item in data if
                           data_key in item and id_field in item.get(data_key, {})]
                    instances = model_cls.objects.filter(**{f"{lookup}__in": ids}).distinct()
                    all_instances[key] = {getattr(instance, lookup): instance for instance in instances}

                edu_lang_ids = [item['group']['educationLang']['code'] for item in data if
                                'group' in item and 'educationLang' in item['group']]
                edu_langs = Educationlang.objects.filter(code__in=edu_lang_ids)
                all_instances['educationLang'] = {lang.code: lang for lang in edu_langs}

                # 2️⃣ Talabalarni qayta ishlash
                def process_student(i):

                    try:
                        user, created = User.objects.get_or_create(
                            username=i['student_id_number'],
                            defaults={
                                'role': 'student',
                                'password': make_password(i['student_id_number']),
                                'first_name': i['first_name'],
                                'last_name': i['second_name']
                            }
                        )
                        if not created:
                            user.first_name = i['first_name']
                            user.last_name = i['second_name']
                            user.save()

                        student_data = {
                            'user': user,
                            'first_name': i['first_name'],
                            'second_name': i['second_name'],
                            'third_name': i['third_name'],
                            'full_name': i['full_name'],
                            'student_id_number': i['student_id_number'],
                            'birth_date': i['birth_date'],
                            'gender': all_instances['gender'][i['gender']['code']],
                            'new_specialty': all_instances['new_specialty'][i['specialty']['id']],
                            'studentStatus': all_instances['studentStatus'][i['studentStatus']['code']],
                            'educationForm': all_instances['educationForm'][i['educationForm']['code']],
                            'educationType': all_instances['educationType'][i['educationType']['code']],
                            'educationYear': all_instances['educationYear'][i['educationYear']['code']],
                            'paymentForm': all_instances['paymentForm'][i['paymentForm']['code']],
                            'group': all_instances['group'][i['group']['id']],
                            'faculty': all_instances['faculty'][i['department']['id']],
                            'educationLang': all_instances['educationLang'][i['group']['educationLang']['code']],
                            'level': all_instances['level'][i['level']['code']],
                            'semester': all_instances['semester'][i['semester']['id']],
                            'country': all_instances['country'][i['country']['code']],
                            'province': all_instances['province'][i['province']['code']],
                            'district': all_instances['district'][i['district']['code']],
                            'citizenship': all_instances['citizenship'][i['citizenship']['code']],
                            'socialCategory': all_instances['socialCategory'][i['socialCategory']['code']],
                            'accommodation': all_instances['accommodation'][i['accommodation']['code']],
                            'year_of_enter': str(i['year_of_enter']),
                            'avg_gpa': i['avg_gpa'],
                            'total_credit': i['total_credit'],
                        }

                        # 📌 Rasm yuklash
                        image_url = i.get('image')
                        if image_url:
                            response = requests.get(image_url)
                            if response.status_code != 200:
                                raise ValidationError(f"⚠️ {i['full_name']} uchun rasm yuklab bo‘lmadi: {image_url}")

                            directory = 'students/'
                            media_dir = os.path.join(settings.MEDIA_ROOT, directory)
                            os.makedirs(media_dir, exist_ok=True)

                            image_name = os.path.basename(image_url)
                            image_path = os.path.join(directory, image_name)

                            full_path = os.path.join(settings.MEDIA_ROOT, image_path)
                            if os.path.exists(full_path):
                                os.remove(full_path)

                            with open(full_path, 'wb') as f:
                                f.write(response.content)

                            student_data['image'] = image_path
                        else:
                            no_image.append(i.get('full_name'))

                        Student.objects.update_or_create(
                            student_id_number=i['student_id_number'],
                            defaults=student_data
                        )

                    except Exception as e:
                        tb = traceback.extract_tb(e.__traceback__)[-1]
                        line_no = tb.lineno
                        class_name = e.__class__.__name__
                        error_message = (
                            f"❌ Xatolik [{class_name}] - {i.get('student_id_number')} "
                            f"talabani qayta ishlashda. "
                            f"Qator: {line_no}. Sabab: {str(e)}"
                        )
                        exceptions.append(error_message)

                # 🔄 ThreadPool bilan tezlashtirish
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = [executor.submit(process_student, i) for i in data]
                    for future in as_completed(futures):
                        future.result()

            except Exception as e:
                tb = traceback.extract_tb(e.__traceback__)[-1]
                exceptions.append(
                    f"❌ Global xatolik qator {tb.lineno}: {str(e)}"
                )

        # 🔗 API’dan barcha sahifalarni olish
        def get_hemis_url(result):
            total_pages = int(result.json()['data']['pagination']['pageCount'])
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = []
                for page in range(1, total_pages + 1):
                    headers = {
                        'Content-Type': 'application/json',
                        'Authorization': f"{token.hemis_token_type} {token.hemis_token}"
                    }
                    params = {
                        'page': page,
                        'limit': '200',
                        '_education_form': '23'
                    }
                    time.sleep(0.1)  # Rate limit uchun
                    futures.append(executor.submit(requests.get, baseurl + pathurl, headers=headers, params=params))

                for future in as_completed(futures):
                    response = future.result()
                    if response.status_code == 429:
                        time.sleep(int(response.headers.get('Retry-After', 5)))
                        continue
                    data = response.json()['data']['items']
                    create_or_update_students(data)

        get_hemis_url(response)
        elapsed_time = time.time() - start_time

        if not exceptions:
            return Response({
                'status': status.HTTP_200_OK,
                'message': '✅ Talabalar bazaga qo‘shildi va yangilandi!',
                'execution_time': f'{elapsed_time:.2f} soniya',
                'no_images': no_image,
            })
        else:
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': '⚠️ Quyidagi xatoliklar topildi:',
                'execution_time': f'{elapsed_time:.2f} soniya',
                'no_images': no_image,
                'exceptions': exceptions,
            })


@method_decorator(csrf_exempt, name='dispatch')
class StudentAllINApiView(views.APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

    def get(self, request, format=None):
        start_time = time.time()

        try:
            hemis = Hemis_Base.objects.get(own_uniq=8)
        except Hemis_Base.DoesNotExist:
            return Response({'error': '❌ Hemis modulida biriktirilmagan!'})

        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi

        token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
        if not token:
            return Response({'error': '❌ Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': '❌ Ushbu API token talab qiladi!'})

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"{token.hemis_token_type} {token.hemis_token}"
        }
        params = {
            'page': '1',
            'limit': '200',
        }
        response = requests.get(baseurl + pathurl, headers=headers, params=params)

        no_image = []
        exceptions = []

        def create_or_update_students(data):
            try:
                # 1️⃣ FK obyektlarni oldindan yig‘ib olish
                fk_fields = {
                    'gender': (Gender, 'code', 'gender', 'code'),
                    'new_specialty': (AllSpeciality, 'id', 'specialty', 'spec_id'),
                    'studentStatus': (H_Student_Status, 'code', 'studentStatus', 'code'),
                    'educationForm': (Educationform, 'code', 'educationForm', 'code'),
                    'educationType': (Educationtype, 'code', 'educationType', 'code'),
                    'educationYear': (Educationyear, 'code', 'educationYear', 'code'),
                    'paymentForm': (FormOfPayment, 'code', 'paymentForm', 'code'),
                    'group': (Group, 'id', 'group', 'h_id'),
                    'faculty': (Faculty, 'id', 'department', 'hemisid'),
                    'level': (HCourse, 'code', 'level', 'code'),
                    'semester': (Hsemester_action, 'id', 'semester', 'h_id'),
                    'country': (State, 'code', 'country', 'code'),
                    'province': (City, 'code', 'province', 'code'),
                    'district': (City, 'code', 'district', 'code'),
                    'citizenship': (H_Citizenship_type, 'code', 'citizenship', 'code'),
                    'socialCategory': (H_Social_Category, 'code', 'socialCategory', 'code'),
                    'accommodation': (H_Accommodation, 'code', 'accommodation', 'code'),
                }

                all_instances = {}
                for key, (model_cls, id_field, data_key, lookup) in fk_fields.items():
                    ids = [item.get(data_key, {}).get(id_field) for item in data if
                           data_key in item and id_field in item.get(data_key, {})]
                    instances = model_cls.objects.filter(**{f"{lookup}__in": ids}).distinct()
                    all_instances[key] = {getattr(instance, lookup): instance for instance in instances}

                edu_lang_ids = [item['group']['educationLang']['code'] for item in data if
                                'group' in item and 'educationLang' in item['group']]
                edu_langs = Educationlang.objects.filter(code__in=edu_lang_ids)
                all_instances['educationLang'] = {lang.code: lang for lang in edu_langs}

                # 2️⃣ Talabalarni qayta ishlash
                def process_student(i):

                    try:
                        user, created = User.objects.get_or_create(
                            username=i['student_id_number'],
                            defaults={
                                'role': 'student',
                                'password': make_password(i['student_id_number']),
                                'first_name': i['first_name'],
                                'last_name': i['second_name']
                            }
                        )
                        if not created:
                            user.first_name = i['first_name']
                            user.last_name = i['second_name']
                            user.save()

                        student_data = {
                            'user': user,
                            'first_name': i['first_name'],
                            'second_name': i['second_name'],
                            'third_name': i['third_name'],
                            'full_name': i['full_name'],
                            'student_id_number': i['student_id_number'],
                            'birth_date': i['birth_date'],
                            'gender': all_instances['gender'][i['gender']['code']],
                            'new_specialty': all_instances['new_specialty'][i['specialty']['id']],
                            'studentStatus': all_instances['studentStatus'][i['studentStatus']['code']],
                            'educationForm': all_instances['educationForm'][i['educationForm']['code']],
                            'educationType': all_instances['educationType'][i['educationType']['code']],
                            'educationYear': all_instances['educationYear'][i['educationYear']['code']],
                            'paymentForm': all_instances['paymentForm'][i['paymentForm']['code']],
                            'group': all_instances['group'][i['group']['id']],
                            'faculty': all_instances['faculty'][i['department']['id']],
                            'educationLang': all_instances['educationLang'][i['group']['educationLang']['code']],
                            'level': all_instances['level'][i['level']['code']],
                            'semester': all_instances['semester'][i['semester']['id']],
                            'country': all_instances['country'][i['country']['code']],
                            'province': all_instances['province'][i['province']['code']],
                            'district': all_instances['district'][i['district']['code']],
                            'citizenship': all_instances['citizenship'][i['citizenship']['code']],
                            'socialCategory': all_instances['socialCategory'][i['socialCategory']['code']],
                            'accommodation': all_instances['accommodation'][i['accommodation']['code']],
                            'year_of_enter': str(i['year_of_enter']),
                            'avg_gpa': i['avg_gpa'],
                            'total_credit': i['total_credit'],
                        }

                        # 📌 Rasm yuklash
                        image_url = i.get('image')
                        if image_url:
                            response = requests.get(image_url)
                            if response.status_code != 200:
                                raise ValidationError(f"⚠️ {i['full_name']} uchun rasm yuklab bo‘lmadi: {image_url}")

                            directory = 'students/'
                            media_dir = os.path.join(settings.MEDIA_ROOT, directory)
                            os.makedirs(media_dir, exist_ok=True)

                            image_name = os.path.basename(image_url)
                            image_path = os.path.join(directory, image_name)

                            full_path = os.path.join(settings.MEDIA_ROOT, image_path)
                            if os.path.exists(full_path):
                                os.remove(full_path)

                            with open(full_path, 'wb') as f:
                                f.write(response.content)

                            student_data['image'] = image_path
                        else:
                            no_image.append(i.get('full_name'))

                        Student.objects.update_or_create(
                            student_id_number=i['student_id_number'],
                            defaults=student_data
                        )

                    except Exception as e:
                        tb = traceback.extract_tb(e.__traceback__)[-1]
                        line_no = tb.lineno
                        class_name = e.__class__.__name__
                        error_message = (
                            f"❌ Xatolik [{class_name}] - {i.get('student_id_number')} "
                            f"talabani qayta ishlashda. "
                            f"Qator: {line_no}. Sabab: {str(e)}"
                        )
                        exceptions.append(error_message)

                # 🔄 ThreadPool bilan tezlashtirish
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = [executor.submit(process_student, i) for i in data]
                    for future in as_completed(futures):
                        future.result()

            except Exception as e:
                tb = traceback.extract_tb(e.__traceback__)[-1]
                exceptions.append(
                    f"❌ Global xatolik qator {tb.lineno}: {str(e)}"
                )

        # 🔗 API’dan barcha sahifalarni olish
        def get_hemis_url(result):
            total_pages = int(result.json()['data']['pagination']['pageCount'])
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = []
                for page in range(1, total_pages + 1):
                    headers = {
                        'Content-Type': 'application/json',
                        'Authorization': f"{token.hemis_token_type} {token.hemis_token}"
                    }
                    params = {
                        'page': page,
                        'limit': '200',
                    }
                    time.sleep(0.1)  # Rate limit uchun
                    futures.append(executor.submit(requests.get, baseurl + pathurl, headers=headers, params=params))

                for future in as_completed(futures):
                    response = future.result()
                    if response.status_code == 429:
                        time.sleep(int(response.headers.get('Retry-After', 5)))
                        continue
                    data = response.json()['data']['items']
                    create_or_update_students(data)

        get_hemis_url(response)
        elapsed_time = time.time() - start_time

        if not exceptions:
            return Response({
                'status': status.HTTP_200_OK,
                'message': '✅ Talabalar bazaga qo‘shildi va yangilandi!',
                'execution_time': f'{elapsed_time:.2f} soniya',
                'no_images': no_image,
            })
        else:
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': '⚠️ Quyidagi xatoliklar topildi:',
                'execution_time': f'{elapsed_time:.2f} soniya',
                'no_images': no_image,
                'exceptions': exceptions,
            })


@method_decorator(csrf_exempt, name='dispatch')
class StudentSecondSrtqApiView(views.APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin]

    def get(self, request, format=None):
        start_time = time.time()

        try:
            hemis = Hemis_Base.objects.get(own_uniq=8)
        except Hemis_Base.DoesNotExist:
            return Response({'error': '❌ Hemis modulida biriktirilmagan!'})

        token = HemisToken.objects.filter(
            status=True,
            hemis_user=hemis.hemis_user
        ).first()

        if not token:
            return Response({'error': '❌ Faol token mavjud emas!'})

        if hemis.openapi:
            return Response({'error': '❌ Ushbu API token talab qiladi!'})

        baseurl = hemis.base_url + hemis.path_url

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"{token.hemis_token_type} {token.hemis_token}"
        }

        params = {
            'page': 1,
            'limit': 200,
            '_education_form': 15
        }

        first_response = requests.get(baseurl, headers=headers, params=params)

        no_image = []
        exceptions = []

        # ============================
        # STUDENT PROCESSOR
        # ============================

        def create_or_update_students(data):

            try:
                fk_fields = {
                    'gender': (Gender, 'code', 'gender', 'code'),
                    'new_specialty': (AllSpeciality, 'id', 'specialty', 'spec_id'),
                    'studentStatus': (H_Student_Status, 'code', 'studentStatus', 'code'),
                    'educationForm': (Educationform, 'code', 'educationForm', 'code'),
                    'educationType': (Educationtype, 'code', 'educationType', 'code'),
                    'educationYear': (Educationyear, 'code', 'educationYear', 'code'),
                    'paymentForm': (FormOfPayment, 'code', 'paymentForm', 'code'),
                    'group': (Group, 'id', 'group', 'h_id'),
                    'faculty': (Faculty, 'id', 'department', 'hemisid'),
                    'level': (HCourse, 'code', 'level', 'code'),
                    'semester': (Hsemester_action, 'id', 'semester', 'h_id'),
                    'country': (State, 'code', 'country', 'code'),
                    'province': (City, 'code', 'province', 'code'),
                    'district': (City, 'code', 'district', 'code'),
                    'citizenship': (H_Citizenship_type, 'code', 'citizenship', 'code'),
                    'socialCategory': (H_Social_Category, 'code', 'socialCategory', 'code'),
                    'accommodation': (H_Accommodation, 'code', 'accommodation', 'code'),
                }

                all_instances = {}

                for key, (model, id_field, data_key, lookup) in fk_fields.items():
                    ids = [
                        item.get(data_key, {}).get(id_field)
                        for item in data
                        if data_key in item and id_field in item[data_key]
                    ]

                    objs = model.objects.filter(**{f"{lookup}__in": ids})
                    all_instances[key] = {
                        getattr(obj, lookup): obj for obj in objs
                    }

                # Education language
                lang_ids = [
                    item['group']['educationLang']['code']
                    for item in data
                    if 'group' in item and 'educationLang' in item['group']
                ]

                langs = Educationlang.objects.filter(code__in=lang_ids)
                all_instances['educationLang'] = {
                    l.code: l for l in langs
                }

                # ============================
                # SINGLE STUDENT
                # ============================

                def process_student(i):

                    try:
                        # 🚫 GROUP CHECK (asosiy shart)
                        group_id = i['group']['id']
                        group_obj = all_instances['group'].get(group_id)

                        if not group_obj:
                            return  # TO‘LIQ SKIP

                        # ✅ USER faqat group bor bo‘lsa yaratiladi
                        user, created = User.objects.get_or_create(
                            username=i['student_id_number'],
                            defaults={
                                'role': 'student',
                                'password': make_password(i['student_id_number']),
                                'first_name': i['first_name'],
                                'last_name': i['second_name']
                            }
                        )

                        if not created:
                            user.first_name = i['first_name']
                            user.last_name = i['second_name']
                            user.save(update_fields=['first_name', 'last_name'])

                        student_data = {
                            'user': user,
                            'first_name': i['first_name'],
                            'second_name': i['second_name'],
                            'third_name': i['third_name'],
                            'full_name': i['full_name'],
                            'student_id_number': i['student_id_number'],
                            'birth_date': i['birth_date'],

                            'gender': all_instances['gender'].get(i['gender']['code']),
                            'new_specialty': all_instances['new_specialty'].get(i['specialty']['id']),
                            'studentStatus': all_instances['studentStatus'].get(i['studentStatus']['code']),
                            'educationForm': all_instances['educationForm'].get(i['educationForm']['code']),
                            'educationType': all_instances['educationType'].get(i['educationType']['code']),
                            'educationYear': all_instances['educationYear'].get(i['educationYear']['code']),
                            'paymentForm': all_instances['paymentForm'].get(i['paymentForm']['code']),
                            'group': group_obj,
                            'faculty': all_instances['faculty'].get(i['department']['id']),
                            'educationLang': all_instances['educationLang'].get(
                                i['group']['educationLang']['code']
                            ),
                            'level': all_instances['level'].get(i['level']['code']),
                            'semester': all_instances['semester'].get(i['semester']['id']),
                            'country': all_instances['country'].get(i['country']['code']),
                            'province': all_instances['province'].get(i['province']['code']),
                            'district': all_instances['district'].get(i['district']['code']),
                            'citizenship': all_instances['citizenship'].get(i['citizenship']['code']),
                            'socialCategory': all_instances['socialCategory'].get(i['socialCategory']['code']),
                            'accommodation': all_instances['accommodation'].get(i['accommodation']['code']),
                            'year_of_enter': str(i['year_of_enter']),
                            'avg_gpa': i['avg_gpa'],
                            'total_credit': i['total_credit'],
                        }

                        # ============================
                        # IMAGE (agar bo‘lsa)
                        # ============================

                        image_url = i.get('image')

                        if image_url:
                            try:
                                r = requests.get(image_url, timeout=10)

                                if r.status_code == 200:
                                    directory = 'students/'
                                    media_dir = os.path.join(settings.MEDIA_ROOT, directory)
                                    os.makedirs(media_dir, exist_ok=True)

                                    name = os.path.basename(image_url)
                                    rel_path = os.path.join(directory, name)
                                    full_path = os.path.join(settings.MEDIA_ROOT, rel_path)

                                    with open(full_path, 'wb') as f:
                                        f.write(r.content)

                                    student_data['image'] = rel_path
                                else:
                                    no_image.append(i['full_name'])

                            except:
                                no_image.append(i['full_name'])

                        else:
                            no_image.append(i['full_name'])

                        # ============================
                        # SAVE
                        # ============================

                        Student.objects.update_or_create(
                            student_id_number=i['student_id_number'],
                            defaults=student_data
                        )

                    except Exception as e:
                        tb = traceback.extract_tb(e.__traceback__)[-1]
                        exceptions.append(
                            f"{i.get('student_id_number')} | {e.__class__.__name__} | line {tb.lineno} | {e}"
                        )

                # ============================
                # PARALLEL EXECUTION
                # ============================

                with ThreadPoolExecutor(max_workers=6) as executor:
                    for _ in executor.map(process_student, data):
                        pass

            except Exception as e:
                tb = traceback.extract_tb(e.__traceback__)[-1]
                exceptions.append(f"GLOBAL | line {tb.lineno} | {e}")

        # ============================
        # PAGINATION FETCH
        # ============================

        def fetch_all(first_response):

            total_pages = int(
                first_response.json()['data']['pagination']['pageCount']
            )

            with ThreadPoolExecutor(max_workers=3) as executor:

                futures = []

                for page in range(1, total_pages + 1):
                    params = {
                        'page': page,
                        'limit': 200,
                        '_education_form': 16
                    }

                    futures.append(
                        executor.submit(
                            requests.get,
                            baseurl,
                            headers=headers,
                            params=params
                        )
                    )

                for future in as_completed(futures):
                    resp = future.result()

                    if resp.status_code == 200:
                        items = resp.json()['data']['items']
                        create_or_update_students(items)

        fetch_all(first_response)

        elapsed = time.time() - start_time

        return Response({
            'status': 200 if not exceptions else 400,
            'message': '✅ Sync tugadi',
            'execution_time': f'{elapsed:.2f} soniya',
            'no_images': no_image,
            'exceptions': exceptions
        })
