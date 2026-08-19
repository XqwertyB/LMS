import requests
from django.utils import timezone
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from config.permissions import AllowOnlyTrustedOrigins
from hemis.models import Hemis_Base, HemisToken
from students.serializers import S_H_Student_StatusSerializer
from .models import (
    Gender,
    H_Student_Status,
    FormOfPayment,
    State,
    H_Citizenship_type,
    H_Social_Category,
    H_Accommodation,
    EmployeeStatus,
    ExamTypes,
    TrainingType
)
from .permissions import IsAdmin, IsAdminTeacherOrStudent
from .serializers import ExamTypesSerializer


class ExamTypesGetApiView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=2)
        except:
            return Response({'error': 'Hemis modulida biriktirilmagan'})

        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi

        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
        except:
            return Response({'error': 'Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'})

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token.hemis_token_type + ' ' + token.hemis_token
        }
        params = {
            'classifier': 'h_exam_type',
            'page': '1',
            'limit': '200',
        }
        respon = requests.get(baseurl + pathurl, headers=headers, params=params)
        data = respon.json()['data']['items'][0]['options']
        # print(data)
        for i in data:
            obj, created = ExamTypes.objects.get_or_create(code=i['code'], defaults={'name': i['name']})
            if not created:
                obj.updated_at = timezone.now()
                obj.save()

        return Response(
            {
                'status': status.HTTP_200_OK,
                'message': 'Baza qo`shildi va yangilandi!'
            }
        )


class TrainingTypesGetApiView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=2)
        except:
            return Response({'error': 'Hemis modulida biriktirilmagan'})

        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi

        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
        except:
            return Response({'error': 'Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'})

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token.hemis_token_type + ' ' + token.hemis_token
        }
        params = {
            'classifier': 'h_training_type',
            'page': '1',
            'limit': '200',
        }
        respon = requests.get(baseurl + pathurl, headers=headers, params=params)
        data = respon.json()['data']['items'][0]['options']
        # print(data)
        for i in data:
            obj, created = TrainingType.objects.get_or_create(code=i['code'], defaults={'name': i['name']})
            if not created:
                obj.updated_at = timezone.now()
                obj.save()

        return Response(
            {
                'status': status.HTTP_200_OK,
                'message': 'Baza qo`shildi va yangilandi!'
            }
        )


class GenderGetApiView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=2)
        except:
            return Response({'error': 'Hemis modulida biriktirilmagan'})

        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi

        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
        except:
            return Response({'error': 'Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'})

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token.hemis_token_type + ' ' + token.hemis_token
        }
        params = {
            'classifier': 'h_gender',
            'page': '1',
            'limit': '200',
        }
        respon = requests.get(baseurl + pathurl, headers=headers, params=params)
        data = respon.json()['data']['items'][0]['options']

        for i in data:
            obj, created = Gender.objects.get_or_create(code=i['code'], defaults={'name': i['name']})

            if not created:
                obj.updated_at = timezone.now()
                obj.save()

        return Response(
            {
                'status': status.HTTP_200_OK,
                'message': 'Baza qo`shildi va yangilandi!'
            }
        )


class StudentStatusAllGetApiView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent,]
    serializer_class = S_H_Student_StatusSerializer

    def get(self, request, format=None):
        queryset = H_Student_Status.objects.all()

        if queryset.exists():
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "status": False,
                "message": "Student status topilmadi"
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class StudentStatusGetApiView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=2)
        except:
            return Response({'error': 'Hemis modulida biriktirilmagan'})

        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi

        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
        except:
            return Response({'error': 'Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'})

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token.hemis_token_type + ' ' + token.hemis_token
        }
        params = {
            'classifier': 'h_student_status',
            'page': '1',
            'limit': '200',
        }
        respon = requests.get(baseurl + pathurl, headers=headers, params=params)
        data = respon.json()['data']['items'][0]['options']

        for i in data:
            obj, created = H_Student_Status.objects.get_or_create(code=i['code'], defaults={'name': i['name']})
            if not created:
                obj.updated_at = timezone.now()
                obj.save()

        return Response(
            {
                'status': status.HTTP_200_OK,
                'message': 'Baza qo`shildi va yangilandi!',
            }
        )


class FormOfPaymentGetApiView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=2)
        except:
            return Response({'error': 'Hemis modulida biriktirilmagan'})

        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi

        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
        except:
            return Response({'error': 'Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'})

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token.hemis_token_type + ' ' + token.hemis_token
        }
        params = {
            'classifier': 'h_payment_form',
            'page': '1',
            'limit': '200',
        }
        respon = requests.get(baseurl + pathurl, headers=headers, params=params)
        data = respon.json()['data']['items'][0]['options']

        for i in data:
            obj, created = FormOfPayment.objects.get_or_create(code=i['code'], defaults={'name': i['name']})
            if not created:
                obj.updated_at = timezone.now()
                obj.save()

        return Response(
            {
                'status': status.HTTP_200_OK,
                'message': 'Baza qo`shildi va yangilandi!',
            }
        )


class EmployeeStatusApiView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=2)
        except:
            return Response({'error': 'Hemis modulida biriktirilmagan'})

        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi

        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
        except:
            return Response({'error': 'Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'})

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token.hemis_token_type + ' ' + token.hemis_token
        }
        params = {
            'classifier': 'h_teacher_status',
            'page': '1',
            'limit': '200',
        }
        respon = requests.get(baseurl + pathurl, headers=headers, params=params)

        data = respon.json()['data']['items'][0]['options']

        for i in data:
            obj, created = EmployeeStatus.objects.get_or_create(code=i['code'], defaults={'name': i['name']})

            if not created:
                obj.updated_at = timezone.now()
                obj.save()

        return Response(
            {
                'status': status.HTTP_200_OK,
                'message': 'Baza qo`shildi va yangilandi!'
            }
        )


class StateGetApiView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=2)
        except:
            return Response({'error': 'Hemis modulida biriktirilmagan'})

        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi

        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
        except:
            return Response({'error': 'Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'})

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token.hemis_token_type + ' ' + token.hemis_token
        }
        params = {
            'classifier': 'h_country',
            'page': '1',
            'limit': '200',
        }
        respon = requests.get(baseurl + pathurl, headers=headers, params=params)
        data = respon.json()['data']['items'][0]['options']

        for i in data:
            obj, created = State.objects.get_or_create(code=i['code'], defaults={'name': i['name']})
            if not created:
                obj.updated_at = timezone.now()
                obj.save()

        return Response(
            {
                'status': status.HTTP_200_OK,
                'message': 'Baza qo`shildi va yangilandi!',
            }
        )


class CitizenshipGetApiView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=2)
        except:
            return Response({'error': 'Hemis modulida biriktirilmagan'})

        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi

        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
        except:
            return Response({'error': 'Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'})

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token.hemis_token_type + ' ' + token.hemis_token
        }
        params = {
            'classifier': 'h_citizenship_type',
            'page': '1',
            'limit': '200',
        }
        respon = requests.get(baseurl + pathurl, headers=headers, params=params)
        data = respon.json()['data']['items'][0]['options']

        for i in data:
            obj, created = H_Citizenship_type.objects.get_or_create(code=i['code'], defaults={'name': i['name']})
            if not created:
                obj.updated_at = timezone.now()
                obj.save()

        return Response(
            {
                'status': status.HTTP_200_OK,
                'message': 'Baza qo`shildi va yangilandi!',
            }
        )


class Social_Category_GetApiView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=2)
        except:
            return Response({'error': 'Hemis modulida biriktirilmagan'})

        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi

        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
        except:
            return Response({'error': 'Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'})

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token.hemis_token_type + ' ' + token.hemis_token
        }
        params = {
            'classifier': 'h_social_category',
            'page': '1',
            'limit': '200',
        }
        respon = requests.get(baseurl + pathurl, headers=headers, params=params)
        data = respon.json()['data']['items'][0]['options']

        for i in data:
            obj, created = H_Social_Category.objects.get_or_create(code=i['code'], defaults={'name': i['name']})
            if not created:
                obj.updated_at = timezone.now()
                obj.save()

        return Response(
            {
                'status': status.HTTP_200_OK,
                'message': 'Baza qo`shildi va yangilandi!',
            }
        )


class H_Accommodation_GetApiView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=2)
        except:
            return Response({'error': 'Hemis modulida biriktirilmagan'})

        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi

        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
        except:
            return Response({'error': 'Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'})

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token.hemis_token_type + ' ' + token.hemis_token
        }
        params = {
            'classifier': 'h_accommodation',
            'page': '1',
            'limit': '200',
        }
        respon = requests.get(baseurl + pathurl, headers=headers, params=params)
        data = respon.json()['data']['items'][0]['options']

        for i in data:
            obj, created = H_Accommodation.objects.get_or_create(code=i['code'], defaults={'name': i['name']})
            if not created:
                obj.updated_at = timezone.now()
                obj.save()

        return Response(
            {
                'status': status.HTTP_200_OK,
                'message': 'Baza qo`shildi va yangilandi!',
            }
        )


class ExamTypeApiView(generics.ListAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent,]
    serializer_class = ExamTypesSerializer
    queryset = ExamTypes.objects.all()


class GetIpAddressAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent,]
    def get(self, request, format=None):
        client_ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '')

        return Response({'client_ip_address': client_ip_address})


from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response


class VideoStream(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent,]
    def get(self, request):
        video_path = 'media/video_content/qwe.mp4'

        def stream_video():
            with open(video_path, 'rb') as video_file:
                while True:
                    chunk = video_file.read(10240)
                    if not chunk:
                        break
                    yield chunk

        response = StreamingHttpResponse(stream_video(), content_type='video/mp4')
        response['Content-Disposition'] = 'inline; filename="video.mp4"'
        return response


class Hemis_get_step_by_step(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request):
        list_url = {}
        list_url['1'] = "/otmcity/hemis/get/"
        list_url['2'] = "/otmtype/hemis/get/"
        list_url['3'] = "/otmshape/hemis/get/"
        list_url['4'] = "/otm/hemis/get/"
        list_url['5'] = "/otmsection/hemis/get/"
        list_url['6'] = "/faculty_type/hemis/get"
        list_url['7'] = "/otmfaculty/hemis/get/"
        list_url['8'] = "/otmdepartment/hemis/get/"
        list_url['9'] = "/science_branch/hemis/get/"
        list_url['10'] = "/bspeciality/hemis/get/"
        list_url['11'] = "/mspeciality/hemis/get/"
        list_url['12'] = "/ospeciality/hemis/get/"
        list_url['13'] = "/dspeciality/hemis/get/"  # s
        list_url['14'] = "/educationyear/hemis/get/"
        list_url['15'] = "/educationtype/hemis/get/"
        list_url['16'] = "/educationform/hemis/get"
        list_url['17'] = "/curriculum/hemis/get/"
        list_url['18'] = "/connectspeciality/hemis/get/"
        list_url['19'] = "/hcourse/hemis/get/"
        list_url['20'] = "/hsemester/hemis/get/"
        list_url['21'] = "/hsemesteraction/hemis/get/"
        list_url['22'] = "/speciality/hemis/get/all/"
        list_url['23'] = "/educationlang/hemis/get/"
        list_url['24'] = "/group/hemis/get/"
        list_url['25'] = "/gender/hemis/get/"
        list_url['26'] = "/student-status/hemis/get/"
        list_url['27'] = "/payment-form/hemis/get/"
        list_url['28'] = "/state/hemis/get/"
        list_url['29'] = "/citizenship/hemis/get/"
        list_url['30'] = "/social-category/hemis/get/"
        list_url['31'] = "/accommodation/hemis/get"
        list_url['32'] = "/students/get/hemis"
        list_url['33'] = "/subject/hemis/get/"
        list_url['34'] = "/subjectblock/hemis/get/"
        list_url['35'] = "/subjecttype/hemis/get/"
        list_url['36'] = "/subjectexamfinsh/hemis/get/"
        list_url['37'] = "/training-types/hemis/get/"
        list_url['38'] = "/exam-types/hemis/get/"
        list_url['39'] = "/subject_curriculum/hemis/get/"
        list_url['40'] = "/employee-status/hemis/get/"
        list_url['41'] = "/teachers/get/hemis/"
        answear = []
        base_url = "http://127.0.0.1:8000/api"
        val = 1
        for item in list_url.values():
            value = {}
            try:
                url = base_url + item
                respons = requests.get(url)
                value['number'] = val
                value['status_code'] = respons.status_code
                value['value'] = respons.json()
                answear.append(value)
                val = val + 1
            except Exception as ex:
                value['number'] = val
                value['status_code'] = 400
                value['value'] = str(ex)
                value['url'] = item
                answear.append(value)
                val = val + 1
        return Response(
            {'results': answear}, status=status.HTTP_200_OK
        )


class GetStudent(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request):
        base = "https://student.tfi.uz/rest/v1/data/student-list"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer" + ' ' + "1IkNesl_0WljArevGU-3psH286CA_GyC"
        }
        params = {
            'page': '1',
            'limit': '200',
            '_student_status': '14',
            '_education_type': '11',
            '_education_form': '11'
        }

        chekrespons = requests.post(base, headers=headers, params=params)
        pages = chekrespons.json()['data']['pagination']['pageSize']
        page = 1
        for i in range(page, pages, 1):
            pass

        return Response({'results': chekrespons.json()}, status=status.HTTP_200_OK)


class GetHemisSpeciality(APIView):
    def get(self, request):
        pass
