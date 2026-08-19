from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

from config.permissions import AllowOnlyTrustedOrigins
from hemis.models import Hemis_sub, Hemis_Base, HemisToken
from shared.permissions import IsAdmin

from .models import Group
from learning_process.models import Curriculum, Educationlang
from universty.models import Faculty
from speciality.models import Bspeciality,AllSpeciality
import datetime


class GetGroup(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=7)
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
                #print(data)
                pagecount = data['data']['pagination']['pageCount'] + 1
                for i in range(int(page), int(pagecount), 1):
                    params = {
                        'page': str(i),
                        'limit': '100',
                        '_curriculum': j.cur_id
                    }
                    prespon = requests.get(baseurl + pathurl, headers=headers, params=params)
                    rdata = prespon.json()['data']['items']

                    for gi in rdata:
                        check = Group.objects.filter(h_id=gi['id']).exists()
                        if check:
                            group = Group.objects.get(h_id=gi['id'])
                            faculty = Faculty.objects.filter(hemisid=gi['department']['id']).exists()
                            if not faculty:
                                #print('1')
                                return Response({'error': 'Hemis modulida bo`lim birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                            faculty = Faculty.objects.get(hemisid=gi['department']['id'])
                            specialty = AllSpeciality.objects.filter(spec_id=gi['specialty']['id']).exists()
                            if not specialty:
                                #print('2')
                                return Response({'error': 'Hemis modulida yonalish birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                            specialty = AllSpeciality.objects.get(spec_id=gi['specialty']['id'])
                            educationLang = Educationlang.objects.filter(code=gi['educationLang']['code']).exists()
                            if not educationLang:
                                #print('3')
                                return Response({'error': 'Hemis modulida oquv tili birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                            educationLang = Educationlang.objects.get(code=gi['educationLang']['code'])
                            group.group_curriculum = j
                            group.name = gi['name']
                            group.educationLang = educationLang
                            group.new_specialty = specialty
                            group.faculty = faculty
                            group.save()
                        else:
                            faculty = Faculty.objects.filter(hemisid=gi['department']['id']).exists()
                            if not faculty:
                                #print('01')
                                return Response({'error': 'Hemis modulida bo`lim birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                            faculty = Faculty.objects.get(hemisid=gi['department']['id'])

                            specialty = AllSpeciality.objects.filter(spec_id=gi['specialty']['id']).exists()
                            if not specialty:
                                #print('02')
                                return Response({'error': 'Hemis modulida yonalish birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                            specialty = AllSpeciality.objects.get(spec_id=gi['specialty']['id'])

                            educationLang = Educationlang.objects.filter(code=gi['educationLang']['code']).exists()
                            if not educationLang:
                                #print('03')
                                return Response({'error': 'Hemis modulida oquv tili birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                            educationLang = Educationlang.objects.get(code=gi['educationLang']['code'])
                            new_group = Group()
                            new_group.name = gi['name']
                            new_group.h_id = gi['id']
                            new_group.educationLang = educationLang
                            new_group.new_specialty = specialty
                            new_group.faculty = faculty
                            new_group.group_curriculum = j
                            new_group.save()

            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time},status=status.HTTP_200_OK)

class GetReGroup(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=7)
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
            curricm = Curriculum.objects.filter(educationform__code__in=[16,23,22])
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
                #print(data)
                pagecount = data['data']['pagination']['pageCount'] + 1
                for i in range(int(page), int(pagecount), 1):
                    params = {
                        'page': str(i),
                        'limit': '100',
                        '_curriculum': j.cur_id
                    }
                    prespon = requests.get(baseurl + pathurl, headers=headers, params=params)
                    rdata = prespon.json()['data']['items']

                    for gi in rdata:
                        check = Group.objects.filter(h_id=gi['id']).exists()
                        if check:
                            group = Group.objects.get(h_id=gi['id'])
                            faculty = Faculty.objects.filter(hemisid=gi['department']['id']).exists()
                            if not faculty:
                                #print('1')
                                return Response({'error': 'Hemis modulida bo`lim birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                            faculty = Faculty.objects.get(hemisid=gi['department']['id'])
                            specialty = AllSpeciality.objects.filter(spec_id=gi['specialty']['id']).exists()
                            if not specialty:
                                #print('2')
                                return Response({'error': 'Hemis modulida yonalish birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                            specialty = AllSpeciality.objects.get(spec_id=gi['specialty']['id'])
                            educationLang = Educationlang.objects.filter(code=gi['educationLang']['code']).exists()
                            if not educationLang:
                                #print('3')
                                return Response({'error': 'Hemis modulida oquv tili birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                            educationLang = Educationlang.objects.get(code=gi['educationLang']['code'])
                            group.group_curriculum = j
                            group.name = gi['name']
                            group.educationLang = educationLang
                            group.new_specialty = specialty
                            group.faculty = faculty
                            group.save()
                        else:
                            faculty = Faculty.objects.filter(hemisid=gi['department']['id']).exists()
                            if not faculty:
                                #print('01')
                                return Response({'error': 'Hemis modulida bo`lim birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                            faculty = Faculty.objects.get(hemisid=gi['department']['id'])

                            specialty = AllSpeciality.objects.filter(spec_id=gi['specialty']['id']).exists()
                            if not specialty:
                                #print('02')
                                return Response({'error': 'Hemis modulida yonalish birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                            specialty = AllSpeciality.objects.get(spec_id=gi['specialty']['id'])

                            educationLang = Educationlang.objects.filter(code=gi['educationLang']['code']).exists()
                            if not educationLang:
                                #print('03')
                                return Response({'error': 'Hemis modulida oquv tili birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                            educationLang = Educationlang.objects.get(code=gi['educationLang']['code'])
                            new_group = Group()
                            new_group.name = gi['name']
                            new_group.h_id = gi['id']
                            new_group.educationLang = educationLang
                            new_group.new_specialty = specialty
                            new_group.faculty = faculty
                            new_group.group_curriculum = j
                            new_group.save()

            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time},status=status.HTTP_200_OK)

class GetALLGroup(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=7)
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
            curricm = Curriculum.objects.filter(educationform__code__in=[11])
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
                #print(data)
                pagecount = data['data']['pagination']['pageCount'] + 1
                for i in range(int(page), int(pagecount), 1):
                    params = {
                        'page': str(i),
                        'limit': '100',
                        '_curriculum': j.cur_id
                    }
                    prespon = requests.get(baseurl + pathurl, headers=headers, params=params)
                    rdata = prespon.json()['data']['items']

                    for gi in rdata:
                        check = Group.objects.filter(h_id=gi['id']).exists()
                        if check:
                            group = Group.objects.get(h_id=gi['id'])
                            faculty = Faculty.objects.filter(hemisid=gi['department']['id']).exists()
                            if not faculty:
                                #print('1')
                                return Response({'error': 'Hemis modulida bo`lim birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                            faculty = Faculty.objects.get(hemisid=gi['department']['id'])
                            specialty = AllSpeciality.objects.filter(spec_id=gi['specialty']['id']).exists()
                            if not specialty:
                                #print('2')
                                return Response({'error': 'Hemis modulida yonalish birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                            specialty = AllSpeciality.objects.get(spec_id=gi['specialty']['id'])
                            educationLang = Educationlang.objects.filter(code=gi['educationLang']['code']).exists()
                            if not educationLang:
                                #print('3')
                                return Response({'error': 'Hemis modulida oquv tili birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                            educationLang = Educationlang.objects.get(code=gi['educationLang']['code'])
                            group.group_curriculum = j
                            group.name = gi['name']
                            group.educationLang = educationLang
                            group.new_specialty = specialty
                            group.faculty = faculty
                            group.save()
                        else:
                            faculty = Faculty.objects.filter(hemisid=gi['department']['id']).exists()
                            if not faculty:
                                #print('01')
                                return Response({'error': 'Hemis modulida bo`lim birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                            faculty = Faculty.objects.get(hemisid=gi['department']['id'])

                            specialty = AllSpeciality.objects.filter(spec_id=gi['specialty']['id']).exists()
                            if not specialty:
                                #print('02')
                                return Response({'error': 'Hemis modulida yonalish birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                            specialty = AllSpeciality.objects.get(spec_id=gi['specialty']['id'])

                            educationLang = Educationlang.objects.filter(code=gi['educationLang']['code']).exists()
                            if not educationLang:
                                #print('03')
                                return Response({'error': 'Hemis modulida oquv tili birktrilmagan'},status=status.HTTP_400_BAD_REQUEST)
                            educationLang = Educationlang.objects.get(code=gi['educationLang']['code'])
                            new_group = Group()
                            new_group.name = gi['name']
                            new_group.h_id = gi['id']
                            new_group.educationLang = educationLang
                            new_group.new_specialty = specialty
                            new_group.faculty = faculty
                            new_group.group_curriculum = j
                            new_group.save()

            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time},status=status.HTTP_200_OK)

