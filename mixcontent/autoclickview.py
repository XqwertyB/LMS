from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

from config.permissions import AllowOnlyTrustedOrigins
from hemis.models import Hemis_sub, Hemis_Base, HemisToken
from shared.permissions import IsAdmin
from universty.models import Faculty, Faculty_type
from speciality.models import Bspeciality, Mspeciality, Ospeciality
from learning_process.models import Educationtype, Science_branch
from .models import ConnectSpeciality
import datetime


class GetConnectSpeciality(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=5)
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
                'limit': '100',
            }
            respon = requests.get(baseurl + pathurl, headers=headers, params=params)

            data = respon.json()
            start_time = datetime.datetime.now()
            page = data['data']['pagination']['page']
            pagecount = data['data']['pagination']['pageCount']
            for i in range(int(page), int(pagecount) + 1, 1):
                # 1
                params = {
                    'page': str(i),
                    'limit': '100',
                }
                prespon = respon = requests.get(baseurl + pathurl, headers=headers, params=params)
                rdata = prespon.json()['data']['items']
                for j in rdata:
                    if not ConnectSpeciality.objects.filter(conbase_spec_id=j['id']).exists():
                        obj = ConnectSpeciality()
                        if j['department'] is not None:
                            try:
                                dept = Faculty.objects.get(hemisid=j['department']['id'])
                                obj.department = dept
                            except Exception as ex:
                                print(ex)
                                return Response({'error': 'Fakultet bo`limi yuklanmagan! Hemisdan yuklanish kere'})
                        else:
                            obj.department = None
                        if j['localityType'] is not None:
                            try:
                                loctype = Faculty_type.objects.get(code=j['localityType']['code'])
                                obj.localitytype = loctype
                            except:
                                return Response({'error': 'Fakultet turi yuklanmagan! Hemisdan yuklanish kere'})
                        else:
                            obj.localitytype = None
                        if j['educationType'] is not None:
                            try:
                                edutype = Educationtype.objects.get(code=j['educationType']['code'])
                                obj.educationtype = edutype
                            except:
                                return Response({'error': 'Talim turi bo`limi yuklanmagan! Hemisdan yuklanish kere'})
                        else:
                            obj.educationtype = None
                        if j['bachelorSpecialty'] is not None:
                            try:
                                bachelor = Bspeciality.objects.get(base_spec_id=j['bachelorSpecialty']['id'])
                                obj.bachelorSpecialty = bachelor
                            except:
                                return Response({'error': 'Bakalavr bo`limi yuklanmagan! Hemisdan yuklanish kere'})
                        else:
                            obj.bachelorSpecialty = None
                        if j['masterSpecialty'] is not None:
                            try:
                                master = Mspeciality.objects.get(base_spec_id=j['masterSpecialty']['id'])
                                obj.masterSpecialty = master
                            except:
                                return Response({'error': 'Magistratura yuklanmagan! Hemisdan yuklanish kere'})
                        else:
                            obj.masterSpecialty = None
                        if j['doctorateSpecialty'] is not None:
                            try:
                                doctorate = Science_branch.objects.get(base_spec_id=j['doctorateSpecialty']['id'])
                                obj.doctorateSpecialty = doctorate
                            except:
                                return Response({'error': 'Doktarantura yuklanmagan! Hemisdan yuklanish kere'})
                        else:
                            obj.doctorateSpecialty = None
                        if j['ordinatureSpecialty'] is not None:
                            try:
                                ordinature = Ospeciality.objects.get(base_spec_id=j['ordinatureSpecialty']['id'])
                                obj.ordinature = ordinature
                            except:
                                return Response({'error': 'Ordinatura yuklanmagan! Hemisdan yuklanish kere'})
                        else:
                            obj.ordinature = None
                        obj.conbase_spec_id = str(j['id'])
                        obj.code = j['code']
                        obj.name = j['name']
                        obj.save()
                    else:
                        obj = ConnectSpeciality.objects.get(conbase_spec_id=j['id'])

                        if j['department'] is not None:
                            try:
                                dept = Faculty.objects.get(hemisid=j['department']['id'])
                                obj.department = dept
                            except Exception as ex:
                                print(ex)
                                return Response({'error': 'Fakultet bo`limi yuklanmagan! Hemisdan yuklanish kere'})
                        else:
                            obj.department = None
                        if j['localityType'] is not None:
                            try:
                                loctype = Faculty_type.objects.get(code=j['localityType']['code'])
                                obj.localitytype = loctype
                            except:
                                return Response({'error': 'Fakultet turi yuklanmagan! Hemisdan yuklanish kere'})
                        else:
                            obj.localitytype = None
                        if j['educationType'] is not None:
                            try:
                                edutype = Educationtype.objects.get(code=j['educationType']['code'])
                                obj.educationtype = edutype
                            except:
                                return Response({'error': 'Talim turi bo`limi yuklanmagan! Hemisdan yuklanish kere'})
                        else:
                            obj.educationtype = None
                        if j['bachelorSpecialty'] is not None:
                            try:
                                bachelor = Bspeciality.objects.get(base_spec_id=j['bachelorSpecialty']['id'])
                                obj.bachelorSpecialty = bachelor
                            except:
                                return Response({'error': 'Bakalavr bo`limi yuklanmagan! Hemisdan yuklanish kere'})
                        else:
                            obj.bachelorSpecialty = None
                        if j['masterSpecialty'] is not None:
                            try:
                                master = Mspeciality.objects.get(base_spec_id=j['masterSpecialty']['id'])
                                obj.masterSpecialty = master
                            except:
                                return Response({'error': 'Magistratura yuklanmagan! Hemisdan yuklanish kere'})
                        else:
                            obj.masterSpecialty = None
                        if j['doctorateSpecialty'] is not None:
                            try:
                                doctorate = Science_branch.objects.get(base_spec_id=j['doctorateSpecialty']['id'])
                                obj.doctorateSpecialty = doctorate
                            except:
                                return Response({'error': 'Doktarantura yuklanmagan! Hemisdan yuklanish kere'})
                        else:
                            obj.doctorateSpecialty = None
                        if j['ordinatureSpecialty'] is not None:
                            try:
                                ordinature = Ospeciality.objects.get(base_spec_id=j['ordinatureSpecialty']['id'])
                                obj.ordinature = ordinature
                            except:
                                return Response({'error': 'Ordinatura yuklanmagan! Hemisdan yuklanish kere'})
                        else:
                            obj.ordinature = None
                        obj.code = j['code']
                        obj.name = j['name']
                        obj.save()


            time = respon.elapsed.total_seconds()
            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time})
