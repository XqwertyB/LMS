import asyncio
import traceback

import aiohttp
from asgiref.sync import sync_to_async
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from collections import Counter
from config.permissions import AllowOnlyTrustedOrigins
from hemis.models import Hemis_sub, Hemis_Base, HemisToken
from shared.permissions import IsAdmin
# h_bachelor_speciality
from .models import Educationyear, Educationtype, Educationform, MarkingSystem, Curriculum, Science_branch, \
    Educationlang
from speciality.models import Bspeciality, AllSpeciality
import datetime
from universty.models import Faculty


class GetEducationyear(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

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
            return Response({'error': 'Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'})
        else:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': token.hemis_token_type + ' ' + token.hemis_token
            }
            params = {
                'classifier': 'h_education_year',
                'page': '1',
                'limit': '200',
            }
            respon = requests.get(baseurl + pathurl, headers=headers, params=params)
            data = respon.json()['data']['items'][0]['options']
            start_time = datetime.datetime.now()
            for i in data:
                obj = Educationyear.objects.filter(code__iexact=i['code']).exists()
                if not obj:
                    new_obj = Educationyear()
                    new_obj.code = i['code']
                    new_obj.name = i['name']
                    if 'current' in i:
                        new_obj.current = i['current']
                    new_obj.save()
                else:
                    update_obj = Educationyear.objects.get(code=i['code'])
                    update_obj.name = i['name']
                    if 'current' in i:
                        update_obj.current = i['current']
                    update_obj.save()
            time = respon.elapsed.total_seconds()
            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time})


class GetEducationtype(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

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
            return Response({'error': 'Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'})
        else:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': token.hemis_token_type + ' ' + token.hemis_token
            }
            params = {
                'classifier': 'h_education_type',
                'page': '1',
                'limit': '200',
            }
            respon = requests.get(baseurl + pathurl, headers=headers, params=params)
            data = respon.json()['data']['items'][0]['options']
            start_time = datetime.datetime.now()
            for i in data:
                obj = Educationtype.objects.filter(code__iexact=i['code']).exists()
                if not obj:
                    new_obj = Educationtype()
                    new_obj.code = i['code']
                    new_obj.name = i['name']
                    new_obj.save()
                else:
                    update_obj = Educationtype.objects.get(code=i['code'])
                    update_obj.name = i['name']
                    update_obj.save()
            time = respon.elapsed.total_seconds()
            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time})


class GetEducationform(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

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
            return Response({'error': 'Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'})
        else:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': token.hemis_token_type + ' ' + token.hemis_token
            }
            params = {
                'classifier': 'h_education_form',
                'page': '1',
                'limit': '200',
            }
            respon = requests.get(baseurl + pathurl, headers=headers, params=params)
            data = respon.json()['data']['items'][0]['options']
            start_time = datetime.datetime.now()
            for i in data:
                obj = Educationform.objects.filter(code__iexact=i['code']).exists()
                if not obj:
                    new_obj = Educationform()
                    new_obj.code = i['code']
                    new_obj.name = i['name']
                    new_obj.save()
                else:
                    update_obj = Educationform.objects.get(code=i['code'])
                    update_obj.name = i['name']
                    update_obj.save()
            time = respon.elapsed.total_seconds()
            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time})


class GetCurriculum(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=4)
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

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token.hemis_token_type + ' ' + token.hemis_token
        }

        params = {
            '_education_form': '16',
            'page': '1',
            'limit': '200',
        }

        respon = requests.get(baseurl + pathurl, headers=headers, params=params)
        data = respon.json()['data']['items']

        start_time = datetime.datetime.now()

        for i in data:
            bspecialiy = None
            educationyear = None
            educationtype = None
            educationform = None
            department = None
            markingsystem_1 = None
            markingsystem_2 = None

            try:
                if Curriculum.objects.filter(cur_id=i['id']).exists():
                    # update
                    if AllSpeciality.objects.filter(spec_id=i['specialty']['id']).exists():
                        try:
                            bspecialiy = AllSpeciality.objects.get(spec_id=i['specialty']['id'])
                            bspecialiy.spec_id = i['specialty']['id']
                            bspecialiy.save()
                        except:
                            return Response({'error': 'Yo`nalish soxalar bazada mavjud emas!'})

                    if Educationyear.objects.filter(code=i['educationYear']['code']).exists():
                        try:
                            educationyear = Educationyear.objects.get(code=i['educationYear']['code'])
                            educationyear.current = i['educationYear']['current']
                            educationyear.save()
                        except:
                            return Response({'error': 'O`quv yillar bazada mavjud emas!'})

                    if Educationtype.objects.filter(code=i['educationType']['code']).exists():
                        try:
                            educationtype = Educationtype.objects.get(code=i['educationType']['code'])
                        except:
                            return Response({'error': 'Yo`nalishlar bazada mavjud emas!'})

                    if Educationform.objects.filter(code=i['educationForm']['code']).exists():
                        try:
                            educationform = Educationform.objects.get(code=i['educationForm']['code'])
                        except:
                            return Response({'error': 'Ta`lim turlari bazada mavjud emas!'})

                    if MarkingSystem.objects.filter(code=i['markingSystem']['code']).exists():
                        try:
                            markingsystem_1 = MarkingSystem.objects.get(code=i['markingSystem']['code'])
                        except:
                            return Response({'error': 'Baholash tizimi bazada mavjud emas!'})
                    else:
                        try:
                            markingsystem_1 = MarkingSystem()
                            markingsystem_1.code = i['markingSystem']['code']
                            markingsystem_1.name = i['markingSystem']['name']
                            markingsystem_1.minimum_limit = i['markingSystem']['minimum_limit']
                            markingsystem_1.gpa_limit = i['markingSystem']['gpa_limit']
                            markingsystem_1.save()
                        except:
                            return Response({'error': 'Baholash tizimi yaratishda hatolik bor!'})

                    if Faculty.objects.filter(kod=i['department']['code']).exists():
                        try:
                            department = Faculty.objects.get(kod=i['department']['code'])
                        except:
                            return Response({'error': 'Fakultet bazada mavjud emas!'})

                    try:
                        curriculum = Curriculum.objects.get(cur_id=i['id'])
                        curriculum.name = i['name']
                        curriculum.new_specialty = bspecialiy
                        curriculum.educationyear = educationyear
                        curriculum.educationtype = educationtype
                        curriculum.educationform = educationform
                        curriculum.markingsystem = markingsystem_1
                        curriculum.department = department
                        curriculum.semester_count = i['semester_count']
                        curriculum.education_period = i['education_period']
                        curriculum.save()
                    except Exception as ex:
                        print(i)
                        print(ex)
                        return Response({'error': 'O`quv reja yangilashda hatolik bor!2'})
                else:
                    # new
                    if AllSpeciality.objects.filter(spec_id=i['specialty']['id']).exists():
                        try:
                            bspecialiy = AllSpeciality.objects.get(spec_id=i['specialty']['id'])
                            bspecialiy.spec_id = i['specialty']['id']
                            bspecialiy.save()
                        except:
                            return Response({'error': 'Yo`nalish soxalar bazada mavjud emas!'})

                    if Educationyear.objects.filter(code=i['educationYear']['code']).exists():
                        try:
                            educationyear = Educationyear.objects.get(code=i['educationYear']['code'])
                            educationyear.current = i['educationYear']['current']
                            educationyear.save()
                        except:
                            return Response({'error': 'O`quv yillar bazada mavjud emas!'})

                    if Educationtype.objects.filter(code=i['educationType']['code']).exists():
                        try:
                            educationtype = Educationtype.objects.get(code=i['educationType']['code'])
                        except:
                            return Response({'error': 'Yo`nalishlar bazada mavjud emas!'})

                    if Educationform.objects.filter(code=i['educationForm']['code']).exists():
                        try:
                            educationform = Educationform.objects.get(code=i['educationForm']['code'])
                        except:
                            return Response({'error': 'Ta`lim turlari bazada mavjud emas!'})

                    if MarkingSystem.objects.filter(code=i['markingSystem']['code']).exists():
                        try:
                            markingsystem_2 = MarkingSystem.objects.get(code=i['markingSystem']['code'])
                        except:
                            return Response({'error': 'Baholash tizimi bazada mavjud emas!'})
                    else:
                        try:
                            markingsystem_2 = MarkingSystem()
                            markingsystem_2.code = i['markingSystem']['code']
                            markingsystem_2.name = i['markingSystem']['name']
                            markingsystem_2.minimum_limit = i['markingSystem']['minimum_limit']
                            markingsystem_2.gpa_limit = i['markingSystem']['gpa_limit']
                            markingsystem_2.save()
                        except:
                            return Response({'error': 'Baholash tizimi yaratishda hatolik bor!'})

                    if Faculty.objects.filter(kod=i['department']['code']).exists():
                        try:
                            department = Faculty.objects.get(kod=i['department']['code'])
                        except:
                            return Response({'error': 'Fakultet bazada mavjud emas!'})

                    try:
                        curriculum = Curriculum()
                        curriculum.cur_id = i['id']
                        curriculum.name = i['name']
                        curriculum.new_specialty = bspecialiy
                        curriculum.educationyear = educationyear
                        curriculum.educationtype = educationtype
                        curriculum.educationform = educationform
                        curriculum.markingsystem = markingsystem_2
                        curriculum.department = department
                        curriculum.semester_count = i['semester_count']
                        curriculum.education_period = i['education_period']
                        curriculum.save()
                    except Exception as ex:
                        print(ex)
                        return Response({'error': 'O`quv reja yangilashda hatolik bor!1'})

            except:
                return Response({'succes': 'Baza qo`shishda xatolik bor!'})

        end_time = datetime.datetime.now()
        elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time})


class GetOtherCurriculum(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=4)
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

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token.hemis_token_type + ' ' + token.hemis_token
        }

        params = {
            '_education_form': '15',
            'page': '1',
            'limit': '200',
        }

        respon = requests.get(baseurl + pathurl, headers=headers, params=params)
        data = respon.json()['data']['items']

        start_time = datetime.datetime.now()

        for i in data:
            bspecialiy = None
            educationyear = None
            educationtype = None
            educationform = None
            department = None
            markingsystem_1 = None
            markingsystem_2 = None

            try:
                if Curriculum.objects.filter(cur_id=i['id']).exists():
                    # update
                    if AllSpeciality.objects.filter(spec_id=i['specialty']['id']).exists():
                        try:
                            bspecialiy = AllSpeciality.objects.get(spec_id=i['specialty']['id'])
                            bspecialiy.spec_id = i['specialty']['id']
                            bspecialiy.save()
                        except:
                            return Response({'error': 'Yo`nalish soxalar bazada mavjud emas!'})

                    if Educationyear.objects.filter(code=i['educationYear']['code']).exists():
                        try:
                            educationyear = Educationyear.objects.get(code=i['educationYear']['code'])
                            educationyear.current = i['educationYear']['current']
                            educationyear.save()
                        except:
                            return Response({'error': 'O`quv yillar bazada mavjud emas!'})

                    if Educationtype.objects.filter(code=i['educationType']['code']).exists():
                        try:
                            educationtype = Educationtype.objects.get(code=i['educationType']['code'])
                        except:
                            return Response({'error': 'Yo`nalishlar bazada mavjud emas!'})

                    if Educationform.objects.filter(code=i['educationForm']['code']).exists():
                        try:
                            educationform = Educationform.objects.get(code=i['educationForm']['code'])
                        except:
                            return Response({'error': 'Ta`lim turlari bazada mavjud emas!'})

                    if MarkingSystem.objects.filter(code=i['markingSystem']['code']).exists():
                        try:
                            markingsystem_1 = MarkingSystem.objects.get(code=i['markingSystem']['code'])
                        except:
                            return Response({'error': 'Baholash tizimi bazada mavjud emas!'})
                    else:
                        try:
                            markingsystem_1 = MarkingSystem()
                            markingsystem_1.code = i['markingSystem']['code']
                            markingsystem_1.name = i['markingSystem']['name']
                            markingsystem_1.minimum_limit = i['markingSystem']['minimum_limit']
                            markingsystem_1.gpa_limit = i['markingSystem']['gpa_limit']
                            markingsystem_1.save()
                        except:
                            return Response({'error': 'Baholash tizimi yaratishda hatolik bor!'})

                    if Faculty.objects.filter(kod=i['department']['code']).exists():
                        try:
                            department = Faculty.objects.get(kod=i['department']['code'])
                        except:
                            return Response({'error': 'Fakultet bazada mavjud emas!'})

                    try:
                        curriculum = Curriculum.objects.get(cur_id=i['id'])
                        curriculum.name = i['name']
                        curriculum.new_specialty = bspecialiy
                        curriculum.educationyear = educationyear
                        curriculum.educationtype = educationtype
                        curriculum.educationform = educationform
                        curriculum.markingsystem = markingsystem_1
                        curriculum.department = department
                        curriculum.semester_count = i['semester_count']
                        curriculum.education_period = i['education_period']
                        curriculum.save()
                    except Exception as ex:
                        print(ex)
                        return Response({'error': 'O`quv reja yangilashda hatolik bor!2'})
                else:
                    # new
                    if AllSpeciality.objects.filter(spec_id=i['specialty']['id']).exists():
                        try:
                            bspecialiy = AllSpeciality.objects.get(spec_id=i['specialty']['id'])
                            bspecialiy.spec_id = i['specialty']['id']
                            bspecialiy.save()
                        except:
                            return Response({'error': 'Yo`nalish soxalar bazada mavjud emas!'})

                    if Educationyear.objects.filter(code=i['educationYear']['code']).exists():
                        try:
                            educationyear = Educationyear.objects.get(code=i['educationYear']['code'])
                            educationyear.current = i['educationYear']['current']
                            educationyear.save()
                        except:
                            return Response({'error': 'O`quv yillar bazada mavjud emas!'})

                    if Educationtype.objects.filter(code=i['educationType']['code']).exists():
                        try:
                            educationtype = Educationtype.objects.get(code=i['educationType']['code'])
                        except:
                            return Response({'error': 'Yo`nalishlar bazada mavjud emas!'})

                    if Educationform.objects.filter(code=i['educationForm']['code']).exists():
                        try:
                            educationform = Educationform.objects.get(code=i['educationForm']['code'])
                        except:
                            return Response({'error': 'Ta`lim turlari bazada mavjud emas!'})

                    if MarkingSystem.objects.filter(code=i['markingSystem']['code']).exists():
                        try:
                            markingsystem_2 = MarkingSystem.objects.get(code=i['markingSystem']['code'])
                        except:
                            return Response({'error': 'Baholash tizimi bazada mavjud emas!'})
                    else:
                        try:
                            markingsystem_2 = MarkingSystem()
                            markingsystem_2.code = i['markingSystem']['code']
                            markingsystem_2.name = i['markingSystem']['name']
                            markingsystem_2.minimum_limit = i['markingSystem']['minimum_limit']
                            markingsystem_2.gpa_limit = i['markingSystem']['gpa_limit']
                            markingsystem_2.save()
                        except:
                            return Response({'error': 'Baholash tizimi yaratishda hatolik bor!'})

                    if Faculty.objects.filter(kod=i['department']['code']).exists():
                        try:
                            department = Faculty.objects.get(kod=i['department']['code'])
                        except:
                            return Response({'error': 'Fakultet bazada mavjud emas!'})

                    try:
                        curriculum = Curriculum()
                        curriculum.cur_id = i['id']
                        curriculum.name = i['name']
                        curriculum.new_specialty = bspecialiy
                        curriculum.educationyear = educationyear
                        curriculum.educationtype = educationtype
                        curriculum.educationform = educationform
                        curriculum.markingsystem = markingsystem_2
                        curriculum.department = department
                        curriculum.semester_count = i['semester_count']
                        curriculum.education_period = i['education_period']
                        curriculum.save()
                    except Exception as ex:
                        print(ex)
                        return Response({'error': 'O`quv reja yangilashda hatolik bor!1'})

            except:
                return Response({'succes': 'Baza qo`shishda xatolik bor!'})

        end_time = datetime.datetime.now()
        elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time})


class GetScience_branch(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

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
            return Response({'error': 'Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'})
        else:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': token.hemis_token_type + ' ' + token.hemis_token
            }
            params = {
                'classifier': 'h_science_branch',
                'page': '1',
                'limit': '200',
            }
            respon = requests.get(baseurl + pathurl, headers=headers, params=params)
            data = respon.json()['data']['items'][0]['options']
            start_time = datetime.datetime.now()
            for i in data:
                obj = Science_branch.objects.filter(code__iexact=i['code']).exists()
                if not obj:
                    new_obj = Science_branch()
                    new_obj.code = i['code']
                    new_obj.name = i['name']
                    new_obj.save()
                else:
                    update_obj = Science_branch.objects.get(code=i['code'])
                    update_obj.name = i['name']
                    update_obj.save()
            time = respon.elapsed.total_seconds()
            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time})


class GetEducationlang(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

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
            return Response({'error': 'Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'})
        else:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': token.hemis_token_type + ' ' + token.hemis_token
            }
            params = {
                'classifier': 'h_language',
                'page': '1',
                'limit': '200',
            }
            respon = requests.get(baseurl + pathurl, headers=headers, params=params)
            data = respon.json()['data']['items'][0]['options']
            start_time = datetime.datetime.now()
            for i in data:
                obj = Educationlang.objects.filter(code__iexact=i['code']).exists()
                if not obj:
                    new_obj = Educationlang()
                    new_obj.code = i['code']
                    new_obj.name = i['name']
                    new_obj.save()
                else:
                    update_obj = Educationlang.objects.get(code=i['code'])
                    update_obj.name = i['name']
                    update_obj.save()
            time = respon.elapsed.total_seconds()
            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time})


class GetSrtqiCurriculum(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=4)
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

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token.hemis_token_type + ' ' + token.hemis_token
        }

        params = {
            '_education_form': '13',
            'page': '1',
            'limit': '200',
        }

        respon = requests.get(baseurl + pathurl, headers=headers, params=params)
        data = respon.json()['data']['items']

        start_time = datetime.datetime.now()

        for i in data:
            bspecialiy = None
            educationyear = None
            educationtype = None
            educationform = None
            department = None
            markingsystem_1 = None
            markingsystem_2 = None

            try:
                if Curriculum.objects.filter(cur_id=i['id']).exists():
                    # update
                    if AllSpeciality.objects.filter(spec_id=i['specialty']['id']).exists():
                        try:
                            bspecialiy = AllSpeciality.objects.get(spec_id=i['specialty']['id'])
                            bspecialiy.spec_id = i['specialty']['id']
                            bspecialiy.save()
                        except:
                            return Response({'error': 'Yo`nalish soxalar bazada mavjud emas!'})

                    if Educationyear.objects.filter(code=i['educationYear']['code']).exists():
                        try:
                            educationyear = Educationyear.objects.get(code=i['educationYear']['code'])
                            educationyear.current = i['educationYear']['current']
                            educationyear.save()
                        except:
                            return Response({'error': 'O`quv yillar bazada mavjud emas!'})

                    if Educationtype.objects.filter(code=i['educationType']['code']).exists():
                        try:
                            educationtype = Educationtype.objects.get(code=i['educationType']['code'])
                        except:
                            return Response({'error': 'Yo`nalishlar bazada mavjud emas!'})

                    if Educationform.objects.filter(code=i['educationForm']['code']).exists():
                        try:
                            educationform = Educationform.objects.get(code=i['educationForm']['code'])
                        except:
                            return Response({'error': 'Ta`lim turlari bazada mavjud emas!'})

                    if MarkingSystem.objects.filter(code=i['markingSystem']['code']).exists():
                        try:
                            markingsystem_1 = MarkingSystem.objects.get(code=i['markingSystem']['code'])
                        except:
                            return Response({'error': 'Baholash tizimi bazada mavjud emas!'})
                    else:
                        try:
                            markingsystem_1 = MarkingSystem()
                            markingsystem_1.code = i['markingSystem']['code']
                            markingsystem_1.name = i['markingSystem']['name']
                            markingsystem_1.minimum_limit = i['markingSystem']['minimum_limit']
                            markingsystem_1.gpa_limit = i['markingSystem']['gpa_limit']
                            markingsystem_1.save()
                        except:
                            return Response({'error': 'Baholash tizimi yaratishda hatolik bor!'})

                    if Faculty.objects.filter(kod=i['department']['code']).exists():
                        try:
                            department = Faculty.objects.get(kod=i['department']['code'])
                        except:
                            return Response({'error': 'Fakultet bazada mavjud emas!'})

                    try:
                        curriculum = Curriculum.objects.get(cur_id=i['id'])
                        curriculum.name = i['name']
                        curriculum.new_specialty = bspecialiy
                        curriculum.educationyear = educationyear
                        curriculum.educationtype = educationtype
                        curriculum.educationform = educationform
                        curriculum.markingsystem = markingsystem_1
                        curriculum.department = department
                        curriculum.semester_count = i['semester_count']
                        curriculum.education_period = i['education_period']
                        curriculum.save()
                    except Exception as ex:
                        print(ex)
                        return Response({'error': 'O`quv reja yangilashda hatolik bor!2'})
                else:
                    # new
                    if AllSpeciality.objects.filter(spec_id=i['specialty']['id']).exists():
                        try:
                            bspecialiy = AllSpeciality.objects.get(spec_id=i['specialty']['id'])
                            bspecialiy.spec_id = i['specialty']['id']
                            bspecialiy.save()
                        except:
                            return Response({'error': 'Yo`nalish soxalar bazada mavjud emas!'})

                    if Educationyear.objects.filter(code=i['educationYear']['code']).exists():
                        try:
                            educationyear = Educationyear.objects.get(code=i['educationYear']['code'])
                            educationyear.current = i['educationYear']['current']
                            educationyear.save()
                        except:
                            return Response({'error': 'O`quv yillar bazada mavjud emas!'})

                    if Educationtype.objects.filter(code=i['educationType']['code']).exists():
                        try:
                            educationtype = Educationtype.objects.get(code=i['educationType']['code'])
                        except:
                            return Response({'error': 'Yo`nalishlar bazada mavjud emas!'})

                    if Educationform.objects.filter(code=i['educationForm']['code']).exists():
                        try:
                            educationform = Educationform.objects.get(code=i['educationForm']['code'])
                        except:
                            return Response({'error': 'Ta`lim turlari bazada mavjud emas!'})

                    if MarkingSystem.objects.filter(code=i['markingSystem']['code']).exists():
                        try:
                            markingsystem_2 = MarkingSystem.objects.get(code=i['markingSystem']['code'])
                        except:
                            return Response({'error': 'Baholash tizimi bazada mavjud emas!'})
                    else:
                        try:
                            markingsystem_2 = MarkingSystem()
                            markingsystem_2.code = i['markingSystem']['code']
                            markingsystem_2.name = i['markingSystem']['name']
                            markingsystem_2.minimum_limit = i['markingSystem']['minimum_limit']
                            markingsystem_2.gpa_limit = i['markingSystem']['gpa_limit']
                            markingsystem_2.save()
                        except:
                            return Response({'error': 'Baholash tizimi yaratishda hatolik bor!'})

                    if Faculty.objects.filter(kod=i['department']['code']).exists():
                        try:
                            department = Faculty.objects.get(kod=i['department']['code'])
                        except:
                            return Response({'error': 'Fakultet bazada mavjud emas!'})

                    try:
                        curriculum = Curriculum()
                        curriculum.cur_id = i['id']
                        curriculum.name = i['name']
                        curriculum.new_specialty = bspecialiy
                        curriculum.educationyear = educationyear
                        curriculum.educationtype = educationtype
                        curriculum.educationform = educationform
                        curriculum.markingsystem = markingsystem_2
                        curriculum.department = department
                        curriculum.semester_count = i['semester_count']
                        curriculum.education_period = i['education_period']
                        curriculum.save()
                    except Exception as ex:
                        print(ex)
                        return Response({'error': 'O`quv reja yangilashda hatolik bor!1'})

            except:
                return Response({'succes': 'Baza qo`shishda xatolik bor!'})

        end_time = datetime.datetime.now()
        elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time})

class GetSrtqi2Curriculum(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=4)
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

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token.hemis_token_type + ' ' + token.hemis_token
        }

        params = {
            '_education_form': '15',
            'page': '1',
            'limit': '200',
        }

        respon = requests.get(baseurl + pathurl, headers=headers, params=params)
        data = respon.json()['data']['items']

        start_time = datetime.datetime.now()

        for i in data:
            bspecialiy = None
            educationyear = None
            educationtype = None
            educationform = None
            department = None
            markingsystem_1 = None
            markingsystem_2 = None

            try:
                if Curriculum.objects.filter(cur_id=i['id']).exists():
                    # update
                    if AllSpeciality.objects.filter(spec_id=i['specialty']['id']).exists():
                        try:
                            bspecialiy = AllSpeciality.objects.get(spec_id=i['specialty']['id'])
                            bspecialiy.spec_id = i['specialty']['id']
                            bspecialiy.save()
                        except:
                            return Response({'error': 'Yo`nalish soxalar bazada mavjud emas!'})

                    if Educationyear.objects.filter(code=i['educationYear']['code']).exists():
                        try:
                            educationyear = Educationyear.objects.get(code=i['educationYear']['code'])
                            educationyear.current = i['educationYear']['current']
                            educationyear.save()
                        except:
                            return Response({'error': 'O`quv yillar bazada mavjud emas!'})

                    if Educationtype.objects.filter(code=i['educationType']['code']).exists():
                        try:
                            educationtype = Educationtype.objects.get(code=i['educationType']['code'])
                        except:
                            return Response({'error': 'Yo`nalishlar bazada mavjud emas!'})

                    if Educationform.objects.filter(code=i['educationForm']['code']).exists():
                        try:
                            educationform = Educationform.objects.get(code=i['educationForm']['code'])
                        except:
                            return Response({'error': 'Ta`lim turlari bazada mavjud emas!'})

                    if MarkingSystem.objects.filter(code=i['markingSystem']['code']).exists():
                        try:
                            markingsystem_1 = MarkingSystem.objects.get(code=i['markingSystem']['code'])
                        except:
                            return Response({'error': 'Baholash tizimi bazada mavjud emas!'})
                    else:
                        try:
                            markingsystem_1 = MarkingSystem()
                            markingsystem_1.code = i['markingSystem']['code']
                            markingsystem_1.name = i['markingSystem']['name']
                            markingsystem_1.minimum_limit = i['markingSystem']['minimum_limit']
                            markingsystem_1.gpa_limit = i['markingSystem']['gpa_limit']
                            markingsystem_1.save()
                        except:
                            return Response({'error': 'Baholash tizimi yaratishda hatolik bor!'})

                    if Faculty.objects.filter(kod=i['department']['code']).exists():
                        try:
                            department = Faculty.objects.get(kod=i['department']['code'])
                        except:
                            return Response({'error': 'Fakultet bazada mavjud emas!'})

                    try:
                        curriculum = Curriculum.objects.get(cur_id=i['id'])
                        curriculum.name = i['name']
                        curriculum.new_specialty = bspecialiy
                        curriculum.educationyear = educationyear
                        curriculum.educationtype = educationtype
                        curriculum.educationform = educationform
                        curriculum.markingsystem = markingsystem_1
                        curriculum.department = department
                        curriculum.semester_count = i['semester_count']
                        curriculum.education_period = i['education_period']
                        curriculum.save()
                    except Exception as ex:
                        print(ex)
                        return Response({'error': 'O`quv reja yangilashda hatolik bor!2'})
                else:
                    # new
                    if AllSpeciality.objects.filter(spec_id=i['specialty']['id']).exists():
                        try:
                            bspecialiy = AllSpeciality.objects.get(spec_id=i['specialty']['id'])
                            bspecialiy.spec_id = i['specialty']['id']
                            bspecialiy.save()
                        except:
                            return Response({'error': 'Yo`nalish soxalar bazada mavjud emas!'})

                    if Educationyear.objects.filter(code=i['educationYear']['code']).exists():
                        try:
                            educationyear = Educationyear.objects.get(code=i['educationYear']['code'])
                            educationyear.current = i['educationYear']['current']
                            educationyear.save()
                        except:
                            return Response({'error': 'O`quv yillar bazada mavjud emas!'})

                    if Educationtype.objects.filter(code=i['educationType']['code']).exists():
                        try:
                            educationtype = Educationtype.objects.get(code=i['educationType']['code'])
                        except:
                            return Response({'error': 'Yo`nalishlar bazada mavjud emas!'})

                    if Educationform.objects.filter(code=i['educationForm']['code']).exists():
                        try:
                            educationform = Educationform.objects.get(code=i['educationForm']['code'])
                        except:
                            return Response({'error': 'Ta`lim turlari bazada mavjud emas!'})

                    if MarkingSystem.objects.filter(code=i['markingSystem']['code']).exists():
                        try:
                            markingsystem_2 = MarkingSystem.objects.get(code=i['markingSystem']['code'])
                        except:
                            return Response({'error': 'Baholash tizimi bazada mavjud emas!'})
                    else:
                        try:
                            markingsystem_2 = MarkingSystem()
                            markingsystem_2.code = i['markingSystem']['code']
                            markingsystem_2.name = i['markingSystem']['name']
                            markingsystem_2.minimum_limit = i['markingSystem']['minimum_limit']
                            markingsystem_2.gpa_limit = i['markingSystem']['gpa_limit']
                            markingsystem_2.save()
                        except:
                            return Response({'error': 'Baholash tizimi yaratishda hatolik bor!'})

                    if Faculty.objects.filter(kod=i['department']['code']).exists():
                        try:
                            department = Faculty.objects.get(kod=i['department']['code'])
                        except:
                            return Response({'error': 'Fakultet bazada mavjud emas!'})

                    try:
                        curriculum = Curriculum()
                        curriculum.cur_id = i['id']
                        curriculum.name = i['name']
                        curriculum.new_specialty = bspecialiy
                        curriculum.educationyear = educationyear
                        curriculum.educationtype = educationtype
                        curriculum.educationform = educationform
                        curriculum.markingsystem = markingsystem_2
                        curriculum.department = department
                        curriculum.semester_count = i['semester_count']
                        curriculum.education_period = i['education_period']
                        curriculum.save()
                    except Exception as ex:
                        print(ex)
                        return Response({'error': 'O`quv reja yangilashda hatolik bor!1'})

            except:
                return Response({'succes': 'Baza qo`shishda xatolik bor!'})

        end_time = datetime.datetime.now()
        elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time})


class GetMasofa2Curriculum(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=4)
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

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token.hemis_token_type + ' ' + token.hemis_token
        }

        params = {
            '_education_form': '22',
            'page': '1',
            'limit': '200',
        }

        respon = requests.get(baseurl + pathurl, headers=headers, params=params)
        data = respon.json()['data']['items']

        start_time = datetime.datetime.now()

        for i in data:
            bspecialiy = None
            educationyear = None
            educationtype = None
            educationform = None
            department = None
            markingsystem_1 = None
            markingsystem_2 = None

            try:
                if Curriculum.objects.filter(cur_id=i['id']).exists():
                    # update
                    if AllSpeciality.objects.filter(spec_id=i['specialty']['id']).exists():
                        try:
                            bspecialiy = AllSpeciality.objects.get(spec_id=i['specialty']['id'])
                            bspecialiy.spec_id = i['specialty']['id']
                            bspecialiy.save()
                        except:
                            return Response({'error': 'Yo`nalish soxalar bazada mavjud emas!'})

                    if Educationyear.objects.filter(code=i['educationYear']['code']).exists():
                        try:
                            educationyear = Educationyear.objects.get(code=i['educationYear']['code'])
                            educationyear.current = i['educationYear']['current']
                            educationyear.save()
                        except:
                            return Response({'error': 'O`quv yillar bazada mavjud emas!'})

                    if Educationtype.objects.filter(code=i['educationType']['code']).exists():
                        try:
                            educationtype = Educationtype.objects.get(code=i['educationType']['code'])
                        except:
                            return Response({'error': 'Yo`nalishlar bazada mavjud emas!'})

                    if Educationform.objects.filter(code=i['educationForm']['code']).exists():
                        try:
                            educationform = Educationform.objects.get(code=i['educationForm']['code'])
                        except:
                            return Response({'error': 'Ta`lim turlari bazada mavjud emas!'})

                    if MarkingSystem.objects.filter(code=i['markingSystem']['code']).exists():
                        try:
                            markingsystem_1 = MarkingSystem.objects.get(code=i['markingSystem']['code'])
                        except:
                            return Response({'error': 'Baholash tizimi bazada mavjud emas!'})
                    else:
                        try:
                            markingsystem_1 = MarkingSystem()
                            markingsystem_1.code = i['markingSystem']['code']
                            markingsystem_1.name = i['markingSystem']['name']
                            markingsystem_1.minimum_limit = i['markingSystem']['minimum_limit']
                            markingsystem_1.gpa_limit = i['markingSystem']['gpa_limit']
                            markingsystem_1.save()
                        except:
                            return Response({'error': 'Baholash tizimi yaratishda hatolik bor!'})

                    if Faculty.objects.filter(kod=i['department']['code']).exists():
                        try:
                            department = Faculty.objects.get(kod=i['department']['code'])
                        except:
                            return Response({'error': 'Fakultet bazada mavjud emas!'})

                    try:
                        curriculum = Curriculum.objects.get(cur_id=i['id'])
                        curriculum.name = i['name']
                        curriculum.new_specialty = bspecialiy
                        curriculum.educationyear = educationyear
                        curriculum.educationtype = educationtype
                        curriculum.educationform = educationform
                        curriculum.markingsystem = markingsystem_1
                        curriculum.department = department
                        curriculum.semester_count = i['semester_count']
                        curriculum.education_period = i['education_period']
                        curriculum.save()
                    except Exception as ex:
                        print(ex)
                        return Response({'error': 'O`quv reja yangilashda hatolik bor!2'})
                else:
                    # new
                    if AllSpeciality.objects.filter(spec_id=i['specialty']['id']).exists():
                        try:
                            bspecialiy = AllSpeciality.objects.get(spec_id=i['specialty']['id'])
                            bspecialiy.spec_id = i['specialty']['id']
                            bspecialiy.save()
                        except:
                            return Response({'error': 'Yo`nalish soxalar bazada mavjud emas!'})

                    if Educationyear.objects.filter(code=i['educationYear']['code']).exists():
                        try:
                            educationyear = Educationyear.objects.get(code=i['educationYear']['code'])
                            educationyear.current = i['educationYear']['current']
                            educationyear.save()
                        except:
                            return Response({'error': 'O`quv yillar bazada mavjud emas!'})

                    if Educationtype.objects.filter(code=i['educationType']['code']).exists():
                        try:
                            educationtype = Educationtype.objects.get(code=i['educationType']['code'])
                        except:
                            return Response({'error': 'Yo`nalishlar bazada mavjud emas!'})

                    if Educationform.objects.filter(code=i['educationForm']['code']).exists():
                        try:
                            educationform = Educationform.objects.get(code=i['educationForm']['code'])
                        except:
                            return Response({'error': 'Ta`lim turlari bazada mavjud emas!'})

                    if MarkingSystem.objects.filter(code=i['markingSystem']['code']).exists():
                        try:
                            markingsystem_2 = MarkingSystem.objects.get(code=i['markingSystem']['code'])
                        except:
                            return Response({'error': 'Baholash tizimi bazada mavjud emas!'})
                    else:
                        try:
                            markingsystem_2 = MarkingSystem()
                            markingsystem_2.code = i['markingSystem']['code']
                            markingsystem_2.name = i['markingSystem']['name']
                            markingsystem_2.minimum_limit = i['markingSystem']['minimum_limit']
                            markingsystem_2.gpa_limit = i['markingSystem']['gpa_limit']
                            markingsystem_2.save()
                        except:
                            return Response({'error': 'Baholash tizimi yaratishda hatolik bor!'})

                    if Faculty.objects.filter(kod=i['department']['code']).exists():
                        try:
                            department = Faculty.objects.get(kod=i['department']['code'])
                        except:
                            return Response({'error': 'Fakultet bazada mavjud emas!'})

                    try:
                        curriculum = Curriculum()
                        curriculum.cur_id = i['id']
                        curriculum.name = i['name']
                        curriculum.new_specialty = bspecialiy
                        curriculum.educationyear = educationyear
                        curriculum.educationtype = educationtype
                        curriculum.educationform = educationform
                        curriculum.markingsystem = markingsystem_2
                        curriculum.department = department
                        curriculum.semester_count = i['semester_count']
                        curriculum.education_period = i['education_period']
                        curriculum.save()
                    except Exception as ex:
                        print(ex)
                        return Response({'error': 'O`quv reja yangilashda hatolik bor!1'})

            except:
                return Response({'succes': 'Baza qo`shishda xatolik bor!'})

        end_time = datetime.datetime.now()
        elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time})


class GetKundizgiCurriculum(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin]

    # 🔹 Universal missing-object logger
    def get_or_log_missing(self, errors, item, model, lookup, label):
        try:
            return model.objects.get(**lookup)
        except model.DoesNotExist:
            errors.append({
                "curriculum_id": item.get("id"),
                "curriculum_name": item.get("name"),
                "missing_model": model.__name__,
                "lookup": lookup,
                "reason": f"{label} bazada topilmadi"
            })
            return None

    def get(self, request, format=None):
        start_time = datetime.datetime.now()

        errors = []
        success_count = 0

        # 🔹 Hemis config
        try:
            hemis = Hemis_Base.objects.get(own_uniq=4)
        except Hemis_Base.DoesNotExist:
            return Response({"error": "Hemis modulida biriktirilmagan"})

        token = HemisToken.objects.filter(
            status=True,
            hemis_user=hemis.hemis_user
        ).first()

        if not token:
            return Response({"error": "Faol token mavjud emas"})

        if hemis.openapi:
            return Response({"error": "Tokensiz murojaat qilib bo‘lmaydi"})

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{token.hemis_token_type} {token.hemis_token}"
        }

        params = {
            "_education_form": "11",
            '_education_type': '11',
            "page": "1",
            "limit": "200"
        }

        try:
            response = requests.get(
                hemis.base_url + hemis.path_url,
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()["data"]["items"]
        except Exception as ex:
            return Response({
                "error": "Hemis API dan ma'lumot olishda xato",
                "detail": str(ex)
            })

        # 🔁 MAIN LOOP
        for i in data:
            # 🔎 Bazadan qidiriladigan obyektlar
            bspecialiy = self.get_or_log_missing(
                errors,
                i,
                AllSpeciality,
                {"spec_id": i["specialty"]["id"]},
                "Speciality"
            )

            educationyear = self.get_or_log_missing(
                errors,
                i,
                Educationyear,
                {"code": i["educationYear"]["code"]},
                "EducationYear"
            )

            educationtype = self.get_or_log_missing(
                errors,
                i,
                Educationtype,
                {"code": i["educationType"]["code"]},
                "EducationType"
            )

            educationform = self.get_or_log_missing(
                errors,
                i,
                Educationform,
                {"code": i["educationForm"]["code"]},
                "EducationForm"
            )

            department = self.get_or_log_missing(
                errors,
                i,
                Faculty,
                {"kod": i["department"]["code"]},
                "Faculty"
            )

            # ❌ Agar bittasi ham topilmasa → o‘tkazib yuboramiz
            if not all([bspecialiy, educationyear, educationtype, educationform, department]):
                continue

            # 🔹 MarkingSystem (create bo‘lishi mumkin)
            try:
                markingsystem, _ = MarkingSystem.objects.get_or_create(
                    code=i["markingSystem"]["code"],
                    defaults={
                        "name": i["markingSystem"]["name"],
                        "minimum_limit": i["markingSystem"]["minimum_limit"],
                        "gpa_limit": i["markingSystem"]["gpa_limit"],
                    }
                )
            except Exception as ex:
                errors.append({
                    "curriculum_id": i["id"],
                    "curriculum_name": i["name"],
                    "missing_model": "MarkingSystem",
                    "lookup": {"code": i["markingSystem"]["code"]},
                    "exception": str(ex)
                })
                continue

            # 🔹 Curriculum save
            try:
                Curriculum.objects.update_or_create(
                    cur_id=i["id"],
                    defaults={
                        "name": i["name"],
                        "new_specialty": bspecialiy,
                        "educationyear": educationyear,
                        "educationtype": educationtype,
                        "educationform": educationform,
                        "markingsystem": markingsystem,
                        "department": department,
                        "semester_count": i["semester_count"],
                        "education_period": i["education_period"],
                    }
                )
                success_count += 1
            except Exception as ex:
                errors.append({
                    "curriculum_id": i["id"],
                    "curriculum_name": i["name"],
                    "reason": "Curriculum saqlashda xato",
                    "exception": str(ex)
                })
                continue

        end_time = datetime.datetime.now()

        return Response({
            "success": True,
            "total_from_hemis": len(data),
            "saved": success_count,
            "skipped": len(errors),
            "errors": errors,
            "time": str(end_time - start_time)
        })


class GetQoshmaCurriculum(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=4)
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

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token.hemis_token_type + ' ' + token.hemis_token
        }

        params = {
            '_education_form': '23',
            'page': '1',
            'limit': '200',
        }

        respon = requests.get(baseurl + pathurl, headers=headers, params=params)
        data = respon.json()['data']['items']

        start_time = datetime.datetime.now()

        for i in data:
            bspecialiy = None
            educationyear = None
            educationtype = None
            educationform = None
            department = None
            markingsystem_1 = None
            markingsystem_2 = None

            try:
                if Curriculum.objects.filter(cur_id=i['id']).exists():
                    # update
                    if AllSpeciality.objects.filter(spec_id=i['specialty']['id']).exists():
                        try:
                            bspecialiy = AllSpeciality.objects.get(spec_id=i['specialty']['id'])
                            bspecialiy.spec_id = i['specialty']['id']
                            bspecialiy.save()
                        except:
                            return Response({'error': 'Yo`nalish soxalar bazada mavjud emas!'})

                    if Educationyear.objects.filter(code=i['educationYear']['code']).exists():
                        try:
                            educationyear = Educationyear.objects.get(code=i['educationYear']['code'])
                            educationyear.current = i['educationYear']['current']
                            educationyear.save()
                        except:
                            return Response({'error': 'O`quv yillar bazada mavjud emas!'})

                    if Educationtype.objects.filter(code=i['educationType']['code']).exists():
                        try:
                            educationtype = Educationtype.objects.get(code=i['educationType']['code'])
                        except:
                            return Response({'error': 'Yo`nalishlar bazada mavjud emas!'})

                    if Educationform.objects.filter(code=i['educationForm']['code']).exists():
                        try:
                            educationform = Educationform.objects.get(code=i['educationForm']['code'])
                        except:
                            return Response({'error': 'Ta`lim turlari bazada mavjud emas!'})

                    if MarkingSystem.objects.filter(code=i['markingSystem']['code']).exists():
                        try:
                            markingsystem_1 = MarkingSystem.objects.get(code=i['markingSystem']['code'])
                        except:
                            return Response({'error': 'Baholash tizimi bazada mavjud emas!'})
                    else:
                        try:
                            markingsystem_1 = MarkingSystem()
                            markingsystem_1.code = i['markingSystem']['code']
                            markingsystem_1.name = i['markingSystem']['name']
                            markingsystem_1.minimum_limit = i['markingSystem']['minimum_limit']
                            markingsystem_1.gpa_limit = i['markingSystem']['gpa_limit']
                            markingsystem_1.save()
                        except:
                            return Response({'error': 'Baholash tizimi yaratishda hatolik bor!'})

                    if Faculty.objects.filter(kod=i['department']['code']).exists():
                        try:
                            department = Faculty.objects.get(kod=i['department']['code'])
                        except:
                            return Response({'error': 'Fakultet bazada mavjud emas!'})

                    try:
                        curriculum = Curriculum.objects.get(cur_id=i['id'])
                        curriculum.name = i['name']
                        curriculum.new_specialty = bspecialiy
                        curriculum.educationyear = educationyear
                        curriculum.educationtype = educationtype
                        curriculum.educationform = educationform
                        curriculum.markingsystem = markingsystem_1
                        curriculum.department = department
                        curriculum.semester_count = i['semester_count']
                        curriculum.education_period = i['education_period']
                        curriculum.save()
                    except Exception as ex:
                        print(ex)
                        return Response({'error': 'O`quv reja yangilashda hatolik bor!2'})
                else:
                    # new
                    if AllSpeciality.objects.filter(spec_id=i['specialty']['id']).exists():
                        try:
                            bspecialiy = AllSpeciality.objects.get(spec_id=i['specialty']['id'])
                            bspecialiy.spec_id = i['specialty']['id']
                            bspecialiy.save()
                        except:
                            return Response({'error': 'Yo`nalish soxalar bazada mavjud emas!'})

                    if Educationyear.objects.filter(code=i['educationYear']['code']).exists():
                        try:
                            educationyear = Educationyear.objects.get(code=i['educationYear']['code'])
                            educationyear.current = i['educationYear']['current']
                            educationyear.save()
                        except:
                            return Response({'error': 'O`quv yillar bazada mavjud emas!'})

                    if Educationtype.objects.filter(code=i['educationType']['code']).exists():
                        try:
                            educationtype = Educationtype.objects.get(code=i['educationType']['code'])
                        except:
                            return Response({'error': 'Yo`nalishlar bazada mavjud emas!'})

                    if Educationform.objects.filter(code=i['educationForm']['code']).exists():
                        try:
                            educationform = Educationform.objects.get(code=i['educationForm']['code'])
                        except:
                            return Response({'error': 'Ta`lim turlari bazada mavjud emas!'})

                    if MarkingSystem.objects.filter(code=i['markingSystem']['code']).exists():
                        try:
                            markingsystem_2 = MarkingSystem.objects.get(code=i['markingSystem']['code'])
                        except:
                            return Response({'error': 'Baholash tizimi bazada mavjud emas!'})
                    else:
                        try:
                            markingsystem_2 = MarkingSystem()
                            markingsystem_2.code = i['markingSystem']['code']
                            markingsystem_2.name = i['markingSystem']['name']
                            markingsystem_2.minimum_limit = i['markingSystem']['minimum_limit']
                            markingsystem_2.gpa_limit = i['markingSystem']['gpa_limit']
                            markingsystem_2.save()
                        except:
                            return Response({'error': 'Baholash tizimi yaratishda hatolik bor!'})

                    if Faculty.objects.filter(kod=i['department']['code']).exists():
                        try:
                            department = Faculty.objects.get(kod=i['department']['code'])
                        except:
                            return Response({'error': 'Fakultet bazada mavjud emas!'})

                    try:
                        curriculum = Curriculum()
                        curriculum.cur_id = i['id']
                        curriculum.name = i['name']
                        curriculum.new_specialty = bspecialiy
                        curriculum.educationyear = educationyear
                        curriculum.educationtype = educationtype
                        curriculum.educationform = educationform
                        curriculum.markingsystem = markingsystem_2
                        curriculum.department = department
                        curriculum.semester_count = i['semester_count']
                        curriculum.education_period = i['education_period']
                        curriculum.save()
                    except Exception as ex:
                        print(ex)
                        return Response({'error': 'O`quv reja yangilashda hatolik bor!1'})

            except:
                return Response({'succes': 'Baza qo`shishda xatolik bor!'})

        end_time = datetime.datetime.now()
        elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time})


class GetAllINCurriculum(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=4)
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

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token.hemis_token_type + ' ' + token.hemis_token
        }

        params = {
            'page': '1',
            'limit': '200',
        }
        respon = requests.get(baseurl + pathurl, headers=headers, params=params)
        data = respon.json()
        page = data['data']['pagination']['page']
        pagecount = data['data']['pagination']['pageCount'] + 1
        for j in range(int(page), int(pagecount), 1):
            params = {
                'page': str(j),
                'limit': '200',
            }
            prespon = requests.get(baseurl + pathurl, headers=headers, params=params)
            data = prespon.json()['data']['items']

            start_time = datetime.datetime.now()

            for i in data:
                bspecialiy = None
                educationyear = None
                educationtype = None
                educationform = None
                department = None
                markingsystem_1 = None
                markingsystem_2 = None

                try:
                    if Curriculum.objects.filter(cur_id=i['id']).exists():
                        # update
                        if AllSpeciality.objects.filter(spec_id=i['specialty']['id']).exists():
                            try:
                                bspecialiy = AllSpeciality.objects.get(spec_id=i['specialty']['id'])
                                bspecialiy.spec_id = i['specialty']['id']
                                bspecialiy.save()
                            except:
                                return Response({'error': 'Yo`nalish soxalar bazada mavjud emas!'})

                        if Educationyear.objects.filter(code=i['educationYear']['code']).exists():
                            try:
                                educationyear = Educationyear.objects.get(code=i['educationYear']['code'])
                                educationyear.current = i['educationYear']['current']
                                educationyear.save()
                            except:
                                return Response({'error': 'O`quv yillar bazada mavjud emas!'})

                        if Educationtype.objects.filter(code=i['educationType']['code']).exists():
                            try:
                                educationtype = Educationtype.objects.get(code=i['educationType']['code'])
                            except:
                                return Response({'error': 'Yo`nalishlar bazada mavjud emas!'})

                        if Educationform.objects.filter(code=i['educationForm']['code']).exists():
                            try:
                                educationform = Educationform.objects.get(code=i['educationForm']['code'])
                            except:
                                return Response({'error': 'Ta`lim turlari bazada mavjud emas!'})

                        if MarkingSystem.objects.filter(code=i['markingSystem']['code']).exists():
                            try:
                                markingsystem_1 = MarkingSystem.objects.get(code=i['markingSystem']['code'])
                            except:
                                return Response({'error': 'Baholash tizimi bazada mavjud emas!'})
                        else:
                            try:
                                markingsystem_1 = MarkingSystem()
                                markingsystem_1.code = i['markingSystem']['code']
                                markingsystem_1.name = i['markingSystem']['name']
                                markingsystem_1.minimum_limit = i['markingSystem']['minimum_limit']
                                markingsystem_1.gpa_limit = i['markingSystem']['gpa_limit']
                                markingsystem_1.save()
                            except:
                                return Response({'error': 'Baholash tizimi yaratishda hatolik bor!'})

                        if Faculty.objects.filter(kod=i['department']['code']).exists():
                            try:
                                department = Faculty.objects.get(kod=i['department']['code'])
                            except:
                                return Response({'error': 'Fakultet bazada mavjud emas!'})

                        try:
                            curriculum = Curriculum.objects.get(cur_id=i['id'])
                            curriculum.name = i['name']
                            curriculum.new_specialty = bspecialiy
                            curriculum.educationyear = educationyear
                            curriculum.educationtype = educationtype
                            curriculum.educationform = educationform
                            curriculum.markingsystem = markingsystem_1
                            curriculum.department = department
                            curriculum.semester_count = i['semester_count']
                            curriculum.education_period = i['education_period']
                            curriculum.save()
                        except Exception as ex:

                            return Response({'error': 'O`quv reja yangilashda hatolik bor!2'})
                    else:
                        # new

                        if AllSpeciality.objects.filter(spec_id=i['specialty']['id']).exists():
                            try:
                                bspecialiy = AllSpeciality.objects.get(spec_id=i['specialty']['id'])
                                bspecialiy.spec_id = i['specialty']['id']
                                bspecialiy.save()
                            except:
                                return Response({'error': 'Yo`nalish soxalar bazada mavjud emas!'})

                        if Educationyear.objects.filter(code=i['educationYear']['code']).exists():
                            try:
                                educationyear = Educationyear.objects.get(code=i['educationYear']['code'])
                                educationyear.current = i['educationYear']['current']
                                educationyear.save()
                            except:
                                return Response({'error': 'O`quv yillar bazada mavjud emas!'})

                        if Educationtype.objects.filter(code=i['educationType']['code']).exists():
                            try:
                                educationtype = Educationtype.objects.get(code=i['educationType']['code'])
                            except:
                                return Response({'error': 'Yo`nalishlar bazada mavjud emas!'})

                        if Educationform.objects.filter(code=i['educationForm']['code']).exists():
                            try:
                                educationform = Educationform.objects.get(code=i['educationForm']['code'])
                            except:
                                return Response({'error': 'Ta`lim turlari bazada mavjud emas!'})

                        if MarkingSystem.objects.filter(code=i['markingSystem']['code']).exists():
                            try:
                                markingsystem_2 = MarkingSystem.objects.get(code=i['markingSystem']['code'])
                            except:
                                return Response({'error': 'Baholash tizimi bazada mavjud emas!'})
                        else:
                            try:
                                markingsystem_2 = MarkingSystem()
                                markingsystem_2.code = i['markingSystem']['code']
                                markingsystem_2.name = i['markingSystem']['name']
                                markingsystem_2.minimum_limit = i['markingSystem']['minimum_limit']
                                markingsystem_2.gpa_limit = i['markingSystem']['gpa_limit']
                                markingsystem_2.save()
                            except:
                                return Response({'error': 'Baholash tizimi yaratishda hatolik bor!'})

                        if Faculty.objects.filter(kod=i['department']['code']).exists():
                            try:
                                department = Faculty.objects.get(kod=i['department']['code'])
                            except:
                                return Response({'error': 'Fakultet bazada mavjud emas!'})

                        try:
                            curriculum = Curriculum()
                            curriculum.cur_id = i['id']
                            curriculum.name = i['name']
                            curriculum.new_specialty = bspecialiy
                            curriculum.educationyear = educationyear
                            curriculum.educationtype = educationtype
                            curriculum.educationform = educationform
                            curriculum.markingsystem = markingsystem_2
                            curriculum.department = department
                            curriculum.semester_count = i['semester_count']
                            curriculum.education_period = i['education_period']
                            curriculum.save()
                        except Exception as ex:

                            return Response({'error': 'O`quv reja yangilashda hatolik bor!1'})

                except:
                    return Response({'succes': 'Baza qo`shishda xatolik bor!'})

            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time})


class GetCurriculum_active(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

    async def fetch_page(self, session, url, headers, page, limit):
        """Bitta sahifani asinxron yuklab olish"""
        params = {'page': page, 'limit': limit}
        async with session.get(url, headers=headers, ssl=False, params=params) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            return data.get('data', {}).get('items', [])

    async def fetch_all_pages(self, base_url, headers, limit=200):
        """Barcha sahifalarni parallel tarzda yuklab olish"""
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=90)) as session:
            # 1-sahifadan umumiy sahifalar sonini olish
            async with session.get(base_url, headers=headers, ssl=False,
                                   params={'page': 1, 'limit': limit}) as first_resp:
                if first_resp.status != 200:
                    return []
                data = await first_resp.json()
                items = data.get('data', {}).get('items', [])
                page_count = data.get('data', {}).get('pagination', {}).get('pageCount', 1)

            if page_count <= 1:
                return items

            # Qolgan sahifalarni parallel yuklab olish
            tasks = [
                self.fetch_page(session, base_url, headers, page, limit)
                for page in range(2, page_count + 1)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for r in results:
                if isinstance(r, list):
                    items.extend(r)
            return items

    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=4)
            hemis_2 = Hemis_Base.objects.get(own_uniq=6)
        except Hemis_Base.DoesNotExist:
            return Response({'error': 'Hemis moduli topilmadi'}, status=status.HTTP_400_BAD_REQUEST)

        token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
        if not token:
            return Response({'error': 'Faol token topilmadi'}, status=status.HTTP_400_BAD_REQUEST)

        headers = {
            'Authorization': f"{token.hemis_token_type} {token.hemis_token}",
            'Content-Type': 'application/json'
        }

        base_url = hemis.base_url + hemis.path_url
        semester_url = hemis_2.base_url + hemis_2.path_url

        start_time = datetime.datetime.now()

        # 🔄 Asinxron tarzda barcha sahifalarni olish
        all_items = asyncio.run(self.fetch_all_pages(base_url, headers))
        if not all_items:
            return Response({'info': 'O‘quv rejalar topilmadi'})

        created, updated, skipped, errors = 0, 0, 0, 0
        error_logs = []
        semaphore = asyncio.Semaphore(10)  # ⏱️ 1 sekundda 10 tadan ortiq so‘rov yubormaslik uchun

        async def check_semester(curriculum_id):
            """Aktiv semestr bor-yo‘qligini tekshiruvchi yordamchi funksiya"""
            async with semaphore:
                async with aiohttp.ClientSession() as session:
                    async with session.get(semester_url, headers=headers, ssl=False,
                                           params={'_curriculum': curriculum_id}) as resp:
                        if resp.status != 200:
                            return False
                        data = await resp.json()
                        items = data.get('data', {}).get('items', [])
                        return any(s.get('current') for s in items)

        async def process_items():
            nonlocal created, updated, skipped, errors

            tasks = [check_semester(i['id']) for i in all_items]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, has_active_sem in zip(all_items, results):
                try:
                    if isinstance(has_active_sem, Exception):
                        raise has_active_sem

                    if not has_active_sem:
                        skipped += 1
                        continue

                    edu_year = i.get('educationYear', {})

                    educationyear, _ = await sync_to_async(Educationyear.objects.update_or_create)(
                        code=edu_year['code'],
                        defaults={
                            'name': edu_year['name'],
                            'current': edu_year.get('current', False)
                        }
                    )

                    bspecialiy = await sync_to_async(AllSpeciality.objects.filter)(
                        spec_id=i['specialty']['id']
                    )
                    bspecialiy = await sync_to_async(bspecialiy.first)()

                    educationtype = await sync_to_async(Educationtype.objects.filter)(
                        code=i['educationType']['code']
                    )
                    educationtype = await sync_to_async(educationtype.first)()

                    educationform = await sync_to_async(Educationform.objects.filter)(
                        code=i['educationForm']['code']
                    )
                    educationform = await sync_to_async(educationform.first)()

                    markingsystem, _ = await sync_to_async(MarkingSystem.objects.update_or_create)(
                        code=i['markingSystem']['code'],
                        defaults={
                            'name': i['markingSystem']['name'],
                            'minimum_limit': i['markingSystem']['minimum_limit'],
                            'gpa_limit': i['markingSystem']['gpa_limit']
                        }
                    )

                    obj, created_flag = await sync_to_async(Curriculum.objects.update_or_create)(
                        cur_id=i['id'],
                        defaults={
                            'name': i['name'],
                            'new_specialty': bspecialiy,
                            'educationyear': educationyear,
                            'educationtype': educationtype,
                            'educationform': educationform,
                            'markingsystem': markingsystem,
                            'semester_count': i['semester_count'],
                            'education_period': i['education_period']
                        }
                    )

                    if created_flag:
                        created += 1
                    else:
                        updated += 1

                except Exception as e:
                    errors += 1
                    error_logs.append({
                        "curriculum_id": i.get('id'),
                        "error": str(e),
                        "trace": traceback.format_exc().splitlines()[-1]
                    })
                    continue

        asyncio.run(process_items())

        elapsed_time = datetime.datetime.now() - start_time

        return Response({
            'success': True,
            'created': created,
            'updated': updated,
            'skipped': skipped,
            'errors': errors,
            'elapsed_time': str(elapsed_time),
            'error_samples': error_logs[:5]  # faqat 5 ta xatolikni ko‘rsatadi
        })


class GetCurriculum_activeSkipe(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin]

    # ================== SKIP LOGGER ==================
    def skip(self, skipped_logs, item, reason, extra=None):
        log = {
            "curriculum_id": item.get("id"),
            "curriculum_name": item.get("name"),
            "reason": reason,
        }
        if extra:
            log.update(extra)
        skipped_logs.append(log)

    # ================== PAGINATION ==================
    async def fetch_page(self, session, url, headers, page, limit):
        async with session.get(
                url,
                headers=headers,
                ssl=False,
                params={"page": page, "limit": limit}
        ) as resp:
            if resp.status != 200:
                return [], 0

            data = await resp.json()
            return (
                data.get("data", {}).get("items", []),
                data.get("data", {}).get("pagination", {}).get("pageCount", 1),
            )

    async def fetch_all_pages(self, base_url, headers, limit=200):
        async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=120)
        ) as session:
            items, page_count = await self.fetch_page(
                session, base_url, headers, 1, limit
            )

            tasks = [
                self.fetch_page(session, base_url, headers, p, limit)
                for p in range(2, page_count + 1)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for r in results:
                if isinstance(r, tuple):
                    items.extend(r[0])

            return items

    # ================== SEMESTER CHECK ==================
    async def check_semester(self, session, semester_url, headers, curriculum_id):
        async with session.get(
                semester_url,
                headers=headers,
                ssl=False,
                params={"_curriculum": curriculum_id},
        ) as resp:
            if resp.status != 200:
                return False, "Semestr API status != 200"

            data = await resp.json()
            items = data.get("data", {}).get("items", [])

            if not items:
                return False, "Semestrlar bo‘sh"

            if not any(s.get("current") for s in items):
                return False, "Semestrlar bor, lekin aktiv yo‘q"

            return True, None

    # ================== MAIN ==================
    def get(self, request, format=None):
        start_time = datetime.datetime.now()

        hemis = Hemis_Base.objects.get(own_uniq=4)
        hemis_2 = Hemis_Base.objects.get(own_uniq=6)

        token = HemisToken.objects.filter(
            status=True, hemis_user=hemis.hemis_user
        ).first()

        headers = {
            "Authorization": f"{token.hemis_token_type} {token.hemis_token}",
            "Content-Type": "application/json",
        }

        curriculum_url = hemis.base_url + hemis.path_url
        semester_url = hemis_2.base_url + hemis_2.path_url

        all_items = asyncio.run(
            self.fetch_all_pages(curriculum_url, headers)
        )

        created = updated = skipped = 0
        skipped_logs = []

        RETRY_LIMIT = 3

        async def process():
            nonlocal created, updated, skipped

            async with aiohttp.ClientSession() as session:
                for i in all_items:
                    retry_count = 0

                    while retry_count < RETRY_LIMIT:
                        ok, reason = await self.check_semester(
                            session, semester_url, headers, i["id"]
                        )

                        if ok:
                            break

                        if reason != "Semestr API status != 200":
                            break

                        retry_count += 1
                        await asyncio.sleep(0.3)  # ⏱ interval

                    # ❌ baribir bo‘lmadi
                    if not ok:
                        skipped += 1
                        self.skip(
                            skipped_logs,
                            i,
                            f"{reason} (retry {retry_count})"
                        )
                        continue

                    # -------- DB CHECKS (qisqartirilgan) --------
                    bspecialiy = await sync_to_async(
                        AllSpeciality.objects.filter(
                            spec_id=i["specialty"]["id"]
                        ).first
                    )()
                    if not bspecialiy:
                        skipped += 1
                        self.skip(skipped_logs, i, "Speciality yo‘q")
                        continue

                    educationtype = await sync_to_async(
                        Educationtype.objects.filter(
                            code=i["educationType"]["code"]
                        ).first
                    )()
                    educationform = await sync_to_async(
                        Educationform.objects.filter(
                            code=i["educationForm"]["code"]
                        ).first
                    )()

                    edu_year = i["educationYear"]
                    educationyear, _ = await sync_to_async(
                        Educationyear.objects.update_or_create
                    )(
                        code=edu_year["code"],
                        defaults={"name": edu_year["name"], "current": edu_year.get("current", False)}
                    )

                    markingsystem, _ = await sync_to_async(
                        MarkingSystem.objects.update_or_create
                    )(
                        code=i["markingSystem"]["code"],
                        defaults={
                            "name": i["markingSystem"]["name"],
                            "minimum_limit": i["markingSystem"]["minimum_limit"],
                            "gpa_limit": i["markingSystem"]["gpa_limit"],
                        },
                    )

                    _, created_flag = await sync_to_async(
                        Curriculum.objects.update_or_create
                    )(
                        cur_id=i["id"],
                        defaults={
                            "name": i["name"],
                            "new_specialty": bspecialiy,
                            "educationyear": educationyear,
                            "educationtype": educationtype,
                            "educationform": educationform,
                            "markingsystem": markingsystem,
                            "semester_count": i["semester_count"],
                            "education_period": i["education_period"],
                        },
                    )

                    if created_flag:
                        created += 1
                    else:
                        updated += 1

        asyncio.run(process())

        elapsed = datetime.datetime.now() - start_time
        summary = Counter([s["reason"] for s in skipped_logs])

        return Response({
            "success": True,
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "elapsed_time": str(elapsed),
            "skipped_summary": summary,
            "skipped_samples": skipped_logs[:10],
        })


class GetCurriculum_activetoday(APIView):
    # permission_classes = [AllowOnlyTrustedOrigins, IsAdmin]

    async def fetch_page(self, session, url, headers, page, limit):
        """Bitta sahifani asinxron yuklab olish"""
        params = {'page': page, 'limit': limit}
        async with session.get(url, headers=headers, ssl=False, params=params) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            return data.get('data', {}).get('items', [])

    async def fetch_all_pages(self, base_url, headers, limit=200):
        """Barcha sahifalarni parallel tarzda yuklab olish"""
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=90)) as session:
            async with session.get(base_url, headers=headers, ssl=False,
                                   params={'page': 1, 'limit': limit}) as first_resp:

                if first_resp.status != 200:
                    return []

                data = await first_resp.json()

                items = data.get('data', {}).get('items', [])
                page_count = data.get('data', {}).get('pagination', {}).get('pageCount', 1)

            if page_count <= 1:
                return items

            tasks = [
                self.fetch_page(session, base_url, headers, page, limit)
                for page in range(2, page_count + 1)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for r in results:
                if isinstance(r, list):
                    items.extend(r)

            return items

    def get(self, request, format=None):

        try:
            hemis = Hemis_Base.objects.get(own_uniq=4)
            hemis_2 = Hemis_Base.objects.get(own_uniq=6)
        except Hemis_Base.DoesNotExist:
            return Response({'error': 'Hemis moduli topilmadi'}, status=status.HTTP_400_BAD_REQUEST)

        token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
        if not token:
            return Response({'error': 'Faol token topilmadi'}, status=status.HTTP_400_BAD_REQUEST)

        headers = {
            'Authorization': f"{token.hemis_token_type} {token.hemis_token}",
            'Content-Type': 'application/json'
        }

        base_url = hemis.base_url + hemis.path_url
        semester_url = hemis_2.base_url + hemis_2.path_url

        start_time = datetime.datetime.now()

        # 🔄 Barcha o‘quv rejalarni olish
        all_items = asyncio.run(self.fetch_all_pages(base_url, headers))
        if not all_items:
            return Response({'info': 'O‘quv rejalar topilmadi'})

        created, updated, skipped, errors = 0, 0, 0, 0
        error_logs = []

        # Hozirgi yil
        current_year = str(datetime.datetime.now().year)

        semaphore = asyncio.Semaphore(10)

        async def check_semester(curriculum_id):
            """
            Tekshiradi:
            1) _education_year == hozirgi yil
            2) current == True bo‘lgan semestr bor yoki yo‘qligini
            """
            async with semaphore:
                async with aiohttp.ClientSession() as session:
                    async with session.get(semester_url, headers=headers, ssl=False,
                                           params={'_curriculum': curriculum_id}) as resp:
                        if resp.status != 200:
                            return False

                        data = await resp.json()
                        items = data.get('data', {}).get('items', [])

                        # 2 ta shartni tekshiramiz
                        return any(
                            s.get('current') is True and s.get('_education_year') == current_year
                            for s in items
                        )

        async def process_items():
            nonlocal created, updated, skipped, errors

            # Barcha curriculumlarni parallel tekshirish
            tasks = [check_semester(i['id']) for i in all_items]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, has_active_sem in zip(all_items, results):
                try:
                    if isinstance(has_active_sem, Exception):
                        raise has_active_sem

                    # ❌ Agar active semestr bo‘lmasa — skip
                    if not has_active_sem:
                        skipped += 1
                        continue

                    # 🔽 Normallashtirish: educationYear
                    edu_year = i.get('educationYear', {})

                    educationyear, _ = await sync_to_async(Educationyear.objects.update_or_create)(
                        code=edu_year['code'],
                        defaults={
                            'name': edu_year['name'],
                            'current': edu_year.get('current', False)
                        }
                    )

                    bspecialiy = await sync_to_async(AllSpeciality.objects.filter)(
                        spec_id=i['specialty']['id']
                    )
                    bspecialiy = await sync_to_async(bspecialiy.first)()

                    educationtype = await sync_to_async(Educationtype.objects.filter)(
                        code=i['educationType']['code']
                    )
                    educationtype = await sync_to_async(educationtype.first)()

                    educationform = await sync_to_async(Educationform.objects.filter)(
                        code=i['educationForm']['code']
                    )
                    educationform = await sync_to_async(educationform.first)()

                    markingsystem, _ = await sync_to_async(MarkingSystem.objects.update_or_create)(
                        code=i['markingSystem']['code'],
                        defaults={
                            'name': i['markingSystem']['name'],
                            'minimum_limit': i['markingSystem']['minimum_limit'],
                            'gpa_limit': i['markingSystem']['gpa_limit']
                        }
                    )

                    # 🔥 Curriculum saqlash
                    obj, created_flag = await sync_to_async(Curriculum.objects.update_or_create)(
                        cur_id=i['id'],
                        defaults={
                            'name': i['name'],
                            'new_specialty': bspecialiy,
                            'educationyear': educationyear,
                            'educationtype': educationtype,
                            'educationform': educationform,
                            'markingsystem': markingsystem,
                            'semester_count': i['semester_count'],
                            'education_period': i['education_period']
                        }
                    )

                    if created_flag:
                        created += 1
                    else:
                        updated += 1

                except Exception as e:
                    errors += 1
                    error_logs.append({
                        "curriculum_id": i.get('id'),
                        "error": str(e),
                        "trace": traceback.format_exc().splitlines()[-1]
                    })
                    continue

        asyncio.run(process_items())

        elapsed_time = datetime.datetime.now() - start_time

        return Response({
            'success': True,
            'created': created,
            'updated': updated,
            'skipped': skipped,
            'errors': errors,
            'elapsed_time': str(elapsed_time),
            'error_samples': error_logs[:5]
        })
