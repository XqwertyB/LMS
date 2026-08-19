from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

from config.permissions import AllowOnlyTrustedOrigins
from hemis.models import Hemis_sub, Hemis_Base, HemisToken
from shared.permissions import IsAdmin
# h_bachelor_speciality
from .models import Hsemester, HCourse, Hsemester_action, CurriculumWeeks
from learning_process.models import Curriculum, Educationyear
import datetime


class GetHCourse(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=2)
        except:
            return Response({'error': 'Hemis modulida birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi
        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user)[0]
        except:
            return Response({'error': 'Faol token mavjud emas!'},status=status.HTTP_400_BAD_REQUEST)

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'},status=status.HTTP_400_BAD_REQUEST)
        else:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': token.hemis_token_type + ' ' + token.hemis_token
            }
            params = {
                'classifier': 'h_course',
                'page': '1',
                'limit': '200',
            }
            respon = requests.get(baseurl + pathurl, headers=headers, params=params)
            data = respon.json()['data']['items'][0]['options']
            start_time = datetime.datetime.now()
            for i in data:
                obj = HCourse.objects.filter(code__iexact=i['code']).exists()
                if not obj:
                    new_obj = HCourse()
                    new_obj.code = i['code']
                    new_obj.name = i['name']
                    new_obj.save()
                else:
                    update_obj = HCourse.objects.get(code=i['code'])
                    update_obj.name = i['name']
                    update_obj.save()
            time = respon.elapsed.total_seconds()
            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time})


class GetHsemester(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=2)
        except:
            return Response({'error': 'Hemis modulida birktrilmagan'})
        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi
        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user)[0]
        except:
            return Response({'error': 'Faol token mavjud emas!'},status=status.HTTP_400_BAD_REQUEST)

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'},status=status.HTTP_400_BAD_REQUEST)
        else:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': token.hemis_token_type + ' ' + token.hemis_token
            }
            params = {
                'classifier': 'h_semester',
                'page': '1',
                'limit': '200',
            }
            respon = requests.get(baseurl + pathurl, headers=headers, params=params)
            data = respon.json()['data']['items'][0]['options']
            start_time = datetime.datetime.now()
            for i in data:
                obj = Hsemester.objects.filter(code__iexact=i['code']).exists()
                if not obj:
                    new_obj = Hsemester()
                    new_obj.code = i['code']
                    new_obj.name = i['name']
                    new_obj.save()
                else:
                    update_obj = Hsemester.objects.get(code=i['code'])
                    update_obj.name = i['name']
                    update_obj.save()
            time = respon.elapsed.total_seconds()
            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time},status=status.HTTP_200_OK)


class GetHsemesterAction(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=6)
        except:
            return Response({'error': 'Hemis modulida birktrilmagan'})
        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi
        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user)[0]
        except:
            return Response({'error': 'Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'})
        else:
            start_time = datetime.datetime.now()
            curricm = Curriculum.objects.all()
            for j in curricm:
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': token.hemis_token_type + ' ' + token.hemis_token
                }
                params = {
                    'page': '1',
                    'limit': '100',
                    '_curriculum': j.cur_id
                }
                respon = requests.get(baseurl + pathurl, headers=headers, params=params)
                data = respon.json()
                page = data['data']['pagination']['page']
                pagecount = data['data']['pagination']['pageCount'] + 1
                for i in range(int(page), int(pagecount), 1):
                    params = {
                        'page': str(i),
                        'limit': '100',
                        '_curriculum': j.cur_id
                    }
                    prespon = requests.get(baseurl + pathurl, headers=headers, params=params)
                    rdata = prespon.json()['data']['items']
                    for rx in rdata:
                        check = Hsemester_action.objects.filter(h_id=rx['id']).exists()
                        if check:
                            haci = Hsemester_action.objects.get(h_id=rx['id'])
                            edy = Educationyear.objects.filter(code=rx['_education_year']).exists()

                            if not edy:
                                return Response(
                                    {'error': 'Mana shu yerda error Hemis modulida oquv yili birktrilmagan'}
                                    ,status=status.HTTP_400_BAD_REQUEST)
                            edy = Educationyear.objects.get(code=rx['_education_year'])
                            if rx['level'] is not None:
                                course = HCourse.objects.filter(code=rx['level']['code']).exists()
                                if not course:
                                    return Response({'error': 'Hemis modulida oquv kurslari birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                                course = HCourse.objects.get(code=rx['level']['code'])
                            else:
                                course = None
                            semester = Hsemester.objects.filter(code=rx['code']).exists()
                            if not semester:
                                return Response({'error': 'Hemis modulida oquv semestrlar birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                            semester = Hsemester.objects.get(code=rx['code'])
                            haci.curriculum = j
                            haci.education_year = edy
                            haci.level = course
                            haci.semester = semester
                            haci.current = rx['current']
                            haci.save()
                            for cw in rx['curriculumWeeks']:
                                if CurriculumWeeks.objects.filter(h_id=cw['id']).exists():
                                    curws = CurriculumWeeks.objects.get(h_id=cw['id'])
                                    curws.msemester = haci
                                    curws.current = cw['current']
                                    curws.start_date = cw['start_date']
                                    curws.end_date = cw['end_date']
                                    curws.start_date_f = datetime.datetime.strptime(cw['start_date_f'],
                                                                                    "%d.%m.%Y").date()
                                    curws.end_date_f = datetime.datetime.strptime(cw['end_date_f'], "%d.%m.%Y").date()
                                    curws.save()
                                else:
                                    curw = CurriculumWeeks()
                                    curw.h_id = cw['id']
                                    curw.msemester = haci
                                    curw.current = cw['current']
                                    curw.start_date = cw['start_date']
                                    curw.end_date = cw['end_date']
                                    curw.start_date_f = datetime.datetime.strptime(cw['start_date_f'],
                                                                                   "%d.%m.%Y").date()
                                    curw.end_date_f = datetime.datetime.strptime(cw['end_date_f'], "%d.%m.%Y").date()
                                    curw.save()
                        else:
                            edy = Educationyear.objects.filter(code=rx['_education_year']).exists()
                            #print("A:", rx['_education_year'])
                           # print("B:", rx)
                            if not edy:
                                return Response({'error': 'Shu yer 2 Hemis modulida oquv yili birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                            edy = Educationyear.objects.get(code=rx['_education_year'])
                            # print(rx)
                            if rx['level'] is not None:
                                course = HCourse.objects.filter(code=rx['level']['code']).exists()
                                if not course:
                                    return Response({'error': 'Hemis modulida oquv kurslari birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                                course = HCourse.objects.get(code=rx['level']['code'])
                            else:
                                course = None
                            semester = Hsemester.objects.filter(code=rx['code']).exists()
                            if not semester:
                                return Response({'error': 'Hemis modulida oquv semestrlar birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                            semester = Hsemester.objects.get(code=rx['code'])

                            hac = Hsemester_action()
                            hac.h_id = rx['id']
                            hac.curriculum = j
                            hac.education_year = edy
                            hac.level = course
                            hac.semester = semester
                            hac.current = rx['current']
                            hac.save()
                            for cw in rx['curriculumWeeks']:
                                curw = CurriculumWeeks()
                                curw.h_id = cw['id']
                                curw.msemester = hac
                                curw.current = cw['current']
                                curw.start_date = cw['start_date']
                                curw.end_date = cw['end_date']
                                curw.start_date_f = datetime.datetime.strptime(cw['start_date_f'], "%d.%m.%Y").date()
                                curw.end_date_f = datetime.datetime.strptime(cw['end_date_f'], "%d.%m.%Y").date()
                                curw.save()

            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time},status=status.HTTP_200_OK)


class GetThisYearHsemesterAction(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    @swagger_auto_schema(
        tags=['Jismoniy Tarbiya uchun'],
        operation_summary="Joriy yil o‘quv semestrlari va haftalarini HEMIS API’dan olib keladi",
        operation_description="""
    Ushbu endpoint HEMIS bazasidan joriy o‘quv yilidagi barcha semestrlar (Hsemester_action) va haftalik jadval (CurriculumWeeks) ma’lumotlarini olib,
    mahalliy bazada yangilaydi yoki qo‘shadi.
            """,
        responses={
            200: openapi.Response(
                description="Muvaffaqiyatli yangilandi yoki qo‘shildi",
                examples={
                    "application/json": {
                        "succes": "Baza qo`shildi va yangilandi!",
                        "time": "0:00:12.321123",
                        "checking_current": 0
                    }
                }
            ),
            400: openapi.Response(
                description="HEMIS ma’lumotlarida xato yoki bog‘lanmagan obyekt mavjud",
                examples={
                    "application/json": {"error": "Hemis modulida o‘quv yili biriktirilmagan"}
                }
            ),
            404: openapi.Response(
                description="Token yoki HEMIS bazasi topilmadi",
                examples={
                    "application/json": {"error": "Faol token mavjud emas!"}
                }
            ),
        }
    )
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=6)
        except:
            return Response({'error': 'Hemis modulida birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi
        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user)[0]
        except:
            return Response({'error': 'Faol token mavjud emas!'},status=status.HTTP_400_BAD_REQUEST)

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'},status=status.HTTP_400_BAD_REQUEST)
        else:
            start_time = datetime.datetime.now()
            curricm = Curriculum.objects.all()
            for j in curricm:
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': token.hemis_token_type + ' ' + token.hemis_token
                }
                params = {
                    'page': '1',
                    'limit': '100',
                    '_curriculum': j.cur_id,

                }
                respon = requests.get(baseurl + pathurl, headers=headers, params=params)
                data = respon.json()
                page = data['data']['pagination']['page']
                pagecount = data['data']['pagination']['pageCount'] + 1
                for i in range(int(page), int(pagecount), 1):
                    params = {
                        'page': str(i),
                        'limit': '100',
                        '_curriculum': j.cur_id
                    }
                    prespon = requests.get(baseurl + pathurl, headers=headers, params=params)
                    rdata = prespon.json()['data']['items']
                    for rx in rdata:
                        check = Hsemester_action.objects.filter(h_id=rx['id']).exists()
                        if check:
                            haci = Hsemester_action.objects.get(h_id=rx['id'])
                            edy = Educationyear.objects.filter(code=rx['_education_year']).exists()

                            if not edy:
                                return Response(
                                    {'error': 'Mana shu yerda error Hemis modulida oquv yili birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                            edy = Educationyear.objects.get(code=rx['_education_year'])
                            if rx['level'] is not None:
                                course = HCourse.objects.filter(code=rx['level']['code']).exists()
                                if not course:
                                    return Response({'error': 'Hemis modulida oquv kurslari birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                                course = HCourse.objects.get(code=rx['level']['code'])
                            else:
                                course = None
                            semester = Hsemester.objects.filter(code=rx['code']).exists()
                            if not semester:
                                return Response({'error': 'Hemis modulida oquv semestrlar birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                            semester = Hsemester.objects.get(code=rx['code'])
                            haci.curriculum = j
                            haci.education_year = edy
                            haci.level = course
                            haci.semester = semester
                            haci.current = rx['current']
                            haci.save()
                            for cw in rx['curriculumWeeks']:
                                if CurriculumWeeks.objects.filter(h_id=cw['id']).exists():
                                    curws = CurriculumWeeks.objects.get(h_id=cw['id'])
                                    curws.msemester = haci
                                    curws.current = cw['current']
                                    curws.start_date = cw['start_date']
                                    curws.end_date = cw['end_date']
                                    curws.start_date_f = datetime.datetime.strptime(cw['start_date_f'],
                                                                                    "%d.%m.%Y").date()
                                    curws.end_date_f = datetime.datetime.strptime(cw['end_date_f'], "%d.%m.%Y").date()
                                    curws.save()
                                else:
                                    curw = CurriculumWeeks()
                                    curw.h_id = cw['id']
                                    curw.msemester = haci
                                    curw.current = cw['current']
                                    curw.start_date = cw['start_date']
                                    curw.end_date = cw['end_date']
                                    curw.start_date_f = datetime.datetime.strptime(cw['start_date_f'],
                                                                                   "%d.%m.%Y").date()
                                    curw.end_date_f = datetime.datetime.strptime(cw['end_date_f'], "%d.%m.%Y").date()
                                    curw.save()
                        else:
                            checking_current = 0
                            if rx['current'] == True:
                                edy = Educationyear.objects.filter(code=rx['_education_year']).exists()
                                # print("A:", rx['_education_year'])
                                # print("B:", rx)
                                if not edy:
                                    return Response({'error': 'Shu yer 2 Hemis modulida oquv yili birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                                edy = Educationyear.objects.get(code=rx['_education_year'])
                                # print(rx)
                                if rx['level'] is not None:
                                    course = HCourse.objects.filter(code=rx['level']['code']).exists()
                                    if not course:
                                        return Response({'error': 'Hemis modulida oquv kurslari birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                                    course = HCourse.objects.get(code=rx['level']['code'])
                                else:
                                    course = None
                                semester = Hsemester.objects.filter(code=rx['code']).exists()
                                if not semester:
                                    return Response({'error': 'Hemis modulida oquv semestrlar birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                                semester = Hsemester.objects.get(code=rx['code'])

                                hac = Hsemester_action()
                                hac.h_id = rx['id']
                                hac.curriculum = j
                                hac.education_year = edy
                                hac.level = course
                                hac.semester = semester
                                hac.current = rx['current']
                                hac.save()
                                for cw in rx['curriculumWeeks']:
                                    curw = CurriculumWeeks()
                                    curw.h_id = cw['id']
                                    curw.msemester = hac
                                    curw.current = cw['current']
                                    curw.start_date = cw['start_date']
                                    curw.end_date = cw['end_date']
                                    curw.start_date_f = datetime.datetime.strptime(cw['start_date_f'],
                                                                                   "%d.%m.%Y").date()
                                    curw.end_date_f = datetime.datetime.strptime(cw['end_date_f'], "%d.%m.%Y").date()
                                    curw.save()
                            else:
                                checking_current += checking_current

            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time
        return Response(
            {'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time, 'checking_current': checking_current},status=status.HTTP_200_OK)
